import os
import sys

sys.path.append('..')
from shared import *
from shared_lig import *

# input: apple font ttf, oneui font ttf, oneui GSUB ttx

ttf = sys.argv[1]
bttf = sys.argv[2]
bgsubttx = sys.argv[3]

f = ttLib.TTFont(ttf)

lig = Lig(f, bttf, bgsubttx)
lig.build()

prepare_strikes(f)
for ppem, strike in f.get('sbix').strikes.items():
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
        name = lig.norm_name(name)
        name = lig.get_glyph_name(name)
        path = f'images/{ppem}/{name}.png'
        if not os.path.exists(path):
            name = native_norm_name(name)
            path = f'extra/images/{ppem}/{name}.png'
        glyph.imageData = get_image_data(path)

if not os.path.exists('../.test'):
    print('Saving changes...')
    ttf = ttf.replace('../apple/', '')
    f.save(ttf)
