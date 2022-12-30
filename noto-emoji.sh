#!/usr/bin/env bash

set -e

FONT_NAME=AppleColorEmoji@2x
NAME=noto-emoji
ASSETS=../$NAME/png/128
FLAG_ASSETS=../$NAME/third_party/region-flags/png
MAX_SIZE=96

rm -rf $NAME
mkdir -p $NAME

echo "Converting SVGs into PNGs..."
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
    rsvg-convert -a -h $MAX_SIZE $svg -o images/${fname/.svg/.png}
done
cd ..

python3 $NAME.py common/${FONT_NAME}_00.ttf $ASSETS $FLAG_ASSETS
python3 $NAME.py common/${FONT_NAME}_01.ttf $ASSETS $FLAG_ASSETS

python3 otf2otc.py $NAME/${FONT_NAME}_00.ttf $NAME/${FONT_NAME}_01.ttf -o $NAME/$NAME.ttc

echo "Output file at $NAME/$NAME.ttc"
