# Quickstart

macOS machine with homebrew and Python 3.7+ installed, assumed:

## Dependencies

```
bash -c "pip3 install afdko fonttools[repacker]"
pip3 install --upgrade Pillow
brew install pngquant freetype imagemagick librsvg inkscape php
```

## AppleColorEmoji font

```
# Copy iOS AppleColorEmoji font to ./AppleColorEmoji_iOS.ttc
cp /System/Library/Fonts/Apple\ Color\ Emoji.ttc ./AppleColorEmoji_macOS.ttc
./prepare.sh; ./apple.sh
```
