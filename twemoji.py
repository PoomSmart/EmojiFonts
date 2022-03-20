# brew install freetype imagemagick
# pip3 install Wand
import sys
import io
import pathlib
from fontTools import ttLib
from wand.color import Color
from wand.image import Image
from PIL import Image as PImage
from shared import *

debug = False
extract = False
direct = True
fontname = 'twemoji'

# input: font ttf, assets folder

ttf = sys.argv[1]
assets = sys.argv[2]

f = ttLib.TTFont(ttf)

def svg_to_blob(svg_file, size):
    with Image(filename=svg_file, background=Color('transparent'), width=size, height=size, format='svg') as image:
        return image.make_blob('png')

def norm_special(name):
    return base_norm_special(name, True)

def twitter_name(name):
    return name.replace('_', '-')

remove_strikes(f)

for ppem, strike in f['sbix'].strikes.items():
    print(f'Reading strike of size {ppem}x{ppem}')
    if not direct:
        pathlib.Path(f'twemoji/{ppem}').mkdir(parents=True, exist_ok=True) 
    for name, glyph in strike.glyphs.items():
        if glyph.graphicType != 'png ':
            continue
        name = norm_name(name)
        if base_is_whitelist(name):
            continue
        name = norm_fam(name)
        name = norm_dual(name)
        if name is None:
            continue
        name = base_norm_variants(name, True, True)
        name = norm_special(name)
        name = twitter_name(name)
        if direct:
            with PImage.open(f'{assets}/{name}.png') as fin:
                img = fin.resize((ppem, ppem), PImage.ANTIALIAS)
                stream = io.BytesIO()
                img.save(stream, format='png')
                glyph.imageData = stream.getvalue()
                stream.close()
        else:
            svg = svg_to_blob(f'{assets}/svg/{name}.svg', ppem)
            if extract:
                with open(f'{fontname}/{ppem}/{name}.png', 'wb') as fout:
                    fout.write(svg)
            glyph.imageData = svg

f.save(f'{fontname}/{ttf}')
