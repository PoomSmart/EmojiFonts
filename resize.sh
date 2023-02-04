#!/usr/bin/env bash

set -e

HD=$1
FULL=$2
[[ $3 = true ]] && COLORS=256 || COLORS=

if [[ $HD = true ]]; then
    mogrify -resize 160x160 images/160/*.png
    pngquant --skip-if-larger $COLORS -f --ext .png images/160/*.png &
    mogrify -resize 96x96 -path images/96 images/160/*.png
    pngquant --skip-if-larger $COLORS -f --ext .png images/96/*.png &
fi
if $FULL; then
    mogrify -resize 64x64 -path images/64 images/96/*.png
    pngquant --skip-if-larger $COLORS -f --ext .png images/64/*.png &
    mogrify -resize 48x48 -path images/48 images/64/*.png
    pngquant --skip-if-larger $COLORS -f --ext .png images/48/*.png &
    mogrify -resize 40x40 -path images/40 images/48/*.png
    pngquant --skip-if-larger $COLORS -f --ext .png images/40/*.png &
    mogrify -resize 32x32 -path images/32 images/40/*.png
    pngquant --skip-if-larger $COLORS -f --ext .png images/32/*.png &
    mogrify -resize 20x20 -path images/20 images/32/*.png
    pngquant --skip-if-larger $COLORS -f --ext .png images/20/*.png &
else
    mogrify -resize 64x64 -path images/64 images/96/*.png
    pngquant --skip-if-larger $COLORS -f --ext .png images/64/*.png &
    mogrify -resize 40x40 -path images/40 images/64/*.png
    pngquant --skip-if-larger $COLORS -f --ext .png images/40/*.png &
fi
wait

oxipng -q images/*/*.png
