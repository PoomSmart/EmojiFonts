#!/usr/bin/env bash

# Script to convert PNG files to EMJC format in parallel
# Usage: ./convert_to_emjc.sh <assets_dir>

set -e
trap 'kill $(jobs -p) 2>/dev/null; exit 130' INT TERM
trap 'echo "Error in $(basename "$0") at line $LINENO" >&2' ERR

VERIFY=0
if [ "$1" == "--verify" ]; then
    VERIFY=1
    ASSETS_DIR="$2"
else
    ASSETS_DIR="$1"
fi

if [ -z "$ASSETS_DIR" ]; then
    echo "Usage: $0 [--verify] <assets_dir>"
    echo "  --verify  Test encoder round-trip on a sample of PNGs (no files modified)"
    echo "Example: $0 apple/EMJC"
    echo "         $0 --verify apple/EMJC"
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

if [ "$VERIFY" == "1" ]; then
    echo "Verifying encoder round-trip (encode → decode → compare)..."

    PASS=0
    FAIL=0
    WORK_DIR=$(mktemp -d)
    trap 'rm -rf "$WORK_DIR"' EXIT

    # Collect up to 5 PNGs across size dirs
    TEST_PNGS=()
    for size in 160 96 64 40; do
        if [ -d "$ASSETS_DIR/$size" ]; then
            while IFS= read -r -d '' f; do
                TEST_PNGS+=("$f:$size")
                [ "${#TEST_PNGS[@]}" -ge 5 ] && break 2
            done < <(find "$ASSETS_DIR/$size" -name "*.png" -print0)
        fi
    done

    if [ "${#TEST_PNGS[@]}" -eq 0 ]; then
        echo "No PNG files found in $ASSETS_DIR"
        exit 1
    fi

    for entry in "${TEST_PNGS[@]}"; do
        png="${entry%:*}"
        size="${entry##*:}"
        name=$(basename "$png" .png)

        orig_bgra="$WORK_DIR/${name}_orig.bgra"
        emjc_file="$WORK_DIR/${name}.emjc"
        decoded_bgra="$WORK_DIR/${name}_decoded.bgra"

        # PNG → BGRA
        if ! magick "$png" -depth 8 bgra:"$orig_bgra" 2>/dev/null; then
            echo "  FAIL: $name (${size}px) — magick conversion failed"
            ((FAIL++)); continue
        fi

        # BGRA → EMJC (no --quantize: lossless round-trip)
        if ! uv run python3 emjc_encoder.py "$orig_bgra" $size $size "$emjc_file" 2>&1; then
            echo "  FAIL: $name (${size}px) — encoding failed"
            FAIL=$((FAIL + 1)); continue
        fi

        # EMJC → BGRA via decoder
        if ! uv run python3 - "$emjc_file" "$decoded_bgra" << 'PYEOF'
import sys
sys.path.insert(0, '.')
from emjc import decode_emjc
with open(sys.argv[1], 'rb') as f:
    data = f.read()
result = decode_emjc(data)
if result is None:
    sys.exit(1)
with open(sys.argv[2], 'wb') as f:
    f.write(result)
PYEOF
        then
            echo "  FAIL: $name (${size}px) — decoding failed"
            FAIL=$((FAIL + 1)); continue
        fi

        # Compare
        png_size=$(wc -c < "$orig_bgra")
        emjc_size=$(wc -c < "$emjc_file")
        if cmp -s "$orig_bgra" "$decoded_bgra"; then
            echo "  PASS: $name (${size}px) — BGRA ${png_size}B → EMJC ${emjc_size}B"
            PASS=$((PASS + 1))
        else
            echo "  FAIL: $name (${size}px) — decoded bytes differ from original"
            FAIL=$((FAIL + 1))
        fi
    done

    echo ""
    echo "Results: $PASS passed, $FAIL failed out of ${#TEST_PNGS[@]} tested"
    exit $((FAIL > 0 ? 1 : 0))
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
