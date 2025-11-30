#!/usr/bin/env bash

# Script to convert PNG files to EMJC format in parallel
# Usage: ./convert_to_emjc.sh <assets_dir>

set -e

ASSETS_DIR="$1"

if [ -z "$ASSETS_DIR" ]; then
    echo "Usage: $0 <assets_dir>"
    echo "Example: $0 apple/EMJC"
    exit 1
fi

if [ ! -d "$ASSETS_DIR" ]; then
    echo "Error: Directory '$ASSETS_DIR' does not exist"
    exit 1
fi

# Detect number of CPU cores
if [[ "$(uname)" == "Darwin" ]]; then
    NPROC=$(sysctl -n hw.ncpu)
else
    NPROC=$(nproc)
fi

echo "Converting PNGs to EMJC format..."

# Create helper script for parallel processing
HELPER_SCRIPT=$(mktemp)
cat > "$HELPER_SCRIPT" << 'EOF'
#!/usr/bin/env bash
png="$1"
size="$2"
filename=$(basename "$png" .png)
dir=$(dirname "$png")

magick "$png" -depth 8 bgra:"$dir/$filename.bgra" 2>/dev/null
uv run python3 emjc_encoder.py "$dir/$filename.bgra" $size $size "$dir/$filename.emjc" --quantize 256 2>/dev/null
rm "$dir/$filename.bgra" "$png"
EOF
chmod +x "$HELPER_SCRIPT"

# Process each size directory
for size in 160 96 64 40; do
    if [ -d "$ASSETS_DIR/$size" ]; then
        png_count=$(find "$ASSETS_DIR/$size" -name "*.png" | wc -l | tr -d ' ')
        if [ "$png_count" -gt 0 ]; then
            echo "Converting ${size}px: $png_count files (using $NPROC parallel jobs)..."
            find "$ASSETS_DIR/$size" -name "*.png" -print0 | xargs -0 -P $NPROC -n 1 -I {} "$HELPER_SCRIPT" {} $size
        fi
    fi
done

rm "$HELPER_SCRIPT"

echo "EMJC conversion complete!"
