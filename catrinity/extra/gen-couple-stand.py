"""Generate person-half PNGs for couple-holding-hands emoji.

Splits the couple PNGs rendered by catrinity_render.py:
  1f46b (woman+man holding hands)  → 1f469{skin}.l  +  1f468{skin}.r
  1f46c (man+man  holding hands)   → 1f468{skin}.l
  1f46d (woman+woman holding hands)→ 1f469{skin}.r
  1f9d1_200d_1f91d_200d_1f9d1     → 1f9d1{skin}.l  +  1f9d1{skin}.r

Also generates silhouette.ml/mr/wl/wr for gen-couple-nn.py.

Run from catrinity/extra/.
"""

from shared import SKINS, extra_images, get_ppems, main_images, split_png, to_silhouette

for ppem in get_ppems():
    src = main_images(ppem)
    dst = extra_images(ppem)

    for skin in SKINS:
        # ── 1f46b  (woman + man holding hands) ──────────────────────────────
        pair = split_png(src / f"1f46b{skin}.png")
        if pair is not None:
            left, right = pair
            left.save(dst / f"1f469{skin}.l.png")
            right.save(dst / f"1f468{skin}.r.png")

        # ── 1f46c  (man + man holding hands) — left half only ────────────────
        pair = split_png(src / f"1f46c{skin}.png")
        if pair is not None:
            left, _ = pair
            left.save(dst / f"1f468{skin}.l.png")

        # ── 1f46d  (woman + woman holding hands) — right half only ───────────
        pair = split_png(src / f"1f46d{skin}.png")
        if pair is not None:
            _, right = pair
            right.save(dst / f"1f469{skin}.r.png")

        # ── neutral person holding hands (1f9d1 ZWJ 1f91d ZWJ 1f9d1) ─────────
        nn_stem = (
            "1f9d1_200d_1f91d_200d_1f9d1"
            if skin == ""
            else f"1f9d1{skin}_200d_1f91d_200d_1f9d1{skin}"
        )
        pair = split_png(src / f"{nn_stem}.png")
        if pair is not None:
            left, right = pair
            left.save(dst / f"1f9d1{skin}.l.png")
            right.save(dst / f"1f9d1{skin}.r.png")

    # ── Man silhouettes (from 1f46c, used by gen-couple-nn.py) ───────────────
    pair = split_png(src / "1f46c.png")
    if pair is not None:
        ml, mr = pair
        to_silhouette(ml).save(dst / "silhouette.ml.png")
        to_silhouette(mr).save(dst / "silhouette.mr.png")

    # ── Woman silhouettes (from 1f46d) ────────────────────────────────────────
    pair = split_png(src / "1f46d.png")
    if pair is not None:
        wl, wr = pair
        to_silhouette(wl).save(dst / "silhouette.wl.png")
        to_silhouette(wr).save(dst / "silhouette.wr.png")
