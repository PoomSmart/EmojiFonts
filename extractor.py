import binascii
import io
import pathlib
import sys
import xml.etree.ElementTree as ET
from emjc import decode_emjc
from PIL import Image

# uv run extractor.py apple common/AppleColorEmoji_macOS._s_b_i_x.ttx

# input: output folder, font sbix ttx
data = ET.parse(sys.argv[2]).getroot()

supported_types = ['png ', 'emjc']
allowed_strikes = [40, 64, 96, 160] + [112]
strike = data.find('sbix/strike')

for strike in data.iter('strike'):
    ppem = int(strike.find('ppem').attrib['value'])
    if ppem not in allowed_strikes:
        continue
    print(f'Reading strike of size {ppem}x{ppem}')
    pathlib.Path(f'{sys.argv[1]}/{ppem}').mkdir(parents=True, exist_ok=True)
    for glyph in strike.findall('glyph'):
        type = glyph.get('graphicType')
        name = glyph.get('name')
        flipped = type == 'flip'
        if flipped:
            ref = glyph.find('ref')
            glyphname = ref.get('glyphname')
            glyph = strike.find(f'glyph[@name="{glyphname}"]')
            type = glyph.get('graphicType')
        if type in supported_types:
            # print(f'Exporting {name} ({ppem}x{ppem})')
            hexdata = glyph.find('hexdata').text.strip()
            data = binascii.unhexlify(''.join(hexdata.split()))
            out_path = f'{sys.argv[1]}/{ppem}/{name}.png'
            if type == 'emjc':
                decoded = decode_emjc(data)
                img = Image.frombuffer('RGBA', (ppem, ppem), decoded, 'raw', 'BGRA', 0, 1)
                if flipped:
                    img = img.transpose(Image.FLIP_LEFT_RIGHT)
                img.save(out_path)
            else:
                if flipped:
                    img = Image.open(io.BytesIO(data))
                    img = img.transpose(Image.FLIP_LEFT_RIGHT)
                    img.save(out_path)
                else:
                    with open(out_path, 'wb') as fout:
                        fout.write(data)
