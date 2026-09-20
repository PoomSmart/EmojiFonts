"""Generate person-half PNGs for people-with-bunny-ears from Noto 3D assets.

Source images (U+1F46F) and gendered variants:
  emoji_u1f46f{skin}               →  1f9d1{skin}_1f430.l/r
  emoji_u1f46f{skin}_200d_2642     →  1f468{skin}_1f430.l/r
  emoji_u1f46f{skin}_200d_2640     →  1f469{skin}_1f430.l/r
"""

from shared import SKINS, split_and_save

JOINER = "1f430"

gender_map = {
    "1f9d1": "1f46f",
    "1f468": "1f46f_200d_2642",
    "1f469": "1f46f_200d_2640",
}

for g_code, filename_base in gender_map.items():
    for skin in SKINS:
        stem = filename_base.replace("1f46f", f"1f46f{skin}", 1)
        split_and_save(
            stem,
            g_code,
            g_code,
            skin,
            joiner=JOINER,
            method="components",
            silhouette=True,
        )
