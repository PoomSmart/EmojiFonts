#!/bin/bash

ASSETS=twemoji/images
MAX_SIZE=96
rm -rf $ASSETS
mkdir -p $ASSETS

# clone twemoji repo alongside this before running the below script
for svg in $(find ../twemoji/assets/svg -type f -name '*.svg')
do
    name=`basename $svg`
    rsvg-convert -a -h $MAX_SIZE $svg > $ASSETS/${name/.svg/.png}
done

cd twemoji-extra
rm -f *.svg *.png
python3 gen-couple-heart.py
python3 gen-couple-kiss.py
python3 gen-couple-stand.py
python3 gen-handshake.py
for svg in $(find . -type f -name '*.svg')
do
    rsvg-convert -a -h $MAX_SIZE $svg > ${svg/.svg/.png}
done
cd ..