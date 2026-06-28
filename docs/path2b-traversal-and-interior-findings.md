# Path 2b — Traversal Study + Corrected Interior Picture

**Status.** Exploratory. Builds a traversal abstraction (LIFO + depth-banded best-first,
soundness invariant: reorder only, never drop a box) to fix the LIFO instrument failure,
then diagnoses why the interior resists resolution. CORRECTS the bounded-run finding's
"interior smearing penalty" and clarifies what is coordinate-fixable vs fundamental.
Frozen v1.2 UNCHANGED.

## Correction to the bounded-run finding (important)
The bounded-run finding reported an interior c=u-h "smearing penalty" (cap14 region: 2b
resolved 0.0% vs old 2.6%) and read it as 2b excluding WORSE. A direct test overturns the
capability reading:
  For interior points OLD excludes, the LARGEST radius at which 2b ALSO excludes was
  measured. Median radius ratio old/2b = 1.0x (over sampled interior points): 2b excludes
  the same interior points at the SAME box size as old. Interior exclusion CAPABILITY is
  NOT degraded. The cap14 0% was a TRAVERSAL/HULL-SHAPE artifact (at depth 14 from the
  wider B_UV hull, 2b's u,v dims had not yet been split down to exclusion scale), not a
  smearing deficit. The genuine interior penalty is modest: ~2-3 extra levels because u,v
  start wider (2.67, 2.87) than old c,d (1.10, 1.30), plus nonphysical-hull pruning.

## Traversal study (instrument)
LIFO and large-band/largest-first frontiers were compared on the (u,v) pilot:
  LIFO            : dives to depth 200 in ONE narrow region (qleft~127); excl=cert=0
                    (it never backtracks to the excludable boxes elsewhere).
  largest-first   : breadth by size; STUCK at depth ~19 within budget; excl=cert=0
                    (never reaches the exclusion scale); but DOES prune nonphysical hull
                    (nph>0 where LIFO had nph=0).
Both FAIL the hard gate (excl>0 or cert>0) -- for a STRUCTURAL reason, not a tuning one:

## The structural finding: the interior is exponentially hard for BOTH coord systems
Interior exclusion fires only at small boxes (radius ~1e-2, ~depth 30-40 from B_UV). Below
that depth NO exclusion fires (enclosures contain 0), so the pre-exclusion tree grows
~2^depth. Pure breadth cannot afford that depth; pure depth reaches it only in one region.
This is a property of the SPHERICAL CONSTRAINT SYSTEM (deep subdivision needed before
exclusion), and it affects OLD coords too (old was BUDGET-EXHAUSTED at 3M = 2^21.5, also
short of the interior exclusion depth). It is NOT specific to the (u,v) transform.

## What this means for Path 2b (calibrated)
- SOLID WIN: 2b removes the EDGE diagonal wall -- the exponential staircase that was 100%
  of old's unresolved. That wall is COORDINATE-FIXABLE and 2b fixes it. Root certifies.
- CORRECTED: 2b's interior exclusion capability = old's (radius ratio 1.0x). No real
  smearing deficit; ~2-3 extra levels from the wider hull.
- SHARED FUNDAMENTAL: the interior exclusion depth (~30-40) is exponentially hard for BOTH
  coord systems -- a property of the spherical constraints, not the transform. Neither old
  nor 2b closes the pilot by pure axis-aligned subdivision in feasible budget.
- NET PREDICTION (not asserted): a full-budget 2b run gets FURTHER than old (edge wall
  removed) but likely ALSO BUDGET-EXHAUSTED (interior fundamental). The wall MOVES from a
  coordinate-fixable edge to a fundamental interior depth.

## Two honest next directions (decide before more code)
A. WALL-MOVE QUANTIFICATION (server, modest): full-budget (u,v) run vs old at equal budget;
   measure how much FURTHER 2b gets (smaller unfinished?) -- confirms 2b's edge win at
   scale even if it does not CLOSE. Use a hybrid traversal (depth-first with periodic
   breadth restarts) so multiple regions reach depth. Verdict: CLOSES / further-but-
   exhausted (report margin vs old's 1.45M) / TECH.
B. ATTACK INTERIOR HARDNESS (research, larger): the binding cost is now the interior
   exclusion DEPTH (exclusion fires too deep). Candidates: tighter large-box exclusion
   (higher-order AA / Taylor models to exclude at bigger boxes), the monotone substrate
   (may tighten some interior enclosures), or a constraint reformulation. This is the
   real lever for CLOSING, and it is coordinate-independent (helps old and 2b alike).

## Recommendation
Path 2b is a confirmed, sound improvement that removes the edge wall and certifies the
root -- commit it as such. But CLOSING the pilot is now gated by the interior exclusion
DEPTH, a fundamental property of the spherical constraints that the transform does not
address. So: (1) optionally run A to quantify 2b's wall-move at scale; (2) the path to
actually CLOSING is B -- tighter large-box exclusion -- which is a new research thread,
coordinate-independent. Coordinate work and traversal tuning alone (LIFO, breadth/
largest-first, depth-banding tested here) are unlikely to close the pilot without
stronger large-box exclusion; not every hybrid/stratified traversal has been exhausted,
but traversal order is no longer the main lever. Do not expect a full-budget 2b run
alone to close the pilot.

## Files
  probe_path2b_corr.py                         + traversal abstraction (LIFO / depth-banded)
  path2b-traversal-and-interior-findings.md    this report (probes inline, reproducible)

SHA-256 hashes for all files in this unit are recorded in `docs/SHA256SUMS`