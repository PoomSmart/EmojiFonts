#!/usr/bin/env bash

set -e

FONT_NAME=AppleColorEmoji@2x
NAME=noto-emoji
ASSETS=../../$NAME/svg
FLAG_ASSETS=../../$NAME/third_party/region-flags/waved-svg
MAX_SIZE=96
[[ $1 == 'HD' ]] && HD=true || HD=false

[[ $HD = true ]] && MAX_SIZE=160

rm -rf images
mkdir -p images/160 images/96 images/64 images/48 images/40 images/32 images/20

echo "Converting SVGs into PNGs..."
for svg in $(find $ASSETS -type f -name '*.svg')
do
    fname=$(basename $svg)
    rsvg-convert -a -h $MAX_SIZE $svg -o images/$MAX_SIZE/${fname/.svg/.png} &
done
wait
for svg in $(find $FLAG_ASSETS -type f -name '*.svg')
do
    fname=$(basename $svg)
    rsvg-convert -a -h $MAX_SIZE $svg -o images/$MAX_SIZE/${fname/.svg/.png} &
done
wait

cd extra
rm -rf svgs images
mkdir -p svgs images/160 images/96 images/64 images/48 images/40 images/32 images/20
python3 gen-couple-heart.py
python3 gen-couple-kiss.py
python3 gen-couple-stand.py
python3 gen-handshake.py
for svg in $(find ./svgs -type f -name '*.svg')
do
    fname=$(basename $svg)
    rsvg-convert -a -h $MAX_SIZE $svg -o images/$MAX_SIZE/${fname/.svg/.png} &
done
wait
../../resize.sh $HD false false
cd ..

echo "Resizing and optimizing PNGs..."
../resize.sh $HD false false

if [[ $HD = true ]]; then
    IN_FONT_NAME=AppleColorEmoji-HD
    OUT_FONT_NAME=$NAME-HD.ttc
else
    IN_FONT_NAME=$FONT_NAME
    OUT_FONT_NAME=$NAME.ttc
fi

python3 $NAME.py $HD ../apple/${IN_FONT_NAME}_00.ttf &
python3 $NAME.py $HD ../apple/${IN_FONT_NAME}_01.ttf &
wait

otf2otc ${IN_FONT_NAME}_00.ttf ${IN_FONT_NAME}_01.ttf -o $OUT_FONT_NAME

echo "Output file at $NAME/$OUT_FONT_NAME"
