"""Shared PNG-based utilities for Catrinity extra composite generation.

All other vendor extra/ scripts manipulate *source* SVG element children.
Catrinity has no source SVGs — its images are rendered from COLR/OTF by
catrinity_render.py and then rasterised to images/{ppem}/.  Therefore all
Catrinity extra generators work at the **PNG level**, splitting already-
rendered PNGs to produce per-person-half images for Apple's sbix table.

Scripts in this folder are run from the catrinity/extra/ directory:
  - Source couple PNGs:  ../images/{ppem}/{stem}.png
  - Output half PNGs:    images/{ppem}/{stem}.png   (this extra/ subtree)
"""

import os
from pathlib import Path

from PIL import Image

_GRAY: tuple[int, int, int] = (0x7E, 0x7E, 0x7E)

SKINS: list[str] = ["", "_1f3fb", "_1f3fc", "_1f3fd", "_1f3fe", "_1f3ff"]


def get_ppems() -> list[int]:
    """Return ppem sizes from IMAGE_SIZES env (default: 160 96 64 40)."""
    return [int(p) for p in os.environ.get("IMAGE_SIZES", "160 96 64 40").split()]


def main_images(ppem: int) -> Path:
    """Path to the main Catrinity images directory for *ppem*."""
    return Path("../images") / str(ppem)


def extra_images(ppem: int) -> Path:
    """Path to the extra output directory for *ppem* (created if absent)."""
    d = Path("images") / str(ppem)
    d.mkdir(parents=True, exist_ok=True)
    return d


def to_silhouette(img: Image.Image) -> Image.Image:
    """Recolour every opaque pixel to flat silhouette gray, preserving alpha."""
    alpha = img.split()[3]
    gray = Image.new("RGBA", img.size, (*_GRAY, 255))
    gray.putalpha(alpha)
    return gray


def _valley_x(img: Image.Image) -> int:
    """Return the x column with the lowest total alpha in the central half."""
    w, h = img.size
    alpha = img.split()[3]
    col_sums = [sum(alpha.getpixel((x, y)) for y in range(h)) for x in range(w)]
    lo, hi = w // 4, 3 * w // 4
    return min(range(lo, hi), key=lambda x: col_sums[x])


def split_png(
    src: Path,
    split_x: int | None = None,
) -> tuple[Image.Image, Image.Image] | None:
    """Valley-split *src* PNG into (left, right) full-canvas RGBA images.

    Returns ``None`` if the source file does not exist.  Both returned images
    have the same canvas size as the original; the complement half is
    transparent.
    """
    if not src.exists():
        return None
    img = Image.open(src).convert("RGBA")
    w, h = img.size
    x = split_x if split_x is not None else _valley_x(img)
    left = Image.new("RGBA", (w, h))
    left.paste(img.crop((0, 0, x + 1, h)), (0, 0))
    right = Image.new("RGBA", (w, h))
    right.paste(img.crop((x + 1, 0, w, h)), (x + 1, 0))
    return left, right


def split_and_save(
    src: Path,
    left_dst: Path,
    right_dst: Path,
    *,
    left_sil_dst: Path | None = None,
    right_sil_dst: Path | None = None,
) -> bool:
    """Split *src* and write left/right (and optional silhouette) halves.

    Returns ``True`` if the source existed and splitting succeeded.
    """
    result = split_png(src)
    if result is None:
        return False
    left, right = result
    left.save(left_dst)
    right.save(right_dst)
    if left_sil_dst is not None:
        to_silhouette(left).save(left_sil_dst)
    if right_sil_dst is not None:
        to_silhouette(right).save(right_sil_dst)
    return True
