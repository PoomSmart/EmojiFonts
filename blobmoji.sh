#!/usr/bin/env bash

set -e

APPLE_FONT_NAME=AppleColorEmoji@2x
NAME=blobmoji
ASSETS=../$NAME/svg
FONT_ASSETS=../$NAME/fonts
FONT_NAME=Blobmoji
FONT_PATH=$FONT_ASSETS/$FONT_NAME.ttf
MAX_SIZE=96

rm -rf $NAME
mkdir -p $NAME/images/96 $NAME/images/64 $NAME/images/48 $NAME/images/40 $NAME/images/32 $NAME/images/20

echo "Extracting font..."
cp $FONT_PATH $NAME
cd $NAME
ttx -q -s -z extfile $FONT_NAME.ttf
cd ..

echo "Copying and resizing PNGs..."
mogrify -resize 96x96 -path $NAME/images/96 $NAME/bitmaps/strike0/*.png
mogrify -resize 64x64 -path $NAME/images/64 $NAME/images/96/*.png
mogrify -resize 48x48 -path $NAME/images/48 $NAME/images/64/*.png
mogrify -resize 40x40 -path $NAME/images/40 $NAME/images/48/*.png
mogrify -resize 32x32 -path $NAME/images/32 $NAME/images/40/*.png
mogrify -resize 20x20 -path $NAME/images/20 $NAME/images/32/*.png

cd $NAME-extra
rm -rf svgs images
mkdir -p svgs images/96 images/64 images/48 images/40 images/32 images/20
python3 gen-couple-heart.py
python3 gen-couple-kiss.py
python3 gen-couple-stand.py
python3 gen-handshake.py
for svg in $(find ./svgs -type f -name '*.svg')
do
    fname=$(basename $svg)
    rsvg-convert -a -h $MAX_SIZE $svg -o images/$MAX_SIZE/${fname/.svg/.png}
done

echo "Resizing PNGs..."
mogrify -resize 64x64 -path images/64 images/96/*.png
mogrify -resize 48x48 -path images/48 images/64/*.png
mogrify -resize 40x40 -path images/40 images/48/*.png
mogrify -resize 32x32 -path images/32 images/40/*.png
mogrify -resize 20x20 -path images/20 images/32/*.png

cd ..
rm -rf $NAME/bitmaps

echo "Optimizing PNGs using pngquant..."
pngquant -f --ext .png $NAME/images/96/*.png
pngquant -f --ext .png $NAME/images/64/*.png
pngquant -f --ext .png $NAME/images/48/*.png
pngquant -f --ext .png $NAME/images/40/*.png
pngquant -f --ext .png $NAME/images/32/*.png
pngquant -f --ext .png $NAME/images/20/*.png
pngquant -f --ext .png $NAME-extra/images/*/*.png

python3 $NAME.py common/${APPLE_FONT_NAME}_00.ttf $NAME/$FONT_NAME.ttf $NAME/$FONT_NAME.G_S_U_B_.ttx
python3 $NAME.py common/${APPLE_FONT_NAME}_01.ttf $NAME/$FONT_NAME.ttf $NAME/$FONT_NAME.G_S_U_B_.ttx

python3 otf2otc.py $NAME/${APPLE_FONT_NAME}_00.ttf $NAME/${APPLE_FONT_NAME}_01.ttf -o $NAME/$NAME.ttc

echo "Output file at $NAME/$NAME.ttc"
