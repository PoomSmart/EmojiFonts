#!/usr/bin/env bash

set -e

IOS_FONT_NAME=AppleColorEmoji_iOS
MAC_FONT_NAME=AppleColorEmoji_macOS
WORK_DIR=common

mkdir -p $WORK_DIR
rm -f *.ttx

echo "Extracting font..."
uv run otc2otf $IOS_FONT_NAME.ttc
mv AppleColorEmoji.ttf $WORK_DIR/${IOS_FONT_NAME}_00.ttf
mv .AppleColorEmojiUI.ttf $WORK_DIR/${IOS_FONT_NAME}_01.ttf

uv run otc2otf $MAC_FONT_NAME.ttc
mv AppleColorEmoji.ttf $WORK_DIR/${MAC_FONT_NAME}_00.ttf
rm .AppleColorEmojiUI.ttf

cd $WORK_DIR
echo "Extracting tables..."
# Un-shared tables: ['head', 'hhea', 'meta', 'name', 'trak', 'cntr']
UNSHARED_TABLES='-t head -t hhea -t meta -t name -t trak -t cntr'
SHARED_TABLES='-x GDEF -x DSIG -x cmap -x feat -x glyf -x hmtx -x loca -x maxp -x morx -x post -x sbix -x vhea -x vmtx -x GPOS -x GlyphOrder -x OS/2'
uv run ttx -q -s -f -x DSIG ${IOS_FONT_NAME}_00.ttf
uv run ttx -q -s -f $SHARED_TABLES ${IOS_FONT_NAME}_01.ttf
uv run ttx -q -s -f -t sbix ${MAC_FONT_NAME}_00.ttf

echo "Fixing up interracial emojis..."
uv run shift-multi ${IOS_FONT_NAME}_00._h_m_t_x.ttx
uv run remove-class3 ${IOS_FONT_NAME}_00.G_D_E_F_.ttx

for ttx in $(find . -type f -name "${IOS_FONT_NAME}_00.*.ttx")
do
    [[ ! -f ${ttx/00/01} ]] && ln $ttx ${ttx/00/01}
done

sed 's/_00/_01/g' ${IOS_FONT_NAME}_00.ttx > ${IOS_FONT_NAME}_01.ttx

echo "Building fonts..."
uv run ttx -q -o ${IOS_FONT_NAME}_00.ttf -b ${IOS_FONT_NAME}_00.ttx
uv run ttx -q -o ${IOS_FONT_NAME}_01.ttf -b ${IOS_FONT_NAME}_01.ttx

cd ..
