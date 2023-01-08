import sys
import io
import os
from fontTools import ttLib
from PIL import Image as PImage
from shared import *

fontname = 'facebook'

# input: font ttf

ttf = sys.argv[1]

f = ttLib.TTFont(ttf)

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

def is_whitelist(name: str):
    return name in hairs or base_is_whitelist(name)

def norm_name(name: str):
    result = base_norm_name(name)
    if '20e3' in result:
        result = result[2:]
    return result

def facebook_name(name: str):
    return name.replace('_', '-')

for ppem, strike in f['sbix'].strikes.items():
    print(f'Reading strike of size {ppem}x{ppem}')
    for name, glyph in strike.glyphs.items():
        if glyph.graphicType != 'png ':
            continue
        name = norm_name(name)
        if is_whitelist(name):
            continue
        is_special = name in specials
        if is_special:
            o_name = name
            name = specials[name]
            if name is None:
                m_print(f'{o_name} is missing')
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
        path = f'{fontname}/images/{ppem}/{name}.png'
        if not os.path.exists(path) or name.startswith('1f491'):
            path = f'{fontname}-extra/images/{ppem}/{name}.png'
            if not os.path.exists(path):
                name = name.replace('-', '_')
                path = f'{fontname}-extra/images/{ppem}/{name}.png'
        with PImage.open(path) as fin:
            stream = io.BytesIO()
            fin.save(stream, format='png')
            glyph.imageData = stream.getvalue()
            stream.close()

print('Saving changes...')
ttf = ttf.replace('common/', '')
f.save(f'{fontname}/{ttf}')
