# Spherical atlas — geometry validation report

**Purpose.** Pre-build gate for the Certified Spherical Atlas viewer. No atlas JSON and no
frontend are produced until this report passes. It verifies that the shipped census bundle is
intact, that its headline counts reproduce, and that the independent geodesic constructor the
viewer will draw from agrees with the certified Gate-4 metadata.

**Checkpoint.** `CENSUS_CHECKPOINT_LAYER1_K12` · engine `de64edfa4979` · dataset DOI
`10.5281/zenodo.21170076`.

## 1. Bundle integrity — PASS

`spherical_roots.jsonl` and `spherical_census.csv` hash to the values recorded in
`spherical_census_manifest.json`:

    spherical_roots.jsonl   fcac94685f6d5367…   MATCH
    spherical_census.csv    a39c7e21ca7137a5…   MATCH

Engine SHA `de64edfa4979…` (frozen reference), 3044 subsets, `gate4_per_root = true`.

## 2. Headline counts — PASS

Recomputed directly from the JSONL (target → recomputed):

    FEASIBLE_CERTIFIED subsets      888  ->  888
    UNRESOLVED_CERT_FAILED           50  ->   50
    UNRESOLVED_NO_CANDIDATE        2106  -> 2106
    certified distinct roots        968  ->  968
    Gate-4 valid roots              525  ->  525
    Gate-4 rejected roots           443  ->  443
    multi-root subsets               77  ->   77
    both-type subsets                26  ->   26

`num_certified_roots == len(roots)` for every feasible subset. 888 + 50 + 2106 = 3044;
525 + 443 = 968.

## 3. Constructor vs census Gate-4 — PASS (968 / 968)

For every certified root, the independent geodesic constructor (`spherical_geo_check.build` +
`gate4`) was run and its valid/rejected verdict compared to the recorded `gate4.valid`:

    closure_tol = 1e-7 :  agree 968/968   disagree 0
    closure_tol = 1e-5 :  agree 968/968   disagree 0

The recorded per-root `gate4.closure_tol` is `1e-7` while the constructor's default is `1e-5`;
the difference produces **no** verdict change, because roots either close far below both tolerances
(machine-solved) or are rejected on ordering/containment, which is tolerance-independent.

## 4. Deterministic test set — PASS

    case                              h        r    a=r-(b+c)  f=r-(d+e)  census  ctor  match
    ------------------------------------------------------------------------------------------
    first Gate-4 VALID             0.3132  1.2575     0.1084     0.0578   valid   valid   ok
    first Gate-4 REJECTED          0.3953  1.1755    -0.1535    -0.2035   reject  reject  ok
    subset (1,2,3,4,6,13) root0    0.3972  1.1736    -0.1616    -0.2121   reject  reject  ok
    subset (1,2,3,4,6,13) root1    0.1982  1.3726     0.3419     0.2539   valid   valid   ok
    3-root (1,2,3,6,7,16) root0    0.7291  0.8417     0.4073     0.4317   valid   valid   ok
    3-root (1,2,3,6,7,16) root1    0.5677  1.0031     0.0668     0.0890   valid   valid   ok
    3-root (1,2,3,6,7,16) root2    0.6180  0.9528     0.4013     0.4224   valid   valid   ok
    min-h root                     0.0085  1.5623     0.0331     0.3091   valid   valid   ok
    max-h root                     1.4909  0.0799     0.0249     0.0177   valid   valid   ok

`h ∈ (0, π/2)` for every case; `r = π/2 − h`; closures ≤ 1.5e-8; residuals ≤ 1.3e-13
(the min-h near-boundary root carries the largest residual, still far below any threshold).
Valid ⟺ `a ≥ 0 and f ≥ 0`; the rejections are ordering/containment violations
(base points leaving `[-r, r]`), consistent with Rao eq. 2.2.

## 5. Findings that shape the generator / viewer

1. **Wide cap range.** `h ∈ [0.0085, 1.4909]` ⇒ `r ∈ [~0.08, ~1.56]`. On a fixed unit sphere,
   figures range from near-hemisphere caps to tiny near-pole caps. The generator must record
   `r` per figure; the viewer needs a frame-to-cap default camera.

2. **Full-figure drawing needs a spherical point-14 lift.** `build()` constructs the validation
   points (closure 11/11a, radial 16–19) but not the full nine-triangle vertex set — points 14
   and 7 are not built (as in the original plane constructor). Before the generator emits drawable
   arcs, add points 14 and 7 as great-circle intersections and round-trip their arcs against
   `chain_sphere`'s `x14`/`x7` to machine precision — the geodesic analogue of the validated
   plane lift.

3. **Closure-tol label.** Record `closure_tol = 1e-7` in the atlas metadata to match the census
   (no verdict impact, but keeps the provenance exact).

## 6. Semantics the viewer must preserve (from the census drafts)

- Presence census, **not** an absence theorem: `INFEASIBLE_CERTIFIED = 0`.
- `unresolved ≠ infeasible`: 2106 = "no certifier-bound candidate under tested budgets k∈{6,12}".
- Gate-4 validity is **per-root metadata**, never a filter on certification; a subset can hold
  both valid and rejected roots (26 such subsets). Never say "this subset is valid/rejected".
- "Rejected" = failed the **registered** Gate-4/Rao ordering-containment test, not "impossible".
- Sidecars (high-cond, super-hemispheric) are audit evidence, **not** census input.

## Verdict

Integrity, counts, and constructor↔metadata agreement all pass. The bundle is sound to build on.
Remaining before the atlas JSON generator emits drawable figures: the spherical point-14/7 lift
(item 5.2), validated to machine precision, then the arc/point schema.

## Addendum — STEP 0 topology correction (recorded 2026-07-04)

The plane-form audit (plane viewer `docs/PLANE_TOPOLOGY_AUDIT.md`, corrected in plane
viewer v1.0.1) found that four of the nine root triangles were rendered with slant sides
**truncated at interior construction crossings** (points 4, 6, 5, 3) instead of
**produced to their Rao-defined corners** (Rao eqs 2.22, 2.24, 2.33, 2.43). The same
truncated table had been ported into the spherical atlas generator. This addendum records
the STEP 0 correction of `roots_to_spherical_atlas_json.py`.

Corrected table (apex → corner, base line), enforced at import by a fail-loud guard
`_assert_rao_topology()` that refuses to emit if the corner set differs from Rao's or if
any of {4, 6, 5, 3} appears as a corner:

    apex P0  -> corner  2  (base line P7, sakti)     apex P10 -> corner  1  (base line P3, siva)
    apex P1  -> corner 18  (base line P8, sakti)     apex P9  -> corner 19  (base line P2, siva)
    apex P2  -> corner 13  (base line P6, sakti)     apex P8  -> corner 10  (base line P4, siva)
    apex P3  -> corner 14  (base line P5, sakti)     apex P7  -> corner 17  (base line P1, siva)
    apex P4  -> corner 16  (base line P9, sakti)

Guard verified two ways: (a) it passes and prints the nine triangles on import with the
corrected table; (b) a negative test that reinstates ("P1","4") makes it raise
AssertionError — the truncated topology can no longer be emitted silently.

Points 4, 6, 5, 3 remain in the emitted point set as **construction/intersection data**
(they are chain-validated positions and are used by the constraints), but they are no
longer used as triangle corners.

**Void notice.** Every spherical visual artifact generated under the truncated table is
void and must not be reused: the previous atlas bundles (digests `ee5a9d59…` and
`2e7650c8…`), all sample renders and screenshots, the SLERP triangle polylines they
contain, the edge-length/area visual diagnostics, the visual-form threshold proposal,
and the blind-review packet. The census itself is unaffected: roots, certificates,
residuals, Krawczyk radii, Gate-4 verdicts, and all headline counts
(968 / 525 / 443 / 949 / 19) involve no triangle drawing.

Scope note: this addendum is the STEP 0 record only. Re-validation of the lift and
round-trip under the corrected topology (STEP 1) and regeneration of any bundle or
review material (STEP 2+) are deliberately not performed here.

## Addendum — STEP 1 verification results (2026-07-04)

STEP 1 checklist against the corrected-topology generator (guard active at import):

1. **Corrected Rao topology in use** — the fail-loud guard prints and passes the nine
   produced-corner triangles on every import; the truncated set {4,6,5,3} is barred from
   corner duty (negative test raises).
2. **Points 7 and 14 still lift correctly** — max arc deviation vs the frozen chain
   1.1e-15 over all 525 valid roots; 0 construction failures; AA-Krawczyk rigorous
   enclosures contain both the numeric and geodesic values on 525/525 (min margin 3.4e-7).
3. **Geometry round-trips against the frozen engine** — faithfulness gate reproduces the
   949 drawable / 19 null split; constructor Gate-4 agrees with census metadata 968/968 at
   closure_tol 1e-7 and 1e-5.
4. **Census counts unchanged** — 3044 subsets, 888 feasible, 968 roots, 525 valid /
   443 rejected; crosstab 525/424/19/0.
5. **Old truncated-topology diagnostics void** — recorded in the STEP 0 addendum above and
   reaffirmed; nothing from the old bundles, renders, spreads, threshold proposal, or
   review packet may be reused.

New result: produced-sides verification (`spherical_lift.verify_produced_sides`) — all
3796 sides lie on their produced great circles to 2.0e-16; truncation points strictly
interior on every valid root (t ∈ [0.379, 0.997], 0/2100 violations); the 187 violations
occur only on Gate-4-rejected roots and are the ordering rejection made geometric.

No bundle regeneration was performed in STEP 1 (deferred to STEP 2+ per instructions).

## Addendum — STEP 2 generator hygiene (2026-07-04)

The generator's embedded first-pass visual-form classifier (thresholds derived from
truncated-topology diagnostics; void per STEP 0/1) has been **removed**, not merely
bypassed. `roots_to_spherical_atlas_json.py` now: (a) computes threshold-free
measurements only (`visual_diagnostics` on the corrected triangles); (b) emits
`visual.form = null` with an explicit pending-calibration note in every drawable
figure; (c) records `visual_form_status` in the manifest in place of the removed
heuristic text and per-class counts.

Verification of the removal: a full inventory diff against the STEP 0 file shows
exactly `-visual_form`, `-VISUAL_FORM_HEURISTIC`, `+VISUAL_FORM_PENDING_NOTE` and no
other change; the TRIANGLES table, fail-loud guard, and all construction functions are
byte-identical to STEP 0 (the guard was re-proven after restoration: prints on import,
raises on a truncated table). Five random rows of the v2 review-packet CSV recompute
identically through the cleaned generator, confirming the packet is consistent with it.

No classifier re-enters the generator until human labels on the corrected v2 review
packet have been compared against candidate model labels and thresholds are signed off.
The v2 packet and judgment sheet used only the measurement path and are unaffected.
