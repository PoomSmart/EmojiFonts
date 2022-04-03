import xml.etree.ElementTree as ET
from shared import *

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
find_set_color(left)
find_set_color(right)
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
find_set_color(left)
find_set_color(right)
left_out = ET.ElementTree(left)
left_out.write('svgs/silhouette.ml.svg', encoding='utf-8')
right_out = ET.ElementTree(right)
right_out.write('svgs/silhouette.mr.svg', encoding='utf-8')