import sys
import binascii
import io
import xml.etree.ElementTree as ET
from PIL import Image

# input: font sbix ttx
data = ET.parse(sys.argv[1]).getroot()

for strike in data.iter('strike'):
    for glyph in strike.findall('glyph'):
        if glyph.get('graphicType') == 'png ':
            hexdata = glyph.find('hexdata')
            hex = ''.join(hexdata.text.strip().split())
            bytes = binascii.unhexlify(hex)
            stream = io.BytesIO(bytes)
            pil = Image.open(stream)
            stripped = Image.new(pil.mode, pil.size)
            stripped.putdata(pil.getdata())
            stripped_stream = io.BytesIO()
            stripped.save(stripped_stream, format='PNG', optimize=True, compress_level=9)
            stripped_hex = stripped_stream.getvalue().hex()
            hexdata.text = stripped_hex
            stream.close()

output = ET.ElementTree(data)
output.write(sys.argv[1], encoding='utf-8')
