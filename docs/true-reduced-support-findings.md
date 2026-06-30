# Route B2 {1,2,3,4,6,7}: coefficient-exact reduction is INFEASIBLE by direct elimination
#   (smallest cone F3 explodes). Exact reduced MV not obtainable this way -> B1 is the decider.

**Status.** Exploratory probe (no driver/engine changes). Attempts the pre-committed Route B2
(coefficient-exact node elimination -> true reduced support over 6 base atoms), with a hard
explosion guard. Frozen engine UNCHANGED. NO infeasibility claim.

## Result: ROUTE_B2_SUPPORT_STATUS = failed
Coefficient-exact elimination of the SMALLEST constraint cone fails:
  F3 (7-node cone): eliminated x10 -> intermediate degree 22, 1169 terms (one node); then
  TIMED OUT on the next node U8 (45 s/step cap). Degree roughly doubled per node eliminated.
Deeper cones are strictly worse (F6:8, F2:10, F7:10, F4:11, F1:13 nodes), so the attempt halts
at F3 by design once the smallest cone fails. Guards: DEG_CAP=120, TERM_CAP=2e5, STEP_TIMEOUT=45s.

CONCLUSION (operational, NOT an impossibility theorem): the TRUE reduced support over the 6 base
atoms is not operationally obtainable by this direct sequential resultant-elimination route under
the stated guards -- the resultant chain explodes (each algebraic node is a degree-2 cover;
eliminating it squares degree, and 7-13 nodes compound past the guard). This is a practical/
architectural negative for THIS method, not a proof that no reduced support exists; a different
elimination (Groebner with a tuned order, numerical interpolation, structured/triangular solvers)
is not excluded. B2-exact is ruled out only for this route under these guards.

## What this does and does NOT establish
DEFINITIVE (for this route): coefficient-exact reduced support via direct sequential resultant
elimination is operationally infeasible under the stated guards. So the ladder
outcome "exact + huge -> presence-first fires" CANNOT be reached through B2 by this method; the
exact decider reverts to B1 (exact/64-bit MV backend on the full 50-var supports).

SUGGESTIVE (NOT conclusive): the rapid growth -- degree 22 in the base atoms after eliminating
just 1 of F3's 7 nodes -- indicates the reduced 6-base system is itself HIGH-DEGREE, leaning
toward "the explosion is intrinsic to the six-base geometry" rather than "pure 50-var lift slack."
But the elimination did not complete, so this is a trend, not a proof. The intrinsic-vs-slack
question is NOT settled here.

## Status board
    FULL_LIFT_MIXED_VOLUME           = BACKEND_OVERFLOW (Int32, intermediate ~7.5e14)
    ROUTE_A_DEGREE_BOX_UPPER_BOUND   = 1.12e12   (conservative + huge; valid, loose)
    ROUTE_B1_FULL_SUPPORT_EXACT_MV   = PENDING    (the remaining exact decider; supports artifact ready)
    ROUTE_B2_REDUCED_SUPPORT_MV      = NOT_OBTAINED
    ROUTE_B2_SUPPORT_STATUS          = failed (coefficient-exact by direct resultant elimination)

## Decision (per pre-commit) -- still NOT presence-first yet
The ladder said: exact -> if huge -> presence-first; conservative+huge -> strong warning, not
final; failed-exact -> needs B1. We are at: conservative bound huge (1.12e12, Route A) AND
exact-reduction failed (B2). Both keep "absence impractical" as a STRONG SIGNAL but not a
certified conclusion. The one remaining route to a CERTIFIED number is:

  ROUTE B1: exact/64-bit mixed-volume backend on lift_123467_supports.json (full 50-var supports,
            50 eqs / 50 vars / 338 monomials). phcpy (PHCpack, arbitrary precision) is the natural
            choice since HC.jl/MixedSubdivisions overflowed Int32. If B1 returns:
              modest  -> absence branch feasible (would be surprising given the signals);
              ~1e9+   -> PRE-COMMITTED CONCLUSION fires: certified absence is NOT operationally
                         reachable through the current global-homotopy / full-lift architecture
                         (B1 measures the full lifted support, not an ideal minimal algebraic
                         formulation -- so this is an architectural negative, NOT 'absence is
                         impossible'). The spherical census proceeds PRESENCE-FIRST with certified
                         lower bounds. If B1 ALSO overflows/explodes across all viable backends ->
                         same architectural conclusion and the same presence-first fallback.

## What is NOT claimed / NOT touched
No infeasibility claim. No presence-first conclusion yet (B1 pending). certify_2b, census_io, the
validated lift, and the presence-first certified census are all untouched and valid.

## Files
  true_reduced_support_123467.py    guarded coefficient-exact elimination attempt (B2)
  true_reduced_support_123467.json  per-constraint elimination outcome + trace
  true-reduced-support-findings.md  this report

SHA-256 hashes for all files in this unit are recorded in `docs/SHA256SUMS`