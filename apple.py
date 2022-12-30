import sys
import io
from fontTools import ttLib
from PIL import Image

fontname = 'AppleColorEmoji@2x'

# input: font ttf, assets folder

ttf = sys.argv[1]
assets = sys.argv[2]

f = ttLib.TTFont(ttf)

for ppem, strike in f['sbix'].strikes.items():
    print(f'Reading strike of size {ppem}x{ppem}')
    for name, glyph in strike.glyphs.items():
        if glyph.graphicType != 'png ':
            continue
        path = f'{assets}/{ppem}/{name}.png'
        with Image.open(path) as fin:
            stream = io.BytesIO()
            fin.save(stream, format='png')
            glyph.imageData = stream.getvalue()
            stream.close()

print('Saving changes...')
f.save(ttf)
