import xml.etree.ElementTree as ET

namespace = 'http://www.w3.org/2000/svg'

ET.register_namespace('', namespace)

font = '../../openmoji/color/svg'

silhouette_color = '#CCCCCC'

skins = [
    'none',
    '1F3FB',
    '1F3FC',
    '1F3FD',
    '1F3FE',
    '1F3FF'
]

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
    left_out.write(left_name, encoding='utf-8')
    right_out.write(right_name, encoding='utf-8')

def find_set_color(data):
    for g in data:
        if g.tag == f'{{{namespace}}}g':
            find_set_color(g)
        elif g.tag == f'{{{namespace}}}path':
            fill = g.attrib['fill']
            if fill == '#FCEA2B' or (fill == 'none' and g.attrib['stroke'] == '#000000'):
                g.set('fill', silhouette_color)
