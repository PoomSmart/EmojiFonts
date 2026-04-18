import os
import sys

sys.path.append('..')
from shared import *

# input: font ttf

ttf = sys.argv[1]

f = ttLib.TTFont(ttf)

def norm_name(name: str):
    result = base_norm_name(name)
    if '20e3' in result:
        result = result.replace('_20e3', '_fe0f_20e3')
    return result

def norm_special(name: str):
    if name == '1f441_1f5e8':
        return '1f441_fe0f_200d_1f5e8_fe0f'
    return base_norm_special(name, True)

def openmoji_name(name: str):
    return name.replace('_', '-').upper()

def image_paths_fn(ppem: int, name: str):
    if name.lower().startswith('silhouette'):
        fallback = name.lower()
    else:
        fallback = name.replace('.L', '.l').replace('.R', '.r')
    return [f'images/{ppem}/{name}.png', f'extra/images/{ppem}/{fallback}.png']

prepare_strikes(f, True)
resolve = make_resolver(
    norm_name_fn=norm_name,
    with_variant_selector=True,
    gender_need_selector=True,
    norm_special_fn=norm_special,
    vendor_name_fn=openmoji_name,
    image_paths_fn=image_paths_fn,
)
process_strikes(f['sbix'].strikes, resolve)

if not os.path.exists('../.test'):
    print('Saving changes...')
    ttf = ttf.replace('../apple/', '')
    f.save(ttf)
