import xml.etree.ElementTree as ET
from shared import *

# left woman, right man
for skin in skins.keys():
    name = f'{font}/1f46b.svg' if skin == 'none' else f'{font}/1f46b-{skin}.svg'
    left_woman = ET.parse(name).getroot()
    right_man = ET.parse(name).getroot()
    for i in range(27, 14, -1):
        remove(left_woman, i)
    for i in range(14, -1, -1):
        remove(right_man, i)
    write_dual(left_woman, right_man, '1f469', '1f468', skin)

# left man
for skin in skins.keys():
    name = f'{font}/1f46c.svg' if skin == 'none' else f'{font}/1f46c-{skin}.svg'
    left = ET.parse(name).getroot()
    for i in range(26, 12, -1):
        remove(left, i)
    left_name = '1f468.l.svg' if skin == 'none' else f'1f468-{skin}.l.svg'
    left_out = ET.ElementTree(left)
    left_out.write(f'svgs/{left_name}', encoding='utf-8')

# right woman
for skin in skins.keys():
    name = f'{font}/1f46d.svg' if skin == 'none' else f'{font}/1f46d-{skin}.svg'
    right = ET.parse(name).getroot()
    for i in range(14, -1, -1):
        remove(right, i)
    right_name = '1f469.r.svg' if skin == 'none' else f'1f469-{skin}.r.svg'
    right_out = ET.ElementTree(right)
    right_out.write(f'svgs/{right_name}', encoding='utf-8')

# silhouette woman
name = f'{font}/1f46d.svg' 
left = ET.parse(name).getroot()
right = ET.parse(name).getroot()
for i in range(29, 11, -1):
    remove(left, i)
for i in range(14, -1, -1):
    remove(right, i)
for c in left:
    c.set('fill', silhouette_color)
for c in right:
    c.set('fill', silhouette_color)
left_out = ET.ElementTree(left)
left_out.write('svgs/silhouette.wl.svg', encoding='utf-8')
right_out = ET.ElementTree(right)
right_out.write('svgs/silhouette.wr.svg', encoding='utf-8')

# silhouette man
name = f'{font}/1f46c.svg' 
left = ET.parse(name).getroot()
right = ET.parse(name).getroot()
for i in range(26, 12, -1):
    remove(left, i)
for i in range(12, -1, -1):
    remove(right, i)
for c in left:
    c.set('fill', silhouette_color)
for c in right:
    c.set('fill', silhouette_color)
left_out = ET.ElementTree(left)
left_out.write('svgs/silhouette.ml.svg', encoding='utf-8')
right_out = ET.ElementTree(right)
right_out.write('svgs/silhouette.mr.svg', encoding='utf-8')