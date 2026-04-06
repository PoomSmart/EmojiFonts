import os
import sys

sys.path.append('..')
from shared import *

# input: font ttf

ttf = sys.argv[1]

f = ttLib.TTFont(ttf)

def noto_name(name: str):
    tokens = name.split('_')
    n = []
    for t in tokens:
        if t[0] == 'u':
            t = t[1:] # strip u prefix
        n.append(t)
    result = '_'.join(n)
    return 'u' + result

prepare_strikes(f, True)

def resolve(name, glyph, ppem):
    if glyph.graphicType != 'png ':
        return None
    name = base_norm_name(name)
    if base_is_whitelist(name):
        return None
    name = norm_fam(name)
    name = norm_dual(name)
    if name is None:
        return None
    name = base_norm_variants(name)
    name = base_norm_special(name)
    name = noto_name(name)
    path = f'images/{ppem}/emoji_{name}.png'
    if not os.path.exists(path):
        name = name[1:] if name[0] == 'u' else name
        path = f'extra/images/{ppem}/{name}.png'
    return get_image_data(path)

process_strikes(f['sbix'].strikes, resolve)

if not os.path.exists('../.test'):
    print('Saving changes...')
    ttf = ttf.replace('../apple/', '')
    f.save(ttf)
