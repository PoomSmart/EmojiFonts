#!/bin/bash

set -e

ASSETS=twemoji/images

./getfonts AppleColorEmoji@2x.ttc
python3 twemoji.py AppleColorEmoji@2x_00.ttf $ASSETS
python3 twemoji.py AppleColorEmoji@2x_01.ttf $ASSETS

python3 otf2otc.py twemoji/AppleColorEmoji@2x_00.ttf twemoji/AppleColorEmoji@2x_01.ttf -o twemoji/twemoji.ttc

echo "Output file at twemoji/twemoji.ttc"
