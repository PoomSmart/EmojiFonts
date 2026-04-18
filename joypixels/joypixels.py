import sys
import os

sys.path.append('..')
from shared import *

# input: font ttf, emoji style

ttf = sys.argv[1]
style = sys.argv[2]

f = ttLib.TTFont(ttf)

def joypixels_name(name: str):
    tokens = name.split('_')
    n = []
    remove = ['fe0f', '200d']
    for token in tokens:
        if token in remove:
            continue
        n.append(token)
    return '-'.join(n)

def image_paths_fn(ppem: int, name: str):
    underscored = name.replace('-', '_')
    return [f'{style}/images/{ppem}/{name}.png', f'extra/images/{ppem}/{underscored}.png']

prepare_strikes(f)
resolve = make_resolver(
    with_variant_selector=True,
    gender_need_selector=True,
    vendor_name_fn=joypixels_name,
    image_paths_fn=image_paths_fn,
)
process_strikes(f['sbix'].strikes, resolve)

if not os.path.exists('../.test'):
    print('Saving changes...')
    ttf = ttf.replace('../apple/', '')
    f.save(f'{style}-{ttf}')
