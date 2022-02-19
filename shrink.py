import sys
import xml.etree.ElementTree as ET

data = ET.parse(sys.argv[1]).getroot()

sbix = data.find('sbix')
for strike in data.iter('strike'):
    ppem = strike.find('ppem')
    value = ppem.attrib['value']
    print(value)
    # possible values: 20, 26, 40, 48, 52, 64, 96, 160
    if value == '26' or value == '52' or value == '160':
        sbix.remove(strike)

output = ET.ElementTree(data)
output.write(sys.argv[1], encoding='utf-8')