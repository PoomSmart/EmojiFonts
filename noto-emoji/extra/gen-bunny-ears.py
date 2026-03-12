import xml.etree.ElementTree as ET
import re
import os
from shared import *

def get_x_coords(element):
    coords = []
    tag = element.tag.split('}')[-1]
    if tag == 'path':
        d = element.attrib.get('d', '')
        # Only look for absolute M coordinates to avoid relative offset pollution
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
        # For gradients and other non-geometric elements, check ID or assume both
        cid = element.attrib.get('id', '')
        if '_2_' in cid or '_1_' in cid: # This is flimsy
            pass
        return None # Undecided
    
    avg_x = sum(coords) / len(coords)
    return avg_x < 66

import copy

def split_person(root):
    left_root = ET.Element(root.tag, root.attrib)
    right_root = ET.Element(root.tag, root.attrib)
    
    l_count = 0
    r_count = 0
    for child in root:
        side = is_left(child)
        if side is True:
            left_root.append(copy.deepcopy(child))
            l_count += 1
        elif side is False:
            right_root.append(copy.deepcopy(child))
            r_count += 1
        else:
            left_root.append(copy.deepcopy(child))
            right_root.append(copy.deepcopy(child))
            l_count += 1
            r_count += 1
            
    # print(f"Split results: L={l_count}, R={r_count}")
    return left_root, right_root

# We need to support:
# neutral: 1f46f
# man: 1f46f_200d_2642
# woman: 1f46f_200d_2640

gender_map = {
    '1f9d1': '1f46f',
    '1f468': '1f46f_200d_2642',
    '1f469': '1f46f_200d_2640'
}

for g_code, filename_base in gender_map.items():
    # Silhouette
    name = f'{font}/emoji_u{filename_base}.svg'
    tree = ET.parse(name)
    root = tree.getroot()
    left, right = split_person(root)
    
    apply_silhouette(left)
    apply_silhouette(right)
    
    left_out = ET.ElementTree(left)
    left_out.write(f'svgs/silhouette_{g_code}_1f430.l.svg', encoding='utf-8')
    right_out = ET.ElementTree(right)
    right_out.write(f'svgs/silhouette_{g_code}_1f430.r.svg', encoding='utf-8')
    
    # Skins
    for skin in skins:
        if skin == 'none':
            name = f'{font}/emoji_u{filename_base}.svg'
        else:
            # Filename for skin is emoji_u1f46f_1f3fb_... or emoji_u1f46f_..._1f3fb?
            # Looking at file list: emoji_u1f46f_1f3fb_200d_2642.svg
            parts = filename_base.split('_')
            if len(parts) > 1:
                # Insert skin after first part: 1f46f_1f3fb_200d_2642
                parts.insert(1, skin)
                name = f'{font}/emoji_u{"_".join(parts)}.svg'
            else:
                name = f'{font}/emoji_u{filename_base}_{skin}.svg'
        
        if not os.path.exists(name):
            continue
            
        tree = ET.parse(name)
        root = tree.getroot()
        left, right = split_person(root)
        
        write_dual(left, right, f"{g_code}_1f430", f"{g_code}_1f430", skin, None)
