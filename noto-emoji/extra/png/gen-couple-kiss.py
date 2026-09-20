"""Generate person-half PNGs for couple-kissing emoji from Noto 3D assets.

Source images  →  output halves
  emoji_u1f48f{skin}                                      →  1f9d1{skin}_1f48b.l/r
  emoji_u1f468{skin}_200d_2764_200d_1f48b_200d_1f468{skin} →  1f468{skin}_1f48b.l/r
  emoji_u1f469{skin}_200d_2764_200d_1f48b_200d_1f469{skin} →  1f469{skin}_1f48b.l/r

Overlapping faces are split geodesically; the heart goes to the right half.
"""

from shared import SKINS, split_and_save

for skin in SKINS:
    split_and_save(
        f"1f48f{skin}",
        "1f9d1",
        "1f9d1",
        skin,
        joiner="1f48b",
        method="heart-geodesic",
        silhouette=True,
        keep_heart=True,
    )

for g in ["1f469", "1f468"]:
    for skin in SKINS:
        if skin == "":
            stem = f"{g}_200d_2764_200d_1f48b_200d_{g}"
        else:
            stem = f"{g}{skin}_200d_2764_200d_1f48b_200d_{g}{skin}"
        split_and_save(
            stem,
            g,
            g,
            skin,
            joiner="1f48b",
            method="heart-geodesic",
            silhouette=True,
            keep_heart=True,
        )
