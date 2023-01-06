import xml.etree.ElementTree as ET
from shared import *

def replace_skin(data, skin):
    find_replace_color(data, '#fac036', skin_colors[skin])
    find_replace_color(data, '#e48c15', skin_alternate_colors[skin])

for skin in skins:
    left = ET.parse('hand.l.svg').getroot()
    right = ET.parse('hand.r.svg').getroot()
    if skin != 'none':
        replace_skin(left, skin)
        replace_skin(right, skin)
    left_name = '1faf1.l.svg' if skin == 'none' else f'1faf1_{skin}.l.svg'
    right_name = '1faf2.r.svg' if skin == 'none' else f'1faf2_{skin}.r.svg'
    left_out = ET.ElementTree(left)
    right_out = ET.ElementTree(right)
    left_out.write(f'svgs/{left_name}', encoding='utf-8')
    right_out.write(f'svgs/{right_name}', encoding='utf-8')

left = ET.parse('hand.l.svg').getroot()
right = ET.parse('hand.r.svg').getroot()
for c in ['#fac036', '#e48c15']:
    find_replace_color(left, c, silhouette_color)
    find_replace_color(right, c, silhouette_color)

left_gray_out = ET.ElementTree(left)
left_gray_out.write('svgs/silhouette_1faf1.l.svg', encoding='utf-8')
right_gray_out = ET.ElementTree(right)
right_gray_out.write('svgs/silhouette_1faf2.r.svg', encoding='utf-8')
