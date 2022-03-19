import sys
import io
from fontTools import ttLib
from PIL import Image

debug = False
fontname = 'noto-emoji'

# input: font ttf, emoji assets folder, flag assets folder

ttf = sys.argv[1]
assets = sys.argv[2]
flag_assets = sys.argv[3]

f = ttLib.TTFont(ttf)

def m_print(str):
    if debug:
        print(str)


# remove some strikes to make font smaller
del f['sbix'].strikes[160]
del f['sbix'].strikes[52]
del f['sbix'].strikes[26]
print('Removed strikes 160, 52 and 26')

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
flags = [
    '1f1e6', '1f1e7', '1f1e8', '1f1e9', '1f1ea',
    '1f1eb', '1f1ec', '1f1ed', '1f1ee', '1f1ef',
    '1f1f0', '1f1f1', '1f1f2', '1f1f3', '1f1f4',
    '1f1f5', '1f1f6', '1f1f7', '1f1f8', '1f1f9',
    '1f1fa', '1f1fb', '1f1fc', '1f1fd', '1f1fe',
    '1f1ff',
    '1f3f4_ue0067'
]

man, woman, neutral = '1f468', '1f469', '1f9d1'
boy, girl = '1f466', '1f467'
persons = {
    'm': man,
    'w': woman,
    'b': boy,
    'g': girl,
    '': ''
}

def is_flag(name):
    for f in flags:
        if f in name:
            return True
    return False

def norm_name(name):
    return name.lower()

def norm_flag(name):
    tokens = name.split('_')
    if tokens[0] == 'u1f3f4':
        tokens = tokens[1:]
    n = ''
    for t in tokens:
        h = int(t[1:], 16)
        if h > 0xe0000:
            n += chr(h - 0xe0061 + 65)
        else:
            n += chr(h - 0x1f1e6 + 65)
    if len(n) > 2:
        n = n[:-1]
        n = f'{n[:2]}-{n[2:]}'
    return n

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
                        return f"u{'_200d_'.join(list(filter(len, seq)))}"
    return name

def norm_dual(name):
    for s in range(1, 6):
        if name == f'u{man}_u1f91d_u{man}.{s}{s}':
            return f'u1f46c_{skins[s]}'
        if name == f'u{woman}_u1f91d_u{man}.{s}{s}':
            return f'u1f46b_{skins[s]}'
        if name == f'u{woman}_u1f91d_u{woman}.{s}{s}':
            return f'u1f46d_{skins[s]}'
    for s1 in range(1, 6):
        for s2 in range(1, 6):
            if name == f'u{neutral}_u1f91d_u{neutral}.{s1}{s2}':
                return f'u{neutral}_{skins[s1]}_200d_1f91d_200d_{neutral}_{skins[s2]}'
    if name == 'u1f9d1_u1f91d_u1f9d1.66':
        m_print(f'Fallback to default for {name}')
        return 'u1f9d1_200d_1f91d_200d_1f9d1'
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
            name = name.replace(f'.{s}.w', f'_{skins[s]}_200d_2640')
    if '.w' in name:
        name = name.replace('.w', '_200d_2640')
    for s in range(1, 6):
        for m in modifiers:
            if f'_u{m}.{s}' in name:
                name = name.replace(f'_u{m}.{s}', f'_{skins[s]}_200d_{m}')
    for p in professions:
        for s in range(1, 6):
            if f'_u{p}.{s}' in name:
                return name.replace(f'_u{p}.{s}', f'_{skins[s]}_200d_{p}')
    if '.0' in name:
        name = name.replace('.0', '')
    for s in range(1, 6):
        if f'.{s}' in name:
            if 'u1f9d1_u1f384' in name:
                return name.replace(f'_u1f384.{s}', f'_{skins[s]}_200d_1f384')
            else:
                return name.replace(f'.{s}', f'_{skins[s]}')
    return name

def norm_special(name):
    if name == 'u2764_u1f525':
        return 'u2764_200d_1f525'
    if name == 'u2764_u1fa79':
        return 'u2764_200d_1fa79'
    if name == 'u1f3f3_u26a7':
        return 'u1f3f3_200d_26a7'
    if name == 'u1f3f3_u1f308':
        return 'u1f3f3_200d_1f308'
    if name == 'u1f3f4_u2620':
        return 'u1f3f4_200d_2620'
    if name == 'u1f408_u2b1b':
        return 'u1f408_200d_2b1b'
    if name == 'u1f415_u1f9ba':
        return 'u1f415_200d_1f9ba'
    if name == 'u1f43b_u2744':
        return 'u1f43b_200d_2744'
    if name == 'u1f441_u1f5e8':
        return 'u1f441_200d_1f5e8'
    if name == 'u1f62e_u1f4a8':
        return 'u1f62e_200d_1f4a8'
    if name == 'u1f635_u1f4ab':
        return 'u1f635_200d_1f4ab'
    if name == 'u1f636_u1f32b':
        return 'u1f636_200d_1f32b'
    if name == 'u1f9d1_u1f384':
        return 'u1f9d1_200d_1f384'
    for m in modifiers:
        if name == f'u1f9d1_u{m}':
            return f'u1f9d1_200d_{m}'
    for p in professions:
        if name == f'u1f9d1_u{p}':
            return f'u1f9d1_200d_{p}'
    for g in [man, woman]:
        for m in modifiers:
            if name == f'u{g}_u{m}':
                return f'u{g}_200d_{m}'
    for p in professions:
        for g in [man, woman]:
            if name == f'u{g}_u{p}':
                return f'u{g}_200d_{p}'
    return name

for ppem, strike in f['sbix'].strikes.items():
    print(f'Reading strike of size {ppem}x{ppem}')
    for code, glyph in strike.glyphs.items():
        if glyph.graphicType != 'png ':
            continue
        name = norm_name(code)
        if name == 'hiddenglyph' or '20e3' in name:
            continue
        flag = is_flag(name)
        if flag:
            name = norm_flag(name)
        else:
            name = norm_fam(name)
            name = norm_dual(name)
            if name is None:
                continue
            name = norm_variants(name)
            name = norm_special(name)
        path = f'{flag_assets}/{name}.png' if flag else f'{assets}/emoji_{name}.png'
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

f.save(f'{fontname}/{ttf}')