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

cd $ASSETS
../../image-sizes.sh false
cd ..

cp -r $EMOJI_ASSETS/ $ASSETS/images/96

../get-assets.sh $NAME

if [[ $MOD == 'Decal' ]]
then
    echo "Applying mod: Decal..."
    mogrify -bordercolor none -border 5 -background white -alpha background -channel A -blur 0x3 -level 0,1% $ASSETS/images/96/*.png
    mogrify -bordercolor none -border 5 -background white -alpha background -channel A -blur 0x3 -level 0,1% extra/images/96/*.png
    mogrify -resize 96x96 extra/images/96/*.png
fi

echo "Resizing and optimizing PNGs..."
cd $ASSETS
../../resize.sh false false false
cd ../extra
../../resize.sh false false false
cd ..

python3 $NAME.py ../apple/${FONT_NAME}_00.ttf $MOD
python3 $NAME.py ../apple/${FONT_NAME}_01.ttf $MOD

PREFIX=$MOD-
OUT_FONT_NAME=$NAME-$MOD.ttc

otf2otc $PREFIX${FONT_NAME}_00.ttf $PREFIX${FONT_NAME}_01.ttf -o $OUT_FONT_NAME
rm -f *_00.ttf *_01.ttf

if [ $OUT_FONT_NAME = "$NAME-Default.ttc" ]; then
    mv $OUT_FONT_NAME $NAME.ttc
    OUT_FONT_NAME=$NAME.ttc
fi

echo "Output file at $NAME/$OUT_FONT_NAME"
