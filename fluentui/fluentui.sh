#!/usr/bin/env bash

set -e
trap 'echo "Error in $(basename "$0") at line $LINENO" >&2' ERR

STYLE="$1"

if [ -z "$STYLE" ]; then
    echo "Usage: $0 <Style>"
    echo "Style: Color, Flat, High Contrast"
    exit 1
fi

FONT_NAME=AppleColorEmoji-HD
NAME=fluentui
ASSETS="$STYLE"
MAX_SIZE=160
SVG_TO_PNG="$(cd "$(dirname "$0")" && pwd)/../svg-to-png.sh"

mkdir -p "$ASSETS"
cd "$ASSETS"
../../image-sizes.sh true
cd ..

echo "Preparing SVGs..."
uv run python $NAME-prepare.py ../../fluentui-emoji/assets . "$STYLE"

mv "$ASSETS"/*.svg "$ASSETS"/images/$MAX_SIZE
cd "$ASSETS"/images/$MAX_SIZE

echo "Converting SVGs into PNGs..."
if [ "$STYLE" == 'Color' ]; then
    echo "Optimizing SVGs..."
    svgo -f . &> /dev/null
fi
"$SVG_TO_PNG" . $MAX_SIZE .
rm -f *.svg
cd ../..

echo "Resizing and optimizing PNGs..."
../../resize.sh true false
cd ..

uv run python $NAME.py ../apple/${FONT_NAME}_00.ttf "$STYLE"
uv run python $NAME.py ../apple/${FONT_NAME}_01.ttf "$STYLE"

uv run otf2otc "$STYLE"-${FONT_NAME}_00.ttf "$STYLE"-${FONT_NAME}_01.ttf -o $NAME-"$STYLE".ttc
rm -f *_00.ttf *_01.ttf

echo "Output file at $NAME/$NAME-$STYLE.ttc"
