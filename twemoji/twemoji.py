import os
import sys

sys.path.append('..')
from shared import *

# input: font ttf

ttf = sys.argv[1]

f = ttLib.TTFont(ttf)

def norm_name(name: str):
    result = base_norm_name(name)
    if '20e3' in result or result in signs:
        result = result[2:]
    return result

def twitter_name(name: str):
    return name.replace('_', '-')

prepare_strikes(f, True)
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
        name = base_norm_variants(name, True, True)
        name = base_norm_special(name, True)
        if name in u15:
            print(f'{name} is missing')
            continue
        name = twitter_name(name)
        path = f'images/{ppem}/{name}.png'
        if not os.path.exists(path):
            path = f'extra/images/{ppem}/{name}.png'
        glyph.imageData = get_image_data(path)

if not os.path.exists('../.test'):
    print('Saving changes...')
    ttf = ttf.replace('../apple/', '')
    f.save(ttf)
