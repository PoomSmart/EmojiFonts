import sys
import io
from fontTools import ttLib
from PIL import Image as PImage
from shared import *

fontname = 'joypixels'

# input: font ttf, emoji assets folder

ttf = sys.argv[1]
assets = sys.argv[2]

f = ttLib.TTFont(ttf)

def is_whitelist(name):
    return base_is_whitelist(name) or '.l' in name or '.r' in name or 'silhouette.' in name

def joypixels_name(name,):
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
        if is_whitelist(name):
            continue
        name = norm_fam(name)
        name = norm_dual(name)
        if name is None:
            continue
        name = base_norm_variants(name, True, True)
        name = base_norm_special(name, True)
        name = joypixels_name(name)
        path = f'{assets}/{name}.png'
        with PImage.open(path) as fin:
            img = fin.resize((ppem, ppem), PImage.Resampling.BICUBIC)
            stream = io.BytesIO()
            img.save(stream, format='png')
            glyph.imageData = stream.getvalue()
            stream.close()

print('Saving changes...')
ttf = ttf.replace('common/', '')
f.save(f'{fontname}/{ttf}')
