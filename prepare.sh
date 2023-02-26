#!/usr/bin/env bash

set -e

IOS_FONT_NAME=AppleColorEmoji_iOS
WORK_DIR=common

mkdir -p $WORK_DIR
rm -f *.ttx

echo "Extracting font..."
otc2otf $IOS_FONT_NAME.ttc
mv AppleColorEmoji.ttf $WORK_DIR/${IOS_FONT_NAME}_00.ttf
mv .AppleColorEmojiUI.ttf $WORK_DIR/${IOS_FONT_NAME}_01.ttf

cd $WORK_DIR
echo "Extracting tables..."
# Un-shared tables: ['head', 'hhea', 'meta', 'name', 'trak']
UNSHARED_TABLES='-t head -t hhea -t meta -t name -t trak'
SHARED_TABLES='-x GDEF -x DSIG -x cmap -x feat -x glyf -x hmtx -x loca -x maxp -x morx -x post -x sbix -x vhea -x vmtx -x GPOS -x GlyphOrder -x OS/2'
ttx -q -s -f -x DSIG ${IOS_FONT_NAME}_00.ttf &
ttx -q -s -f $SHARED_TABLES ${IOS_FONT_NAME}_01.ttf &
wait -n

echo "Removing unneeded strikes..."
python3 ../remove-strikes.py ${IOS_FONT_NAME}_00._s_b_i_x.ttx

echo "Fixing up interracial emojis..."
python3 ../shift-multi.py ${IOS_FONT_NAME}_00._h_m_t_x.ttx
python3 ../remove-class3.py ${IOS_FONT_NAME}_00.G_D_E_F_.ttx

for ttx in $(find . -type f -name "${IOS_FONT_NAME}_00.*.ttx")
do
    [[ ! -f ${ttx/00/01} ]] && ln $ttx ${ttx/00/01}
done

sed 's/_00/_01/g' ${IOS_FONT_NAME}_00.ttx > ${IOS_FONT_NAME}_01.ttx

echo "Building fonts..."
ttx -q -o ${IOS_FONT_NAME}_00.ttf -b ${IOS_FONT_NAME}_00.ttx &
ttx -q -o ${IOS_FONT_NAME}_01.ttf -b ${IOS_FONT_NAME}_01.ttx &
wait -n

cd ..
