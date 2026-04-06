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

def resolve(name, glyph, ppem):
    if glyph.graphicType != 'png ':
        return None
    name = norm_name(name)
    if base_is_whitelist(name):
        return None
    name = norm_fam(name)
    name = norm_dual(name)
    if name is None:
        return None
    name = base_norm_variants(name, True, True)
    name = base_norm_special(name, True)
    name = twitter_name(name)
    path = f'images/{ppem}/{name}.png'
    if not os.path.exists(path):
        path = f'extra/images/{ppem}/{name}.png'
    return get_image_data(path)

process_strikes(f['sbix'].strikes, resolve)

if not os.path.exists('../.test'):
    print('Saving changes...')
    ttf = ttf.replace('../apple/', '')
    f.save(ttf)
