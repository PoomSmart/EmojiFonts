import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import gen_couple_nn

_SKIN = {1: '1F3FB', 2: '1F3FC', 3: '1F3FD', 4: '1F3FE', 5: '1F3FF'}


def couple_fn(x: int, y: int) -> str:
    if x == 6 and y == 6:
        return '1F9D1-200D-1F91D-200D-1F9D1'
    s1 = f'-{_SKIN[x]}' if x != 6 else ''
    s2 = f'-{_SKIN[y]}' if y != 6 else ''
    return f'1F9D1{s1}-200D-1F91D-200D-1F9D1{s2}'


gen_couple_nn.main(couple_fn, '-', caller_file=__file__)
