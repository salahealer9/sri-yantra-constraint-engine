# F3 Rigorous Second-Order Enclosure — Build + Result: 1.33x exclusion radius, sound

**Status.** Exploratory probe (no driver changes). Builds the rigorous degree-2 Taylor
enclosure of F3 justified by the feasibility GO, and benchmarks it. Result: SOUND, with a modest median
1.33x exclusion-radius gain (BELOW the >=2x target). Frozen v1.2 UNCHANGED.

CORRECTION: an earlier draft reported "median 2.00x" -- that came from a non-representative
reduced grid (9 points, radii from 0.04). On the file's own FULL grid (15 points, radii to
0.002) the honest median is 1.33x (mean 1.47x). The 2x figure is withdrawn.

## Build
1. SECOND-ORDER DUAL (dual2_sphere.D2): propagates (value, gradient[6], Hessian[6x6]) as
   AAr enclosures through the chain ops (+,-,*,/,sin,cos,tan,atan,acos), correlated
   second-order structure. VERIFIED at a point vs finite-difference of the true constraint:
     max|grad_dual - grad_fd| = 3.4e-9 ; max|Hess_dual - Hess_fd| = 3.0e-6  (both PASS).
2. RIGOROUS ENCLOSURE (probe_f3_rigorous.f3_taylor2_enclosure), over box X = x0+[-r,r]:
     F3(x) in F3(x0) + gradF3(x0).Δ + 1/2 Δ^T H0 Δ + R3
   where F3(x0), gradF3(x0), POINT Hessian H0 come from a zero-radius dual (exact,
   rounding-bounded); the quadratic uses the POINT Hessian with one-sided Δ_i^2 in [0,r_i^2];
   and R3 = 1/2 Δ^T (H(ξ)-H0) Δ is bounded by the box-dual Hessian SPREAD (H(X)-H0), an
   O(r^3) remainder. Rigorous by the mean-value/Taylor theorem (ξ in the convex box, so
   H(ξ) in H(X)). (An earlier full box-Hessian quadratic was sound but only mixed vs AA --
   the box-Hessian is ~3x loose; using the point Hessian for the dominant quadratic and
   isolating the spread to O(r^3) is what recovers the tightness.)

## Result (exclusion-radius benchmark, F3 only; FULL grid, honest)
  median radius ratio T2/AA = 1.33x ; mean = 1.47x   (TARGET >=2x: NOT met)
  T2 fires at >= AA radius on 12/15 sampled interior points, including 3x wins and one box
  where AA NEVER excludes but T2 does. Regressions: 2/15 (spread remainder bloats on
  high-3rd-order boxes) -> T2 is NOT a strict superset of AA.
  Note: F3 is the TIGHTEST constraint under AA (~1.5x), so it had the LEAST to gain from
  second-order. HYPOTHESIS: the ~3x-loose constraints (F1/F2/F4/F7) are stronger candidates for
  second-order gain (more looseness headroom) -- to be tested, not assumed.

## Soundness
Safety harness on the reformulated enclosure: 120 random interior boxes (radii 0.005-0.03),
14,400 random point evaluations, 0 soundness failures (every point eval inside the
enclosure). Corroborates the rigorous derivation + verified dual. (Random-sampling is
strong evidence, not a formal proof; soundness rests on the derivation and the dual
verification.)

## Deployment implication (important)
Because T2 is not a strict superset of AA (2/15 regressions), the correct use is the UNION:
exclude if EITHER natural AA OR the T2(F3) enclosure misses 0. That is never worse than AA
and gains the boxes where T2 beats AA, including some 2x-3x wins. Cost: ~404 ms/box for two D2 evals -- so T2 must be invoked
SELECTIVELY (e.g. only on boxes AA fails to exclude, possibly only in a depth band), not on
every box. The cost/benefit (one 404 ms test vs the many subdivision levels a 2x-larger
exclusion saves) needs a driver-level measurement before integration.

## Read and next steps
- READ: F3 proves the D2 machinery is SOUND and sometimes useful, but F3 alone (1.33x
  median) does NOT yet justify driver integration. The decisive next probe is F4.
- NEXT (F4 first): extend the second-order enclosure to F4. F4 shares F3's iso form
  cos(V)-cos(2x)/cos(x), so it is structurally close (low implementation risk) but looser
  than F3 under AA -- the cleanest test of the HYPOTHESIS "does second-order pay off more on
  a looser, structurally similar constraint?". Report BOTH the raw T2/AA radius AND the
  deployable UNION (exclude if AA OR T2 misses 0) radius / AA, on the FULL grid.
- Then F1/F2/F7 if F4 confirms the hypothesis. Driver integration (selective union, measure
  net box-count vs the 404 ms cost) only once a constraint clears a worthwhile margin.
- Coordinate-INDEPENDENT: benefits the frozen old-coord engine and 2b alike.

## Files
  dual2_sphere.py                       verified second-order dual (value, grad, Hessian)
  probe_f3_rigorous.py                  rigorous F3 degree-2 enclosure + benchmark + harness
  f3-secondorder-rigorous-findings.md   this report

SHA-256 hashes for all files in this unit are recorded in `docs/SHA256SUMS`