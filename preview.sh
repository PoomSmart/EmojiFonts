#!/usr/bin/env bash

# Render macOS Preview-style specimens for Apple Color Emoji-compatible fonts.
#
# Uses HarfBuzz hb-view with the CoreText shaper so AAT/morx ligatures
# (keycaps, ZWJ sequences) match Font Book. The default OpenType shaper
# skips morx and leaves keycaps as digits plus tofu.
#
# Usage:
#   ./preview.sh [font.ttc ...]
#   ./preview.sh                 # every .ttc under this repo
#
# Writes full-size PNGs to previews/<font-stem>.png and a 720px pngquant/oxipng
# copy into PoomSmart.github.io/repo/screenshots/<package>/<name>.png
#
# Environment:
#   PREVIEW_DIR              Full-size output directory (default: ./previews)
#   PREVIEW_FONT_SIZE        hb-view --font-size (default: 96)
#   PREVIEW_FACE_INDEX       TTC face index (default: 0)
#   PREVIEW_SCREENSHOTS_DIR  720px destination (default: ../../PoomSmart.github.io/repo/screenshots)
#   PREVIEW_SCREENSHOTS=0    Skip the 720px screenshot export
#   PNGQUANT=0               Skip pngquant on the 720px copy

set -e
trap 'echo "Error in $(basename "$0") at line $LINENO" >&2' ERR

ROOT="$(cd "$(dirname "$0")" && pwd)"
OUT_DIR="${PREVIEW_DIR:-$ROOT/previews}"
FONT_SIZE="${PREVIEW_FONT_SIZE:-96}"
FACE_INDEX="${PREVIEW_FACE_INDEX:-0}"
SCREENSHOTS_DIR="${PREVIEW_SCREENSHOTS_DIR:-$ROOT/../../PoomSmart.github.io/repo/screenshots}"
SCREENSHOT_WIDTH=720

# Same three-line sample CoreText returns from CTFontCopySampleString for AppleColorEmoji.
# Keycaps are digit + U+20E3 (no VS16).
SAMPLE=$'😃😇😍😜😸🙈🐺🐰👽🐉\n💰🏡🎅🍪🍕🚀🚻💩📷📦\n1⃣2⃣3⃣4⃣5⃣6⃣7⃣8⃣9⃣0⃣'

usage() {
    cat <<'EOF'
Usage: ./preview.sh [font.ttc ...]
       ./preview.sh                 # every .ttc under this repo

Writes full-size PNGs to previews/<font-stem>.png using hb-view --shaper=coretext.

Environment:
  PREVIEW_DIR              Full-size output directory (default: ./previews)
  PREVIEW_FONT_SIZE        hb-view --font-size (default: 96)
  PREVIEW_FACE_INDEX       TTC face index (default: 0)
  PREVIEW_SCREENSHOTS_DIR  720px screenshot destination
  PREVIEW_SCREENSHOTS=0    Skip the 720px screenshot export
  PNGQUANT=0               Skip pngquant on the 720px copy
EOF
}

screenshot_rel() {
    case "$1" in
        AppleColorEmoji-HD) echo "emojifontefm/font.png" ;;
        AppleColorEmoji-HD-flip) echo "emojifontflipefm/font.png" ;;
        AppleColorEmoji-LQ) echo "emojifontlqefm/font.png" ;;
        AppleColorEmoji-pixel) echo "emojifontpxefm/font.png" ;;
        blobmoji) echo "blobmojiefm/font.png" ;;
        facebook) echo "fbemojiefm/font.png" ;;
        fluentui-Color) echo "fluentuiefm/color.png" ;;
        fluentui-Flat) echo "fluentuiefm/flat.png" ;;
        joypixels) echo "joypixelsefm/font.png" ;;
        joypixels-Decal) echo "joypixelsdecalefm/font.png" ;;
        noto-emoji) echo "notoemojiefm/font.png" ;;
        noto-emoji-3D) echo "notoemoji3defm/font.png" ;;
        oneui) echo "oneuiefm/font.png" ;;
        openmoji) echo "openmojiefm/font.png" ;;
        tossface) echo "tossfaceefm/font.png" ;;
        twemoji) echo "twemojiefm/font.png" ;;
        whatsapp) echo "whatsappefm/font.png" ;;
        *) echo "" ;;
    esac
}

if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    usage
    exit 0
fi

if ! command -v hb-view >/dev/null 2>&1; then
    echo "hb-view not found. Install HarfBuzz: brew install harfbuzz" >&2
    exit 1
fi

if ! hb-shape --list-shapers 2>/dev/null | grep -qx coretext; then
    echo "hb-view is missing the CoreText shaper (macOS HarfBuzz required). brew install harfbuzz" >&2
    exit 1
fi

fonts=()
if [[ $# -eq 0 ]]; then
    while IFS= read -r -d '' font; do
        fonts+=("$font")
    done < <(find "$ROOT" -name '*.ttc' -print0 | sort -z)
    if [[ ${#fonts[@]} -eq 0 ]]; then
        echo "No .ttc fonts found under $ROOT" >&2
        exit 1
    fi
else
    fonts=("$@")
fi

mkdir -p "$OUT_DIR"

export_screenshot() {
    local src="$1" dest="$2"
    if ! command -v magick >/dev/null 2>&1; then
        echo "magick not found; skip 720px export. brew install imagemagick" >&2
        return 1
    fi
    mkdir -p "$(dirname "$dest")"
    local tmpdir tmp
    tmpdir="$(mktemp -d "${TMPDIR:-/tmp}/preview720.XXXXXX")"
    tmp="$tmpdir/preview.png"
    magick "$src" -resize "${SCREENSHOT_WIDTH}x" "$tmp"
    if [[ "${PNGQUANT:-1}" != "0" ]] && command -v pngquant >/dev/null 2>&1; then
        pngquant --skip-if-larger -f --ext .png "$tmp" || true
    fi
    if command -v oxipng >/dev/null 2>&1; then
        oxipng -q "$tmp"
    fi
    mv "$tmp" "$dest"
    rm -rf "$tmpdir"
}

preview_one() {
    local font="$1"
    if [[ ! -f "$font" && ! -L "$font" ]]; then
        echo "Font not found: $font" >&2
        exit 1
    fi
    local stem
    stem="$(basename "$font")"
    stem="${stem%.*}"
    local out="$OUT_DIR/$stem.png"
    echo "Previewing $font -> $out"
    hb-view --shaper=coretext --face-index="$FACE_INDEX" --font-size="$FONT_SIZE" \
        --background=1c1c1e --foreground=ffffff \
        --margin=24 --line-space=24 \
        -o "$out" "$font" "$SAMPLE"

    if [[ "${PREVIEW_SCREENSHOTS:-1}" == "0" ]]; then
        return 0
    fi
    local rel
    rel="$(screenshot_rel "$stem")"
    if [[ -z "$rel" ]]; then
        return 0
    fi
    if [[ ! -d "$SCREENSHOTS_DIR" ]]; then
        echo "Screenshots directory not found, skip 720px export: $SCREENSHOTS_DIR" >&2
        return 0
    fi
    local dest="$SCREENSHOTS_DIR/$rel"
    echo "Screenshot $out -> $dest (${SCREENSHOT_WIDTH}px)"
    export_screenshot "$out" "$dest"
}

for font in "${fonts[@]}"; do
    preview_one "$font"
done
