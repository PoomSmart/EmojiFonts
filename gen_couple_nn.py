"""Generate neutral-couple (NN) per-skin-combo silhouette PNGs for a themed emoji font.

This module is **only** responsible for the 26 per-XY combination tiles:
  * ``silhouette{sep}1f9d1{sep}1f91d.l.{xy}.png``  (left person gray, right in colour)
  * ``silhouette{sep}1f9d1{sep}1f91d.r.{xy}.png``  (right person gray, left in colour)
  * ``silhouette{sep}1f9d1{sep}1f91d.lr.png``       (both persons gray)

Vendor-specific shims in ``<vendor>/extra/gen-couple-nn.py`` call :func:`main`
with two parameters:

``couple_fn(x, y) -> str``
    Returns the filename *stem* (without extension) for the NN couple image
    for skin-tone combination (x, y) where 1-5 → 1f3fb-1f3ff and 6 → default
    (no skin modifier).

``out_sep``
    Character used as separator in output filenames.  ``'_'`` → noto-style
    ``silhouette_1f9d1_1f91d.l.{xy}.png``; ``'-'`` → twemoji-style
    ``silhouette-1f9d1-1f91d.l.{xy}.png``.

All images are read from / written to ``extra/images/{ppem}/`` (relative to
the vendor's ``extra/`` directory).  The compositing strategy is identical to
:mod:`make_neutral_couple_silhouette` used for Apple:

* ``silhouette.ml.png`` is sampled for the canonical gray shade.
* Each couple image has its left or right half replaced with a flat-gray
  overlay (the ML/MR hand-fix technique).
* A single full-gray ``silhouette{sep}1f9d1{sep}1f91d.lr.png`` is generated
  from the default (no-skin) couple.

The script respects the ``IMAGE_SIZES`` environment variable (set by
``image-sizes.sh``) and falls back to ``160 96 64 40``.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Callable

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_neutral_couple_silhouette import _sample_gray

# Canonical silhouette gray — matches apply_silhouette() used in all vendor SVG scripts.
_GRAY: tuple[int, int, int] = (0x7E, 0x7E, 0x7E)

_SKIN_ROWS = list(range(1, 6))
_XY_SUFFIXES: list[str] = [f"{x}{y}" for x in _SKIN_ROWS for y in _SKIN_ROWS] + ["66"]


def _bootstrap_ml_mr(images_dir: Path, nn6_stem: str) -> tuple[Image.Image, Image.Image]:
    """Create crude silhouette.ml/mr images from the default couple PNG.

    Used when ``silhouette.ml/mr.png`` have not yet been rendered from SVG
    (i.e. when the NN block runs before ``svg-to-png.sh``).  The resulting
    images only carry the left/right half of the default couple in flat gray;
    the few pixels where the hands cross the centre-line are not fixed up.
    ``svg-to-png.sh`` will later overwrite the files with the proper renders.
    """
    src = images_dir / f"{nn6_stem}.png"
    if not src.exists():
        raise FileNotFoundError(f"silhouette.ml.png not found and no bootstrap couple image at {src}")
    img = Image.open(src).convert("RGBA")
    w, h = img.size
    alpha = img.split()[3]
    gray_full = Image.new("RGBA", (w, h), (*_GRAY, 255))
    gray_full.putalpha(alpha)
    blank = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ml = blank.copy()
    lc = gray_full.crop((0, 0, w // 2, h))
    ml.paste(lc, (0, 0), lc)
    mr = blank.copy()
    rc = gray_full.crop((w // 2, 0, w, h))
    mr.paste(rc, (w // 2, 0), rc)
    return ml, mr


def _make_silhouettes(
    ppem: int,
    images_dir: Path,
    extra_dir: Path,
    couple_fn: Callable[[int, int], str],
    out_sep: str,
) -> None:
    ml_path = extra_dir / "silhouette.ml.png"
    mr_path = extra_dir / "silhouette.mr.png"
    if ml_path.exists():
        ml = Image.open(ml_path).convert("RGBA")
        mr = Image.open(mr_path).convert("RGBA")
        gray_rgb = _sample_gray(ml)
    else:
        ml, mr = _bootstrap_ml_mr(images_dir, couple_fn(6, 6))
        gray_rgb = _GRAY

    # Full-gray couple (both-silhouette target).
    couple66_path = images_dir / f"{couple_fn(6, 6)}.png"
    if couple66_path.exists():
        c66 = Image.open(couple66_path).convert("RGBA")
        alpha66 = c66.split()[3].point(lambda p: 255 if p > 128 else 0)
        gray66 = Image.new("RGBA", c66.size, (*gray_rgb, 255))
        gray66.putalpha(alpha66)
        out_prefix = f"silhouette{out_sep}1f9d1{out_sep}1f91d"
        gray66.save(extra_dir / f"{out_prefix}.lr.png")
    else:
        print(f"  warning: missing {couple66_path.name}", file=sys.stderr)
        out_prefix = f"silhouette{out_sep}1f9d1{out_sep}1f91d"

    blank: Image.Image | None = None

    for xy in _XY_SUFFIXES:
        x, y = int(xy[0]), int(xy[1])
        stem = couple_fn(x, y)
        couple_path = images_dir / f"{stem}.png"
        if not couple_path.exists():
            print(f"  warning: missing {couple_path.name}", file=sys.stderr)
            continue

        couple = Image.open(couple_path).convert("RGBA")
        w, h = couple.size

        if blank is None or blank.size != (w, h):
            blank = Image.new("RGBA", (w, h), (0, 0, 0, 0))

        alpha_binary = couple.split()[3].point(lambda p: 255 if p > 128 else 0)
        gray = Image.new("RGBA", (w, h), (*gray_rgb, 255))
        gray.putalpha(alpha_binary)

        def _overlay(body_box, hand_src, hand_box, _gray=gray, _blank=blank):
            canvas = _blank.copy()
            crop = _gray.crop(body_box)
            canvas.paste(crop, body_box[:2], crop)
            hand_canvas = _blank.copy()
            hand_piece = hand_src.crop(hand_box)
            hand_canvas.paste(hand_piece, hand_box[:2], hand_piece)
            return Image.alpha_composite(canvas, hand_canvas)

        sil_l = Image.alpha_composite(couple.copy(), _overlay((0, 0, w // 2, h), ml, (w // 2, 0, w, h)))
        sil_r = Image.alpha_composite(couple.copy(), _overlay((w // 2, 0, w, h), mr, (0, 0, w // 2, h)))

        sil_l.save(extra_dir / f"{out_prefix}.l.{xy}.png")
        sil_r.save(extra_dir / f"{out_prefix}.r.{xy}.png")


def main(
    couple_fn: Callable[[int, int], str],
    out_sep: str,
    *,
    caller_file: str | None = None,
    images_root: str | Path | None = None,
) -> None:
    """Generate silhouettes for every available ppem strike.

    ``caller_file`` should be ``__file__`` from the calling shim so the script
    can locate the vendor's ``extra/`` and ``images/`` directories.  When
    omitted the call stack is used to infer the caller's directory.

    ``images_root`` overrides the directory that is scanned for per-ppem source
    couple images.  Defaults to ``<vendor>/images/``.  Set to
    ``<vendor>/extra/images/`` for vendors (e.g. OneUI) whose couple PNGs live
    inside the extra tree rather than the main images tree.
    """
    if caller_file is None:
        import inspect

        frame = inspect.stack()[1]
        caller_file = frame.filename

    extra_root = Path(caller_file).resolve().parent
    vendor_images = Path(images_root) if images_root is not None else extra_root.parent / "images"

    sizes_env = os.environ.get("IMAGE_SIZES", "160 96 64 40")
    ppems = [int(p) for p in sizes_env.split()]

    for ppem in ppems:
        src = vendor_images / str(ppem)
        dst = extra_root / "images" / str(ppem)
        if not src.is_dir():
            continue
        # Skip sizes whose source images haven't been generated yet (e.g. when
        # resize.sh will produce them after this script runs).  Those sizes will
        # be filled in by the resize step from the larger ppem.
        if not (src / f"{couple_fn(6, 6)}.png").exists():
            continue
        dst.mkdir(parents=True, exist_ok=True)
        print(f"Generating NN silhouettes for {ppem}px...")
        _make_silhouettes(ppem, src, dst, couple_fn, out_sep)
