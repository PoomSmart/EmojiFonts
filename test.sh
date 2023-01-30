#!/usr/bin/env bash

set -e

FONT_NAME=AppleColorEmoji@2x

python3 blobmoji.py apple/${FONT_NAME}_00.ttf blobmoji/Blobmoji.ttf blobmoji/Blobmoji.G_S_U_B_.ttx
python3 facebook.py apple/${FONT_NAME}_00.ttf
python3 fluentui.py apple/${FONT_NAME}_00.ttf Flat
python3 joypixels.py apple/${FONT_NAME}_00.ttf
python3 noto-emoji.py false apple/${FONT_NAME}_00.ttf
python3 oneui.py apple/${FONT_NAME}_00.ttf oneui/NotoColorEmoji.ttf oneui/NotoColorEmoji.G_S_U_B_.ttx
python3 openmoji.py false apple/${FONT_NAME}_00.ttf
python3 twemoji.py false apple/${FONT_NAME}_00.ttf
python3 whatsapp.py apple/${FONT_NAME}_00.ttf whatsapp/NotoColorEmoji.ttf whatsapp/NotoColorEmoji.G_S_U_B_.ttx
