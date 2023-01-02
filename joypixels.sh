#!/usr/bin/env bash

set -e

FONT_NAME=AppleColorEmoji@2x
NAME=joypixels
ASSETS=../$NAME-7/png/unicode/128
MOD=$1

rm -rf $NAME
mkdir -p $NAME/96 $NAME/64 $NAME/48 $NAME/40 $NAME/32 $NAME/20

echo "Copying and resizing PNGs..."
cp -r $ASSETS/ $NAME/96

if [[ $MOD == 'Decal' ]]
then
    echo "Applying mod: Decal..."
    mogrify -bordercolor none -border 5 -background white -alpha background -channel A -blur 0x3 -level 0,1% $NAME/96/*.png
fi

mogrify -resize 96x96 $NAME/96/*.png
mogrify -resize 64x64 -path $NAME/64 $NAME/96/*.png
mogrify -resize 48x48 -path $NAME/48 $NAME/64/*.png
mogrify -resize 40x40 -path $NAME/40 $NAME/48/*.png
mogrify -resize 32x32 -path $NAME/32 $NAME/40/*.png
mogrify -resize 20x20 -path $NAME/20 $NAME/32/*.png

echo "Optimizing PNGs using pngquant..."
pngquant -f --ext .png $NAME/*/*.png

python3 $NAME.py common/${FONT_NAME}_00.ttf
python3 $NAME.py common/${FONT_NAME}_01.ttf

if [[ $MOD != '' ]]
then
    OUT_FONT_NAME=$NAME-$MOD.ttc
else
    OUT_FONT_NAME=$NAME.ttc
fi

python3 otf2otc.py $NAME/${FONT_NAME}_00.ttf $NAME/${FONT_NAME}_01.ttf -o $NAME/$OUT_FONT_NAME

echo "Output file at $NAME/$OUT_FONT_NAME"
