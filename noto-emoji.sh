#!/bin/bash

set -e

FONT_NAME=AppleColorEmoji@2x
NAME=noto-emoji
ASSETS=../$NAME/png/128
FLAG_ASSETS=../$NAME/third_party/region-flags/png

rm -rf $NAME
mkdir -p $NAME

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

python3 $NAME.py ${FONT_NAME}_00.ttf $ASSETS $FLAG_ASSETS
python3 $NAME.py ${FONT_NAME}_01.ttf $ASSETS $FLAG_ASSETS

python3 otf2otc.py $NAME/${FONT_NAME}_00.ttf $NAME/${FONT_NAME}_01.ttf -o $NAME/$NAME.ttc

echo "Output file at $NAME/$NAME.ttc"
