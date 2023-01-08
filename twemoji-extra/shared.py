import xml.etree.ElementTree as ET

ET.register_namespace('', 'http://www.w3.org/2000/svg')

font = '../../twemoji/assets/svg'

silhouette_color = '#CCCCCC'

skins = {
    'none': {
        'primary': '#EF9645',
        'secondary': '#FFDC5D'
    },
    '1f3fb': {
        'primary': '#E0AA94',
        'secondary': '#F7DECE'
    },
    '1f3fc': {
        'primary': '#D2A077',
        'secondary': '#F3D2A2'
    },
    '1f3fd': {
        'primary': '#B78B60',
        'secondary': '#D4AB88'
    },
    '1f3fe': {
        'primary': '#90603E',
        'secondary': '#AF7E57'
    },
    '1f3ff': {
        'primary': '#583529',
        'secondary': '#7C533E'
    }
}

def remove(data, index):
    data.remove(data[index])

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
