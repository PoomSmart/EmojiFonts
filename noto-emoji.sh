#!/bin/bash

set -e

FONT_NAME=AppleColorEmoji@2x
NAME=noto-emoji
ASSETS=../$NAME/png/128
FLAG_ASSETS=../$NAME/third_party/region-flags/png

rm -rf $NAME
mkdir -p $NAME

# ./getfonts $FONT_NAME.ttc
python3 $NAME.py ${FONT_NAME}_00.ttf $ASSETS $FLAG_ASSETS
python3 $NAME.py ${FONT_NAME}_01.ttf $ASSETS $FLAG_ASSETS

python3 otf2otc.py $NAME/${FONT_NAME}_00.ttf $NAME/${FONT_NAME}_01.ttf -o $NAME/$NAME.ttc

echo "Output file at $NAME/$NAME.ttc"
