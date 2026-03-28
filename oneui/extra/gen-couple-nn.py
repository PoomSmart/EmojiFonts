import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import gen_couple_nn

# OneUI uses a "d" suffix for the default (no-skin) person instead of omitting
# the skin entirely, so:  1f9d1d_200d_1f91d_200d_1f9d1d  (both default)
#                         1f9d1_1f3fb_200d_1f91d_200d_1f9d1d  (left=skin1, right=default)
# Couple PNGs live in extra/images/{ppem}/ (assembled by get-assets.sh), so
# images_root points there instead of the main images/ tree.

_SKIN = {1: "1f3fb", 2: "1f3fc", 3: "1f3fd", 4: "1f3fe", 5: "1f3ff"}


def _couple_fn(x: int, y: int) -> str:
    s1 = f"_{_SKIN[x]}" if x != 6 else "d"
    s2 = f"_{_SKIN[y]}" if y != 6 else "d"
    return f"1f9d1{s1}_200d_1f91d_200d_1f9d1{s2}"


gen_couple_nn.main(
    _couple_fn,
    "_",
    caller_file=__file__,
    images_root=Path(__file__).resolve().parent / "images",
)
