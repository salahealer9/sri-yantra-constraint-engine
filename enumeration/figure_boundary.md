# Validated-constructor boundary for the plane Śrī Yantra figure

**Provenance note — forward record for the figure / viewer project**
Author: Salah-Eddin Gherbi (ORCID 0009-0005-4017-1095)
Scope: Rao (1998) **plane** form only; all checks within `B_plane`.
Engine: corrected plane chain (`sriyantra_plane.chain`), constructor (`figure_coords.figure_coordinates`).
Engine commit: `0baa2c5` (tag `dataset-v1.0.0`)

## Purpose

This note records *where the validated coordinate constructor terminates*, so the
figure / viewer project inherits the exact boundary rather than rediscovering it.
It is a forward note for the repository. It does **not** correct the enumeration
results note: that paper's distinct-figure count (128) was computed on the deposited
27-point subset and is an exact, rigorous lower bound on that subset; the two
additional validations below tighten an already-exact bound and change no published
number.

## What the constructor reconstructs

The §7 metric point set is the 30 points P0–P10 together with intersection points
1–19. The deposited constructor validated 27 of these (omitting P5, point 14, and
point 15). This session pins two more, both inside the metric set:

- **P5 = d − U₇.** The fifth interior baseline is the height of points 7 and 14.
- **Point 14 = iy(P8, point 10, d − U₇)** — i.e. point 14 lies on the existing
  **P8→10** Śiva side, at the P5 baseline. Validated against the chain's `x14`.

Validated coverage of the metric set is therefore now **29 of 30**. The single
remaining gap among the 30 metric points is **point 15**.

Additionally, the eighth primary triangle was identified and validated:

- **Point 11a = iy(P2, point 13, −g).** Point 11a lies on the **P2 Śakti side**,
  which is the line from apex P2 through point 13. Validated against the chain's
  `x11a`.

### Six-root residuals  (max |x_constructed| − |x_chain|)

| root (subset) | point 14 on P8→10 | point 11a on P2–13 |
|---|---|---|
| {1,2,3,4,8}   | 5.55e-17 | 5.55e-17 |
| {1,2,3,10,15} | 5.55e-17 | 0.00e+00 |
| {1,2,4,5,10}  | 0.00e+00 | 2.78e-17 |
| {1,2,5,6,19}  | 0.00e+00 | 5.55e-17 |
| {1,2,6,14,19} | 5.55e-17 | 8.33e-17 |
| {1,2,8,9,20}  | 0.00e+00 | 0.00e+00 |

Both validate to machine precision across all six Rao Table-3 roots (≤ 1 ULP).

## The boundary — what the engine does *not* represent as coordinates

- **Points 20 and 21 are outside the §7 metric set** (they are beyond 1–19,
  auxiliary to the inner triangles only). They are carried by the engine as the
  **scalars U₂₀, U₂₁** (computed for constraints F13–F15), not as (x, y).
- **Point 15** is in the metric set but is likewise absent from the engine's
  coordinate representation; it is the sole remaining metric-point gap.

Consequently the **ninth primary triangle** (fifth Śakti) is not reconstructable
from the chain's coordinate outputs.

### Negative results (recorded so they are not re-attempted)

- The P2 Śakti side **P2–13 does not reach point 16 as its base corner**:
  extending the line to height d + e misses point 16 by ≈ 0.088 (not machine zero).
  The P2 side's *direction* is validated; its top vertex is not a validatable point.
- **No P3-apex triangle side carries two validatable chain points.** The only
  collinear hits through P3 are degenerate — P3, 1, 3, 5 share the −c baseline, so
  their collinearity is the baseline itself, not a triangle side.
- The inner concurrency points (15, 20, 21) sit in the **F13–F15 region** — the same
  region that contained the corrected Q₂₁ transcription error.

## Open problem for the viewer / renderer project

> Can the scalar U₂₀ / U₂₁ machinery (F13–F15) be lifted to a complete coordinate
> realization of Rao's plane Śrī Yantra — i.e. explicit, chain-validated (x, y) for
> points 15, 20, 21 — closing the (b, c, d, e, g) → full-geometry map?

If that map validates end to end across the six roots, the complete nine-triangle
figure becomes admissible (arXiv v2 / journal revision), and the map is itself a
citable artifact: *a validated coordinate realization of Rao's plane Śrī Yantra*.

### Inherited boundary, in one line

P5 = d − U₇ (pinned); point 14 on P8→10 (5.55e-17); P2 side = P2–13 (8.33e-17);
no validatable P3 triangle from the chain; points 20/21 outside the metric set and
point 15 the only remaining metric gap — all three absent from the engine's
coordinate representation, carried instead as U₂₀, U₂₁.
