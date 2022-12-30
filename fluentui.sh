#!/usr/bin/env bash

set -e

FONT_NAME=AppleColorEmoji@2x
NAME=fluentui
STYLE=$1
ASSETS=$NAME/$STYLE
MAX_SIZE=96

rm -rf $ASSETS
mkdir -p $ASSETS

echo "Preparing SVGs..."
python3 $NAME-prepare.py ../$NAME-emoji/assets $NAME $STYLE

cd $ASSETS
echo "Converting SVGs into PNGs..."
if [ $STYLE == 'Color' ]
then
    inkscape --batch-process --export-type=png --export-height=$MAX_SIZE *.svg
else
    for svg in $(find . -type f -name '*.svg')
    do
        fname=$(basename $svg)
        rsvg-convert -a -h $MAX_SIZE $svg -o ${fname/.svg/.png}
    done
fi
rm -f *.svg
cd ../..

python3 $NAME.py common/${FONT_NAME}_00.ttf $ASSETS
python3 $NAME.py common/${FONT_NAME}_01.ttf $ASSETS

python3 otf2otc.py $NAME/${FONT_NAME}_00.ttf $NAME/${FONT_NAME}_01.ttf -o $NAME/$NAME-$STYLE.ttc

echo "Output file at $NAME/$NAME-$STYLE.ttc"
