import os
import sys

sys.path.append('..')
from shared import *
from shared_lig import *

# input: apple font ttf, tossface font ttf

ttf = sys.argv[1]
bttf = sys.argv[2]
f = ttLib.TTFont(ttf)

lig = Lig(f, bttf)
lig.build()

def post_special_filter_fn(name: str):
    if name in u15_1 or name.endswith('_200d_27a1'):
        m_print(f'{name} is missing')
        return None
    return name

def image_paths_fn(ppem: int, name: str):
    native = native_norm_name(name)
    return [
        f'images/{ppem}/{name}.png',
        f'../twemoji/images/{ppem}/{native}.png',
        f'../twemoji/extra/images/{ppem}/{native}.png',
        f'../twemoji/extra/images/{ppem}/{native.replace("_", "-")}.png',
    ]

prepare_strikes(f)
resolve = make_resolver(
    post_special_filter_fn=post_special_filter_fn,
    vendor_name_fn=lambda name: lig.get_glyph_name(lig.norm_name(name)),
    image_paths_fn=image_paths_fn,
)
process_strikes(f['sbix'].strikes, resolve)

if not os.path.exists('../.test'):
    print('Saving changes...')
    ttf = ttf.replace('../apple/', '')
    f.save(f'{ttf}')
