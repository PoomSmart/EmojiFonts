#!/usr/bin/env python3
"""
catrinity_render.py

Renders all COLR v0 glyphs from Catrinity.otf and CatrinityFlags.otf to SVG
files named after their Unicode codepoint sequences, suitable for rasterization
by rsvg-convert.

Output: svgs/<codepoint_seq>.svg  (e.g. svgs/1f600.svg, svgs/1f1fa_1f1f8.svg)
        All sequences strip U+FE0F variation selectors.

Usage:
    python catrinity_render.py [--out svgs]
"""

import argparse
from pathlib import Path

from fontTools import ttLib
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen

# Glyph names for variation selector / ZWJ that we exclude from output filenames
_SKIP_CODEPOINTS = {0xFE0F, 0xFE0E}

_SCRIPT_DIR = Path(__file__).parent


def _hex_seq(codepoints: tuple[int, ...]) -> str:
    """Return underscore-joined lowercase hex codepoints, stripping FE0F."""
    filtered = [cp for cp in codepoints if cp not in _SKIP_CODEPOINTS]
    return "_".join(f"{cp:x}" for cp in filtered)


def _build_cmap_lookup(font: ttLib.TTFont) -> dict[str, tuple[int, ...]]:
    """Map glyph_name -> (codepoint,) for simple cmap entries."""
    result: dict[str, tuple[int, ...]] = {}
    cmap = font.getBestCmap()
    if cmap:
        for cp, name in cmap.items():
            if name not in result:
                result[name] = (cp,)
    return result


def _build_gsub_ligatures(
    font: ttLib.TTFont,
    glyph_to_cp: dict[str, tuple[int, ...]],
) -> dict[str, tuple[int, ...]]:
    """
    Walk GSUB Type-4 (ligature) subtables and build a map from
    LigGlyph name -> codepoint sequence tuple.

    Only records ligatures where every component has a known codepoint mapping,
    so partial/unknown chains are silently ignored.
    """
    result: dict[str, tuple[int, ...]] = {}
    gsub = font.get("GSUB")
    if gsub is None:
        return result

    for lookup in gsub.table.LookupList.Lookup:
        if lookup.LookupType != 4:
            continue
        for subtable in lookup.SubTable:
            for first_glyph, lig_list in subtable.ligatures.items():
                first_seq = glyph_to_cp.get(first_glyph)
                if first_seq is None:
                    continue
                for lig in lig_list:
                    comp_seqs = [glyph_to_cp.get(c) for c in lig.Component]
                    if any(s is None for s in comp_seqs):
                        continue
                    full_seq: tuple[int, ...] = first_seq
                    for s in comp_seqs:
                        full_seq = full_seq + s  # type: ignore[operator]
                    if lig.LigGlyph not in result:
                        result[lig.LigGlyph] = full_seq
    return result


def _render_colr_glyph(
    glyph_name: str,
    color_layers,
    glyph_set,
    palette: list,
    upm: int,
) -> str | None:
    """
    Render a COLR v0 glyph to an SVG string with a per-glyph square viewBox
    derived from the actual bounding box of all its layers.

    Returns None if the glyph has no drawable layers.
    """
    layers_data: list[tuple[str, str]] = []  # (fill_attr, path_commands)
    x_min = y_min = float("inf")
    x_max = y_max = float("-inf")

    for layer in color_layers:
        # Draw paths
        svg_pen = SVGPathPen(glyph_set)
        try:
            glyph_set[layer.name].draw(svg_pen)
        except Exception:
            continue
        commands = svg_pen.getCommands()
        if not commands:
            continue

        # Accumulate bounding box
        bounds_pen = BoundsPen(glyph_set)
        try:
            glyph_set[layer.name].draw(bounds_pen)
        except Exception:
            pass
        if bounds_pen.bounds:
            bx0, by0, bx1, by1 = bounds_pen.bounds
            x_min = min(x_min, bx0)
            y_min = min(y_min, by0)
            x_max = max(x_max, bx1)
            y_max = max(y_max, by1)

        # colorID 0xFFFF means "use the text foreground color" in COLR v0.
        # For emoji rendering we treat that as opaque black.
        if layer.colorID == 0xFFFF:
            fill_attr = 'fill="#000000"'
        else:
            color = palette[layer.colorID]
            r, g, b, a = color.red, color.green, color.blue, color.alpha
            fill = f"#{r:02x}{g:02x}{b:02x}"
            fill_attr = f'fill="{fill}"'
            if a < 255:
                opacity = f"{a / 255:.4f}".rstrip("0").rstrip(".")
                fill_attr += f' fill-opacity="{opacity}"'

        layers_data.append((fill_attr, commands))

    if not layers_data or x_min == float("inf"):
        return None

    # Compute a centered square viewBox with 5% padding on each side.
    #
    # OTF uses y-up; SVG uses y-down.  We want SVG (0,0) to map to OTF top-left
    # corner of the padded square, so we use the transform:
    #   translate(-vx, vy_top) scale(1,-1)
    # which maps OTF (x, y) → SVG (x - vx, vy_top - y).
    # The padded square in OTF space spans [vx, vx+side] × [vy_bot, vy_top].
    cx = (x_min + x_max) / 2
    cy = (y_min + y_max) / 2
    side = max(x_max - x_min, y_max - y_min)
    margin = side * 0.05
    half = side / 2 + margin
    svg_size = 2 * half

    vx = cx - half
    vy_top = cy + half  # OTF top of the padded square

    paths = "\n".join(f'  <path {fa} d="{d}"/>' for fa, d in layers_data)
    tx = -vx
    ty = vy_top
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_size:.2f} {svg_size:.2f}">\n'
        f' <g transform="translate({tx:.2f},{ty:.2f}) scale(1,-1)">\n'
        f"{paths}\n"
        f" </g>\n"
        f"</svg>\n"
    )


def render_font(
    otf_path: Path,
    out_dir: Path,
    extra_glyph_map: dict[str, tuple[int, ...]] | None = None,
) -> int:
    """
    Render all COLR glyphs from *otf_path* to SVG files in *out_dir*.

    *extra_glyph_map* can supply additional glyph->seq entries (e.g. from a
    companion font's cmap) to ensure every COLR glyph gets a filename.

    Returns the count of SVGs written.
    """
    font = ttLib.TTFont(str(otf_path))
    colr = font.get("COLR")
    if colr is None:
        print(f"[warn] {otf_path.name}: no COLR table, skipping")
        return 0

    glyph_set = font.getGlyphSet()
    upm = font["head"].unitsPerEm
    palette = font["CPAL"].palettes[0]

    # Build glyph -> codepoint sequence maps
    glyph_to_cp = _build_cmap_lookup(font)
    if extra_glyph_map:
        for name, seq in extra_glyph_map.items():
            if name not in glyph_to_cp:
                glyph_to_cp[name] = seq

    lig_map = _build_gsub_ligatures(font, glyph_to_cp)
    glyph_to_cp.update(lig_map)

    written = 0
    skipped_no_seq = 0
    skipped_empty = 0

    for glyph_name, color_layers in colr.ColorLayers.items():
        seq = glyph_to_cp.get(glyph_name)
        if seq is None:
            skipped_no_seq += 1
            continue

        hex_name = _hex_seq(seq)
        if not hex_name:
            skipped_no_seq += 1
            continue

        svg = _render_colr_glyph(glyph_name, color_layers, glyph_set, palette, upm)
        if svg is None:
            skipped_empty += 1
            continue

        out_path = out_dir / f"{hex_name}.svg"
        out_path.write_text(svg, encoding="utf-8")
        written += 1

    print(f"[{otf_path.name}] written={written}, no_seq={skipped_no_seq}, empty={skipped_empty}")
    return written


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Render Catrinity COLR glyphs to SVGs.")
    parser.add_argument("--out", type=Path, default=Path("svgs"), help="Output directory (default: svgs/)")
    parser.add_argument(
        "--fonts",
        nargs="+",
        type=Path,
        default=None,
        help="OTF paths to render (default: Catrinity.otf CatrinityFlags.otf alongside this script)",
    )
    args = parser.parse_args(argv)

    script_dir = _SCRIPT_DIR
    if args.fonts:
        font_paths = args.fonts
    else:
        font_paths = [
            script_dir / "Catrinity.otf",
            script_dir / "CatrinityFlags.otf",
        ]

    args.out.mkdir(parents=True, exist_ok=True)

    total = 0
    for fp in font_paths:
        if not fp.exists():
            print(f"[warn] font not found: {fp}, skipping")
            continue
        total += render_font(fp, args.out)

    print(f"Total SVGs written: {total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
