#!/bin/bash

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
rm -f *.png 1f*.svg silhouette*.svg
python3 gen-couple-heart.py
python3 gen-couple-kiss.py
python3 gen-couple-stand.py
python3 gen-handshake.py
for svg in $(find . -type f -name '*.svg')
do
    rsvg-convert -a -h $MAX_SIZE $svg > ${svg/.svg/.png}
done
cd ..

rm -f $NAME/*.ttx
python3 $NAME.py ${FONT_NAME}_00.ttf $ASSETS $FLAG_ASSETS
./compat.sh $NAME/${FONT_NAME}_00.ttf
python3 $NAME.py ${FONT_NAME}_01.ttf $ASSETS $FLAG_ASSETS
./compat.sh $NAME/${FONT_NAME}_01.ttf

python3 otf2otc.py $NAME/${FONT_NAME}_00.ttf $NAME/${FONT_NAME}_01.ttf -o $NAME/$NAME.ttc

echo "Output file at $NAME/$NAME.ttc"
