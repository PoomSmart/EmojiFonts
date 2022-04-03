#!/bin/bash

set -e

FONT_NAME=AppleColorEmoji@2x
NAME=twemoji
ASSETS=$NAME/images
MAX_SIZE=96

rm -rf $ASSETS
mkdir -p $ASSETS

echo "Converting SVGs into PNGs..."
for svg in $(find ../twemoji/assets/svg -type f -name '*.svg')
do
    fname=$(basename $svg)
    rsvg-convert -a -h $MAX_SIZE $svg > $ASSETS/${fname/.svg/.png}
done

cd ${NAME}-extra
rm -rf images svgs
mkdir -p images svgs
python3 gen-couple-heart.py
python3 gen-couple-kiss.py
python3 gen-couple-stand.py
python3 gen-handshake.py
for svg in $(find ./svgs -type f -name '*.svg')
do
    fname=$(basename $svg)
    rsvg-convert -a -h $MAX_SIZE $svg > images/${fname/.svg/.png}
done
cd ..

python3 $NAME.py common/${FONT_NAME}_00.ttf $ASSETS
python3 $NAME.py common/${FONT_NAME}_01.ttf $ASSETS

python3 otf2otc.py $NAME/${FONT_NAME}_00.ttf $NAME/${FONT_NAME}_01.ttf -o $NAME/$NAME.ttc

echo "Output file at $NAME/$NAME.ttc"
