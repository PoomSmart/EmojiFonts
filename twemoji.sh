#!/bin/bash

set -e

rm -rf twemoji
mkdir -p twemoji/images

ASSETS=twemoji/images

# for svg in $(find ../twemoji/assets/svg -type f -name '*.svg')
# do
#     name=`basename $svg`
#     rsvg-convert -a -h 160 $svg > $ASSETS/${name/.svg/.png}
# done

./getfonts AppleColorEmoji@2x.ttc
python3 twemoji.py AppleColorEmoji@2x_00.ttf $ASSETS
python3 twemoji.py AppleColorEmoji@2x_01.ttf $ASSETS

python3 otf2otc.py twemoji/AppleColorEmoji@2x_00.ttf twemoji/AppleColorEmoji@2x_01.ttf -o twemoji/twemoji.ttc
