"""Generate handshake half PNGs from Noto 3D combined handshake assets.

Source images  →  output halves
  emoji_u1f91d{skin}  →  1faf1{skin}.l  +  1faf2{skin}.r

Standalone 1faf1/1faf2 (rightwards/leftwards hand) are not handshake halves.
"""

from shared import SKINS, split_and_save

for skin in SKINS:
    split_and_save(
        f"1f91d{skin}",
        "1faf1",
        "1faf2",
        skin,
        method="geodesic",
        silhouette=True,
    )
