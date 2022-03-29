#!/bin/bash

set -e

STEPS=11

echo "[0/${STEPS}] This is going to take a while. You should grab your drink, or optimize the code (PR would be welcome), or both."

rm -f *.ttx
echo "[1/${STEPS}] Extracting tables from AppleColorEmoji font..."
ttx -q -y 0 -s -x GDEF AppleColorEmoji@2x.ttc
echo "[2/${STEPS}] Removing unneeded strikes..."
python3 remove-strikes.py AppleColorEmoji@2x._s_b_i_x.ttx
echo "[3/${STEPS}] Stripping image data..."
echo "Skipped by default, edit this script if you want to optimize the image data."
# python3 strip.py AppleColorEmoji@2x._s_b_i_x.ttx
echo "[4/${STEPS}] Fixing up interracial emojis..."
python3 shift-multi.py AppleColorEmoji@2x._h_m_t_x.ttx
echo "[5/${STEPS}] Building AppleColorEmoji TTF (AppleColorEmoji@2x.ttf)..."
ttx -q -o AppleColorEmoji@2x.ttf -b AppleColorEmoji@2x.ttx

rm -f *.ttx
echo "[6/${STEPS}] Extracting tables from .AppleColorEmojiUI font..."
ttx -q -y 1 -s -x GDEF AppleColorEmoji@2x.ttc
echo "[7/${STEPS}] Removing strikes..."
python3 remove-strikes.py AppleColorEmoji@2x._s_b_i_x.ttx
echo "[8/${STEPS}] Stripping image data..."
echo "Skipped by default, edit this script if you want to optimize the image data."
# python3 strip.py AppleColorEmoji@2x._s_b_i_x.ttx
echo "[9/${STEPS}] Fixing up interracial emojis..."
python3 shift-multi.py AppleColorEmoji@2x._h_m_t_x.ttx
echo "[10/${STEPS}] Building .AppleColorEmojiUI TTF (AppleColorEmoji@2x#1.ttf)..."
ttx -q -o AppleColorEmoji@2x#1.ttf -b AppleColorEmoji@2x.ttx

echo "[11/${STEPS}] Combining TTFs into TTC..."
python3 otf2otc.py AppleColorEmoji@2x.ttf AppleColorEmoji@2x#1.ttf -o AppleColorEmoji-out@2x.ttc

echo "Output files: AppleColorEmoji@2x.ttf and AppleColorEmoji-out@2x.ttc"