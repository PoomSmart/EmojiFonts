import argparse
import logging
from pathlib import Path

from fontTools import ttLib

from shared import get_image_data, prepare_strikes

LOGGER = logging.getLogger(__name__)


def _load_font(path: Path) -> ttLib.TTFont:
    if not path.exists():
        raise FileNotFoundError(f'Input font not found: {path}')
    return ttLib.TTFont(str(path))


def _resolve_asset(path: Path) -> bytes:
    if not path.exists():
        raise FileNotFoundError(f'Asset image missing: {path}')
    return get_image_data(str(path))


def update_sbix_images(input_font: Path, output_font: Path, assets_dir: Path, *, hd: bool) -> None:
    font = _load_font(input_font)

    prepare_strikes(font, hd)

    sbix_table = font['sbix']
    for ppem, strike in sbix_table.strikes.items():
        LOGGER.info('Reading strike of size %sx%s', ppem, ppem)
        for name, glyph in strike.glyphs.items():
            if glyph.graphicType not in {'emjc', 'flip'}:
                continue
            glyph.graphicType = 'png '
            asset_path = assets_dir / str(ppem) / f'{name}.png'
            glyph.imageData = _resolve_asset(asset_path)

    LOGGER.info('Saving changes to %s', output_font)
    font.save(str(output_font))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Replace sbix glyph images with PNG assets.')
    parser.add_argument('input_font', type=Path, help='Input TTC/TTF file with sbix table')
    parser.add_argument('output_font', type=Path, help='Output TTC/TTF file that will be written')
    parser.add_argument('assets_dir', type=Path, help='Directory containing extracted PNG assets')
    parser.add_argument(
        '--hd',
        action='store_true',
        help='Expect HD assets (keep 160ppem strike). The default trims 160ppem.',
    )
    parser.add_argument('--log-level', default='INFO', help='Python logging level (default: INFO)')
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.INFO))

    try:
        update_sbix_images(args.input_font, args.output_font, args.assets_dir, hd=args.hd)
    except Exception as exc:  # pylint: disable=broad-except
        LOGGER.error('Failed to update sbix images: %s', exc)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
