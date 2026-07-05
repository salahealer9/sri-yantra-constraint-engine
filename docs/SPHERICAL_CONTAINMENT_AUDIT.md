# Spherical containment audit — cap boundary vs figure geometry

**Scope: geometry diagnostic only. No visual-form labels were created or changed.**
Bundle audited: corrected-topology STEP 2 build (968 figures, 949 drawable), guard active.

## 1. Topology confirmation

The generator's fail-loud guard passes and prints the nine produced-corner triangles on
import (P1→18, P4→16, P7→17, P9→19; truncated points 4, 6, 5, 3 barred from corner duty).
The emitted bundle's corner set is exactly {2, 18, 13, 14, 16, 1, 19, 10, 17}, and the
viewer draws bundle polylines verbatim (no topology of its own). Confirmed.

## 2. What the cap boundary IS (and is not)

The gold circle at angular radius r about the cap centre is **Rao's base/circumscribing
circle** (Fig. 2.1: the horizontal base circle through P0–1–2–P10, radius Rc = R·sin r).
It is a **construction datum**: points P0, P10, 1, 2 lie ON it by construction in every
figure, so every drawable figure "touches" it by definition.

It is **not a strict containment boundary** for the whole figure. Produced corners are
pinned to the circle only by constraints: F8 (corner 16 on circle), F9 (corner 17), and
the equidistance relations F16–F19 that tie 18, 19 to them. A subset that does not select
these leaves r16…r19 free — above or below r. The registered **Gate-4 test constrains
base points** (ordering and containment on the axis of symmetry), never corners; and the
diagnostics a = r−(b+c), f = r−(d+e) are **basic-variable spacings**, not corner bounds.
Therefore `gate4_valid = True, a > 0, f > 0` is fully compatible with a corner lying
genuinely outside the circle.

**Projection faithfulness.** The cap-normal view is an orthographic projection along the
cap axis; angular distance d from the centre maps to screen radius sin d, which is
strictly monotone for d < π/2. Since every cap has r = π/2 − h < π/2, *apparent crossings
of the circle are real geometry, not projection artifacts.* (The converse artifact exists:
points beyond the equator fold back inward — 354 such points occur, all on wrap-heavy
rejected roots — so the cap-normal view can *hide* extreme violations, never invent them.)

## 3. Method

For each of the 949 drawable figures, from the emitted bundle geometry:
`min_vertex_cap_margin` = min over all labelled points of r − ang(point);
`min_arc_cap_margin`   = the same over the triangle arcs, resampled at 0.002 rad
(finer than the rendered 0.04 polyline step);
`cap_violation` = min margin < −1e-6; `cap_touching` = |min margin| ≤ 1e-6 otherwise.

Internal consistency checks, both passed: (i) **no figure has an arc violation with
contained vertices** (0/949) — exactly what spherical-cap convexity (r < π/2) requires,
so the emitted arcs are geometrically consistent with their endpoints; (ii) **no
F8-selected root has a corner-16 violation** — where the pinning constraint is selected,
the corner sits on the circle to certificate scale.

## 4–5. Results

Every figure is at least cap-touching (P0, P10, 1, 2 are on the circle by construction).
Beyond that:

| population | cap_violation | touching only |
|---|---|---|
| Gate-4 VALID (525) | **203** | 322 |
| Gate-4 rejected (424) | 414 | 10 |

Violating vertex, by population:
- VALID roots: corner 16 ×117, corner 19 ×61, corner 17 ×18, corner 18 ×7 — **only
  produced corners, never base points** (0 P-label violations among valid roots, exactly
  as Gate-4 guarantees).
- REJECTED roots: corner 16 ×280 plus **base points P9 ×74, P1 ×31** and corners — the
  ordering/containment failures Gate-4 exists to flag, visible in the geometry.

Deepest violations are rejected wrap cases (to −1.38 rad). Valid-root violations are
moderate corner excursions (the disputed set below is typical).

### The six disputed rows

| stable_id | gate4 | r | min vertex margin | at | classification |
|---|---|---|---|---|---|
| S_1-2-3-5-6-9__root_0__f66e3ee8 | VALID | 1.180 | −0.0417 | 16 | **actual vertex violation** |
| S_1-2-3-5-6-13__root_1__5946592d | VALID | 1.433 | −0.0520 | 19 | **actual vertex violation** |
| S_1-2-4-7-8-12__root_0__a461a8e4 | VALID | 0.582 | −0.0831 | 17 | **actual vertex violation** |
| S_1-2-4-5-11-14__root_0__35ec1b6b | VALID | 0.640 | −0.0496 | 16 | **actual vertex violation** |
| S_1-2-6-9-10-16__root_0__b4d276b5 | VALID | 0.848 | −0.0000 | P0 | cap-touching (by construction) |
| S_1-2-3-8-9-10__root_0__90a56f22 | VALID | 0.870 | −0.0000 | 1 | cap-touching (F8 selected: 16 pinned) |

In all four violating cases the fine-arc minimum equals the vertex minimum (the excursion
is the corner itself; arcs follow it). Their a, f values are healthy (+0.02…+0.47),
confirming that a, f do not bound corners.

## 6. Data

`review_packet_v2/diagnostics.csv` now carries `min_vertex_cap_margin,
min_arc_cap_margin, cap_violation, cap_touching, containment_note` (inserted between the
measurement and thumbnail columns; all review/label columns untouched and still blank).

## 7. Interpretation guardrails

- A corner beyond the circle on a valid root is **not an error and not a Gate-4
  contradiction**: it is the figure's honest shape when the pinning constraints are
  unselected. Wording discipline: "extends beyond the bounding circle", never "violates
  certification".
- These columns are geometry diagnostics available to the visual-form discussion (they
  plausibly inform the near-boundary class), but **no visual-form labels were derived,
  changed, or suggested by this audit**.
