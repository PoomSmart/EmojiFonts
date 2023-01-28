import sys
import os
from fontTools import ttLib
from shared import *

fontname = 'joypixels'

# input: font ttf, emoji style

ttf = sys.argv[1]
style = sys.argv[2] if len(sys.argv) > 2 else None

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
        path = f'{fontname}/{ppem}/{name}.png' if style is None else f'{fontname}/{style}/{ppem}/{name}.png'
        if not os.path.exists(path):
            name = name.replace('-', '_')
            path = f'{fontname}-extra/images/{ppem}/{name}.png'
        glyph.imageData = get_image_data(path)

print('Saving changes...')
ttf = ttf.replace('apple/', '')
f.save(f'{fontname}/{ttf}' if style is None else f'{fontname}/{style}-{ttf}')
