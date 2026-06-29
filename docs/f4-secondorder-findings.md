# F4 Second-Order Enclosure — Hypothesis REFUTED; AA derivative-enclosure explosion

**Status.** Exploratory probe (no driver changes). Tests the hypothesis that a looser,
deeper-chain constraint (F4) gains MORE from the rigorous degree-2 Taylor enclosure than F3
did. Result: REFUTED, with a clear and general mechanism. Frozen v1.2 UNCHANGED.

## Setup
F4 = cos(c+d+v9-v12) - cos(2 x13)/cos(x13): same iso form as F3 but a DEEPER chain (needs
v9 via x5,U9; v12 via v8,U8,x6,x10,U12; x13 via v12,x3). Built in the verified second-order
dual; chain matches RAO exactly; dual grad/Hess verified vs finite difference
(max|grad-fd|=3.5e-9, max|Hess-fd|=5.4e-6). Same rigorous enclosure + safety harness as F3,
benchmarked on the FULL grid, reporting BOTH raw T2/AA and the deployable UNION (AA OR T2).

## Result: REFUTED
  RAW   median T2/AA = 1.00x (mean 1.00x)   -- NO gain (vs F3's 1.33x)
  UNION median U/AA  = 1.00x (mean 1.12x)   -- barely above AA
  Soundness harness: 120 boxes / 14,400 evals, 0 failures (T2 is sound, just loose).
  At radius 0.02, T2 is 2x-8x WIDER than natural AA (T2/sampled up to 27x vs AA's ~2.6x);
  it only ties AA at small radii where the O(r^3) remainder finally shrinks.

## Mechanism (decisive): NOT fundamental -- AA Hessian-enclosure EXPLOSION
The degree-2 math is fine; the box-Hessian ENCLOSURE is the problem. Direct check on F4
boxes (radius 0.02), worst Hessian entry vs densely-sampled true Hessian spread:
  AA box-Hessian spread / sampled-true spread = 500x .. 4,400,000x
  (true Hessian spread ~10-37; AA encloses it as ~4e3 .. 1.7e8). Worst entry always
  H[5][5] = d2F4/dh2, since h enters r=pi/2-h and feeds the ENTIRE chain.
=> The TRUE Hessian is well-behaved over the box; AA's first-order enclosure of it explodes
   on the deep chain. The rigorous R3 remainder (needs the Hessian spread) inherits the
   explosion -> T2 becomes far wider than AA.

## General insight (the real obstruction)
AA enclosure looseness COMPOUNDS with derivative order on deep chains:
  values  ~3x loose ; Hessians ~10^2 .. 10^6x loose.
Second-order needs TIGHT Hessian enclosures, which first-order AA cannot provide over deep
chains. Higher-order Taylor (degree 3+) would need even-higher-derivative enclosures, which
explode FASTER -- a dead end, not a fix.

## Calibrated scope of second-order
- WORKS only where the chain is shallow enough that the Hessian enclosure stays tight: F3
  (shallow) -> 1.33x. It is a LIMITED tool: usable on shallow constraints, in the UNION.
- FAILS on deep/loose constraints (F4 -> worse than AA). Because the binding interior
  looseness lives in the deep/loose constraints (F1,F2,F4,F7 are ~3x loose under AA, and
  they are the deep ones), second-order does NOT crack the large-box exclusion bottleneck.

## Read and redirect
- READ: second-order is a modest, narrow tool (shallow constraints only), not the general
  lever for large-box interior exclusion. The hypothesis that looser constraints gain more
  is FALSE -- looser here means deeper, and deeper means the AA Hessian enclosure explodes.
- Driver integration of T2 is NOT justified: it helps only F3 (1.33x) and the per-box cost
  is high (404 ms F3, 841 ms F4); on the loose constraints it is worse than AA.
- REDIRECT candidates (make exclusion fire at larger boxes WITHOUT tight high derivatives):
  1. CHAIN-DEPTH REDUCTION / reformulation: shorten the constraint chains so even first-order
     AA value enclosures tighten (attacks the root cause -- depth-driven wrapping).
  2. MONOTONICITY / denominator-safe analytic bounds on the worst sub-expressions (the
     tan/division near-poles that drive both value looseness and Hessian explosion;
     H[5][5] via r=pi/2-h is the flag).
  3. Bank the confirmed 2b EDGE-removal win; treat the deep-interior as a separate, harder
     problem rather than forcing second-order onto it.
- Coordinate-INDEPENDENT throughout.

## Files
  probe_f4_rigorous.py        F4 chain + rigorous degree-2 enclosure + harness + benchmark
  f4-secondorder-findings.md  this report
  (reuses verified dual2_sphere.py)

SHA-256 hashes for all files in this unit are recorded in `docs/SHA256SUMS`