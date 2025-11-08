"""CLI helpers for stripping class 3 glyphs from an Apple GDEF table."""

import argparse
import logging
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional, Sequence

LOGGER = logging.getLogger(__name__)


def _iter_non_outline_classes(root: ET.Element):
    for class_def in root.iter('ClassDef'):
        glyph = class_def.attrib.get('glyph', '')
        if glyph.startswith('outline.'):
            continue
        yield class_def


def remove_class_three_entries(gdef_ttx: Path) -> int:
    tree = ET.parse(str(gdef_ttx))
    root = tree.getroot()
    glyph_class_def = root.find('.//GlyphClassDef')
    if glyph_class_def is None:
        raise ValueError('The provided TTX file does not contain a GlyphClassDef section')

    removal_candidates = list(_iter_non_outline_classes(root))
    if not removal_candidates:
        LOGGER.info('No non-outline class definitions found in %s', gdef_ttx)
        return 0

    for element in removal_candidates:
        glyph_class_def.remove(element)

    tree.write(str(gdef_ttx), encoding='utf-8')
    LOGGER.info('Removed %s entries from %s', len(removal_candidates), gdef_ttx)
    return len(removal_candidates)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description='Remove class 3 glyph assignments from an Apple GDEF TTX file.',
    )
    parser.add_argument(
        'gdef_ttx',
        type=Path,
        help='Path to the Apple GDEF table exported as TTX (XML)',
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

    try:
        remove_class_three_entries(args.gdef_ttx)
    except Exception as exc:  # pylint: disable=broad-except
        LOGGER.error('Failed to update %s: %s', args.gdef_ttx, exc)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
