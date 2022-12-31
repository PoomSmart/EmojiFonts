import xml.etree.ElementTree as ET
from shared import *

# neutral
for skin in skins:
    name = f'{font}/1F491.svg' if skin == 'none' else f'{font}/1F491-{skin}.svg'
    left = ET.parse(name).getroot()
    right = ET.parse(name).getroot()
    remove(left, 2)
    remove(left, 0)
    remove(right, 1)
    write_dual(left, right, '1F9D1', '1F9D1', skin, '2764')

# dual woman, dual man
for g in ['1F469', '1F468', '1F9D1']:
    name = f'{font}/1F491.svg' if g == '1F9D1' else f'{font}/{g}-200D-2764-200D-{g}.svg'
    left = ET.parse(name).getroot()
    right = ET.parse(name).getroot()
    if g == '1F469':
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
    left_out.write(f'silhouette-{g}-2764.l.svg', encoding='utf-8')
    right_out = ET.ElementTree(right)
    right_out.write(f'silhouette-{g}-2764.r.svg', encoding='utf-8')
    for skin in skins:
        if skin == 'none':
            name = f'{font}/1F491.svg' if g == '1F9D1' else f'{font}/{g}-200D-2764-200D-{g}.svg'
        else:
            name = f'{font}/1F491-{skin}.svg' if g == '1F9D1' else f'{font}/{g}-{skin}-200D-2764-200D-{g}-{skin}.svg'
        left = ET.parse(name).getroot()
        right = ET.parse(name).getroot()
        if g == '1F469':
            remove(left, 2)
            remove(left, 1)
            remove(right, 0)
        else:
            remove(left, 2)
            remove(left, 0)
            remove(right, 1)
        write_dual(left, right, g, g, skin, '2764')
