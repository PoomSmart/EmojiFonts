import os
import sys

sys.path.append('..')
from shared import *

# input: font ttf

ttf = sys.argv[1]

f = ttLib.TTFont(ttf)

def norm_name(name: str):
    result = base_norm_name(name)
    if '20e3' in result or result in signs:
        result = result[2:]
    return result

def twitter_name(name: str):
    return name.replace('_', '-')

def image_paths_fn(ppem: int, name: str):
    return [f'images/{ppem}/{name}.png', f'extra/images/{ppem}/{name}.png']

prepare_strikes(f, True)
resolve = make_resolver(
    norm_name_fn=norm_name,
    with_variant_selector=True,
    gender_need_selector=True,
    vendor_name_fn=twitter_name,
    image_paths_fn=image_paths_fn,
)
process_strikes(f['sbix'].strikes, resolve)

if not os.path.exists('../.test'):
    print('Saving changes...')
    ttf = ttf.replace('../apple/', '')
    f.save(ttf)
