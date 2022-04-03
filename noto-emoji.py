import os
import sys
import io
from fontTools import ttLib
from PIL import Image
from shared import *

fontname = 'noto-emoji'

# input: font ttf, emoji assets folder, flag assets folder

ttf = sys.argv[1]
assets = sys.argv[2]
flag_assets = sys.argv[3]

f = ttLib.TTFont(ttf)

flags = [
    '1f1e6', '1f1e7', '1f1e8', '1f1e9', '1f1ea',
    '1f1eb', '1f1ec', '1f1ed', '1f1ee', '1f1ef',
    '1f1f0', '1f1f1', '1f1f2', '1f1f3', '1f1f4',
    '1f1f5', '1f1f6', '1f1f7', '1f1f8', '1f1f9',
    '1f1fa', '1f1fb', '1f1fc', '1f1fd', '1f1fe',
    '1f1ff',
    '1f3f4_e0067'
]

def is_flag(name):
    for f in flags:
        if f in name:
            return True
    return False

def norm_flag(name):
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
        path = f'{flag_assets}/{name}.png' if flag else f'{assets}/emoji_{name}.png'
        if not os.path.exists(path):
            name = name[1:] if name[0] == 'u' else name
            path = f'{fontname}-extra/{name}.png'
        with Image.open(path) as fin:
            if flag:
                # TODO: Vertically center the images?
                fin.thumbnail((ppem, ppem), Image.ANTIALIAS)
            else:
                fin = fin.resize((ppem, ppem), Image.ANTIALIAS)
            stream = io.BytesIO()
            fin.save(stream, format='png')
            glyph.imageData = stream.getvalue()
            stream.close()

print('Saving changes...')
ttf = ttf.replace('common/', '')
f.save(f'{fontname}/{ttf}')