#!/usr/bin/env bash

set -e

NAME=blobmoji
APPLE_FONT_NAME=AppleColorEmoji
ASSETS=../../$NAME/png
MAX_SIZE=96

../image-sizes.sh false

cp -r $ASSETS/ images/$MAX_SIZE

echo "Resizing and optimizing PNGs..."
../resize.sh false false false true

cd extra
rm -rf svgs images
mkdir -p svgs images/96 images/64 images/40
uv run gen-couple-heart.py
uv run gen-couple-kiss.py
uv run gen-couple-stand.py
uv run gen-handshake.py
for svg in $(find ./svgs -type f -name '*.svg')
do
    fname=$(basename $svg)
    rsvg-convert -a -h $MAX_SIZE $svg -o images/$MAX_SIZE/${fname/.svg/.png}
done
../../resize.sh false false false
cd ..

uv run $NAME-noto.py ../apple/${APPLE_FONT_NAME}_00.ttf
uv run $NAME-noto.py ../apple/${APPLE_FONT_NAME}_01.ttf

uv run otf2otc ${APPLE_FONT_NAME}_00.ttf ${APPLE_FONT_NAME}_01.ttf -o $NAME.ttc
rm -f *_00.ttf *_01.ttf

echo "Output file at $NAME/$NAME.ttc"
