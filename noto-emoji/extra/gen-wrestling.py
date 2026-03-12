import xml.etree.ElementTree as ET
import re
import os
import copy
from shared import *

# wrestling uses 1faef as joiner
JOINER = '1faef'

def get_x_coords(element):
    coords = []
    tag = element.tag.split('}')[-1]
    if tag == 'path':
        d = element.attrib.get('d', '')
        # Only look for absolute M coordinates
        for match in re.finditer(r'M\s*([-+]?\d*\.\d+|\d+)', d):
            coords.append(float(match.group(1)))
    elif tag in ['ellipse', 'circle']:
        coords.append(float(element.attrib.get('cx', 0)))
    elif tag == 'rect':
        coords.append(float(element.attrib.get('x', 0)))
    elif tag in ['polygon', 'polyline']:
        points = element.attrib.get('points', '')
        nums = re.findall(r'[-+]?\d*\.\d+|\d+', points)
        for i in range(0, len(nums), 2):
            coords.append(float(nums[i]))
    elif tag == 'g':
        for child in element:
            coords.extend(get_x_coords(child))
    return coords

def is_left(element):
    coords = get_x_coords(element)
    if not coords:
        return None # Undecided (gradients etc)
    
    avg_x = sum(coords) / len(coords)
    return avg_x < 68.8

def split_person(root):
    left_root = ET.Element(root.tag, root.attrib)
    right_root = ET.Element(root.tag, root.attrib)
    
    for child in root:
        side = is_left(child)
        if side is True:
            left_root.append(copy.deepcopy(child))
        elif side is False:
            right_root.append(copy.deepcopy(child))
        else:
            # Undecided (gradients etc) - duplicate in both
            left_root.append(copy.deepcopy(child))
            right_root.append(copy.deepcopy(child))
            
    return left_root, right_root

gender_map = {
    '1f9d1': '1f93c',
    '1f468': '1f93c_200d_2642',
    '1f469': '1f93c_200d_2640'
}

for g_code, filename_base in gender_map.items():
    # Silhouette
    name = f'{font}/emoji_u{filename_base}.svg'
    if not os.path.exists(name):
        print(f"File not found: {name}")
        continue
        
    tree = ET.parse(name)
    root = tree.getroot()
    left, right = split_person(root)
    
    apply_silhouette(left)
    apply_silhouette(right)
    
    left_out = ET.ElementTree(left)
    left_out.write(f'svgs/silhouette_{g_code}_{JOINER}.l.svg', encoding='utf-8')
    right_out = ET.ElementTree(right)
    right_out.write(f'svgs/silhouette_{g_code}_{JOINER}.r.svg', encoding='utf-8')
    
    # Skins
    for skin in skins:
        if skin == 'none':
            name = f'{font}/emoji_u{filename_base}.svg'
        else:
            # Skin tone usually follows u1f93c
            parts = filename_base.split('_')
            # Insert skin after first part
            parts.insert(1, skin)
            name = f'{font}/emoji_u{"_".join(parts)}.svg'
            
        if not os.path.exists(name):
            print(f"Skin file not found: {name}")
            continue
            
        tree = ET.parse(name)
        root = tree.getroot()
        left, right = split_person(root)
        write_dual(left, right, f"{g_code}_{JOINER}", f"{g_code}_{JOINER}", skin, None)
