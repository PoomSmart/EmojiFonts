import os
import sys

sys.path.append('..')
from shared import *

# input: font ttf

ttf = sys.argv[1]

f = ttLib.TTFont(ttf)

def noto_name(name: str):
    tokens = name.split('_')
    n = []
    for t in tokens:
        if t[0] == 'u':
            t = t[1:] # strip u prefix
        n.append(t)
    result = '_'.join(n)
    return 'u' + result

def image_paths_fn(ppem: int, name: str):
    no_u = name[1:] if name.startswith('u') else name
    return [f'images/{ppem}/emoji_{name}.png', f'extra/images/{ppem}/{no_u}.png']

prepare_strikes(f, True)
resolve = make_resolver(vendor_name_fn=noto_name, image_paths_fn=image_paths_fn)
process_strikes(f['sbix'].strikes, resolve)

if not os.path.exists('../.test'):
    print('Saving changes...')
    ttf = ttf.replace('../apple/', '')
    f.save(ttf)
