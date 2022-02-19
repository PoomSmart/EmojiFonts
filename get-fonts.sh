#!/bin/bash

set -e

rm -f *.ttx
ttx -y 0 -s AppleColorEmoji@2x.ttc
python3 shrink.py AppleColorEmoji@2x._s_b_i_x.ttx
python3 shift-multi.py AppleColorEmoji@2x._h_m_t_x.ttx
ttx -o AppleColorEmoji@2x.ttf -b AppleColorEmoji@2x.ttx

rm -f *.ttx
ttx -y 1 -s AppleColorEmoji@2x.ttc
python3 shrink.py AppleColorEmoji@2x._s_b_i_x.ttx
python3 shift-multi.py AppleColorEmoji@2x._h_m_t_x.ttx
ttx -o AppleColorEmoji@2x#1.ttf -b AppleColorEmoji@2x.ttx

python3 otf2otc.py AppleColorEmoji@2x.ttf AppleColorEmoji@2x#1.ttf -o AppleColorEmoji-out@2x.ttc