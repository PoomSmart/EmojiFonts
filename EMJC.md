# EMJC Format

This document describes Apple's proprietary **EMJC** image format (`emj1`), used
to store emoji bitmaps in the `sbix` table of AppleColorEmoji fonts, and explains
the implementation in `emjc.py` (decoder) and `emjc_encoder.py` (encoder).

---

## Overview

EMJC is a tile-based, losslessly-compressed raster image format. Each emoji strike
stored as EMJC data contains a single RGBA image. The format achieves compression
through three stacked techniques:

1. **Reversible color-space transform** — decorrelates R, G, B channels.
2. **Row-level prediction filtering** — removes spatial redundancy (similar to PNG).
3. **lzfse compression** — entropy-codes the residuals.

An optional **appendix** section handles pixel components whose residuals exceed
the normal per-byte encoding range.

---

## File Structure

### Header (16 bytes)

| Offset | Size | Endian | Field | Value / Notes |
|--------|------|--------|-------|---------------|
| 0 | 4 | BE | Magic | `emj1` |
| 4 | 2 | LE | Version | `0` |
| 6 | 2 | LE | Unknown | `0xa101` |
| 8 | 2 | LE | Width | Image width in pixels |
| 10 | 2 | LE | Height | Image height in pixels |
| 12 | 2 | LE | Appendix Length | Byte length of the appendix section |
| 14 | 2 | LE | Padding | `0` (unused) |

The header is written in mixed endianness: the magic is read as big-endian bytes,
while all numeric fields are little-endian.

### Compressed Payload

Everything from byte 16 onward is a single **lzfse-compressed** blob. After
decompression, the expected byte length is:

```
pixels + height + pixels * 3 + appendix_length
```

where `pixels = width * height`.

The decompressed payload is divided into four contiguous sections:

| Section | Size | Description |
|---------|------|-------------|
| **Alpha** | `pixels` bytes | Raw alpha channel, one byte per pixel (row-major) |
| **Filters** | `height` bytes | One filter type (0–4) per row |
| **RGB Residuals** | `pixels * 3` bytes | Zigzag-encoded prediction residuals in transformed color space |
| **Appendix** | `appendix_length` bytes | Overflow offset adjustments (see below) |

---

## Color Space Transform

EMJC stores color in a reversible YCoCg-R-inspired transform. Each pixel's
`(R, G, B)` triple is converted to `(base, p, q)` before filtering and encoding.

### Forward Transform (encoder)

```python
p = R - B
t = B + (p // 2)   # floor division
q = G - t
base = G - ((q + 1) // 2 if q >= 0 else q // 2)
```

- **p** ≈ red–blue difference (Co channel).
- **q** ≈ green–luma difference (Cg channel).
- **base** ≈ luma.

The integer arithmetic is carefully chosen so that the transform is exactly
reversible without any rounding loss.

### Inverse Transform (decoder)

The decoder reconstructs `(R, G, B)` from `(base, p, q)` using four cases that
depend on the signs of `p` and `q`:

| `p` | `q` | R | G | B |
|-----|-----|---|---|---|
| ≥ 0 | ≥ 0 | `base + (p+1)//2 - q//2` | `base + (q+1)//2` | `base - p//2 - q//2` |
| ≥ 0 | < 0 | `base + (p+1)//2 - (q+1)//2` | `base + q//2` | `base - p//2 - (q+1)//2` |
| < 0 | ≥ 0 | `base + p//2 - q//2` | `base + (q+1)//2` | `base - (p+1)//2 - q//2` |
| < 0 | < 0 | `base + p//2 - (q+1)//2` | `base + q//2` | `base - (p+1)//2 - (q+1)//2` |

After inversion, output channel values are taken modulo 257 (with wrap-around for
negatives) and written as BGRA bytes.

---

## Prediction Filters

Each row is encoded with one of five prediction strategies, selected per-row by
the encoder (stored in the **Filters** section). Each strategy computes a
prediction for the current pixel from its already-decoded neighbors, then stores
only the *residual* (difference).

| Filter | Name | Prediction source |
|--------|------|-------------------|
| 0 | None | Zero (no prediction) |
| 1 | Paeth | Left or upper, chosen per-row based on channel-0 gradient |
| 2 | Sub | Left neighbor |
| 3 | Up | Upper neighbor |
| 4 | Average | Biased average of left and upper |

Filters 2 and 3 degrade gracefully at image edges (left column uses zero for left
neighbor; top row uses zero for upper neighbor).

### Filter 1 — Paeth-like

For each pixel (when both left and upper neighbors exist), the decoder resolves
the prediction using only the **base** channel (channel 0):

```
if |left[0] - left_upper[0]| < |upper[0] - left_upper[0]|:
    predict = upper  # apply to all three channels
else:
    predict = left
```

This is a simplified Paeth predictor that uses gradient magnitude to choose
between the left and upper neighbor, but applies the same choice to all channels.

### Filter 4 — Biased Average

```python
def filter4_value(left, upper):
    value = left + upper + 1
    return -((-value) // 2) if value < 0 else value // 2
```

This computes `floor((left + upper + 1) / 2)`, a biased average that rounds
toward positive infinity — the ceiling of the unbiased average.

---

## Residual Encoding (Zigzag)

Each component residual `diff = actual - predicted` is mapped to an unsigned byte
via a **zigzag** scheme that interleaves positive and negative values:

```
encoded = 2 * (diff - offset)       for diff ≥ offset
encoded = 2 * -(diff + offset) + 1  for diff ≤ -offset
```

With `offset = 0` (the common case):

- Even bytes `→` positive diffs: `enc = 2 * diff`
- Odd bytes `→` negative diffs: `enc = 2 * (-diff) - 1`

The encoded value must fit in one byte (0–255), which covers diffs in
`[-127, 127]` with offset 0, or a shifted range when the appendix provides a
larger offset.

Decoding (inverse):

```
diff = (enc // 2) + offset          if enc is even
diff = -((enc - 1) // 2) - offset   if enc is odd
```

---

## Appendix

The appendix handles pixel components whose residuals fall outside the ±127 range
encodeable with offset 0. It is processed by the decoder *before* the main pixel
loop, scanning sequentially through all `pixels * 3` component buffer positions.

### Appendix Byte Format

Each byte encodes two fields:

```
high 6 bits  →  skip  (number of buffer positions to advance before applying)
low 2 bits   →  multiplier  (0–3)
```

When the decoder processes an appendix byte at current buffer position `pos`:

1. Advance `pos` by `skip`.
2. Set `buffer[pos] = multiplier * 128`.  This becomes the encoding `offset`
   for that component position.
3. Advance `pos` by 1.

When `skip` exceeds 63, the encoder emits a padding byte (`skip=63, multiplier=0`)
that advances the position by 64 without changing any offset, then continues.

The effective encodeable range for a component with multiplier `m` is
`[-(m*128 + 127), m*128 + 127]`, up to ±511 for `m = 3`.

---

## Encoding Algorithm

`encode_emjc(rgba_data, width, height, quantize_colors=None)` in `emjc_encoder.py`
proceeds as follows:

1. **Optional quantization** — reduce to at most `quantize_colors` distinct RGB
   colors using PIL's median-cut quantizer (alpha is preserved unchanged).
2. **Channel extraction** — separate alpha from RGB; apply the forward color transform
   to obtain `(base, p, q)` per pixel.
3. **Filter selection** — for each row, evaluate all five filter candidates.  For
   each candidate, compute the total residual cost (sum of encoded byte values) plus
   a penalty of 1000 per required appendix entry.  Select the filter with the lowest
   total cost.
4. **Appendix collection** — components that cannot be encoded with offset 0 record
   their buffer position and the minimum multiplier required.
5. **Serialization** — concatenate `alpha + filters + residuals + appendix`, then
   compress with lzfse.
6. **Header** — prepend the 16-byte header with the magic, dimensions, and appendix
   length.

---

## `convert_to_emjc.sh`

`convert_to_emjc.sh <assets_dir>` is a shell wrapper that converts a directory tree
of PNG emoji images to EMJC in parallel, using all available CPU cores.

```bash
./convert_to_emjc.sh apple/EMJC          # convert in-place
./convert_to_emjc.sh --verify apple/EMJC # round-trip test (no files modified)
```

The `--verify` flag encodes a sample of PNGs, immediately decodes them, and
compares pixel-by-pixel against the originals, confirming lossless round-trip
fidelity.
