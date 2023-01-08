import xml.etree.ElementTree as ET

namespace = 'http://www.w3.org/2000/svg'

ET.register_namespace('', namespace)

font = '../../noto-emoji/svg'

silhouette_color = '#CCCCCC'

skins = [
    'none',
    '1f3fb',
    '1f3fc',
    '1f3fd',
    '1f3fe',
    '1f3ff'
]

def remove(data, index):
    data.remove(data[index])

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

def apply_silhouette(data):
    for g in data:
        if g.tag == f'{{{namespace}}}g':
            apply_silhouette(g)
        elif g.tag == f'{{{namespace}}}path':
            style = g.attrib['style']
            if style == 'fill:#F386AB;' or style == 'fill:#DA2E75;' or style == 'fill:#EF5592;':
                continue
            g.attrib.pop('style')
            g.set('fill', silhouette_color)
    to_remove = []
    for g in data:
        if g.tag == f'{{{namespace}}}linearGradient' or g.tag == f'{{{namespace}}}radialGradient' or g.tag == f'{{{namespace}}}ellipse' or g.tag == f'{{{namespace}}}polygon':
            to_remove.append(g)
    for g in to_remove:
        data.remove(g)
