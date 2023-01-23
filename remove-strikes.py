import sys
import xml.etree.ElementTree as ET

# input: font sbix ttx
data = ET.parse(sys.argv[1]).getroot()

sbix = data.find('sbix')
for strike in data.iter('strike'):
    ppem = strike.find('ppem')
    value = ppem.attrib['value']
    # possible values: 20, 26, 32, 40, 48, 52, 64, 96, 160
    if value == '26' or value == '52':
        print(f'Removed strike {value}x{value}')
        sbix.remove(strike)

output = ET.ElementTree(data)
output.write(sys.argv[1], encoding='utf-8')
