#!/usr/bin/env bash

set -e

FONT_NAME=AppleColorEmoji@2x
NAME=fluentui
STYLE="$1"
ASSETS="$NAME/$STYLE"
MAX_SIZE=96

rm -rf "$ASSETS"
mkdir -p "$ASSETS"/96 "$ASSETS"/64 "$ASSETS"/48 "$ASSETS"/40 "$ASSETS"/32 "$ASSETS"/20

echo "Preparing SVGs..."
python3 $NAME-prepare.py ../$NAME-emoji/assets $NAME "$STYLE"

mv "$ASSETS"/*.svg "$ASSETS"/96
cd "$ASSETS"/96
echo "Converting SVGs into PNGs..."
if [ "$STYLE" == 'Color' ]
then
    echo "This will take a while..."
    inkscape --batch-process --export-type=png --export-height=$MAX_SIZE *.svg &> /dev/null
else
    for svg in $(find . -type f -name '*.svg')
    do
        fname=$(basename $svg)
        rsvg-convert -a -h $MAX_SIZE $svg -o ${fname/.svg/.png} &
    done
    wait
fi
rm -f *.svg
cd ../../..

echo "Resizing PNGs..."
mogrify -resize 64x64 -path "$ASSETS"/64 "$ASSETS"/96/*.png
mogrify -resize 40x40 -path "$ASSETS"/40 "$ASSETS"/64/*.png
# mogrify -resize 48x48 -path "$ASSETS"/48 "$ASSETS"/64/*.png
# mogrify -resize 40x40 -path "$ASSETS"/40 "$ASSETS"/48/*.png
# mogrify -resize 32x32 -path "$ASSETS"/32 "$ASSETS"/40/*.png
# mogrify -resize 20x20 -path "$ASSETS"/20 "$ASSETS"/32/*.png

echo "Optimizing PNGs..."
pngquant -f --ext .png "$ASSETS"/96/*.png &
pngquant -f --ext .png "$ASSETS"/64/*.png &
# pngquant -f --ext .png "$ASSETS"/48/*.png &
pngquant -f --ext .png "$ASSETS"/40/*.png &
# pngquant -f --ext .png "$ASSETS"/32/*.png &
# pngquant -f --ext .png "$ASSETS"/20/*.png &
wait
oxipng -q "$ASSETS"/96/*.png &
oxipng -q "$ASSETS"/64/*.png &
oxipng -q "$ASSETS"/40/*.png &
wait

python3 $NAME.py apple/${FONT_NAME}_00.ttf "$STYLE" &
python3 $NAME.py apple/${FONT_NAME}_01.ttf "$STYLE" &
wait

otf2otc $NAME/"$STYLE"-${FONT_NAME}_00.ttf $NAME/"$STYLE"-${FONT_NAME}_01.ttf -o $NAME/$NAME-"$STYLE".ttc

echo "Output file at $NAME/$NAME-$STYLE.ttc"
