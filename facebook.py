import sys
import io
import os
from fontTools import ttLib
from PIL import Image as PImage
from shared import *

fontname = 'facebook'

# input: font ttf, assets folder

ttf = sys.argv[1]
assets = sys.argv[2]

f = ttLib.TTFont(ttf)

with_variants = [
    '203c', '2049', '2122', '2139', '2194',
    '2195', '2196', '2197', '2198', '2199',
    '21a9', '21aa', '2328', '23cf', '23ed',
    '23ee', '23ef', '23f1', '23f2', '23f8',
    '23f9', '23fa', '24c2', '25aa', '25ab',
    '25b6', '25c0', '25fb', '25fc', '2600',
    '2601', '2602', '2603', '2604', '2611',
    '2618', '261d', '2620', '2622', '2623',
    '2626', '2638', '2639', '2660', '2663',
    '2665', '2666', '2668', '2692', '2694',
    '2696', '2697', '2699', '26a0', '26a7',
    '26b0', '26b1', '26c8', '26cf', '26d1',
    '26d3', '26e9', '26f0', '26f1', '26f4',
    '26f7', '26f8', '26f9', '27a1', '203c',
    '260e', '262a', '262e', '262f', '263a',
    '265f', '267b', '267e', '269b', '269c',
    '2702', '2708', '2709', '270c', '270d',
    '270f', '2712', '2714', '2716', '271d',
    '2721', '2733', '2734', '2744', '2747',
    '2763', '2764', '2934', '2935', '2b05',
    '2b06', '2b07', '303d', '3030', '3297',
    '3299',
    '1f170', '1f171', '1f17e', '1f17f', '1f202',
    '1f237', '1f321', '1f324', '1f325', '1f326',
    '1f327', '1f328', '1f329', '1f32a', '1f32b',
    '1f32c', '1f336', '1f37d', '1f396', '1f397',
    '1f399', '1f39a', '1f39b', '1f39e', '1f39f',
    '1f3cb', '1f3cc', '1f3cd', '1f3ce', '1f3d4',
    '1f3d5', '1f3d6', '1f3d7', '1f3d8', '1f3d9',
    '1f3da', '1f3db', '1f3dc', '1f3dd', '1f3de',
    '1f3df', '1f3f3', '1f3f5', '1f3f7', '1f43f',
    '1f441', '1f4fd', '1f549', '1f54a', '1f56f',
    '1f570', '1f573', '1f574', '1f575', '1f576',
    '1f577', '1f578', '1f579', '1f587', '1f58a',
    '1f58b', '1f58c', '1f58d', '1f590', '1f5a5',
    '1f5a8', '1f5b1', '1f5b2', '1f5bc', '1f5c2',
    '1f5c3', '1f5c4', '1f5d1', '1f5d2', '1f5d3',
    '1f5dc', '1f5dd', '1f5de', '1f5e1', '1f5e3',
    '1f5e8', '1f5ef', '1f5f3', '1f5fa', '1f6cb',
    '1f6cd', '1f6ce', '1f6cf', '1f6e0', '1f6e1',
    '1f6e2', '1f6e3', '1f6e4', '1f6e5', '1f6e9',
    '1f6f0', '1f6f3'
]

specials = {
    '23_20e3': '23-20e3',
    '2a_20e3': '2a-20e3',
    '30_20e3': '30-20e3',
    '31_20e3': '31-20e3',
    '32_20e3': '32-20e3',
    '33_20e3': '33-20e3',
    '34_20e3': '34-20e3',
    '35_20e3': '35-20e3',
    '36_20e3': '36-20e3',
    '37_20e3': '37-20e3',
    '38_20e3': '38-20e3',
    '39_20e3': '39-20e3',
    '26f9.0.w': '26f9-200d-2640',
    '2764_1f525' : '2764-200d-1f525',
    '2764_1fa79': '2764-200d-1fa79',
    '1f3cb.0.w': '1f3cb-200d-2640',
    '1f3cc.0.w': '1f3cc-200d-2640',
    '1f3f3_26a7': '1f3f3-200d-26a7',
    '1f441_1f5e8': '1f441-200d-1f5e8',
    '1f575.0.w': '1f575-200d-2640',
    '1f636_1f32b': '1f636-200d-1f32b',
    '1f9d4.0.w': '1f9d4-200d-2640',
    '1f9d4.1.w': '1f9d4-1f3fb-200d-2640',
    '1f9d4.2.w': '1f9d4-1f3fc-200d-2640',
    '1f9d4.3.w': '1f9d4-1f3fd-200d-2640',
    '1f9d4.4.w': '1f9d4-1f3fe-200d-2640',
    '1f9d4.5.w': '1f9d4-1f3ff-200d-2640'
}

hairs = ['1f9b1', '1f9b2', '1f9b3']

def is_missing_duo(name):
    if len(name) < 20:
        return False
    if name[:5] == neutral:
        return name[:-2][0] != '5'
    return False

def is_whitelist(name):
    return name in hairs or base_is_whitelist(name) or '.l' in name or '.r' in name or 'silhouette.' in name

def norm_name(name):
    result = base_norm_name(name)
    if '20e3' in result:
        result = result[2:]
    return result

def norm_variant_selector(name):
    if name in with_variants:
        return f'{name}_fe0f'
    return name

def facebook_name(name):
    return name.replace('_', '-')

for ppem, strike in f['sbix'].strikes.items():
    print(f'Reading strike of size {ppem}x{ppem}')
    for name, glyph in strike.glyphs.items():
        if glyph.graphicType != 'png ':
            continue
        name = norm_name(name)
        if is_whitelist(name):
            continue
        is_special = name in specials.keys()
        if is_special:
            o_name = name
            name = specials[name]
            if name is None:
                m_print(f'{o_name} is missing')
                continue
        elif is_missing_duo(name):
            m_print(f'{name} is missing')
            continue
        else:
            name = norm_fam(name)
            name = norm_dual(name)
            if name is None:
                continue
            name = base_norm_variants(name, True, True)
            name = base_norm_special(name, True)
            name = norm_variant_selector(name)
        name = facebook_name(name)
        path = f'{assets}/{name}.png'
        if not os.path.exists(path):
            path = f'./{fontname}-extra/{name}.png'
        with PImage.open(path) as fin:
            fin = fin.resize((ppem, ppem), PImage.ANTIALIAS)
            stream = io.BytesIO()
            fin.save(stream, format='png')
            glyph.imageData = stream.getvalue()
            stream.close()

print('Saving changes...')
ttf = ttf.replace('common/', '')
f.save(f'{fontname}/{ttf}')