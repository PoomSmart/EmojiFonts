#!/usr/bin/env bash

set -e

FONT_NAME=AppleColorEmoji@2x
NAME=facebook
ASSETS=../../facebook-emojis/images/96

rm -rf images
mkdir -p images/96 images/64 images/48 images/40 images/32 images/20

rm -rf extra/images
mkdir -p extra/images/96 extra/images/64 extra/images/48 extra/images/40 extra/images/32 extra/images/20

cp -r $ASSETS/ images/96

cp extra/original/*.png extra/images/96
../get-assets.sh facebook

echo "Resizing PNGs..."
mogrify -resize 64x64 -path images/64 images/96/*.png
mogrify -resize 40x40 -path images/40 images/64/*.png
# mogrify -resize 48x48 -path images/48 images/64/*.png
# mogrify -resize 40x40 -path images/40 images/48/*.png
# mogrify -resize 32x32 -path images/32 images/40/*.png
# mogrify -resize 20x20 -path images/20 images/32/*.png

mogrify -resize 64x64 -path extra/images/64 extra/images/96/*.png
mogrify -resize 40x40 -path extra/images/40 extra/images/64/*.png
# mogrify -resize 48x48 -path extra/images/48 extra/images/64/*.png
# mogrify -resize 40x40 -path extra/images/40 extra/images/48/*.png
# mogrify -resize 32x32 -path extra/images/32 extra/images/40/*.png
# mogrify -resize 20x20 -path extra/images/20 extra/images/32/*.png

echo "Optimizing PNGs..."
pngquant --skip-if-larger -f --ext .png images/96/*.png &
pngquant --skip-if-larger -f --ext .png images/64/*.png &
# pngquant --skip-if-larger -f --ext .png images/48/*.png &
pngquant --skip-if-larger -f --ext .png images/40/*.png &
# pngquant --skip-if-larger -f --ext .png images/32/*.png &
# pngquant --skip-if-larger -f --ext .png images/20/*.png &
pngquant --skip-if-larger -f --ext .png extra/images/*/*.png &
wait || true
oxipng -q images/96/*.png &
oxipng -q images/64/*.png &
oxipng -q images/40/*.png &
oxipng -q extra/images/*/*.png &
wait

python3 $NAME.py ../apple/${FONT_NAME}_00.ttf &
python3 $NAME.py ../apple/${FONT_NAME}_01.ttf &
wait

otf2otc ${FONT_NAME}_00.ttf ${FONT_NAME}_01.ttf -o $NAME.ttc

echo "Output file at $NAME/$NAME.ttc"
