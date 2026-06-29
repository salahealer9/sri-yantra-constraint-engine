# F4 Chain-Variable Contractor — FAILS the bar; contraction (like enclosure) does not
#                                 crack large-box exclusion. Deep-interior closeout.

**Status.** Exploratory probe (no driver changes). Tests the chain-variable contractor --
the one remaining genuinely-different (constraint-propagation, not enclosure) lever for
large-box interior exclusion. Result: FAILS the pre-committed criterion. Frozen v1.2
UNCHANGED.

## Method (genuinely different from enclosure)
Instead of evaluating one deeply-substituted expression, introduce an interval variable for
every F4 intermediate (r,z1,z2,tx1..tx6,tx10,U8,v8,U9,v9,U12,v12,tx13,A,F4) and impose the
shallow relations between them. Run HC4-style forward/backward interval constraint
propagation to a fixpoint. For EXCLUSION: impose F4=0 and propagate; an EMPTY interval on
any node proves F4 has no zero on the box (sound). Forward F4 interval verified to contain
the RAO point value.

## Pre-committed criterion
SUCCESS = contractor narrows U12/v12/x13 by >2x (backward doing real work) OR excludes at
>=2x the AA radius. FAILURE = no meaningful narrowing / same exclusion radius as AA.

## Result: FAIL
  Backward narrowing (forward width / contracted width, median):
    tx13 ~1.9x | v12 ~1.5x | U12 ~1.3x   -- ALL below the >2x bar; narrowing DILUTES with depth.
  Exclusion radius (full grid): median contractor/AA = 1.00x (mean 1.65x).
  The mean lift is INCIDENTAL (forward-pass exclusions that avoid the cos(2x13) inflection
  split, same artifact as the trig-pair probe), NOT from backward narrowing.

## Why it fails (mechanism -- constructive)
The backward pass is NON-INERT (it does narrow: tx13 1.9x), unlike a same-paradigm null
result -- but the narrowing DILUTES as it propagates deeper (tx13 1.9x -> v12 1.5x ->
U12 1.3x). Root cause: F4 ALONE is ONE equation, underdetermined for the many intermediate
variables, so backward propagation from a single constraint cannot strongly pin the deep
multi-variable nodes (e.g. A=c+d+v9-v12 couples two unknowns; one equation can't fix both).

## The determined variant is already covered
The narrowing argument says the determined test is the FULL 6-constraint system contractor
(F1,F2,F3,F4,F6,F7=0 jointly: 6 eqs, 6 vars). BUT a full-system contractor -- preconditioned
Krawczyk (interval Newton), the linearized full-system contraction -- was ALREADY tested in
the exclusion-strength probe and gave 1.00x (no improvement over AA at large boxes). So both
the single-constraint (HC4, here) and full-system (Krawczyk, earlier) contractors fail to
beat AA at large interior boxes. A full-system HC4 variant remains technically untested, but
the prior from Krawczyk is discouraging.

## CLOSEOUT: both paradigms are bounded; the interior needs a different global method
Representatives of BOTH families have now been tested and bounded for large-box interior
exclusion:
  ENCLOSURE:   first-order AA (~3x loose) ; second-order Taylor (Hessian explosion on deep
               chains) ; denominator-cleared F4 (deep h-chain, not the secant) ; trig-pair
               (looser, not tighter).
  CONTRACTION: preconditioned Krawczyk full-system (1.00x) ; HC4 chain-variable F4 (dilutes,
               <2x, 1.00x exclusion).
The binding obstruction is the deep angle chain's accumulated wrapping / under-determination,
and it resists every interval-based refinement tested. The deep-interior large-box exclusion
wall is BOUNDED for interval enclosure AND contraction methods.

## Honest banked spherical result
- 2b removes the EDGE diagonal wall (was 100% of old's unresolved) and the root certifies --
  a real, coordinate-fixable advance, the spherical contribution from the interval paradigm.
- Full S6 / 3044 certification of the deep interior needs a DIFFERENT GLOBAL METHOD, not
  interval refinement: the homotopy / parameterized-family enumeration thread (algebraic,
  not enclosure/contraction based) is the indicated route.
- Phrasing: "the deep-interior wall is bounded for the tested interval enclosure/contraction
  paradigm," NOT "the spherical method is impossible."

## Files
  probe_f4_factor_contract.py   HC4 chain-variable contractor; narrowing + exclusion benchmark
  f4-contractor-findings.md     this report

SHA-256 hashes for all files in this unit are recorded in `docs/SHA256SUMS`