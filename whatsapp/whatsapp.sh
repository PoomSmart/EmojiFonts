#!/usr/bin/env bash

set -e

NAME=whatsapp
ASSETS=../../whatsapp-emoji-linux/png/160

../image-sizes.sh true
cp -r $ASSETS/ images/160

echo "Resizing and optimizing PNGs..."
../resize.sh true false

echo "Generating couple split tiles..."
uv run python split_from_160_restart.py

echo "Optimizing generated PNGs..."
pngquant --skip-if-larger -f --ext .png extra/images/*/*.png || true
oxipng -q extra/images/*/*.png

IN_FONT_NAME=AppleColorEmoji-HD
OUT_FONT_NAME=$NAME.ttc

uv run python $NAME.py ../apple/${IN_FONT_NAME}_00.ttf
uv run python $NAME.py ../apple/${IN_FONT_NAME}_01.ttf

uv run otf2otc ${IN_FONT_NAME}_00.ttf ${IN_FONT_NAME}_01.ttf -o $OUT_FONT_NAME
rm -f *_00.ttf *_01.ttf

echo "Output file at $NAME/$OUT_FONT_NAME"
