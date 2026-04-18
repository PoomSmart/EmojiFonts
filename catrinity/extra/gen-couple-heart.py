"""Generate person-half PNGs for couple-with-heart emoji.

Works at **SVG level** using the rendered SVGs in ``../svgs/`` to cleanly
separate left-person subpaths from heart+right-person subpaths.

Each ``<path>`` element's compound ``d`` is split into individual subpaths on
``M`` commands.  Each subpath's first ``M`` x-coordinate + ``translate-x``
from the ``<g>`` transform gives its canvas x; subpaths with canvas x <
canvas-centre go to the left SVG, the rest (including the heart) to the right.

Output (convention matches twemoji):
  .l  = left-person paths only
  .r  = heart decoration + right-person paths

Prerequisites
-------------
``../svgs/`` must exist (produced by ``catrinity_render.py``).  In normal
operation ``catrinity.sh`` runs this script after ``svg-to-png.sh`` but before
the SVG directory is cleaned up.

Run from catrinity/extra/.
"""

import os
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image

from shared import SKINS, extra_images, get_ppems, to_silhouette

SVG_DIR = Path("../svgs")
_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", _NS)


# ── SVG helpers ────────────────────────────────────────────────────────────────


def _parse_tx(transform: str) -> float:
    """Extract the translate-x from a 'translate(tx,ty) scale(1,-1)' string."""
    m = re.search(r"translate\(\s*([-+]?\d*\.?\d+)", transform)
    return float(m.group(1)) if m else 0.0


def _split_subpaths(d: str) -> list[str]:
    """Split a compound SVG path data string into individual subpaths."""
    return [p.strip() for p in re.split(r"(?=[Mm])", d.strip()) if p.strip()]


def _subpath_x_mean(subpath: str) -> float | None:
    """Return the mean x coordinate across all control points in *subpath*.

    Extracts every number from the path data and treats even-indexed values
    as x coordinates (valid for M/Q/L/Z which are all paired x,y commands).
    Using the mean rather than just the first M avoids misclassifying paths
    whose first M lies near the centre but whose body extends far to one side
    (e.g. the semi-transparent heart shadow).
    """
    nums = re.findall(r"[-+]?\d+(?:\.\d+)?", subpath)
    if not nums:
        return None
    xs = [float(nums[i]) for i in range(0, len(nums), 2)]
    return sum(xs) / len(xs) if xs else None


def split_couple_svg(svg_path: Path) -> tuple[ET.Element, ET.Element] | None:
    """Return *(left_root, right_root)* by splitting an SVG at canvas centre.

    Each ``<path>`` element's compound ``d`` is split into individual subpaths.
    Subpaths with canvas x < centre → left; subpaths at or beyond centre →
    right.  Unclassifiable subpaths go to both.

    Returns ``None`` when *svg_path* does not exist.
    """
    if not svg_path.exists():
        return None

    tree = ET.parse(svg_path)
    root = tree.getroot()

    # catrinity_render.py always writes viewBox="0 0 svg_size svg_size"
    vb = root.get("viewBox", "0 0 100 100").split()
    svg_size = float(vb[2]) if len(vb) >= 3 else 100.0
    centre = svg_size / 2.0

    # Single <g> child holds all <path> elements
    g = root.find(f"{{{_NS}}}g")
    if g is None:
        g = root[0] if len(root) else None
    if g is None:
        return None

    tx = _parse_tx(g.get("transform", ""))

    left_elems: list[ET.Element] = []
    right_elems: list[ET.Element] = []

    for path in g:
        d = path.get("d", "")
        left_parts: list[str] = []
        right_parts: list[str] = []

        for sp in _split_subpaths(d):
            font_x = _subpath_x_mean(sp)
            if font_x is None:
                # Can't classify — include in both
                left_parts.append(sp)
                right_parts.append(sp)
                continue
            if font_x + tx < centre:
                left_parts.append(sp)
            else:
                right_parts.append(sp)

        attrib = path.attrib.copy()
        if left_parts:
            e = ET.Element(path.tag, attrib)
            e.set("d", " ".join(left_parts))
            left_elems.append(e)
        if right_parts:
            e = ET.Element(path.tag, attrib)
            e.set("d", " ".join(right_parts))
            right_elems.append(e)

    def _wrap(elems: list[ET.Element]) -> ET.Element:
        r = ET.Element(root.tag, root.attrib.copy())
        new_g = ET.Element(g.tag, g.attrib.copy())
        for e in elems:
            new_g.append(e)
        r.append(new_g)
        return r

    return _wrap(left_elems), _wrap(right_elems)


def _rsvg(svg_root: ET.Element, out_path: Path, size: int) -> None:
    """Rasterise *svg_root* to *out_path* at *size* px using rsvg-convert."""
    fd, tmp = tempfile.mkstemp(suffix=".svg")
    try:
        with os.fdopen(fd, "w") as f:
            ET.ElementTree(svg_root).write(f, encoding="unicode", xml_declaration=False)
        subprocess.run(
            ["rsvg-convert", "-a", "-h", str(size), tmp, "-o", str(out_path)],
            check=True,
            stderr=subprocess.DEVNULL,
        )
    finally:
        os.unlink(tmp)


def _sil(svg_root: ET.Element, out_path: Path, size: int) -> None:
    """Rasterise, apply flat-gray silhouette colouring, and save."""
    tmp_png = out_path.with_name("_tmp_" + out_path.name)
    _rsvg(svg_root, tmp_png, size)
    to_silhouette(Image.open(tmp_png).convert("RGBA")).save(out_path)
    tmp_png.unlink()


def _sil_right(svg_root: ET.Element, out_path: Path, size: int) -> None:
    """Rasterise a right-half silhouette: person paths grayed, heart kept colored.

    For the black compound path (person outline + heart outline as subpaths),
    subpaths whose mean canvas-x < svg_size*0.55 are the heart outline and stay
    black; subpaths beyond that threshold are the person outline and turn gray.
    """
    import copy

    root = copy.deepcopy(svg_root)

    vb = root.get("viewBox", "0 0 100 100").split()
    svg_size = float(vb[2]) if len(vb) >= 3 else 100.0
    heart_threshold = svg_size * 0.55

    g = root.find(f"{{{_NS}}}g")
    if g is not None:
        tx = _parse_tx(g.get("transform", ""))
        heart_paths_to_add: list[ET.Element] = []

        for path in g:
            fill = path.get("fill", "")
            # Heart body (red) and semi-transparent shadow stay as-is.
            if fill == "#eb0000" or path.get("fill-opacity") is not None:
                continue

            if fill == "#000000":
                # Split compound path: heart outline subpaths (mean canvas-x near
                # centre) stay black; person outline subpaths become gray.
                heart_subs: list[str] = []
                person_subs: list[str] = []
                for sp in _split_subpaths(path.get("d", "")):
                    mx = _subpath_x_mean(sp)
                    canvas_x = (mx + tx) if mx is not None else svg_size
                    if canvas_x < heart_threshold:
                        heart_subs.append(sp)
                    else:
                        person_subs.append(sp)

                if person_subs:
                    path.set("fill", "#7e7e7e")
                    path.set("d", " ".join(person_subs))
                # If there were no person subpaths, the path is all heart — leave black.

                if heart_subs:
                    hp = ET.Element(path.tag, {"fill": "#000000", "d": " ".join(heart_subs)})
                    heart_paths_to_add.append(hp)
            else:
                # Person paths (face, eyes, hair) → gray.
                path.set("fill", "#7e7e7e")

        for hp in heart_paths_to_add:
            g.append(hp)

    _rsvg(root, out_path, size)


# ── Generation ─────────────────────────────────────────────────────────────────

if not SVG_DIR.exists():
    raise RuntimeError(f"{SVG_DIR} not found — run catrinity_render.py (or catrinity.sh) first")

for ppem in get_ppems():
    dst = extra_images(ppem)

    # ── 1f491 (woman+man with heart) ─────────────────────────────────────────
    for skin in SKINS:
        result = split_couple_svg(SVG_DIR / f"1f491{skin}.svg")
        if result is None:
            continue
        l_root, r_root = result
        # Neutral-person halves
        _rsvg(l_root, dst / f"1f9d1{skin}_2764.l.png", ppem)
        _rsvg(r_root, dst / f"1f9d1{skin}_2764.r.png", ppem)
        # Gendered halves: 1f491 = woman left, man right
        _rsvg(l_root, dst / f"1f469{skin}_2764.l.png", ppem)
        _rsvg(r_root, dst / f"1f468{skin}_2764.r.png", ppem)

    # Silhouettes from no-skin version
    result = split_couple_svg(SVG_DIR / "1f491.svg")
    if result is not None:
        sl, sr = result
        _sil(sl, dst / "silhouette_1f9d1_2764.l.png", ppem)
        _sil_right(sr, dst / "silhouette_1f9d1_2764.r.png", ppem)
        _sil(sl, dst / "silhouette_1f469_2764.l.png", ppem)
        _sil_right(sr, dst / "silhouette_1f468_2764.r.png", ppem)

    # ── Man+man / woman+woman with heart (if Catrinity has them) ─────────────
    for glyph, stem_base in [
        ("1f468", "1f468_200d_2764_200d_1f468"),
        ("1f469", "1f469_200d_2764_200d_1f469"),
    ]:
        for skin in SKINS:
            result = split_couple_svg(SVG_DIR / f"{stem_base}{skin}.svg")
            if result is None:
                continue
            l_root, r_root = result
            _rsvg(l_root, dst / f"{glyph}{skin}_2764.l.png", ppem)
            _rsvg(r_root, dst / f"{glyph}{skin}_2764.r.png", ppem)

        result = split_couple_svg(SVG_DIR / f"{stem_base}.svg")
        if result is not None:
            sl, sr = result
            _sil(sl, dst / f"silhouette_{glyph}_2764.l.png", ppem)
            _sil_right(sr, dst / f"silhouette_{glyph}_2764.r.png", ppem)
