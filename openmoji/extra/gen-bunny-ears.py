import copy
import os
import re
import xml.etree.ElementTree as ET

from shared import *

JOINER = '1F430'


def get_x_coords(element):
    coords = []
    tag = element.tag.split('}')[-1]
    if tag == 'path':
        d = element.attrib.get('d', '')
        # Use only absolute M x-coordinates to avoid relative offset noise.
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


def get_split_x(root):
    # Use viewBox center when available (e.g. "0 0 72 72").
    vb = root.attrib.get('viewBox', '')
    parts = vb.replace(',', ' ').split()
    if len(parts) == 4:
        try:
            x0 = float(parts[0])
            w = float(parts[2])
            return x0 + (w / 2.0)
        except ValueError:
            pass
    return 36.0


def is_left(element, split_x):
    coords = get_x_coords(element)
    if not coords:
        return None
    avg_x = sum(coords) / len(coords)
    return avg_x < split_x


def split_person(root):
    split_x = get_split_x(root)

    def split_children(src, left_parent, right_parent):
        for child in src:
            tag = child.tag.split('}')[-1]

            if tag in ['svg', 'g', 'defs']:
                left_child = ET.Element(child.tag, child.attrib)
                right_child = ET.Element(child.tag, child.attrib)
                split_children(child, left_child, right_child)
                if len(left_child):
                    left_parent.append(left_child)
                if len(right_child):
                    right_parent.append(right_child)
                continue

            side = is_left(child, split_x)
            if side is True:
                left_parent.append(copy.deepcopy(child))
            elif side is False:
                right_parent.append(copy.deepcopy(child))
            else:
                # Duplicate undecided blocks (gradients/defs/shared refs).
                left_parent.append(copy.deepcopy(child))
                right_parent.append(copy.deepcopy(child))

    left_root = ET.Element(root.tag, root.attrib)
    right_root = ET.Element(root.tag, root.attrib)
    split_children(root, left_root, right_root)
    return left_root, right_root


def source_name(filename_base: str, skin: str) -> str:
    if skin == 'none':
        return f'{font}/{filename_base}.svg'
    parts = filename_base.split('-')
    parts.insert(1, skin)
    return f"{font}/{'-'.join(parts)}.svg"


# 1F9D1 + 1F430 -> 1F46F
# 1F468 + 1F430 -> 1F46F-200D-2642-FE0F
# 1F469 + 1F430 -> 1F46F-200D-2640-FE0F
gender_map = {
    '1F9D1': '1F46F',
    '1F468': '1F46F-200D-2642-FE0F',
    '1F469': '1F46F-200D-2640-FE0F',
}

for g_code, filename_base in gender_map.items():
    # Silhouette from default skin file.
    silhouette_src = f'{font}/{filename_base}.svg'
    if os.path.exists(silhouette_src):
        root = ET.parse(silhouette_src).getroot()
        left, right = split_person(root)
        apply_silhouette(left)
        apply_silhouette(right)
        ET.ElementTree(left).write(
            f'svgs/silhouette-{g_code}-{JOINER}.l.svg',
            encoding='utf-8',
        )
        ET.ElementTree(right).write(
            f'svgs/silhouette-{g_code}-{JOINER}.r.svg',
            encoding='utf-8',
        )

    # Per-skin split assets.
    for skin in skins:
        name = source_name(filename_base, skin)
        if not os.path.exists(name):
            continue
        root = ET.parse(name).getroot()
        left, right = split_person(root)
        write_dual(left, right, g_code, g_code, skin, JOINER)
