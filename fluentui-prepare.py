import argparse
import json
import shutil
import sys
from pathlib import Path

SK_FOLDERS = {
    'Default': None,
    'Light': '1f3fb',
    'Medium-Light': '1f3fc',
    'Medium': '1f3fd',
    'Medium-Dark': '1f3fe',
    'Dark': '1f3ff'
}

styles = ["3D", "Color", "Flat", "High Contrast"]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("assets",
                    help="Path to asset root folder",
                    type=Path)
    ap.add_argument("output",
                    help="Path to SVG output",
                    type=Path)
    ap.add_argument("style",
                    help=f'Style of emoji, has to be one of {styles}',
                    type=str)
    opts = ap.parse_args()

    for jp in opts.assets.rglob('**/metadata.json'):
        folder = jp.parent
        with open(jp, 'r') as jf:
            md = json.load(jf)
        
        uc = md.get('unicode')
        sks = md.get('unicodeSkintones')

        if sks is not None:
            i = 0
            for fldr in SK_FOLDERS:
                svg_path = next((folder / fldr / opts.style).glob('*.svg'))
                name = sks[i].replace(' ', '-')
                name = f'{name}.svg'
                dst = opts.output / opts.style / name
                shutil.copy(svg_path, dst)
                i += 1
        else:
            name = uc.replace(' ', '-')
            name = f'{name}.svg'
            svg_path = next(next(folder.glob(opts.style)).glob('*.svg'))
            dst = opts.output / opts.style / name
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(svg_path, dst)

if __name__ == '__main__':
    sys.exit(main())
