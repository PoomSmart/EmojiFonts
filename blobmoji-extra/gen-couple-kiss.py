import xml.etree.ElementTree as ET
from shared import *

# neutral
for skin in skins:
    skin_name = skin_names[skin]
    left = ET.parse('kiss.l.svg').getroot()
    right = ET.parse('kiss.r.svg').getroot()
    if skin != 'none':
        find_replace_color(left, default_hair_color, hair_colors[skin])
        find_replace_color(left, default_skin_color, skin_colors[skin])
        find_replace_color(left, default_skin_alternate_color, skin_alternate_colors[skin])
        find_replace_color(right, default_hair_color, hair_colors[skin])
        find_replace_color(right, default_skin_color, skin_colors[skin])
        find_replace_color(right, default_skin_alternate_color, skin_alternate_colors[skin])
    write_dual(left, right, '1f9d1', '1f9d1', skin, '1f48b')

# neutral silhouette
left = ET.parse('kiss.l.svg').getroot()
right = ET.parse('kiss.r.svg').getroot()
find_replace_color(left, default_hair_color, silhouette_color)
find_replace_color(left, default_skin_color, silhouette_color)
make_gray(left)
find_replace_color(right, default_hair_color, silhouette_color)
find_replace_color(right, default_skin_color, silhouette_color)
make_gray(right)

left_out = ET.ElementTree(left)
left_out.write('svgs/silhouette_1f9d1_1f48b.l.svg', encoding='utf-8')
right_out = ET.ElementTree(right)
right_out.write('svgs/silhouette_1f9d1_1f48b.r.svg', encoding='utf-8')

# woman, man silhouette
for g in ['1f469', '1f468']:
    gender_name = gender_names[g]
    left = ET.parse(f'kiss_{gender_name}.l.svg').getroot()
    right = ET.parse(f'kiss_{gender_name}.r.svg').getroot()
    find_replace_color(left, default_hair_color, silhouette_color)
    find_replace_color(left, default_skin_color, silhouette_color)
    make_gray(left)
    find_replace_color(right, default_hair_color, silhouette_color)
    find_replace_color(right, default_skin_color, silhouette_color)
    make_gray(right)
    left_out = ET.ElementTree(left)
    left_out.write(f'svgs/silhouette_{g}_1f48b.l.svg', encoding='utf-8')
    right_out = ET.ElementTree(right)
    right_out.write(f'svgs/silhouette_{g}_1f48b.r.svg', encoding='utf-8')

# dual woman, dual man
for g in ['1f469', '1f468']:
    gender_name = gender_names[g]
    for skin in skins:
        name = f'kiss_{gender_name}_light' if skin != 'none' and gender_name == 'man' else f'kiss_{gender_name}'
        left = ET.parse(f'{name}.l.svg').getroot()
        right = ET.parse(f'{name}.r.svg').getroot()
        if skin != 'none':
            find_replace_color(left, default_hair_color, hair_colors[skin])
            find_replace_color(left, default_skin_color, skin_colors[skin])
            find_replace_color(left, default_skin_alternate_color, skin_alternate_colors[skin])
            find_replace_color(right, default_hair_color, hair_colors[skin])
            find_replace_color(right, default_skin_color, skin_colors[skin])
            find_replace_color(right, default_skin_alternate_color, skin_alternate_colors[skin])
            if skin != 'light':
                find_replace_color(left, light_hair_color, hair_colors[skin])
                find_replace_color(left, light_skin_color, skin_colors[skin])
                find_replace_color(left, light_skin_alternate_color, skin_alternate_colors[skin])
                find_replace_color(right, light_hair_color, hair_colors[skin])
                find_replace_color(right, light_skin_color, skin_colors[skin])
                find_replace_color(right, light_skin_alternate_color, skin_alternate_colors[skin])
        write_dual(left, right, g, g, skin, '1f48b')
