#!/bin/bash

set -e

FONT=$1

if [ -z $FONT ];then
    echo "Provide TTF font path"
    exit 1
fi

echo "Extracting tables..."
ttx -q -s -x GDEF $FONT
echo "Fixing up interracial emojis..."
python3 shift-multi.py ${FONT/.ttf/._h_m_t_x.ttx}
echo "Building font..."
ttx -q -o $FONT -b ${FONT/.ttf/.ttx}
