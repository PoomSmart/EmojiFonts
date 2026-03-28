# morx Table — AppleColorEmoji Modifications

This document explains how the `morx` (Extended Glyph Metamorphosis) table works in
AppleColorEmoji, and details the modifications made by `inject_neutral_couple_silhouette.py`.

---

## Background: what is morx?

`morx` is an Apple-specific OpenType/AAT table that drives **glyph substitution and
rearrangement** during text layout.  It is the primary mechanism Apple uses to map
emoji Unicode sequences (ZWJ sequences, skin-tone modifier sequences, etc.) to the
composite glyph IDs stored in the font.

### Chains and subtables

A `morx` table contains one or more **MorphChains**.  AppleColorEmoji has a single
chain.  Each chain holds an ordered list of **MorphSubtables**.  Subtables are applied
left-to-right; each one can transform the current glyph run before passing it to the
next.

Every subtable carries a `SubFeatureFlags` bitmask.  The rendering engine enables a
set of feature flags based on context (e.g. normal rendering, silhouette rendering for
Messages app contact photos).  A subtable only fires when its flags are a subset of the
currently active flags.

### Subtable types used in AppleColorEmoji

| MorphType | Name | What it does |
|---|---|---|
| 1 | ContextualMorph | State-machine-driven per-glyph substitution with mark/current register |
| 2 | LigatureMorph | State-machine-driven multi-glyph → single-glyph ligature formation |
| 4 | NoncontextualMorph | Simple one-to-one glyph substitution table (lookup) |

### SubFeatureFlags in AppleColorEmoji

The silhouette feature is split across three flags:

| Flag | Meaning |
|---|---|
| `0x00000001` | Always active (normal rendering) |
| `0x00000020` | Left-person silhouette |
| `0x00000040` | Right-person silhouette |

Subtables with flags `0x01` fire in all rendering contexts.  Subtables with flags
`0x20` or `0x40` fire only when the engine is rendering a couple emoji for the
Messages silhouette feature (one person gray, the other in colour).

---

## The original morx chain structure

The single MorphChain in AppleColorEmoji (iOS) originally contains 26 subtables
(indices 0–25 after our patch is applied; 0–25 before as well, since our insertion
preserves count by shifting).  The subtables most relevant to couple handling:

| Original index | Flags | Type | Role |
|---|---|---|---|
| 0 | `0x01` | NoncontextualMorph | Initial identity / normalisation pass |
| 1–6 | `0x01`–`0x04` | LigatureMorph | Various ZWJ ligature formations |
| **7** | `0x01` | **LigatureMorph** | **NN skin-tone couple** — forms `u1F9D1+skin+ZWJ+u1F91D+ZWJ+u1F9D1+skin` → composite `u1F9D1_u1F91D_u1F9D1.XY` |
| **9** | `0x01` | **LigatureMorph** | **NN neutral couple** — forms `u1F9D1+ZWJ+u1F91D+ZWJ+u1F9D1` → `u1F9D1_u1F91D_u1F9D1.66` |
| 14 | `0x01` | ContextualMorph | Person contextual tagging (pre-pass) |
| 15 | `0x01` | ContextualMorph | Tags `u1F468/9/9D1.X` → `.L`/`.R` for heart, kiss, and wrestling couples |
| 16 | `0x01` | LigatureMorph | Forms heart/kiss composite from `.L+ZWJ+♥+ZWJ+.R` |
| 17–22 | `0x08`–`0x10` | Various | Other feature variants |
| **23** | **`0x20`** | **NoncontextualMorph** | **Left silhouette** — maps left-person half-glyph → `silhouette.ML` |
| **24** | **`0x40`** | **NoncontextualMorph** | **Right silhouette** — maps right-person half-glyph → `silhouette.MR` |
| 25 | `0x01` | NoncontextualMorph | Final normalisation pass |

### How FM/FF/MM holding-hands silhouette works (Apple's approach)

For female+male, female+female, and male+male holding-hands couples, subtable [15]
(ContextualMorph, `0x01`) tags the left person glyph with `.L` and the right with `.R`
during its state-machine traversal.  Subtable [23] then maps every `.L` variant to
`silhouette.ML` and subtable [24] maps every `.R` variant to `silhouette.MR`.

Apple does **not** provide silhouette support for neutral-person (`U+1F9D1`) holding-
hands couples — it only added those couples in later OS versions and never patched the
silhouette pipeline for them.

---

## Our modification: NN couple silhouette injection

### The problem

The NN holding-hands ZWJ sequence (`U+1F9D1 [skin] U+200D U+1F91D U+200D U+1F9D1 [skin]`)
is resolved to a composite glyph by subtable [7] (LigatureMorph, always active).
By the time the silhouette subtables [23]/[24] process the glyph stream, the entire
sequence has already been collapsed into a single composite such as
`u1F9D1_u1F91D_u1F9D1.11`.  Apple's subtables [23] and [24] have no entries for any
of these composites — they left them as identity pass-throughs.

### The solution

We patch the two existing NoncontextualMorph silhouette subtables to map each of the
26 composite glyphs to a new per-combination silhouette glyph.  This works because:

1. Subtable [7] (LigatureMorph, `0x01`) runs in ALL rendering contexts and ligates the
   full sequence into `u1F9D1_u1F91D_u1F9D1.XY` — no intermediate ZWJ, skin, or
   handshake glyphs remain in the stream.
2. Subtable [23] (NoncontextualMorph, `0x20`) then performs a single one-to-one
   substitution: composite → per-XY left-silhouette glyph.
3. Subtable [24] (NoncontextualMorph, `0x40`) does the same for the right silhouette.

The silhouette images are baked composites — both persons are in one image, with the
appropriate half already grayed out.  This matches exactly how Apple handles all other
couple silhouettes.

### New glyphs (52 total)

For each of the 26 skin-tone combinations (XY where X, Y ∈ {1..5} plus `66` for
neutral+neutral):

| Glyph name | Image content |
|---|---|
| `silhouette.u1F9D1.u1F91D.L.XY` | Left person gray, right person in combo XY colours |
| `silhouette.u1F9D1.u1F91D.R.XY` | Right person gray, left person in combo XY colours |

Glyph outlines are cloned from the donor composite `u1F9D1_u1F91D_u1F9D1.66` (empty
placeholder, 800-unit advance).  Actual rendering comes from the sbix PNG strikes.

### NoncontextualMorph patches

**Left-silhouette subtable (`0x20`):**
```
u1F9D1_u1F91D_u1F9D1.XY  →  silhouette.u1F9D1.u1F91D.L.XY   (for all 26 XY)
```

**Right-silhouette subtable (`0x40`):**
```
u1F9D1_u1F91D_u1F9D1.XY  →  silhouette.u1F9D1.u1F91D.R.XY   (for all 26 XY)
```

**Identity pass-through subtables** (all others with `silhouette.ML → silhouette.ML`):
All 52 new glyphs are added as self-mappings so they survive unmodified through the
chain when silhouette features are not active.

### Image generation

`make_neutral_couple_silhouette.py` generates the 52 per-ppem PNG files from existing
source images.  For each couple image `u1F9D1_u1F91D_u1F9D1.XY.png` it produces:

- `.L.XY`: full couple composited with a left-half gray overlay (sampled from
  `silhouette.ML`) plus a clasped-hand correction from the right half of `silhouette.ML`.
- `.R.XY`: full couple composited with a right-half gray overlay (sampled from
  `silhouette.ML`) plus a clasped-hand correction from the left half of `silhouette.MR`.

---

## Relevant scripts

| Script / CLI | What it touches |
|---|---|
| `make_neutral_couple_silhouette.py` | Generates 52 per-ppem silhouette PNG files from couple + ML/MR reference images |
| `inject_neutral_couple_silhouette.py` (`emojifonts-inject-silhouette`) | Adds 52 glyphs, injects PNGs into sbix, patches NoncontextualMorph subtables [23]/[24] |
| `apple-prepare.sh` | Calls `make_neutral_couple_silhouette.py` then `emojifonts-inject-silhouette` during font preparation |
| `tests/test_cli_tools.py` | Regression tests: verifies glyph presence, sbix PNG injection, and morx mapping correctness |
