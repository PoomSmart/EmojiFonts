import os
import sys

sys.path.append('..')
from shared import *
from shared_lig import *

# input: apple font ttf, oneui font ttf

ttf = sys.argv[1]
bttf = sys.argv[2]
f = ttLib.TTFont(ttf)

lig = Lig(f, bttf)
lig.build()

def image_paths_fn(ppem: int, name: str):
    return [f'images/{ppem}/{name}.png', f'extra/images/{ppem}/{native_norm_name(name)}.png']

prepare_strikes(f)
resolve = make_resolver(
    vendor_name_fn=lambda name: lig.get_glyph_name(lig.norm_name(name)),
    image_paths_fn=image_paths_fn,
)
process_strikes(f.get('sbix').strikes, resolve)

if not os.path.exists('../.test'):
    print('Saving changes...')
    ttf = ttf.replace('../apple/', '')
    f.save(ttf)
