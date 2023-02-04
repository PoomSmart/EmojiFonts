import xml.etree.ElementTree as ET
from shared import *

handshake = f'{font}/1F91D.svg'

def remove_left(data):
    remove_by_id(data, 'skin-b')
    to_remove = [9, 8, 7, 6, 5]
    for i in to_remove:
        remove_child_at(data, 'line', i)

def remove_right(data):
    remove_by_id(data, 'skin-a')
    to_remove = [4, 3, 2, 1, 0]
    for i in to_remove:
        remove_child_at(data, 'line', i)

for skin in skins:
    name = handshake if skin == 'none' else f'{font}/1F91D-{skin}.svg'
    left = ET.parse(name).getroot()
    right = ET.parse(name).getroot()
    remove_left(left)
    remove_right(right)
    left_name = '1FAF1.l.svg' if skin == 'none' else f'1FAF1-{skin}.l.svg'
    right_name = '1FAF2.r.svg' if skin == 'none' else f'1FAF2-{skin}.r.svg'
    left_out = ET.ElementTree(left)
    right_out = ET.ElementTree(right)
    left_out.write(f'svgs/{left_name}', encoding='utf-8')
    right_out.write(f'svgs/{right_name}', encoding='utf-8')

left_gray = ET.parse(handshake).getroot()
remove_left(left_gray)
apply_silhouette(left_gray)
left_gray_out = ET.ElementTree(left_gray)
left_gray_out.write('svgs/silhouette-1FAF1.l.svg', encoding='utf-8')
right_gray = ET.parse(handshake).getroot()
remove_right(right_gray)
apply_silhouette(right_gray)
right_gray_out = ET.ElementTree(right_gray)
right_gray_out.write('svgs/silhouette-1FAF2.r.svg', encoding='utf-8')
