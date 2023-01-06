import xml.etree.ElementTree as ET

namespace = 'http://www.w3.org/2000/svg'

ET.register_namespace('', namespace)

font = '../../blobmoji/svg'

silhouette_color = '#CCCCCC'
default_skin_color = '#fcc21b'
default_hair_color = '#6d4c41'
default_skin_alternate_color = '#e48c15'
default_skin_alternate_2_color = '#e59900'
default_skin_alternate_3_color = '#e8a23d'
default_man_shirt_color = '#da4105'
default_man_shirt_2_color = '#00bfa5'
default_woman_shirt_color = '#651fff'
default_woman_shirt_alternate_color = '#4527a0'
default_man_ear_color = '#e48c15'
heart_color = '#f06292'

default_colors = [
    default_skin_color,
    default_skin_alternate_color,
    default_skin_alternate_2_color,
    default_skin_alternate_3_color,
    default_hair_color,
    default_man_shirt_color,
    default_man_shirt_2_color,
    default_woman_shirt_color,
    default_woman_shirt_alternate_color,
    default_man_ear_color,
    '#e59600', # stand man alternate skin
    '#616161', # stand man pants
    '#513f35', # stand man mouth
    '#007689', # stand man shirt 2 color
    '#a0f', # stand woman shirt color
    '#7b1fa2', # stand woman shirt alternate color
]

light_skin_color = '#fadcbc'
light_skin_alternate_color = '#dba689'
light_hair_color = '#212121'

skins = [
    'none',
    '1f3fb',
    '1f3fc',
    '1f3fd',
    '1f3fe',
    '1f3ff'
]

skin_names = {
    'none': 'none',
    '1f3fb': 'light',
    '1f3fc': 'medium',
    '1f3fd': 'medium-light',
    '1f3fe': 'medium-dark',
    '1f3ff': 'dark'
}

gender_names = {
    '1f468': 'man',
    '1f469': 'woman',
    '1f9d1': 'person'
}

hair_colors = {
    '1f3fb': '#212121',
    '1f3fc': '#bfa055',
    '1f3fd': '#6d4c41',
    '1f3fe': '#47352d',
    '1f3ff': '#232020'
}

skin_colors = {
    '1f3fb': '#fadcbc',
    '1f3fc': '#e0bb95',
    '1f3fd': '#bf8f68',
    '1f3fe': '#9b643c',
    '1f3ff': '#70534a'
}

skin_alternate_colors = {
    '1f3fb': '#dba689',
    '1f3fc': '#c48e6a',
    '1f3fd': '#99674f',
    '1f3fe': '#7a4c32',
    '1f3ff': '#563e37',
}

def remove(data, index):
    data.remove(data[index])

def remove_child(data, index, child_index):
    parent = data[index]
    parent.remove(parent[child_index])

def write_dual(left, right, code_left, code_right, skin, joiner = None):
    if joiner is None:
        left_name = f'{code_left}.l.svg' if skin == 'none' else f'{code_left}_{skin}.l.svg'
        right_name = f'{code_right}.r.svg' if skin == 'none' else f'{code_right}_{skin}.r.svg'
    else:
        left_name = f'{code_left}_{joiner}.l.svg' if skin == 'none' else f'{code_left}_{skin}_{joiner}.l.svg'
        right_name = f'{code_right}_{joiner}.r.svg' if skin == 'none' else f'{code_right}_{skin}_{joiner}.r.svg'
    left_out = ET.ElementTree(left)
    right_out = ET.ElementTree(right)
    left_out.write(f'svgs/{left_name}', encoding='utf-8')
    right_out.write(f'svgs/{right_name}', encoding='utf-8')

def find_replace_color(data, original_color, replaced_color):
    for g in data:
        if g.tag == f'{{{namespace}}}g':
            if 'fill' in g.attrib and g.get('fill') == original_color:
                g.set('fill', replaced_color)
            else:
                find_replace_color(g, original_color, replaced_color)
        if g.tag == f'{{{namespace}}}ellipse' or g.tag == f'{{{namespace}}}path' or g.tag == f'{{{namespace}}}use':
            if 'style' in g.attrib and original_color in g.attrib['style']:
                g.attrib.pop('style')
                g.set('fill', replaced_color)
            elif 'fill' in g.attrib and original_color in g.attrib['fill']:
                g.set('fill', replaced_color)
            if 'stroke' in g.attrib and original_color in g.attrib['stroke']:
                g.set('stroke', replaced_color)

def make_gray(data, remove_clip_path=True):
    to_remove = []
    for g in data:
        if g.tag == f'{{{namespace}}}g':
            if remove_clip_path and 'clip-path' in g.attrib:
                to_remove.append(g)
            else:
                make_gray(g)
        if g.tag == f'{{{namespace}}}defs' or g.tag == f'{{{namespace}}}clipPath':
            to_remove.append(g)
        elif g.tag == f'{{{namespace}}}path':
            if 'style' in g.attrib:
                style = g.attrib['style']
                if default_skin_alternate_color in style or '#444' in style or '#4c3734' in style:
                    g.attrib.pop('style')
                    to_remove.append(g)
            elif 'fill' in g.attrib:
                fill = g.attrib['fill']
                if fill in ['#e48c15', '#4c3734', '#444']:
                    to_remove.append(g)
    for g in to_remove:
        data.remove(g)
