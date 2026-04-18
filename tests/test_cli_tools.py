"""Minimal regression tests covering the public CLIs."""

from __future__ import annotations

import binascii
import io
import json
import shutil
import sys
import textwrap
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest
from fontTools import ttLib
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import extractor
import inject_neutral_couple_silhouette as _inj
import remove_class3
import shift_multi


@pytest.fixture
def sample_png_hex() -> str:
    img = Image.new("RGBA", (4, 4), (255, 0, 0, 255))
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return binascii.hexlify(buffer.getvalue()).decode("ascii")


def _write_file(path: Path, content: str) -> Path:
    path.write_text(content, encoding="utf-8")
    return path


def test_extract_images_handles_flip_glyph(tmp_path: Path, sample_png_hex: str) -> None:
    sbix_content = textwrap.dedent(
        f"""<?xml version="1.0" encoding="UTF-8"?>
<ttFont>
  <sbix>
    <strike>
      <ppem value="40"/>
      <glyph name="u1F600" graphicType="png ">
        <hexdata>{sample_png_hex}</hexdata>
      </glyph>
      <glyph name="u1F603" graphicType="flip">
        <ref glyphname="u1F600"/>
      </glyph>
    </strike>
  </sbix>
</ttFont>
"""
    )
    sbix_path = _write_file(tmp_path / "sbix.ttx", sbix_content)
    output_dir = tmp_path / "out"

    extractor.extract_images(output_dir, sbix_path, sbix_path, allowed_strikes=[40])

    base = output_dir / "40" / "u1F600.png"
    flipped = output_dir / "40" / "u1F603.png"
    assert base.exists()
    assert flipped.exists()

    with Image.open(base) as base_img, Image.open(flipped) as flipped_img:
        assert base_img.size == flipped_img.size == (4, 4)


def test_remove_class_three_entries_strips_non_outline(tmp_path: Path) -> None:
    gdef_content = textwrap.dedent(
        """<?xml version="1.0" encoding="UTF-8"?>
<ttFont>
  <GDEF>
    <GlyphClassDef>
      <ClassDef glyph="outline.example" class="1"/>
      <ClassDef glyph="foo" class="3"/>
      <ClassDef glyph="outline.bar" class="2"/>
      <ClassDef glyph="baz" class="3"/>
    </GlyphClassDef>
  </GDEF>
</ttFont>
"""
    )
    gdef_path = _write_file(tmp_path / "gdef.ttx", gdef_content)

    removed = remove_class3.remove_class_three_entries(gdef_path)
    assert removed == 2

    tree = ET.parse(str(gdef_path))
    glyphs = [node.attrib["glyph"] for node in tree.iterfind(".//ClassDef")]
    assert glyphs == ["outline.example", "outline.bar"]


def test_apply_overrides_updates_metrics(tmp_path: Path) -> None:
    overrides_data = {
        "u1F468.1.L": {"width": 400, "lsb": 0},
        "u1F468.1.R": {"width": 400, "lsb": -400},
    }
    overrides_path = tmp_path / "overrides.json"
    overrides_path.write_text(
        json.dumps(overrides_data, indent=2) + "\n",
        encoding="utf-8",
    )

    hmtx_content = textwrap.dedent(
        """<?xml version="1.0" encoding="UTF-8"?>
<ttFont>
  <hmtx>
    <mtx name="u1F468.1.L" width="300" lsb="10"/>
    <mtx name="u1F468.1.R" width="300" lsb="-10"/>
  </hmtx>
</ttFont>
"""
    )
    hmtx_path = _write_file(tmp_path / "hmtx.ttx", hmtx_content)

    overrides = shift_multi.load_overrides(overrides_path)
    applied = shift_multi.apply_overrides(hmtx_path, overrides)

    assert applied == len(overrides_data)

    tree = ET.parse(str(hmtx_path))
    metrics = {node.attrib["name"]: (node.attrib["width"], node.attrib["lsb"]) for node in tree.iterfind(".//mtx")}
    assert metrics == {
        "u1F468.1.L": ("400", "0"),
        "u1F468.1.R": ("400", "-400"),
    }

    with pytest.raises(KeyError):
        shift_multi.apply_overrides(hmtx_path, {"missing": {"width": 1, "lsb": 2}})


# ---------------------------------------------------------------------------
# inject_neutral_couple_silhouette tests
# ---------------------------------------------------------------------------

_REAL_FONT = Path(__file__).resolve().parents[1] / "common" / "AppleColorEmoji_iOS_00.ttf"


def _strip_silhouette_from_font(font_path: Path) -> None:
    """Remove previously-injected silhouette glyphs so injection tests start from an unpatched state."""
    all_silhouette = set(_inj.ALL_SILHOUETTE_GLYPHS_L + _inj.ALL_SILHOUETTE_GLYPHS_R + [_inj.FULL_SILHOUETTE_GLYPH])
    font = ttLib.TTFont(str(font_path))
    if not any(g in font.getGlyphOrder() for g in all_silhouette):
        return  # already clean

    # Force-decompile these tables BEFORE shrinking GlyphOrder.  Each table
    # decompiles lazily on first access using the current GlyphOrder; if
    # GlyphOrder is shortened first the binary size no longer matches and
    # fontTools raises an IndexError when it tries to decompile later.
    hmtx = font["hmtx"]
    vmtx = font["vmtx"] if "vmtx" in font else None
    glyf_table = font["glyf"]
    sbix = font["sbix"]
    morx = font["morx"]

    font.setGlyphOrder([g for g in font.getGlyphOrder() if g not in all_silhouette])

    for g in all_silhouette:
        if g in glyf_table.glyphs:
            del glyf_table.glyphs[g]

    for g in all_silhouette:
        hmtx.metrics.pop(g, None)
    if vmtx is not None:
        for g in all_silhouette:
            vmtx.metrics.pop(g, None)

    for strike in sbix.strikes.values():
        for g in all_silhouette:
            strike.glyphs.pop(g, None)

    chain = morx.table.MorphChain[0]
    for sub in chain.MorphSubtable:
        subst = _inj._get_noncontextual_subst(sub)
        if subst is None:
            continue
        to_delete = [k for k, v in subst.items() if k in all_silhouette or v in all_silhouette]
        for k in to_delete:
            del subst[k]

    font.save(str(font_path))


@pytest.fixture(scope="session")
def _unpatched_font_path(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Strip silhouette glyphs from the real font once per session; tests copy from here."""
    if not _REAL_FONT.exists():
        pytest.skip("Compiled font not available – run prepare.sh first")
    dst = tmp_path_factory.mktemp("font_cache") / "AppleColorEmoji_iOS_00_unpatched.ttf"
    shutil.copy(_REAL_FONT, dst)
    _strip_silhouette_from_font(dst)
    return dst


@pytest.fixture(scope="session")
def _patched_font_path(_unpatched_font_path: Path, tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Inject silhouette support once per session for read-only assertion tests."""
    dst = tmp_path_factory.mktemp("font_cache") / "AppleColorEmoji_iOS_00_patched.ttf"
    shutil.copy(_unpatched_font_path, dst)
    assets_dir = tmp_path_factory.mktemp("assets_patched")
    _inj.inject_silhouette(dst, assets_dir)
    return dst


@pytest.fixture
def font_copy(tmp_path: Path, _unpatched_font_path: Path) -> Path:
    """Return a per-test mutable copy of the unpatched font (fast — no strip needed)."""
    dst = tmp_path / "AppleColorEmoji_iOS_00.ttf"
    shutil.copy(_unpatched_font_path, dst)
    return dst


def test_inject_silhouette_adds_glyph_and_metrics(_patched_font_path: Path) -> None:
    font = ttLib.TTFont(str(_patched_font_path))
    # Spot-check first (.11) and last (.66) of each direction.
    sample = (
        _inj.ALL_SILHOUETTE_GLYPHS_L[0],
        _inj.ALL_SILHOUETTE_GLYPHS_L[-1],
        _inj.ALL_SILHOUETTE_GLYPHS_R[0],
        _inj.ALL_SILHOUETTE_GLYPHS_R[-1],
    )
    for glyph_name in sample:
        assert glyph_name in font.getGlyphOrder()
        assert font["hmtx"].metrics[glyph_name] == (800, 0)
        if "vmtx" in font:
            assert font["vmtx"].metrics[glyph_name] == (800, 0)


def test_inject_silhouette_morx_subtables(_patched_font_path: Path) -> None:
    font = ttLib.TTFont(str(_patched_font_path))
    chain = font["morx"].table.MorphChain[0]

    left_subst: dict[str, str] | None = None
    right_subst: dict[str, str] | None = None
    identity_substs: list[dict[str, str]] = []

    for sub in chain.MorphSubtable:
        subst = _inj._get_noncontextual_subst(sub)
        if subst is None:
            continue
        if sub.SubFeatureFlags == _inj._LEFT_SILHOUETTE_FLAGS:
            left_subst = subst
        elif sub.SubFeatureFlags == _inj._RIGHT_SILHOUETTE_FLAGS:
            right_subst = subst
        elif subst.get("silhouette.ML") == "silhouette.ML":
            identity_substs.append(subst)

    assert left_subst is not None, "Left-silhouette subtable not found"
    assert right_subst is not None, "Right-silhouette subtable not found"

    for src, dst_l, dst_r in zip(
        _inj.NEUTRAL_COUPLE_GLYPHS, _inj.ALL_SILHOUETTE_GLYPHS_L, _inj.ALL_SILHOUETTE_GLYPHS_R
    ):
        assert left_subst.get(src) == dst_l, f"{src} not mapped to {dst_l} in Left morx subtable"
        assert right_subst.get(src) == dst_r, f"{src} not mapped to {dst_r} in Right morx subtable"

    for subst in identity_substs:
        for g in _inj.ALL_SILHOUETTE_GLYPHS_L[:2] + _inj.ALL_SILHOUETTE_GLYPHS_R[:2]:
            assert subst.get(g) == g


def test_inject_silhouette_idempotent(tmp_path: Path, font_copy: Path) -> None:
    assets_dir = tmp_path / "images"
    assets_dir.mkdir()

    assert _inj.inject_silhouette(font_copy, assets_dir) is True
    assert _inj.inject_silhouette(font_copy, assets_dir) is False


def test_inject_silhouette_injects_png(tmp_path: Path, font_copy: Path) -> None:
    assets_dir = tmp_path / "images"
    (assets_dir / "64").mkdir(parents=True)

    # Test first (.11) and last (.66) from each direction — 4 PNGs total.
    test_glyphs = (
        _inj.ALL_SILHOUETTE_GLYPHS_L[0],
        _inj.ALL_SILHOUETTE_GLYPHS_L[-1],
        _inj.ALL_SILHOUETTE_GLYPHS_R[0],
        _inj.ALL_SILHOUETTE_GLYPHS_R[-1],
    )
    png_bytes: dict[str, bytes] = {}
    for glyph_name in test_glyphs:
        img = Image.new("RGBA", (64, 64), (128, 128, 128, 255))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        data = buf.getvalue()
        (assets_dir / "64" / f"{glyph_name}.png").write_bytes(data)
        png_bytes[glyph_name] = data

    _inj.inject_silhouette(font_copy, assets_dir)

    font = ttLib.TTFont(str(font_copy))
    for glyph_name in test_glyphs:
        assert glyph_name in font["sbix"].strikes[64].glyphs
        sil = font["sbix"].strikes[64].glyphs[glyph_name]
        assert sil.graphicType == "png "
        assert sil.imageData == png_bytes[glyph_name]
