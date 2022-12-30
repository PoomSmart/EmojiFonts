#!/usr/bin/env bash

NAME=apple
FONT_NAME=AppleColorEmoji@2x
ASSETS=$NAME

rm -rf $ASSETS
mkdir -p $ASSETS

echo "Extracting PNGs from $FONT_NAME font..."
python3 extractor.py $NAME common/${FONT_NAME}_00._s_b_i_x.ttx

echo "Optimizing PNGs using pngquant..."
pngquant -f --ext .png $ASSETS/*/*.png

cp common/${FONT_NAME}_00.ttf apple/${FONT_NAME}_00.ttf
cp common/${FONT_NAME}_01.ttf apple/${FONT_NAME}_01.ttf

python3 $NAME.py apple/${FONT_NAME}_00.ttf $ASSETS
python3 $NAME.py apple/${FONT_NAME}_01.ttf $ASSETS
cp apple/${FONT_NAME}_00.ttf apple/${FONT_NAME}.ttf

python3 otf2otc.py apple/${FONT_NAME}_00.ttf apple/${FONT_NAME}_01.ttf -o apple/$FONT_NAME.ttc
