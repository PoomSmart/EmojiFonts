import sys
import binascii
import pathlib
import xml.etree.ElementTree as ET

# input: output folder, font sbix ttx
data = ET.parse(sys.argv[2]).getroot()

for strike in data.iter('strike'):
    ppem = strike.find('ppem').attrib['value']
    pathlib.Path(f'{sys.argv[1]}/{ppem}').mkdir(parents=True, exist_ok=True) 
    for glyph in strike.findall('glyph'):
        if glyph.get('graphicType') == 'png ':
            name = glyph.get('name')
            print(f'Exporting {name} ({ppem}x{ppem})')
            hexdata = glyph.find('hexdata').text.strip()
            with open(f'{sys.argv[1]}/{ppem}/{name}.png', 'wb') as fout:
                fout.write(binascii.unhexlify(''.join(hexdata.split())))
