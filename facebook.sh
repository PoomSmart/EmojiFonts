#!/usr/bin/env bash

set -e

FONT_NAME=AppleColorEmoji@2x
NAME=facebook
ASSETS_96=../emoji-data/img-facebook-96
ASSETS_64=../emoji-data/img-facebook-64

rm -rf $NAME
mkdir -p $NAME/images/96 $NAME/images/64 $NAME/images/48 $NAME/images/40 $NAME/images/32 $NAME/images/20

echo "Fetching extra PNGs..."
# rm -rf $NAME-extra/images
mkdir -p $NAME-extra/images/96 $NAME-extra/images/64 $NAME-extra/images/48 $NAME-extra/images/40 $NAME-extra/images/32 $NAME-extra/images/20
php facebook-fetch.php &> /dev/null

echo "Copying PNGs..."
cp -r $ASSETS_96/ $NAME/images/96
cp -r $ASSETS_64/ $NAME/images/64

cp $NAME-extra/original/*.png $NAME-extra/images/96
./get-assets.sh facebook

echo "Resizing PNGs..."
mogrify -resize 40x40 -path $NAME/images/40 $NAME/images/64/*.png
# mogrify -resize 48x48 -path $NAME/images/48 $NAME/images/64/*.png
# mogrify -resize 40x40 -path $NAME/images/40 $NAME/images/48/*.png
# mogrify -resize 32x32 -path $NAME/images/32 $NAME/images/40/*.png
# mogrify -resize 20x20 -path $NAME/images/20 $NAME/images/32/*.png

mogrify -resize 64x64 -path $NAME-extra/images/64 $NAME-extra/images/96/*.png
mogrify -resize 40x40 -path $NAME-extra/images/40 $NAME-extra/images/64/*.png
# mogrify -resize 48x48 -path $NAME-extra/images/48 $NAME-extra/images/64/*.png
# mogrify -resize 40x40 -path $NAME-extra/images/40 $NAME-extra/images/48/*.png
# mogrify -resize 32x32 -path $NAME-extra/images/32 $NAME-extra/images/40/*.png
# mogrify -resize 20x20 -path $NAME-extra/images/20 $NAME-extra/images/32/*.png

echo "Optimizing PNGs using pngquant..."
pngquant -f --ext .png $NAME/images/96/*.png &
pngquant -f --ext .png $NAME/images/64/*.png &
# pngquant -f --ext .png $NAME/images/48/*.png &
pngquant -f --ext .png $NAME/images/40/*.png &
# pngquant -f --ext .png $NAME/images/32/*.png &
# pngquant -f --ext .png $NAME/images/20/*.png &
pngquant -f --ext .png $NAME-extra/images/*/*.png &
wait

python3 $NAME.py apple/${FONT_NAME}_00.ttf &
python3 $NAME.py apple/${FONT_NAME}_01.ttf &
wait

otf2otc $NAME/${FONT_NAME}_00.ttf $NAME/${FONT_NAME}_01.ttf -o $NAME/$NAME.ttc

echo "Output file at $NAME/$NAME.ttc"
