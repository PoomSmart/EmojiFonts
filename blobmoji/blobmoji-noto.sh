#!/usr/bin/env bash

set -e

NAME=blobmoji
APPLE_FONT_NAME=AppleColorEmoji-HD
ASSETS=../../${NAME}2/svg
FLAG_ASSETS=../../${NAME}2/third_party/region-flags/waved-svg
MAX_SIZE=160

../image-sizes.sh true

echo "Converting SVGs into PNGs..."
for svg in $(find $ASSETS -type f -name '*.svg')
do
    fname=$(basename $svg)
    rsvg-convert -a -h $MAX_SIZE $svg -o images/$MAX_SIZE/${fname/.svg/.png}
done
for svg in $(find $FLAG_ASSETS -type f -name '*.svg')
do
    fname=$(basename $svg)
    rsvg-convert -a -h $MAX_SIZE $svg -o images/$MAX_SIZE/${fname/.svg/.png}
done

cd extra
rm -rf svgs images
mkdir -p svgs
../../image-sizes.sh true
uv run python gen-couple-heart.py
uv run python gen-couple-kiss.py
uv run python gen-couple-stand.py
uv run python gen-handshake.py
for svg in $(find ./svgs -type f -name '*.svg')
do
    fname=$(basename $svg)
    rsvg-convert -a -h $MAX_SIZE $svg -o images/$MAX_SIZE/${fname/.svg/.png}
done
../../resize.sh true false false
cd ..

echo "Resizing and optimizing PNGs..."
../resize.sh true false false

uv run python $NAME-noto.py ../apple/${APPLE_FONT_NAME}_00.ttf
uv run python $NAME-noto.py ../apple/${APPLE_FONT_NAME}_01.ttf

uv run otf2otc ${APPLE_FONT_NAME}_00.ttf ${APPLE_FONT_NAME}_01.ttf -o $NAME.ttc
rm -f *_00.ttf *_01.ttf

echo "Output file at $NAME/$NAME.ttc"
