#!/usr/bin/env bash

set -e

NAME=apple
MOD=$1
IOS_FONT_NAME=AppleColorEmoji_iOS
[[ $MOD = 'LQ' || $MOD = 'HD-flip' ]] && ASSETS=$NAME/$MOD || ASSETS=$NAME/Default
COLORS=
[[ $MOD = 'HD' || $MOD = 'HD-flip' ]] && HD=true || HD=false

echo "Copying PNGs..."
mkdir -p $ASSETS
rm -rf $ASSETS/160 $ASSETS/96 $ASSETS/64 $ASSETS/52 $ASSETS/48 $ASSETS/40 $ASSETS/32 $ASSETS/26 $ASSETS/20
cp -r $NAME/images/* $ASSETS

if [[ $MOD == 'LQ' ]]
then
    COLORS=8
    echo "Applying mod: LQ..."
    mogrify +dither -posterize 8 -normalize $ASSETS/96/*.png
    mogrify +dither -posterize 8 -normalize $ASSETS/64/*.png
    mogrify +dither -posterize 8 -normalize $ASSETS/40/*.png
elif [[ $MOD == 'HD-flip' ]]
then
    echo "Applying mod: HD-flip..."
    mogrify -flop $ASSETS/160/*.png
    mogrify -flop $ASSETS/96/*.png
    mogrify -flop $ASSETS/64/*.png
    mogrify -flop $ASSETS/40/*.png
fi

echo "Optimizing PNGs..."
[[ $HD == true ]] && [[ $MOD != 'LQ' ]] && pngquant --skip-if-larger -f --ext .png $ASSETS/160/*.png || true
pngquant --skip-if-larger $COLORS -f --ext .png $ASSETS/96/*.png || true
pngquant --skip-if-larger $COLORS -f --ext .png $ASSETS/64/*.png || true
pngquant --skip-if-larger $COLORS -f --ext .png $ASSETS/40/*.png || true

[[ $HD == true ]] && [[ $MOD != 'LQ' ]] && oxipng -q $ASSETS/160/*.png
oxipng -q $ASSETS/96/*.png
oxipng -q $ASSETS/64/*.png
oxipng -q $ASSETS/40/*.png

if [[ $MOD != '' ]]
then
    OUT_FONT_NAME=AppleColorEmoji-$MOD
else
    OUT_FONT_NAME=AppleColorEmoji
    COMPAT_OUT_FONT_NAME=AppleColorEmoji@2x
fi

python3 $NAME.py $HD common/${IOS_FONT_NAME}_00.ttf apple/${OUT_FONT_NAME}_00.ttf $ASSETS
python3 $NAME.py $HD common/${IOS_FONT_NAME}_01.ttf apple/${OUT_FONT_NAME}_01.ttf $ASSETS

rm -f apple/$OUT_FONT_NAME.ttf
if [[ $COMPAT_OUT_FONT_NAME != '' ]]
then
    ln apple/${OUT_FONT_NAME}_00.ttf apple/$COMPAT_OUT_FONT_NAME.ttf
fi

if [[ $MOD == 'HD' ]]
then
    ln apple/${OUT_FONT_NAME}.ttc apple/AppleColorEmoji-160px.ttc
fi

otf2otc apple/${OUT_FONT_NAME}_00.ttf apple/${OUT_FONT_NAME}_01.ttf -o apple/$OUT_FONT_NAME.ttc
if [[ $COMPAT_OUT_FONT_NAME != '' ]]
then
    [[ -f apple/$COMPAT_OUT_FONT_NAME.ttc ]] && rm -f apple/$COMPAT_OUT_FONT_NAME.ttc
    ln apple/$OUT_FONT_NAME.ttc apple/$COMPAT_OUT_FONT_NAME.ttc
fi

if [[ $MOD != '' && $MOD != 'HD' ]]
then
    rm -f apple/${OUT_FONT_NAME}_00.ttf apple/${OUT_FONT_NAME}_01.ttf
fi
