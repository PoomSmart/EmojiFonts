import struct
import sys

import liblzfse


def forward_transform(r, g, b):
    p = r - b
    if p >= 0:
        t = b + (p // 2)
    else:
        t = b + ((p + 1) // 2)
    q = g - t
    if q >= 0:
        base = g - ((q + 1) // 2)
    else:
        base = g - (q // 2)
    return base, p, q


def zigzag_encode(diff, offset):
    # Returns encoded value or None if not representable
    # convert(E, offset) == diff

    # Try Even (k + offset = diff) -> k = diff - offset
    if diff >= offset:
        k = diff - offset
        e = 2 * k
        if e <= 255:
            return e

    # Try Odd (-k - offset = diff) -> k = -(diff + offset)
    if diff <= -offset:
        k = -(diff + offset)
        e = 2 * k + 1
        if e <= 255:
            return e

    return None


def filter4_value(left, upper):
    value = left + upper + 1
    return -((-value) // 2) if value < 0 else value // 2


def decode_zigzag(enc: int, offset: int) -> int:
    if enc % 2 == 0:
        return (enc // 2) + offset
    else:
        return -((enc - 1) // 2) - offset


def predict_filter(filter_type, x, y, width, buffer, i):
    if filter_type == 0:
        return 0, 0, 0

    left = (0, 0, 0)
    upper = (0, 0, 0)
    left_upper = (0, 0, 0)

    if x > 0:
        left = buffer[(i - 1) * 3 : (i - 1) * 3 + 3]
    if y > 0:
        upper = buffer[(i - width) * 3 : (i - width) * 3 + 3]
    if x > 0 and y > 0:
        left_upper = buffer[(i - width - 1) * 3 : (i - width - 1) * 3 + 3]

    if filter_type == 1:  # Decoder filter 1: pick left or upper based on component 0 only
        if x > 0 and y > 0:
            if abs(left[0] - left_upper[0]) < abs(upper[0] - left_upper[0]):
                return (upper[0], upper[1], upper[2])
            else:
                return (left[0], left[1], left[2])
        elif x > 0:
            return left
        elif y > 0:
            return upper
        return (0, 0, 0)

    elif filter_type == 2:  # Sub (Left)
        return left

    elif filter_type == 3:  # Up
        return upper

    elif filter_type == 4:  # Average (filter4_value only when both left AND upper exist)
        if x > 0 and y > 0:
            return tuple(filter4_value(left[c], upper[c]) for c in range(3))
        elif x > 0:
            return left   # decoder: adds left directly
        elif y > 0:
            return upper  # decoder: adds upper directly
        return (0, 0, 0)

    return 0, 0, 0


def encode_emjc(rgba_data, width, height, quantize_colors=None):
    pixels = width * height

    # Optional quantization
    if quantize_colors:

        from PIL import Image

        # Convert BGRA to RGBA for PIL
        rgba_pil = bytearray(len(rgba_data))
        for i in range(pixels):
            rgba_pil[i * 4 + 0] = rgba_data[i * 4 + 2]  # R
            rgba_pil[i * 4 + 1] = rgba_data[i * 4 + 1]  # G
            rgba_pil[i * 4 + 2] = rgba_data[i * 4 + 0]  # B
            rgba_pil[i * 4 + 3] = rgba_data[i * 4 + 3]  # A

        img = Image.frombytes("RGBA", (width, height), bytes(rgba_pil))
        # Quantize to reduce colors
        img_rgb = img.convert("RGB")
        img_p = img_rgb.quantize(colors=quantize_colors, method=2, dither=0)
        img_quant = img_p.convert("RGB")

        # Merge back with alpha
        img_final = Image.merge("RGBA", (*img_quant.split(), img.split()[3]))
        quantized = img_final.tobytes()

        # Convert back to BGRA
        rgba_data = bytearray(len(quantized))
        for i in range(pixels):
            rgba_data[i * 4 + 0] = quantized[i * 4 + 2]  # B
            rgba_data[i * 4 + 1] = quantized[i * 4 + 1]  # G
            rgba_data[i * 4 + 2] = quantized[i * 4 + 0]  # R
            rgba_data[i * 4 + 3] = quantized[i * 4 + 3]  # A

    alpha = bytearray(pixels)
    rgb_input = []

    for i in range(pixels):
        b = rgba_data[i * 4 + 0]
        g = rgba_data[i * 4 + 1]
        r = rgba_data[i * 4 + 2]
        a = rgba_data[i * 4 + 3]
        alpha[i] = a
        rgb_input.append((r, g, b))

    transformed = []
    for r, g, b in rgb_input:
        transformed.append(forward_transform(r, g, b))

    # Dynamic appendix: covers ANY buffer position that needs a non-zero initial offset.
    # The decoder processes appendix bytes before the main pixel loop, scanning sequentially
    # through buffer positions. Each byte encodes (skip << 2 | multiplier).
    appendix = bytearray()
    _appendix_cur_pos = 0

    def append_entry(buf_pos, multiplier):
        nonlocal _appendix_cur_pos
        if multiplier == 0:
            return
        skip = buf_pos - _appendix_cur_pos
        while skip > 63:
            # Padding byte: skip 63, set buffer[pos]=0 (no-op), advance 64
            appendix.append(63 * 4)
            _appendix_cur_pos += 64
            skip -= 64
        appendix.append(skip * 4 + multiplier)
        _appendix_cur_pos = buf_pos + 1

    def required_multiplier(diff):
        """Minimum appendix multiplier m (0-3) so that zigzag_encode(diff, m*128) succeeds."""
        needed = abs(diff) - 127
        for m in range(4):
            if m * 128 >= needed:
                return m
        return 3  # handles |diff| up to 511; valid pixels never exceed 510

    offsets = [0] * (pixels * 3)

    # With lossless encoding (appendix covers all hard pixels), reconstructed == target
    # for every pixel, so buffer_flat stays at target values throughout.
    buffer_flat = [v for t in transformed for v in t]

    filters = bytearray(height)
    encoded_rgb = bytearray()
    candidates = [0, 1, 2, 3, 4]

    for y in range(height):
        # Evaluate each filter candidate. For components that would overflow with the
        # current offset, project the required multiplier and include an appendix penalty.
        candidate_results = {}  # f -> (total_cost, residuals, new_entries)

        for f in candidates:
            residuals = []
            cost = 0
            new_entries = []  # (comp_idx, multiplier) pairs for overflow components

            for x in range(width):
                i = y * width + x
                target = transformed[i]
                pred = predict_filter(f, x, y, width, buffer_flat, i)

                for k in range(3):
                    comp_idx = i * 3 + k
                    diff = target[k] - pred[k]
                    enc = zigzag_encode(diff, offsets[comp_idx])
                    if enc is None:
                        mult = required_multiplier(diff)
                        new_entries.append((comp_idx, mult))
                        enc = zigzag_encode(diff, mult * 128)
                    residuals.append(enc)
                    cost += enc

            # Prefer fewer appendix entries; break ties by residual cost.
            candidate_results[f] = (cost + len(new_entries) * 1000, residuals, new_entries)

        best_filter = min(candidate_results, key=lambda f: candidate_results[f][0])
        _, best_residuals, new_entries = candidate_results[best_filter]

        # Commit appendix entries for this row's chosen filter (in comp_idx order).
        for comp_idx, mult in new_entries:
            append_entry(comp_idx, mult)
            offsets[comp_idx] = mult * 128

        filters[y] = best_filter
        encoded_rgb.extend(best_residuals)

    data_to_compress = bytes(alpha + filters + encoded_rgb + appendix)
    compressed_data = liblzfse.compress(data_to_compress)

    header = struct.pack("<4sHHH HHH", b"emj1", 0, 0xA101, width, height, len(appendix), 0)

    return header + compressed_data


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Encode BGRA to EMJC format")
    parser.add_argument("input", help="Input BGRA file")
    parser.add_argument("width", type=int, help="Image width")
    parser.add_argument("height", type=int, help="Image height")
    parser.add_argument("output", help="Output EMJC file")
    parser.add_argument("--quantize", type=int, help="Quantize to N colors (optional)", default=None)

    args = parser.parse_args()

    with open(args.input, "rb") as f:
        data = f.read()

    if len(data) != args.width * args.height * 4:
        print(f"Input data size {len(data)} does not match dimensions {args.width}x{args.height}x4")
        sys.exit(1)

    encoded = encode_emjc(data, args.width, args.height, quantize_colors=args.quantize)

    with open(args.output, "wb") as f:
        f.write(encoded)
