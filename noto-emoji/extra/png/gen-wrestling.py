"""Generate person-half PNGs for wrestlers from Noto 3D assets.

Source images (U+1F93C) and gendered variants:
  emoji_u1f93c{skin}               →  1f9d1{skin}_1faef.l/r
  emoji_u1f93c{skin}_200d_2642     →  1f468{skin}_1faef.l/r
  emoji_u1f93c{skin}_200d_2640     →  1f469{skin}_1faef.l/r
"""

from shared import SKINS, split_and_save

JOINER = "1faef"

gender_map = {
    "1f9d1": "1f93c",
    "1f468": "1f93c_200d_2642",
    "1f469": "1f93c_200d_2640",
}

for g_code, filename_base in gender_map.items():
    for skin in SKINS:
        stem = filename_base.replace("1f93c", f"1f93c{skin}", 1)
        split_and_save(
            stem,
            g_code,
            g_code,
            skin,
            joiner=JOINER,
            method="geodesic",
            silhouette=True,
        )
