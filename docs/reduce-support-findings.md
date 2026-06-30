# Route A — conservative DEGREE-BOX bound {1,2,3,4,6,7}: full lift overflowed the MV backend;
#   degree-box/permanent upper bound ~1.1e12 (inconclusive, COARSER than true support MV).
#   Both signal LARGE. Route B (exact backend / true support propagation) decides.

**Status.** Exploratory probe (no driver/engine changes). Follows the full-lift mixed-volume run,
which OVERFLOWED. Attempts the pre-committed Route A (support-only reduction to 6 base DOF) and
reads it against the overflow. Frozen engine UNCHANGED. NO infeasibility claim.

## Measurement 0 (server): full-lift MV backend OVERFLOW
`JULIA_NUM_THREADS=8 julia lift_123467_hc.jl` on the 50-var/50-eq system:
  ERROR InexactError: trunc(Int32, 750599938220032)  -- MixedSubdivisions.jl mixed-cell
  traversal exceeded Int32 at an intermediate ~7.5e14. This is a ROUTE failure (32-bit indexing
  on the un-eliminated 50-var Cayley configuration), NOT proof of impossibility and NOT a lift
  error (the known-root gate already PASSED at 6.66e-16).
  Label: FULL_LIFT_MIXED_VOLUME = BACKEND_OVERFLOW.

## Route A: conservative DEGREE-BOX bound over 6 base DOF (no backend, no coeff expansion)
NOTE ON METHOD: this is a degree-box / permanent upper bound, NOT true support-only Newton-
polytope propagation. A degree box [0,d] per variable is the BOUNDING BOX of the true Newton
polytope; permanent(D) is the MV of those boxes -- strictly COARSER than the MV of the actual
polytopes (real supports have holes/slanted faces the box ignores). Valid upper bound, coarser
than the true reduced support MV (which is Route B2).
Propagate Newton supports/degrees through the triangular node chain: each base angle contributes
degree 1; sin/cos of a sum = sum of constituent degrees; a node (linear in its own (S,C)) is, after
clearing its denominator and the degree-2 cover norm, of degree <= deg(num)+deg(den) per base angle
(OVER-approximation). The 6 constraints' degree vectors over the 6 base angles form a 6x6 matrix D;
mixed volume of the bounding boxes = permanent(D) >= true reduced MV (Newton polytopes contained in
boxes; MV monotone). Acos nodes handled (constant term counted) so the bound stays valid.

  reduced degree matrix D (rows F1,F2,F3,F4,F6,F7; cols b,c,d,e,g,h): deepest col h up to 312
  CONSERVATIVE reduced MV upper bound = permanent(D) = 1.12e12
  total-degree bound                  = 1.05e15
  (deepest node x11a reaches conservative degree 296 in h: additive propagation through 19
   sequential cover levels compounds hard.)

## Reading (honest): inconclusive, but both signals point LARGE
- Route A bound (1.12e12) is a VALID but LOOSE upper bound. It does NOT prove the reduced route
  tractable (the true MV could be far smaller -- cancellations the support bound cannot see), and
  being an upper bound it cannot prove intractable either. Inconclusive on its own.
- Cross-read with the overflow via the node cover degree 2^19=5.24e5: if the full-lift MV is near
  the overflow scale (~7.5e14), then reduced ~ full/2^19 ~ 1.4e9. Route A's independent upper
  bound (1.1e12) sits above that, consistent.
- CONVERGENT SIGNAL (not a certified count): reduced MV plausibly ~1e9, full ~1e14+. ~1e9 paths
  is beyond feasible path-tracking; ~1e14 is hopeless. This SUGGESTS the absence branch via global
  homotopy is impractical -- but it is a signal from a loose bound + an intermediate overflow, NOT
  a certified mixed volume.

## Pre-committed next: Route B (split B1/B2) BEFORE any conclusion
Per the agreed plan (Route A -> Route B -> only then presence-first). Route B splits:

  ROUTE B1 -- exact/64-bit MV backend on the FULL 50-var supports (lift_123467_supports.json):
    phcpy (PHCpack, arbitrary precision) / newer 64-bit MixedSubdivisions / any MV tool consuming
    integer support matrices. A huge B1 PROVES the un-eliminated FULL-LIFT route impractical -- but
    the full lift pays the 2^19 cover slack, so B1 alone does NOT settle the absence question.

  ROUTE B2 -- TRUE 6-base-variable support propagation (next build, true_reduced_support_123467.py):
    propagate ACTUAL exponent supports via set-union + Minkowski sums (NOT degree vectors/boxes),
    forming the six reduced Newton polytopes over [b,c,d,e,g,h], then MV of those. B2 distinguishes
    "geometry intrinsically high-degree" from "lift formulation paying algebraic branch slack".

Decision: only if B2 (true reduced support MV) is ALSO ~1e9+ does the pre-committed conclusion fire:
    certified absence by global homotopy NOT operationally reachable in this architecture for now;
    spherical census proceeds PRESENCE-FIRST with certified lower bounds.

## Status board
    FULL_LIFT_MIXED_VOLUME          = BACKEND_OVERFLOW (Int32, intermediate ~7.5e14)
    ROUTE_A_DEGREE_BOX_UPPER_BOUND  = 1.12e12   (valid, loose, coarser than support MV)
    ROUTE_B1_EXACT_BACKEND          = PENDING    (full 50-var supports artifact ready)
    ROUTE_B2_REDUCED_6DOF_TRUE_MV   = PENDING    (true Newton-polytope propagation, next build)

## What is NOT claimed
No infeasibility claim. No presence-first conclusion yet (Route B pending). The full lift is
implementation-valid (gate passed); only the FEASIBILITY of the homotopy-absence route is in
question, and the certified decider is Route B. certify_2b and census_io are untouched and valid.

## Files
  reduce_support_123467.py        Route A support-only degree propagation + permanent bound
  reduce_support_123467.json      Route A summary (degree matrix, conservative bound)
  lift_123467_supports.json       Route B artifact: Newton supports for an exact/64-bit MV backend
  reduce-support-findings.md      this report

SHA-256 hashes for all files in this unit are recorded in `docs/SHA256SUMS`