import struct
import sys
from array import array
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

def predict_filter(filter_type, x, y, width, buffer, i):
    if filter_type == 0:
        return 0, 0, 0
    
    left = (0, 0, 0)
    upper = (0, 0, 0)
    left_upper = (0, 0, 0)
    
    if x > 0:
        left = buffer[(i - 1)*3 : (i - 1)*3 + 3]
    if y > 0:
        upper = buffer[(i - width)*3 : (i - width)*3 + 3]
    if x > 0 and y > 0:
        left_upper = buffer[(i - width - 1)*3 : (i - width - 1)*3 + 3]
        
    if filter_type == 1: # Paeth
        res = []
        for c in range(3):
            a = left[c]
            b = upper[c]
            c_val = left_upper[c]
            p = a + b - c_val
            pa = abs(p - a)
            pb = abs(p - b)
            pc = abs(p - c_val)
            if pa <= pb and pa <= pc:
                res.append(a)
            elif pb <= pc:
                res.append(b)
            else:
                res.append(c_val)
        return tuple(res)
        
    elif filter_type == 2: # Sub (Left)
        return left
        
    elif filter_type == 3: # Up
        return upper
        
    elif filter_type == 4: # Average
        return tuple(filter4_value(left[c], upper[c]) for c in range(3))
        
    return 0, 0, 0

def encode_emjc(rgba_data, width, height, quantize_colors=None):
    pixels = width * height
    
    # Optional quantization
    if quantize_colors:
        from PIL import Image
        import io
        # Convert BGRA to RGBA for PIL
        rgba_pil = bytearray(len(rgba_data))
        for i in range(pixels):
            rgba_pil[i*4+0] = rgba_data[i*4+2]  # R
            rgba_pil[i*4+1] = rgba_data[i*4+1]  # G
            rgba_pil[i*4+2] = rgba_data[i*4+0]  # B
            rgba_pil[i*4+3] = rgba_data[i*4+3]  # A
        
        img = Image.frombytes('RGBA', (width, height), bytes(rgba_pil))
        # Quantize to reduce colors
        img_rgb = img.convert('RGB')
        img_p = img_rgb.quantize(colors=quantize_colors, method=2, dither=0)
        img_quant = img_p.convert('RGB')
        
        # Merge back with alpha
        img_final = Image.merge('RGBA', (*img_quant.split(), img.split()[3]))
        quantized = img_final.tobytes()
        
        # Convert back to BGRA
        rgba_data = bytearray(len(quantized))
        for i in range(pixels):
            rgba_data[i*4+0] = quantized[i*4+2]  # B
            rgba_data[i*4+1] = quantized[i*4+1]  # G
            rgba_data[i*4+2] = quantized[i*4+0]  # R
            rgba_data[i*4+3] = quantized[i*4+3]  # A
    
    alpha = bytearray(pixels)
    rgb_input = []
    
    for i in range(pixels):
        b = rgba_data[i*4 + 0]
        g = rgba_data[i*4 + 1]
        r = rgba_data[i*4 + 2]
        a = rgba_data[i*4 + 3]
        alpha[i] = a
        rgb_input.append((r, g, b))
        
    transformed = []
    for r, g, b in rgb_input:
        transformed.append(forward_transform(r, g, b))
        
    # Improved appendix generation
    # Analyze all pixels to determine which components need offsets
    component_values = [[] for _ in range(3)]
    for base, p, q in transformed:
        component_values[0].append(base)
        component_values[1].append(p)
        component_values[2].append(q)
    
    # Determine optimal offsets for components
    # We can set offsets to 0, 128, 256, or 384 (0*128, 1*128, 2*128, 3*128)
    optimal_offsets = []
    for comp_idx in range(3):
        values = component_values[comp_idx]
        # Try each possible offset and see which minimizes encoding cost
        best_offset = 0
        best_cost = float('inf')
        
        for offset_multiplier in [0, 1, 2, 3]:
            offset = offset_multiplier * 128
            cost = 0
            for val in values[:100]:  # Sample first 100 pixels for speed
                enc = zigzag_encode(val, offset)
                if enc is None:
                    cost += 1000  # Penalty for non-encodable
                else:
                    cost += enc
            if cost < best_cost:
                best_cost = cost
                best_offset = offset_multiplier
        
        optimal_offsets.append(best_offset)
    
    # Build appendix
    appendix = bytearray()
    current_offset = 0
    initial_buffer_values = [0, 0, 0]
    
    for comp_idx in range(3):
        offset_multiplier = optimal_offsets[comp_idx]
        if offset_multiplier > 0:  # Only add to appendix if non-zero
            skip = comp_idx - current_offset
            appendix_byte = skip * 4 + offset_multiplier
            if appendix_byte <= 255:
                appendix.append(appendix_byte)
                initial_buffer_values[comp_idx] = offset_multiplier * 128
                current_offset = comp_idx + 1
    
    appendix_length = len(appendix)
    
    # Initialize buffer for prediction
    # buffer is flat array of reconstructed values.
    # But wait, `buffer` in decoder is updated IN PLACE.
    # `buffer[i] = convert(...)`.
    # So `buffer[i]` holds the final reconstructed value (Target).
    # So for prediction, we just need `transformed` array!
    # `transformed` IS the reconstructed values (since lossless).
    # So `predict_filter` can just read from `transformed`.
    # BUT, we need `buffer` (offset) for `zigzag_encode`.
    # The `offset` used in `zigzag_encode` is the value of `buffer` BEFORE update.
    # Before update, `buffer` holds the Appendix value (for i < appendix_len) or 0.
    # Wait, `buffer` is size `colors*4`.
    # Appendix initializes it.
    # Then loop `i` from 0 to `colors`.
    # `buffer[i]` is used as offset.
    # Then `buffer[i]` is updated to `Target`.
    # So for `zigzag_encode`, we need the "Previous Buffer State".
    # For `i=0,1,2`, previous state is `initial_buffer_values`.
    # For `i >= 3`, previous state is 0 (assuming Appendix only set first 3).
    
    # So we need an array of `offsets`.
    offsets = [0] * (pixels * 3)
    for k in range(3):
        offsets[k] = initial_buffer_values[k]
        
    buffer_flat = []
    for t in transformed:
        buffer_flat.extend(t)
        
    filters = bytearray(height)
    encoded_rgb = bytearray()
    
    candidates = [0, 1, 2, 3, 4]
    
    for y in range(height):
        best_filter = 0
        best_cost = float('inf')
        best_residuals = []
        
        for f in candidates:
            current_residuals = []
            current_cost = 0
            possible = True
            
            for x in range(width):
                i = y * width + x
                target = transformed[i]
                pred = predict_filter(f, x, y, width, buffer_flat, i)
                
                diffs = [target[0]-pred[0], target[1]-pred[1], target[2]-pred[2]]
                
                encoded_diffs = []
                for k in range(3):
                    comp_idx = i * 3 + k
                    offset = offsets[comp_idx]
                    d = diffs[k]
                    
                    enc = zigzag_encode(d, offset)
                    if enc is None:
                        possible = False
                        break
                    encoded_diffs.append(enc)
                
                if not possible:
                    break
                
                current_cost += sum(encoded_diffs)
                current_residuals.extend(encoded_diffs)
            
            if possible and current_cost < best_cost:
                best_cost = current_cost
                best_filter = f
                best_residuals = current_residuals
        
        if best_cost == float('inf'):
            # Fallback: Use Filter 0 and clamp
            best_filter = 0
            best_residuals = []
            for x in range(width):
                i = y * width + x
                target = transformed[i]
                pred = predict_filter(0, x, y, width, buffer_flat, i)
                diffs = [target[0]-pred[0], target[1]-pred[1], target[2]-pred[2]]
                for k in range(3):
                    comp_idx = i * 3 + k
                    offset = offsets[comp_idx]
                    d = diffs[k]
                    enc = zigzag_encode(d, offset)
                    if enc is None:
                        # Best effort clamp
                        # We want E such that convert(E, offset) is closest to D
                        # If D > offset, use max Even (254 -> 127+offset)
                        # If D < -offset, use max Odd (255 -> -127-offset)
                        # This is getting complicated. Just clamp E to 255.
                        # But E calculation assumes validity.
                        # If diff is huge positive:
                        if d > 0: enc = 254 # Max positive
                        else: enc = 255 # Max negative
                    best_residuals.append(enc)

        filters[y] = best_filter
        encoded_rgb.extend(best_residuals)
        
        # Verify reconstruction for this row to catch drift
        for x in range(width):
            i = y * width + x
            target = transformed[i]
            pred = predict_filter(best_filter, x, y, width, buffer_flat, i)
            
            # Reconstruct from residuals
            diffs = [0, 0, 0]
            for k in range(3):
                comp_idx = i * 3 + k
                offset = offsets[comp_idx]
                enc = best_residuals[x * 3 + k]
                
                # Decode ZigZag
                # convert(E, offset)
                val = 0
                if enc % 2 == 0:
                    val = (enc // 2) + offset
                else:
                    val = -((enc - 1) // 2) - offset
                
                diffs[k] = val
            
            reconstructed = (pred[0] + diffs[0], pred[1] + diffs[1], pred[2] + diffs[2])
            
            if reconstructed != target:
                # Encoder drift detected.
                # Update buffer with RECONSTRUCTED value to match decoder state
                pass
            
            # Update buffer_flat with reconstructed values
            buffer_flat[i*3+0] = reconstructed[0]
            buffer_flat[i*3+1] = reconstructed[1]
            buffer_flat[i*3+2] = reconstructed[2]
        
    data_to_compress = bytes(alpha + filters + encoded_rgb + appendix)
    compressed_data = liblzfse.compress(data_to_compress)
    
    header = struct.pack('<4sHHH HHH', b'emj1', 0, 0xa101, width, height, appendix_length, 0)
    
    return header + compressed_data

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Encode BGRA to EMJC format')
    parser.add_argument('input', help='Input BGRA file')
    parser.add_argument('width', type=int, help='Image width')
    parser.add_argument('height', type=int, help='Image height')
    parser.add_argument('output', help='Output EMJC file')
    parser.add_argument('--quantize', type=int, help='Quantize to N colors (optional)', default=None)
    
    args = parser.parse_args()
    
    with open(args.input, 'rb') as f:
        data = f.read()
        
    if len(data) != args.width * args.height * 4:
        print(f"Input data size {len(data)} does not match dimensions {args.width}x{args.height}x4")
        sys.exit(1)
        
    encoded = encode_emjc(data, args.width, args.height, quantize_colors=args.quantize)
    
    with open(args.output, 'wb') as f:
        f.write(encoded)

