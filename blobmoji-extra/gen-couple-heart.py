import xml.etree.ElementTree as ET
from shared import *

def replace_skin(data, skin):
    find_replace_color(data, default_hair_color, hair_colors[skin])
    find_replace_color(data, default_skin_color, skin_colors[skin])
    find_replace_color(data, default_skin_alternate_color, skin_alternate_colors[skin])
    find_replace_color(data, default_skin_alternate_2_color, skin_alternate_colors[skin])

# neutral
for skin in skins:
    skin_name = skin_names[skin]
    left = ET.parse('couple.l.svg').getroot()
    right = ET.parse('couple.r.svg').getroot()
    if skin != 'none':
        replace_skin(left, skin)
        replace_skin(right, skin)
    write_dual(left, right, '1f9d1', '1f9d1', skin, '2764')

# dual woman, dual man
for g in ['1f469', '1f468', '1f9d1']:
    gender_name = gender_names[g]
    name = 'couple' if g == '1f9d1' else f'couple_{gender_name}'
    left = ET.parse(f'{name}.l.svg').getroot()
    right = ET.parse(f'{name}.r.svg').getroot()
    for c in default_colors:
        find_replace_color(left, c, silhouette_color)
        find_replace_color(right, c, silhouette_color)
    make_gray(left, False)
    make_gray(right, False)
    left_out = ET.ElementTree(left)
    left_out.write(f'svgs/silhouette_{g}_2764.l.svg', encoding='utf-8')
    right_out = ET.ElementTree(right)
    right_out.write(f'svgs/silhouette_{g}_2764.r.svg', encoding='utf-8')
    gender_name = gender_names[g]
    for skin in skins:
        name = 'couple' if gender_name == 'person' else f'couple_{gender_name}'
        left = ET.parse(f'{name}.l.svg').getroot()
        right = ET.parse(f'{name}.r.svg').getroot()
        if skin != 'none':
            replace_skin(left, skin)
            replace_skin(right, skin)
        write_dual(left, right, g, g, skin, '2764')
