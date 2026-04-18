#!/usr/bin/env bash

set -e
trap 'echo "Error in $(basename "$0") at line $LINENO" >&2' ERR

NAME=openmoji
ASSETS=../../$NAME/color/svg
MAX_SIZE=160

../image-sizes.sh true

cd extra
rm -rf svgs
mkdir -p svgs
../../image-sizes.sh true
uv run python gen-couple-heart.py
uv run python gen-couple-kiss.py
uv run python gen-couple-stand.py
uv run python gen-handshake.py
uv run python gen-bunny-ears.py
uv run python gen-wrestling.py

echo "Converting SVGs into PNGs..."
../../svg-to-png.sh ./svgs $MAX_SIZE
../../resize.sh true true
cd ..

../svg-to-png.sh "$ASSETS" $MAX_SIZE

echo "Resizing and optimizing PNGs..."
../resize.sh true true

uv run python extra/gen-couple-nn.py

IN_FONT_NAME=AppleColorEmoji-HD
OUT_FONT_NAME=$NAME.ttc

uv run python $NAME.py ../apple/${IN_FONT_NAME}_00.ttf
uv run python $NAME.py ../apple/${IN_FONT_NAME}_01.ttf

uv run otf2otc ${IN_FONT_NAME}_00.ttf ${IN_FONT_NAME}_01.ttf -o $OUT_FONT_NAME
rm -f *_00.ttf *_01.ttf

echo "Output file at $NAME/$OUT_FONT_NAME"
