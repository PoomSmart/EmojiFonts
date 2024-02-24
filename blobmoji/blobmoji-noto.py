import os
import sys

sys.path.append('..')
from shared import *

# input: font ttf

ttf = sys.argv[1]

f = ttLib.TTFont(ttf)

def blobmoji_name(name: str):
    tokens = name.split('_')
    n = []
    for t in tokens:
        if t[0] == 'u':
            t = t[1:] # strip u prefix
        n.append(t)
    result = '_'.join(n)
    if result.endswith('_20e3'):
        result = result[2:]
    return 'u' + result

corrections = {
    'u26d3_200d_1f4a5': 'u26d3_fe0f_200d_1f4a5',
    'u1f3cc_200d_2640': 'u1f3cc_fe0f_200d_2640',
    'u1f3f3_fe0f_200d_1f308': 'u1f3f3_200d_1f308',
    'u1f3f4_200d_2620_fe0f': 'u1f3f4_200d_2620',
    'u1f43b_200d_2744_fe0f': 'u1f43b_200d_2744',
    'u1f468_200d_2695_fe0f': 'u1f468_200d_2695',
    'u1f468_200d_2696_fe0f': 'u1f468_200d_2696',
    'u1f468_200d_2708_fe0f': 'u1f468_200d_2708',
    'u1f469_200d_2695_fe0f': 'u1f468_200d_2695',
    'u1f469_200d_2696_fe0f': 'u1f468_200d_2696',
    'u1f469_200d_2708_fe0f': 'u1f468_200d_2708',
    'u1f636_200d_1f32b_fe0f': 'u1f636_200d_1f32b',
    'u1f9ce': 'u1f9ce_200d_2640',
    'u1f9ce_1f3fb': 'u1f9ce_1f3fb_200d_2640',
    'u1f9ce_1f3fc': 'u1f9ce_1f3fc_200d_2640',
    'u1f9ce_1f3fd': 'u1f9ce_1f3fd_200d_2640',
    'u1f9ce_1f3fe': 'u1f9ce_1f3fe_200d_2640',
    'u1f9ce_1f3ff': 'u1f9ce_1f3ff_200d_2640',
    'u1f9d1_200d_2695_fe0f': 'u1f9d1_200d_2695',
    'u1f9d1_200d_2696_fe0f': 'u1f9d1_200d_2696',
    'u1f9d1_200d_2708_fe0f': 'u1f9d1_200d_2708',
}

noto = [
    'u1f9d1_200d_1f9b2',
    'u1f9d1_1f3fb_200d_1f9b2',
    'u1f9d1_1f3fc_200d_1f9b2',
    'u1f9d1_1f3fd_200d_1f9b2',
    'u1f9d1_1f3fe_200d_1f9b2',
    'u1f9d1_1f3ff_200d_1f9b2',
]

prepare_strikes(f)
for ppem, strike in f['sbix'].strikes.items():
    print(f'Reading strike of size {ppem}x{ppem}')
    for name, glyph in strike.glyphs.items():
        if glyph.graphicType != 'png ':
            continue
        name = base_norm_name(name)
        if base_is_whitelist(name):
            continue
        name = norm_fam(name)
        name = norm_dual(name)
        if name is None or name in signs:
            continue
        name = base_norm_variants(name)
        name = base_norm_special(name, True)
        name = norm_variant_selector(name)
        name = blobmoji_name(name)
        path = f'images/{ppem}/emoji_{name}.png'
        if not os.path.exists(path):
            if name in corrections:
                name = corrections[name]
                path = f'images/{ppem}/emoji_{name}.png'
            if len(name.split('_')) == 2 or name == 'u1f3f3_fe0f_200d_26a7_fe0f':
                m_name = name.replace('_fe0f', '')
                path = f'images/{ppem}/emoji_{m_name}.png'
            if name in noto:
                path = f'../noto-emoji/images/{ppem}/emoji_{name}.png'
            if not os.path.exists(path):
                name = name[1:] if name[0] == 'u' else name
                path = f'extra/images/{ppem}/{name}.png'
        glyph.imageData = get_image_data(path)

if not os.path.exists('../.test'):
    print('Saving changes...')
    ttf = ttf.replace('../apple/', '')
    f.save(ttf)
