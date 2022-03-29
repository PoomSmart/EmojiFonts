#!/bin/bash

set -e

FONT_NAME=AppleColorEmoji@2x
NAME=facebook
ASSETS=../emoji-data/img-facebook-96

rm -rf $NAME
mkdir -p $NAME
mkdir -p ${NAME}-extra

rm -f $NAME/*.ttx
python3 $NAME.py ${FONT_NAME}_00.ttf $ASSETS
./compat.sh $NAME/${FONT_NAME}_00.ttf
python3 $NAME.py ${FONT_NAME}_01.ttf $ASSETS
./compat.sh $NAME/${FONT_NAME}_01.ttf

python3 otf2otc.py $NAME/${FONT_NAME}_00.ttf $NAME/${FONT_NAME}_01.ttf -o $NAME/$NAME.ttc

echo "Output file at $NAME/$NAME.ttc"
