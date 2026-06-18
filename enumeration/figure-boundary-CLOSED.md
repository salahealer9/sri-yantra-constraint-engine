# Coordinate realization of Rao's plane Śrī Yantra — figure boundary CLOSED

**Provenance note (revision). Supersedes the earlier "figure-boundary inherited" note.**
Author: Salah-Eddin Gherbi (ORCID 0009-0005-4017-1095)
Scope: Rao (1998) **plane** form only; all checks within `B_plane`.
Engine (pinned): `sriyantra_plane` at commit `75aed90`. Module: `figure_coords_inner.py`.

## Summary

The boundary the earlier note described is now closed. The two auxiliary points the
engine carried only as scalars (`U20`, `U21`) are coordinatized, and the one apparent
"metric-point gap" (point 15) turned out not to exist. The
`(b, c, d, e, g) -> full-geometry` map closes end to end across the six Rao Table-3
roots. This revision records the closure and corrects the earlier note's accounting.

## What closed it

### Points 20 and 21 are coordinatized

Both are two-line intersections of already-validated transversals — Rao's own
definitions (constraints 13-14, p.216):

- **Point 20 = (P2->13) n (P8->10)**, height `yP8 - U20`
- **Point 21 = (P1->4) n (P9->3)**, height `(d+e) - U21`
  (P1->18 is the same line as P1->4 since point 18 lies on it; P9->19 == P9->3.)

Confirmed two independent ways: against Rao's text, and against the chain scalars to
machine precision across all six roots. These are inner-triangle apex feet, **outside**
the Section 7 metric set; their base lines meet the axis at `P20 = (0, y20)`,
`P21 = (0, y21)`.

| root (subset) | resid 20 (yP8 - U20) | resid 21 ((d+e) - U21) |
|---|---|---|
| {1,2,3,4,8}   | 9.45e-17 | 2.08e-17 |
| {1,2,3,10,15} | 1.87e-16 | 2.08e-17 |
| {1,2,4,5,10}  | 3.47e-17 | 1.73e-16 |
| {1,2,5,6,19}  | 1.04e-17 | 4.51e-17 |
| {1,2,6,14,19} | 3.30e-17 | 1.87e-16 |
| {1,2,8,9,20}  | 1.39e-16 | 1.20e-16 |

Max residual 1.87e-16 (<= 1e-15 bar). Reproduce: `python3 figure_coords_inner.py`.

### There is no point 15 — confirmed three ways

The earlier note's "point 15, the only remaining metric gap" was a phantom:

1. The engine chain computes no `x15`.
2. `figure_coords.figure_coordinates` returns no `'15'` label (it appears in the code
   only inside comments that *assumed* it missing — the original error propagating).
3. **Rao's source text:** p.211 defines point 8, then **point 16** directly
   (eq 2.22, "intersection of the base line through P9 with the transverse line P4-6
   extended") with nothing numbered 15 between them; p.213 runs the construction tail
   — 12, 14, 13, 19, 11a — with no 15. The index 15 occurs only as the constraint
   label F15, never as a vertex.

### The ninth triangle

Rao p.213: "The transverse arc P3-14 is drawn." The fifth Sakti side is **P3->14**,
with point 14 (validated last session, on the P8->10 side at the P5 baseline d - U7)
as its vertex. With 14 down, the ninth triangle is reconstructable — resolving the
earlier "no validatable P3 triangle" finding, which was an artifact of having dropped
point 14.

## Corrected accounting

- **Metric set = 29 points**, not 30: P0-P10 (11) plus intersection points 1-14 and
  16-19 (18). Rao defines no point 15; point 11a coincides with point 11 wherever F1
  holds (every figure in the census) and is not a separate vertex.
- **Deposited constructor covered 27** of these 29 (base points other than P5;
  intersections 1-13, 16-19). The two it lacked, **P5 (= d - U7)** and **point 14**,
  were validated to machine precision last session, so the constructor now covers all
  29 metric points. Coverage is complete.
- **128 is unaffected.** It was computed over the validated 27-point subset and is an
  exact, rigorous lower bound on the count over the full set; 29-vs-30 does not enter
  the argument. 134/681 are likewise untouched. This corrects the earlier note's
  "29 of 30 / point 15 outstanding" — there is no point 15 to be outstanding.

## Status

- The earlier note's **open problem** ("lift the U20/U21 scalar machinery to explicit
  coordinates") is **solved**.
- The `(b, c, d, e, g) -> full-geometry` map closes end to end across the six roots —
  the citable artifact the results note anticipated: *a validated coordinate
  realization of Rao's plane Sri Yantra*.
- **Remaining before any figure ships:** render the full nine-triangle figure (the
  seven original sides, plus P2->13 and P3->14, with 20/21 for the inner detail) and
  validate every element end to end in the frozen harness (engine `75aed90`) at the
  1e-15 bar. The arXiv v1 remains figure-free by design; the validated figure is a
  v2 / journal-revision addition.
