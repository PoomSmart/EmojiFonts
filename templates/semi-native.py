import os
import sys

sys.path.append('..')
from shared import *
from shared_lig import *

# input: apple font ttf, EMOJI_FONT font ttf

ttf = sys.argv[1]
bttf = sys.argv[2]
f = ttLib.TTFont(ttf)

lig = Lig(f, bttf)
lig.build()

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
    name = lig.norm_name(name)
    name = lig.get_glyph_name(name)
    path = f'images/{ppem}/{name}.png'
    if not os.path.exists(path):
        name = native_norm_name(name)
        path = f'extra/images/{ppem}/{name}.png'
    return get_image_data(path)

process_strikes(f['sbix'].strikes, resolve)

if not os.path.exists('../.test'):
    print('Saving changes...')
    ttf = ttf.replace('../apple/', '')
    f.save(ttf)
