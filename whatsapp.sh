#!/usr/bin/env bash

set -e

APPLE_FONT_NAME=AppleColorEmoji@2x
NAME=whatsapp
FONT_NAME=NotoColorEmoji
FONT_PATH=$NAME/$FONT_NAME.ttf

rm -rf $NAME/images
mkdir -p $NAME/images/96 $NAME/images/64 $NAME/images/48 $NAME/images/40 $NAME/images/32 $NAME/images/20

echo "Extracting font..."
cd $NAME
ttx -q -f -z extfile $FONT_NAME.ttf
ttx -q -f -s -t GSUB $FONT_NAME.ttf
cd ..

echo "Copying, resizing and optimizing PNGs..."
mogrify -resize 96x96 -path $NAME/images/96 $NAME/bitmaps/strike0/*.png
./resize.sh $NAME false false false
rm -rf $NAME/bitmaps

./get-assets.sh whatsapp

pngquant --skip-if-larger -f --ext .png $NAME-extra/images/*/*.png
oxipng -q $NAME-extra/images/*/*.png

python3 $NAME.py apple/${APPLE_FONT_NAME}_00.ttf $NAME/$FONT_NAME.ttf $NAME/$FONT_NAME.G_S_U_B_.ttx &
python3 $NAME.py apple/${APPLE_FONT_NAME}_01.ttf $NAME/$FONT_NAME.ttf $NAME/$FONT_NAME.G_S_U_B_.ttx &
wait

otf2otc $NAME/${APPLE_FONT_NAME}_00.ttf $NAME/${APPLE_FONT_NAME}_01.ttf -o $NAME/$NAME.ttc

echo "Output file at $NAME/$NAME.ttc"
