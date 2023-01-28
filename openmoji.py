import os
import sys
from fontTools import ttLib
from shared import *

fontname = 'openmoji'

# input: HD boolean, font ttf

hd = sys.argv[1] == 'true'
ttf = sys.argv[2]

f = ttLib.TTFont(ttf)

def norm_name(name: str):
    result = base_norm_name(name)
    if '20e3' in result:
        result = result.replace('_20e3', '_fe0f_20e3')
    return result

def norm_special(name: str):
    if name == '1f441_1f5e8':
        return '1f441_fe0f_200d_1f5e8_fe0f'
    return base_norm_special(name, True)

def openmoji_name(name: str):
    return name.replace('_', '-').upper()

prepare_strikes(f, hd)
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
        name = norm_special(name)
        name = openmoji_name(name)
        path = f'{fontname}/images/{ppem}/{name}.png'
        if not os.path.exists(path):
            if name.startswith('silhouette'):
                name = name.lower()
            name = name.replace('.L', '.l').replace('.R', '.r')
            path = f'{fontname}-extra/images/{ppem}/{name}.png'
        glyph.imageData = get_image_data(path)

print('Saving changes...')
ttf = ttf.replace('apple/', '')
f.save(f'{fontname}/{ttf}')
