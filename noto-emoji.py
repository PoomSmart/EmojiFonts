import os
import sys
from fontTools import ttLib
from shared import *

fontname = 'noto-emoji'

# input: HD boolean, font ttf

hd = sys.argv[1] == 'true'
ttf = sys.argv[2]

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

prepare_strikes(f, hd)
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
        name = base_norm_variants(name)
        name = base_norm_special(name)
        name = noto_name(name)
        path = f'{fontname}/images/{ppem}/emoji_{name}.png'
        if not os.path.exists(path):
            name = name[1:] if name[0] == 'u' else name
            path = f'{fontname}-extra/images/{ppem}/{name}.png'
        glyph.imageData = get_image_data(path)

print('Saving changes...')
ttf = ttf.replace('apple/', '')
f.save(f'{fontname}/{ttf}')
