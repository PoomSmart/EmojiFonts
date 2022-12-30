#!/bin/sh

set -e

FONT_NAME=AppleColorEmoji@2x
NAME=openmoji
MAX_SIZE=96
VERSION=13.1.0
DOWNLOAD=0

rm -rf $NAME
mkdir -p $NAME/images $NAME/svgs
if [ $DOWNLOAD ]
then
    curl -OL https://github.com/hfg-gmuend/openmoji/releases/download/$VERSION/openmoji-svg-color.zip
    unzip openmoji-svg-color.zip -d $NAME/svgs
    rm -f openmoji-svg-color.zip
fi

echo "Converting SVGs into PNGs..."
for svg in $(find $NAME/svgs -type f -name '*.svg')
do
    fname=$(basename $svg)
    rsvg-convert -a -h $MAX_SIZE $svg -o $NAME/images/${fname/.svg/.png}
done

# cd ${NAME}-extra
# rm -f *.svg *.png
# python3 gen-couple-heart.py
# python3 gen-couple-kiss.py
# python3 gen-couple-stand.py
# python3 gen-handshake.py

python3 $NAME.py common/${FONT_NAME}_00.ttf $NAME/images
python3 $NAME.py common/${FONT_NAME}_01.ttf $NAME/images

python3 otf2otc.py $NAME/${FONT_NAME}_00.ttf $NAME/${FONT_NAME}_01.ttf -o $NAME/$NAME.ttc

echo "Output file at $NAME/$NAME.ttc"
