#!/usr/bin/env bash
# Usage: svg-to-png.sh <source_dir> <size> [output_dir]
# Converts all SVGs found in <source_dir> into PNGs.
# output_dir defaults to images/<size>/ (relative to cwd).

set -e
trap 'kill $(jobs -p) 2>/dev/null; exit 130' INT TERM

SOURCE="$1"
SIZE="$2"
OUTPUT="${3:-images/$SIZE}"

export SIZE OUTPUT
find "$SOURCE" -type f -name '*.svg' -print0 | \
    xargs -0 -P "$(sysctl -n hw.logicalcpu)" -I {} bash -c \
    'fname=$(basename "$1"); rsvg-convert -a -h "$SIZE" "$1" -o "$OUTPUT/${fname/.svg/.png}"' \
    _ {}
