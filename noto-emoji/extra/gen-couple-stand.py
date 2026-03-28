import sys
from pathlib import Path
import xml.etree.ElementTree as ET
from shared import *

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import gen_couple_nn

# left woman, right man
for skin in skins:
    name = f'{font}/emoji_u1f46b.svg' if skin == 'none' else f'{font}/emoji_u1f46b_{skin}.svg'
    left_woman = ET.parse(name).getroot()
    right_man = ET.parse(name).getroot()
    remove(left_woman, 0)
    remove(right_man, 1)
    write_dual(left_woman, right_man, '1f469', '1f468', skin)

# left man
for skin in skins:
    name = f'{font}/emoji_u1f46c.svg' if skin == 'none' else f'{font}/emoji_u1f46c_{skin}.svg'
    left = ET.parse(name).getroot()
    remove(left, 0)
    left_name = '1f468.l.svg' if skin == 'none' else f'1f468_{skin}.l.svg'
    left_out = ET.ElementTree(left)
    left_out.write(f'svgs/{left_name}', encoding='utf-8')

# right woman
for skin in skins:
    name = f'{font}/emoji_u1f46d.svg' if skin == 'none' else f'{font}/emoji_u1f46d_{skin}.svg'
    right = ET.parse(name).getroot()
    remove(right, 1)
    right_name = '1f469.r.svg' if skin == 'none' else f'1f469_{skin}.r.svg'
    right_out = ET.ElementTree(right)
    right_out.write(f'svgs/{right_name}', encoding='utf-8')

# silhouette woman
name = f'{font}/emoji_u1f46d.svg'
left = ET.parse(name).getroot()
right = ET.parse(name).getroot()
remove(left, 0)
remove(right, 1)
apply_silhouette(left)
apply_silhouette(right)
left_out = ET.ElementTree(left)
left_out.write('svgs/silhouette.wl.svg', encoding='utf-8')
right_out = ET.ElementTree(right)
right_out.write('svgs/silhouette.wr.svg', encoding='utf-8')

# silhouette man
name = f'{font}/emoji_u1f46c.svg'
left = ET.parse(name).getroot()
right = ET.parse(name).getroot()
remove(left, 0)
remove(right, 1)
apply_silhouette(left)
apply_silhouette(right)
left_out = ET.ElementTree(left)
left_out.write('svgs/silhouette.ml.svg', encoding='utf-8')
right_out = ET.ElementTree(right)
right_out.write('svgs/silhouette.mr.svg', encoding='utf-8')

# NN (neutral-person) couple silhouettes — generated after SVG→PNG conversion
# is handled by the caller (blobmoji.sh / noto-emoji.sh).
_SKIN = {1: "1f3fb", 2: "1f3fc", 3: "1f3fd", 4: "1f3fe", 5: "1f3ff"}

def _couple_fn(x: int, y: int) -> str:
    if x == 6 and y == 6:
        return "emoji_u1f9d1_200d_1f91d_200d_1f9d1"
    s1 = f"_{_SKIN[x]}" if x != 6 else ""
    s2 = f"_{_SKIN[y]}" if y != 6 else ""
    return f"emoji_u1f9d1{s1}_200d_1f91d_200d_1f9d1{s2}"

gen_couple_nn.main(_couple_fn, "_", caller_file=__file__)
