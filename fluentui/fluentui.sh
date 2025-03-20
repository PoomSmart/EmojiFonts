#!/usr/bin/env bash

set -e

STYLE="$1"

if [ -z "$STYLE" ]; then
    echo "Usage: $0 <Style>"
    echo "Style: Color, Flat, High Contrast"
    exit 1
fi

FONT_NAME=AppleColorEmoji
NAME=fluentui
ASSETS="$STYLE"
MAX_SIZE=96

mkdir -p "$ASSETS"
cd "$ASSETS"
../../image-sizes.sh false
cd ..

echo "Preparing SVGs..."
uv run $NAME-prepare.py ../../fluentui-emoji/assets . "$STYLE"

mv "$ASSETS"/*.svg "$ASSETS"/images/$MAX_SIZE
cd "$ASSETS"/images/$MAX_SIZE

echo "Converting SVGs into PNGs..."
if [ "$STYLE" == 'Color' ]; then
    echo "Optimizing SVGs..."
    svgo -f . &> /dev/null
fi
for svg in $(find . -type f -name '*.svg')
do
    fname=$(basename $svg)
    rsvg-convert -a -h $MAX_SIZE $svg -o ${fname/.svg/.png}
done
rm -f *.svg
cd ../..

echo "Resizing and optimizing PNGs..."
../../resize.sh false false false
cd ..

uv run $NAME.py ../apple/${FONT_NAME}_00.ttf "$STYLE"
uv run $NAME.py ../apple/${FONT_NAME}_01.ttf "$STYLE"

uv run otf2otc "$STYLE"-${FONT_NAME}_00.ttf "$STYLE"-${FONT_NAME}_01.ttf -o $NAME-"$STYLE".ttc
rm -f *_00.ttf *_01.ttf

echo "Output file at $NAME/$NAME-$STYLE.ttc"
