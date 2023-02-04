import sys
import os
from fontTools import ttLib

sys.path.append('..')
from shared import *

# input: font ttf, emoji style

ttf = sys.argv[1]
style = sys.argv[2]

f = ttLib.TTFont(ttf)

def joypixels_name(name: str):
    tokens = name.split('_')
    n = []
    remove = ['fe0f', '200d']
    for token in tokens:
        if token in remove:
            continue
        n.append(token)
    return '-'.join(n)

prepare_strikes(f)
for ppem, strike in f['sbix'].strikes.items():
    print(f'Reading strike of size {ppem}x{ppem}')
    for name, glyph in strike.glyphs.items():
        if glyph.graphicType != 'png ':
            continue
        name = base_norm_name(name)
        if base_is_whitelist(name):
            continue
        name = norm_fam(name)
        name = norm_dual(name)
        if name is None:
            continue
        name = base_norm_variants(name, True, True)
        name = base_norm_special(name, True)
        name = joypixels_name(name)
        path = f'{style}/images/{ppem}/{name}.png'
        if not os.path.exists(path):
            name = name.replace('-', '_')
            path = f'extra/images/{ppem}/{name}.png'
        glyph.imageData = get_image_data(path)

if not os.path.exists('../.test'):
    print('Saving changes...')
    ttf = ttf.replace('../apple/', '')
    f.save(f'{style}-{ttf}')
