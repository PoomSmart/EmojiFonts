#!/usr/bin/env bash

set -e

FONT_NAME=AppleColorEmoji@2x
NAME=facebook
ASSETS_96=../emoji-data/img-facebook-96
ASSETS_64=../emoji-data/img-facebook-64

rm -rf $NAME
mkdir -p $NAME
mkdir -p ${NAME}-extra

rm -f ${NAME}-extra/64/*.png
for png in $(find ./${NAME}-extra/96 -type f -name '*.png')
do
    fname=$(basename $png)
    convert $png -resize 64x64 png32:${NAME}-extra/64/$fname
done

python3 $NAME.py common/${FONT_NAME}_00.ttf $ASSETS_96 $ASSETS_64
python3 $NAME.py common/${FONT_NAME}_01.ttf $ASSETS_96 $ASSETS_64

python3 otf2otc.py $NAME/${FONT_NAME}_00.ttf $NAME/${FONT_NAME}_01.ttf -o $NAME/$NAME.ttc

echo "Output file at $NAME/$NAME.ttc"
