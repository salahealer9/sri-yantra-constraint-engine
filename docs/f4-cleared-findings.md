# F4 Denominator-Cleared Reformulation — does NOT rescue F4; pathology is the deep chain

**Status.** Exploratory probe (no driver changes). Tests the denominator-cleared,
zero-equivalent reformulation of F4 as a rescue for the failed second-order route. Result:
does NOT rescue F4 -- value enclosure unchanged, Hessian explosion not tamed, second-order
does not reopen. Frozen v1.2 UNCHANGED.

## Idea (sound and rigorous)
Original:  F4 = cos(A) - cos(2 x13)/cos(x13),  A = c+d+v9-v12
Cleared:   G4 = cos(A) cos(x13) - cos(2 x13)              [= F4 * cos(x13), verified]
Where cos(x13) is SIGN-CERTIFIED nonzero on the box, F4=0 <=> G4=0, so for exclusion:
  if cos(x13) sign-certified nonzero on X and 0 not in G4(X), then F4 has no zero on X.
Rigorous. Motivation: remove the explicit 1/cos(x13) (secant) amplification that the F4
second-order probe blamed for the Hessian explosion.

## Results (full grid; reproduced by `python3 probe_f4_cleared.py`)
1. VALUE exclusion radius: median G4/F4 = 1.00x (mean 1.03x). G4 >= F4 on 15/15 (never
   worse; sign-certification held, 0 cos(x13) skips), but only ONE box improved. Clearing
   does NOT tighten the VALUE enclosure -- because cos(x13) ~ 0.5-0.85, so 1/cos(x13) is
   only a ~1.2-2x factor on the VALUE; it was never the value-looseness driver.
2. HESSIAN explosion: clearing reduces the worst box-Hessian spread by only ~1-2x (median
   1.5x, occasionally 18x). G4's Hessian is STILL 10^3-10^7 -> explosion NOT tamed.
3. SECOND-ORDER on G4: median T2(G4)/AA(F4) = 1.00x -> second-order does NOT reopen.

## Conclusion: the pathology is the DEEP h-CHAIN, not the secant
The F4 Hessian explosion is dominated by the deep chain -- d2/dh2 threaded through r=pi/2-h
into x1..x13 (worst entry H[5][5]) -- NOT the 1/cos(x13) wrapper. Removing the secant takes
off one amplifier (~1.5x) but leaves the deep-chain accumulation, which still explodes. So
denominator-clearing, though rigorous and worth testing, does not rescue F4.

## What this settles
- Second-order on the deep angle chain: ruled out (F4 + cleared-F4 both fail).
- Denominator-clearing: ruled out as a rescue for the deep constraints (F4).
- The binding obstruction is the DEEP CHAIN STRUCTURE itself (depth-driven wrapping in
  values and, far worse, in derivatives), independent of algebraic wrapper form.

## Remaining candidate (deeper, not yet tested): trig-pair formulation
Carry (sin theta, cos theta) for intermediate angles through the chain instead of repeatedly
forming an angle and then taking trig of it (the atan -> tan round-trips that accumulate
wrapping). This attacks the chain STRUCTURE -- the actual source -- rather than an algebraic
wrapper. It is a larger rewrite; it is the honest next test before declaring the deep
interior wall bounded. If it does not materially tighten the value enclosure on the deep
constraints, the interior wall is effectively bounded for this enclosure paradigm, and the
banked win is 2b's edge removal + root certification.

## Files
  probe_f4_cleared.py     cleared G4, sign-certification, value + Hessian + second-order checks
  f4-cleared-findings.md  this report
  (reuses verified dual2_sphere.py, probe_f4_rigorous.py)

SHA-256 hashes for all files in this unit are recorded in `docs/SHA256SUMS`