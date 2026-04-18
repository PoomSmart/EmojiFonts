import io
import os
import sys
import threading
from PIL import Image

sys.path.append('..')
from shared import *

# input: font ttf

ttf = sys.argv[1]

f = ttLib.TTFont(ttf)

_tls = threading.local()

def post_special_filter_fn(name: str):
    _tls.flip = name.endswith('_200d_27a1')
    if _tls.flip:
        return name[:-len('_200d_27a1')]
    return name

def image_paths_fn(ppem: int, name: str):
    no_u = name[1:] if name.startswith('u') else name
    return [f'images/{ppem}/emoji_{name}.png', f'extra/images/{ppem}/{no_u}.png']

def post_process_fn(data: bytes):
    if not getattr(_tls, 'flip', False):
        return data
    img = Image.open(io.BytesIO(data)).transpose(Image.FLIP_LEFT_RIGHT)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return buf.getvalue()

prepare_strikes(f, True)
resolve = make_resolver(
    post_special_filter_fn=post_special_filter_fn,
    vendor_name_fn=noto_style_name,
    image_paths_fn=image_paths_fn,
    post_process_fn=post_process_fn,
)
process_strikes(f['sbix'].strikes, resolve)

if not os.path.exists('../.test'):
    print('Saving changes...')
    ttf = ttf.replace('../apple/', '')
    f.save(ttf)
