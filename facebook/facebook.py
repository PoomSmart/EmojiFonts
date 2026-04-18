import sys
import os

sys.path.append('..')
from shared import *

# input: font ttf

ttf = sys.argv[1]

f = ttLib.TTFont(ttf)

def norm_name(name: str):
    name = base_norm_name(name)
    if '20e3' in name or name in signs:
        name = name[2:]
    return name

def facebook_name(name: str):
    return name.replace('_', '-')

def image_paths_fn(ppem: int, name: str):
    underscored = name.replace('-', '_')
    if name.startswith('1f491') or name.startswith('1f48f'):
        return [f'extra/images/{ppem}/{name}.png', f'extra/images/{ppem}/{underscored}.png']
    return [
        f'images/{ppem}/{name}.png',
        f'extra/images/{ppem}/{name}.png',
        f'extra/images/{ppem}/{underscored}.png',
    ]

prepare_strikes(f)
resolve = make_resolver(
    norm_name_fn=norm_name,
    vendor_name_fn=facebook_name,
    image_paths_fn=image_paths_fn,
)
process_strikes(f['sbix'].strikes, resolve)

if not os.path.exists('../.test'):
    print('Saving changes...')
    ttf = ttf.replace('../apple/', '')
    f.save(ttf)
