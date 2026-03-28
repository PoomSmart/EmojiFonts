"""Generate NN couple silhouette tiles for WhatsApp emoji.

WhatsApp has no gen-couple-stand.py and uses pre-rendered PNGs instead of
SVGs, so silhouette.ml.png / silhouette.mr.png are synthesised on the fly
from the two-men standing-couple image (emoji_u1f46c) by gen_couple_nn's
built-in bootstrap logic.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import gen_couple_nn

_SKIN = {1: "1f3fb", 2: "1f3fc", 3: "1f3fd", 4: "1f3fe", 5: "1f3ff"}


def couple_fn(x: int, y: int) -> str:
    if x == 6 and y == 6:
        return "emoji_u1f9d1_200d_1f91d_200d_1f9d1"
    s1 = f"_{_SKIN[x]}" if x != 6 else ""
    s2 = f"_{_SKIN[y]}" if y != 6 else ""
    return f"emoji_u1f9d1{s1}_200d_1f91d_200d_1f9d1{s2}"


gen_couple_nn.main(couple_fn, "_", caller_file=__file__)
