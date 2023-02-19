#!/usr/bin/env bash

set -e

rm -rf release
mkdir -p release

ln apple/AppleColorEmoji-HD.ttc release/AppleColorEmoji-HD.ttc
ln apple/AppleColorEmoji-LQ.ttc release/AppleColorEmoji-LQ.ttc
ln blobmoji/blobmoji.ttc release/blobmoji.ttc
ln facebook/facebook.ttc release/facebook.ttc
ln fluentui/fluentui-Color.ttc release/fluentui-Color.ttc
ln fluentui/fluentui-Flat.ttc release/fluentui-Flat.ttc
ln joypixels/joypixels.ttc release/joypixels.ttc
ln joypixels/joypixels-Decal.ttc release/joypixels-Decal.ttc
ln noto-emoji/noto-emoji.ttc release/noto-emoji.ttc
ln oneui/oneui.ttc release/oneui.ttc
ln openmoji/openmoji.ttc release/openmoji.ttc
ln tossface/tossface.ttc release/tossface.ttc
ln twemoji/twemoji.ttc release/twemoji.ttc
ln whatsapp/whatsapp.ttc release/whatsapp.ttc
