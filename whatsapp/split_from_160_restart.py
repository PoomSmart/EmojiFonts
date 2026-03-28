#!/usr/bin/env python3
"""Generate split couple tiles from canonical base couple assets.

Couple inputs come from images/160.
Single-person references come from images/160.
Outputs are written under extra/original.

Every pixel is classified into exactly one of three mutually exclusive classes:
  HEART       -> right tile (from src), left tile (from aligned left-person reference)
  LEFT_PERSON -> left tile (from src),  right tile transparent
  RIGHT_PERSON-> right tile (from src), left tile transparent
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple, cast

# Allow importing split_emoji from the parent directory when this script runs
# from whatsapp/ (its home folder).
sys.path.insert(0, str(Path(__file__).parent.parent))

from PIL import Image

from split_emoji import find_valley, split_at, split_by_components, split_by_geodesic

COUPLE_SRC = Path("images/160")
SINGLE_SRC = Path("images/160")
DST = Path("extra/original")
EXTRA_IMAGES_DST = Path("extra/images/160")
IDENTITY_OVERRIDES = Path("../data/couple_identity_overrides.json")
HEART_MASK_DST = Path("extra/heart-mask")
# Canonical heart mask provided by user — 160×160, correct position for all couple variants.
HEART_MASK_REF = Path("extra/original/heart-mask.png")

ALPHA_THRESHOLD = 10
UPPER_HEAD_Y_MAX = 66
SIDE_PAD = 8
# First row guaranteed to be fully below the heart mask (heart_full covers y=3–86).
HEART_BOTTOM = 87
# How many pixels beyond the heart mask edge are filled with the standalone filler.
# 2 px covers the heart's own anti-aliased edge (used internally for right-tile fringe).
# 6 px (default) adds a ~4 px buffer that eliminates the dark transition / shadow seam.
# Raise by 1-2 if a faint seam is still visible; lower if the filler bleeds too far.
HEART_FILL_RADIUS = 8
# Per-category/skin overrides for HEART_FILL_RADIUS (controls how much of the base
# couple canvas is cleared to make room for the standalone filler).
# Keys follow the same pattern as ALIGN_OVERRIDES: "category" or "category/slot".
FILL_RADIUS_OVERRIDES: Dict[str, int] = {
    "kiss-male": 6,
    "kiss-female": 6,
    "kiss-female/d": 5,
    "heart-female/d": 5,
}
# How far the standalone filler itself is allowed to extend beyond heart_core.
# Defaults to HEART_FILL_RADIUS. Set smaller to shrink the filler, larger to expand it.
# Operates independently from HEART_FILL_RADIUS / FILL_RADIUS_OVERRIDES.
FILLER_MASK_RADIUS = HEART_FILL_RADIUS
# Per-category/skin overrides for FILLER_MASK_RADIUS.
FILLER_MASK_OVERRIDES: Dict[str, int] = {
    "kiss-male": 7,
    "kiss-female": 7,
    "kiss-female/d": 5,
    "heart-female/d": 5,
}
# Override which single-person emoji is used as the heart-zone filler.
# By default the filler is single_filename(left_person, tone) from SINGLE_SRC.
# Set a value to a codepoint string (e.g. "1f469") to use a different emoji;
# the tone suffix is appended automatically so all skin tones are handled.
# Keys follow the same pattern: "category" or "category/slot".
HEART_FILLER_REF: Dict[str, str] = {
    "kiss-female/d": "1f469_200d_2695",
    "heart-female/d": "1f469_200d_2695",
}
# Crop-based filler: instead of using the standalone single-person emoji as the
# heart-zone filler, crop a region from the top-right of the couple source image.
# Value is (width, height) or (width, height, dx, dy).
# The rectangle is taken from (160-width, 0, 160, height) of the couple source.
# dx/dy shift the crop's final position on the left tile (positive = right/down).
# Keys follow the same pattern: "category" or "category/slot".
CROP_FILLER: Dict[str, Tuple[int, ...]] = {
    "kiss-nogender": (20, 90, -98),
}
# Cut N pixels off the top of the couple-canvas base before compositing the filler.
# Use this to hide stray heart/kiss content that bleeds in at the top of the filler.
FILLER_TOP_CROP = 20
# Per-category/skin overrides for FILLER_TOP_CROP.
# Keys follow the same pattern: "category" or "category/slot".
FILLER_TOP_CROP_OVERRIDES: Dict[str, int] = {
    # "kiss-female": 20,
}
# The standalone 160×160 emoji scaled down to match each person's visual size in a couple.
STANDALONE_SCALED_SIZE = 111

SKINS: List[Tuple[str, str]] = [
    ("d", ""),
    ("0", "1f3fb"),
    ("1", "1f3fc"),
    ("2", "1f3fd"),
    ("3", "1f3fe"),
    ("4", "1f3ff"),
]

CATEGORIES: Dict[str, Tuple[str, str, str]] = {
    "heart-male": ("heart", "1f468", "1f468"),
    "heart-female": ("heart", "1f469", "1f469"),
    "heart-nogender": ("heart", "1f9d1", "1f9d1"),
    "kiss-male": ("kiss", "1f468", "1f468"),
    "kiss-female": ("kiss", "1f469", "1f469"),
    "kiss-nogender": ("kiss", "1f9d1", "1f9d1"),
}

# Unicode codepoint for the joiner element of each kind (heart or kiss mark).
KIND_CODES: Dict[str, str] = {
    "heart": "2764",
    "kiss": "1f48b",
}

# Per-category (and optionally per-skin) manual ox/oy/sz overrides for the standalone fill alignment.
# ox = horizontal offset (positive = right), oy = vertical offset (positive = down).
# sz = scale size in pixels (standalone is resized from 160 to sz before pasting).
# Set any value to None to use the auto-computed result instead.
# Use "category/slot" (e.g. "heart-male/d") for a skin-specific override; it takes
# priority over the plain "category" entry. Slots: d 0 1 2 3 4  (d = default/yellow).
# Rerun the script after adjusting to preview changes.
ALIGN_OVERRIDES: Dict[str, Tuple[int | None, int | None, int | None]] = {
    #  category          ox     oy     sz
    "heart-male":       (-26,  23,   113),
    "heart-female":     (-26,  24,   113),
    "heart-female/d":   (-47,  16,   157),
    "heart-nogender":   (-25,  26,   110),
    "kiss-male":        (-24,  23,   111),
    "kiss-female":      (-26,  24,   113),
    "kiss-female/d":    (-46,  16,   156),
    "kiss-nogender":    (-25,  26,   110),
}

RGBA = Tuple[int, int, int, int]


def rgba_at(img: Image.Image, point: Tuple[int, int]) -> RGBA:
    return cast(RGBA, img.getpixel(point))


def to_silhouette(img: Image.Image) -> Image.Image:
    """Return a copy of img with all RGB channels set to mid-gray (128), alpha preserved."""
    _, _, _, a = img.split()
    gray = Image.new("L", img.size, 128)
    return Image.merge("RGBA", (gray, gray, gray, a))


def tone_suffix(tone: str) -> str:
    return f"_{tone}" if tone else ""


def couple_filename(category: str, kind: str, left: str, right: str, tone: str) -> str:
    suffix = tone_suffix(tone)
    if category == "heart-nogender":
        return f"emoji_u1f491{suffix}.png"
    if category == "kiss-nogender":
        return f"emoji_u1f48f{suffix}.png"
    if kind == "heart":
        return f"emoji_u{left}{suffix}_200d_2764_200d_{right}{suffix}.png"
    return f"emoji_u{left}{suffix}_200d_2764_200d_1f48b_200d_{right}{suffix}.png"


def single_filename(person: str, tone: str) -> str:
    return f"emoji_u{person}{tone_suffix(tone)}.png"


def load_identity_overrides() -> Dict[str, Dict[str, Dict[str, str]]]:
    if not IDENTITY_OVERRIDES.exists():
        raise FileNotFoundError(f"Missing identity override file: {IDENTITY_OVERRIDES}")

    raw = json.loads(IDENTITY_OVERRIDES.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("Identity override file must contain a top-level object")

    resolved: Dict[str, Dict[str, Dict[str, str]]] = {}
    for category in CATEGORIES:
        if category not in raw:
            raise ValueError(f"Missing category in identity overrides: {category}")
        resolved[category] = {}
        category_data = raw[category]
        if not isinstance(category_data, dict):
            raise ValueError(f"Identity overrides for {category} must be an object")
        for slot, _ in SKINS:
            if slot not in category_data:
                raise ValueError(f"Missing override for {category} slot {slot}")
            slot_data = category_data[slot]
            if not isinstance(slot_data, dict):
                raise ValueError(f"Override for {category} slot {slot} must be an object")
            visual_left = slot_data.get("visual_left")
            visual_right = slot_data.get("visual_right")
            if not isinstance(visual_left, str) or not isinstance(visual_right, str):
                raise ValueError(
                    f"Override for {category} slot {slot} requires string visual_left/visual_right"
                )
            resolved[category][slot] = {
                "visual_left": visual_left,
                "visual_right": visual_right,
            }

            desired_left = CATEGORIES[category][1]
            desired_right = CATEGORIES[category][2]
            if desired_left != desired_right:
                allowed = {desired_left, desired_right}
                provided = {visual_left, visual_right}
                if provided != allowed:
                    raise ValueError(
                        "Invalid override identities for mixed category "
                        f"{category} slot {slot}: expected {sorted(allowed)}, got {sorted(provided)}"
                    )
                if visual_left == visual_right:
                    raise ValueError(
                        f"Invalid override for {category} slot {slot}: visual_left and visual_right cannot match"
                    )
    return resolved


def split_pair(img: Image.Image) -> Tuple[Image.Image, Image.Image]:
    try:
        return split_by_geodesic(img)
    except Exception:
        pass
    try:
        return split_by_components(img)
    except Exception:
        pass
    split_x = find_valley(img)
    return split_at(img, split_x)


def build_shared_heart_mask() -> Tuple[List[List[bool]], List[List[bool]], List[List[bool]]]:
    """Load the canonical heart mask directly from HEART_MASK_REF.

    The mask is already 160×160 and correctly positioned — it applies to
    every couple variant (male, female, nogender, heart, kiss) without
    any per-category scaling or colour detection.
    heart_core = exact mask shape (alpha > 128).
    heart_full = heart_core dilated by 2px to cover anti-aliased source edges.
    """
    if not HEART_MASK_REF.exists():
        raise FileNotFoundError(f"Missing canonical heart mask: {HEART_MASK_REF}")

    ref = Image.open(HEART_MASK_REF).convert("RGBA")
    w, h = ref.size
    if (w, h) != (160, 160):
        raise RuntimeError(f"heart-mask.png must be 160×160, got {w}×{h}")

    heart_core: List[List[bool]] = [
        [rgba_at(ref, (x, y))[3] > 128 for x in range(w)]
        for y in range(h)
    ]
    # radius=6 covers: 2px for the heart's own anti-aliased edge PLUS ~4px of
    # transition where the couple-canvas person is noticeably dimmer than the
    # standalone fill.  Without this wider margin a visible shadow/seam appears
    # at the left boundary of the heart zone.
    heart_full = dilate_mask(heart_core, radius=2)
    heart_fill = dilate_mask(heart_core, radius=HEART_FILL_RADIUS)
    return heart_core, heart_full, heart_fill


def dilate_mask(mask: List[List[bool]], radius: int = 1) -> List[List[bool]]:
    h = len(mask)
    w = len(mask[0])
    out = [[False] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            if not mask[y][x]:
                continue
            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):
                    nx = x + dx
                    ny = y + dy
                    if 0 <= nx < w and 0 <= ny < h:
                        out[ny][nx] = True
    return out


def save_mask_png(mask: List[List[bool]], out_path: Path) -> None:
    h = len(mask)
    w = len(mask[0])
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for y in range(h):
        for x in range(w):
            if mask[y][x]:
                img.putpixel((x, y), (255, 255, 255, 255))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)


def alpha_bounds(img: Image.Image, y_max: int | None = None) -> Tuple[int, int, int, int]:
    w, h = img.size
    xs: List[int] = []
    ys: List[int] = []
    for y in range(h):
        if y_max is not None and y > y_max:
            continue
        for x in range(w):
            if rgba_at(img, (x, y))[3] > ALPHA_THRESHOLD:
                xs.append(x)
                ys.append(y)
    if not xs:
        raise ValueError("Missing alpha bounds for reference image")
    return min(xs), max(xs), min(ys), max(ys)


def mask_bounds_with_limit(mask: List[List[bool]], y_max: int | None = None) -> Tuple[int, int, int, int]:
    xs: List[int] = []
    ys: List[int] = []
    for y, row in enumerate(mask):
        if y_max is not None and y > y_max:
            continue
        for x, value in enumerate(row):
            if value:
                xs.append(x)
                ys.append(y)
    if not xs:
        raise ValueError("Missing bounds for target mask")
    return min(xs), max(xs), min(ys), max(ys)


def side_head_mask(img: Image.Image, side: str) -> List[List[bool]]:
    w, h = img.size
    minx, maxx, _, _ = alpha_bounds(img, y_max=UPPER_HEAD_Y_MAX)
    center_x = (minx + maxx) // 2
    mask = [[False] * w for _ in range(h)]
    for y in range(h):
        if y > UPPER_HEAD_Y_MAX:
            continue
        for x in range(w):
            if rgba_at(img, (x, y))[3] <= ALPHA_THRESHOLD:
                continue
            if side == "right" and x < center_x - SIDE_PAD:
                continue
            if side == "left" and x > center_x + SIDE_PAD:
                continue
            mask[y][x] = True
    return mask


def mask_bounds(mask: List[List[bool]]) -> Tuple[int, int, int, int]:
    xs: List[int] = []
    ys: List[int] = []
    for y, row in enumerate(mask):
        for x, value in enumerate(row):
            if value:
                xs.append(x)
                ys.append(y)
    if not xs:
        raise ValueError("Missing bounds for shifted mask")
    return min(xs), max(xs), min(ys), max(ys)


def shift_image(img: Image.Image, dx: int, dy: int = 0) -> Image.Image:
    out = Image.new("RGBA", img.size)
    out.paste(img, (dx, dy))
    return out


def make_crop_filler(src: Image.Image, width: int, height: int, dx: int = 0, dy: int = 0) -> Image.Image:
    """Crop width×height from the top-right of src and place it on a 160×160 canvas.

    The crop is taken from (160-width, 0, 160, height) and pasted at the same
    position shifted by (dx, dy) so pixel positions can be nudged if needed.
    """
    sw, sh = src.size
    x0 = sw - width
    region = src.crop((x0, 0, sw, height))
    canvas = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    canvas.paste(region, (x0 + dx, dy))
    return canvas


def align_reference_to_target(
    ref: Image.Image,
    target_mask: List[List[bool]],
    split_x: int,
    ox_override: int | None = None,
    oy_override: int | None = None,
    sz_override: int | None = None,
) -> Image.Image:
    """Scale reference down to couple-person size and position to match the left person.

    Each person in a couple appears at roughly STANDALONE_SCALED_SIZE×STANDALONE_SCALED_SIZE
    rather than the full 160×160 of a standalone emoji.  Resize first, then align:
      ox — right-edge alignment at HEART_BOTTOM: aligns the standalone's body right
             edge at the heart-bottom transition row to the couple person's body right
             edge there.  This corrects the ~5px overshoot that centroid gives because
             the standalone’s head hair is proportionally wider than the couple person's.
      oy — head-top alignment (first opaque row in each).
    """
    w, h = ref.size  # 160×160

    # Resize to couple-equivalent size so the silhouette naturally fits within the person's bounds.
    sz = sz_override if sz_override is not None else STANDALONE_SCALED_SIZE
    scaled = ref.resize((sz, sz), Image.LANCZOS)

    scaled_alpha: List[List[bool]] = [
        [rgba_at(scaled, (x, y))[3] > ALPHA_THRESHOLD for x in range(sz)]
        for y in range(sz)
    ]

    # ox: align right edges at HEART_BOTTOM (first body row below heart zone).
    # Using right-edge rather than centroid avoids the wider-head overshoot.
    hb_row = min(HEART_BOTTOM, len(target_mask) - 1)
    target_hb_xs: List[int] = [x for x in range(len(target_mask[hb_row])) if target_mask[hb_row][x]]
    scaled_hb_y = min(int(round(HEART_BOTTOM * sz / 160)), sz - 1)
    ref_hb_xs: List[int] = [x for x in range(sz) if scaled_alpha[scaled_hb_y][x]]
    if target_hb_xs and ref_hb_xs:
        ox = int(round(max(target_hb_xs) - max(ref_hb_xs)))
    else:
        # Fallback: centroid
        ref_body_xs = [x for y in range(scaled_hb_y, sz) for x in range(sz) if scaled_alpha[y][x]]
        target_body_xs = [x for y in range(HEART_BOTTOM, len(target_mask)) for x in range(len(target_mask[0])) if target_mask[y][x]]
        ref_cx = sum(ref_body_xs) / len(ref_body_xs) if ref_body_xs else sz / 2
        target_cx = sum(target_body_xs) / len(target_body_xs) if target_body_xs else split_x / 2
        ox = int(round(target_cx - ref_cx))
    # Small empirical correction: right-edge alignment at HEART_BOTTOM overshoots ~2px left.
    ox += 2

    # oy: align head tops (first opaque row in each).
    ref_top_y = next((y for y in range(sz) if any(scaled_alpha[y])), 0)
    target_top_y = next(
        (y for y in range(len(target_mask)) if any(target_mask[y])),
        ref_top_y,
    )
    oy = target_top_y - ref_top_y

    # Apply per-category overrides when provided.
    if ox_override is not None:
        ox = ox_override
    if oy_override is not None:
        oy = oy_override

    print(f"    align: ox={ox}, oy={oy}, sz={sz}")

    # Paste scaled image onto a 160×160 transparent canvas.
    canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    canvas.paste(scaled, (ox, oy))
    return canvas


def alpha_mask(img: Image.Image) -> List[List[bool]]:
    w, h = img.size
    mask = [[False] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            if rgba_at(img, (x, y))[3] > ALPHA_THRESHOLD:
                mask[y][x] = True
    return mask


def composite_over(top: RGBA, bottom: RGBA) -> RGBA:
    """Alpha-composite top over bottom (Porter-Duff 'over' operator)."""
    a_t = top[3] / 255.0
    a_b = bottom[3] / 255.0
    a_out = a_t + a_b * (1.0 - a_t)
    if a_out == 0.0:
        return (0, 0, 0, 0)
    r = int((top[0] * a_t + bottom[0] * a_b * (1.0 - a_t)) / a_out)
    g = int((top[1] * a_t + bottom[1] * a_b * (1.0 - a_t)) / a_out)
    b = int((top[2] * a_t + bottom[2] * a_b * (1.0 - a_t)) / a_out)
    return (min(r, 255), min(g, 255), min(b, 255), min(int(a_out * 255), 255))


def _is_stray_heart_px(px: RGBA) -> bool:
    """True if px looks like a heart-red pixel that doesn't belong to a person.

    When a swap shifts the geodesic splits, heart pixels from the original
    heart zone can end up outside the heart_full mask.  This detector lets
    the ownership branches reroute them cleanly instead of painting red
    artefacts onto the person tiles.

    Heart red is highly saturated and symmetric (G ≈ B, both << R).
    Skin/hair pixels have G >> B (yellow-brown bias) so they are not caught.
    """
    r, g, b, a = px
    return (
        a > ALPHA_THRESHOLD
        and r > 200
        and r > g + 90
        and r > b + 90
    )


def neighbor_owned(mask: List[List[bool]], x: int, y: int, radius: int = 2) -> bool:
    h = len(mask)
    w = len(mask[0])
    for dy in range(-radius, radius + 1):
        ny = y + dy
        if ny < 0 or ny >= h:
            continue
        for dx in range(-radius, radius + 1):
            nx = x + dx
            if nx < 0 or nx >= w:
                continue
            if mask[ny][nx]:
                return True
    return False


def remap_person_canvases(
    src: Image.Image,
    desired_left_person: str,
    desired_right_person: str,
    source_visual_left_person: str,
    source_visual_right_person: str,
) -> Tuple[Image.Image, Image.Image]:
    left_split, right_split = split_pair(src)

    swap = False
    if (
        desired_left_person != desired_right_person
        and source_visual_left_person != source_visual_right_person
    ):
        if (
            desired_left_person == source_visual_right_person
            and desired_right_person == source_visual_left_person
        ):
            swap = True
        elif (
            desired_left_person == source_visual_left_person
            and desired_right_person == source_visual_right_person
        ):
            swap = False
        else:
            raise ValueError(
                "Desired output identities do not match source visual identities: "
                f"desired=({desired_left_person},{desired_right_person}) "
                f"source=({source_visual_left_person},{source_visual_right_person})"
            )

    if not swap:
        return left_split, right_split

    try:
        lminx, lmaxx, lminy, _ = alpha_bounds(left_split)
        rminx, rmaxx, rminy, _ = alpha_bounds(right_split)
    except ValueError:
        return left_split, right_split

    lcx = (lminx + lmaxx) / 2
    rcx = (rminx + rmaxx) / 2

    # Source visual order is reversed relative to desired output order.
    # Shift each person into the opposite side slot before classification.
    desired_left_canvas = shift_image(right_split, int(round(lcx - rcx)), lminy - rminy)
    desired_right_canvas = shift_image(left_split, int(round(rcx - lcx)), rminy - lminy)
    return desired_left_canvas, desired_right_canvas


def apply_rules(
    src: Image.Image,
    kind: str,
    heart_core: List[List[bool]],
    heart_full: List[List[bool]],
    heart_fill: List[List[bool]],
    filler_mask: List[List[bool]],
    left_person_canvas: Image.Image,
    right_person_canvas: Image.Image,
    left_ref: Image.Image,
    ox_override: int | None = None,
    oy_override: int | None = None,
    sz_override: int | None = None,
    filler_top_crop: int = 0,
    left_filler: Image.Image | None = None,
) -> Tuple[Image.Image, Image.Image]:
    """Build left and right outputs with deterministic mask ownership and heart handling.

    Left tile rule:
      heart_fill zone (heart_core dilated 6px) — all pixels in this area are
        painted over by the heart in the source.  Replace from the scaled+positioned
        standalone reference; composite semi-transparent standalone edge pixels over
        the couple canvas so the output stays fully opaque.
      outside heart_fill — couple canvas directly; stray heart pixels (from swap
        shifts) fall back to standalone; unclaimed pixels follow the split valley.

    Right tile rule: heart_core → src pixel; heart_full fringe → right-person canvas;
                    outside heart_full → ownership/tie-break as before.
    """
    src = src.convert("RGBA")
    left_ref = left_ref.convert("RGBA")
    w, h = src.size

    split_x = find_valley(src)

    left_owner = alpha_mask(left_person_canvas)
    # Exclude heart_full (radius=2) pixels from the alignment target.  Using the
    # full heart_fill (radius=6) here would break oy: couple pixels at y=4-28
    # outside heart_core but inside heart_fill would make target_top_y=4 instead
    # of 29, shifting the standalone 25 rows too high.
    left_owner_for_align = [
        [left_owner[y][x] and not heart_full[y][x] for x in range(w)]
        for y in range(h)
    ]
    aligned_left_ref = align_reference_to_target(
        left_ref, left_owner_for_align, split_x, ox_override, oy_override, sz_override
    )

    right_owner = alpha_mask(right_person_canvas)

    left_out = Image.new("RGBA", (w, h))
    right_out = Image.new("RGBA", (w, h))
    transparent: RGBA = (0, 0, 0, 0)

    for y in range(h):
        for x in range(w):
            point = (x, y)
            src_pixel = rgba_at(src, point)

            # --- LEFT TILE (base pass: couple canvas only) ---
            # The standalone filler is composited on top after the loop.
            lp = rgba_at(left_person_canvas, point)
            if lp[3] > ALPHA_THRESHOLD and not _is_stray_heart_px(lp):
                left_out.putpixel(point, lp)
            else:
                left_out.putpixel(point, transparent)

            # --- RIGHT TILE ---
            if heart_core[y][x]:
                right_out.putpixel(point, src_pixel)
            elif heart_full[y][x]:
                rp = rgba_at(right_person_canvas, point)
                right_out.putpixel(point, rp if rp[3] > ALPHA_THRESHOLD else transparent)
            else:
                owns_left = left_owner[y][x]
                owns_right = right_owner[y][x]
                if owns_right and not owns_left:
                    canvas_px = rgba_at(right_person_canvas, point)
                    right_out.putpixel(point, transparent if _is_stray_heart_px(canvas_px) else canvas_px)
                elif owns_left and not owns_right:
                    right_out.putpixel(point, transparent)
                elif owns_left and owns_right:
                    if x <= split_x:
                        right_out.putpixel(point, transparent)
                    else:
                        canvas_px = rgba_at(right_person_canvas, point)
                        right_out.putpixel(point, transparent if _is_stray_heart_px(canvas_px) else canvas_px)
                else:
                    if src_pixel[3] <= ALPHA_THRESHOLD:
                        right_out.putpixel(point, transparent)
                    else:
                        near_left = neighbor_owned(left_owner, x, y)
                        near_right = neighbor_owned(right_owner, x, y)
                        if near_right and not near_left:
                            right_out.putpixel(point, src_pixel)
                        elif x > split_x:
                            right_out.putpixel(point, src_pixel)
                        else:
                            right_out.putpixel(point, transparent)

    # Blank top rows of the standalone filler before compositing.
    composited_ref = aligned_left_ref.copy()
    if filler_top_crop > 0:
        composited_ref.paste((0, 0, 0, 0), (0, 0, composited_ref.width, filler_top_crop))

    # Mask the standalone filler to filler_mask zone (independently tunable via
    # FILLER_MASK_RADIUS) and clear the base inside heart_fill so couple-canvas
    # heart/kiss pixels don't show through.
    for fy in range(h):
        for fx in range(w):
            if not filler_mask[fy][fx]:
                composited_ref.putpixel((fx, fy), (0, 0, 0, 0))
            if heart_fill[fy][fx]:
                left_out.putpixel((fx, fy), (0, 0, 0, 0))

    # Composite the heart-masked standalone filler on top of the couple-canvas base.
    left_out = Image.alpha_composite(left_out, composited_ref)

    if left_filler is not None:
        # Composite the top-right crop from the couple source onto the finished left
        # tile. This is applied after the pixel loop so it covers the entire tile —
        # including areas above the heart zone (e.g. eyebrows) that are sourced from
        # left_person_canvas rather than the standalone filler.
        left_out = Image.alpha_composite(left_out, left_filler.convert("RGBA"))

    return left_out, right_out


def generate_extra_images(heart_core: List[List[bool]]) -> None:
    """Write extra/images/160/ files consumed by whatsapp.py as fallback sources.

    Produces two groups:
    - Per-skin direction tiles for all CATEGORIES × SKINS:
        {gender}{tone_suffix}_{kind_code}.{l|r}.png
    - Silhouette placeholders (default skin, one per category):
        silhouette_{gender}_{kind_code}.{l|r}.png
          Left silhouette : all opaque pixels → mid-gray
          Right silhouette: mid-gray body, original colours preserved in heart_core region
    """
    EXTRA_IMAGES_DST.mkdir(parents=True, exist_ok=True)

    for category, (kind, gender, _) in CATEGORIES.items():
        kind_code = KIND_CODES[kind]

        for slot, tone in SKINS:
            tone_part = f"_{tone}" if tone else ""
            left_path = DST / category / f"left-{slot}.png"
            right_path = DST / category / f"right-{slot}.png"
            if not left_path.exists() or not right_path.exists():
                print(f"  Warning: missing tiles for {category}/{slot}, skipping extra/images output")
                continue

            left_img = Image.open(left_path).convert("RGBA")
            right_img = Image.open(right_path).convert("RGBA")
            left_img.save(EXTRA_IMAGES_DST / f"{gender}{tone_part}_{kind_code}.l.png")
            right_img.save(EXTRA_IMAGES_DST / f"{gender}{tone_part}_{kind_code}.r.png")

        # Silhouette uses default skin (slot 'd') only.
        left_d = Image.open(DST / category / "left-d.png").convert("RGBA")
        right_d = Image.open(DST / category / "right-d.png").convert("RGBA")

        sil_left = to_silhouette(left_d)
        sil_right = to_silhouette(right_d)
        # Restore original colours in the heart/kiss zone on the right silhouette.
        w, h = right_d.size
        for y in range(h):
            for x in range(w):
                if heart_core[y][x]:
                    sil_right.putpixel((x, y), cast(RGBA, right_d.getpixel((x, y))))

        sil_left.save(EXTRA_IMAGES_DST / f"silhouette_{gender}_{kind_code}.l.png")
        sil_right.save(EXTRA_IMAGES_DST / f"silhouette_{gender}_{kind_code}.r.png")
        print(f"{category}: wrote {len(SKINS) * 2} tiles + 2 silhouettes to {EXTRA_IMAGES_DST}")


def main() -> None:
    identity_overrides = load_identity_overrides()
    heart_core, heart_full, heart_fill = build_shared_heart_mask()

    for category, (kind, left_person, right_person) in CATEGORIES.items():
        out_dir = DST / category
        out_dir.mkdir(parents=True, exist_ok=True)

        for slot, tone in SKINS:
            fill_radius = FILL_RADIUS_OVERRIDES.get(f"{category}/{slot}", FILL_RADIUS_OVERRIDES.get(category, HEART_FILL_RADIUS))
            current_heart_fill = heart_fill if fill_radius == HEART_FILL_RADIUS else dilate_mask(heart_core, radius=fill_radius)
            filler_radius = FILLER_MASK_OVERRIDES.get(f"{category}/{slot}", FILLER_MASK_OVERRIDES.get(category, FILLER_MASK_RADIUS))
            current_filler_mask = current_heart_fill if filler_radius == fill_radius else dilate_mask(heart_core, radius=filler_radius)
            slot_overrides = identity_overrides[category][slot]
            source_visual_left = slot_overrides["visual_left"]
            source_visual_right = slot_overrides["visual_right"]

            src_name = couple_filename(category, kind, left_person, right_person, tone)
            src_path = COUPLE_SRC / src_name
            if not src_path.exists():
                raise FileNotFoundError(
                    f"Missing canonical couple source: {src_path}. Refresh images/160 first."
                )

            single_name = single_filename(
                HEART_FILLER_REF.get(f"{category}/{slot}", HEART_FILLER_REF.get(category, left_person)),
                tone,
            )
            single_path = SINGLE_SRC / single_name
            if not single_path.exists():
                raise FileNotFoundError(f"Missing single-person reference: {single_path}")

            src_img = Image.open(src_path).convert("RGBA")
            if src_img.size != (160, 160):
                raise RuntimeError(f"Unexpected couple size for {src_path}: {src_img.size}")

            left_ref = Image.open(single_path).convert("RGBA")
            if left_ref.size != (160, 160):
                raise RuntimeError(f"Unexpected single size for {single_path}: {left_ref.size}")

            left_person_canvas, right_person_canvas = remap_person_canvases(
                src_img,
                desired_left_person=left_person,
                desired_right_person=right_person,
                source_visual_left_person=source_visual_left,
                source_visual_right_person=source_visual_right,
            )

            crop_spec = CROP_FILLER.get(f"{category}/{slot}", CROP_FILLER.get(category))
            left_filler = make_crop_filler(src_img, *crop_spec) if crop_spec is not None else None

            left_img, right_img = apply_rules(
                src_img,
                kind,
                heart_core,
                heart_full,
                current_heart_fill,
                current_filler_mask,
                left_person_canvas,
                right_person_canvas,
                left_ref,
                *ALIGN_OVERRIDES.get(f"{category}/{slot}", ALIGN_OVERRIDES.get(category, (None, None, None))),
                filler_top_crop=FILLER_TOP_CROP_OVERRIDES.get(f"{category}/{slot}", FILLER_TOP_CROP_OVERRIDES.get(category, FILLER_TOP_CROP)),
                left_filler=left_filler,
            )

            left_out = out_dir / f"left-{slot}.png"
            right_out = out_dir / f"right-{slot}.png"
            left_img.save(left_out)
            right_img.save(right_out)
            # Keep per-slot mask files in sync (same mask, just stamped for each slot)
            save_mask_png(heart_core, HEART_MASK_DST / category / f"heart-core-{slot}.png")
            save_mask_png(heart_full, HEART_MASK_DST / category / f"heart-full-{slot}.png")
            print(f"{category} {slot}: {src_name} -> {left_out.name}, {right_out.name}")

    generate_extra_images(heart_core)
    print("Done")


if __name__ == "__main__":
    main()
