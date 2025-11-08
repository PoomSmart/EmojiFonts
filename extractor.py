import argparse
import binascii
import io
import logging
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Iterable, Optional, Sequence

from PIL import Image

from emjc import decode_emjc

LOGGER = logging.getLogger(__name__)

SUPPORTED_TYPES = {'png ', 'emjc', 'flip'}
DEFAULT_ALLOWED_STRIKES = {40, 64, 96, 112, 160}


def _ensure_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _decode_hexdata(hexdata: str) -> bytes:
    return binascii.unhexlify(''.join(hexdata.split()))


def _resolve_flip_source(strike: ET.Element, reference: ET.Element) -> ET.Element:
    glyphname = reference.get('glyphname')
    if not glyphname:
        raise ValueError('Flip glyph reference missing "glyphname" attribute')
    match = strike.find(f'glyph[@name="{glyphname}"]')
    if match is None:
        raise ValueError(f'Flip glyph references unknown glyph "{glyphname}"')
    return match


def extract_images(
    output_dir: Path,
    sbix_ttx: Path,
    *,
    allowed_strikes: Optional[Iterable[int]] = DEFAULT_ALLOWED_STRIKES,
) -> None:
    if not sbix_ttx.exists():
        raise FileNotFoundError(f'SBIX ttx file not found: {sbix_ttx}')

    output_dir = output_dir.resolve()
    allowed = set(allowed_strikes) if allowed_strikes is not None else set()
    data = ET.parse(sbix_ttx).getroot()

    for strike in data.iter('strike'):
        ppem_text = strike.find('ppem')
        if ppem_text is None:
            LOGGER.debug('Skipping strike without ppem entry')
            continue
        ppem = int(ppem_text.attrib['value'])
        if allowed and ppem not in allowed:
            LOGGER.debug('Skipping strike %sx%s because it is not allowed', ppem, ppem)
            continue

        LOGGER.info('Reading strike of size %sx%s', ppem, ppem)
        strike_output_dir = output_dir / str(ppem)
        _ensure_directory(strike_output_dir)

        for glyph in strike.findall('glyph'):
            graphic_type = glyph.get('graphicType')
            name = glyph.get('name')
            if not name:
                LOGGER.debug('Skipping glyph with no name in strike %s', ppem)
                continue

            is_flip = graphic_type == 'flip'
            source_glyph = glyph
            if is_flip:
                ref = glyph.find('ref')
                if ref is None:
                    LOGGER.warning('Flip glyph %s missing <ref> element; skipping', name)
                    continue
                try:
                    source_glyph = _resolve_flip_source(strike, ref)
                except ValueError as exc:
                    LOGGER.warning('%s; skipping glyph %s', exc, name)
                    continue
                graphic_type = source_glyph.get('graphicType')

            if graphic_type not in SUPPORTED_TYPES:
                LOGGER.debug('Skipping glyph %s (%s); unsupported graphic type', name, graphic_type)
                continue

            hexdata_node = source_glyph.find('hexdata')
            if hexdata_node is None or not (hexdata_text := hexdata_node.text):
                LOGGER.warning('Glyph %s has no hexdata; skipping', name)
                continue

            data_bytes = _decode_hexdata(hexdata_text.strip())
            out_path = strike_output_dir / f'{name}.png'

            if graphic_type == 'emjc':
                decoded = decode_emjc(data_bytes)
                img = Image.frombuffer('RGBA', (ppem, ppem), decoded, 'raw', 'BGRA', 0, 1)
                if is_flip:
                    img = img.transpose(Image.FLIP_LEFT_RIGHT)
                img.save(out_path)
                continue

            if graphic_type == 'png ':
                if is_flip:
                    img = Image.open(io.BytesIO(data_bytes))
                    img = img.transpose(Image.FLIP_LEFT_RIGHT)
                    img.save(out_path)
                else:
                    out_path.write_bytes(data_bytes)
                continue

            LOGGER.debug('Glyph %s uses unsupported type %s after flip resolution', name, graphic_type)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Extract emoji images from an sbix TTX file.')
    parser.add_argument('output_dir', type=Path, help='Directory where extracted images will be written')
    parser.add_argument('sbix_ttx', type=Path, help='sbix table exported as TTX (xml)')
    parser.add_argument(
        '--all-strikes',
        action='store_true',
        help='Extract from every strike instead of the default subset (40,64,96,112,160)',
    )
    parser.add_argument(
        '--strikes',
        type=int,
        nargs='+',
        metavar='PPEM',
        help='Explicit list of strikes to extract (overrides --all-strikes)',
    )
    parser.add_argument(
        '--log-level',
        default='INFO',
        help='Python logging level (default: INFO)',
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.INFO))

    if args.strikes:
        allowed = args.strikes
    elif args.all_strikes:
        allowed = []
    else:
        allowed = DEFAULT_ALLOWED_STRIKES

    try:
        extract_images(args.output_dir, args.sbix_ttx, allowed_strikes=allowed)
    except Exception as exc:  # pylint: disable=broad-except
        LOGGER.error('Extraction failed: %s', exc)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
