# Quickstart

macOS machine with homebrew and Python 3.7+ installed, assumed:

## Dependencies

```
bash -c "pip3 install afdko fonttools[repacker]"
brew install bash pngquant oxipng freetype imagemagick librsvg inkscape
```

## AppleColorEmoji font

```
# Copy iOS AppleColorEmoji font to ./AppleColorEmoji_iOS.ttc
cp /System/Library/Fonts/Apple\ Color\ Emoji.ttc ./AppleColorEmoji_macOS.ttc
./prepare.sh; ./apple.sh
```
