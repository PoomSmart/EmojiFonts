import os
import sys
import io
from fontTools import ttLib
from PIL import Image as PImage
from shared import *

fontname = 'noto-emoji'

# input: font ttf

ttf = sys.argv[1]

f = ttLib.TTFont(ttf)

def norm_flag(name: str):
    tokens = name.split('_')
    if tokens[0] == '1f3f4':
        tokens = tokens[1:]
    n = ''
    for t in tokens:
        h = int(t, 16)
        if h > 0xe0000:
            n += chr(h - 0xe0061 + 65)
        else:
            n += chr(h - 0x1f1e6 + 65)
    if len(n) > 2:
        n = n[:-1]
        n = f'{n[:2]}-{n[2:]}'
    return n

def noto_name(name, with_prefix):
    tokens = name.split('_')
    n = []
    for t in tokens:
        if t[0] == 'u':
            t = t[1:] # strip u prefix
        n.append(t)
    result = '_'.join(n)
    return 'u' + result if with_prefix else result

prepare_strikes(f)
for ppem, strike in f['sbix'].strikes.items():
    print(f'Reading strike of size {ppem}x{ppem}')
    for name, glyph in strike.glyphs.items():
        if glyph.graphicType != 'png ':
            continue
        name = base_norm_name(name)
        if base_is_whitelist(name):
            continue
        flag = is_flag(name)
        if flag:
            name = norm_flag(name)
        else:
            name = norm_fam(name)
            name = norm_dual(name)
            if name is None:
                continue
            name = base_norm_variants(name)
            name = base_norm_special(name)
        name = noto_name(name, not flag)
        path = f'{fontname}/images/{ppem}/{name}.png' if flag else f'{fontname}/images/{ppem}/emoji_{name}.png'
        if not os.path.exists(path):
            name = name[1:] if name[0] == 'u' else name
            path = f'{fontname}-extra/images/{ppem}/{name}.png'
        with PImage.open(path) as fin:
            stream = io.BytesIO()
            fin.save(stream, format='png')
            glyph.imageData = stream.getvalue()
            stream.close()

print('Saving changes...')
ttf = ttf.replace('apple/', '')
f.save(f'{fontname}/{ttf}')
