import sys
import os

sys.path.append('..')
from shared import *

# input: font ttf

ttf = sys.argv[1]

f = ttLib.TTFont(ttf)

def norm_name(name: str):
    name = base_norm_name(name)
    if '20e3' in name or name in signs:
        name = name[2:]
    return name

def facebook_name(name: str):
    return name.replace('_', '-')

prepare_strikes(f)
for ppem, strike in f['sbix'].strikes.items():
    print(f'Reading strike of size {ppem}x{ppem}')
    for name, glyph in strike.glyphs.items():
        if glyph.graphicType != 'png ':
            continue
        name = norm_name(name)
        if base_is_whitelist(name):
            continue
        name = norm_fam(name)
        name = norm_dual(name)
        if name is None:
            continue
        name = base_norm_variants(name)
        name = base_norm_special(name)
        name = facebook_name(name)
        path = f'images/{ppem}/{name}.png'
        if not os.path.exists(path) or name.startswith('1f491') or name.startswith('1f48f'):
            path = f'extra/images/{ppem}/{name}.png'
            if not os.path.exists(path):
                name = name.replace('-', '_')
                path = f'extra/images/{ppem}/{name}.png'
        glyph.imageData = get_image_data(path)

if not os.path.exists('../.test'):
    print('Saving changes...')
    ttf = ttf.replace('../apple/', '')
    f.save(ttf)
