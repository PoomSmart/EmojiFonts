#!/usr/bin/env bash

set -e

NAME=blobmoji
APPLE_FONT_NAME=AppleColorEmoji
ASSETS=../../$NAME/svg
FONT_ASSETS=../../$NAME/fonts
FONT_NAME=Blobmoji
FONT_PATH=$FONT_ASSETS/$FONT_NAME.ttf
MAX_SIZE=96

../image-sizes.sh false

echo "Extracting font..."
cp $FONT_PATH .
ttx -q -f -z extfile $FONT_NAME.ttf
ttx -q -f -s -t GSUB $FONT_NAME.ttf

echo "Resizing and optimizing PNGs..."
mogrify -resize 96x96 -path images/96 bitmaps/strike0/*.png
../resize.sh false false false
rm -rf bitmaps

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

uv run $NAME.py ../apple/${APPLE_FONT_NAME}_00.ttf $FONT_NAME.ttf $FONT_NAME.G_S_U_B_.ttx
uv run $NAME.py ../apple/${APPLE_FONT_NAME}_01.ttf $FONT_NAME.ttf $FONT_NAME.G_S_U_B_.ttx

uv run otf2otc ${APPLE_FONT_NAME}_00.ttf ${APPLE_FONT_NAME}_01.ttf -o $NAME.ttc
rm -f *_00.ttf *_01.ttf

echo "Output file at $NAME/$NAME.ttc"
