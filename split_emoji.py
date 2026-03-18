#!/usr/bin/env python3
"""
split_emoji.py

Split a combined emoji image containing two side-by-side components into
separate left and right images, both preserving the original canvas size.

Usage:
    python split_emoji.py <input> <left_output> <right_output> [options]

Options:
    --split-x X          Force split at column X (0-indexed). Auto-detected otherwise.
    --method valley      (default) Find the column with the lowest alpha density in
                         the middle region and split there.
    --method components  Label connected components and assign each to left/right
                         by centroid. Falls back to valley if fewer than 2 are found.
    --method geodesic    Split a single connected blob by geodesic distance from
                         left/right edge seeds. Good for overlapping people.

Examples:
    # Auto-detect split point
    python split_emoji.py combined.png left.png right.png

    # Force split at a specific column
    python split_emoji.py combined.png left-d.png right-d.png --split-x 48

    # Use connected-component separation
    python split_emoji.py combined.png left.png right.png --method components

    # Use geodesic separation for overlapping subjects
    python split_emoji.py combined.png left.png right.png --method geodesic
"""

import argparse
import collections
from pathlib import Path

from PIL import Image


def col_alpha_sums(img: Image.Image) -> list[int]:
    """Return per-column sums of the alpha channel."""
    w = img.size[0]
    data = img.split()[3].tobytes()
    return [sum(data[x::w]) for x in range(w)]


def find_valley(img: Image.Image) -> int:
    """Find the column with the minimum alpha sum in the middle half of the image."""
    w = img.size[0]
    sums = col_alpha_sums(img)
    search_start = w // 4
    search_end = 3 * w // 4
    return min(range(search_start, search_end), key=lambda x: sums[x])


def split_at(img: Image.Image, split_x: int) -> tuple[Image.Image, Image.Image]:
    """
    Split *img* at column *split_x*.
    Left output gets columns 0..split_x (inclusive) on a full-size canvas.
    Right output gets columns split_x+1..w-1 on a full-size canvas.
    """
    w, h = img.size
    left = Image.new("RGBA", (w, h))
    right = Image.new("RGBA", (w, h))
    left.paste(img.crop((0, 0, split_x + 1, h)), (0, 0))
    right.paste(img.crop((split_x + 1, 0, w, h)), (split_x + 1, 0))
    return left, right


def find_components(img: Image.Image, alpha_threshold: int = 10) -> list[list[tuple[int, int]]]:
    """
    Return connected components (8-connectivity) of non-transparent pixels.
    Each component is a list of (x, y) tuples.
    """
    w, h = img.size
    alpha = img.split()[3].tobytes()
    visited = bytearray(w * h)
    components: list[list[tuple[int, int]]] = []

    for start in range(w * h):
        if alpha[start] < alpha_threshold or visited[start]:
            continue
        component: list[tuple[int, int]] = []
        queue: collections.deque[tuple[int, int]] = collections.deque()
        queue.append((start % w, start // w))
        while queue:
            x, y = queue.popleft()
            i = y * w + x
            if visited[i]:
                continue
            visited[i] = 1
            component.append((x, y))
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h:
                        ni = ny * w + nx
                        if not visited[ni] and alpha[ni] >= alpha_threshold:
                            queue.append((nx, ny))
        components.append(component)

    return components


def split_by_components(img: Image.Image, min_size: int = 30) -> tuple[Image.Image, Image.Image]:
    """
    Separate the two main connected components and assign them to left/right
    based on their centroid x position.

    Small components (< min_size pixels) are merged into whichever main group
    their centroid is closest to.

    Raises ValueError if fewer than 2 significant components are found.
    """
    w, h = img.size
    components = find_components(img)
    significant = sorted(
        [c for c in components if len(c) >= min_size],
        key=len,
        reverse=True,
    )

    if len(significant) < 2:
        raise ValueError(
            f"Found only {len(significant)} significant component(s); "
            "consider using --method valley."
        )

    def cx(comp: list[tuple[int, int]]) -> float:
        return sum(x for x, _ in comp) / len(comp)

    # Take the two largest as anchors
    anchors = significant[:2]
    anchors.sort(key=cx)  # anchors[0] is left, anchors[1] is right

    left_pixels: set[tuple[int, int]] = set(map(tuple, anchors[0]))
    right_pixels: set[tuple[int, int]] = set(map(tuple, anchors[1]))
    lc, rc = cx(anchors[0]), cx(anchors[1])

    # Assign remaining components to the nearest anchor centroid
    for comp in significant[2:]:
        c = cx(comp)
        if abs(c - lc) <= abs(c - rc):
            left_pixels.update(map(tuple, comp))
        else:
            right_pixels.update(map(tuple, comp))

    # Also assign tiny/noise components
    for comp in components:
        if len(comp) < min_size:
            c = cx(comp)
            if abs(c - lc) <= abs(c - rc):
                left_pixels.update(map(tuple, comp))
            else:
                right_pixels.update(map(tuple, comp))

    left = Image.new("RGBA", (w, h))
    right = Image.new("RGBA", (w, h))
    src = img.load()
    lp, rp = left.load(), right.load()
    for x, y in left_pixels:
        lp[x, y] = src[x, y]
    for x, y in right_pixels:
        rp[x, y] = src[x, y]

    return left, right


def split_by_geodesic(
    img: Image.Image,
    alpha_threshold: int = 10,
    seed_band_ratio: float = 0.2,
) -> tuple[Image.Image, Image.Image]:
    """
    Split one connected foreground mask into left/right groups using geodesic
    distance from edge seeds.

    This helps when subjects overlap and plain x-splits leak body parts.
    """
    w, h = img.size
    alpha = img.split()[3].tobytes()

    def i(x: int, y: int) -> int:
        return y * w + x

    opaque = [a >= alpha_threshold for a in alpha]
    if not any(opaque):
        raise ValueError("Input image has no foreground pixels.")

    band = max(1, int(w * seed_band_ratio))
    left_seeds: list[int] = []
    right_seeds: list[int] = []

    for y in range(h):
        for x in range(band):
            idx = i(x, y)
            if opaque[idx]:
                left_seeds.append(idx)
        for x in range(w - band, w):
            idx = i(x, y)
            if opaque[idx]:
                right_seeds.append(idx)

    if not left_seeds or not right_seeds:
        raise ValueError("Could not find seeds on both sides.")

    # Multi-source BFS over opaque pixels for geodesic distance.
    inf = 10**9
    dl = [inf] * (w * h)
    dr = [inf] * (w * h)
    ql: collections.deque[int] = collections.deque(left_seeds)
    qr: collections.deque[int] = collections.deque(right_seeds)

    for idx in left_seeds:
        dl[idx] = 0
    for idx in right_seeds:
        dr[idx] = 0

    def bfs(queue: collections.deque[int], dist: list[int]) -> None:
        while queue:
            idx = queue.popleft()
            x = idx % w
            y = idx // w
            nd = dist[idx] + 1
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h:
                    ni = i(nx, ny)
                    if opaque[ni] and nd < dist[ni]:
                        dist[ni] = nd
                        queue.append(ni)

    bfs(ql, dl)
    bfs(qr, dr)

    left = Image.new("RGBA", (w, h))
    right = Image.new("RGBA", (w, h))
    src = img.load()
    lp, rp = left.load(), right.load()

    for y in range(h):
        for x in range(w):
            idx = i(x, y)
            if not opaque[idx]:
                continue
            # Tie-break toward geometric side to reduce seam noise.
            if dl[idx] < dr[idx] or (dl[idx] == dr[idx] and x <= (w - 1) // 2):
                lp[x, y] = src[x, y]
            else:
                rp[x, y] = src[x, y]

    return left, right


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Split a combined emoji image into left and right components.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("input", help="Source image (any PIL-supported format).")
    parser.add_argument("left_output", help="Output path for the left component.")
    parser.add_argument("right_output", help="Output path for the right component.")
    parser.add_argument(
        "--split-x",
        type=int,
        default=None,
        metavar="X",
        help="Force the split at column X (0-indexed). Overrides --method.",
    )
    parser.add_argument(
        "--method",
        choices=["valley", "components", "geodesic"],
        default="valley",
        help="Auto-detection method when --split-x is not given (default: valley).",
    )
    args = parser.parse_args()

    img = Image.open(args.input).convert("RGBA")
    w = img.size[0]

    if args.split_x is not None:
        print(f"Using forced split at x={args.split_x} (of {w})")
        left, right = split_at(img, args.split_x)
    elif args.method == "components":
        try:
            left, right = split_by_components(img)
            print("Split by connected components.")
        except ValueError as e:
            print(f"Component method failed: {e}")
            print("Falling back to valley detection.")
            split_x = find_valley(img)
            print(f"Valley split at x={split_x} (of {w})")
            left, right = split_at(img, split_x)
    elif args.method == "geodesic":
        try:
            left, right = split_by_geodesic(img)
            print("Split by geodesic distance.")
        except ValueError as e:
            print(f"Geodesic method failed: {e}")
            print("Falling back to valley detection.")
            split_x = find_valley(img)
            print(f"Valley split at x={split_x} (of {w})")
            left, right = split_at(img, split_x)
    else:
        split_x = find_valley(img)
        print(f"Valley split at x={split_x} (of {w})")
        left, right = split_at(img, split_x)

    Path(args.left_output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.right_output).parent.mkdir(parents=True, exist_ok=True)
    left.save(args.left_output)
    right.save(args.right_output)
    print(f"Saved: {args.left_output}")
    print(f"Saved: {args.right_output}")


if __name__ == "__main__":
    main()
