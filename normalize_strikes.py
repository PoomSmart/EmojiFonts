"""Ensure all strike sizes contain the same set of PNG emoji images.

For any emoji missing from a strike, the image is sourced from the closest
available strike (preferring the smallest strike larger than the target for
better downscale quality), resized to the target ppem via Lanczos, then
optimised with pngquant and oxipng.
"""

import argparse
import logging
import subprocess
from pathlib import Path
from typing import Sequence

from PIL import Image

LOGGER = logging.getLogger(__name__)


def _resize_and_save(src: Path, dst: Path, ppem: int) -> None:
    img = Image.open(src).convert("RGBA")
    img = img.resize((ppem, ppem), Image.LANCZOS)
    img.save(dst, "PNG")


def _optimize(paths: list[Path]) -> None:
    if not paths:
        return
    str_paths = [str(p) for p in paths]
    subprocess.run(
        ["pngquant", "--skip-if-larger", "-f", "--ext", ".png", *str_paths],
        check=False,
    )
    subprocess.run(
        ["oxipng", "-q", "--", *str_paths],
        check=False,
    )


def normalize_strikes(assets_dir: Path) -> None:
    strike_dirs = sorted(
        [d for d in assets_dir.iterdir() if d.is_dir() and d.name.isdigit()],
        key=lambda d: int(d.name),
    )
    if not strike_dirs:
        LOGGER.warning("No strike directories found in %s", assets_dir)
        return

    ppems = [int(d.name) for d in strike_dirs]
    by_ppem: dict[int, Path] = {int(d.name): d for d in strike_dirs}

    per_ppem_names: dict[int, set[str]] = {}
    all_names: set[str] = set()
    for ppem, d in by_ppem.items():
        names = {f.name for f in d.iterdir() if f.suffix == ".png"}
        per_ppem_names[ppem] = names
        all_names |= names

    to_create: list[tuple[Path, Path, int]] = []  # (src_path, dst_path, target_ppem)
    for ppem in ppems:
        missing = all_names - per_ppem_names[ppem]
        if not missing:
            continue
        LOGGER.info("Strike %s is missing %d image(s)", ppem, len(missing))
        for name in sorted(missing):
            # Prefer smallest strike larger than target (downscale = better quality),
            # fall back to largest strike smaller than target.
            larger = [c for c in sorted(ppems) if c > ppem and name in per_ppem_names[c]]
            smaller = [c for c in sorted(ppems, reverse=True) if c < ppem and name in per_ppem_names[c]]
            if larger:
                source_ppem = larger[0]
            elif smaller:
                source_ppem = smaller[0]
            else:
                LOGGER.warning("No source found for %s at ppem=%s; skipping", name, ppem)
                continue
            src = by_ppem[source_ppem] / name
            dst = by_ppem[ppem] / name
            to_create.append((src, dst, ppem))
            LOGGER.debug("Will resize %s from ppem=%s to ppem=%s", name, source_ppem, ppem)

    if not to_create:
        LOGGER.info("All strikes already have the same set of images")
        return

    LOGGER.info("Creating %d missing image(s) via resize...", len(to_create))
    for src, dst, ppem in to_create:
        _resize_and_save(src, dst, ppem)

    new_files = [dst for _, dst, _ in to_create]
    LOGGER.info("Optimising %d new image(s)...", len(new_files))
    _optimize(new_files)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ensure all strike sizes contain the same set of PNG emoji images.")
    parser.add_argument("assets_dir", type=Path, help="Directory containing ppem subdirectories (e.g. apple/images)")
    parser.add_argument("--log-level", default="INFO", help="Python logging level (default: INFO)")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.INFO))
    normalize_strikes(args.assets_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
