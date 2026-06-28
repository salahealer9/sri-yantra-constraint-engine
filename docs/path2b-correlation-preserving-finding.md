# Path 2b — Correlation-Preserving Transformed Wrapper: REOPENS Path 2 (strong positive)

**Status.** Exploratory micro-probe. SUPERSEDES the pessimistic verdict of probe 2a
(naive-interval) and the premature phase closeout drafted from it. Frozen v1.2 UNCHANGED.
The 2a finding "intrinsic smearing caps the benefit" was an ARTIFACT of a correlation-
LOSING implementation; preserving the correlation reverses it.

## The distinction that matters
- Probe 2a (DEAD): enumerate (u,v); form c=u-h, d=v-h as INTERVAL subtractions; reuse the
  old chain. The interval collapse discards the u,h correlation -> the reused Krawczyk
  Jacobian treats c,d,h as independent -> root NEVER certifies (indeterminate to r=1e-5).
- Probe 2b (ALIVE): enumerate (u,v); build c=u-h, d=v-h as DualRS / AAr EXPRESSIONS (shared
  noise symbols + derivative slots). The chain rule then yields the TRUE native (u,v,h)
  Jacobian automatically. This is a cheap WRAPPER, not a substrate rewrite.

## Decisive result 1 — the root CERTIFIES in correlation-preserving coords
Transformed Krawczyk at the known root (c=u-h, d=v-h as DualRS expressions):
  r=3e-3: split    r=1e-3: split    r=3e-4: UNIQUE    r=1e-4: UNIQUE   cond(J)=1.374e+02
Identical certification pattern to old coords, with the BETTER-conditioned native Jacobian
(137 vs old 258, exactly the finite-difference prediction). Probe 2a gave indeterminate at
every r. => correlation preservation recovers certification. Path 2 is ALIVE.

## Decisive result 2 — the straightening pays off, and the payoff GROWS with depth
Path-independent resolution of a FIXED edge-straddling region (the wall), resolved% =
fraction of leaves domain/excluded/certified at each depth cap:
  cap   old resolved%   2b resolved%   2b total boxes vs old
  14       14.8%           4.4%          13,395 vs 20,127
  16        7.2%           9.2%          51,795 vs 69,535
  17        3.8%          29.1%          98,849 vs 134,047   (2b resolves 14,377 vs 2,547)
Old's resolved% DECAYS toward 0 (it keeps staircasing the diagonal); 2b's RISES sharply
(axis-aligned u/v splits cleanly resolve the edge), using FEWER total boxes. The advantage
compounds with depth — the signature of removing an exponential staircase. The 2a "capped
benefit" was the correlation-loss artifact; with 2b it is uncapped in this region.

## Why the short LIFO dive did NOT show this (instrument caveat)
A 120k-box LIFO dive over B_UV gave 2a==2b (UNFIN 50,023) because excl=cert=0 there: the
dive is consumed on the domain edge and never reaches the exclusion/certification region
(same instrument failure as Lever 2). The path-independent fixed-region resolution is the
correct instrument and shows the large 2b advantage.

## Architecture finding: correctness needs only the WRAPPER, not a rewrite
Building c=u-h, d=v-h as affine/Dual expressions and feeding the EXISTING frozen chain
yields both the native Jacobian (certification) and correlation-aware value enclosures.
No chain/substrate rewrite is required for correctness. This is far cheaper than the
"substrate-scale rebuild" the scoping memo assumed Path 2 would need.

## Verdict: Path 2 REOPENED, strong positive — proceed to a broader confirmation run
The two things that sank 2a are both resolved by 2b: the root certifies, and the edge
region resolves dramatically better at depth. The remaining work is confirmation at scale,
NOT a question of viability:
  NEXT (scoped, not yet done):
  1. Confirm the wrapper finds the ACTUAL known solution(s) in a bounded census-style run
     in (u,v) (certifies the real root box, excludes the rest) — correctness at scale.
  2. Measure TOTAL cost (boxes to completion) of the correlation-preserving (u,v) run vs
     the old-coord v2 budget on the pilot subset {1,2,3,4,6,7} — does the depth advantage
     translate to a finished (not BUDGET-EXHAUSTED) or much-cheaper run.
  3. Only then consider the full size-six universe (3,044) / the C(18,3) program.
Do NOT jump to 3,044 yet. The next experiment is the bounded pilot-subset run in
correlation-preserving (u,v) coords, with the native u/v domain edge and the wrapper.

## Correction note
The earlier "spherical pilot phase closeout" (Option A adopt / B do-not-build) was drafted
from probe 2a and is SUPERSEDED by this result. If it was committed, it should be amended:
Path 2 is reopened via the correlation-preserving wrapper. If not committed, it should be
revised before any closeout.

## Files
  probe_path2b_corr.py                       transformed Krawczyk + corr-preserving classify/dive
  path2b-correlation-preserving-finding.md   this report (probes inline, reproducible)

SHA-256 hashes for all files in this unit are recorded in `docs/SHA256SUMS`