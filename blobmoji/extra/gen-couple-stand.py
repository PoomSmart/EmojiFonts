import xml.etree.ElementTree as ET
from shared import *

def replace_skin(data, skin):
    find_replace_color(data, default_hair_color, hair_colors[skin])
    find_replace_color(data, default_skin_color, skin_colors[skin])
    find_replace_color(data, default_skin_alternate_color, skin_alternate_colors[skin])
    find_replace_color(data, default_skin_alternate_2_color, skin_alternate_colors[skin])
    find_replace_color(data, default_skin_alternate_3_color, skin_alternate_colors[skin])

for g in ['1f469', '1f468']:
    gender_name = gender_names[g]
    for skin in skins:
        left = ET.parse(f'stand_{gender_name}.l.svg').getroot()
        right = ET.parse(f'stand_{gender_name}.r.svg').getroot()
        if skin != 'none':
            replace_skin(left, skin)
            replace_skin(right, skin)
        write_dual(left, right, g, g, skin)
    left = ET.parse(f'stand_{gender_name}.l.svg').getroot()
    right = ET.parse(f'stand_{gender_name}.r.svg').getroot()
    for c in default_colors:
        find_replace_color(left, c, silhouette_color)
        find_replace_color(right, c, silhouette_color)
    make_gray(left, False)
    make_gray(right, False)
    left_out = ET.ElementTree(left)
    left_out.write(f'svgs/silhouette.{gender_name[0]}l.svg', encoding='utf-8')
    right_out = ET.ElementTree(right)
    right_out.write(f'svgs/silhouette.{gender_name[0]}r.svg', encoding='utf-8')
