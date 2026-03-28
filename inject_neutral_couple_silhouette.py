"""Inject silhouette support for the neutral couple holding-hands emoji.

AppleColorEmoji ships 26 composite glyphs for U+1F9D1 U+200D U+1F91D U+200D U+1F9D1
(u1F9D1_u1F91D_u1F9D1.{XY}) but provides no silhouette substitution for them in the
morx table.  This script adds 53 new glyphs — one ``.L.XY`` and one ``.R.XY`` per
skin-tone combination, plus one shared ``.LR`` full-silhouette glyph:

  * ``silhouette.u1F9D1.u1F91D.L.XY`` — left person gray, right person in skin combo XY
  * ``silhouette.u1F9D1.u1F91D.R.XY`` — right person gray, left person in skin combo XY
  * ``silhouette.u1F9D1.u1F91D.LR`` — both persons gray (morx cascade target)

Patches the morx NoncontextualMorph subtables so that:

  - All identity pass-through subtables include identity entries for all 52 new glyphs.
  - The Left-silhouette subtable (SubFeatureFlags == 0x00000020) maps each
    ``u1F9D1_u1F91D_u1F9D1.XY`` → ``silhouette.u1F9D1.u1F91D.L.XY``, and cascades
    any already-right-silhouetted ``.R.XY`` glyph → ``.LR`` (full gray).
  - The Right-silhouette subtable (SubFeatureFlags == 0x00000040) maps each
    ``u1F9D1_u1F91D_u1F9D1.XY`` → ``silhouette.u1F9D1.u1F91D.R.XY``, and cascades
    any already-left-silhouetted ``.L.XY`` glyph → ``.LR`` (full gray).
  - When BOTH flags are active the two subtables fire in sequence; the second
    fires on the intermediate ``.L.XY`` or ``.R.XY`` result and produces ``.LR``.

Usage::

    emojifonts-inject-silhouette <assets_dir> <font_path>

``assets_dir`` is the directory that contains per-ppem sub-directories with PNG images
(e.g. ``apple/images``).  For each strike ppem the script looks for
``assets_dir/<ppem>/silhouette.u1F9D1.u1F91D.L.XY.png`` (and ``.R.XY``) and injects
them into sbix.  Missing PNG files are silently skipped.

The script is idempotent: if ``silhouette.u1F9D1.u1F91D.L.11`` is already present in
the font's GlyphOrder the script exits without making any changes.
"""

from __future__ import annotations

import argparse
import copy
import logging
from pathlib import Path

from fontTools import ttLib
from fontTools.ttLib.tables.sbixGlyph import Glyph as SbixGlyph

LOGGER = logging.getLogger(__name__)

# XY suffix order: 11..15, 21..25, ..., 51..55, 66
_SKIN_ROWS = list(range(1, 6))
_XY_SUFFIXES: list[str] = [
    f"{x}{y}" for x in _SKIN_ROWS for y in _SKIN_ROWS
] + ["66"]

# The 26 source composite couple glyphs and their 52 per-XY silhouette targets.
NEUTRAL_COUPLE_GLYPHS: list[str] = [f"u1F9D1_u1F91D_u1F9D1.{xy}" for xy in _XY_SUFFIXES]
ALL_SILHOUETTE_GLYPHS_L: list[str] = [f"silhouette.u1F9D1.u1F91D.L.{xy}" for xy in _XY_SUFFIXES]
ALL_SILHOUETTE_GLYPHS_R: list[str] = [f"silhouette.u1F9D1.u1F91D.R.{xy}" for xy in _XY_SUFFIXES]

# Shared "both silhouette" glyph — morx cascade target when both flags are active.
FULL_SILHOUETTE_GLYPH = "silhouette.u1F9D1.u1F91D.LR"

# Used for idempotency detection.
_IDEMPOTENCY_GLYPH = ALL_SILHOUETTE_GLYPHS_L[0]  # "silhouette.u1F9D1.u1F91D.L.11"

# Donor glyph used to clone the glyf bounding-box placeholder.
_DONOR_GLYPH = "u1F9D1_u1F91D_u1F9D1.66"

# SubFeatureFlags values identifying the silhouette NoncontextualMorph subtables.
_LEFT_SILHOUETTE_FLAGS = 0x00000020
_RIGHT_SILHOUETTE_FLAGS = 0x00000040


def _get_noncontextual_subst(sub) -> dict[str, str] | None:
    """Return the Substitution dict from a NoncontextualMorph subtable, or None."""
    if sub.MorphType != 4:
        return None
    substruct = getattr(sub, "SubStruct", None)
    if substruct is None:
        return None
    return getattr(substruct, "Substitution", None)


def _is_identity_subtable(subst: dict[str, str]) -> bool:
    """True when the subtable is a pass-through (e.g. silhouette.ML → silhouette.ML)."""
    val = subst.get("silhouette.ML")
    return val == "silhouette.ML"


def _add_glyph(font, name: str) -> None:
    """Append *name* to GlyphOrder and clone donor metrics/glyf into it."""
    order = font.getGlyphOrder()
    order.append(name)
    font.setGlyphOrder(order)
    font["glyf"][name] = copy.deepcopy(font["glyf"][_DONOR_GLYPH])
    font["hmtx"].metrics[name] = (800, 0)
    if "vmtx" in font:
        font["vmtx"].metrics[name] = (800, 0)


def inject_silhouette(font_path: Path, assets_dir: Path) -> bool:
    """Inject neutral-couple silhouette support into *font_path*.

    Returns True when changes were made, False when the font was already patched.
    """
    font = ttLib.TTFont(str(font_path))

    if _IDEMPOTENCY_GLYPH in font.getGlyphOrder():
        LOGGER.info("Already patched: %s", font_path)
        return False

    LOGGER.info("Patching %s", font_path)

    all_new_glyphs = ALL_SILHOUETTE_GLYPHS_L + ALL_SILHOUETTE_GLYPHS_R

    # ------------------------------------------------------------------
    # 1. Add all 53 glyphs to GlyphOrder, glyf, hmtx, vmtx
    # ------------------------------------------------------------------
    for glyph_name in all_new_glyphs:
        _add_glyph(font, glyph_name)
    _add_glyph(font, FULL_SILHOUETTE_GLYPH)

    # ------------------------------------------------------------------
    # 2. sbix — inject PNG for each strike where file is available
    # ------------------------------------------------------------------
    all_sbix_glyphs = all_new_glyphs + [FULL_SILHOUETTE_GLYPH]
    for ppem, strike in font["sbix"].strikes.items():
        for glyph_name in all_sbix_glyphs:
            png_path = assets_dir / str(ppem) / f"{glyph_name}.png"
            if not png_path.exists():
                LOGGER.debug("No PNG for %s ppem %s, skipping", glyph_name, ppem)
                continue
            strike.glyphs[glyph_name] = SbixGlyph(
                glyphName=glyph_name,
                originOffsetX=0,
                originOffsetY=0,
                graphicType="png ",
                imageData=png_path.read_bytes(),
            )
            LOGGER.debug("Injected sbix PNG for %s ppem %s", glyph_name, ppem)

    # ------------------------------------------------------------------
    # 3. morx — patch NoncontextualMorph subtables
    # ------------------------------------------------------------------
    # Pre-build per-XY lookup maps.
    _l_map = dict(zip(NEUTRAL_COUPLE_GLYPHS, ALL_SILHOUETTE_GLYPHS_L))
    _r_map = dict(zip(NEUTRAL_COUPLE_GLYPHS, ALL_SILHOUETTE_GLYPHS_R))

    chain = font["morx"].table.MorphChain[0]
    for sub in chain.MorphSubtable:
        subst = _get_noncontextual_subst(sub)
        if subst is None:
            continue

        if _is_identity_subtable(subst):
            for g in all_new_glyphs:
                subst[g] = g
            subst[FULL_SILHOUETTE_GLYPH] = FULL_SILHOUETTE_GLYPH

        if sub.SubFeatureFlags == _LEFT_SILHOUETTE_FLAGS:
            # NN couple → .L.XY (left person gray, right in colour).
            for src, dst in _l_map.items():
                subst[src] = dst
            # .L.XY: identity (left-only silhouette already complete).
            for g in ALL_SILHOUETTE_GLYPHS_L:
                subst[g] = g
            # .R.XY: cascade → full gray (right already silhouetted, now gray left too).
            for g in ALL_SILHOUETTE_GLYPHS_R:
                subst[g] = FULL_SILHOUETTE_GLYPH
            subst[FULL_SILHOUETTE_GLYPH] = FULL_SILHOUETTE_GLYPH
        elif sub.SubFeatureFlags == _RIGHT_SILHOUETTE_FLAGS:
            # NN couple → .R.XY (right person gray, left in colour).
            for src, dst in _r_map.items():
                subst[src] = dst
            # .R.XY: identity (right-only silhouette already complete).
            for g in ALL_SILHOUETTE_GLYPHS_R:
                subst[g] = g
            # .L.XY: cascade → full gray (left already silhouetted, now gray right too).
            for g in ALL_SILHOUETTE_GLYPHS_L:
                subst[g] = FULL_SILHOUETTE_GLYPH
            subst[FULL_SILHOUETTE_GLYPH] = FULL_SILHOUETTE_GLYPH

    # ------------------------------------------------------------------
    # 4. Save
    # ------------------------------------------------------------------
    font.save(str(font_path))
    LOGGER.info("Saved %s", font_path)
    return True


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Inject silhouette support for the neutral couple holding-hands emoji "
            "into an AppleColorEmoji TTF."
        )
    )
    parser.add_argument(
        "assets_dir",
        type=Path,
        help="Directory containing per-ppem PNG sub-directories (e.g. apple/images)",
    )
    parser.add_argument(
        "font_path",
        type=Path,
        help="Input/output TTF file (modified in place)",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        help="Python logging level (default: INFO)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.INFO))

    if not args.font_path.exists():
        LOGGER.error("Font not found: %s", args.font_path)
        return 1

    changed = inject_silhouette(args.font_path, args.assets_dir)
    return 0 if changed is not None else 1


if __name__ == "__main__":
    raise SystemExit(main())
