import os
import sys
import io
import xml.etree.ElementTree as ET
from fontTools import ttLib
from PIL import Image as PImage
from shared import *

fontname = 'whatsapp'

# input: apple font ttf, whatsapp font ttf, blobemoji GSUB ttx

ttf = sys.argv[1]
bttf = sys.argv[2]
bgsubttx = sys.argv[3]

name_map = {
    'u0023': 'numbersign',
    'u002A': 'asterisk',
    'u0030': 'zero',
    'u0031': 'one',
    'u0032': 'two',
    'u0033': 'three',
    'u0034': 'four',
    'u0035': 'five',
    'u0036': 'six',
    'u0037': 'seven',
    'u0038': 'eight',
    'u0039': 'nine',
}

f = ttLib.TTFont(ttf)
b = ttLib.TTFont(bttf)
bgsub = ET.parse(bgsubttx).getroot()
blig = {}

icmap = f.get('cmap').buildReversed()
cmap = f.get('cmap').tables[0].cmap
bicmap = b.get('cmap').buildReversed()
bcmap = b.get('cmap').tables[1].cmap

def get_apple_code(code: str):
    code = next(iter(bicmap[code]))
    if code == 0x200D:
        return 'u200D'
    if code in cmap:
        code = cmap[code]
    code = str(code)
    code = code.replace('.0', '')
    return code

print('Building ligatures...')
bicmap_apple = {}
for key in bicmap:
    bicmap_apple[get_apple_code(key)] = bicmap[key]

for lookup in bgsub.iter('Lookup'):
    lookup_type = lookup.find('LookupType').get('value')
    if lookup_type != '4':
        continue
    for ligset in lookup.iter('LigatureSet'):
        glyph = get_apple_code(ligset.get('glyph'))
        for lig in ligset.iter('Ligature'):
            components = str(lig.get('components'))
            tokens = components.split(',')
            s = []
            for t in tokens:
                s.append(get_apple_code(t))
            remaining = '_'.join(s)
            name = f'{glyph}_{remaining}'
            real_glyph = lig.get('glyph')
            blig[name] = real_glyph

def norm_name(name: str):
    name = name.upper()
    tokens = name.split('_')
    s = []
    for t in tokens:
        t = f'uni{t}' if t in genders else f'u{t}'
        s.append(t)
    if s[0] in name_map:
        s[0] = name_map[s[0]]
    return '_'.join(s)

def get_glyph_name(name: str):
    if name in icmap:
        code = next(iter(icmap[name]))
        return bcmap[code]
    if name in bicmap_apple:
        code = next(iter(bicmap_apple[name]))
        return bcmap[code]
    if name in blig:
        return blig[name]
    return name

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
        o_name = name
        name = norm_name(name)
        name = get_glyph_name(name)
        path = f'{fontname}/images/{ppem}/{name}.png'
        if not os.path.exists(path) or o_name.startswith('1f491') or o_name.startswith('1f48f'):
            name = native_norm_name(o_name)
            path = f'{fontname}-extra/images/{ppem}/{name}.png'
            if not os.path.exists(path):
                name = name.replace('_', '-')
                path = f'{fontname}-extra/images/{ppem}/{name}.png'
        with PImage.open(path) as fin:
            stream = io.BytesIO()
            fin.save(stream, format='png')
            glyph.imageData = stream.getvalue()
            stream.close()

print('Saving changes...')
ttf = ttf.replace('common/', '')
f.save(f'{fontname}/{ttf}')
