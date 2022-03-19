# brew install freetype imagemagick
# pip3 install Wand
import sys
import io
import pathlib
from fontTools import ttLib
from wand.color import Color
from wand.image import Image
from PIL import Image as PImage

debug = False
extract = False
direct = True
fontname = 'twemoji'

# input: font ttf, assets folder

ttf = sys.argv[1]
assets = sys.argv[2]

f = ttLib.TTFont(ttf)

# and hairs
professions = [
    '1f33e', '1f373', '1f37c', '1f393', '1f3a4',
    '1f3a8', '1f3eb', '1f3ed', '1f4bb', '1f4bc',
    '1f527', '1f52c', '1f680', '1f692', '1f9af',
    '1f9b0', '1f9b1', '1f9b2', '1f9b3', '1f9bc',
    '1f9bd'
]
heart = '2764'
kiss = '1f48b'
modifiers = ['2695', '2696', '2708']
skins = {
    1: '1f3fb',
    2: '1f3fc',
    3: '1f3fd',
    4: '1f3fe',
    5: '1f3ff'
}

man, woman, neutral = '1f468', '1f469', '1f9d1'
boy, girl = '1f466', '1f467'
persons = {
    'm': man,
    'w': woman,
    'b': boy,
    'g': girl,
    '': ''
}

def m_print(str):
    if debug:
        print(str)

def svg_to_blob(svg_file, size):
    with Image(filename=svg_file, background=Color('transparent'), width=size, height=size, format='svg') as image:
        return image.make_blob('png')

def norm_joiner(name):
    if 'silhouette' in name:
        return name
    return name.replace('u', '').replace('_', '-').lower()

def norm_fam(name):
    if '1f46a.' not in name:
        return name
    for p1 in ['m', 'w', '']:
        for p2 in ['m', 'w']:
            for c1 in ['g', 'b', '']:
                for c2 in ['g', 'b']:
                    suffix = f'.{p1}{p2}{c1}{c2}'
                    if suffix in name:
                        seq = [persons[p1], persons[p2], persons[c1], persons[c2]]
                        return '-200d-'.join(list(filter(len, seq)))
    return name

def norm_dual(name):
    for s in range(1, 6):
        if name == f'{man}-1f91d-{man}.{s}{s}':
            return f'1f46c-{skins[s]}'
        if name == f'{woman}-1f91d-{man}.{s}{s}':
            return f'1f46b-{skins[s]}'
        if name == f'{woman}-1f91d-{woman}.{s}{s}':
            return f'1f46d-{skins[s]}'
    for s1 in range(1, 6):
        for s2 in range(1, 6):
            if name == f'{neutral}-1f91d-{neutral}.{s1}{s2}':
                return f'{neutral}-{skins[s1]}-200d-1f91d-200d-{neutral}-{skins[s2]}'
    if name == '1f9d1-1f91d-1f9d1.66':
        m_print(f'Fallback to default for {name}')
        return '1f9d1-200d-1f91d-200d-1f9d1'
    if '.l' in name or '.r' in name or 'silhouette.' in name:
        # FIXME: Create extra SVGs specific for Apple?
        m_print(f'Not modified: {name}')
        return None
    return name

def norm_variants(name):
    if '.m' in name:
        name = name.replace('.m', '')
    for s in range(1, 6):
        if f'.{s}.w' in name:
            name = name.replace(f'.{s}.w', f'-{skins[s]}-200d-2640-fe0f')
    if '.w' in name:
        if '26f9' in name or '1f3cb' in name or '1f3cc' in name or '1f575' in name:
            name = name.replace('.w', '-fe0f-200d-2640-fe0f')
        else:
            name = name.replace('.w', '-200d-2640-fe0f')
    for s in range(1, 6):
        for m in modifiers:
            if f'-{m}.{s}' in name:
                name = name.replace(f'-{m}.{s}', f'-{skins[s]}-200d-{m}-fe0f')
    for p in professions:
        for s in range(1, 6):
            if f'-{p}.{s}' in name:
                return name.replace(f'-{p}.{s}', f'-{skins[s]}-200d-{p}')
    if '.0' in name:
        name = name.replace('.0', '')
    for s in range(1, 6):
        if f'.{s}' in name:
            if '1f9d1-1f384' in name:
                return name.replace(f'-1f384.{s}', f'-{skins[s]}-200d-1f384')
            else:
                return name.replace(f'.{s}', f'-{skins[s]}')
    return name

def norm_special(name):
    if name == '2764-1f525':
        return '2764-fe0f-200d-1f525'
    if name == '2764-1fa79':
        return '2764-fe0f-200d-1fa79'
    if name == '1f3f3-26a7':
        return '1f3f3-fe0f-200d-26a7-fe0f'
    if name == '1f3f3-1f308':
        return '1f3f3-fe0f-200d-1f308'
    if name == '1f3f4-2620':
        return '1f3f4-200d-2620-fe0f'
    if name == '1f408-2b1b':
        return '1f408-200d-2b1b'
    if name == '1f415-1f9ba':
        return '1f415-200d-1f9ba'
    if name == '1f43b-2744':
        return '1f43b-200d-2744-fe0f'
    if name == '1f441-1f5e8':
        return '1f441-200d-1f5e8'
    if name == '1f62e-1f4a8':
        return '1f62e-200d-1f4a8'
    if name == '1f635-1f4ab':
        return '1f635-200d-1f4ab'
    if name == '1f636-1f32b':
        return '1f636-200d-1f32b-fe0f'
    if name == '1f9d1-1f384':
        return '1f9d1-200d-1f384'
    for m in modifiers:
        if name == f'1f9d1-{m}':
            return f'1f9d1-200d-{m}-fe0f'
    for p in professions:
        if name == f'1f9d1-{p}':
            return f'1f9d1-200d-{p}'
    for g in [man, woman]:
        for m in modifiers:
            if name == f'{g}-{m}':
                return f'{g}-200d-{m}-fe0f'
    for p in professions:
        for g in [man, woman]:
            if name == f'{g}-{p}':
                return f'{g}-200d-{p}'
    return name

whitelists = ['00a9', '00ae', 'hiddenglyph']

# remove some strikes to make font smaller
del f['sbix'].strikes[160]
del f['sbix'].strikes[52]
del f['sbix'].strikes[26]
print('Removed strikes 160, 52 and 26')

for ppem, strike in f['sbix'].strikes.items():
    print(f'Reading strike of size {ppem}x{ppem}')
    if not direct:
        pathlib.Path(f'twemoji/{ppem}').mkdir(parents=True, exist_ok=True) 
    for code, glyph in strike.glyphs.items():
        if glyph.graphicType != 'png ':
            continue
        name = norm_joiner(code)
        if '20e3' in name or name in whitelists:
            continue
        name = norm_fam(name)
        name = norm_dual(name)
        if name is None:
            continue
        name = norm_variants(name)
        name = norm_special(name)
        if direct:
            with PImage.open(f'{assets}/{name}.png') as fin:
                img = fin.resize((ppem, ppem), PImage.ANTIALIAS)
                stream = io.BytesIO()
                img.save(stream, format='png')
                glyph.imageData = stream.getvalue()
                stream.close()
        else:
            svg = svg_to_blob(f'{assets}/svg/{name}.svg', ppem)
            if extract:
                with open(f'{fontname}/{ppem}/{name}.png', 'wb') as fout:
                    fout.write(svg)
            glyph.imageData = svg

f.save(f'{fontname}/{ttf}')
