import sys
import io
from fontTools import ttLib
from PIL import Image as PImage
from shared import *

fontname = 'fluentui'

# input: font ttf, emoji style

ttf = sys.argv[1]
style = sys.argv[2]

f = ttLib.TTFont(ttf)

missing = [
    '1f3ae',
    '1f468_200d_1f4bb',
    '1f468_1f3fb_200d_1f4bb',
    '1f468_1f3fc_200d_1f4bb',
    '1f468_1f3fd_200d_1f4bb',
    '1f468_1f3fe_200d_1f4bb',
    '1f468_1f3ff_200d_1f4bb',
    '1f469_200d_1f4bb',
    '1f469_1f3fb_200d_1f4bb',
    '1f469_1f3fc_200d_1f4bb',
    '1f469_1f3fd_200d_1f4bb',
    '1f469_1f3fe_200d_1f4bb',
    '1f469_1f3ff_200d_1f4bb',
    '1f46a',
    '1f46b',
    '1f46c',
    '1f46d',
    '1f48f',
    '1f48f_1f3fb',
    '1f48f_1f3fc',
    '1f48f_1f3fd',
    '1f48f_1f3fe',
    '1f48f_1f3ff',
    '1f491',
    '1f491_1f3fb',
    '1f491_1f3fc',
    '1f491_1f3fd',
    '1f491_1f3fe',
    '1f491_1f3ff',
    '1f4ce',
    '1f91d_1f3fb',
    '1f91d_1f3fc',
    '1f91d_1f3fd',
    '1f91d_1f3fe',
    '1f91d_1f3ff',
    '1f9d1_200d_1f4bb',
    '1f9d1_1f3fb_200d_1f4bb',
    '1f9d1_1f3fc_200d_1f4bb',
    '1f9d1_1f3fd_200d_1f4bb',
    '1f9d1_1f3fe_200d_1f4bb',
    '1f9d1_1f3ff_200d_1f4bb',
]

def norm_special(name):
    if name == '1f441_1f5e8':
        return '1f441_fe0f_200d_1f5e8_fe0f'
    return base_norm_special(name, True)

def is_whitelist(name):
    return base_is_whitelist(name) or '.l' in name or '.r' in name or 'silhouette.' in name

def fluentui_name(name):
    if name.endswith('_20e3'):
        name = name.replace('_20e3', '_fe0f_20e3')
    return name.replace('_', '-')

for ppem, strike in f['sbix'].strikes.items():
    print(f'Reading strike of size {ppem}x{ppem}')
    for name, glyph in strike.glyphs.items():
        if glyph.graphicType != 'png ':
            continue
        name = base_norm_name(name)
        if is_whitelist(name):
            continue
        # FIXME: flags, hairs and standalone skins not available
        if is_flag(name) or name in hairs or name in skins.values():
            m_print(f'{name} is missing')
            continue
        o_name = name
        name = norm_fam(name)
        name = norm_dual(name)
        if name is None:
            continue
        # FIXME: multi emojis not available
        if name != o_name:
            m_print(f'{name} is missing')
            continue
        name = base_norm_variants(name, True, True)
        name = norm_special(name)
        name = norm_variant_selector(name)
        # FIXME: some emojis not available
        if name in missing:
            m_print(f'{name} is missing')
            continue
        name = fluentui_name(name)
        path = f'{fontname}/{style}/{ppem}/{name}.png'
        with PImage.open(path) as fin:
            stream = io.BytesIO()
            fin.save(stream, format='png')
            glyph.imageData = stream.getvalue()
            stream.close()

print('Saving changes...')
ttf = ttf.replace('common/', '')
f.save(f'{fontname}/{style}-{ttf}')