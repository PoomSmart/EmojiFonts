#!/usr/bin/env bash

set -e

FONT_NAME=AppleColorEmoji@2x
NAME=joypixels
ASSETS=../$NAME-7/png/unicode/128
MAX_SIZE=96

rm -rf $NAME
mkdir -p $NAME

python3 $NAME.py common/${FONT_NAME}_00.ttf $ASSETS
python3 $NAME.py common/${FONT_NAME}_01.ttf $ASSETS

python3 otf2otc.py $NAME/${FONT_NAME}_00.ttf $NAME/${FONT_NAME}_01.ttf -o $NAME/$NAME.ttc

echo "Output file at $NAME/$NAME.ttc"
