#!/usr/bin/env bash

set -e

APPLE_FONT_NAME=AppleColorEmoji
NAME=facebook
FONT_NAME=NotoColorEmoji
ASSETS=../../facebook-emojis/images/96

../image-sizes.sh false

cp -r $ASSETS/ images/96

echo "Extracting font..."
ttx -q -f -z extfile $FONT_NAME.ttf
ttx -q -f -s -t GSUB $FONT_NAME.ttf

echo "Resizing and optimizing PNGs..."
mogrify -resize 96x96 -path images/96 bitmaps/strike0/*.png
../resize.sh false false false
rm -rf bitmaps

mkdir -p extra/images/96
cp extra/original/*.png extra/images/96
../get-assets.sh facebook

uv run $NAME.py ../apple/${APPLE_FONT_NAME}_00.ttf $FONT_NAME.ttf $FONT_NAME.G_S_U_B_.ttx
uv run $NAME.py ../apple/${APPLE_FONT_NAME}_01.ttf $FONT_NAME.ttf $FONT_NAME.G_S_U_B_.ttx

uv run otf2otc ${APPLE_FONT_NAME}_00.ttf ${APPLE_FONT_NAME}_01.ttf -o $NAME.ttc
rm -f *_00.ttf *_01.ttf

echo "Output file at $NAME/$NAME.ttc"
