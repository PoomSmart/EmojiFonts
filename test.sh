#!/usr/bin/env bash

set -e

FONT_NAME=AppleColorEmoji@2x

touch .test

cd blobmoji && python3 blobmoji.py ../apple/${FONT_NAME}_00.ttf Blobmoji.ttf Blobmoji.G_S_U_B_.ttx && cd ..
cd facebook && python3 facebook.py ../apple/${FONT_NAME}_00.ttf && cd ..
cd fluentui && python3 fluentui.py ../apple/${FONT_NAME}_00.ttf Flat && cd ..
cd joypixels && python3 joypixels.py ../apple/${FONT_NAME}_00.ttf Default && cd ..
cd noto-emoji && python3 noto-emoji.py false ../apple/${FONT_NAME}_00.ttf && cd ..
cd oneui && python3 oneui.py ../apple/${FONT_NAME}_00.ttf NotoColorEmoji.ttf NotoColorEmoji.G_S_U_B_.ttx && cd ..
cd openmoji && python3 openmoji.py false ../apple/${FONT_NAME}_00.ttf && cd ..
cd twemoji && python3 twemoji.py false ../apple/${FONT_NAME}_00.ttf && cd ..
cd whatsapp && python3 whatsapp.py ../apple/${FONT_NAME}_00.ttf NotoColorEmoji.ttf NotoColorEmoji.G_S_U_B_.ttx && cd ..

rm .test