import xml.etree.ElementTree as ET
from shared import *

handshake = f'{font}/1f91d.svg'

def set_colors(data, skin, index):
    data[index].set('fill', skins[skin]['primary'])
    data[index + 1].set('fill', skins[skin]['secondary'])

for skin, preset in skins.items():
    left = ET.parse(handshake).getroot()
    right = ET.parse(handshake).getroot()
    set_colors(left, skin, 0)
    remove(left, 3)
    remove(left, 2)
    set_colors(right, skin, 2)
    remove(right, 1)
    remove(right, 0)
    left_name = '1faf1.l.svg' if skin == 'none' else f'1faf1-{skin}.l.svg'
    right_name = '1faf2.r.svg' if skin == 'none' else f'1faf2-{skin}.r.svg'
    left_out = ET.ElementTree(left)
    right_out = ET.ElementTree(right)
    left_out.write(f'svgs/{left_name}', encoding='utf-8')
    right_out.write(f'svgs/{right_name}', encoding='utf-8')

left_gray = ET.parse(handshake).getroot()
left_gray[0].set('fill', silhouette_color)
left_gray[1].set('fill', silhouette_color)
remove(left_gray, 3)
remove(left_gray, 2)
left_gray_out = ET.ElementTree(left_gray)
left_gray_out.write('svgs/silhouette-1faf1.l.svg', encoding='utf-8')
right_gray = ET.parse(handshake).getroot()
right_gray[2].set('fill', silhouette_color)
right_gray[3].set('fill', silhouette_color)
remove(right_gray, 1)
remove(right_gray, 0)
right_gray_out = ET.ElementTree(right_gray)
right_gray_out.write('svgs/silhouette-1faf2.r.svg', encoding='utf-8')