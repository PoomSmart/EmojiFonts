#!/usr/bin/env bash

set -e

HD=$1
[[ $2 = true ]] && COLORS=256 || COLORS=
[[ $3 = true ]] && RESIZE_96=true || RESIZE_96=false

if [[ $HD = true ]]; then
    pngquant --skip-if-larger $COLORS -f --ext .png images/160/*.png || true
    mogrify -resize 96x96 -path images/96 images/160/*.png
    pngquant --skip-if-larger $COLORS -f --ext .png images/96/*.png || true
fi

[[ $RESIZE_96 = true ]] && mogrify -resize 96x96 images/96/*.png
pngquant --skip-if-larger $COLORS -f --ext .png images/96/*.png || true
mogrify -resize 64x64 -path images/64 images/96/*.png
pngquant --skip-if-larger $COLORS -f --ext .png images/64/*.png || true
mogrify -resize 40x40 -path images/40 images/64/*.png
pngquant --skip-if-larger $COLORS -f --ext .png images/40/*.png || true

oxipng -q images/*/*.png
