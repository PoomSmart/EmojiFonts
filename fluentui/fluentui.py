import os
import sys

sys.path.append('..')
from shared import *

# input: font ttf, emoji style

ttf = sys.argv[1]
style = sys.argv[2]

f = ttLib.TTFont(ttf)

def fluentui_name(name: str):
    if name.endswith('_20e3'):
        name = name.replace('_20e3', '_fe0f_20e3')
    return name.replace('_', '-')

def extra_whitelist_fn(name: str):
    return '.l' in name or '.r' in name or 'silhouette.' in name

def pre_norm_filter_fn(name: str):
    # FIXME: flags, hairs and standalone skins not available
    if is_flag(name) or name in hairs or name in skins.values():
        m_print(f'{name} is missing')
        return None
    return name

def norm_special_fn(name: str):
    if name == '1f441_1f5e8':
        return '1f441_fe0f_200d_1f5e8_fe0f'
    return norm_variant_selector(base_norm_special(name, True))

def image_paths_fn(ppem: int, name: str):
    return [f'{style}/images/{ppem}/{name}.png']

prepare_strikes(f, True)
resolve = make_resolver(
    extra_whitelist_fn=extra_whitelist_fn,
    pre_norm_filter_fn=pre_norm_filter_fn,
    # FIXME: multi emojis not available
    skip_if_multi=True,
    with_variant_selector=True,
    gender_need_selector=True,
    norm_special_fn=norm_special_fn,
    vendor_name_fn=fluentui_name,
    image_paths_fn=image_paths_fn,
)
process_strikes(f['sbix'].strikes, resolve)

if not os.path.exists('../.test'):
    print('Saving changes...')
    ttf = ttf.replace('../apple/', '')
    f.save(f'{style}-{ttf}')
