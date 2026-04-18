import os
import sys

sys.path.append('..')
from shared import *

# input: font ttf

ttf = sys.argv[1]

f = ttLib.TTFont(ttf)

corrections = {
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

def image_paths_fn(ppem: int, name: str):
    paths = [f'images/{ppem}/emoji_{name}.png']
    corrected = corrections.get(name, name)
    if corrected != name:
        paths.append(f'images/{ppem}/emoji_{corrected}.png')
    if len(name.split('_')) == 2 or name == 'u1f3f3_fe0f_200d_26a7_fe0f':
        paths.append(f'images/{ppem}/emoji_{name.replace("_fe0f", "")}.png')
    no_u = name[1:] if name.startswith('u') else name
    paths.append(f'extra/images/{ppem}/{no_u}.png')
    paths.append(f'../noto-emoji/extra/images/{ppem}/{no_u}.png')
    return paths

prepare_strikes(f, True)
resolve = make_resolver(
    vendor_name_fn=noto_style_name,
    image_paths_fn=image_paths_fn,
)
process_strikes(f['sbix'].strikes, resolve)

if not os.path.exists('../.test'):
    print('Saving changes...')
    ttf = ttf.replace('../apple/', '')
    f.save(ttf)
