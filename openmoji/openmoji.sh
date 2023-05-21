#!/usr/bin/env bash

set -e

FONT_NAME=AppleColorEmoji@2x
NAME=openmoji
ASSETS=../../$NAME/color/svg
MAX_SIZE=160

../image-sizes.sh true

cd extra
rm -rf svgs
mkdir -p svgs
../../image-sizes.sh true
python3 gen-couple-heart.py
python3 gen-couple-kiss.py
python3 gen-couple-stand.py
python3 gen-handshake.py

echo "Converting SVGs into PNGs..."
for svg in $(find ./svgs -type f -name '*.svg')
do
    fname=$(basename $svg)
    rsvg-convert -a -h $MAX_SIZE $svg -o images/$MAX_SIZE/${fname/.svg/.png}
done
../../resize.sh true false true
cd ..

for svg in $(find $ASSETS -type f -name '*.svg')
do
    fname=$(basename $svg)
    rsvg-convert -a -h $MAX_SIZE $svg -o images/$MAX_SIZE/${fname/.svg/.png}
done

echo "Resizing and optimizing PNGs..."
../resize.sh true false true

IN_FONT_NAME=AppleColorEmoji-HD
OUT_FONT_NAME=$NAME.ttc

python3 $NAME.py ../apple/${IN_FONT_NAME}_00.ttf
python3 $NAME.py ../apple/${IN_FONT_NAME}_01.ttf

otf2otc ${IN_FONT_NAME}_00.ttf ${IN_FONT_NAME}_01.ttf -o $OUT_FONT_NAME
rm -f *_00.ttf *_01.ttf

echo "Output file at $NAME/$OUT_FONT_NAME"
