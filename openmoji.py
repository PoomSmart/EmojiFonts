# import os
import sys
import io
from fontTools import ttLib
from PIL import Image as PImage
from shared import *

fontname = 'openmoji'

# input: font ttf

ttf = sys.argv[1]

f = ttLib.TTFont(ttf)

def norm_name(name):
    result = base_norm_name(name)
    if '20e3' in result:
        result = result.replace('_20e3', '_fe0f_20e3')
    return result

def norm_special(name):
    if name == '1f441_1f5e8':
        return '1f441_fe0f_200d_1f5e8_fe0f'
    return base_norm_special(name, True)

def openmoji_name(name):
    return name.replace('_', '-').upper()

for ppem, strike in f['sbix'].strikes.items():
    print(f'Reading strike of size {ppem}x{ppem}')
    for name, glyph in strike.glyphs.items():
        if glyph.graphicType != 'png ':
            continue
        name = norm_name(name)
        if base_is_whitelist(name):
            continue
        if '.l' in name or '.r' in name or 'silhouette' in name:
            m_print(f'{name} is missing')
            continue
        name = norm_fam(name)
        name = norm_dual(name)
        if name is None:
            continue
        name = base_norm_variants(name, True, True)
        name = norm_special(name)
        name = openmoji_name(name)
        path = f'{fontname}/images/{ppem}/{name}.png'
        # if not os.path.exists(path):
        #     path = f'{fontname}-extra/{name}.png'
        with PImage.open(path) as fin:
            img = fin.resize((ppem, ppem), PImage.Resampling.BICUBIC)
            stream = io.BytesIO()
            img.save(stream, format='png')
            glyph.imageData = stream.getvalue()
            stream.close()

print('Saving changes...')
ttf = ttf.replace('common/', '')
f.save(f'{fontname}/{ttf}')
