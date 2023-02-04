import xml.etree.ElementTree as ET
from shared import *

def remove_for_left(data, g):
    remove_by_id(data, 'hair-b')
    remove_by_id(data, 'skin-b')
    if g == '1F469':
        remove_child_at(data, 'line', 11)
        remove_child_at(data, 'line', 7)
        remove_child_at(data, 'line', 6)
        remove_child_at(data, 'line', 5)
        remove_child_at(data, 'line', 4)
        remove_child_at(data, 'line', 3)
        remove_child_at(data, 'line', 2)
        remove_child_at(data, 'color', 1)
        remove_child_at(data, 'color', 0)
    elif g == '1F468':
        remove_child_at(data, 'line', 12)
        remove_child_at(data, 'line', 11)
        remove_child_at(data, 'line', 10)
        remove_child_at(data, 'line', 9)
        remove_child_at(data, 'line', 2)
        remove_child_at(data, 'line', 1)
        remove_child_at(data, 'line', 0)
        remove_child_at(data, 'color', 2)
        remove_child_at(data, 'color', 1)
    else:
        remove_child_at(data, 'line', 9)
        remove_child_at(data, 'line', 8)
        remove_child_at(data, 'line', 7)
        remove_child_at(data, 'line', 5)
        remove_child_at(data, 'line', 4)
        remove_child_at(data, 'line', 3)
        remove_child_at(data, 'line', 2)
        remove_child_at(data, 'color', 2)
        remove_child_at(data, 'color', 0)

def remove_for_right(data, g):
    remove_by_id(data, 'hair-a')
    remove_by_id(data, 'skin-a')
    if g == '1F469':
        remove_child_at(data, 'line', 12)
        remove_child_at(data, 'line', 10)
        remove_child_at(data, 'line', 9)
        remove_child_at(data, 'line', 8)
        remove_child_at(data, 'line', 1)
        remove_child_at(data, 'line', 0)
        remove_child_at(data, 'color', 2)
    elif g == '1F468':
        remove_child_at(data, 'line', 8)
        remove_child_at(data, 'line', 7)
        remove_child_at(data, 'line', 6)
        remove_child_at(data, 'line', 5)
        remove_child_at(data, 'line', 4)
        remove_child_at(data, 'line', 3)
        remove_child_at(data, 'color', 0)
    else:
        remove_child_at(data, 'line', 12)
        remove_child_at(data, 'line', 11)
        remove_child_at(data, 'line', 10)
        remove_child_at(data, 'line', 6)
        remove_child_at(data, 'line', 1)
        remove_child_at(data, 'line', 0)
        remove_child_at(data, 'color', 1)

# neutral
for skin in skins:
    name = f'{font}/1F491.svg' if skin == 'none' else f'{font}/1F491-{skin}.svg'
    left = ET.parse(name).getroot()
    right = ET.parse(name).getroot()
    remove_for_left(left, '1F9D1')
    remove_for_right(right, '1F9D1')
    write_dual(left, right, '1F9D1', '1F9D1', skin, '2764')

# dual woman, dual man
for g in ['1F469', '1F468', '1F9D1']:
    name = f'{font}/1F491.svg' if g == '1F9D1' else f'{font}/{g}-200D-2764-FE0F-200D-{g}.svg'
    left = ET.parse(name).getroot()
    right = ET.parse(name).getroot()
    remove_for_left(left, g)
    remove_for_right(right, g)
    apply_silhouette(left)
    apply_silhouette(right)
    left_out = ET.ElementTree(left)
    left_out.write(f'svgs/silhouette-{g}-2764.l.svg', encoding='utf-8')
    right_out = ET.ElementTree(right)
    right_out.write(f'svgs/silhouette-{g}-2764.r.svg', encoding='utf-8')
    for skin in skins:
        if skin == 'none':
            name = f'{font}/1F491.svg' if g == '1F9D1' else f'{font}/{g}-200D-2764-FE0F-200D-{g}.svg'
        else:
            name = f'{font}/1F491-{skin}.svg' if g == '1F9D1' else f'{font}/{g}-{skin}-200D-2764-FE0F-200D-{g}-{skin}.svg'
        left = ET.parse(name).getroot()
        right = ET.parse(name).getroot()
        remove_for_left(left, g)
        remove_for_right(right, g)
        write_dual(left, right, g, g, skin, '2764')
