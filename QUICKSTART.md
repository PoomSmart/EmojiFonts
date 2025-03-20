# Quickstart

Assuming a macOS machine with homebrew and Python 3.8+ installed:

## Dependencies

```
uv sync
brew install bash pngquant oxipng freetype imagemagick librsvg svgo
```

## AppleColorEmoji font

```
# Copy iOS AppleColorEmoji font to ./AppleColorEmoji_iOS.ttc
cp /System/Library/Fonts/Apple\ Color\ Emoji.ttc ./AppleColorEmoji_macOS.ttc
./prepare.sh && ./apple-prepare.sh macOS && ./apple.sh HD
```
