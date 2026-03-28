#!/usr/bin/env bash

set -e

HD=$1
[[ $2 = true ]] && COLORS=256 || COLORS=
[[ $3 = true ]] && RESIZE_96=true || RESIZE_96=false

JOBS=$(sysctl -n hw.logicalcpu)

if [[ $HD = true ]]; then
    find images/160 -maxdepth 1 -name '*.png' -print0 | xargs -0 -P "$JOBS" -n 1 pngquant --skip-if-larger $COLORS -f --ext .png || true
    find images/160 -maxdepth 1 -name '*.png' -print0 | \
        xargs -0 -P "$JOBS" -I {} bash -c 'magick "$1" -resize 96x96 "images/96/$(basename "$1")"' _ {}
    find images/96 -maxdepth 1 -name '*.png' -print0 | xargs -0 -P "$JOBS" -n 1 pngquant --skip-if-larger $COLORS -f --ext .png || true
fi

if [[ $RESIZE_96 = true ]]; then
    find images/96 -maxdepth 1 -name '*.png' -print0 | xargs -0 -P "$JOBS" -I {} magick {} -resize 96x96 {}
fi
find images/96 -maxdepth 1 -name '*.png' -print0 | xargs -0 -P "$JOBS" -n 1 pngquant --skip-if-larger $COLORS -f --ext .png || true
find images/96 -maxdepth 1 -name '*.png' -print0 | \
    xargs -0 -P "$JOBS" -I {} bash -c 'magick "$1" -resize 64x64 "images/64/$(basename "$1")"' _ {}
find images/64 -maxdepth 1 -name '*.png' -print0 | xargs -0 -P "$JOBS" -n 1 pngquant --skip-if-larger $COLORS -f --ext .png || true
find images/64 -maxdepth 1 -name '*.png' -print0 | \
    xargs -0 -P "$JOBS" -I {} bash -c 'magick "$1" -resize 40x40 "images/40/$(basename "$1")"' _ {}
find images/40 -maxdepth 1 -name '*.png' -print0 | xargs -0 -P "$JOBS" -n 1 pngquant --skip-if-larger $COLORS -f --ext .png || true

oxipng -q images/*/*.png
