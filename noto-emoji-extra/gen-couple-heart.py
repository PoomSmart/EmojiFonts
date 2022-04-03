import xml.etree.ElementTree as ET
from shared import *

# neutral
for skin in skins:
    name = f'{font}/emoji_u1f491.svg' if skin == 'none' else f'{font}/emoji_u1f491_{skin}.svg'
    left = ET.parse(name).getroot()
    right = ET.parse(name).getroot()
    remove(left, 2)
    remove(left, 0)
    remove(right, 1)
    write_dual(left, right, '1f9d1', '1f9d1', skin, '2764')

# dual woman, dual man
for g in ['1f469', '1f468', '1f9d1']:
    name = f'{font}/emoji_u1f491.svg' if g == '1f9d1' else f'{font}/emoji_u{g}_200d_2764_200d_{g}.svg'
    left = ET.parse(name).getroot()
    right = ET.parse(name).getroot()
    if g == '1f469':
        remove(left, 2)
        remove(left, 1)
        remove(right, 0)
    else:
        remove(left, 2)
        remove(left, 0)
        remove(right, 1)
    find_set_color(left)
    find_set_color(right)
    left_out = ET.ElementTree(left)
    left_out.write(f'svgs/silhouette_{g}_2764.l.svg', encoding='utf-8')
    right_out = ET.ElementTree(right)
    right_out.write(f'svgs/silhouette_{g}_2764.r.svg', encoding='utf-8')
    for skin in skins:
        if skin == 'none':
            name = f'{font}/emoji_u1f491.svg' if g == '1f9d1' else f'{font}/emoji_u{g}_200d_2764_200d_{g}.svg'
        else:
            name = f'{font}/emoji_u1f491_{skin}.svg' if g == '1f9d1' else f'{font}/emoji_u{g}_{skin}_200d_2764_200d_{g}_{skin}.svg'
        left = ET.parse(name).getroot()
        right = ET.parse(name).getroot()
        if g == '1f469':
            remove(left, 2)
            remove(left, 1)
            remove(right, 0)
        else:
            remove(left, 2)
            remove(left, 0)
            remove(right, 1)
        write_dual(left, right, g, g, skin, '2764')
