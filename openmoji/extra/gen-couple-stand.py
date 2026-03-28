import sys
from pathlib import Path
import xml.etree.ElementTree as ET
from shared import *

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import gen_couple_nn

# TODO: beautify remove_child?

# left woman, right man
for skin in skins:
    name = f'{font}/1F46B.svg' if skin == 'none' else f'{font}/1F46B-{skin}.svg'
    left_woman = ET.parse(name).getroot()
    right_man = ET.parse(name).getroot()
    remove_child(left_woman, 1, 0)
    remove_child(left_woman, 4, 4)
    remove_child(left_woman, 4, 2)
    remove_child(left_woman, 4, 0)
    remove_child(right_man, 1, 1)
    remove_child(right_man, 4, 5)
    remove_child(right_man, 4, 3)
    remove_child(right_man, 4, 1)
    write_dual(left_woman, right_man, '1F469', '1F468', skin)

# left man
for skin in skins:
    name = f'{font}/1F46C.svg' if skin == 'none' else f'{font}/1F46C-{skin}.svg'
    left = ET.parse(name).getroot()
    remove_child(left, 1, 0)
    remove_child(left, 4, 2)
    remove_child(left, 4, 1)
    remove_child(left, 4, 0)
    left_name = '1F468.l.svg' if skin == 'none' else f'1F468-{skin}.l.svg'
    left_out = ET.ElementTree(left)
    left_out.write(f'svgs/{left_name}', encoding='utf-8')

# right woman
for skin in skins:
    name = f'{font}/1F46D.svg' if skin == 'none' else f'{font}/1F46D-{skin}.svg'
    right = ET.parse(name).getroot()
    remove_child(right, 1, 1)
    remove_child(right, 4, 2)
    remove_child(right, 4, 1)
    remove_child(right, 4, 0)
    right_name = '1F469.r.svg' if skin == 'none' else f'1F469-{skin}.r.svg'
    right_out = ET.ElementTree(right)
    right_out.write(f'svgs/{right_name}', encoding='utf-8')

# silhouette woman
name = f'{font}/1F46D.svg'
left = ET.parse(name).getroot()
right = ET.parse(name).getroot()
remove_child(left, 1, 0)
remove_child(left, 4, 5)
remove_child(left, 4, 4)
remove_child(left, 4, 3)
remove_child(right, 1, 1)
remove_child(right, 4, 2)
remove_child(right, 4, 1)
remove_child(right, 4, 0)
apply_silhouette(left)
apply_silhouette(right)
left_out = ET.ElementTree(left)
left_out.write('svgs/silhouette.wl.svg', encoding='utf-8')
right_out = ET.ElementTree(right)
right_out.write('svgs/silhouette.wr.svg', encoding='utf-8')

# silhouette man
name = f'{font}/1F46C.svg'
left = ET.parse(name).getroot()
right = ET.parse(name).getroot()
remove_child(left, 1, 0)
remove_child(left, 4, 2)
remove_child(left, 4, 1)
remove_child(left, 4, 0)
remove_child(right, 1, 1)
remove_child(right, 4, 5)
remove_child(right, 4, 4)
remove_child(right, 4, 3)
apply_silhouette(left)
apply_silhouette(right)
left_out = ET.ElementTree(left)
left_out.write('svgs/silhouette.ml.svg', encoding='utf-8')
right_out = ET.ElementTree(right)
right_out.write('svgs/silhouette.mr.svg', encoding='utf-8')

# NN (neutral-person) couple silhouettes
_SKIN = {1: "1F3FB", 2: "1F3FC", 3: "1F3FD", 4: "1F3FE", 5: "1F3FF"}

def _couple_fn(x: int, y: int) -> str:
    if x == 6 and y == 6:
        return "1F9D1-200D-1F91D-200D-1F9D1"
    s1 = f"-{_SKIN[x]}" if x != 6 else ""
    s2 = f"-{_SKIN[y]}" if y != 6 else ""
    return f"1F9D1{s1}-200D-1F91D-200D-1F9D1{s2}"

gen_couple_nn.main(_couple_fn, "-", caller_file=__file__)
