#!/usr/bin/env bash

set -e

NAME=tossface
APPLE_FONT_NAME=AppleColorEmoji
FONT_NAME=TossFaceFontMac
ASSETS=images
ORIGINAL_SIZE=112
MAX_SIZE=96

../image-sizes.sh false

echo "Extracting font..."
uv run ttx -q -s -f -t sbix $FONT_NAME.ttf
uv run emojifonts-extract images $FONT_NAME._s_b_i_x.ttx

echo "Resizing and optimizing PNGs..."
mogrify -resize 96x96 -path $ASSETS/96 $ASSETS/$ORIGINAL_SIZE/*.png
rm -rf $ASSETS/$ORIGINAL_SIZE
../resize.sh false false

uv run python $NAME.py ../apple/${APPLE_FONT_NAME}_00.ttf $FONT_NAME.ttf
uv run python $NAME.py ../apple/${APPLE_FONT_NAME}_01.ttf $FONT_NAME.ttf

uv run otf2otc ${APPLE_FONT_NAME}_00.ttf ${APPLE_FONT_NAME}_01.ttf -o $NAME.ttc
rm -f *_00.ttf *_01.ttf

echo "Output file at $NAME/$NAME.ttc"
