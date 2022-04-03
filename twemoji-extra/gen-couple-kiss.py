import xml.etree.ElementTree as ET
from shared import *

# neutral
for skin in skins.keys():
    name = f'{font}/1f48f.svg' if skin == 'none' else f'{font}/1f48f-{skin}.svg'
    left = ET.parse(name).getroot()
    right = ET.parse(name).getroot()
    for i in range(8, 3, -1):
        remove(left, i)
    for i in range(3, -1, -1):
        remove(right, i)
    write_dual(left, right, '1f9d1', '1f9d1', skin, '1f48b')

# neutral silhouette
name = f'{font}/1f48f.svg' 
left = ET.parse(name).getroot()
right = ET.parse(name).getroot()
for i in range(8, 3, -1):
    remove(left, i)
for i in range(3, -1, -1):
    remove(right, i)
for c in left:
    c.set('fill', silhouette_color)
for c in right:
    if c.get('fill') == '#DD2E44':
        continue
    c.set('fill', silhouette_color)
left_out = ET.ElementTree(left)
left_out.write('svgs/silhouette-1f9d1-1f48b.l.svg', encoding='utf-8')
right_out = ET.ElementTree(right)
right_out.write('svgs/silhouette-1f9d1-1f48b.r.svg', encoding='utf-8')

# woman, man silhouette
for g in ['1f469', '1f468']:
    name = f'{font}/{g}-200d-2764-fe0f-200d-1f48b-200d-{g}.svg'
    left = ET.parse(name).getroot()
    right = ET.parse(name).getroot()
    for i in range(8, 3, -1):
        remove(left, i)
    for i in range(3, -1, -1):
        remove(right, i)
    for c in left:
        c.set('fill', silhouette_color)
    for c in right:
        c.set('fill', silhouette_color)
    left_out = ET.ElementTree(left)
    left_out.write(f'svgs/silhouette-{g}-1f48b.l.svg', encoding='utf-8')
    right_out = ET.ElementTree(right)
    right_out.write(f'svgs/silhouette-{g}-1f48b.r.svg', encoding='utf-8')

# dual woman, dual man
for g in ['1f469', '1f468']:
    for skin in skins.keys():
        if skin == 'none':
            name = f'{font}/{g}-200d-2764-fe0f-200d-1f48b-200d-{g}.svg'
        else:
            name = f'{font}/{g}-{skin}-200d-2764-fe0f-200d-1f48b-200d-{g}-{skin}.svg'
        left = ET.parse(name).getroot()
        right = ET.parse(name).getroot()
        for i in range(8, 3, -1):
            remove(left, i)
        for i in range(3, -1, -1):
            remove(right, i)
        write_dual(left, right, g, g, skin, '1f48b')