# Quickstart

macOS machine with homebrew and Python 3.7+ installed, assumed:

## Dependencies

```
python3 -m pip install --upgrade Pillow
pip3 install fonttools[repacker]
brew install pngquant freetype imagemagick librsvg inkscape php
```

## AppleColorEmoji font

```
cp /System/Library/Fonts/Apple\ Color\ Emoji.ttc ./AppleColorEmoji@2x.ttc
./prepare.sh && ./apple.sh
```
