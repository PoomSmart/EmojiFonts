import xml.etree.ElementTree as ET
from shared import *

ET.register_namespace('', 'http://www.w3.org/2000/svg')

# neutral
for skin in skins.keys():
    name = f'{font}/1f491.svg' if skin == 'none' else f'{font}/1f491-{skin}.svg'
    left = ET.parse(name).getroot()
    right = ET.parse(name).getroot()
    for i in range(12, 5, -1):
        remove(left, i)
    for i in range(5, -1, -1):
        remove(right, i)
    write_dual(left, right, '1f9d1', '1f9d1', skin, '2764')

# dual woman, dual man
for g in ['1f469', '1f468', '1f9d1']:
    name = f'{font}/1f491.svg' if g == '1f9d1' else f'{font}/{g}-200d-2764-fe0f-200d-{g}.svg'
    left = ET.parse(name).getroot()
    right = ET.parse(name).getroot()
    if g == '1f469':
        for i in range(14, 6, -1):
            remove(left, i)
        for i in range(6, -1, -1):
            remove(right, i)
    else:
        for i in range(12, 5, -1):
            remove(left, i)
        for i in range(5, -1, -1):
            remove(right, i)
    for c in left:
        c.set('fill', silhouette_color)
    for c in right:
        if c.get('fill') == '#DD2E44':
            continue
        c.set('fill', silhouette_color)
    left_out = ET.ElementTree(left)
    left_out.write(f'silhouette-{g}-2764.l.svg', encoding='utf-8')
    right_out = ET.ElementTree(right)
    right_out.write(f'silhouette-{g}-2764.r.svg', encoding='utf-8')
    for skin in skins.keys():
        if skin == 'none':
            name = f'{font}/1f491.svg' if g == '1f9d1' else f'{font}/{g}-200d-2764-fe0f-200d-{g}.svg'
        else:
            name = f'{font}/1f491-{skin}.svg' if g == '1f9d1' else f'{font}/{g}-{skin}-200d-2764-fe0f-200d-{g}-{skin}.svg'
        left = ET.parse(name).getroot()
        right = ET.parse(name).getroot()
        if g == '1f469':
            for i in range(14, 6, -1):
                remove(left, i)
            for i in range(6, -1, -1):
                remove(right, i)
        else:
            for i in range(12, 5, -1):
                remove(left, i)
            for i in range(5, -1, -1):
                remove(right, i)
        write_dual(left, right, g, g, skin, '2764')
