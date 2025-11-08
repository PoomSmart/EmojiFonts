"""Minimal regression tests covering the public CLIs."""

from __future__ import annotations

import binascii
import io
import json
import sys
import textwrap
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import extractor
import remove_class3
import shift_multi


@pytest.fixture
def sample_png_hex() -> str:
    img = Image.new('RGBA', (4, 4), (255, 0, 0, 255))
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    return binascii.hexlify(buffer.getvalue()).decode('ascii')


def _write_file(path: Path, content: str) -> Path:
    path.write_text(content, encoding='utf-8')
    return path


def test_extract_images_handles_flip_glyph(tmp_path: Path, sample_png_hex: str) -> None:
    sbix_content = textwrap.dedent(
        f'''<?xml version="1.0" encoding="UTF-8"?>
<ttFont>
  <sbix>
    <strike>
      <ppem value="40"/>
      <glyph name="u1F600" graphicType="png ">
        <hexdata>{sample_png_hex}</hexdata>
      </glyph>
      <glyph name="u1F603" graphicType="flip">
        <ref glyphname="u1F600"/>
      </glyph>
    </strike>
  </sbix>
</ttFont>
'''
    )
    sbix_path = _write_file(tmp_path / 'sbix.ttx', sbix_content)
    output_dir = tmp_path / 'out'

    extractor.extract_images(output_dir, sbix_path, allowed_strikes=[40])

    base = output_dir / '40' / 'u1F600.png'
    flipped = output_dir / '40' / 'u1F603.png'
    assert base.exists()
    assert flipped.exists()

    with Image.open(base) as base_img, Image.open(flipped) as flipped_img:
        assert base_img.size == flipped_img.size == (4, 4)


def test_remove_class_three_entries_strips_non_outline(tmp_path: Path) -> None:
    gdef_content = textwrap.dedent(
        '''<?xml version="1.0" encoding="UTF-8"?>
<ttFont>
  <GDEF>
    <GlyphClassDef>
      <ClassDef glyph="outline.example" class="1"/>
      <ClassDef glyph="foo" class="3"/>
      <ClassDef glyph="outline.bar" class="2"/>
      <ClassDef glyph="baz" class="3"/>
    </GlyphClassDef>
  </GDEF>
</ttFont>
'''
    )
    gdef_path = _write_file(tmp_path / 'gdef.ttx', gdef_content)

    removed = remove_class3.remove_class_three_entries(gdef_path)
    assert removed == 2

    tree = ET.parse(str(gdef_path))
    glyphs = [node.attrib['glyph'] for node in tree.iterfind('.//ClassDef')]
    assert glyphs == ['outline.example', 'outline.bar']


def test_apply_overrides_updates_metrics(tmp_path: Path) -> None:
    overrides_data = {
        "u1F468.1.L": {"width": 400, "lsb": 0},
        "u1F468.1.R": {"width": 400, "lsb": -400},
    }
    overrides_path = tmp_path / 'overrides.json'
    overrides_path.write_text(
        json.dumps(overrides_data, indent=2) + '\n',
        encoding='utf-8',
    )

    hmtx_content = textwrap.dedent(
        '''<?xml version="1.0" encoding="UTF-8"?>
<ttFont>
  <hmtx>
    <mtx name="u1F468.1.L" width="300" lsb="10"/>
    <mtx name="u1F468.1.R" width="300" lsb="-10"/>
  </hmtx>
</ttFont>
'''
    )
    hmtx_path = _write_file(tmp_path / 'hmtx.ttx', hmtx_content)

    overrides = shift_multi.load_overrides(overrides_path)
    applied = shift_multi.apply_overrides(hmtx_path, overrides)

    assert applied == len(overrides_data)

    tree = ET.parse(str(hmtx_path))
    metrics = {
        node.attrib['name']: (node.attrib['width'], node.attrib['lsb'])
        for node in tree.iterfind('.//mtx')
    }
    assert metrics == {
        'u1F468.1.L': ('400', '0'),
        'u1F468.1.R': ('400', '-400'),
    }

    with pytest.raises(KeyError):
        shift_multi.apply_overrides(hmtx_path, {"missing": {"width": 1, "lsb": 2}})
