"""Generate person-half PNGs for couple-holding-hands emoji from Noto 3D assets.

Source images  →  output halves
  emoji_u1f46b{skin}  (woman+man)   →  1f469{skin}.l  +  1f468{skin}.r
  emoji_u1f46c{skin}  (man+man)     →  1f468{skin}.l
  emoji_u1f46d{skin}  (woman+woman) →  1f469{skin}.r
  emoji_u1f9d1{skin}_200d_1f91d_200d_1f9d1{skin} →  1f9d1{skin}.l/r

Also writes silhouette.ml/mr/wl/wr for gen_couple_nn, then NN silhouettes.
"""

import sys
from pathlib import Path

from shared import SKINS, extra_images, split_png, src_png, to_silhouette

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
import gen_couple_nn

dst = extra_images()

for skin in SKINS:
    pair = split_png(src_png(f"1f46b{skin}"), "geodesic")
    if pair is not None:
        left, right = pair
        left.save(dst / f"1f469{skin}.l.png")
        right.save(dst / f"1f468{skin}.r.png")

    pair = split_png(src_png(f"1f46c{skin}"), "geodesic")
    if pair is not None:
        left, _ = pair
        left.save(dst / f"1f468{skin}.l.png")

    pair = split_png(src_png(f"1f46d{skin}"), "geodesic")
    if pair is not None:
        _, right = pair
        right.save(dst / f"1f469{skin}.r.png")

    nn_stem = "1f9d1_200d_1f91d_200d_1f9d1" if skin == "" else f"1f9d1{skin}_200d_1f91d_200d_1f9d1{skin}"
    pair = split_png(src_png(nn_stem), "geodesic")
    if pair is not None:
        left, right = pair
        left.save(dst / f"1f9d1{skin}.l.png")
        right.save(dst / f"1f9d1{skin}.r.png")

pair = split_png(src_png("1f46c"), "geodesic")
if pair is not None:
    ml, mr = pair
    to_silhouette(ml).save(dst / "silhouette.ml.png")
    to_silhouette(mr).save(dst / "silhouette.mr.png")

pair = split_png(src_png("1f46d"), "geodesic")
if pair is not None:
    wl, wr = pair
    to_silhouette(wl).save(dst / "silhouette.wl.png")
    to_silhouette(wr).save(dst / "silhouette.wr.png")

_SKIN = {1: "1f3fb", 2: "1f3fc", 3: "1f3fd", 4: "1f3fe", 5: "1f3ff"}


def _couple_fn(x: int, y: int) -> str:
    if x == 6 and y == 6:
        return "emoji_u1f9d1_200d_1f91d_200d_1f9d1"
    s1 = f"_{_SKIN[x]}" if x != 6 else ""
    s2 = f"_{_SKIN[y]}" if y != 6 else ""
    return f"emoji_u1f9d1{s1}_200d_1f91d_200d_1f9d1{s2}"


# gen_couple_nn locates extra/ from caller_file's parent.
gen_couple_nn.main(_couple_fn, "_", caller_file=str(Path(__file__).resolve().parents[1] / "shared.py"))
