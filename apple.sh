#!/usr/bin/env bash

set -e
trap 'kill $(jobs -p) 2>/dev/null; exit 130' INT TERM
trap 'echo "Error in $(basename "$0") at line $LINENO" >&2' ERR

NAME=apple
MOD=$1
IOS_FONT_NAME=AppleColorEmoji_iOS
[[ $MOD = 'LQ' || $MOD = 'HD-flip' || $MOD = 'pixel' || $MOD = 'EMJC' ]] && ASSETS=$NAME/$MOD || ASSETS=$NAME/Default
COLORS=
[[ $MOD = 'HD' || $MOD = 'HD-flip' || $MOD = 'pixel' || $MOD = 'EMJC' ]] && HD=true || HD=false

echo "Copying PNGs..."
mkdir -p $ASSETS
rm -rf $ASSETS/160 $ASSETS/96 $ASSETS/64 $ASSETS/40
cp -r $NAME/images/* $ASSETS

if [[ $MOD == 'LQ' ]]
then
    COLORS=8
    echo "Applying mod: LQ..."
    mogrify +dither -posterize 8 -normalize $ASSETS/96/*.png &
    mogrify +dither -posterize 8 -normalize $ASSETS/64/*.png &
    mogrify +dither -posterize 8 -normalize $ASSETS/40/*.png &
    wait
elif [[ $MOD == 'HD-flip' ]]
then
    echo "Applying mod: HD-flip..."
    mogrify -flop $ASSETS/160/*.png &
    mogrify -flop $ASSETS/96/*.png &
    mogrify -flop $ASSETS/64/*.png &
    mogrify -flop $ASSETS/40/*.png &
    wait
elif [[ $MOD == 'pixel' ]]
then
    echo "Applying mod: pixel..."
    mogrify -resize 10% -scale 1000% -filter point $ASSETS/160/*.png
    mogrify -resize 96x96 -filter point -path $ASSETS/96 $ASSETS/160/*.png
    mogrify -resize 64x64 -filter point -path $ASSETS/64 $ASSETS/96/*.png
    mogrify -resize 40x40 -filter point -path $ASSETS/40 $ASSETS/64/*.png
fi

echo "Optimizing PNGs..."
pq_pids=()
[[ $HD == true ]] && [[ $MOD != 'LQ' ]] && { ( pngquant --skip-if-larger -f --ext .png $ASSETS/160/*.png || true ) & pq_pids+=($!); }
( pngquant --skip-if-larger $COLORS -f --ext .png $ASSETS/96/*.png || true ) & pq_pids+=($!)
( pngquant --skip-if-larger $COLORS -f --ext .png $ASSETS/64/*.png || true ) & pq_pids+=($!)
( pngquant --skip-if-larger $COLORS -f --ext .png $ASSETS/40/*.png || true ) & pq_pids+=($!)
for pid in "${pq_pids[@]}"; do wait "$pid"; done

ox_pids=()
[[ $HD == true ]] && [[ $MOD != 'LQ' ]] && { oxipng -q $ASSETS/160/*.png & ox_pids+=($!); }
oxipng -q $ASSETS/96/*.png & ox_pids+=($!)
oxipng -q $ASSETS/64/*.png & ox_pids+=($!)
oxipng -q $ASSETS/40/*.png & ox_pids+=($!)
for pid in "${ox_pids[@]}"; do wait "$pid"; done

if [[ $MOD == 'EMJC' ]]; then
    ./convert_to_emjc.sh "$ASSETS"
fi

if [[ $MOD != '' ]]
then
    OUT_FONT_NAME=AppleColorEmoji-$MOD
else
    OUT_FONT_NAME=AppleColorEmoji
    COMPAT_OUT_FONT_NAME=AppleColorEmoji@2x
fi

[[ $HD == true ]] && HD_FLAG="--hd" || HD_FLAG=""
[[ $MOD == 'EMJC' ]] && EMJC_FLAG="--emjc" || EMJC_FLAG=""
uv run emojifonts-apple $HD_FLAG $EMJC_FLAG common/${IOS_FONT_NAME}_00.ttf apple/${OUT_FONT_NAME}_00.ttf $ASSETS &
pid_apple0=$!
uv run emojifonts-apple $HD_FLAG $EMJC_FLAG common/${IOS_FONT_NAME}_01.ttf apple/${OUT_FONT_NAME}_01.ttf $ASSETS &
pid_apple1=$!
wait $pid_apple0
wait $pid_apple1

rm -f apple/$OUT_FONT_NAME.ttf
if [[ $COMPAT_OUT_FONT_NAME != '' ]]
then
    rm -f apple/$COMPAT_OUT_FONT_NAME.ttf
    ln apple/${OUT_FONT_NAME}_00.ttf apple/$COMPAT_OUT_FONT_NAME.ttf
fi

uv run otf2otc apple/${OUT_FONT_NAME}_00.ttf apple/${OUT_FONT_NAME}_01.ttf -o apple/$OUT_FONT_NAME.ttc

if [[ $MOD == 'HD' ]]
then
    rm -f apple/AppleColorEmoji-160px.ttc apple/AppleColorEmoji-160px.ttf
    ln apple/${OUT_FONT_NAME}.ttc apple/AppleColorEmoji-160px.ttc
    ln apple/${OUT_FONT_NAME}_00.ttf apple/AppleColorEmoji-160px.ttf
fi

if [[ $COMPAT_OUT_FONT_NAME != '' ]]
then
    rm -f apple/$COMPAT_OUT_FONT_NAME.ttc
    ln apple/$OUT_FONT_NAME.ttc apple/$COMPAT_OUT_FONT_NAME.ttc
fi

if [[ $MOD != '' && $MOD != 'HD' ]]
then
    rm -f apple/${OUT_FONT_NAME}_00.ttf apple/${OUT_FONT_NAME}_01.ttf
fi
