"""Extract every emoji from a CCF sidecar to a user-provided output directory.

The iOS version is auto-detected from the CCF magic bytes:
  - b'\\x40\\x30\\x20\\x10'  →  v1 (iOS 8.x)
  - b'fcca'               →  v2 (iOS 9.x)

Output layout:
    <output>/<pixelSize>/<glyphName>.png

Usage:
    python extract_ccf.py --output out_dir
    python extract_ccf.py path/to/font.ccf --output out_dir
"""

import argparse
import pathlib
import sys

from fontTools.ttLib import TTFont

from accf import AccfTable, MAGIC, MAGIC_V1

SCRIPT_DIR = pathlib.Path(__file__).parent

_VERSION_LABELS = {
    MAGIC: "9.x",
    MAGIC_V1: "8.x",
}


def main():
    parser = argparse.ArgumentParser(description="Extract PNG strikes from a CCF file")
    parser.add_argument(
        "ccf_path",
        nargs="?",
        type=pathlib.Path,
        default=SCRIPT_DIR / "AppleColorEmoji@2x.ccf",
        help="Path to .ccf file (default: AppleColorEmoji@2x.ccf next to this script)",
    )
    parser.add_argument(
        "-o",
        "--output",
        required=True,
        type=pathlib.Path,
        help="Output directory where extracted images will be written",
    )

    args = parser.parse_args()

    ccf_path = args.ccf_path
    ttf_path = ccf_path.with_suffix(".ttf")

    ccf_bytes = ccf_path.read_bytes()
    magic = ccf_bytes[:4]
    version_label = _VERSION_LABELS.get(magic)
    if version_label is None:
        print(f"Unknown CCF magic {magic!r}, cannot determine version.", file=sys.stderr)
        sys.exit(1)

    out_dir = args.output
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"CCF:     {ccf_path}  (iOS {version_label})")
    print(f"TTF:     {ttf_path}")
    print(f"Output:  {out_dir}")

    ttf = TTFont(ttf_path, lazy=True)
    glyph_order = ttf.getGlyphOrder()

    accf = AccfTable()
    accf.decompile(ccf_bytes, glyph_order)

    sizes = sorted(accf.strikes.keys())
    print(f"Strikes: {sizes} px")

    total = 0
    for px in sizes:
        strike = accf.strikes[px]
        px_dir = out_dir / str(px)
        px_dir.mkdir(parents=True, exist_ok=True)

        glyphs = list(strike.glyphs.keys())
        print(f"  {px}px — {len(glyphs)} glyph(s) …", end="", flush=True)
        for name in glyphs:
            png = strike.glyphs[name].imageData
            (px_dir / f"{name}.png").write_bytes(png)
            total += 1
        print(" done")

    print(f"\nExtracted {total} image(s) to {out_dir}/")


if __name__ == "__main__":
    main()
