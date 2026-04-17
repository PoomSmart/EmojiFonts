"""Generate person-half PNGs for couple-kissing emoji.

Source images  →  output halves
  1f48f{skin}                            →  1f9d1{skin}_1f48b.l/r  +  1f469{skin}_1f48b.l  +  1f468{skin}_1f48b.r
  1f468_200d_2764_200d_1f48b_200d_1f468  →  1f468{skin}_1f48b.l/r  (man+man kiss)
  1f469_200d_2764_200d_1f48b_200d_1f469  →  1f469{skin}_1f48b.l/r  (woman+woman kiss)

Run from catrinity/extra/.
"""

from shared import SKINS, extra_images, get_ppems, main_images, split_png, to_silhouette

for ppem in get_ppems():
    src = main_images(ppem)
    dst = extra_images(ppem)

    # ── Neutral/gendered couple kissing (1f48f) ───────────────────────────────
    for skin in SKINS:
        pair = split_png(src / f"1f48f{skin}.png")
        if pair is None:
            continue
        left, right = pair
        left.save(dst / f"1f9d1{skin}_1f48b.l.png")
        right.save(dst / f"1f9d1{skin}_1f48b.r.png")
        left.save(dst / f"1f469{skin}_1f48b.l.png")
        right.save(dst / f"1f468{skin}_1f48b.r.png")

    pair = split_png(src / "1f48f.png")
    if pair is not None:
        sl, sr = pair
        to_silhouette(sl).save(dst / "silhouette_1f9d1_1f48b.l.png")
        to_silhouette(sr).save(dst / "silhouette_1f9d1_1f48b.r.png")
        to_silhouette(sl).save(dst / "silhouette_1f469_1f48b.l.png")
        to_silhouette(sr).save(dst / "silhouette_1f468_1f48b.r.png")

    # ── Man+man kiss (catrinity_render strips fe0f) ───────────────────────────
    mm_base = "1f468_200d_2764_200d_1f48b_200d_1f468"
    for skin in SKINS:
        pair = split_png(src / f"{mm_base}{skin}.png")
        if pair is None:
            continue
        left, right = pair
        left.save(dst / f"1f468{skin}_1f48b.l.png")
        right.save(dst / f"1f468{skin}_1f48b.r.png")

    pair = split_png(src / f"{mm_base}.png")
    if pair is not None:
        sl, sr = pair
        to_silhouette(sl).save(dst / "silhouette_1f468_1f48b.l.png")
        to_silhouette(sr).save(dst / "silhouette_1f468_1f48b.r.png")

    # ── Woman+woman kiss ──────────────────────────────────────────────────────
    ww_base = "1f469_200d_2764_200d_1f48b_200d_1f469"
    for skin in SKINS:
        pair = split_png(src / f"{ww_base}{skin}.png")
        if pair is None:
            continue
        left, right = pair
        left.save(dst / f"1f469{skin}_1f48b.l.png")
        right.save(dst / f"1f469{skin}_1f48b.r.png")

    pair = split_png(src / f"{ww_base}.png")
    if pair is not None:
        sl, sr = pair
        to_silhouette(sl).save(dst / "silhouette_1f469_1f48b.l.png")
        to_silhouette(sr).save(dst / "silhouette_1f469_1f48b.r.png")
