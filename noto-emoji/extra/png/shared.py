"""Shared PNG-based utilities for Noto 3D extra composite generation.

3D ships combined multi-person glyphs as PNGs (no SVG layers). Extra
generators split those into Apple-style left/right halves for the sbix table.

Scripts in this folder are run from noto-emoji/extra/:
  - Source couple PNGs:  ../images/160/emoji_u{stem}.png
  - Output half PNGs:    images/160/{stem}.png
"""

from __future__ import annotations

import colorsys
import sys
from pathlib import Path
from typing import Literal

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from split_emoji import find_valley, split_at, split_by_components, split_by_geodesic

_GRAY: tuple[int, int, int] = (0x7E, 0x7E, 0x7E)

PPEM = 160
SKINS: list[str] = ["", "_1f3fb", "_1f3fc", "_1f3fd", "_1f3fe", "_1f3ff"]

SplitMethod = Literal["geodesic", "components", "valley", "heart", "heart-geodesic"]


def main_images() -> Path:
    return Path("../images") / str(PPEM)


def extra_images() -> Path:
    d = Path("images") / str(PPEM)
    d.mkdir(parents=True, exist_ok=True)
    return d


def src_png(stem: str) -> Path:
    """Path to a main Noto PNG (`emoji_u{stem}.png`)."""
    return main_images() / f"emoji_u{stem}.png"


def half_name(code: str, skin: str, side: str, joiner: str | None = None) -> str:
    if joiner is None:
        return f"{code}{skin}.{side}.png"
    return f"{code}{skin}_{joiner}.{side}.png"


def _is_heart_color(r: int, g: int, b: int) -> bool:
    """True for the magenta/pink 3D Noto heart (not orange skin)."""
    h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
    if s < 0.35 or v < 0.45:
        return False
    return h >= 0.78 or h <= 0.02


def to_silhouette(img: Image.Image, keep_heart: bool = False) -> Image.Image:
    """Recolour opaque pixels to flat silhouette gray, optionally keeping heart pixels."""
    out = Image.new("RGBA", img.size)
    src = img.load()
    dst = out.load()
    w, h = img.size
    y_limit = int(h * 0.45) if keep_heart else -1
    for y in range(h):
        for x in range(w):
            r, g, b, a = src[x, y]
            if a == 0:
                continue
            if keep_heart and y < y_limit and _is_heart_color(r, g, b):
                dst[x, y] = (r, g, b, a)
            else:
                dst[x, y] = (*_GRAY, a)
    return out


def _split_people(img: Image.Image, method: SplitMethod) -> tuple[Image.Image, Image.Image]:
    try:
        if method == "geodesic":
            return split_by_geodesic(img)
        if method == "components":
            return split_by_components(img)
        if method == "valley":
            return split_at(img, find_valley(img))
    except ValueError:
        pass
    return split_at(img, find_valley(img))


def split_with_heart(img: Image.Image, people_method: SplitMethod = "components") -> tuple[Image.Image, Image.Image]:
    """Split people, then attach detected heart pixels to the right half."""
    w, h = img.size
    src = img.load()
    y_limit = int(h * 0.45)
    heart_pixels: list[tuple[int, int]] = []
    people = img.copy()
    pp = people.load()
    for y in range(y_limit):
        for x in range(w):
            r, g, b, a = src[x, y]
            if a > 10 and _is_heart_color(r, g, b):
                heart_pixels.append((x, y))
                pp[x, y] = (0, 0, 0, 0)

    method = people_method if people_method != "heart" else "components"
    left, right = _split_people(people, method)
    lp, rp = left.load(), right.load()
    for x, y in heart_pixels:
        rp[x, y] = src[x, y]
        lp[x, y] = (0, 0, 0, 0)
    for y in range(y_limit):
        for x in range(w):
            r, g, b, a = lp[x, y]
            if a > 10 and _is_heart_color(r, g, b):
                rp[x, y] = lp[x, y]
                lp[x, y] = (0, 0, 0, 0)
    return left, right


def split_png(src: Path, method: SplitMethod = "geodesic") -> tuple[Image.Image, Image.Image] | None:
    """Split *src* into (left, right) full-canvas RGBA images.

    Returns ``None`` if the source file does not exist.
    """
    if not src.exists():
        print(f"  warning: missing {src}", file=sys.stderr)
        return None
    img = Image.open(src).convert("RGBA")
    if method == "heart":
        return split_with_heart(img, people_method="components")
    if method == "heart-geodesic":
        return split_with_heart(img, people_method="geodesic")
    return _split_people(img, method)


def split_and_save(
    stem: str,
    left_code: str,
    right_code: str,
    skin: str,
    *,
    joiner: str | None = None,
    method: SplitMethod = "geodesic",
    silhouette: bool = False,
    keep_heart: bool = False,
) -> bool:
    """Split ``emoji_u{stem}.png`` and write Apple-named halves (and optional silhouettes)."""
    pair = split_png(src_png(stem), method)
    if pair is None:
        return False
    left, right = pair
    dst = extra_images()
    left.save(dst / half_name(left_code, skin, "l", joiner))
    right.save(dst / half_name(right_code, skin, "r", joiner))
    if silhouette and skin == "":
        prefix = f"{left_code}_{joiner}" if joiner else left_code
        rprefix = f"{right_code}_{joiner}" if joiner else right_code
        to_silhouette(left).save(dst / f"silhouette_{prefix}.l.png")
        to_silhouette(right, keep_heart=keep_heart).save(dst / f"silhouette_{rprefix}.r.png")
    return True
