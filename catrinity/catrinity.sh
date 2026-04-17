#!/usr/bin/env bash

set -e

NAME=catrinity
MAX_SIZE=160

../image-sizes.sh true

echo "Rendering Catrinity COLR glyphs to SVGs..."
rm -rf svgs
mkdir -p svgs
uv run python catrinity_render.py --out svgs

echo "Converting SVGs into PNGs..."
../svg-to-png.sh svgs $MAX_SIZE

echo "Resizing and optimizing PNGs..."
../resize.sh true false

echo "Generating extra composites..."
cd extra
uv run python gen-couple-stand.py
uv run python gen-couple-heart.py
uv run python gen-couple-kiss.py
uv run python gen-bunny-ears.py
uv run python gen-wrestling.py
cd ..
uv run python extra/gen-couple-nn.py

IN_FONT_NAME=AppleColorEmoji-HD
OUT_FONT_NAME=$NAME.ttc

uv run python $NAME.py ../apple/${IN_FONT_NAME}_00.ttf
uv run python $NAME.py ../apple/${IN_FONT_NAME}_01.ttf

uv run otf2otc ${IN_FONT_NAME}_00.ttf ${IN_FONT_NAME}_01.ttf -o $OUT_FONT_NAME
rm -f *_00.ttf *_01.ttf

echo "Output file at $NAME/$OUT_FONT_NAME"
