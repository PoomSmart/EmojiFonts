#!/usr/bin/env bash

set -e

NAME=apple
FONT_NAME=AppleColorEmoji@2x
ASSETS=$NAME
MOD=$1
COLORS=

mkdir -p $ASSETS

echo "Extracting PNGs from $FONT_NAME font..."
python3 extractor.py $NAME common/${FONT_NAME}_00._s_b_i_x.ttx

if [[ $MOD == 'LQ' ]]
then
    COLORS=8
    echo "Applying mod: LQ..."
    mogrify +dither -posterize 8 -normalize $ASSETS/*/*.png
fi

echo "Optimizing PNGs using pngquant..."
pngquant $COLORS -f --ext .png $ASSETS/*/*.png

if [[ $MOD != '' ]]
then
    OUT_FONT_NAME=AppleColorEmoji-$MOD
else
    OUT_FONT_NAME=$FONT_NAME
fi

python3 $NAME.py common/${FONT_NAME}_00.ttf apple/${OUT_FONT_NAME}_00.ttf $ASSETS
python3 $NAME.py common/${FONT_NAME}_01.ttf apple/${OUT_FONT_NAME}_01.ttf $ASSETS
ln apple/${OUT_FONT_NAME}_00.ttf apple/$OUT_FONT_NAME.ttf

python3 otf2otc.py apple/${OUT_FONT_NAME}_00.ttf apple/${OUT_FONT_NAME}_01.ttf -o apple/$OUT_FONT_NAME.ttc
