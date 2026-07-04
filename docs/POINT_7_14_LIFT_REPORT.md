# Spherical point-7 / point-14 lift — validation report

**Task.** Construct Rao points 7 and 14 on the unit sphere (the great-circle analogue of the
validated plane point-14 lift) and validate against the frozen numeric chain (`sriyantra.chain`,
engine `de64edfa4979`) before the atlas generator emits any geometry.

## 1. Construction (module `spherical_lift.py`)

Same unit-sphere frame and conventions as `spherical_geo_check.build` — no new orientation
assumptions. Axis meridian in the x–z plane, `axis(s) = (sin s, 0, cos s)`; a base-line through
`axis(s)` is the great circle spanned by `axis(s)` and `Y=(0,1,0)`.

    point 7  = geodesic(P4→6) ∩ geodesic(P7→5)          # topology of plane ii(P4,6,P7,5)
    P5       = axis( foot(point 7) )                    # P5 is the axial foot of point 7
    point 14 = geodesic(P8→10) ∩ base-line(P5)          # plane iy(P8,10, d−U7), at the P5 foot

Point 7 is not itself a triangle corner; it is constructed to locate `P5` geometrically (its axial
foot equals `d − U7`) so that point 14 — the corner of the fifth Śakti triangle P3→14 — can be built
without recourse to the chain. With 14 added, all nine triangles' vertices are available.

## 2. Antipodal / sign disambiguation rule

Two great circles meet at an antipodal pair; every constructed point 1..19 lies on the **right half
(y > 0)**, so `meet()` selects the intersection with `y > 0`. This rule is unambiguous for every
well-posed (Gate-4-valid) figure — the minimum right-half margin over the emitted set is `1.6e-3`.
It is exactly this rule that breaks on the degenerate rejects (Section 5): when base points are driven
outside `[-r, r]`, the correct point crosses to `y ≤ 0` or the arc wraps past `π/2`, and the meet
lands on the antipode.

## 3. Fidelity to the frozen chain — machine precision (525 / 525 valid roots)

Measured with floor-free metrics (Euclidean chord and `atan2` arc; **not** `gdist = acos(dot)`,
which floors at `acos(1−ULP) ≈ √(2ε) ≈ 2.1e-8`):

    max chord | p7  − chain |     1.10e-14
    max chord | p14 − chain |     1.09e-14
    max foot(P5) − (d − U7)       1.10e-14
    max arc  x7  − chain x7       4.44e-16
    max arc  x14 − chain x14      1.11e-15
    max existing x16..r19 recheck 1.68e-15

Deterministic test set (all pass, including the two rejected cases and both roots of the
both-type subset):

    case                     valid    |x7−chain|   |x14−chain|
    first VALID              true      5.6e-17      2.2e-16
    first REJECTED           false     1.1e-16      1.7e-16
    (1,2,3,4,6,13) root0     false     5.6e-17      1.1e-16
    (1,2,3,4,6,13) root1     true      2.8e-16      3.3e-16
    (1,2,3,6,7,16) root0..2  true      ≤2.8e-17     ≤1.7e-16
    min-h  (h=0.0085)        true      4.4e-16      0.0e+00
    max-h  (h=1.4909)        true      0.0e+00      6.9e-18

## 4. Gate-4 verdict agreement

The geodesic constructor's Gate-4 verdict already matches the census metadata on **968 / 968** roots
(validation report §3). Adding points 7/14 changes no verdict (they are not ordering points).

## 5. Roots requiring special handling — 19 (all Gate-4 rejected)

Across all 968 roots, reconstruction is chain-faithful (`|x7|,|x14| < 1e-8`) on **949**; the
remaining **19 diverge by ≈ π**. Every one of the 19 is Gate-4 **rejected**. They are geometrically
degenerate — base points outside `[-r,r]` and/or arcs past `π/2` — so the right-half meet lands on the
antipode. The trigger is not a single clean `a<0 ∨ f<0` predicate (some divergent rejects have
`a>0`); it is the antipodal/arc-wrap condition itself, which the generator detects **per root** by
round-tripping against the chain.

## 6. Generator geometry gate (rule)

The generator round-trips every root through `spherical_lift` + `spherical_geo_check` against the
chain and emits `geometry {points, arcs}` **only** when faithful:

    chain-faithful (|Δarc| < 1e-8)  -> 949 roots  -> emit points[] (incl. 7, 14) + arcs[]
    degenerate                      ->  19 roots  -> geometry: null, reason recorded

All 19 are rejects, so **no valid figure ever lacks geometry**. The 19 are still first-class atlas
entries (parameters, certificate, Gate-4 reason, evidence) — they are shown without a drawn figure,
consistent with being registered-test rejections.

## 7. Consequences for the schema

The `geometry` block is now specifiable and complete: `points[]` = all validated vertices including
7 and 14; `arcs[]` = great-circle (geodesic) polylines between triangle vertices, which lie on the
construction geodesics by construction and so need no separate validation beyond their endpoints.
The schema may be locked once the arc sampling format is fixed.

## 8. Rigorous archival confirmation — PASS (525 / 525 valid roots)

The point-7/14 arcs are interval-certified by the same AA-Krawczyk stack the census used
(`chain_sphere` → `aar_sphere` → `aar`). Evaluating the rigorous chain over each root's certified
box (`radius_used`) encloses x7 and x14 in verified intervals; for every one of the 525 valid roots,
**both** the numeric chain value and the geodesic constructor's value lie inside the enclosure:

    valid roots enclosed at certified radius    525 / 525   (no shrink, no AA failure)
    numeric + geodesic x7/x14 outside interval     0
    max enclosure width                         2.6e-2
    min containment margin                      3.4e-7

So points 7 and 14 are not merely numerically faithful but rigorously bracketed by the frozen
interval engine — the same standard as the certified roots themselves.

## Verdict

Points 7 and 14 are faithful to the frozen chain at machine precision on every drawable (valid)
root, and interval-certified by the rigorous AA-Krawczyk stack over every certified box (§8). The
19 non-reconstructable roots are all rejects, handled by the generator's per-root geometry gate.
The lift is sound and archival-grade; the full nine-triangle figure is now reconstructable, and the
geometry validation the atlas generator was gated on is complete.

## Addendum — STEP 1 re-validation under the corrected Rao topology (2026-07-04)

The topology correction (plane viewer v1.0.1; spherical STEP 0) changes which segment of
each transverse side is rendered — produced to corners 18, 16, 17, 19 instead of truncated
at construction crossings 4, 6, 5, 3. **The lift of points 7 and 14 is unchanged by this**:
it is built on the supporting great circles, and geodesic(P4→6) is the same great circle as
the produced side geodesic(P4→16) exactly when 6 is an interior point of that side.
This was verified per root, per side (new `spherical_lift.verify_produced_sides`):

    sides checked (drawable roots × 4 produced sides)   3796
    max |triple product apex·(mid×corner)|              2.0e-16   (same great circle, machine precision)
    interior parameter t, Gate-4 VALID roots            [0.379, 0.997] — 0 violations of 2100
    interior parameter t, Gate-4 REJECTED (drawable)    [0.031, 1.434] — 187 sides outside (0,1)

The rejected-root violations are not a defect: they are the registered ordering-containment
rejection made visible in the geometry — along the transverse, those roots cross their base
lines out of order, so a construction crossing can fall beyond the produced corner. On every
valid root the truncation points are strictly interior, as Rao's construction requires.

Full re-validation results (frozen engine, corrected-topology generator imported with its
fail-loud guard active):

    lift arc agreement vs chain, 525 valid roots        max 1.1e-15   (0 construction failures)
    non-drawable roots (faithfulness gate)              19, all Gate-4-rejected (unchanged)
    constructor Gate-4 vs census, closure_tol 1e-7      968 / 968 agree
    constructor Gate-4 vs census, closure_tol 1e-5      968 / 968 agree
    census counts                                       3044 subsets · 888 feasible · 968 roots · 525 valid / 443 rejected
    drawable crosstab                                   525 v+d · 424 r+d · 19 r+n · 0 v+n
    AA-Krawczyk rigorous enclosure (x7, x14)            525/525 inside, 0 AA failures, min margin 3.4e-7

All prior visual artifacts produced under the truncated table remain **void** per the
STEP 0 addendum in GEOMETRY_VALIDATION_REPORT.md. No bundle was regenerated in STEP 1.
