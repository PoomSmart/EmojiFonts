#!/usr/bin/env bash

set -e

STYLE="$1"

if [ -z "$STYLE" ]; then
    echo "Usage: $0 <Style>"
    echo "Style: Color, Flat, High Contrast"
    exit 1
fi

FONT_NAME=AppleColorEmoji@2x
NAME=fluentui
ASSETS="$STYLE"
MAX_SIZE=96

rm -rf "$ASSETS"
mkdir -p "$ASSETS"/96 "$ASSETS"/64 "$ASSETS"/48 "$ASSETS"/40 "$ASSETS"/32 "$ASSETS"/20

echo "Preparing SVGs..."
python3 $NAME-prepare.py ../../fluentui-emoji/assets . "$STYLE"

mv "$ASSETS"/*.svg "$ASSETS"/$MAX_SIZE
cd "$ASSETS"/$MAX_SIZE

echo "Converting SVGs into PNGs..."
[[ "$STYLE" == 'Color' ]] && svgo -f . &> /dev/null
for svg in $(find . -type f -name '*.svg')
do
    fname=$(basename $svg)
    rsvg-convert -a -h $MAX_SIZE $svg -o ${fname/.svg/.png}
done
rm -f *.svg
cd ../..

echo "Resizing PNGs..."
mogrify -resize 64x64 -path "$ASSETS"/64 "$ASSETS"/96/*.png
mogrify -resize 40x40 -path "$ASSETS"/40 "$ASSETS"/64/*.png
# mogrify -resize 48x48 -path "$ASSETS"/48 "$ASSETS"/64/*.png
# mogrify -resize 40x40 -path "$ASSETS"/40 "$ASSETS"/48/*.png
# mogrify -resize 32x32 -path "$ASSETS"/32 "$ASSETS"/40/*.png
# mogrify -resize 20x20 -path "$ASSETS"/20 "$ASSETS"/32/*.png

echo "Optimizing PNGs..."
pngquant --skip-if-larger -f --ext .png "$ASSETS"/96/*.png &
pngquant --skip-if-larger -f --ext .png "$ASSETS"/64/*.png &
# pngquant --skip-if-larger -f --ext .png "$ASSETS"/48/*.png &
pngquant --skip-if-larger -f --ext .png "$ASSETS"/40/*.png &
# pngquant --skip-if-larger -f --ext .png "$ASSETS"/32/*.png &
# pngquant --skip-if-larger -f --ext .png "$ASSETS"/20/*.png &
wait
oxipng -q "$ASSETS"/96/*.png &
oxipng -q "$ASSETS"/64/*.png &
oxipng -q "$ASSETS"/40/*.png &
wait

python3 $NAME.py ../apple/${FONT_NAME}_00.ttf "$STYLE" &
python3 $NAME.py ../apple/${FONT_NAME}_01.ttf "$STYLE" &
wait

otf2otc "$STYLE"-${FONT_NAME}_00.ttf "$STYLE"-${FONT_NAME}_01.ttf -o $NAME-"$STYLE".ttc

echo "Output file at $NAME/$NAME-$STYLE.ttc"
