#!/usr/bin/env bash

set -e

MOD=$1
if [ -z $MOD ]; then
    echo "Usage: $0 <MOD>"
    echo "MOD: Decal, Default"
    exit 1
fi

FONT_NAME=AppleColorEmoji@2x
NAME=joypixels
EMOJI_ASSETS=../../$NAME-7/png/unicode/128
ASSETS=$MOD

rm -rf $ASSETS
mkdir -p $ASSETS/images/96 $ASSETS/images/64 $ASSETS/images/48 $ASSETS/images/40 $ASSETS/images/32 $ASSETS/images/20

echo "Copying PNGs..."
cp -r $EMOJI_ASSETS/ $ASSETS/images/96

../get-assets.sh $NAME

if [[ $MOD == 'Decal' ]]
then
    echo "Applying mod: Decal..."
    mogrify -bordercolor none -border 5 -background white -alpha background -channel A -blur 0x3 -level 0,1% $ASSETS/images/96/*.png
    mogrify -bordercolor none -border 5 -background white -alpha background -channel A -blur 0x3 -level 0,1% extra/images/96/*.png
    mogrify -resize 96x96 extra/images/96/*.png
fi

echo "Resizing PNGs..."
mogrify -resize 96x96 $ASSETS/images/96/*.png
mogrify -resize 64x64 -path $ASSETS/images/64 $ASSETS/images/96/*.png
mogrify -resize 40x40 -path $ASSETS/images/40 $ASSETS/images/64/*.png
# mogrify -resize 48x48 -path $ASSETS/images/48 $ASSETS/images/64/*.png
# mogrify -resize 40x40 -path $ASSETS/images/40 $ASSETS/images/48/*.png
# mogrify -resize 32x32 -path $ASSETS/images/32 $ASSETS/images/40/*.png
# mogrify -resize 20x20 -path $ASSETS/images/20 $ASSETS/images/32/*.png

echo "Optimizing PNGs..."
pngquant --skip-if-larger -f --ext .png $ASSETS/images/*/*.png &
pngquant --skip-if-larger -f --ext .png extra/images/*/*.png &
wait
oxipng -q $ASSETS/images/*/*.png &
oxipng -q extra/images/*/*.png &
wait

python3 $NAME.py ../apple/${FONT_NAME}_00.ttf $MOD &
python3 $NAME.py ../apple/${FONT_NAME}_01.ttf $MOD &
wait

PREFIX=$MOD-
OUT_FONT_NAME=$NAME-$MOD.ttc

otf2otc $PREFIX${FONT_NAME}_00.ttf $PREFIX${FONT_NAME}_01.ttf -o $OUT_FONT_NAME

if [ $OUT_FONT_NAME = "$NAME-Default.ttc" ]; then
    mv $OUT_FONT_NAME $NAME.ttc
    OUT_FONT_NAME=$NAME.ttc
fi

echo "Output file at $NAME/$OUT_FONT_NAME"
