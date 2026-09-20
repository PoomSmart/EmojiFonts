#!/usr/bin/env bash

set -e
trap 'echo "Error in $(basename "$0") at line $LINENO" >&2' ERR

STYLE="$1"

if [[ "$STYLE" != "2D" && "$STYLE" != "3D" ]]; then
    echo "Usage: $0 <Style>"
    echo "Style: 2D, 3D"
    exit 1
fi

NAME=noto-emoji
MAX_SIZE=160
JOBS=$(nproc 2>/dev/null || sysctl -n hw.logicalcpu)

../image-sizes.sh true

if [[ "$STYLE" == "3D" ]]; then
    ASSETS=../../$NAME/3D/png/512
    echo "Resizing 3D PNGs to ${MAX_SIZE}x${MAX_SIZE}..."
    find "$ASSETS" -maxdepth 1 -name '*.png' -print0 \
        | xargs -0 -P "$JOBS" -I {} bash -c \
        'magick "$1" -resize '"$MAX_SIZE"'x'"$MAX_SIZE"' "images/'"$MAX_SIZE"'/$(basename "$1")"' \
        _ {}
else
    ASSETS=../../$NAME/2D/svg
    FLAG_ASSETS=../../$NAME/third_party/region-flags/waved-svg
    echo "Converting 2D SVGs into PNGs..."
    ../svg-to-png.sh "$ASSETS" $MAX_SIZE
    ../svg-to-png.sh "$FLAG_ASSETS" $MAX_SIZE
fi

cd extra
../../image-sizes.sh true
if [[ "$STYLE" == "3D" ]]; then
    uv run python png/gen-couple-heart.py
    uv run python png/gen-couple-kiss.py
    uv run python png/gen-couple-stand.py
    uv run python png/gen-handshake.py
    uv run python png/gen-bunny-ears.py
    uv run python png/gen-wrestling.py
else
    rm -rf svgs
    mkdir -p svgs
    uv run python gen-couple-heart.py
    uv run python gen-couple-kiss.py
    uv run python gen-couple-stand.py
    uv run python gen-handshake.py
    uv run python gen-bunny-ears.py
    uv run python gen-wrestling.py
    ../../svg-to-png.sh ./svgs $MAX_SIZE
fi
../../resize.sh true false
cd ..

echo "Resizing and optimizing PNGs..."
../resize.sh true false

IN_FONT_NAME=AppleColorEmoji-HD
if [[ "$STYLE" == "3D" ]]; then
    OUT_FONT_NAME=$NAME-3D.ttc
else
    OUT_FONT_NAME=$NAME.ttc
fi

uv run python $NAME.py ../apple/${IN_FONT_NAME}_00.ttf
uv run python $NAME.py ../apple/${IN_FONT_NAME}_01.ttf

uv run otf2otc ${IN_FONT_NAME}_00.ttf ${IN_FONT_NAME}_01.ttf -o $OUT_FONT_NAME
rm -f *_00.ttf *_01.ttf

echo "Output file at $NAME/$OUT_FONT_NAME"
