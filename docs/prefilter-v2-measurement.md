# v2 Cone-Edge Pre-filter — Branch-and-Prune Measurement (exploratory)

**Status.** Exploratory measurement. v2 driver = frozen v1.2 `domain_sphere.py`
copied to `domain_sphere_v2_prefilter.py` with the cone-edge analytic pre-filter
wired in behind `USE_CONE_EDGE_PREFILTER`. Frozen v1.2 driver UNCHANGED.

## Wiring soundness (Gate-M + differential)
- Gate-M c3/c4/c5 on v2: PASS, identical to v1.2 (root certifies unique at r<=3e-4;
  c5 307 excluded / 93 split / 0 indeterminate; c3 clean).
- Differential over uniform K=4 grid: the ONLY classify change base->v2 is
  `split -> domain` (704/4096), with 0 changes that are not `->domain`. The
  pre-filter provably only adds earlier exclusions of provably-empty boxes; it
  never alters a valid verdict, certification, or off-root exclusion.

## Head-to-head at equal box budget (400,000 boxes)
| metric | v1.2 base | v2 pre-filter | change |
|---|---|---|---|
| domain-excluded | 7,081 | 45,963 | +38,882 |
| unresolved (max_depth) | 192,848 | 153,978 | -38,870 |
| constraint-excluded | 0 | 0 (->1,312 by 1M boxes) | — |
| queue_left | 143 | 119 | ~same |
| max_depth | 200 | 200 | same |
| certified | 0 | 0 | — |
| throughput | 28,390 box/s | 17,721 box/s | slower/box |

The trade is ~1:1: ~39k boxes the baseline dives on and marks unresolved become
cheap domain exclusions. Slower per box because pruning the invalid bulk raises the
fraction of processed boxes that are expensive valid-region boxes (full ~40-node
chain + cone_F). In the longer 1M-box run, v2 reaches constraint exclusion
(excl 0 -> 1,312) that the baseline never reached (excl stayed 0).

## Verdict on the lever
**Helps, does not close.** Real ~20% reduction in unresolved pressure and the
search finally reaches the productive (constraint-excluding) region. But the
structural wall is unchanged: queue stays ~120 (LIFO depth-first never builds a
frontier), max_depth=200 saturation persists, nothing certifies. At full 3M budget
v2 would still BUDGET-EXHAUST, with more domain exits and some constraint
exclusions. The pre-filter alone does not close the size-six subset.

## What the data says about the NEXT lever
The persistent tiny queue (~120 across both drivers, every box count) is now
arguably the dominant wall. Even with perfect domain exclusion, the depth-first
dive drives boxes to max_depth in a narrow slice rather than breadth-excluding
whole regions. Implication:
  - **Driver order (breadth / best-first, lever 3)** is likely higher-leverage now
    than extending analytic filters — it directly attacks queue starvation and
    max_depth saturation.
  - Full-chain analytic filters (r16..r19 edges) would extend the cone-edge win
    incrementally but will NOT fix queue starvation.
  - Monotone across-inflection enclosures (lever 2) address the boundary-straddle
    boxes that the cone-edge filter cannot exclude.

**Recommendation.** Keep the cone-edge pre-filter (sound, real partial gain). Make
the NEXT exploratory lever the driver order (breadth/best-first), measured the same
way, before or alongside the full-chain analytic extension. Decide full-chain vs
driver from a driver-order measurement.

## Files (exploratory unit)
  domain_sphere_v2_prefilter.py   v1.2 driver + flagged cone-edge pre-filter
  harness_gate_m_345_v2.py        Gate-M c3/c4/c5 on v2 (PASS)
  prefilter-v2-measurement.md     this report

SHA-256 hashes for all files in this unit are recorded in `docs/SHA256SUMS`