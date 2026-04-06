from fontTools import ttLib

from shared import gender_selectors

name_map = {
    "u0023": "numbersign",
    "u002A": "asterisk",
    "u0030": "zero",
    "u0031": "one",
    "u0032": "two",
    "u0033": "three",
    "u0034": "four",
    "u0035": "five",
    "u0036": "six",
    "u0037": "seven",
    "u0038": "eight",
    "u0039": "nine",
}


class Lig:
    def __init__(self, f: ttLib.TTFont, bttf: str):
        b = ttLib.TTFont(bttf)
        self.bgsub = b["GSUB"].table
        self.blig = {}
        self.icmap = f.get("cmap").buildReversed()
        self.cmap = f.get("cmap").tables[0].cmap
        self.bicmap = b.get("cmap").buildReversed()
        self.bcmap = b.get("cmap").tables[1].cmap

    def get_apple_code(self, code: str):
        code = next(iter(self.bicmap[code]))
        if code == 0x200D:
            return "u200D"
        if code in self.cmap:
            code = self.cmap[code]
        code = str(code)
        code = code.replace(".0", "")
        return code

    def norm_name(self, name: str):
        name = name.upper()
        tokens = name.split("_")
        s = []
        for t in tokens:
            t = f"uni{t}" if t in gender_selectors.values() else f"u{t}"
            s.append(t)
        if s[0] in name_map:
            s[0] = name_map[s[0]]
        return "_".join(s)

    def build(self):
        print("Building ligatures...")
        self.bicmap_apple = {}
        for key in self.bicmap:
            self.bicmap_apple[self.get_apple_code(key)] = self.bicmap[key]

        for lookup in self.bgsub.LookupList.Lookup:
            if lookup.LookupType != 4:
                continue
            for subtable in lookup.SubTable:
                for first_glyph, ligs in subtable.ligatures.items():
                    glyph = self.get_apple_code(first_glyph)
                    for lig in ligs:
                        s = [self.get_apple_code(c) for c in lig.Component]
                        name = f"{glyph}_{'_'.join(s)}"
                        self.blig[name] = lig.LigGlyph

    def get_glyph_name(self, name: str):
        if name in self.icmap:
            code = next(iter(self.icmap[name]))
            return self.bcmap[code]
        if name in self.bicmap_apple:
            code = next(iter(self.bicmap_apple[name]))
            return self.bcmap[code]
        if name in self.blig:
            return self.blig[name]
        return name
