# Caveats

Missing emojis or limitations of each non-Apple themed font will be listed here.

## Blobmoji Emoji

- Nothing of significant.

## Facebook Emoji

- Nothing of significant.

## FluentUI Emoji

- Their `Color` style SVG files are weird that `rsvg-convert` would error out with no memory. I have to use a slower approach `inkscape` instead.
- Upstream is missing family, couple, flag, skinned handshake, paperclip, technologist and some other emojis.

## Google Noto Emoji

- Nothing of significant.

## JoyPixels Emoji

- Nothing of significant.

## OpenMoji Emoji

- Couple emojis of different skins will not share the same hair color as it seems so in the original OpenMoji. In my opinion, this is better because why would two people of different races always share the same hair color?

## Samsung One UI Emoji

- Eye in speech emoji is from the older design of One UI. Samsung just didn't include it in One UI 5.0 officially.

## Twitter Twemoji

- Nothing of significant.

## WhatsApp Emoji

- Nothing of significant.

## Notes

<!-- _PNGs only_: They come in PNGs which means adding silhouettes, handshake and couple emojis are difficult. If they were in SVGs, we can simply write a script to remove parts that we do not need. -->

Special thanks to [@Dayanch96](https://twitter.com/Dayanch96) for splitting PNG-only couple emojis from certain emoji vendors to the format that is suitable for Apple Color Emoji.
