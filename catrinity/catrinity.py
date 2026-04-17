import os
import sys

sys.path.append('..')
from shared import *

# input: font ttf

ttf = sys.argv[1]

f = ttLib.TTFont(ttf)

def norm_name(name: str) -> str:
    result = base_norm_name(name)
    if '20e3' in result or result in signs:
        result = result[2:]
    return result

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
    # Catrinity images (main + extra composites)
    path = f'images/{ppem}/{name}.png'
    if os.path.exists(path):
        return get_image_data(path)
    path = f'extra/images/{ppem}/{name}.png'
    if os.path.exists(path):
        return get_image_data(path)
    # Fall back to Twemoji for any glyph Catrinity doesn't cover.
    # Requires twemoji.sh to have been run first.
    tw = name.replace('_', '-')
    path = f'../twemoji/images/{ppem}/{tw}.png'
    if os.path.exists(path):
        return get_image_data(path)
    path = f'../twemoji/extra/images/{ppem}/{tw}.png'
    if os.path.exists(path):
        return get_image_data(path)
    return None

process_strikes(f['sbix'].strikes, resolve)

if not os.path.exists('../.test'):
    print('Saving changes...')
    ttf = ttf.replace('../apple/', '')
    f.save(ttf)
