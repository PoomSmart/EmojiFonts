# EmojiFonts

Python and shell scripts to backport and theme [Apple Color Emoji font](https://en.wikipedia.org/wiki/Apple_Color_Emoji).

# Prerequisites

- [Python 3.7 or later](http://www.python.org/download/)
- [pip](https://pip.pypa.io/en/stable/)
- [fonttools](https://github.com/fonttools/fonttools) (`pip3 install fonttools[repacker]`)
- [Pillow](https://pillow.readthedocs.io/en/stable/) (`python3 -m pip install --upgrade Pillow`)
- [getfonts](https://github.com/DavidBarts/getfonts) (for `getfonts`, `getfontname` and `stripttc`)
- [pngquant](https://pngquant.org) (`brew install pngquant`)

# Prerequisites (Theming)

- [ImageMagick](https://imagemagick.org/index.php) (`brew install freetype imagemagick`)
- [Wand](https://pypi.org/project/Wand/) (`pip3 install Wand`)
- [librsvg](https://wiki.gnome.org/Projects/LibRsvg) (`brew install librsvg`)
- [inkscape](https://formulae.brew.sh/cask/inkscape) (`brew install inkscape`)
- php (`brew install php`)

# Before anything

1. Copy `Apple Color Emoji.ttc` from `/System/Library/Fonts` of your macOS instance to the root of this repository and rename it to `AppleColorEmoji@2x.ttc`.
2. Execute `prepare.sh` to create emoji TTF files and tables. Run this once.

# Building Apple Color Emoji font

- Execute `apple.sh`, you will get `AppleColorEmoji@2x.ttc` (for iOS 10 and above) and `AppleColorEmoji@2x.ttf` (for iOS 9 and below) under `apple` directory.

## Optimization

The script `apple.sh` uses `pngquant` to optimize the images with little to none changes to the quality. The Apple emoji font sizes are reduced by nearly 50% using this method.

# Scripts

EmojiFonts deals with certain font tables; mainly `GDEF` and `sbix`.

`shift-multi.py` resizes and shifts the multi-skinned emojis that pair up as one, including couples and handshake, to have them displayed on iOS 13 and below correctly where there is no render logic to automatically place the pair close together.

`GDEF` table which maps each of paired emojis to a certain class, is removed by the scripts. This is for the easiest backward-compatible solution for the emoji font. If the table is present, the text render engine on iOS 14+ will try to place the pair close together again even when we applied `shift-multi.py` to the font.

`remove-strikes.py` removes supposedly least used strikes (image data) from `sbix` table. By default, emoji images come in a variety of dimensions from `20x20` to `160x160`. If images are uncompressed (macOS, for example), the total font size exceeds 100 MB which is not suitable for storing in GitHub repository.

`extractor.py` extracts PNG emoji images from the font. This opens up the possibility to theme the emoji font.

`otf2otc.py` combines TTF (True Type Font) fonts into a single TTC (True Type Collection) font. From iOS 10, Apple Color Emoji is built as TTC.

# Theming

Theming scripts for all emojis vendors produce the font in TTC format. The font may be used by EmojiFontManager iOS tweak, and is guaranteed to work on iOS 6 and higher. Ensure that you executed `apple.sh` before following instructions below.

## Blobmoji Emoji

1. Clone [blobmoji](https://github.com/C1710/blobmoji) and place its folder alongside this project.
2. Execute `blobmoji.sh` to create themed font, output at `blobmoji/blobmoji.ttc`.

## Facebook Emoji

1. Shallow clone [emoji-data](https://github.com/iamcal/emoji-data) and place its folder alongside this project.
3. Execute `facebook.sh` to create them themed font, output at `facebook/facebook.ttc`.

## FluentUI Emoji

1. Clone [fluentui-emoji](https://github.com/microsoft/fluentui-emoji) and place its folder alongside this project.
2. Execute `fluentui.sh STYLE` (where `STYLE` is one of this list: `Color, Flat, High Contrast`) to create themed font, output at `fluentui/fluentui-STYLE.ttc`.

## Google Noto Emoji

1. Clone [noto-emoji](https://github.com/googlefonts/noto-emoji) and place its folder alongside this project.
2. Execute `noto-emoji.sh` to create the themed font, output at `noto-emoji/noto-emoji.ttc`.

## JoyPixels Emoji

1. Download JoyPixels 7.0 Free assets from JoyPixels [Download page](https://joypixels.com/download) and place the folder alongside this project.
2. Execute `joypixels.sh` to create themed font, output at `joypixels/joypixels.ttc`.

## OpenMoji Emoji

1. Clone [openmoji](https://github.com/hfg-gmuend/openmoji) and place its folder alongside this project.
2. Execute `openmoji.sh` to create themed font, output at `openmoji/openmoji.ttc`.

## Samsung One UI Emoji

1. Retrieve `NotoColorEmoji.ttf` with Samsung One UI 5.0 emojis somehow and place that in `oneui` folder.
2. Execute `oneui.sh` to create themed font, output at `oneui/oneui.ttc`.

## Twitter Twemoji

1. Clone [twemoji](https://github.com/twitter/twemoji) and place its folder alongside this project.
2. Execute `twemoji.sh` to create the themed font, output at `twemoji/twemoji.ttc`.

## WhatsApp Emoji

1. Retrieve `NotoColorEmoji.ttf` with WhatsApp emojis somehow and place that in `whatsapp` folder.
2. Execute `whatsapp.sh` to create themed font, output at `whatsapp/whatsapp.ttc`.
