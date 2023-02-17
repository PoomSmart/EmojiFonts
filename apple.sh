#!/usr/bin/env bash

set -e

NAME=apple
IOS_FONT_NAME=AppleColorEmoji_iOS
MAC_FONT_NAME=AppleColorEmoji_macOS
ASSETS=$NAME
MOD=$1
COLORS=
[[ $MOD = 'HD' ]] && HD=true || HD=false

mkdir -p $ASSETS
rm -rf $ASSETS/160 $ASSETS/96 $ASSETS/64 $ASSETS/52 $ASSETS/48 $ASSETS/40 $ASSETS/32 $ASSETS/26 $ASSETS/20

echo "Extracting sbix table from $MAC_FONT_NAME font..."
ttx -q -s -f -y 0 -t sbix ${MAC_FONT_NAME}.ttc

echo "Extracting PNGs from $MAC_FONT_NAME font..."
python3 remove-strikes.py ${MAC_FONT_NAME}._s_b_i_x.ttx
python3 extractor.py $NAME ${MAC_FONT_NAME}._s_b_i_x.ttx

if [[ $MOD == 'LQ' ]]
then
    COLORS=8
    echo "Applying mod: LQ..."
    mogrify +dither -posterize 8 -normalize $ASSETS/96/*.png &
    mogrify +dither -posterize 8 -normalize $ASSETS/64/*.png &
    mogrify +dither -posterize 8 -normalize $ASSETS/40/*.png &
    wait
fi

echo "Optimizing PNGs..."
[[ $HD == true ]] && pngquant --skip-if-larger -f --ext .png $ASSETS/160/*.png || true
pngquant --skip-if-larger $COLORS -f --ext .png $ASSETS/96/*.png || true
pngquant --skip-if-larger $COLORS -f --ext .png $ASSETS/64/*.png || true
pngquant --skip-if-larger $COLORS -f --ext .png $ASSETS/40/*.png || true

[[ $HD == true ]] && oxipng -q $ASSETS/160/*.png &
oxipng -q $ASSETS/96/*.png &
oxipng -q $ASSETS/64/*.png &
oxipng -q $ASSETS/40/*.png &
wait

if [[ $MOD != '' ]]
then
    OUT_FONT_NAME=AppleColorEmoji-$MOD
else
    OUT_FONT_NAME=AppleColorEmoji@2x
fi

python3 $NAME.py $HD common/${IOS_FONT_NAME}_00.ttf apple/${OUT_FONT_NAME}_00.ttf $ASSETS &
python3 $NAME.py $HD common/${IOS_FONT_NAME}_01.ttf apple/${OUT_FONT_NAME}_01.ttf $ASSETS &
wait
rm -f apple/$OUT_FONT_NAME.ttf
ln apple/${OUT_FONT_NAME}_00.ttf apple/$OUT_FONT_NAME.ttf

otf2otc apple/${OUT_FONT_NAME}_00.ttf apple/${OUT_FONT_NAME}_01.ttf -o apple/$OUT_FONT_NAME.ttc
