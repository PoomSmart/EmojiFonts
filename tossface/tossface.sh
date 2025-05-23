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
ttx -q -s -f -t sbix -t GSUB $FONT_NAME.ttf
uv run ../extractor.py images $FONT_NAME._s_b_i_x.ttx

echo "Resizing and optimizing PNGs..."
mogrify -resize 96x96 -path $ASSETS/96 $ASSETS/$ORIGINAL_SIZE/*.png
rm -rf $ASSETS/$ORIGINAL_SIZE
../resize.sh false false false

uv run $NAME.py ../apple/${APPLE_FONT_NAME}_00.ttf $FONT_NAME.ttf $FONT_NAME.G_S_U_B_.ttx
uv run $NAME.py ../apple/${APPLE_FONT_NAME}_01.ttf $FONT_NAME.ttf $FONT_NAME.G_S_U_B_.ttx

uv run otf2otc ${APPLE_FONT_NAME}_00.ttf ${APPLE_FONT_NAME}_01.ttf -o $NAME.ttc
rm -f *_00.ttf *_01.ttf

echo "Output file at $NAME/$NAME.ttc"
