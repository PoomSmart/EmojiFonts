#!/usr/bin/env bash

set -e

HD=$1
FULL=$2
[[ $3 = true ]] && COLORS=256 || COLORS=
[[ $4 = true ]] && RESIZE_96=true || RESIZE_96=false

if [[ $HD = true ]]; then
    pngquant --skip-if-larger $COLORS -f --ext .png images/160/*.png || true
    mogrify -resize 96x96 -path images/96 images/160/*.png
    pngquant --skip-if-larger $COLORS -f --ext .png images/96/*.png || true
fi
if $FULL; then
    pngquant --skip-if-larger $COLORS -f --ext .png images/96/*.png || true
    mogrify -resize 64x64 -path images/64 images/96/*.png
    pngquant --skip-if-larger $COLORS -f --ext .png images/64/*.png || true
    mogrify -resize 48x48 -path images/48 images/64/*.png
    pngquant --skip-if-larger $COLORS -f --ext .png images/48/*.png || true
    mogrify -resize 40x40 -path images/40 images/48/*.png
    pngquant --skip-if-larger $COLORS -f --ext .png images/40/*.png || true
    mogrify -resize 32x32 -path images/32 images/40/*.png
    pngquant --skip-if-larger $COLORS -f --ext .png images/32/*.png || true
    mogrify -resize 20x20 -path images/20 images/32/*.png
    pngquant --skip-if-larger $COLORS -f --ext .png images/20/*.png || true
else
    [[ $RESIZE_96 = true ]] && mogrify -resize 96x96 images/96/*.png
    pngquant --skip-if-larger $COLORS -f --ext .png images/96/*.png || true
    mogrify -resize 64x64 -path images/64 images/96/*.png
    pngquant --skip-if-larger $COLORS -f --ext .png images/64/*.png || true
    mogrify -resize 40x40 -path images/40 images/64/*.png
    pngquant --skip-if-larger $COLORS -f --ext .png images/40/*.png || true
fi

oxipng -q images/*/*.png
