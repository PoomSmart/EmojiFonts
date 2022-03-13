#!/bin/bash

# to get rsvg-convert, run:
# brew install librsvg

ASSETS=twemoji/images
rm -rf $ASSETS
mkdir -p $ASSETS

# clone twemoji repo alongside this before running the below script
for svg in $(find ../twemoji/assets/svg -type f -name '*.svg')
do
    name=`basename $svg`
    rsvg-convert -a -h 96 $svg > $ASSETS/${name/.svg/.png}
done
