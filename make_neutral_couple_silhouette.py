"""Generate silhouette.u1F9D1.u1F91D.{L,R}.XY.png for every XY combo in a ppem directory.

Usage::

    python3 make_neutral_couple_silhouette.py <ppem_dir>

``ppem_dir`` must contain ``silhouette.ML.png``, ``silhouette.MR.png``, and at
least one ``u1F9D1_u1F91D_u1F9D1.*.png`` couple image.

For every ``u1F9D1_u1F91D_u1F9D1.XY.png`` found the script generates:

  * ``silhouette.u1F9D1.u1F91D.L.XY.png`` — left person gray,  right person in colour
  * ``silhouette.u1F9D1.u1F91D.R.XY.png`` — right person gray, left person in colour

A single ``silhouette.u1F9D1.u1F91D.LR.png`` (full-gray couple) is also generated
from the ``.66`` couple image and used as the morx cascade target when BOTH persons
are silhouetted simultaneously.

Strategy
--------
The NN couple is a single composite glyph (not split into .L/.R halves like FM/FF/MM).
When morx substitutes it, the ENTIRE glyph is replaced — so our image must contain
BOTH persons: the silhouette side gray and the normal side in full colour.

* Body *shape*: couple's own alpha, binary-thresholded to 0/255 to avoid a gray
  anti-aliased outline when the flat-color overlay is composited over the colour couple.
* Body *colour*: sampled from silhouette.ML (canonical gray shade reference).
* Hand fix: ML/MR pixels past the w//2 split restore the clasped-hand area.

  .L.XY = full couple base (XY) + gray overlay on left half  (left=gray,  right=colour)
  .R.XY = full couple base (XY) + gray overlay on right half (left=colour, right=gray)
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image


def _sample_gray(img: Image.Image) -> tuple[int, int, int]:
    """Return the average RGB of all opaque pixels in *img*."""
    r_sum = g_sum = b_sum = count = 0
    for r, g, b, a in img.get_flattened_data():
        if a > 128:
            r_sum += r
            g_sum += g
            b_sum += b
            count += 1
    if count == 0:
        return (128, 128, 128)
    return r_sum // count, g_sum // count, b_sum // count


def make_silhouettes(ppem_dir: Path) -> None:
    ml = Image.open(ppem_dir / "silhouette.ML.png").convert("RGBA")
    mr = Image.open(ppem_dir / "silhouette.MR.png").convert("RGBA")
    gray_rgb = _sample_gray(ml)

    # Generate the single "both silhouette" full-gray couple used when both persons
    # are simultaneously silhouetted (morx cascade target).
    couple66_path = ppem_dir / "u1F9D1_u1F91D_u1F9D1.66.png"
    if couple66_path.exists():
        c66 = Image.open(couple66_path).convert("RGBA")
        alpha66 = c66.split()[3].point(lambda p: 255 if p > 128 else 0)
        gray66 = Image.new("RGBA", c66.size, (*gray_rgb, 255))
        gray66.putalpha(alpha66)
        gray66.save(ppem_dir / "silhouette.u1F9D1.u1F91D.LR.png")

    for couple_path in sorted(ppem_dir.glob("u1F9D1_u1F91D_u1F9D1.*.png")):
        xy = couple_path.stem.split(".")[-1]  # "u1F9D1_u1F91D_u1F9D1.XY" → "XY"
        couple = Image.open(couple_path).convert("RGBA")
        w, h = couple.size

        # Binary-threshold alpha to avoid muddy semi-transparent edge pixels when the
        # flat-gray layer is composited over the coloured couple below.
        alpha_binary = couple.split()[3].point(lambda p: 255 if p > 128 else 0)
        gray = Image.new("RGBA", (w, h), (*gray_rgb, 255))
        gray.putalpha(alpha_binary)

        blank = Image.new("RGBA", (w, h), (0, 0, 0, 0))

        def _gray_overlay(body_box: tuple, hand_src: Image.Image, hand_box: tuple) -> Image.Image:
            """Build a gray-only overlay (one half gray, other half transparent)."""
            canvas = blank.copy()
            body_crop = gray.crop(body_box)
            canvas.paste(body_crop, body_box[:2], body_crop)
            hand_canvas = blank.copy()
            hand_piece = hand_src.crop(hand_box)
            hand_canvas.paste(hand_piece, hand_box[:2], hand_piece)
            return Image.alpha_composite(canvas, hand_canvas)

        # .L.XY: left half gray + ML hand fix, composited over the full colour couple
        overlay_l = _gray_overlay((0, 0, w // 2, h), ml, (w // 2, 0, w, h))
        sil_l = Image.alpha_composite(couple.copy(), overlay_l)
        sil_l.save(ppem_dir / f"silhouette.u1F9D1.u1F91D.L.{xy}.png")

        # .R.XY: right half gray + MR hand fix, composited over the full colour couple
        overlay_r = _gray_overlay((w // 2, 0, w, h), mr, (0, 0, w // 2, h))
        sil_r = Image.alpha_composite(couple.copy(), overlay_r)
        sil_r.save(ppem_dir / f"silhouette.u1F9D1.u1F91D.R.{xy}.png")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <ppem_dir>", file=sys.stderr)
        raise SystemExit(1)
    make_silhouettes(Path(sys.argv[1]))
