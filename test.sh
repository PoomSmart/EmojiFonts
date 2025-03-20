#!/usr/bin/env bash

set -e

FONT_NAME=AppleColorEmoji

touch .test

cd blobmoji && uv run blobmoji.py ../apple/${FONT_NAME}_00.ttf Blobmoji.ttf Blobmoji.G_S_U_B_.ttx && cd ..
cd facebook && uv run facebook.py ../apple/${FONT_NAME}_00.ttf && cd ..
cd fluentui && uv run fluentui.py ../apple/${FONT_NAME}_00.ttf Flat && cd ..
cd joypixels && uv run joypixels.py ../apple/${FONT_NAME}_00.ttf Default && cd ..
cd noto-emoji && uv run noto-emoji.py ../apple/${FONT_NAME}_00.ttf && cd ..
cd oneui && uv run oneui.py ../apple/${FONT_NAME}_00.ttf NotoColorEmoji.ttf NotoColorEmoji.G_S_U_B_.ttx && cd ..
cd openmoji && uv run openmoji.py ../apple/${FONT_NAME}_00.ttf && cd ..
cd tossface && uv run tossface.py ../apple/${FONT_NAME}_00.ttf TossFaceFontMac.ttf TossFaceFontMac.G_S_U_B_.ttx && cd ..
cd twemoji && uv run twemoji.py ../apple/${FONT_NAME}_00.ttf && cd ..
cd whatsapp && uv run whatsapp.py ../apple/${FONT_NAME}_00.ttf NotoColorEmoji.ttf NotoColorEmoji.G_S_U_B_.ttx && cd ..

rm .test
