#!/usr/bin/env bash

set -e

FONT_NAME=AppleColorEmoji

touch .test

cd blobmoji && uv run python blobmoji.py ../apple/${FONT_NAME}_00.ttf Blobmoji.ttf Blobmoji.G_S_U_B_.ttx && cd ..
cd facebook && uv run python facebook.py ../apple/${FONT_NAME}_00.ttf && cd ..
cd fluentui && uv run python fluentui.py ../apple/${FONT_NAME}_00.ttf Flat && cd ..
cd joypixels && uv run python joypixels.py ../apple/${FONT_NAME}_00.ttf Default && cd ..
cd noto-emoji && uv run python noto-emoji.py ../apple/${FONT_NAME}_00.ttf && cd ..
cd oneui && uv run python oneui.py ../apple/${FONT_NAME}_00.ttf NotoColorEmoji.ttf NotoColorEmoji.G_S_U_B_.ttx && cd ..
cd openmoji && uv run python openmoji.py ../apple/${FONT_NAME}_00.ttf && cd ..
cd tossface && uv run python tossface.py ../apple/${FONT_NAME}_00.ttf TossFaceFontMac.ttf TossFaceFontMac.G_S_U_B_.ttx && cd ..
cd twemoji && uv run python twemoji.py ../apple/${FONT_NAME}_00.ttf && cd ..
cd whatsapp && uv run python whatsapp.py ../apple/${FONT_NAME}_00.ttf NotoColorEmoji.ttf NotoColorEmoji.G_S_U_B_.ttx && cd ..

rm .test
