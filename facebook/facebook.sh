#!/usr/bin/env bash

set -e

FONT_NAME=AppleColorEmoji
NAME=facebook
ASSETS=../../facebook-emojis/images/96

../image-sizes.sh false
cd extra
../../image-sizes.sh false
cd ..

cp -r $ASSETS/ images/96

cp extra/original/*.png extra/images/96
../get-assets.sh facebook

echo "Resizing and optimizing PNGs..."
../resize.sh false false false
cd extra
../../resize.sh false false false
cd ..

uv run $NAME.py ../apple/${FONT_NAME}_00.ttf
uv run $NAME.py ../apple/${FONT_NAME}_01.ttf

uv run otf2otc ${FONT_NAME}_00.ttf ${FONT_NAME}_01.ttf -o $NAME.ttc
rm -f *_00.ttf *_01.ttf

echo "Output file at $NAME/$NAME.ttc"
