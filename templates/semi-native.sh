#!/usr/bin/env bash

set -e

APPLE_FONT_NAME=AppleColorEmoji@2x
NAME=EMOJI_FONT
FONT_NAME=NotoColorEmoji
FONT_PATH=$NAME/$FONT_NAME.ttf

rm -rf $NAME/images
mkdir -p $NAME/images/96 $NAME/images/64 $NAME/images/48 $NAME/images/40 $NAME/images/32 $NAME/images/20

echo "Extracting font..."
cd $NAME
rm -f *.ttx
ttx -q -s -z extfile $FONT_NAME.ttf
cd ..

echo "Copying and resizing PNGs..."
mogrify -resize 96x96 -path $NAME/images/96 $NAME/bitmaps/strike0/*.png
mogrify -resize 64x64 -path $NAME/images/64 $NAME/images/96/*.png
mogrify -resize 48x48 -path $NAME/images/48 $NAME/images/64/*.png
mogrify -resize 40x40 -path $NAME/images/40 $NAME/images/48/*.png
mogrify -resize 32x32 -path $NAME/images/32 $NAME/images/40/*.png
mogrify -resize 20x20 -path $NAME/images/20 $NAME/images/32/*.png
rm -rf $NAME/bitmaps

echo "Optimizing PNGs using pngquant..."
pngquant -f --ext .png $NAME/images/96/*.png
pngquant -f --ext .png $NAME/images/64/*.png
pngquant -f --ext .png $NAME/images/48/*.png
pngquant -f --ext .png $NAME/images/40/*.png
pngquant -f --ext .png $NAME/images/32/*.png
pngquant -f --ext .png $NAME/images/20/*.png
# pngquant -f --ext .png $NAME-extra/images/*/*.png

python3 $NAME.py common/${APPLE_FONT_NAME}_00.ttf $NAME/$FONT_NAME.ttf $NAME/$FONT_NAME.G_S_U_B_.ttx
python3 $NAME.py common/${APPLE_FONT_NAME}_01.ttf $NAME/$FONT_NAME.ttf $NAME/$FONT_NAME.G_S_U_B_.ttx

otf2otc $NAME/${APPLE_FONT_NAME}_00.ttf $NAME/${APPLE_FONT_NAME}_01.ttf -o $NAME/$NAME.ttc

echo "Output file at $NAME/$NAME.ttc"
