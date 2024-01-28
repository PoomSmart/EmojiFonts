# Quickstart

Assuming a macOS machine with homebrew and Python 3.7+ installed:

## Dependencies

```
bash -c "pip3 install --upgrade afdko fonttools[repacker]>=4.39.1 pyliblzfse Pillow"
brew install bash pngquant oxipng freetype imagemagick librsvg svgo
```

## AppleColorEmoji font

```
# Copy iOS AppleColorEmoji font to ./AppleColorEmoji_iOS.ttc
cp /System/Library/Fonts/Apple\ Color\ Emoji.ttc ./AppleColorEmoji_macOS.ttc
./prepare.sh && ./apple-prepare.sh macOS && ./apple.sh HD
```
