#!/usr/bin/env bash

set -e

NAME=$1
HD=$2
FULL=$3
COLORS=
[[ $4 = true ]] && COLORS=256


if [[ $HD = true ]]; then
    mogrify -resize 160x160 $NAME/images/160/*.png
    pngquant $COLORS -f --ext .png $NAME/images/160/*.png &
    mogrify -resize 96x96 -path $NAME/images/96 $NAME/images/160/*.png
    pngquant $COLORS -f --ext .png $NAME/images/96/*.png &
fi
if $FULL; then
    mogrify -resize 64x64 -path $NAME/images/64 $NAME/images/96/*.png
    pngquant $COLORS -f --ext .png $NAME/images/64/*.png &
    mogrify -resize 48x48 -path $NAME/images/48 $NAME/images/64/*.png
    pngquant $COLORS -f --ext .png $NAME/images/48/*.png &
    mogrify -resize 40x40 -path $NAME/images/40 $NAME/images/48/*.png
    pngquant $COLORS -f --ext .png $NAME/images/40/*.png &
    mogrify -resize 32x32 -path $NAME/images/32 $NAME/images/40/*.png
    pngquant $COLORS -f --ext .png $NAME/images/32/*.png &
    mogrify -resize 20x20 -path $NAME/images/20 $NAME/images/32/*.png
    pngquant $COLORS -f --ext .png $NAME/images/20/*.png &
else
    mogrify -resize 64x64 -path $NAME/images/64 $NAME/images/96/*.png
    pngquant $COLORS -f --ext .png $NAME/images/64/*.png &
    mogrify -resize 40x40 -path $NAME/images/40 $NAME/images/64/*.png
    pngquant $COLORS -f --ext .png $NAME/images/40/*.png &
fi
wait

echo "Optimizing PNGs using oxipng..."
oxipng -q $NAME/images/*/*.png
