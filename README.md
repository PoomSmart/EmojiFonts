# EmojiFonts

Python scripts to backport Apple Color Emoji font.

# Prerequisites

- [Python 3.7 or later](http://www.python.org/download/)
- [pip](https://pip.pypa.io/en/stable/)
- [fonttools](https://github.com/fonttools/fonttools) (`pip3 install fonttools`)
- (Optional) [Pillow](https://pillow.readthedocs.io/en/stable/) (`python3 -m pip install --upgrade Pillow`)

# How to use

1. Copy `Apple Color Emoji.ttc` from `/System/Library/Fonts` of your macOS instance to the root of this repository and rename it to `AppleColorEmoji@2x.ttc`.
2. Execute `get-fonts.sh`
3. Once finished, you will get `AppleColorEmoji@2x-out.ttc` that's compatible with iOS 13 and below and `AppleColorEmoji@2x.ttf` that's compatible with iOS 9 and below.

# Scripts

EmojiFonts modifies two font tables; `hmtx` and `sbix`.

`shift-multi.py` resizes and shifts the multi-skinned emojis that pair up as one, including couples and handshake, to have them displayed on iOS 13 and below correctly where there is no render logic to automatically place the pair close together.

`shrink.py` removes supposedly least used strikes (image data) from `sbix` table. By default, emoji images come in certain dimensions from `20x20` to `160x160`. If images are uncompressed (macOS, for example), the total font size exceeds 100 MB which is not suitable for storing in GitHub repository.

`strip.py` strips PNG metadata out of emoji images using Python PIL Fork (Pillow). This is the case for older macOS emoji font where Apple simply did not optimize the PNGs and made the font size so big. You may comment out the execution of this script in `get-fonts.sh` if you are working on a recent emoji font.

`extractor.py` extracts PNG emoji images from the font - and opens up the possibility to theme the emoji font!

`otf2otc.py` combines TTF (True Type Font) fonts into a single TTC (True Type Collection) font. Fron iOS 10, Apple Color Emoji is built as TTC.