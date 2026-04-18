# ACCF Format

This document describes Apple's proprietary **ACCF** (Apple Color Compressed Font)
table (`accf`), used to store emoji bitmaps in iOS 8.3–9.3. It explains the binary
format, the image-record encoding scheme, and the `accf.py` implementation.

---

## Overview

The `accf` table is a sidecar file (stored alongside the `.ttf` as
`AppleColorEmoji@2x.ccf`) that holds compressed colour bitmap images for every glyph
at one or more pixel sizes. It replaces the `sbix`-based PNG approach used in later
iOS versions with a proprietary palette + run-length encoding scheme that is
significantly more compact.

Two wire formats exist:

| | **Version 1** (iOS 8.x) | **Version 2** (iOS 9.x) |
|---|---|---|
| Magic | `\x40\x30\x20\x10` (LE `0x10203040`) | `fcca` (LE `0x61636366`) |
| Header size | 48 112 bytes (`0xBBF0`) | 105 332 bytes (`0x19B74`) |
| LUT entries/tier | 2 000 (4 000 bytes) | 2 500 (5 000 bytes) |
| Tier slots | 4 | 7 |
| Pixel-size order | largest first | smallest first |

The image-record format (palette, runs table, bit-stream) is **identical** in both
versions.

---

## File Structure

### Version 1 Header (48 112 bytes)

```
[0x0000]  magic             : 4 bytes  = \x40\x30\x20\x10
[0x0004]  reserved0         : uint32le = 0
[0x0008]  reserved1         : uint32le = 0
[0x000C]  numTiers          : uint32le  (e.g. 3 for [96, 64, 40] px)
[0x0010]  storedPixelSizes  : uint32le[numTiers]  (largest first)
[0x0024]  numStoredGlyphs   : uint32le
[0x0028]  tierGlyphLUTs     : 4 × 4000 bytes
              For tier k: uint16le[2000] at file offset 4000×k + 40
              Entry for glyph_id: global image index, or 0xFFFF if absent.
[0x3EA8]  tierRangeMeta     : 64 bytes  (tier start/end/count data)
[0x3EE8]  glyphOffsetTable  : uint32le[numStoredGlyphs]
              Offset of image record i relative to base 0xBBF0
[0xBBF0]  image records     (variable length, one per stored glyph image)
```

### Version 2 Header (105 332 bytes)

```
[0x0000]  magic             : 4 bytes  = fcca
[0x0004]  version           : uint32le = 2
[0x0008]  field3            : uint32le = 1
[0x000C]  numTiers          : uint32le  (e.g. 3 for [40, 64, 96] px)
[0x0010]  storedPixelSizes  : uint32le[numTiers]  (smallest first)
[0x002F]  resSizeMap        : uint8[161]
              resSizeMap[pxSize] = tier index for the requested pixel size
              (covers sizes 0–160; accessed as data[pxSize + 47])
[0x00D0]  numStoredGlyphs   : uint32le
[0x00D4]  tierGlyphLUTs     : 7 × 5000 bytes
              For tier k: uint16le[2500] at file offset 5000×k + 212
              Entry for glyph_id: global image index, or 0xFFFF if absent.
[0x89AC]  tierRangeMeta     : 112 bytes  (preserved verbatim on round-trip)
[0x89FC]  glyphOffsetTable  : uint32le[numStoredGlyphs]
              Offset of image record i relative to base 0x19B74
[0x19B74] image records     (variable length, one per stored glyph image)
```

### Glyph LUT

Each tier occupies one LUT slot. A slot is a flat array of `uint16le` entries
indexed by glyph ID. The value is the **global image index** — a 0-based index
into the glyph-offset table. `0xFFFF` means no image for that glyph in this tier.

Unused tier slots (allocated but not active) are zero-filled in Apple-produced files.

### Glyph Offset Table

```
uint32le[numStoredGlyphs]
```

Each entry is the byte offset of image record `i` relative to the image-data base
(`0xBBF0` for v1, `0x19B74` for v2). Multiple glyph LUT entries may point to the
same global index (image deduplication).

---

## Image Record Format

Every image record begins with a 40-byte header (all fields `uint32le`, little-endian):

| Offset | Field | Notes |
|--------|-------|-------|
| +00 | `width` | Equal to the tier's stored pixel size |
| +04 | `height` | Always equal to `width` |
| +08 | `paletteOffset` | Offset from record start to palette data (= 40) |
| +0C | `paletteSizeBytes` | Byte length of the palette blob |
| +10 | `bitsPerPaletteIdx` | `= ceil(log2(numPaletteEntries))`, minimum 1 |
| +14 | `runsTableOffset` | Offset from record start to runs table |
| +18 | `reserved0` | `0` |
| +1C | `reserved1` | `0` |
| +20 | `bitStreamOffset` | Offset from record start to bit-stream |
| +24 | `bitStreamBytes` | Byte length of the bit-stream |

Immediately following the header (at `paletteOffset`) come the palette, runs table,
and bit-stream in that order.

---

## Palette Encoding

The palette is a packed big-endian bit-stream of 21-bit entries. Each entry encodes
one colour:

```
bits [20:14]  B7  — blue  channel (7 bits, MSBs first)
bits [13: 7]  G7  — green channel (7 bits)
bits [ 6: 0]  R7  — red   channel (7 bits, LSBs)
```

> **Note:** the channel order is **BGR** in the bit-stream, not RGB.

Decoded 8-bit values are `R = R7 × 2`, `G = G7 × 2`, `B = B7 × 2`, giving a range
of 0–254 (not 0–255). Eight palette entries occupy exactly 21 bytes (`8 × 21 = 168`
bits = 21 bytes). The palette blob is padded to the next byte boundary.

---

## Runs Table

The runs table encodes which pixels are present (non-transparent) and their alpha
values. It immediately follows the palette.

```
uint16le  numRuns

For each run:
  uint16le  pixelIdx    — flat 1-D index into the width×height output buffer
  uint8     control
  if control & 0x80:    # Mode B — per-pixel alpha
    uint8[control & 0x7F]  alpha values, one per pixel
  else:                 # Mode A — uniform alpha
    uint8  alpha         — the same alpha for all pixels in this run
```

Pixels **not** referenced by any run are fully transparent (RGBA = `0, 0, 0, 0`).

### Mode A vs Mode B

- **Mode A** (`control & 0x80 == 0`): All pixels in the run share one alpha value.
  `control` itself is the pixel count. Efficient for solid-colour or flat regions.
- **Mode B** (`control & 0x80 != 0`): Each pixel has an individual alpha byte.
  `control & 0x7F` is the pixel count. Used for anti-aliased edges.

---

## Bit-Stream

The bit-stream encodes colour indices for every pixel referenced by the runs table,
in the same order the runs table lists them. Bits are packed **LSB-first within each
byte** (i.e. bit 0 of byte 0 is read first).

For each pixel, a 2-bit opcode is read:

| Opcode | Meaning |
|--------|---------|
| `0b00` | Keep current palette index |
| `0b01` | `palette_index += 1` |
| `0b10` | `palette_index -= 1` |
| `0b11` | Read `bitsPerPaletteIdx` bits for absolute palette index |

The delta opcodes (`01` / `10`) allow nearby pixels sharing similar colours to be
encoded without emitting a full index each time.

---

## Encoder Strategy

The encoder in `accf.py` sorts the palette by pixel frequency (most common colour
→ index 0) to minimise the average index width. The encoder:

1. Skips fully-transparent pixels (alpha = 0) — they take no space in palette, runs,
   or bit-stream.
2. Groups contiguous non-transparent pixels into runs, broken at transparency gaps.
3. Uses Mode A for runs where all alphas are equal; Mode B otherwise.
4. Emits delta opcodes where possible; falls back to absolute only when needed.
5. Deduplicates identical image records in `compile()` — multiple glyph LUT entries
   can point to the same physical record (matching Apple's own deduplication).

Re-encoded files are approximately **105–106%** of Apple-produced sizes after a
PNG round-trip. Unedited glyphs are re-emitted verbatim (lossless).

---

## Implementation (`accf.py`)

The ACCF reader/writer lives in [`accf.py`](accf.py) — a self-contained module with
no dependency on fonttools for any CCF-specific logic. (`extract_ccf.py` still uses
fonttools solely to read the companion `.ttf`'s glyph order.)

| Symbol | Description |
|--------|-------------|
| `MAGIC` | `b'fcca'` — v2 magic bytes |
| `MAGIC_V1` | `b'\x40\x30\x20\x10'` — v1 magic bytes |
| `_decode_palette(bytes)` | Packed 21-bit BGR → list of `(R, G, B)` tuples |
| `_encode_palette(list)` | `(R, G, B)` list → packed 21-bit BGR bytes |
| `decode_image_record(bytes)` | Raw record bytes → `width×height×4` RGBA bytes |
| `encode_image_record(rgba, w, h)` | RGBA bytes → raw record bytes |
| `_rgba_to_png(rgba, w, h)` | RGBA → PNG bytes (Pillow or pure-Python fallback) |
| `_png_to_rgba(png)` | PNG bytes → `(rgba, width, height)` |
| `CcfGlyph` | One glyph in one strike; lazily decodes PNG on first `.imageData` access |
| `CcfStrike` | One resolution tier; `glyphs` dict maps glyph name → `CcfGlyph` |
| `AccfTable` | Top-level table; `strikes` dict maps pixel size → `CcfStrike` |

### Usage

```python
from accf import AccfTable

# Read glyph order from the companion .ttf (using fonttools or any other means)
glyph_order = [...]   # list of glyph names in glyph-ID order

# Decompile

accf = AccfTable()
with open("AppleColorEmoji@2x.ccf", "rb") as f:
    accf.decompile(f.read(), glyph_order)

# List available pixel sizes
print(accf.strikes.keys())   # e.g. dict_keys([40, 64, 96])

# Extract a glyph image as PNG bytes
png_bytes = accf.strikes[96].glyphs["uni1F600"].imageData

# Round-trip back to CCF
with open("out.ccf", "wb") as f:
    f.write(accf.compile(glyph_order))
```

### Encoder strategy

The encoder sorts the palette by pixel frequency (most common colour → index 0) to
minimise the average index width.  It:

1. Skips fully-transparent pixels — they take no space in palette, runs, or bit-stream.
2. Groups contiguous non-transparent pixels into runs, broken at transparency gaps.
3. Uses Mode A for runs where all alphas are equal; Mode B otherwise.
4. Emits delta opcodes where possible; falls back to absolute only when needed.
5. Deduplicates identical image records in `compile()` — multiple glyph LUT entries
   can point to the same physical record (matching Apple's own deduplication).

Re-encoded files are approximately **105–106%** of Apple-produced sizes after a
PNG round-trip. Unedited glyphs are re-emitted verbatim (lossless).

---

## Version Differences Summary

| Feature | v1 (iOS 8.x) | v2 (iOS 9.x) |
|---------|-------------|-------------|
| Magic | `\x40\x30\x20\x10` | `fcca` |
| Header | 48 112 bytes | 105 332 bytes |
| Tier LUT slots | 4 × 4 000 bytes | 7 × 5 000 bytes |
| Max glyph ID / LUT | 1 999 | 2 499 |
| Pixel-size order | descending | ascending |
| Resolution size map | absent | `uint8[161]` at `0x002F` |
| Tier range meta | 64 bytes | 112 bytes |
| Image data base | `0xBBF0` | `0x19B74` |
