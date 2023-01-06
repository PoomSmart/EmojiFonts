# Caveats

Missing emojis or limitations of each themed font will be listed here.

## Twitter Twemoji

- Nothing of significant.

## Google Noto Emoji

- Nothing of significant.

## Facebook Emoji

- Rely on `emoji-data` repository which is outdated and I had to write additional code to fetch few more emojis.
- _PNGs only._

## JoyPixels Emoji

- _PNGs only._

## FluentUI Emoji

- Their `Color` style SVG files are weird that `rsvg-convert` would error out with no memory. I have to use a slower approach `inkscape` instead.
- Upstream is missing family, couple, flag, skinned handshake, paperclip, technologist and some other emojis.

## Blobmoji Emoji

- Nothing of significant.

## OpenMoji Emoji

- Not yet support: skinned handshake, some couple emojis.

## Samsung One UI Emoji

- Eye in speech bubble emoji is not supported.
- Somewhat _PNGs only._

## Notes

_PNGs only_: They come in PNGs which means adding silhouettes, handshake and couple emojis are difficult. If they were in SVGs, we can simply write a script to remove parts that we do not need.
