import sys
from fontTools import ttLib
from shared import prepare_strikes

# input: input font ttf, output font ttf, assets folder

ittf = sys.argv[1]
ottf = sys.argv[2]
assets = sys.argv[3]

f = ttLib.TTFont(ittf)

prepare_strikes(f)
for ppem, strike in f['sbix'].strikes.items():
    print(f'Reading strike of size {ppem}x{ppem}')
    for name, glyph in strike.glyphs.items():
        if glyph.graphicType != 'emjc': # or 'png ' for macOS equivalent
            continue
        glyph.graphicType = 'png '
        path = f'{assets}/{ppem}/{name}.png'
        with open(path, 'rb') as fin:
            glyph.imageData = fin.read()

print('Saving changes...')
f.save(ottf)
