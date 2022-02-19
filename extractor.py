import sys
import binascii
import pathlib
import xml.etree.ElementTree as ET

data = ET.parse(sys.argv[1]).getroot()

for strike in data.findall('sbix/strike'):
    ppem = strike.find('ppem').attrib['value']
    pathlib.Path(f'out/{ppem}').mkdir(parents=True, exist_ok=True) 
    for glyph in strike.findall('glyph'):
        if glyph.get('graphicType') == 'png ':
            name = glyph.get('name')
            # print(f'Exporting {name} ({ppem}x{ppem})')
            hexdata = glyph.find('hexdata').text.strip()
            with open(f'out/{ppem}/{name}.png', 'wb') as fout:
                fout.write(binascii.unhexlify(''.join(hexdata.split())))
