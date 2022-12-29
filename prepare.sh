#!/usr/bin/env bash

FONT_NAME=AppleColorEmoji@2x
WORK_DIR=common

mkdir -p $WORK_DIR

./getfonts $FONT_NAME.ttc
mv ${FONT_NAME}_00.ttf $WORK_DIR/
mv ${FONT_NAME}_01.ttf $WORK_DIR/

cd $WORK_DIR
echo "Extracting tables..."
# Un-shared tables: ['head', 'hhea', 'meta', 'name', 'trak']
rm -f *.ttx
ttx -q -s -x GDEF ${FONT_NAME}_00.ttf
ttx -q -s -x GDEF ${FONT_NAME}_01.ttf

echo "Removing unneeded strikes..."
python3 ../remove-strikes.py ${FONT_NAME}_00._s_b_i_x.ttx
python3 ../remove-strikes.py ${FONT_NAME}_01._s_b_i_x.ttx

echo "Fixing up interracial emojis..."
python3 ../shift-multi.py ${FONT_NAME}_00._h_m_t_x.ttx
python3 ../shift-multi.py ${FONT_NAME}_01._h_m_t_x.ttx

echo "Building fonts..."
ttx -q -o ${FONT_NAME}_00.ttf -b ${FONT_NAME}_00.ttx
ttx -q -o ${FONT_NAME}_01.ttf -b ${FONT_NAME}_01.ttx
cp ${FONT_NAME}_00.ttf ${FONT_NAME}.ttf

cd ..