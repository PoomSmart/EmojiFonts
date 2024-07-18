import sys
import os

sys.path.append('..')
from shared import *
from shared_lig import *

# input: font ttf
ttf = sys.argv[1]
bttf = sys.argv[2]
bgsubttx = sys.argv[3]

f = ttLib.TTFont(ttf)

lig = Lig(f, bttf, bgsubttx)
lig.build()

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
        o_name = facebook_name(name)
        name = lig.norm_name(name)
        name = lig.get_glyph_name(name)
        path = f'images/{ppem}/{o_name}.png'
        if not os.path.exists(path) or name.startswith('1f491') or o_name.startswith('1f48f'):
            path = f'extra/images/{ppem}/{o_name}.png'
            if not os.path.exists(path):
                o_name = o_name.replace('-', '_')
                path = f'extra/images/{ppem}/{o_name}.png'
                if not os.path.exists(path):
                    path = f'images/{ppem}/{name}.png'
        glyph.imageData = get_image_data(path)

if not os.path.exists('../.test'):
    print('Saving changes...')
    ttf = ttf.replace('../apple/', '')
    f.save(ttf)
