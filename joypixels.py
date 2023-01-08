import sys
import io
import os
from fontTools import ttLib
from PIL import Image as PImage
from shared import *

fontname = 'joypixels'

# input: font ttf

ttf = sys.argv[1]

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
        path = f'{fontname}/{ppem}/{name}.png'
        if not os.path.exists(path):
            name = name.replace('-', '_')
            path = f'{fontname}-extra/images/{ppem}/{name}.png'
        with PImage.open(path) as fin:
            stream = io.BytesIO()
            fin.save(stream, format='png')
            glyph.imageData = stream.getvalue()
            stream.close()

print('Saving changes...')
ttf = ttf.replace('common/', '')
f.save(f'{fontname}/{ttf}')
