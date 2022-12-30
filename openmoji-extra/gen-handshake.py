import xml.etree.ElementTree as ET
from shared import *

handshake = f'emoji_u1f91d.svg'

def remove_left(data):
    to_remove = [9, 8, 7, 5, 4, 3, 0]
    for i in to_remove:
        data.remove(data[i])

def remove_right(data):
    to_remove = [12, 11, 10, 6, 2, 1]
    for i in to_remove:
        data.remove(data[i])

for skin in skins:
    name = handshake if skin == 'none' else f'emoji_u1f91d_{skin}.svg'
    left = ET.parse(name).getroot()
    right = ET.parse(name).getroot()
    remove_left(right[0])
    remove_right(left[0])
    left_name = '1faf1.l.svg' if skin == 'none' else f'1faf1_{skin}.l.svg'
    right_name = '1faf2.r.svg' if skin == 'none' else f'1faf2_{skin}.r.svg'
    left_out = ET.ElementTree(left)
    right_out = ET.ElementTree(right)
    left_out.write(left_name, encoding='utf-8')
    right_out.write(right_name, encoding='utf-8')

left_gray = ET.parse(handshake).getroot()
remove_right(left_gray[0])
find_set_color(left_gray)
left_gray_out = ET.ElementTree(left_gray)
left_gray_out.write('silhouette_1faf1.l.svg', encoding='utf-8')
right_gray = ET.parse(handshake).getroot()
remove_left(right_gray[0])
find_set_color(right_gray)
right_gray_out = ET.ElementTree(right_gray)
right_gray_out.write('silhouette_1faf2.r.svg', encoding='utf-8')