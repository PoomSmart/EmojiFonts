#!/usr/bin/env bash

set -e

FONT_NAME=AppleColorEmoji@2x
NAME=joypixels
EMOJI_ASSETS=../$NAME-7/png/unicode/128
MOD=$1
ASSETS=$NAME/$MOD

rm -rf $ASSETS
mkdir -p $ASSETS/96 $ASSETS/64 $ASSETS/48 $ASSETS/40 $ASSETS/32 $ASSETS/20

echo "Copying PNGs..."
cp -r $EMOJI_ASSETS/ $ASSETS/96

./get-assets.sh joypixels

if [[ $MOD == 'Decal' ]]
then
    echo "Applying mod: Decal..."
    mogrify -bordercolor none -border 5 -background white -alpha background -channel A -blur 0x3 -level 0,1% $ASSETS/96/*.png
    mogrify -bordercolor none -border 5 -background white -alpha background -channel A -blur 0x3 -level 0,1% $NAME-extra/images/96/*.png
    mogrify -resize 96x96 $NAME-extra/images/96/*.png
fi

echo "Resizing PNGs..."
mogrify -resize 96x96 $ASSETS/96/*.png
mogrify -resize 64x64 -path $ASSETS/64 $ASSETS/96/*.png
mogrify -resize 40x40 -path $ASSETS/40 $ASSETS/64/*.png
# mogrify -resize 48x48 -path $ASSETS/48 $ASSETS/64/*.png
# mogrify -resize 40x40 -path $ASSETS/40 $ASSETS/48/*.png
# mogrify -resize 32x32 -path $ASSETS/32 $ASSETS/40/*.png
# mogrify -resize 20x20 -path $ASSETS/20 $ASSETS/32/*.png

echo "Optimizing PNGs using pngquant..."
pngquant -f --ext .png $ASSETS/*/*.png
pngquant -f --ext .png $NAME-extra/*/*.png

python3 $NAME.py apple/${FONT_NAME}_00.ttf $MOD
python3 $NAME.py apple/${FONT_NAME}_01.ttf $MOD

if [[ $MOD != '' ]]
then
    PREFIX=$MOD-
    OUT_FONT_NAME=$NAME-$MOD.ttc
else
    OUT_FONT_NAME=$NAME.ttc
fi

python3 otf2otc.py $NAME/$PREFIX${FONT_NAME}_00.ttf $NAME/$PREFIX${FONT_NAME}_01.ttf -o $NAME/$OUT_FONT_NAME

echo "Output file at $NAME/$OUT_FONT_NAME"
