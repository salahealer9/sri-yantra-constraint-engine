# Path 2 Micro-Probe (2a, naive-interval) — Findings

> SUPERSEDED-IN-PART: this probe tested the NAIVE-INTERVAL implementation only. Its
> finding that THAT implementation cannot certify the root is correct and stands. Its
> broader pessimism ("benefit intrinsically capped", "reassess not proceed") was an
> ARTIFACT of correlation loss and is SUPERSEDED by probe 2b
> (path2b-correlation-preserving-finding.md): building c=u-h, d=v-h as affine/Dual
> EXPRESSIONS preserves the correlation, certifies the root (cond 137), and the edge
> region resolves dramatically better with depth. Path 2 is REOPENED. Read 2b for the
> live verdict.


**Status.** Exploratory micro-probe (short dives + path-independent resolution + root
certification test; NOT an engine). Tests the Path-2 scoping memo's open risk before any
substrate-scale build. Frozen v1.2 UNCHANGED. This UPDATES the memo's "strongly leaning
GO" verdict downward — the probe surfaced two issues paper analysis missed.

## What the probe built (and reused)
Native (u,v) coordinates (u=h+c, v=h+d) as SPLIT AXES, with the acos domain edge handled
NATIVELY (exclude when u_lo>pi/2 / v_lo>pi/2; split on u/v at pi/2 when straddling). The
rest of the chain was REUSED from the frozen old-coord substrate via an interval inverse
map c=u-h, d=v-h ("naive-native"). This is the cheap path a build would try first.

## Finding 1 — the geometric straightening WORKS (confirmed)
- Native unresolved boxes straddling u/v=pi/2: 0.0% (old coords: 100%). The axis-aligned
  u/v split eliminates the diagonal acos-edge STAIRCASE that was the entire wall.
- Native generates FEWER total boxes resolving a fixed region (cap14: 13,395 vs 20,127;
  cap16: 51,795 vs 69,535) — the staircase is gone.
The memo's central geometric claim holds: in (u,v) the diagonal becomes axis-aligned.

## Finding 2 — naive-native CANNOT certify the root (correlation loss, not width)
Root certification via the reused old-coord Jacobian on the inverse-mapped box:
  native r = 3e-3 .. 1e-4 : INDETERMINATE at every r (old coords: unique at 3e-4, 1e-4).
  shrinking to r=1e-5 (smeared c,d radius 2e-5, far inside the old contraction zone):
  STILL indeterminate.
=> Not a width effect. The inverse map makes c=u-h, d=v-h, but the reused old Krawczyk
   treats c,d,h as INDEPENDENT, discarding the u,h correlation. That correlation loss
   defeats contraction at ALL radii tested. The cheap "reuse the old chain via inverse
   map" path cannot certify the root in this probe (a property of this tested architecture,
   not a proof that no inverse-map variant could).

## Finding 3 — value smearing in the NAIVE-INTERVAL path (NOT intrinsic; see 2b)
In THIS naive-interval probe the constraint values are smeared by c=u-h widening.
(NOTE: probe 2b later showed affine/Dual EXPRESSIONS preserve the correlation and remove
most of this — so the smearing is an artifact of the interval implementation, not intrinsic.)
For the interval path as tested: cos(c)=cos(u-h) over a box has width
u_width+h_width (interval arithmetic cannot cancel h). Path-independent resolution of a
fixed seam-straddling region (which already carries this smearing) shows a depth-dependent
crossover:
  cap14: native resolved 4.4% vs old 14.8%  (smearing hurts on LARGE boxes)
  cap16: native resolved 9.1% vs old 7.2%   (native OVERTAKES as boxes shrink)
The smearing scales with box width, so it dominates shallow and vanishes deep; whether
the net is favorable at full census depth is UNRESOLVED within feasible probe depth.

## What a TRUE native rewrite would and would not fix
WOULD fix: root certification — computing the Krawczyk operator with the native (u,v,h)
Jacobian respects the correlation; that Jacobian is BETTER conditioned (cond 1.37e2 vs
2.58e2, computed at the root), so it is PREDICTED (not proven — rigorous proof needs the
native AA substrate) to certify. WOULD fix: the domain-edge staircase (already shown).
WOULD NOT fix: the intrinsic constraint-value smearing of c=u-h (Finding 3), which caps
the upside and makes the net benefit depth-dependent and uncertain.

## Verdict (updates the scoping memo): NOT a clean GO
The micro-probe did its job — it converted "strongly leaning GO" into a clear-eyed
cost/benefit by surfacing two issues paper missed:
  - the cheap reuse path is DEAD (correlation loss -> no root certification at any r);
  - the only viable path is a substrate-scale native rewrite (chain + Jacobian in (u,v)),
    whose root certification is predicted-favorable but whose NET branch-and-prune benefit
    is CAPPED by intrinsic constraint smearing and is depth-dependent/uncertain.
Against my own GO/NO-GO rule: "root certifies in transformed coordinates" FAILS for the
testable implementation; "transformed boxes much looser through the sheared inverse map"
HOLDS (correlation loss). Only "u/v domain splits remove the diagonal wall" passes.
=> On current evidence a substrate-scale Path-2 rewrite is NOT clearly justified: large,
   fixed cost for an uncertain, intrinsically-capped gain. This is a legitimate
   reassessment point, NOT an auto-proceed.

## Options from here (honest menu, no auto-pick)
  A. STOP optimizing the spherical pilot bottleneck. Accept cone-edge (~20% shave) as the
     practical best for axis-aligned interval B&P here; record the wall as a characterized,
     likely-intrinsic limit of axis-aligned interval methods on this curved-domain system.
  B. BUILD the true native (u,v) substrate anyway, accepting it as a research bet: the only
     remaining lever on the diagonal, root certification predicted-viable, net benefit to be
     MEASURED (the probe cannot settle the depth-dependent crossover). High cost, uncertain
     payoff, now with eyes open.
  C. A different attack not yet scoped (e.g. non-axis-aligned/parallelepiped boxes that
     keep c native AND split along the diagonal; or a co-tree that tracks the u,h
     correlation through the constraint values). Unscoped; would need its own memo.

## Recommendation
Lean A or C over B. The probe lowered Path 2's expected value: its upside is now known to
be capped by intrinsic smearing, and B is a substrate-scale commitment for an uncertain,
possibly-marginal gain. If the diagonal must be beaten, C (correlation-preserving boxes)
attacks the ACTUAL newly-identified root cause (correlation loss) rather than just the edge
geometry — but it is unscoped and should be a paper memo before any code, same discipline.

## Files
  probe_path2_native.py          the micro-probe (native u,v dive + inverse map)
  path2-microprobe-findings.md   this report (probes inline, reproducible)

SHA-256 hashes for all files in this unit are recorded in `docs/SHA256SUMS`