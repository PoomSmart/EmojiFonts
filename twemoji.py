import os
import sys
from fontTools import ttLib
from shared import *

fontname = 'twemoji'

# input: font ttf

ttf = sys.argv[1]

f = ttLib.TTFont(ttf)

def norm_name(name: str):
    result = base_norm_name(name)
    if '20e3' in result:
        result = result[2:]
    return result

def norm_special(name: str):
    return base_norm_special(name, True)

def twitter_name(name: str):
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
        name = base_norm_variants(name, True, True)
        name = norm_special(name)
        name = twitter_name(name)
        path = f'{fontname}/images/{ppem}/{name}.png'
        if not os.path.exists(path):
            path = f'{fontname}-extra/images/{ppem}/{name}.png'
        with open(path, 'rb') as fin:
            glyph.imageData = fin.read()

print('Saving changes...')
ttf = ttf.replace('apple/', '')
f.save(f'{fontname}/{ttf}')
