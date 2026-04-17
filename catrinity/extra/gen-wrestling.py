"""Generate person-half PNGs for wrestlers emoji.

Source images (U+1F93C) and gendered variants:
  1f93c{skin}                  →  1f9d1{skin}_1faef.l/r   (neutral / default)
  1f93c_200d_2642_fe0f{skin}   →  1f468{skin}_1faef.l/r   (men wrestling)
  1f93c_200d_2640_fe0f{skin}   →  1f469{skin}_1faef.l/r   (women wrestling)

Joiner is U+1FAEF, used in Apple's half-glyph naming.

Run from catrinity/extra/.
"""

from shared import SKINS, extra_images, get_ppems, main_images, split_png, to_silhouette

JOINER = "1faef"

for ppem in get_ppems():
    src = main_images(ppem)
    dst = extra_images(ppem)

    for skin in SKINS:
        # Neutral / default: 1f93c
        pair = split_png(src / f"1f93c{skin}.png")
        if pair is not None:
            left, right = pair
            left.save(dst / f"1f9d1{skin}_{JOINER}.l.png")
            right.save(dst / f"1f9d1{skin}_{JOINER}.r.png")

        # Men: 1f93c ZWJ male-sign
        pair = split_png(src / f"1f93c_200d_2642{skin}.png")
        if pair is None:
            pair = split_png(src / f"1f93c_200d_2642_fe0f{skin}.png")
        if pair is not None:
            left, right = pair
            left.save(dst / f"1f468{skin}_{JOINER}.l.png")
            right.save(dst / f"1f468{skin}_{JOINER}.r.png")

        # Women: 1f93c ZWJ female-sign
        pair = split_png(src / f"1f93c_200d_2640{skin}.png")
        if pair is None:
            pair = split_png(src / f"1f93c_200d_2640_fe0f{skin}.png")
        if pair is not None:
            left, right = pair
            left.save(dst / f"1f469{skin}_{JOINER}.l.png")
            right.save(dst / f"1f469{skin}_{JOINER}.r.png")

    # ── No-skin silhouettes ───────────────────────────────────────────────────
    pair = split_png(src / "1f93c.png")
    if pair is not None:
        sl, sr = pair
        to_silhouette(sl).save(dst / f"silhouette_1f9d1_{JOINER}.l.png")
        to_silhouette(sr).save(dst / f"silhouette_1f9d1_{JOINER}.r.png")

    for g, base in [("1f468", "1f93c_200d_2642"), ("1f469", "1f93c_200d_2640")]:
        pair = split_png(src / f"{base}.png")
        if pair is None:
            pair = split_png(src / f"{base}_fe0f.png")
        if pair is not None:
            sl, sr = pair
            to_silhouette(sl).save(dst / f"silhouette_{g}_{JOINER}.l.png")
            to_silhouette(sr).save(dst / f"silhouette_{g}_{JOINER}.r.png")
