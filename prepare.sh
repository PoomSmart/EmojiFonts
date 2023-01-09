#!/usr/bin/env bash

set -e

FONT_NAME=AppleColorEmoji@2x
WORK_DIR=common

mkdir -p $WORK_DIR

echo "Extracting font..."
./getfonts $FONT_NAME.ttc
mv ${FONT_NAME}_00.ttf $WORK_DIR/
mv ${FONT_NAME}_01.ttf $WORK_DIR/

cd $WORK_DIR
echo "Extracting tables..."
# Un-shared tables: ['head', 'hhea', 'meta', 'name', 'trak']
UNSHARED_TABLES='-t head -t hhea -t meta -t name -t trak'
SHARED_TABLES='-x DSIG -x cmap -x feat -x glyf -x hmtx -x loca -x maxp -x morx -x post -x sbix -x vhea -x vmtx -x GPOS -x GlyphOrder -x OS/2'
ttx -q -s -f -x GDEF -x DSIG ${FONT_NAME}_00.ttf
echo "Extracted 00"
ttx -q -s -f -x GDEF $SHARED_TABLES ${FONT_NAME}_01.ttf
echo "Extracted 01"

echo "Removing unneeded strikes..."
python3 ../remove-strikes.py ${FONT_NAME}_00._s_b_i_x.ttx

echo "Fixing up interracial emojis..."
python3 ../shift-multi.py ${FONT_NAME}_00._h_m_t_x.ttx

for ttx in $(find . -type f -name "${FONT_NAME}_00.*.ttx")
do
    [[ ! -f ${ttx/00/01} ]] && ln $ttx ${ttx/00/01}
done

sed 's/_00/_01/g' ${FONT_NAME}_00.ttx > ${FONT_NAME}_01.ttx

echo "Building fonts..."
ttx -q -o ${FONT_NAME}_00.ttf -b ${FONT_NAME}_00.ttx
echo "Built 00"
ttx -q -o ${FONT_NAME}_01.ttf -b ${FONT_NAME}_01.ttx
echo "Built 01"
cp ${FONT_NAME}_00.ttf ${FONT_NAME}.ttf

cd ..
