#!/usr/bin/env bash

set -e

FONT_NAME=AppleColorEmoji@2x
NAME=facebook
ASSETS=$NAME
ASSETS_96=../emoji-data/img-facebook-96
ASSETS_64=../emoji-data/img-facebook-64

rm -rf $NAME
rm -f ${NAME}-extra/*/*.png
mkdir -p $NAME/96 $NAME/64 $NAME/48 $NAME/40 $NAME/32 $NAME/20

echo "Fetching extra PNGs..."
php facebook-fetch.php &> /dev/null

echo "Copying and resizing PNGs..."
cp -r $ASSETS_96/ $NAME/96
cp -r $ASSETS_64/ $NAME/64

mogrify -resize 48x48 -path $NAME/48 $NAME/64/*.png
mogrify -resize 40x40 -path $NAME/40 $NAME/48/*.png
mogrify -resize 32x32 -path $NAME/32 $NAME/40/*.png
mogrify -resize 20x20 -path $NAME/20 $NAME/32/*.png

mogrify -resize 64x64 -path ${NAME}-extra/64 ${NAME}-extra/96/*.png
mogrify -resize 48x48 -path ${NAME}-extra/48 ${NAME}-extra/64/*.png
mogrify -resize 40x40 -path ${NAME}-extra/40 ${NAME}-extra/48/*.png
mogrify -resize 32x32 -path ${NAME}-extra/32 ${NAME}-extra/40/*.png
mogrify -resize 20x20 -path ${NAME}-extra/20 ${NAME}-extra/32/*.png

echo "Optimizing PNGs using pngquant..."
pngquant -f --ext .png $NAME/*/*.png ${NAME}-extra/*/*.png

python3 $NAME.py common/${FONT_NAME}_00.ttf $ASSETS
python3 $NAME.py common/${FONT_NAME}_01.ttf $ASSETS

python3 otf2otc.py $NAME/${FONT_NAME}_00.ttf $NAME/${FONT_NAME}_01.ttf -o $NAME/$NAME.ttc

echo "Output file at $NAME/$NAME.ttc"
