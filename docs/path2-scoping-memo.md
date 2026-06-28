# Path 2 (Coordinate-Straightening) — Decision-Gate Scoping Memo

**Status.** Exploratory analysis (paper + cheap probes; no engine code). Decides whether
the coordinate transform deserves a build. Verdict at the end. Frozen v1.2 UNCHANGED.

## The transform
T : (b, c, d, e, g, h) -> (b, u=h+c, v=h+d, e, g, h);  inverse c=u-h, d=v-h.
Symbolic facts (verified): det(dT)=det(dT^-1)=1 (volume-preserving, globally invertible,
introduces NO singularity of its own); it is a SHEAR (c=u-h, d=v-h), so the new h-column
of any Jacobian becomes (old h-col) - (old c-col) - (old d-col).

What it straightens: the two acos DOMAIN diagonals
  x1 real edge  cos(r)/cos(c)=1  <=>  h+c=pi/2  <=>  u=pi/2   (axis-aligned plane)
  x2 real edge                   <=>  h+d=pi/2  <=>  v=pi/2   (axis-aligned plane)
Axis-aligned splits on u (resp. v) then separate the valid (u<pi/2) and invalid slabs\nDIRECTLY, 
without staircasing the diagonal as the original coordinates force. (A box\nstraddling u=pi/2 or 
v=pi/2 still splits, but the seam it splits ON is now an axis,\nnot a diagonal — so resolution is 
O(splits) along that axis, not an exponential\nstaircase approximating a slanted surface.)

## Geometry note (carries into the micro-probe design)
T(B_sphere) is NOT an axis-aligned rectangular box: under the shear it is a sheared
PARALLELEPIPED in (b,u,v,e,g,h). A branch-and-prune driver needs an axis-aligned
domain, so the micro-probe must choose between (i) the EXACT transformed parallelepiped
T(B_sphere) (tighter, but the driver must subdivide a non-rectangular region) and
(ii) an axis-aligned HULL B_uv enclosing it (rectangular, driver-friendly, but the hull
ADDS volume the original box did not contain — the same hull-reintroduces-volume caveat
as the original design memo). Which option, and how much volume the hull adds, is itself
part of what the micro-probe must measure; it is not free.

## Unknown 1 — non-acos seam survival (does a NEW wall appear?)
The transform straightens ONLY seams x1, x2. Other seams remain curved/diagonal in (u,v,h):
  - radial acos inflection cos(A)cos(B)=0: e.g. b+c=pi/2 -> b+u-h=pi/2 (diagonal); NOT straightened
  - atan inflections sin(S)=0 (S a sum of arcs): curved; NOT straightened
  - denominators sin(c+d)=sin(u+v-2h): diagonal; NOT straightened
  - cos(2x)/cos(x) conditioning: an arc-VALUE property, unchanged by the transform

PROBE (decisive for the CURRENT wall). Of the unresolved (max_depth) boxes in a 200k v2
dive (76,890 boxes):
  straddle v=h+d=pi/2 (acos x2)     : 100.0%
  straddle u=h+c=pi/2 (acos x1)     :  26.2%
  straddle EITHER acos diagonal     : 100.0%   <- Path 2 straightens exactly these
  straddle NEITHER (other seam)     :   0.0%
=> The ENTIRE current unresolved wall IS the acos domain diagonal. None of it is the
   other (surviving) seams. Path 2 attacks precisely the binding bottleneck.

HONEST RESIDUAL RISK (cannot be settled on paper). "0% stuck on other seams now" means
those seams are UNREACHED — the dive is consumed on the diagonal and never reaches the
regions where atan-inflection / denominator seams live. Once Path 2 collapses the
diagonal, the dive would reach new territory; a currently-unreached curved seam COULD
become a new (smaller or comparable) wall. This is consistent with the Lever-2 finding
(the inflection is off the critical path only because the dive never gets there). Whether
a new wall appears is an EMPIRICAL question that only a transformed-coordinate probe can
answer; it is not resolvable analytically.

## Unknown 2 — Krawczyk conditioning under the shear (COMPUTED, decisive)
At the known Newton root (residual 4e-16), Jacobian condition number:
  cond(J_old) [b,c,d,e,g,h] = 2.58e+02
  cond(J_new) [b,u,v,e,g,h] = 1.37e+02     ratio 0.53  -> conditioning IMPROVES ~47%
  smallest singular value : 3.24e-02 -> 4.19e-02  (up, favorable)
  largest  singular value : 8.35e+00 -> 5.76e+00  (down, favorable)
Mechanism: the old h-column was near-aligned with the c,d columns (the diagonal coupling);
the shear de-correlates them, de-stretching the Jacobian. The known root therefore stays
well-conditioned — better — in transformed variables: Krawczyk contraction at the root is
not a Path-2 risk, it is a Path-2 benefit. NOTE the GM-1 ill-conditioning (cos(2x)/cos(x)
near the arc edge, F3/F4/F6) is an arc-VALUE property and is UNCHANGED by the transform —
neither helped nor hurt.

## VERDICT: NEEDS-MICRO-PROBE, strongly leaning GO
Two of the three concerns are resolved FAVORABLY as far as paper allows:
  (a) the transform provably straightens the diagonal to axis-aligned planes [symbolic];
  (b) the diagonal is 100% of the current unresolved wall [probe] — Path 2 hits the exact
      binding bottleneck, not a peripheral one;
  (c) root conditioning IMPROVES 2x under the shear [computed].
The single unresolved concern is the residual risk in Unknown 1: a currently-unreached
curved seam could become a new wall after straightening. That is exactly — and only — what
a tiny transformed-coordinate probe tests, cheaply, BEFORE committing to a full engine.
A clean GO would require ruling out the new-wall risk, which paper cannot; a NO-GO is
unjustified given (a)-(c). Hence: build the micro-probe next, not the full engine.

## If GO: the first build is a MICRO-PROBE, not the transformed engine
A tiny transformed-coordinate probe (point / Jacobian / SHORT dive), NOT a branch-and-prune
rebuild. Minimum content:
  1. Transformed box B_uv = T(B_sphere) and the inverse-image evaluation F_new = F_old o T^-1;
     confirm the acos domain edge in B_uv is the axis-aligned slab u in [.,pi/2], v in [.,pi/2]
     and that a single split on u/v domain-excludes the invalid slab (vs the old staircase).
  2. Certify the known root in transformed coords (AA-Krawczyk) and confirm 'unique' at small
     r with the improved conditioning.
  3. A SHORT transformed dive (e.g. 50-100k boxes) restricted to the now-straightened region,
     instrumented to detect whether a NEW curved seam (atan inflection / denominator) becomes
     the dominant unresolved cause — the residual-risk test. Predicted (not asserted): the
     diagonal staircase collapses; the open question is what, if anything, replaces it.
### Micro-probe decision rule (explicit)
GO signal (proceed to full transformed build):
  - the known root certifies 'unique' in transformed coordinates (improved conditioning holds);
  - axis-aligned u/v domain splits remove the diagonal unresolved wall (the 100% collapses);
  - no new seam dominates the unresolved boxes within the short dive.
NO-GO signal (abandon or rethink Path 2):
  - transformed boxes become much wider/looser through the sheared inverse map (hull volume
    or dependency blow-up swamps the diagonal gain);
  - Krawczyk fails to certify at the known root in transformed coordinates;
  - unresolved boxes merely SHIFT to a new, comparably severe curved seam.

Only if the micro-probe shows the diagonal collapses AND no comparably-bad new wall appears
should the full transformed substrate/driver be built. The substrate-scale rebuild remains
out of scope until then.

## Files
  path2-scoping-memo.md   this memo (analysis; the probes are inline, reproducible)

SHA-256 hash for this file is recorded in `docs/SHA256SUMS`
