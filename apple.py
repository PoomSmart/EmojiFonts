import sys
from fontTools import ttLib
from shared import get_image_data, prepare_strikes

# input: HD boolean, input font ttf, output font ttf, assets folder

hd = sys.argv[1] == 'true'
ittf = sys.argv[2]
ottf = sys.argv[3]
assets = sys.argv[4]

f = ttLib.TTFont(ittf)

prepare_strikes(f, hd)
for ppem, strike in f['sbix'].strikes.items():
    print(f'Reading strike of size {ppem}x{ppem}')
    for name, glyph in strike.glyphs.items():
        if glyph.graphicType != 'emjc' and glyph.graphicType != 'flip': # or 'png ' for macOS equivalent of the font
            continue
        glyph.graphicType = 'png '
        path = f'{assets}/{ppem}/{name}.png'
        glyph.imageData = get_image_data(path)

print('Saving changes...')
f.save(ottf)
