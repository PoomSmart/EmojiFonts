import json as _json
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path as _Path

from fontTools import ttLib

debug = False

_data = _json.loads((_Path(__file__).parent / "data" / "emoji_constants.json").read_text())
hairs: list = _data["hairs"]
professions: list = _data["professions"]
directions: list = _data["directions"]
modifiers: list = _data["modifiers"]
gender_selectors: dict = _data["gender_selectors"]
skins: dict = {int(k): v for k, v in _data["skins"].items()}
neutral_fams: list = _data["neutral_fams"]
flags: list = _data["flags"]
with_variants: set = set(_data["with_variants"])
u15_1: list = _data["u15_1"]
u17_0: list = _data["u17_0"]
whitelist: set = set(_data["whitelist"])
signs: list = _data["signs"]
gender_with_selector: list = _data["gender_with_selector"]

man, woman, neutral = "1f468", "1f469", "1f9d1"
boy, girl = "1f466", "1f467"
persons = {"m": man, "w": woman, "b": boy, "g": girl, "": ""}


def m_print(string: str):
    if debug:
        print(string)


def is_flag(name: str):
    return any(f in name for f in flags)


def base_is_whitelist(name: str):
    return name in whitelist


def base_norm_name(name: str):
    if len(name) == 13 and "silhouette." in name:
        return name
    tokens = name.replace(".u", "_").split("_")
    n = []
    for t in tokens:
        if t[0] == "u":
            t = t[1:]
        n.append(t)
    return "_".join(n).lower()


def native_norm_name(name: str):
    if name[0] == "u":
        name = name[1:].lower()
        tokens = name.split("_")
        n = []
        for t in tokens:
            if t[0] == "u":
                t = t[1:]
            n.append(t)
        name = "_".join(n)
    return name


def norm_fam(name: str):
    if name in neutral_fams:
        return "_200d_".join(name.split("_"))
    if "1f46a." not in name:
        return name
    for p1 in ["m", "w", ""]:
        for p2 in ["m", "w"]:
            for c1 in ["g", "b", ""]:
                for c2 in ["g", "b"]:
                    suffix = f".{p1}{p2}{c1}{c2}"
                    if suffix in name:
                        seq = [persons[p1], persons[p2], persons[c1], persons[c2]]
                        return "_200d_".join(list(filter(len, seq)))
    return name


def norm_dual(name: str):
    for s in range(1, 6):
        if name == f"{man}_1f91d_{man}.{s}{s}":
            return f"1f46c_{skins[s]}"
        if name == f"{woman}_1f91d_{man}.{s}{s}":
            return f"1f46b_{skins[s]}"
        if name == f"{woman}_1f91d_{woman}.{s}{s}":
            return f"1f46d_{skins[s]}"
    for s1 in range(1, 6):
        for s2 in range(1, 6):
            if name == f"{neutral}_1f91d_{neutral}.{s1}{s2}":
                return f"{neutral}_{skins[s1]}_200d_1f91d_200d_{neutral}_{skins[s2]}"
    if name == "1f9d1_1f91d_1f9d1.66":
        m_print(f"Fallback to default for {name}")
        return "1f9d1_200d_1f91d_200d_1f9d1"
    if ".ra" in name:
        name = name.replace(".ra", ".r")
    return name


def norm_variant_selector(name: str):
    if name in with_variants:
        return f"{name}_fe0f"
    return name




def base_norm_variants(name: str, with_variant_selector=False, gender_need_selector=False, convert_male=False):
    if name.startswith("silhouette_1f9d1_1f91d"):
        return name
    v = "_fe0f" if with_variant_selector else ""
    for gender in ["m", "w"]:
        selector = gender_selectors[gender]
        for s in range(1, 6):
            if f".{s}.{gender}" in name:
                name = name.replace(f".{s}.{gender}", f"_{skins[s]}_200d_{selector}{v}")
        if f".{gender}" in name:
            found = False
            if gender_need_selector:
                for x in gender_with_selector:
                    if x in name:
                        found = True
                        name = name.replace(f".{gender}", f"_fe0f_200d_{selector}{v}")
                        break
            if not found:
                name = name.replace(f".{gender}", f"_200d_{selector}{v}")
    for s in range(1, 6):
        for m in modifiers:
            if name.endswith(f"_{m}.{s}"):
                name = name.replace(f"_{m}.{s}", f"_{skins[s]}_200d_{m}{v}")
    for d in directions:
        if name.endswith(f"_{d}"):
            name = name.replace(f"_{d}", f"_200d_{d}{v}")
    for p in professions:
        for s in range(1, 6):
            if name.endswith(f"_{p}.{s}"):
                return name.replace(f"_{p}.{s}", f"_{skins[s]}_200d_{p}")
            for d in directions:
                if name.endswith(f"_{p}.{s}_200d_{d}{v}"):
                    return name.replace(f"_{p}.{s}_200d_{d}{v}", f"_{skins[s]}_200d_{p}_200d_{d}{v}")
    if ".0" in name:
        name = name.replace(".0", "")
    for p in ["1f430", "1faef"]:
        for s in range(1, 6):
            for d in ["l", "r"]:
                if f"_{p}.{s}.{d}" in name:
                    name = name.replace(f"_{p}.{s}.{d}", f"_{skins[s]}_{p}.{d}")
                if f"_{p}.{d}.{s}" in name:
                    name = name.replace(f"_{p}.{d}.{s}", f"_{skins[s]}_{p}.{d}")
    for s in range(1, 6):
        if f".{s}" in name:
            if "1f9d1_1f384" in name:
                name = name.replace(f"_1f384.{s}", f"_{skins[s]}_200d_1f384")
            else:
                name = name.replace(f".{s}", f"_{skins[s]}")
    return name


def base_norm_special(name: str, with_variant_selector=False):
    v = "_fe0f" if with_variant_selector else ""
    if name == "26d3_1f4a5":
        return f"26d3{v}_200d_1f4a5"
    if name == "2764_1f525":
        return f"2764{v}_200d_1f525"
    if name == "2764_1fa79":
        return f"2764{v}_200d_1fa79"
    if name == "1f344_1f7eb":
        return "1f344_200d_1f7eb"
    if name == "1f34b_1f7e9":
        return "1f34b_200d_1f7e9"
    if name == "1f3f3_26a7":
        return f"1f3f3{v}_200d_26a7{v}"
    if name == "1f3f3_1f308":
        return f"1f3f3{v}_200d_1f308"
    if name == "1f3f4_2620":
        return f"1f3f4_200d_2620{v}"
    if name == "1f426_1f525":
        return "1f426_200d_1f525"
    if name == "1f43b_2744":
        return f"1f43b_200d_2744{v}"
    if name == "1f636_1f32b":
        return f"1f636_200d_1f32b{v}"
    if name == "1f408_2b1b":
        return "1f408_200d_2b1b"
    if name == "1f415_1f9ba":
        return "1f415_200d_1f9ba"
    if name == "1f426_2b1b":
        return "1f426_200d_2b1b"
    if name == "1f441_1f5e8":
        return "1f441_200d_1f5e8"
    if name == "1f62e_1f4a8":
        return "1f62e_200d_1f4a8"
    if name == "1f635_1f4ab":
        return "1f635_200d_1f4ab"
    if name == "1f9d1_1f384":
        return "1f9d1_200d_1f384"
    for g in [man, woman, neutral]:
        for m in modifiers:
            if name == f"{g}_{m}":
                return f"{g}_200d_{m}{v}"
        for p in professions:
            if name == f"{g}_{p}":
                return f"{g}_200d_{p}"
            for d in directions:
                if name == f"{g}_{p}_200d_{d}{v}":
                    return f"{g}_200d_{p}_200d_{d}{v}"
    return name


def get_image_data(path: str):
    with open(path, "rb") as fin:
        return fin.read()


def process_strikes(strikes, resolve):
    for ppem, strike in strikes.items():
        print(f"Reading strike of size {ppem}x{ppem}")
        with ThreadPoolExecutor() as executor:
            futures = {executor.submit(resolve, name, glyph, ppem): glyph for name, glyph in strike.glyphs.items()}
            for future, glyph in futures.items():
                data = future.result()
                if data is not None:
                    glyph.imageData = data


def prepare_strikes(f: ttLib.TTFont, hd=False):
    if hd and 160 not in f["sbix"].strikes:
        raise Exception("No 160 strike")
    if not hd and 160 in f["sbix"].strikes:
        f["sbix"].strikes.pop(160)


def make_resolver(
    *,
    norm_name_fn=None,
    extra_whitelist_fn=None,
    pre_norm_filter_fn=None,
    skip_if_multi=False,
    with_variant_selector=False,
    gender_need_selector=False,
    norm_special_fn=None,
    post_special_filter_fn=None,
    vendor_name_fn,
    image_paths_fn,
    post_process_fn=None,
):
    """Factory that returns a resolve(name, glyph, ppem) function for sbix strike processing.

    The returned resolver applies the shared normalisation chain and delegates vendor-specific
    naming and path lookup to the provided callbacks.
    """
    _norm_name = norm_name_fn or base_norm_name
    _norm_special = norm_special_fn or (lambda n: base_norm_special(n, with_variant_selector))

    def resolve(name, glyph, ppem):
        if glyph.graphicType != "png ":
            return None
        name = _norm_name(name)
        if base_is_whitelist(name):
            return None
        if extra_whitelist_fn is not None and extra_whitelist_fn(name):
            return None
        if pre_norm_filter_fn is not None:
            name = pre_norm_filter_fn(name)
            if name is None:
                return None
        o_name = name
        name = norm_fam(name)
        name = norm_dual(name)
        if name is None:
            return None
        if skip_if_multi and name != o_name:
            m_print(f"{name} is missing")
            return None
        name = base_norm_variants(name, with_variant_selector, gender_need_selector)
        name = _norm_special(name)
        if post_special_filter_fn is not None:
            name = post_special_filter_fn(name)
            if name is None:
                return None
        name = vendor_name_fn(name)
        for path in image_paths_fn(ppem, name):
            if os.path.exists(path):
                data = get_image_data(path)
                if post_process_fn is not None:
                    data = post_process_fn(data)
                return data
        return None

    return resolve
