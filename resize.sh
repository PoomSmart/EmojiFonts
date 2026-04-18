#!/usr/bin/env bash

set -e
trap 'kill $(jobs -p) 2>/dev/null; exit 130' INT TERM
trap 'echo "Error in $(basename "$0") at line $LINENO" >&2' ERR

HD=$1
[[ $2 = true ]] && COLORS=256 || COLORS=
[[ $3 = true ]] && RESIZE_96=true || RESIZE_96=false

JOBS=$(nproc 2>/dev/null || sysctl -n hw.logicalcpu)

pngquant_dir() {
    find "$1" -maxdepth 1 -name '*.png' -print0 \
        | xargs -0 -P "$JOBS" -n 1 pngquant --skip-if-larger $COLORS -f --ext .png || true
}

resize_dir() {
    local src="$1" dst="$2" size="$3"
    find "$src" -maxdepth 1 -name '*.png' -print0 \
        | xargs -0 -P "$JOBS" -I {} bash -c 'magick "$1" -resize '"$size"' "'"$dst"'/$(basename "$1")"' _ {}
}

if [[ $HD = true ]]; then
    pngquant_dir images/160
    resize_dir images/160 images/96 96x96
    pngquant_dir images/96
fi

if [[ $RESIZE_96 = true ]]; then
    find images/96 -maxdepth 1 -name '*.png' -print0 | xargs -0 -P "$JOBS" -I {} magick {} -resize 96x96 {}
fi
pngquant_dir images/96
resize_dir images/96 images/64 64x64
pngquant_dir images/64
resize_dir images/64 images/40 40x40
pngquant_dir images/40

oxipng -q images/*/*.png
