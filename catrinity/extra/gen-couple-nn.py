"""Generate NN (neutral-person) couple silhouettes for Catrinity.

Delegates to the root gen_couple_nn module.  Images are read from
catrinity/images/{ppem}/ (the main rendered PNGs) and written to
catrinity/extra/images/{ppem}/.

Catrinity uses underscore-separated, lowercase-hex filenames (matching
catrinity_render.py's _hex_seq() output).

Run from catrinity/extra/ OR as:  uv run python extra/gen-couple-nn.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import gen_couple_nn

_SKIN = {1: "1f3fb", 2: "1f3fc", 3: "1f3fd", 4: "1f3fe", 5: "1f3ff"}


def couple_fn(x: int, y: int) -> str:
    """Return the PNG stem for neutral-person couple with skins (x, y).

    x, y ∈ {1..5} for skin tones 1f3fb-1f3ff; 6 = no skin modifier.
    """
    if x == 6 and y == 6:
        return "1f9d1_200d_1f91d_200d_1f9d1"
    s1 = f"_{_SKIN[x]}" if x != 6 else ""
    s2 = f"_{_SKIN[y]}" if y != 6 else ""
    return f"1f9d1{s1}_200d_1f91d_200d_1f9d1{s2}"


gen_couple_nn.main(couple_fn, "_", caller_file=__file__)
