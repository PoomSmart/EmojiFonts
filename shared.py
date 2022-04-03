from wand.color import Color
from wand.image import Image

debug = False

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

flags = [
    '1f1e6', '1f1e7', '1f1e8', '1f1e9', '1f1ea',
    '1f1eb', '1f1ec', '1f1ed', '1f1ee', '1f1ef',
    '1f1f0', '1f1f1', '1f1f2', '1f1f3', '1f1f4',
    '1f1f5', '1f1f6', '1f1f7', '1f1f8', '1f1f9',
    '1f1fa', '1f1fb', '1f1fc', '1f1fd', '1f1fe',
    '1f1ff',
    '1f3f4_e0067'
]

u14 = [
    '1f62e_1f4a8',
    '1f635_1f4ab',
    '1f636_1f32b',
    '1f6dd',
    '1f6de',
    '1f6df',
    '1f7f0',
    '1f979',
    '1f9cc',
    '1f9d4.0.w',
    '1f9d4.1.w',
    '1f9d4.2.w',
    '1f9d4.3.w',
    '1f9d4.4.w',
    '1f9d4.5.w',
    '1fa7b',
    '1fa7c',
    '1faa9',
    '1faaa',
    '1faab',
    '1faac',
    '1fab7',
    '1fab8',
    '1fab9',
    '1faba',
    '1fad7',
    '1fad8',
    '1fad9',
    '1fae0',
    '1fae1',
    '1fae2',
    '1fae3',
    '1fae4',
    '1fae5',
    '1fae6',
    '1fae7'
]

whitelists = ['00a9', '00ae', 'hiddenglyph']

def m_print(str):
    if debug:
        print(str)

def is_flag(name):
    for f in flags:
        if f in name:
            return True
    return False

def base_is_whitelist(name):
    return name in whitelists

def base_norm_name(name):
    if len(name) == 13 and 'silhouette.' in name:
        return name
    tokens = name.replace('.u', '_').split('_')
    n = []
    for t in tokens:
        if t[0] == 'u':
            t = t[1:] # strip u prefix
        n.append(t)
    return '_'.join(n).lower()

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
                        return '_200d_'.join(list(filter(len, seq)))
    return name

def norm_dual(name):
    for s in range(1, 6):
        if name == f'{man}_1f91d_{man}.{s}{s}':
            return f'1f46c_{skins[s]}'
        if name == f'{woman}_1f91d_{man}.{s}{s}':
            return f'1f46b_{skins[s]}'
        if name == f'{woman}_1f91d_{woman}.{s}{s}':
            return f'1f46d_{skins[s]}'
    for s1 in range(1, 6):
        for s2 in range(1, 6):
            if name == f'{neutral}_1f91d_{neutral}.{s1}{s2}':
                return f'{neutral}_{skins[s1]}_200d_1f91d_200d_{neutral}_{skins[s2]}'
    if name == '1f9d1_1f91d_1f9d1.66':
        m_print(f'Fallback to default for {name}')
        return '1f9d1_200d_1f91d_200d_1f9d1'
    if '.ra' in name:
        name = name.replace('.ra', '.r')
    return name

gender_with_selector = [
    '26f9', '1f3cb', '1f3cc', '1f3fb', '1f575'
]

def base_norm_variants(name, with_variant_selector = False, with_condition = False):
    v = '_fe0f' if with_variant_selector else ''
    if '.m' in name:
        name = name.replace('.m', '')
    for s in range(1, 6):
        if f'.{s}.w' in name:
            name = name.replace(f'.{s}.w', f'_{skins[s]}_200d_2640{v}')
    if '.w' in name:
        found = False
        if with_condition:
            for x in gender_with_selector:
                if x in name:
                    found = True
                    name = name.replace('.w', f'_fe0f_200d_2640{v}')
                    break
        if not found:
            name = name.replace('.w', f'_200d_2640{v}')
    for s in range(1, 6):
        for m in modifiers:
            if f'_{m}.{s}' in name:
                name = name.replace(f'_{m}.{s}', f'_{skins[s]}_200d_{m}{v}')
    for p in professions:
        for s in range(1, 6):
            if f'_{p}.{s}' in name:
                return name.replace(f'_{p}.{s}', f'_{skins[s]}_200d_{p}')
    if '.0' in name:
        name = name.replace('.0', '')
    for s in range(1, 6):
        if f'.{s}' in name:
            if '1f9d1_1f384' in name:
                return name.replace(f'_1f384.{s}', f'_{skins[s]}_200d_1f384')
            else:
                return name.replace(f'.{s}', f'_{skins[s]}')
    return name

def base_norm_special(name, with_variant_selector = False):
    v = '_fe0f' if with_variant_selector else ''
    if name == '2764_1f525':
        return f'2764{v}_200d_1f525'
    if name == '2764_1fa79':
        return f'2764{v}_200d_1fa79'
    if name == '1f3f3_26a7':
        return f'1f3f3{v}_200d_26a7{v}'
    if name == '1f3f3_1f308':
        return f'1f3f3{v}_200d_1f308'
    if name == '1f3f4_2620':
        return f'1f3f4_200d_2620{v}'
    if name == '1f43b_2744':
        return f'1f43b_200d_2744{v}'
    if name == '1f636_1f32b':
        return f'1f636_200d_1f32b{v}'
    if name == '1f408_2b1b':
        return '1f408_200d_2b1b'
    if name == '1f415_1f9ba':
        return '1f415_200d_1f9ba'
    if name == '1f441_1f5e8':
        return '1f441_200d_1f5e8'
    if name == '1f62e_1f4a8':
        return '1f62e_200d_1f4a8'
    if name == '1f635_1f4ab':
        return '1f635_200d_1f4ab'
    if name == '1f9d1_1f384':
        return '1f9d1_200d_1f384'
    for g in [man, woman, neutral]:
        for m in modifiers:
            if name == f'{g}_{m}':
                return f'{g}_200d_{m}{v}'
        for p in professions:
            if name == f'{g}_{p}':
                return f'{g}_200d_{p}'
    return name

def svg_to_blob(svg_file, size):
    with Image(filename=svg_file, background=Color('transparent'), width=size, height=size, format='svg') as image:
        return image.make_blob('png')