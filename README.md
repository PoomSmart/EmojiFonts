# EmojiFonts

Python and shell scripts to backport and theme [Apple Color Emoji font](https://en.wikipedia.org/wiki/Apple_Color_Emoji).

# Prerequisites

- Bash version 5+ (`brew install bash`)
- [Python 3.11+](http://www.python.org/download/)
- [uv](https://github.com/astral-sh/uv)
- [pip](https://pip.pypa.io/en/stable/)
- [fonttools 4.48.0+](https://github.com/fonttools/fonttools) (`pip3 install fonttools[repacker]>=4.48.0`)
- [afdko](https://github.com/adobe-type-tools/afdko) (`pip3 install afdko`)
- [libpylzfse](https://github.com/ydkhatri/pyliblzfse) (`pip3 install libpylzfse`)
- [Pillow](https://github.com/python-pillow/Pillow) (`pip3 install Pillow`)
- [pngquant](https://pngquant.org) (`brew install pngquant`)
- [oxipng](https://github.com/shssoichiro/oxipng) (`brew install oxipng`)

# Prerequisites (Theming)

- [ImageMagick](https://imagemagick.org/index.php) (`brew install freetype imagemagick`)
- [librsvg](https://wiki.gnome.org/Projects/LibRsvg) (`brew install librsvg`)
- [svgo](https://github.com/svg/svgo) (`brew install svgo`)

# Before anything

1. Copy `Apple Color Emoji.ttc` from `/System/Library/Fonts` of your macOS instance to the root of this repository and rename it to `AppleColorEmoji_macOS.ttc`.
2. Copy AppleColorEmoji font from your iOS instance to the root of this repository and rename it to `AppleColorEmoji_iOS.ttc`. Read [here](https://poomsmart.github.io/emojiport) for the exact file path.
3. Execute `uv sync` to activate/synchronize the Python virtual environment.
4. Execute `./prepare.sh` to create emoji TTF files and tables. Run this once.

# Building Apple Color Emoji font

Build format: `./apple-prepare.sh <OS> && ./apple.sh [HD]`

Replace `<OS>` with `macOS` (if you have both macOS and iOS fonts) or `iOS` (if you only have iOS font).

Replace `[HD]` with `HD` if you want to build HD version (160x160 image set included), or leave it blank for normal version.

Executing `./apple-prepare.sh <OS> && ./apple.sh` will get `AppleColorEmoji@2x.ttc` (for iOS 10 and above) and `AppleColorEmoji@2x.ttf` (for iOS 9 and below) for you under `apple` directory.

# Notable Python Scripts

EmojiFonts deals with certain font tables; mainly `GDEF` and `sbix`.

`shift-multi.py` (or CLI alias `emojifonts-shift-multi`) resizes and shifts the multi-skinned emojis that pair up as one, including couples and handshake, to have them displayed on iOS 13 and below correctly where there is no render logic to automatically place the pair close together.

`GDEF` table which maps each of paired emojis to a certain class, is modified by the scripts. This is for the easiest backward-compatible solution for the emoji font. In this table, emojis with class `1` and `3` represent `left` and `right`, respectively. With those present, the text render engine on iOS 14+ will try to place the pair close together again even when we applied `shift-multi.py` to the font. Another script `remove-class3.py` ensures that there are no class `1` and `3` emojis that will otherwise be visible to the users.

`extractor.py` (CLI alias `emojifonts-extract`) extracts PNG emoji images from the font. This opens up the possibility to theme the emoji font.

Also in `extractor.py`, it detects glyphs of type `flip`, reads the actual image glyph ID that they reference to, programmatically flips them and then extracts them. `flip` glyphs are present in iOS 17.4 version of Apple Color Emoji font and not supported by any lower OS versions. They are for directional emojis - Apple has a single image for each direction, and the font uses `flip` glyphs to render the correct image.

`apple.py` (CLI alias `emojifonts-apple`) swaps in PNG assets extracted with the previous step back into the sbix table.

`remove-class3.py` (CLI alias `emojifonts-remove-class3`) trims class 3 glyph assignments from the Apple GDEF table.

# PNG Optimization

`pngquant` and `oxipng` are used to optimize the images with little to none changes to the quality. The Apple emoji font sizes are reduced by 50% using this method. The simpler the emoji images, the more size reduction is achieved.

# Verification

- Run `uv run pytest` to ensure the extractor, class trimming, and metric overrides behave as expected against the bundled fixtures.
- Run `uv run ruff check .` to lint the Python toolchain, or `uv run ruff format .` to auto-format when needed.
- After running `emojifonts-extract`, spot-check output with `open apple/images/64/u1F600.png` (or any glyph) and verify flipped glyphs are emitted.
- After `emojifonts-apple`, diff the sbix table with `ttx -o - apple/AppleColorEmoji@2x.ttc | grep -c '<glyph'` to confirm the strike counts remain unchanged.

# Troubleshooting

- `Flip glyph references unknown glyph`: regenerate TTX tables with `./prepare.sh` to keep sbix data in sync with recent Apple font updates.
- `Overrides refer to missing glyph metrics`: re-run `emojifonts-shift-multi` against the freshly exported `hmtx.ttx`; stale files from earlier releases omit the new handshake glyphs.
- `pngquant: command not found`: install the dependency via `brew install pngquant` (or remove the optimizer by setting `PNGQUANT=0` before invoking shell helpers).

# Theming

Theming scripts for all emojis vendors produce the font in TTC format. The font may be used by EmojiFontManager iOS tweak, and is guaranteed to work on iOS 6 and higher. Ensure that you executed `./apple-prepare.sh <OS> && ./apple.sh HD` before following instructions below.

It is recommended to limit the depth of clone to `1` (`git clone --depth 1 git@github.com:PoomSmart/EmojiFonts.git`) because of a long history of commits.

## Blobmoji Emoji

1. Clone [blobmoji2](https://github.com/DavidBerdik/blobmoji2) and place its folder alongside this project.
2. Execute `cd blobmoji && ./blobmoji-noto.sh` to create themed font, output at `blobmoji/blobmoji.ttc`.

## Facebook Emoji

1. Clone [facebook-emojis](https://github.com/PoomSmart/facebook-emojis) and place its folder alongside this project.
3. Execute `cd facebook && ./facebook.sh` to create them themed font, output at `facebook/facebook.ttc`.

## FluentUI Emoji

1. Clone [fluentui-emoji](https://github.com/microsoft/fluentui-emoji) and place its folder alongside this project.
2. Execute `cd fluentui && ./fluentui.sh STYLE` (where `STYLE` is one of this list: `Color, Flat, High Contrast`) to create themed font, output at `fluentui/fluentui-STYLE.ttc`.

## Google Noto Color Emoji

1. Clone [noto-emoji](https://github.com/googlefonts/noto-emoji) and place its folder alongside this project.
2. Execute `cd noto-emoji && ./noto-emoji.sh` to create the themed font, output at `noto-emoji/noto-emoji.ttc`.

## JoyPixels Emoji

1. Clone [emoji-assets](https://github.com/joypixels/emoji-assets) and place its folder alongside this project.
2. Execute `cd joypixels && ./joypixels.sh` to create themed font, output at `joypixels/joypixels.ttc`.

## OpenMoji Emoji

1. Clone [openmoji](https://github.com/hfg-gmuend/openmoji) and place its folder alongside this project.
2. Execute `cd openmoji && ./openmoji.sh` to create themed font, output at `openmoji/openmoji.ttc`.

## Samsung One UI Emoji

1. Retrieve `SamsungColorEmoji.ttf` with Samsung One UI emojis somehow and place that in `oneui` folder.
2. Execute `cd oneui && ./oneui.sh` to create themed font, output at `oneui/oneui.ttc`.

## Toss Face Emoji

1. Download `TossFaceFontMac.ttf` from [tossface GitHub Releases](https://github.com/toss/tossface) and place that in `tossface` folder.
2. Execute `cd tossface && ./tossface.sh` to create themed font, output at `tossface/tossface.ttc`.

## Twitter Twemoji

1. Clone [twemoji](https://github.com/jdecked/twemoji) and place its folder alongside this project.
2. Execute `cd twemoji && ./twemoji.sh` to create the themed font, output at `twemoji/twemoji.ttc`.

## WhatsApp Emoji

1. Clone [whatsapp-emoji-linux](https://github.com/dmlls/whatsapp-emoji-linux) and place its folder alongside this project.
2. Execute `cd whatsapp && ./whatsapp.sh` to create themed font, output at `whatsapp/whatsapp.ttc`.
