# F4 Trig-Pair (tan-free) Reformulation — does NOT rescue; deep-interior wall is bounded
#                                          for this enclosure paradigm

**Status.** Exploratory probe (no driver changes). Tests the trig-pair / tan-free chain
reformulation as the last untested rescue for large-box interior exclusion. Result: does
NOT tighten the enclosure (it is LOOSER); the deep-interior wall is effectively bounded for
the interval/AA enclosure paradigm. Frozen v1.2 UNCHANGED.

## Idea
The node scan localized F4's value looseness to the U-nodes (U8 2.3x, U9 2.5x, U12 3.7x)
where Q = (sin/sin)(tan(x_i)/tan(x_j)) and U = atan(sin(S)/(Q+cos(S))) -- i.e. atan->tan
round-trips. Trig-pair carries each angle as (sin,cos) (or tan = pre-atan argument) and uses
addition/double-angle identities, never forming an angle then re-applying trig. Question
(first-order only): does a better chain REPRESENTATION make AA tight enough?

## Build + verification
Full F4 cone rebuilt tan-free (acos-arg pairs for x1,x2; tan=W for the atan arcs;
(sin,cos)=(N,D)/sqrt(N^2+D^2) for the U-nodes; addition formulas for v8,v9,v12,A; the iso
wrapper cos(2x13)/cos(x13) computed algebraically as (1-W13^2)/sqrt(1+W13^2)). Reproduces
RAO EXACTLY at 3 points incl. the near-root (F4=-1.8e-5). Trig-pair AA enclosure SOUND
(containment harness: 80 boxes, 0 failures).

## Result: REFUTED -- trig-pair is LOOSER, not tighter
  (3) WIDTH on non-straddling boxes (rad 0.02, isolating wrapping from inflection splits):
      median AA_orig/sampled    = 2.6x
      median AA_trigpair/sampled = 11.3x   <- trig-pair ~4x WIDER than original
  (4) EXCLUSION-RADIUS (full grid): raw median trigpair/orig = 1.00x (mean 1.53x);
      union median 1.00x (mean 1.60x); trig-pair >= orig 12/15.

## Why it fails (mechanism)
The (sin,cos)-pair machinery adds MORE wrapping than the atan->tan round-trips it removes:
each U-node now carries a sqrt(N^2+D^2) normalization and each angle sum/diff is a pair
product (4 AAr multiplies, each spawning a fresh nonlinear symbol). The Q-ratio looseness
(tan(x_i)/tan(x_j) = t_xi/t_xj) is UNCHANGED -- it is the same ratio -- and the added sqrt
+ pair products pile on top. Net: looser.
The mean exclusion-radius lift (1.53x) is INCIDENTAL: the trig-pair computes cos(2x13)/cos(x13)
algebraically and so avoids the cos(2x13) inflection SplitNeeded that forces the original to
subdivide. That avoids some splits but does NOT tighten the enclosure (width test is
decisive). It is inconsistent (median 1.00x, regressions present).

## What this settles (the three rescues are exhausted)
  - Second-order (degree-2 Taylor): dead for deep chains (AA Hessian explosion 10^2-10^6x).
  - Denominator-clearing: dead for F4 (pathology is the deep h-chain, not the secant).
  - Trig-pair / tan-free: dead for value tightening (looser, not tighter).
The binding obstruction is the DEEP CHAIN'S accumulated AA wrapping, and it is NOT removed by
algebraic wrapper changes, denominator clearing, second-order enclosures, or trig-pair
representation. => the deep-interior large-box exclusion wall is effectively BOUNDED for the
first/second-order interval-AA enclosure paradigm.

## Honest banked result + redirect
- BANKED (solid): 2b removes the EDGE diagonal wall (was 100% of old's unresolved) and the
  root certifies. That is a real, coordinate-fixable advance.
- DEEP INTERIOR: needs a DIFFERENT GLOBAL METHOD, not interval/AA enclosure refinement.
  Candidates beyond this paradigm: (a) the homotopy/parameterized-family enumeration thread
  (algebraic, not enclosure-based); (b) an extended chain-variable contractor that treats
  x13,v12,U12,... as variables with interval constraints (preserves dependencies instead of
  substituting into one deep expression) -- heavier, untested, the one remaining
  enclosure-adjacent idea; (c) accept the pilot as interior-bounded and report 2b's edge
  removal + root certification as the spherical contribution.
- MINOR (optional, not a rescue): computing the iso wrapper cos(2x)/cos(x) algebraically
  from tan(x) avoids the cos(2x) inflection split for F3/F4/F6 -- a small reduction in forced
  splits, deployable as a hybrid WITHOUT the trig-pair value penalty. Marginal.

## Files
  probe_f4_trigpair.py     tan-free F4 cone; point/containment/width/exclusion checks
  f4-trigpair-findings.md  this report

SHA-256 hashes for all files in this unit are recorded in `docs/SHA256SUMS`