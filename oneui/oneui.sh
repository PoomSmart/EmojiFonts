#!/usr/bin/env bash

set -e

APPLE_FONT_NAME=AppleColorEmoji@2x
NAME=oneui
FONT_NAME=NotoColorEmoji

../image-sizes.sh false

echo "Extracting font..."
ttx -q -f -z extfile $FONT_NAME.ttf
ttx -q -f -s -t GSUB $FONT_NAME.ttf

echo "Resizing and optimizing PNGs..."
mogrify -resize 96x96 -path images/96 bitmaps/strike0/*.png
../resize.sh false false false
rm -rf bitmaps

mkdir -p extra/images/96
cp extra/original/*.png extra/images/96
../get-assets.sh oneui

python3 $NAME.py ../apple/${APPLE_FONT_NAME}_00.ttf $FONT_NAME.ttf $FONT_NAME.G_S_U_B_.ttx
python3 $NAME.py ../apple/${APPLE_FONT_NAME}_01.ttf $FONT_NAME.ttf $FONT_NAME.G_S_U_B_.ttx

otf2otc ${APPLE_FONT_NAME}_00.ttf ${APPLE_FONT_NAME}_01.ttf -o $NAME.ttc
rm -f *_00.ttf *_01.ttf

echo "Output file at $NAME/$NAME.ttc"
