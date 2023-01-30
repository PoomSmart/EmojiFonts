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
ttx -q -f -z extfile $FONT_NAME.ttf
ttx -q -f -s -t GSUB $FONT_NAME.ttf
cd ..

echo "Copying, resizing and optimizing PNGs..."
mogrify -resize 96x96 -path $NAME/images/96 $NAME/bitmaps/strike0/*.png
./resize.sh $NAME false false false
rm -rf $NAME/bitmaps

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
    rsvg-convert -a -h $MAX_SIZE $svg -o images/$MAX_SIZE/${fname/.svg/.png} &
done
wait

echo "Resizing and optimizing PNGs..."
cd ..
./resize.sh $NAME-extra false false false

python3 $NAME.py apple/${APPLE_FONT_NAME}_00.ttf $NAME/$FONT_NAME.ttf $NAME/$FONT_NAME.G_S_U_B_.ttx &
python3 $NAME.py apple/${APPLE_FONT_NAME}_01.ttf $NAME/$FONT_NAME.ttf $NAME/$FONT_NAME.G_S_U_B_.ttx &
wait

otf2otc $NAME/${APPLE_FONT_NAME}_00.ttf $NAME/${APPLE_FONT_NAME}_01.ttf -o $NAME/$NAME.ttc

echo "Output file at $NAME/$NAME.ttc"
