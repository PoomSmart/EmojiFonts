# decoder credit: https://github.com/cc4966/emjc-decoder

from array import array
from liblzfse import decompress, error
from struct import unpack

def convert_to_difference(value: int, offset: int):
    return -(value >> 1) - offset if value & 1 else (value >> 1) + offset

def filter4_value(left: int, upper: int):
    value = left + upper + 1
    return -((-value) // 2) if value < 0 else value // 2

def decode_emjc(emjc_data: bytes):
    '''decode emjc image data to BGRA image data'''
    header = unpack('>4s', emjc_data[:4])[0]
    if header != b'emj1':
        print(f'Expected emj1 but got {header}')
        return None
    # version = int(unpack('<H', emjc_data[4:6])[0])
    # unknown = int(unpack('<H', emjc_data[6:8])[0]) # 0xa101
    width = int(unpack('<H', emjc_data[8:10])[0])
    height = int(unpack('<H', emjc_data[10:12])[0])
    appendix_length = int(unpack('<H', emjc_data[12:14])[0])
    # padding = int(unpack('<H', emjc_data[14:16])[0])
    filter_length = height
    pixels = height * width # alpha array
    dst_length = pixels + filter_length + pixels * 3 + appendix_length
    try:
        decompressed_data = decompress(emjc_data[16:])
    except error:
        print(f'decompression failed with an error: {error}')
        exit(1)
    if len(decompressed_data) != dst_length:
        print(f'decompressed data length ({len(decompressed_data)}) is not equal to expected length ({dst_length})')
        exit(1)
    colors = pixels * 3 # rgb
    alpha = decompressed_data
    filters = decompressed_data[pixels:]
    rgb = decompressed_data[(pixels + filter_length):]
    appendix = decompressed_data[(pixels + filter_length + colors):]
    buffer = array('i', (0 for _ in range(0, colors * 4 + 1)))
    dst_buffer = bytearray(width * height * 4)
    offset = 0
    for i in range(0, appendix_length):
        offset += appendix[i] // 4
        if offset >= colors:
            break
        buffer[offset] = 128 * (appendix[i] % 4)
        offset += 1
    i = 0
    for y in range(0, height):
        filter = filters[y]
        for x in range(0, width):
            buffer[i * 3 + 0] = convert_to_difference(rgb[i * 3 + 0], buffer[i * 3 + 0])
            buffer[i * 3 + 1] = convert_to_difference(rgb[i * 3 + 1], buffer[i * 3 + 1])
            buffer[i * 3 + 2] = convert_to_difference(rgb[i * 3 + 2], buffer[i * 3 + 2])
            if filter == 1:
                if x > 0 and y > 0:
                    left = buffer[(i - 1) * 3 + 0]
                    upper = buffer[(i - width) * 3 + 0]
                    left_upper = buffer[(i - width - 1) * 3 + 0]
                    if abs(left - left_upper) < abs(upper - left_upper):
                        buffer[i * 3 + 0] += upper
                        buffer[i * 3 + 1] += buffer[(i - width) * 3 + 1]
                        buffer[i * 3 + 2] += buffer[(i - width) * 3 + 2]
                    else:
                        buffer[i * 3 + 0] += left
                        buffer[i * 3 + 1] += buffer[(i - 1) * 3 + 1]
                        buffer[i * 3 + 2] += buffer[(i - 1) * 3 + 2] 
                elif x > 0:
                    buffer[i * 3 + 0] += buffer[(i - 1) * 3 + 0]
                    buffer[i * 3 + 1] += buffer[(i - 1) * 3 + 1]
                    buffer[i * 3 + 2] += buffer[(i - 1) * 3 + 2]
                elif y > 0:
                    buffer[i * 3 + 0] += buffer[(i - width) * 3 + 0]
                    buffer[i * 3 + 1] += buffer[(i - width) * 3 + 1]
                    buffer[i * 3 + 2] += buffer[(i - width) * 3 + 2]
            elif filter == 2:
                if x > 0:
                    buffer[i * 3 + 0] += buffer[(i - 1) * 3 + 0]
                    buffer[i * 3 + 1] += buffer[(i - 1) * 3 + 1]
                    buffer[i * 3 + 2] += buffer[(i - 1) * 3 + 2]
            elif filter == 3:
                if y > 0:
                    buffer[i * 3 + 0] += buffer[(i - width) * 3 + 0]
                    buffer[i * 3 + 1] += buffer[(i - width) * 3 + 1]
                    buffer[i * 3 + 2] += buffer[(i - width) * 3 + 2]
            elif filter == 4:
                if x > 0 and y > 0:
                    buffer[i * 3 + 0] += filter4_value(buffer[(i - 1) * 3 + 0], buffer[(i - width) * 3 + 0])
                    buffer[i * 3 + 1] += filter4_value(buffer[(i - 1) * 3 + 1], buffer[(i - width) * 3 + 1])
                    buffer[i * 3 + 2] += filter4_value(buffer[(i - 1) * 3 + 2], buffer[(i - width) * 3 + 2])
                elif x > 0:
                    buffer[i * 3 + 0] += buffer[(i - 1) * 3 + 0]
                    buffer[i * 3 + 1] += buffer[(i - 1) * 3 + 1]
                    buffer[i * 3 + 2] += buffer[(i - 1) * 3 + 2]
                elif y > 0:
                    buffer[i * 3 + 0] += buffer[(i - width) * 3 + 0]
                    buffer[i * 3 + 1] += buffer[(i - width) * 3 + 1]
                    buffer[i * 3 + 2] += buffer[(i - width) * 3 + 2]

            base = buffer[i * 3 + 0]
            p = buffer[i * 3 + 1]
            q = buffer[i * 3 + 2]
            r, g, b = 0, 0, 0
            if p < 0 and q < 0:
                r = base + p // 2 - (q + 1) // 2
                g = base + q // 2
                b = base - (p + 1) // 2 - (q + 1) // 2
            elif p < 0:
                r = base + p // 2 - q // 2
                g = base + (q + 1) // 2
                b = base - (p + 1) // 2 - q // 2
            elif q < 0:
                r = base + (p + 1) // 2 - (q + 1) // 2
                g = base + q // 2
                b = base - p // 2 - (q + 1) // 2
            else:
                r = base + (p + 1) // 2 - q // 2
                g = base + (q + 1) // 2
                b = base - p // 2 - q // 2

            dst_buffer[i * 4 + 0] = (b % 257) + 257 if b < 0 else b % 257
            dst_buffer[i * 4 + 1] = (g % 257) + 257 if g < 0 else g % 257
            dst_buffer[i * 4 + 2] = (r % 257) + 257 if r < 0 else r % 257
            dst_buffer[i * 4 + 3] = alpha[i]
            i += 1

    return bytes(dst_buffer)
