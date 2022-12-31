import sys
from PIL import Image

# input: path to image, size to resize to, path to output

png = sys.argv[1]
size = int(sys.argv[2])
out = sys.argv[3]

with Image.open(png) as fin:
    img = fin.resize((size, size), Image.Resampling.BICUBIC)
    img.save(out)
