"""Generate person-half PNGs for people-with-bunny-ears emoji.

Source images (U+1F46F) and gendered variants:
  1f46f{skin}                  →  1f9d1{skin}_1f430.l/r   (neutral / women default)
  1f46f_200d_2642_fe0f{skin}   →  1f468{skin}_1f430.l/r   (men with bunny ears)
  1f46f_200d_2640_fe0f{skin}   →  1f469{skin}_1f430.l/r   (women with bunny ears)

Joiner is U+1F430 (rabbit face), used in Apple's half-glyph naming.

Run from catrinity/extra/.
"""

from shared import SKINS, extra_images, get_ppems, main_images, split_png, to_silhouette

JOINER = "1f430"

for ppem in get_ppems():
    src = main_images(ppem)
    dst = extra_images(ppem)

    for skin in SKINS:
        # Neutral / women: 1f46f
        pair = split_png(src / f"1f46f{skin}.png")
        if pair is not None:
            left, right = pair
            left.save(dst / f"1f9d1{skin}_{JOINER}.l.png")
            right.save(dst / f"1f9d1{skin}_{JOINER}.r.png")

        # Men: 1f46f ZWJ male-sign (fe0f stripped in filename)
        pair = split_png(src / f"1f46f_200d_2642{skin}.png")
        if pair is None:
            # Alternate form without explicit fe0f suffix
            pair = split_png(src / f"1f46f_200d_2642_fe0f{skin}.png")
        if pair is not None:
            left, right = pair
            left.save(dst / f"1f468{skin}_{JOINER}.l.png")
            right.save(dst / f"1f468{skin}_{JOINER}.r.png")

        # Women: 1f46f ZWJ female-sign
        pair = split_png(src / f"1f46f_200d_2640{skin}.png")
        if pair is None:
            pair = split_png(src / f"1f46f_200d_2640_fe0f{skin}.png")
        if pair is not None:
            left, right = pair
            left.save(dst / f"1f469{skin}_{JOINER}.l.png")
            right.save(dst / f"1f469{skin}_{JOINER}.r.png")

    # ── No-skin silhouettes ───────────────────────────────────────────────────
    pair = split_png(src / "1f46f.png")
    if pair is not None:
        sl, sr = pair
        to_silhouette(sl).save(dst / f"silhouette_1f9d1_{JOINER}.l.png")
        to_silhouette(sr).save(dst / f"silhouette_1f9d1_{JOINER}.r.png")

    for g, base in [("1f468", "1f46f_200d_2642"), ("1f469", "1f46f_200d_2640")]:
        pair = split_png(src / f"{base}.png")
        if pair is None:
            pair = split_png(src / f"{base}_fe0f.png")
        if pair is not None:
            sl, sr = pair
            to_silhouette(sl).save(dst / f"silhouette_{g}_{JOINER}.l.png")
            to_silhouette(sr).save(dst / f"silhouette_{g}_{JOINER}.r.png")
