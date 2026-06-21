# spherical-amendment-02 — Near-pole seeding completeness (census re-run required)

- **Filed:** _to be GPG-signed and OpenTimestamps-stamped before the corrected census run._
- **Registration amended:** `spherical_preregistration.md` v1.0.0 (+ amendment-01).
- **Nature:** completeness fix to the analysis engine, surfaced by the first full census via the §6 α→0 consistency gate. No decision rule changed.

## Defect (proven, not suspected)

The first full census returned **PLANE_CONTINUATION = 132**, but there are **134**
plane survivors. The two missing survivors are the high-altitude fold cases
**(1,2,8,10,11)** and **(1,2,8,11,19)**, both returned ALGEBRAIC_ONLY with *no valid
figure found at any altitude* — yet, being plane survivors, each must have a valid
in-box figure at the pole. This trips the registered §6 α→0 consistency gate
(survivors must reach an in-box pole limit).

Root cause: the seeding altitude grid topped out at **72°**, while these subsets'
valid figures live only in a band **above** their fold (≈[77.6°,90°] and
≈[81.5°,90°]) — disconnected by the fold from the moderate-altitude seeds. No seed
was ever placed where the figure exists. Seeding each from its own plane root at
h=88° yields a valid, in-box figure immediately, confirming the figures exist and the
gap is purely seeding coverage.

## Fix

The seeding altitude grid is extended into the near-pole band (added 76°, 80°, 84°,
88°). Verified:

- (1,2,8,10,11) → **PLANE_CONTINUATION** [77.6°, 89.7°]
- (1,2,8,11,19) → **PLANE_CONTINUATION** [81.5°, 89.8°]

so all 134 survivors are recovered (§6 consistency restored). The pilot remains
deterministic (identical classification hash `2d80952dbe7b621d`, 7/7, Gate-6 live).
The census runner now self-checks §6 (flags any survivor not reaching an in-box pole).

## Additional completeness gate (generic high-altitude audit)

The fold-survivor lesson is generalized into a **permanent safeguard**, not a one-off
grid patch. Before any **negative** class (ALGEBRAIC_ONLY / ALGEBRAIC_EMPTY) is
finalized, the classifier re-probes the coverage edge (88 deg) with a dense,
stable-seeded budget (`tag="audit"`); if a Gate-4-valid figure is found there, the
subset is re-traced and re-classified, with a recorded note. 88 deg is not
scientifically special — it is the registered coverage edge, and high-altitude-only
branches above a fold are now a demonstrated phenomenon. This makes "no figure found"
mean "none found after an explicit high-altitude audit," strengthening every negative
classification. The audit is toggleable (`--no-audit`) and deterministic.

The census runner is also parallelized (multiprocessing); subsets are independent and
stable-seeded, so results are identical to a sequential run (the canonical hash is
computed from sorted output, order-independent), and the §6 survivor-consistency
self-check, the Gate-6 HALT guard, and resumability are retained.

## Why the first census must be re-run (asymmetric reliability)

The near-pole gap under-samples exactly the region where pole-limit figures live, so
its effect is **one-directional — missed figures, never spurious ones**:

- **POSITIVE classes are sound lower bounds** (figures actually found): the re-run can
  only add to PLANE_CONTINUATION (132→134 already), SPHERICAL_ONLY, POLE_OUT_OF_DOMAIN.
- **NEGATIVE classes are over-counted**: ALGEBRAIC_ONLY (317) and ALGEBRAIC_EMPTY (23)
  include near-pole false negatives and will shrink. **H3 cannot be evaluated** from the
  first run (the 23 empties may be seeding-missed, exactly as (1,2,7,12,17) was).
- **Gate 6 must be re-tested**: an in-box pole limit (the HALT/plane-false-negative
  condition) lives near the pole — precisely the under-sampled band. The first run's
  "no HALT" is therefore **not yet a trustworthy all-clear**; the corrected run is what
  validates census integrity.

## Residual caveat (unchanged §8 spirit)

Even with near-pole seeding, a figure existing only in a razor-thin band above a
fold very close to the pole could still be missed. ALGEBRAIC_EMPTY / ALGEBRAIC_ONLY
therefore remain "no figure found under the registered budget," never "proven empty."
The error direction is conservative (under-counting figures), so the integrity result
is on the safe side.

## Engine hash

- `spherical_existence_mapper.py` — SHA-256 `a0772717e4d07c327e744608bd0abf4f9a50d5f343b07fc3ffc119a7cd8a59af`
- `spherical_census.py` — adds the §6 survivor-consistency self-check
- `spherical_geo_check.py`, `sriyantra.py` — unchanged

Committed, GPG-signed, OpenTimestamps-stamped before the corrected census run.
