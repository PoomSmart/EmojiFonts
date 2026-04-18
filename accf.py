"""Standalone reader/writer for Apple's ACCF (Apple Color Compressed Font) format.

The CCF sidecar file (``AppleColorEmoji@2x.ccf``) stores emoji bitmaps using a
proprietary palette + run-length encoding scheme. Two wire formats exist:

* **Version 1** (iOS 8.x) — magic ``b'\\x40\\x30\\x20\\x10'``, 48 112-byte header.
* **Version 2** (iOS 9.x) — magic ``b'fcca'``, 105 332-byte header.

Public API
----------
- :data:`MAGIC` / :data:`MAGIC_V1` — magic-byte constants for version detection.
- :func:`decode_image_record` — raw CCF record bytes → RGBA bytes.
- :func:`encode_image_record` — RGBA bytes → raw CCF record bytes.
- :class:`CcfGlyph` — single glyph image (lazy PNG decode).
- :class:`CcfStrike` — one resolution tier; ``glyphs`` dict maps name → CcfGlyph.
- :class:`AccfTable` — top-level table; ``strikes`` dict maps pixel size → CcfStrike.

Quick example::

    from accf import AccfTable

    ccf_bytes = open("AppleColorEmoji@2x.ccf", "rb").read()
    glyph_order = [...]   # from the companion .ttf

    table = AccfTable()
    table.decompile(ccf_bytes, glyph_order)

    png_bytes = table.strikes[96].glyphs["uni1F600"].imageData

    out_bytes = table.compile(glyph_order)

See ``ACCF.md`` for a complete format description.
"""

import io
import math
import struct
from typing import Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

#: Magic bytes for Version 2 (iOS 9.x).
MAGIC = b"fcca"

#: Magic bytes for Version 1 (iOS 8.x).
MAGIC_V1 = b"\x40\x30\x20\x10"

# ── v2 layout ───────────────────────────────────────────────────────────────

#: Total header size (= image-data base offset) for v2.
HEADER_SIZE = 0x19B74  # 105 332

_OFF_NUM_STORED = 208  # offset of numStoredGlyphs in v2 header
_TIER_LUT_BYTES = 5000  # bytes per tier-LUT slot (v2)
_TIER_LUT_BASE = 212  # file offset of tier-LUT area (v2)
_TIER_LUT_MAX_GID = 2500  # max glyph ID in a v2 LUT slot
_NUM_TIER_SLOTS = 7  # allocated LUT slots (v2)
_OFF_TIER_RANGE_META = _TIER_LUT_BASE + _NUM_TIER_SLOTS * _TIER_LUT_BYTES  # 35 212
_OFF_GLYPH_OFFSET_TABLE = 0x89FC  # 35 324
_OFF_IMAGE_DATA = HEADER_SIZE

# ── v1 layout ───────────────────────────────────────────────────────────────

#: Total header size (= image-data base offset) for v1.
HEADER_SIZE_V1 = 48112  # 0xBBF0

_V1_OFF_NUM_STORED = 36
_V1_LUT_BASE = 40
_V1_LUT_BYTES = 4000
_V1_LUT_MAX_GID = 2000
_V1_NUM_TIER_SLOTS = 4
_V1_OFF_TIER_RANGE_META = _V1_LUT_BASE + _V1_NUM_TIER_SLOTS * _V1_LUT_BYTES  # 16 040
_V1_OFF_GLYPH_OFFSET_TABLE = 16104  # _V1_OFF_TIER_RANGE_META + 64
_V1_OFF_IMAGE_DATA = HEADER_SIZE_V1


# ---------------------------------------------------------------------------
# Palette helpers
# ---------------------------------------------------------------------------


def _decode_palette(palette_bytes: bytes) -> List[Tuple[int, int, int]]:
    """Decode packed 21-bit-per-entry BGR palette to a list of ``(R, G, B)`` tuples.

    Each 21-bit entry stores 7-bit B, 7-bit G, 7-bit R (B in MSBs, R in LSBs)
    within a big-endian bit-stream.  The 7-bit value ``v7`` maps to the 8-bit
    channel value ``v7 << 1`` (range 0–254).
    """
    n = len(palette_bytes) * 8 // 21
    if n == 0:
        return []

    total_bits = len(palette_bytes) * 8
    bits = int.from_bytes(palette_bytes, "big")

    result: List[Tuple[int, int, int]] = []
    for i in range(n):
        start = i * 21
        shift = total_bits - start - 21
        if shift < 0:
            break
        entry = (bits >> shift) & 0x1FFFFF
        b7 = (entry >> 14) & 0x7F
        g7 = (entry >> 7) & 0x7F
        r7 = entry & 0x7F
        result.append((r7 << 1, g7 << 1, b7 << 1))
    return result


def _encode_palette(palette: List[Tuple[int, int, int]]) -> bytes:
    """Encode a list of ``(R, G, B)`` 8-bit tuples to the packed 21-bit BGR format."""
    n = len(palette)
    total_bits = n * 21
    total_bit_len = (total_bits + 7) & ~7  # round up to byte boundary
    bits = 0
    for i, (r, g, b) in enumerate(palette):
        r7 = (r >> 1) & 0x7F
        g7 = (g >> 1) & 0x7F
        b7 = (b >> 1) & 0x7F
        entry = (b7 << 14) | (g7 << 7) | r7
        shift = total_bit_len - (i + 1) * 21
        bits |= entry << shift
    return bits.to_bytes(total_bit_len // 8, "big")


# ---------------------------------------------------------------------------
# Bit-stream helper
# ---------------------------------------------------------------------------


def _read_bits_lsb(data: bytes, bit_pos: int, n: int) -> Tuple[int, int]:
    """Read *n* bits from *data* starting at *bit_pos* (LSB-first convention).

    Returns ``(value, new_bit_pos)``.
    """
    val = 0
    for i in range(n):
        byte_idx = (bit_pos + i) >> 3
        bit_idx = (bit_pos + i) & 7
        if byte_idx < len(data):
            val |= ((data[byte_idx] >> bit_idx) & 1) << i
    return val, bit_pos + n


# ---------------------------------------------------------------------------
# Image record decode / encode
# ---------------------------------------------------------------------------


def decode_image_record(record: bytes) -> bytes:
    """Decode a single CCF image record to raw RGBA bytes.

    Parameters
    ----------
    record:
        Raw bytes of one image record (starting from the 40-byte record header).

    Returns
    -------
    bytes
        Raw ``width × height × 4`` RGBA bytes, top-left origin, row-major.
    """
    if len(record) < 40:
        raise ValueError("Image record too short")

    (
        width,
        height,
        palette_off,
        palette_size_bytes,
        bits_per_idx,
        runs_off,
        _reserved0,
        _reserved1,
        bitstream_off,
        bitstream_size,
    ) = struct.unpack_from("<IIIIIIIIII", record, 0)

    palette = _decode_palette(record[palette_off : palette_off + palette_size_bytes])
    bitstream = record[bitstream_off : bitstream_off + bitstream_size]
    output = bytearray(4 * width * height)

    num_runs = struct.unpack_from("<H", record, runs_off)[0]
    run_pos = runs_off + 2
    bit_pos = 0
    palette_idx = 0

    for _ in range(num_runs):
        pixel_idx = struct.unpack_from("<H", record, run_pos)[0]
        control = record[run_pos + 2]

        if control & 0x80:
            # Mode B: per-pixel alpha
            count = control & 0x7F
            alphas = record[run_pos + 3 : run_pos + 3 + count]
            run_pos += 3 + count
        else:
            # Mode A: uniform alpha
            count = control
            alpha_byte = record[run_pos + 3]
            alphas = bytes([alpha_byte]) * count
            run_pos += 4

        for k in range(count):
            opcode, bit_pos = _read_bits_lsb(bitstream, bit_pos, 2)
            if opcode == 3:
                palette_idx, bit_pos = _read_bits_lsb(bitstream, bit_pos, bits_per_idx)
            elif opcode == 1:
                palette_idx += 1
            elif opcode == 2:
                palette_idx -= 1
            # opcode 0: keep palette_idx

            r, g, b = palette[palette_idx]
            a = alphas[k]
            out_off = (pixel_idx + k) * 4
            output[out_off] = r
            output[out_off + 1] = g
            output[out_off + 2] = b
            output[out_off + 3] = a

    return bytes(output)


def encode_image_record(rgba: bytes, width: int, height: int) -> bytes:
    """Encode raw RGBA bytes to a CCF image record.

    The palette is sorted by pixel frequency (most common colour → index 0).
    The bit-stream uses delta opcodes (``+1``/``−1``) where possible to minimise
    emitted bits.  Fully transparent pixels are omitted from all structures.
    Runs are split into Mode-A (uniform alpha) and Mode-B (per-pixel alpha)
    segments to produce compact output that closely matches Apple-produced sizes.
    """
    total = width * height

    # Build palette from non-transparent pixels, sorted by frequency
    freq: Dict[Tuple[int, int, int], int] = {}
    for i in range(total):
        if rgba[i * 4 + 3] == 0:
            continue
        r = rgba[i * 4] & 0xFE
        g = rgba[i * 4 + 1] & 0xFE
        b = rgba[i * 4 + 2] & 0xFE
        c = (r, g, b)
        freq[c] = freq.get(c, 0) + 1

    palette = sorted(freq.keys(), key=lambda c: -freq[c])
    color_to_idx = {c: i for i, c in enumerate(palette)}
    n_colors = len(palette)
    bits_per_idx = max(1, math.ceil(math.log2(max(n_colors, 1))))
    palette_bytes = _encode_palette(palette)

    # Collect non-transparent pixels in scan order
    pixels: List[Tuple[int, Tuple[int, int, int], int]] = []
    for i in range(total):
        a = rgba[i * 4 + 3]
        if a == 0:
            continue
        r = rgba[i * 4] & 0xFE
        g = rgba[i * 4 + 1] & 0xFE
        b = rgba[i * 4 + 2] & 0xFE
        pixels.append((i, (r, g, b), a))

    # Build runs and bit-stream
    runs_parts: List[bytes] = []
    bitstream_bits: List[int] = []
    cur_pal_idx = 0

    def append_bits(v: int, n: int) -> None:
        for i in range(n):
            bitstream_bits.append((v >> i) & 1)

    def emit_color(color: Tuple[int, int, int]) -> None:
        nonlocal cur_pal_idx
        new_idx = color_to_idx[color]
        d = new_idx - cur_pal_idx
        if d == 0:
            append_bits(0, 2)
        elif d == 1:
            append_bits(1, 2)
        elif d == -1:
            append_bits(2, 2)
        else:
            append_bits(3, 2)
            append_bits(new_idx, bits_per_idx)
        cur_pal_idx = new_idx

    # Walk contiguous flat-index segments (transparency gaps split segments)
    k = 0
    while k < len(pixels):
        seg_start = k
        while k + 1 < len(pixels) and pixels[k + 1][0] == pixels[k][0] + 1:
            k += 1
        k += 1
        seg = pixels[seg_start:k]

        j = 0
        while j < len(seg):
            alpha = seg[j][2]
            # Find maximal same-alpha run (Mode-A candidate, ≤ 127 pixels)
            m = j + 1
            while m < len(seg) and seg[m][2] == alpha and (m - j) < 127:
                m += 1

            if m - j >= 2:
                # Mode A: uniform alpha
                count = m - j
                runs_parts.append(struct.pack("<HBB", seg[j][0], count, alpha))
                for p in seg[j:m]:
                    emit_color(p[1])
                j = m
            else:
                # Mode B: per-pixel alpha; stop when two consecutive same-alpha
                # pixels appear (better encoded as Mode A)
                mb: List[Tuple[int, Tuple[int, int, int], int]] = [seg[j]]
                j += 1
                while j < len(seg) and len(mb) < 127:
                    if j + 1 < len(seg) and seg[j][2] == seg[j + 1][2]:
                        break
                    mb.append(seg[j])
                    j += 1
                count = len(mb)
                alphas_b = bytes(p[2] for p in mb)
                runs_parts.append(struct.pack("<HB", mb[0][0], 0x80 | count) + alphas_b)
                for p in mb:
                    emit_color(p[1])

    # Pack bit-stream (LSB-first bits → bytes)
    nbytes = (len(bitstream_bits) + 7) // 8
    bitstream_buf = bytearray(nbytes)
    for b_i, bit in enumerate(bitstream_bits):
        bitstream_buf[b_i >> 3] |= bit << (b_i & 7)
    bitstream_bytes = bytes(bitstream_buf)

    # Assemble record
    HEADER_LEN = 40
    runs_table = struct.pack("<H", len(runs_parts)) + b"".join(runs_parts)
    palette_off = HEADER_LEN
    runs_off = palette_off + len(palette_bytes)
    bitstream_off = runs_off + len(runs_table)
    header = struct.pack(
        "<IIIIIIIIII",
        width,
        height,
        palette_off,
        len(palette_bytes),
        bits_per_idx,
        runs_off,
        0,  # reserved0
        0,  # reserved1
        bitstream_off,
        len(bitstream_bytes),
    )
    assert len(header) == HEADER_LEN
    return header + palette_bytes + runs_table + bitstream_bytes


# ---------------------------------------------------------------------------
# RGBA ↔ PNG helpers
# ---------------------------------------------------------------------------


def _rgba_to_png(rgba: bytes, width: int, height: int) -> bytes:
    """Convert raw RGBA bytes to PNG bytes (uses Pillow if available)."""
    try:
        from PIL import Image

        img = Image.frombytes("RGBA", (width, height), rgba)
        buf = io.BytesIO()
        img.save(buf, "PNG")
        return buf.getvalue()
    except ImportError:
        pass
    return _write_png(rgba, width, height)


def _png_to_rgba(png_data: bytes) -> Tuple[bytes, int, int]:
    """Convert PNG bytes to ``(rgba_bytes, width, height)``."""
    try:
        from PIL import Image

        img = Image.open(io.BytesIO(png_data)).convert("RGBA")
        w, h = img.size
        return img.tobytes(), w, h
    except ImportError:
        pass
    return _read_png(png_data)


def _write_png(rgba: bytes, width: int, height: int) -> bytes:
    """Minimal pure-Python PNG encoder (no external deps)."""
    import zlib

    def make_chunk(tag: bytes, data: bytes) -> bytes:
        crc = zlib.crc32(tag + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", crc)

    ihdr = struct.pack(">II", width, height) + bytes([8, 6, 0, 0, 0])
    raw_rows = bytearray()
    row_bytes = width * 4
    for y in range(height):
        raw_rows.append(0)  # filter type = None
        raw_rows += rgba[y * row_bytes : (y + 1) * row_bytes]
    idat_data = zlib.compress(bytes(raw_rows), 9)

    sig = b"\x89PNG\r\n\x1a\n"
    return sig + make_chunk(b"IHDR", ihdr) + make_chunk(b"IDAT", idat_data) + make_chunk(b"IEND", b"")


def _read_png(png_data: bytes) -> Tuple[bytes, int, int]:
    """Minimal pure-Python PNG reader (8-bit RGBA, filter-type-0 only)."""
    import zlib

    if png_data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("Not a PNG")
    pos = 8
    ihdr_data: Optional[bytes] = None
    idat_parts: List[bytes] = []
    while pos < len(png_data):
        length = struct.unpack_from(">I", png_data, pos)[0]
        tag = png_data[pos + 4 : pos + 8]
        data = png_data[pos + 8 : pos + 8 + length]
        if tag == b"IHDR":
            ihdr_data = data
        elif tag == b"IDAT":
            idat_parts.append(data)
        elif tag == b"IEND":
            break
        pos += 12 + length

    if ihdr_data is None:
        raise ValueError("PNG missing IHDR chunk")
    width = struct.unpack_from(">I", ihdr_data, 0)[0]
    height = struct.unpack_from(">I", ihdr_data, 4)[0]
    bit_depth = ihdr_data[8]
    colour_type = ihdr_data[9]
    if bit_depth != 8 or colour_type != 6:
        raise ValueError("Only 8-bit RGBA PNG supported in fallback reader")

    raw = zlib.decompress(b"".join(idat_parts))
    row_bytes = width * 4
    rgba = bytearray(width * height * 4)
    for y in range(height):
        filter_type = raw[y * (row_bytes + 1)]
        if filter_type != 0:
            raise ValueError("PNG filter types other than None (0) not supported")
        row = raw[y * (row_bytes + 1) + 1 : y * (row_bytes + 1) + 1 + row_bytes]
        rgba[y * row_bytes : (y + 1) * row_bytes] = row
    return bytes(rgba), width, height


# ---------------------------------------------------------------------------
# Private structural helpers
# ---------------------------------------------------------------------------


def _get_image_record(
    data: bytes,
    global_img_idx: int,
    off_table: int,
    img_base: int,
) -> Optional[bytes]:
    """Return the raw bytes of image record *global_img_idx*, or ``None``."""
    entry_off = off_table + 4 * global_img_idx
    if entry_off + 4 > len(data):
        return None
    rel_offset = struct.unpack_from("<I", data, entry_off)[0]
    abs_start = img_base + rel_offset
    if abs_start + 40 > len(data):
        return None

    bitstream_off = struct.unpack_from("<I", data, abs_start + 32)[0]
    bitstream_size = struct.unpack_from("<I", data, abs_start + 36)[0]
    record_size = bitstream_off + bitstream_size
    if abs_start + record_size > len(data):
        record_size = len(data) - abs_start
    return data[abs_start : abs_start + record_size]


def _build_v1_tier_range_meta(
    header: bytearray,
    tier_luts: List[Dict[int, int]],
) -> None:
    """Populate the 64-byte tier-range metadata block for v1 format."""
    counts = [len(lut) for lut in tier_luts]
    while len(counts) < _V1_NUM_TIER_SLOTS:
        counts.append(0)

    starts = []
    ends = []
    cumulative = 0
    for c in counts:
        starts.append(cumulative)
        ends.append(cumulative + c - 1 if c > 0 else 0)
        cumulative += c

    off = _V1_OFF_TIER_RANGE_META
    for i, v in enumerate(starts):
        struct.pack_into("<I", header, off + 4 * i, v)
    for i, v in enumerate(ends):
        struct.pack_into("<I", header, off + 4 * (_V1_NUM_TIER_SLOTS + i), v)
    for i, v in enumerate(counts):
        struct.pack_into("<I", header, off + 4 * (2 * _V1_NUM_TIER_SLOTS + i), v)
    for i, v in enumerate(counts):
        struct.pack_into("<I", header, off + 4 * (3 * _V1_NUM_TIER_SLOTS + i), v)


def _build_resolution_map(header: bytearray, sorted_sizes: List[int]) -> None:
    """Populate the 161-byte resolution-class lookup table at bytes 47–207 (v2)."""
    num_tiers = len(sorted_sizes)
    for px in range(161):
        best = num_tiers - 1
        for ti, sz in enumerate(sorted_sizes):
            if px <= sz:
                best = ti
                break
        off = px + 47
        if off < HEADER_SIZE:
            header[off] = best


# ---------------------------------------------------------------------------
# Public data model
# ---------------------------------------------------------------------------


class CcfGlyph:
    """A single glyph image within one :class:`CcfStrike`.

    Attributes
    ----------
    glyphName : str
        Name of the glyph.
    imageData : bytes | None
        PNG-encoded image data.  Decoded lazily from the raw CCF record on
        first access; ``None`` only if no image was stored.
    """

    def __init__(
        self,
        glyphName: str = "",
        imageData: Optional[bytes] = None,
        rawRecordData: Optional[bytes] = None,
    ) -> None:
        self.glyphName = glyphName
        self._imageData = imageData
        self._rawRecordData = rawRecordData

    @property
    def rawRecordData(self) -> Optional[bytes]:
        """Raw CCF image-record bytes.

        Available only while the glyph has not been decoded or externally
        modified.  Returns ``None`` once :attr:`imageData` has been accessed
        or assigned.
        """
        return self._rawRecordData

    @property
    def imageData(self) -> Optional[bytes]:
        """PNG image bytes, decoded from the raw CCF record on first access."""
        if self._imageData is None and self._rawRecordData is not None:
            rgba = decode_image_record(self._rawRecordData)
            w = struct.unpack_from("<I", self._rawRecordData, 0)[0]
            h = struct.unpack_from("<I", self._rawRecordData, 4)[0]
            self._imageData = _rgba_to_png(rgba, w, h)
            self._rawRecordData = None  # free raw bytes
        return self._imageData

    @imageData.setter
    def imageData(self, value: bytes) -> None:
        self._imageData = value
        self._rawRecordData = None


class CcfStrike:
    """One resolution tier (stored pixel size) within an :class:`AccfTable`.

    Attributes
    ----------
    pixelSize : int
        Stored pixel size (width = height) for all images in this strike.
    glyphs : dict[str, CcfGlyph]
        Maps glyph name → :class:`CcfGlyph`.
    """

    def __init__(self, pixelSize: int = 0) -> None:
        self.pixelSize = pixelSize
        self.glyphs: Dict[str, CcfGlyph] = {}


class AccfTable:
    """Reader/writer for an Apple Color Compressed Font (ACCF) CCF file.

    Attributes
    ----------
    version : int
        Wire-format version: ``1`` (iOS 8.x) or ``2`` (iOS 9.x).
    strikes : dict[int, CcfStrike]
        Maps stored pixel size → :class:`CcfStrike`.

    Usage::

        table = AccfTable()
        table.decompile(ccf_bytes, glyph_order)

        png = table.strikes[96].glyphs["uni1F600"].imageData

        out = table.compile(glyph_order)
    """

    def __init__(self) -> None:
        self.version: int = 2
        self.field3: int = 1
        self.strikes: Dict[int, CcfStrike] = {}
        self._rawHeader: Optional[bytes] = None

    # ------------------------------------------------------------------
    # decompile
    # ------------------------------------------------------------------

    def decompile(self, data: bytes, glyph_order: List[str]) -> None:
        """Populate *strikes* from raw CCF bytes.

        Parameters
        ----------
        data:
            Complete CCF file contents.
        glyph_order:
            Glyph names in glyph-ID order, matching the companion ``.ttf``.
        """
        magic = data[:4]
        if magic == MAGIC:
            self.version = struct.unpack_from("<I", data, 4)[0]
            self.field3 = struct.unpack_from("<I", data, 8)[0]
            hdr_size = HEADER_SIZE
            lut_base = _TIER_LUT_BASE
            lut_bytes = _TIER_LUT_BYTES
            lut_max_gid = _TIER_LUT_MAX_GID
            off_gt = _OFF_GLYPH_OFFSET_TABLE
            off_img = _OFF_IMAGE_DATA
        elif magic == MAGIC_V1:
            self.version = 1
            self.field3 = 0
            hdr_size = HEADER_SIZE_V1
            lut_base = _V1_LUT_BASE
            lut_bytes = _V1_LUT_BYTES
            lut_max_gid = _V1_LUT_MAX_GID
            off_gt = _V1_OFF_GLYPH_OFFSET_TABLE
            off_img = _V1_OFF_IMAGE_DATA
        else:
            raise ValueError(f"Unknown CCF magic {magic!r}; expected {MAGIC!r} (v2) or {MAGIC_V1!r} (v1)")

        if len(data) < hdr_size + 1:
            raise ValueError(f"CCF data too short: expected ≥ {hdr_size + 1} bytes, got {len(data)}")

        num_tiers = struct.unpack_from("<I", data, 12)[0]
        stored_sizes = [struct.unpack_from("<I", data, 16 + 4 * i)[0] for i in range(num_tiers)]

        self._rawHeader = data[:hdr_size]
        gid_to_name = {gid: name for gid, name in enumerate(glyph_order)}

        for tier_idx, pixel_size in enumerate(stored_sizes):
            strike = CcfStrike(pixelSize=pixel_size)
            max_gid = min(len(glyph_order), lut_max_gid)

            for gid in range(max_gid):
                lut_off = lut_base + lut_bytes * tier_idx + 2 * gid
                if lut_off + 2 > len(data):
                    break
                global_img_idx = struct.unpack_from("<H", data, lut_off)[0]
                if global_img_idx == 0xFFFF:
                    continue

                record = _get_image_record(data, global_img_idx, off_gt, off_img)
                if record is None:
                    continue

                glyph_name = gid_to_name.get(gid)
                if glyph_name is None:
                    continue

                strike.glyphs[glyph_name] = CcfGlyph(
                    glyphName=glyph_name,
                    rawRecordData=record,
                )

            self.strikes[pixel_size] = strike

    # ------------------------------------------------------------------
    # compile
    # ------------------------------------------------------------------

    def compile(self, glyph_order: List[str]) -> bytes:
        """Serialise *strikes* back to CCF binary format.

        Parameters
        ----------
        glyph_order:
            Glyph names in glyph-ID order, matching the companion ``.ttf``.

        Returns
        -------
        bytes
            Complete CCF file contents.
        """
        name_to_gid = {name: gid for gid, name in enumerate(glyph_order)}

        if self.version == 1:
            sorted_sizes = sorted(self.strikes.keys(), reverse=True)
            hdr_size = HEADER_SIZE_V1
            lut_base = _V1_LUT_BASE
            lut_bytes = _V1_LUT_BYTES
            lut_max_gid = _V1_LUT_MAX_GID
            num_tier_slots = _V1_NUM_TIER_SLOTS
            off_gt = _V1_OFF_GLYPH_OFFSET_TABLE
            off_num_stored = _V1_OFF_NUM_STORED
        else:
            sorted_sizes = sorted(self.strikes.keys())
            hdr_size = HEADER_SIZE
            lut_base = _TIER_LUT_BASE
            lut_bytes = _TIER_LUT_BYTES
            lut_max_gid = _TIER_LUT_MAX_GID
            num_tier_slots = _NUM_TIER_SLOTS
            off_gt = _OFF_GLYPH_OFFSET_TABLE
            off_num_stored = _OFF_NUM_STORED

        num_tiers = len(sorted_sizes)

        # Build global image list and per-tier LUTs
        all_records: List[bytes] = []
        tier_luts: List[Dict[int, int]] = [{} for _ in range(num_tiers)]

        for tier_idx, pixel_size in enumerate(sorted_sizes):
            strike = self.strikes[pixel_size]
            for glyph_name, glyph in strike.glyphs.items():
                gid = name_to_gid.get(glyph_name)
                if gid is None or gid >= lut_max_gid:
                    continue
                raw = glyph.rawRecordData
                if raw is not None:
                    record = raw
                else:
                    image_data = glyph.imageData
                    if image_data is None:
                        continue
                    rgba, w, h = _png_to_rgba(image_data)
                    record = encode_image_record(rgba, w, h)
                global_idx = len(all_records)
                all_records.append(record)
                tier_luts[tier_idx][gid] = global_idx

        num_stored = len(all_records)

        # Build the fixed-size header
        header = bytearray(hdr_size)
        if self._rawHeader is not None and len(self._rawHeader) == hdr_size:
            header[:] = self._rawHeader

        if self.version == 1:
            header[0:4] = MAGIC_V1
            header[4:12] = b"\x00" * 8
            struct.pack_into("<I", header, 12, num_tiers)
            for i, sz in enumerate(sorted_sizes):
                struct.pack_into("<I", header, 16 + 4 * i, sz)
            struct.pack_into("<I", header, off_num_stored, num_stored)
            if self._rawHeader is None:
                _build_v1_tier_range_meta(header, tier_luts)
        else:
            struct.pack_into("<4sIII", header, 0, MAGIC, self.version, self.field3, num_tiers)
            for i, sz in enumerate(sorted_sizes):
                struct.pack_into("<I", header, 16 + 4 * i, sz)
            struct.pack_into("<I", header, off_num_stored, num_stored)
            if self._rawHeader is None:
                _build_resolution_map(header, sorted_sizes)

        # Rebuild tier LUTs
        for tier_idx in range(num_tier_slots):
            slot_base = lut_base + lut_bytes * tier_idx
            if tier_idx < num_tiers:
                header[slot_base : slot_base + lut_bytes] = b"\xff" * lut_bytes
                for gid, global_idx in tier_luts[tier_idx].items():
                    struct.pack_into("<H", header, slot_base + 2 * gid, global_idx)
            else:
                header[slot_base : slot_base + lut_bytes] = b"\x00" * lut_bytes

        # Glyph-offset table + image data (with deduplication)
        record_to_phys: Dict[bytes, int] = {}
        unique_buf: List[bytes] = []
        phys_cumulative = 0
        global_phys_offsets: List[int] = []

        for record in all_records:
            if record in record_to_phys:
                global_phys_offsets.append(record_to_phys[record])
            else:
                record_to_phys[record] = phys_cumulative
                unique_buf.append(record)
                global_phys_offsets.append(phys_cumulative)
                phys_cumulative += len(record)

        for i, phys_off in enumerate(global_phys_offsets):
            off_in_hdr = off_gt + 4 * i
            if off_in_hdr + 4 <= hdr_size:
                struct.pack_into("<I", header, off_in_hdr, phys_off)

        return bytes(header) + b"".join(unique_buf)
