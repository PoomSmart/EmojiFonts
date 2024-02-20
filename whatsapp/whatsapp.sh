#!/usr/bin/env bash

set -e

NAME=whatsapp
ASSETS=../../whatsapp-emoji-linux/png/160

../image-sizes.sh true
cp -r $ASSETS/ images/160

echo "Resizing and optimizing PNGs..."
../resize.sh true false false

../get-assets.sh whatsapp false true

# IN_FONT_NAME=AppleColorEmoji-HD
IN_FONT_NAME=AppleColorEmoji
OUT_FONT_NAME=$NAME.ttc

python3 $NAME.py ../apple/${IN_FONT_NAME}_00.ttf
python3 $NAME.py ../apple/${IN_FONT_NAME}_01.ttf

otf2otc ${IN_FONT_NAME}_00.ttf ${IN_FONT_NAME}_01.ttf -o $OUT_FONT_NAME
rm -f *_00.ttf *_01.ttf

echo "Output file at $NAME/$OUT_FONT_NAME"
