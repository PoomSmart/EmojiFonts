import xml.etree.ElementTree as ET

namespace = 'http://www.w3.org/2000/svg'

ET.register_namespace('', namespace)

font = '../../../openmoji/color/svg'

silhouette_color = '#7E7E7E'

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

def remove_child_at(data, ident, child_index):
    for g in data:
        if g.tag == f'{{{namespace}}}g':
            if g.get('id') == ident:
                g.remove(g[child_index])
                return

def remove_by_id(data, ident):
    for g in data:
        if g.tag == f'{{{namespace}}}g':
            if g.get('id') == ident:
                data.remove(g)
                return
            remove_by_id(g, ident)
        elif g.get('id') == ident:
            data.remove(g)
            return

def write_dual(left, right, code_left, code_right, skin, joiner = None):
    if joiner is None:
        left_name = f'{code_left}.l.svg' if skin == 'none' else f'{code_left}-{skin}.l.svg'
        right_name = f'{code_right}.r.svg' if skin == 'none' else f'{code_right}-{skin}.r.svg'
    else:
        left_name = f'{code_left}-{joiner}.l.svg' if skin == 'none' else f'{code_left}-{skin}-{joiner}.l.svg'
        right_name = f'{code_right}-{joiner}.r.svg' if skin == 'none' else f'{code_right}-{skin}-{joiner}.r.svg'
    left_out = ET.ElementTree(left)
    right_out = ET.ElementTree(right)
    left_out.write(f'svgs/{left_name}', encoding='utf-8')
    right_out.write(f'svgs/{right_name}', encoding='utf-8')

def apply_silhouette(data):
    to_remove = []
    for g in data:
        if g.tag == f'{{{namespace}}}g':
            apply_silhouette(g)
        elif g.tag == f'{{{namespace}}}path' or g.tag == f'{{{namespace}}}circle':
            if 'fill' in g.attrib:
                fill = g.attrib['fill']
                if fill.upper() in ['#FCEA2B', '#92D3F5', '#A57939']:
                    g.set('fill', silhouette_color)
            if 'stroke' in g.attrib and g.attrib['stroke'] in ['#000', '#000000']:
                g.set('stroke', silhouette_color)
            if 'fill' not in g.attrib: # eyes
                to_remove.append(g)
    for g in to_remove:
        data.remove(g)
