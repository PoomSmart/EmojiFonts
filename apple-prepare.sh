#!/usr/bin/env bash

set -e

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
