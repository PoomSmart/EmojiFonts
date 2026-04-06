import os
import sys

sys.path.append('..')
from shared import *
from shared_lig import *

# input: apple font ttf, noto-emoji-cursed font ttf

ttf = sys.argv[1]
bttf = sys.argv[2]
f = ttLib.TTFont(ttf)

lig = Lig(f, bttf)
lig.build()

def noto_name(name: str):
    tokens = name.split('_')
    n = []
    for t in tokens:
        if t[0] == 'u':
            t = t[1:] # strip u prefix
        n.append(t)
    result = '_'.join(n)
    return 'u' + result

prepare_strikes(f)

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
    fallback_name = noto_name(name)
    name = lig.norm_name(name)
    name = lig.get_glyph_name(name)
    path = f'images/{ppem}/{name}.png'
    if not os.path.exists(path):
        path = f'../noto-emoji/images/{ppem}/emoji_{fallback_name}.png'
        if not os.path.exists(path):
            name = native_norm_name(name)
            path = f'../noto-emoji/extra/images/{ppem}/{name}.png'
    return get_image_data(path)

process_strikes(f['sbix'].strikes, resolve)

if not os.path.exists('../.test'):
    print('Saving changes...')
    ttf = ttf.replace('../apple/', '')
    f.save(ttf)
