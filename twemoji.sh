#!/bin/bash

set -e

FONT_NAME=AppleColorEmoji@2x
NAME=twemoji
ASSETS=$NAME/images

./getfonts $FONT_NAME.ttc
python3 $NAME.py ${FONT_NAME}_00.ttf $ASSETS
python3 $NAME.py ${FONT_NAME}_01.ttf $ASSETS

python3 otf2otc.py $NAME/${FONT_NAME}_00.ttf $NAME/${FONT_NAME}_01.ttf -o $NAME/$NAME.ttc

echo "Output file at $NAME/$NAME.ttc"
