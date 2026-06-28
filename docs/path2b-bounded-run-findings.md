# Path 2b Bounded Pilot Run — Findings: edge wall REMOVED, interior smearing penalty
# revealed; net closure PROMISING but not yet demonstrated

**Status.** Exploratory. Extends and PARTIALLY TEMPERS the 2b finding. The correlation-
preserving wrapper is confirmed VIABLE (root certifies under the full soundness contract),
and it removes the edge diagonal wall, but a bounded full-pilot run reveals a c=u-h
SMEARING penalty in the valid interior. Frozen v1.2 UNCHANGED. This corrects the 2b
finding's "strong positive / proceed" framing, which was written before the interior was
tested.

## Confirmed (solid)
1. ROOT CERTIFIES under the FULL soundness contract in (u,v): native edge + hull prune +
   full-chain-real domain guard (on correlation-preserving AAr expressions) + cone
   exclusion + transformed Krawczyk -> root box 'certified' at r=3e-4, 1e-4. The (u,v)
   certificate is geometric, not merely algebraic. The 2a-fatal flaw is fixed.
2. EDGE WALL REMOVED: in a 2M-box (u,v) run, of the unresolved boxes sampled, 0.0% straddle
   u/v=pi/2 (old coords: 100% straddled the acos diagonal), 0.0% are hull-nonphysical, and
   100% are PHYSICAL INTERIOR. The exponential diagonal STAIRCASE is gone (axis-aligned u/v
   splits replace it). Path-independent edge region: 2b resolves 29.1% vs old 3.8% at cap17.

## Revealed (the trade)
3. INTERIOR SMEARING PENALTY: path-independent resolution of a PHYSICAL INTERIOR region
   (u,v well below pi/2, no edge):
     cap14 old  : resolved 2.6% (418 constraint exclusions)
     cap14 2b   : resolved 0.0% (0 constraint exclusions)
   In the interior there is NO diagonal to straighten, so 2b gets only the COST of c=u-h
   (constraint values widen by ~u_width+h_width -> looser enclosures -> fewer exclusions),
   with no offsetting gain. After the edge is removed, the interior is the NEW wall (100%
   of 2b's unresolved boxes).

## Why this is a TRADE, and why it is still promising
- The edge gain is EXPONENTIAL: axis-aligned splits resolve the edge in O(depth) where the
  old diagonal staircase needed ~2^depth. This was the entire old wall (v1.2: 100% of
  unresolved straddled the edge).
- The interior penalty is CONSTANT-FACTOR and VANISHING: the smearing u_width+h_width
  shrinks as boxes shrink, so it costs a bounded number of EXTRA subdivision levels and
  disappears at depth (deep boxes are tiny -> both old and 2b exclude).
- Asymptotically the exponential edge gain should dominate the bounded interior penalty,
  so 2b should net-win at sufficient depth. But the BOUNDED sandbox runs are interior-bound
  BUDGET-EXHAUSTED before that crossover manifests for the full pilot.

## Bounded run verdict (sandbox)
2M-box (u,v) run on subset {1,2,3,4,6,7}: bound_by max_boxes, error none; dom (u/v)=166,707,
excl=0, cert=0, unres=833,232 (all physical interior), nph=0. VERDICT: BUDGET-EXHAUSTED,
interior-bound. NOTE the LIFO dive is a KNOWN-POOR instrument here (excl=cert=0: it never
reaches the small interior boxes where exclusion/certification fires) -- the same instrument
failure seen with Lever 2. So the bounded run neither demonstrates CLOSES nor refutes it.

## Honest net verdict: VIABLE and edge-wall-REMOVED, net closure UNDEMONSTRATED
What is established: (1) the wrapper is correct (root certifies); (2) it removes the edge
diagonal wall that was 100% of the old bottleneck; (3) it pays a bounded, vanishing interior
smearing penalty. What is NOT established: that 2b CLOSES the pilot, or that net it beats
old's 3M-box BUDGET-EXHAUSTED -- the bounded run is interior-bound and LIFO-confounded.

## Recommended next step (this is the decisive test, needs server budget)
A FULL-BUDGET (u,v) run on subset {1,2,3,4,6,7} at the v1.2 frame (3,000,000 boxes / 7200s),
ideally with a BETTER traversal than pure LIFO (best-first or bounded-breadth) so the
interior resolution region is actually reached. Hard verdict:
  CLOSES            : queue exhausts; root box certified; rest domain/constraint excluded.
  BUDGET-EXHAUSTED  : report unfinished AND whether it beats old's 1.45M edge-unresolved
                      (i.e. did removing the exponential edge wall net-reduce the total).
  TECH              : crash/NaN/etc.
Two implementation levers to consider if interior-bound persists: (a) a non-LIFO traversal
to reach the resolving region; (b) reduce interior smearing (higher-order AA, or a HYBRID
that uses (u,v) only near the edge and native c,d in the interior).

## Correction to the 2b finding
The 2b finding's "REOPENS Path 2 (strong positive) -> proceed to broader run" is AMENDED:
the edge result is real and large, but the broader (bounded) run reveals an interior smearing
trade not tested when 2b was written. Path 2b is VIABLE and the edge wall is removed; net
pilot closure remains an OPEN question pending a full-budget, better-instrumented run. The
direction is genuinely promising (exponential gain vs vanishing penalty) but not yet proven.

## Files
  probe_path2b_corr.py             transformed Krawczyk + full classify + bounded run
  path2b-bounded-run-findings.md   this report (probes inline, reproducible)

SHA-256 hashes for all files in this unit are recorded in `docs/SHA256SUMS`