import sys
import xml.etree.ElementTree as ET

data = ET.parse(sys.argv[1]).getroot()

to_remove = []
for classDef in data.iter('ClassDef'):
    glyph = classDef.attrib['glyph']
    if not glyph.startswith('outline.'):
        to_remove.append(classDef)

parent = data.find('.//GlyphClassDef')
for c in to_remove:
    parent.remove(c)

output = ET.ElementTree(data)
output.write(sys.argv[1], encoding='utf-8')
