"""Generate person-half PNGs for couple-with-heart emoji from Noto 3D assets.

Source images  →  output halves
  emoji_u1f491{skin}                         →  1f9d1{skin}_2764.l/r
  emoji_u1f468{skin}_200d_2764_200d_1f468{skin}  →  1f468{skin}_2764.l/r
  emoji_u1f469{skin}_200d_2764_200d_1f469{skin}  →  1f469{skin}_2764.l/r

The heart is detected by color and attached to the right half.
"""

from shared import SKINS, split_and_save

for skin in SKINS:
    split_and_save(
        f"1f491{skin}",
        "1f9d1",
        "1f9d1",
        skin,
        joiner="2764",
        method="heart",
        silhouette=True,
        keep_heart=True,
    )

for g in ["1f469", "1f468"]:
    for skin in SKINS:
        stem = f"{g}_200d_2764_200d_{g}" if skin == "" else f"{g}{skin}_200d_2764_200d_{g}{skin}"
        split_and_save(
            stem,
            g,
            g,
            skin,
            joiner="2764",
            method="heart",
            silhouette=True,
            keep_heart=True,
        )
