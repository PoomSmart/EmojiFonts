#!/usr/bin/env bash

set -e
trap 'kill $(jobs -p) 2>/dev/null; exit 130' INT TERM

NAME=apple
KIND=$1
[[ $KIND != 'iOS' && $KIND != 'macOS' ]] && echo "KIND can only be iOS or macOS" && exit 1
IOS_FONT_NAME=AppleColorEmoji_iOS
MAC_FONT_NAME=AppleColorEmoji_$KIND
ASSETS=$NAME/images

mkdir -p $ASSETS
rm -rf $ASSETS/160 $ASSETS/96 $ASSETS/64 $ASSETS/40

echo "Copying sbix table for $MAC_FONT_NAME font..."
cp common/${MAC_FONT_NAME}_00._s_b_i_x.ttx $NAME/${MAC_FONT_NAME}._s_b_i_x.ttx

if [ $KIND != 'iOS' ]
then
    cp common/${IOS_FONT_NAME}_00._s_b_i_x.ttx $NAME/${IOS_FONT_NAME}._s_b_i_x.ttx
fi

echo "Extracting PNGs from $MAC_FONT_NAME font..."
uv run emojifonts-extract $ASSETS $NAME/${IOS_FONT_NAME}._s_b_i_x.ttx $NAME/${MAC_FONT_NAME}._s_b_i_x.ttx

echo "Normalising strikes (filling any missing emojis from other strikes)..."
uv run emojifonts-normalize-strikes $ASSETS

echo "Creating neutral couple silhouette PNGs..."
# Build per-ppem silhouette images for all 26 XY combos:
#   .L.XY  = left half gray  + ML's right-of-center pixels (hand fix),  right in XY colour
#   .R.XY  = right half gray + MR's left-of-center pixels  (hand fix), left in XY colour
sil_pids=()
for ppem_dir in $ASSETS/40 $ASSETS/64 $ASSETS/96 $ASSETS/160; do
    [[ ! -d $ppem_dir ]] && continue
    [[ ! -f $ppem_dir/silhouette.ML.png || ! -f $ppem_dir/silhouette.MR.png ]] && continue
    uv run python3 make_neutral_couple_silhouette.py "$ppem_dir" &
    sil_pids+=($!)
done
for pid in "${sil_pids[@]}"; do wait "$pid"; done

echo "Optimizing silhouette PNGs..."
JOBS=$(sysctl -n hw.logicalcpu)
find "$ASSETS" -maxdepth 2 -name 'silhouette.u1F9D1.u1F91D.*.png' -print0 | \
    xargs -0 -P "$JOBS" -n 1 pngquant --skip-if-larger -f --ext .png || true
find "$ASSETS" -maxdepth 2 -name 'silhouette.u1F9D1.u1F91D.*.png' -print0 | \
    xargs -0 oxipng -q -- || true

echo "Injecting neutral couple silhouette into compiled fonts..."
uv run emojifonts-inject-silhouette $ASSETS common/${IOS_FONT_NAME}_00.ttf &
pid_inj0=$!
uv run emojifonts-inject-silhouette $ASSETS common/${IOS_FONT_NAME}_01.ttf &
pid_inj1=$!
wait $pid_inj0
wait $pid_inj1
