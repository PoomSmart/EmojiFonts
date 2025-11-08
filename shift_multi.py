"""CLI for applying metric overrides to multi-glyph emoji silhouettes."""

import argparse
import json
import logging
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Optional, Sequence

LOGGER = logging.getLogger(__name__)
DEFAULT_OVERRIDE_PATH = Path(__file__).resolve().parent / 'data' / 'shift_overrides.json'

MetricOverrides = Dict[str, Dict[str, int]]


def load_overrides(path: Path) -> MetricOverrides:
    if not path.exists():
        raise FileNotFoundError(f'Override file not found: {path}')
    with path.open('r', encoding='utf-8') as handle:
        data = json.load(handle)

    if not isinstance(data, dict):
        raise ValueError('Overrides file must contain a JSON object at the top level')

    for glyph_name, metrics in data.items():
        if not isinstance(metrics, dict):
            raise ValueError(f'Override for {glyph_name} must be an object with width/lsb values')
        if 'width' not in metrics or 'lsb' not in metrics:
            raise ValueError(f'Override for {glyph_name} must declare "width" and "lsb" keys')
        if not isinstance(metrics['width'], int) or not isinstance(metrics['lsb'], int):
            raise ValueError(f'Override for {glyph_name} must use integer width/lsb values')
    return data


def apply_overrides(hmtx_ttx: Path, overrides: MetricOverrides) -> int:
    tree = ET.parse(str(hmtx_ttx))
    root = tree.getroot()

    remaining = set(overrides.keys())
    for mtx in root.iter('mtx'):
        name = mtx.attrib.get('name')
        if not name or name not in overrides:
            continue
        metrics = overrides[name]
        mtx.set('width', str(metrics['width']))
        mtx.set('lsb', str(metrics['lsb']))
        remaining.discard(name)

    applied_total = len(overrides) - len(remaining)
    if remaining:
        raise KeyError(f'Overrides refer to missing glyph metrics: {", ".join(sorted(remaining))}')

    tree.write(str(hmtx_ttx), encoding='utf-8')
    return applied_total


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description='Apply width/lsb overrides for multi-glyph emoji silhouettes.',
    )
    parser.add_argument(
        'hmtx_ttx',
        type=Path,
        help='Path to the hmtx table exported as TTX (XML)',
    )
    parser.add_argument(
        '--overrides',
        type=Path,
        default=DEFAULT_OVERRIDE_PATH,
        help=f'Path to JSON overrides file (default: {DEFAULT_OVERRIDE_PATH.name})',
    )
    parser.add_argument('--log-level', default='INFO', help='Python logging level (default: INFO)')
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.INFO))

    try:
        overrides = load_overrides(args.overrides)
        applied_count = apply_overrides(args.hmtx_ttx, overrides)
    except Exception as exc:  # pylint: disable=broad-except
        LOGGER.error('Failed to apply overrides: %s', exc)
        return 1

    LOGGER.info('Applied overrides for %s glyphs', applied_count)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
