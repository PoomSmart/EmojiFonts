import xml.etree.ElementTree as ET
from shared import *

# neutral
for skin in skins:
    name = f'{font}/emoji_u1f48f.svg' if skin == 'none' else f'{font}/emoji_u1f48f_{skin}.svg'
    left = ET.parse(name).getroot()
    right = ET.parse(name).getroot()
    remove(left, 2)
    remove(left, 1)
    remove(right, 0)
    write_dual(left, right, '1f9d1', '1f9d1', skin, '1f48b')

# neutral silhouette
name = f'{font}/emoji_u1f48f.svg' 
left = ET.parse(name).getroot()
right = ET.parse(name).getroot()
remove(left, 2)
remove(left, 1)
remove(right, 0)
find_set_color(left)
find_set_color(right)

left_out = ET.ElementTree(left)
left_out.write('silhouette_1f9d1_1f48b.l.svg', encoding='utf-8')
right_out = ET.ElementTree(right)
right_out.write('silhouette_1f9d1_1f48b.r.svg', encoding='utf-8')

# woman, man silhouette
for g in ['1f469', '1f468']:
    name = f'{font}/emoji_u{g}_200d_2764_200d_1f48b_200d_{g}.svg'
    left = ET.parse(name).getroot()
    right = ET.parse(name).getroot()
    remove(left, 2)
    remove(left, 1)
    remove(right, 0)
    find_set_color(left)
    find_set_color(right)
    left_out = ET.ElementTree(left)
    left_out.write(f'silhouette_{g}_1f48b.l.svg', encoding='utf-8')
    right_out = ET.ElementTree(right)
    right_out.write(f'silhouette_{g}_1f48b.r.svg', encoding='utf-8')

# dual woman, dual man
for g in ['1f469', '1f468']:
    for skin in skins:
        if skin == 'none':
            name = f'{font}/emoji_u{g}_200d_2764_200d_1f48b_200d_{g}.svg'
        else:
            name = f'{font}/emoji_u{g}_{skin}_200d_2764_200d_1f48b_200d_{g}_{skin}.svg'
        left = ET.parse(name).getroot()
        right = ET.parse(name).getroot()
        remove(left, 2)
        remove(left, 1)
        remove(right, 0)
        write_dual(left, right, g, g, skin, '1f48b')