# Design Memo — Next Lever: Volume-Reduction Paths (decision, not build)

**Purpose.** After the v1.2 BUDGET-EXHAUSTED pilot, the sound-but-partial cone-edge
pre-filter (~20% unfinished-work reduction), and the FIFO negative result (pure
breadth-first rejected; wall is a depth-AND-breadth VOLUME problem around the curved
acos domain boundary), choose the next lever from a fair comparison. No build until
chosen. This memo compares two paths and names a third intermediate option.

## The obstacle, precisely (from the FIFO result)
Resolving subset {1,2,3,4,6,7} on B_sphere requires reaching depth ~40-54 (where
boxes are small enough to exclude/certify) across the curved acos domain boundary
(r=c, r=d, i.e. h+c=pi/2, h+d=pi/2). Axis-aligned subdivision approximates these
DIAGONAL surfaces with a staircase -> exponentially many boxes at resolving depth.
LIFO reaches depth in a narrow slice; FIFO covers breadth but cannot reach depth.
Neither escapes the volume. A useful lever must REDUCE THE BOX VOLUME needed, by
either (A) excluding more of the invalid bulk cheaply, or (B) removing the
geometric mismatch between axis-aligned boxes and the diagonal boundary.

---

## PATH 1 (CONSERVATIVE) — Full-chain analytic pre-filter extension
Extend the proven cone-edge pre-filter (h_lo+c_lo>pi/2, h_lo+d_lo>pi/2) to the
remaining full-chain acos domain edges (radial r16..r19 and any other acos-arg /
denominator domain inequalities), each as an independent proof-by-inequality.

- **What it changes:** more cheap analytic `domain` exits before AA evaluation.
  Same architecture as the committed cone-edge filter. Boxes stay in (b,c,d,e,g,h);
  substrate unchanged.
- **Attacks:** the invalid BULK (more boxes excluded before subdivision). Does NOT
  attack the boundary-STRADDLE boxes — those still need axis-aligned subdivision of
  the diagonal surface (the actual volume driver).
- **Soundness work:** modest. Per-edge proof-by-inequality + harness validation +
  Gate-M c3 re-check. Same tier as cone-edge; low risk.
- **Plausible closure:** LOW. The FIFO result showed the binding cost is the curved
  boundary, not the bulk. Cone-edge already excluded the obvious bulk with
  diminishing returns; r16..r19 edges add more bulk exclusion but leave the
  staircase problem intact. Expected outcome: shaves unfinished work further
  (maybe another 10-20%), does not close. Same CHARACTER as cone-edge: helps,
  does not close.
- **Risk if it fails:** near-zero wasted effort; the filters are independently
  useful and compose with any future lever.

---

## PATH 2 (AMBITIOUS) — Coordinate-straightening
Reformulate in (b, u=h+c, v=h+d, e, g, h). PROBED FACT: this makes BOTH dominant
acos boundaries axis-aligned (u=pi/2, v=pi/2) simultaneously; the map is invertible
and volume-preserving (det J = 1).

> **Caveat (volume).** The map is volume-preserving as a LINEAR transformation, but
> the axis-aligned HULL of the transformed registered box may be larger than the
> exact transformed parallelepiped. If an implementation replaces the sheared
> transformed domain with a rectangular hull in (u,v,h), it reintroduces extra
> volume — potentially eating much of the straightening benefit. Working in the
> exact sheared region (not its hull) is required to realize the gain.

- **What it changes:** the diagonal valid/invalid boundary becomes a single
  axis-aligned cut. One split on u separates h+c<pi/2 (x1 real) from h+c>pi/2 (x1
  undefined) cleanly — no staircase. Directly removes the geometric mismatch the
  FIFO result identified as the core obstacle.
- **Attacks:** the boundary itself (B) — the actual volume driver — not just the
  bulk. This is why it could CLOSE rather than shave.
- **Cost / footprint (the scoping fact):** the transform couples every box to h
  (c=u-h, d=v-h), so an axis-aligned box in new coords is a SHEARED parallelepiped
  in old coords. The entire certified pipeline is built in (b,c,d,e,g,h): the AA
  substrate (aar_sphere value+dual forms), chain_sphere, the full-chain domain
  guard, and the 6-var Krawczyk Jacobian all assume axis-aligned old-coord boxes.
  Straightening requires EITHER (a) rebuilding the substrate/chain/Krawczyk in
  transformed coordinates (substrate-scale effort, comparable to the original
  spherical substrate build), OR (b) evaluating from sheared boxes in old coords
  (wider enclosures — partially defeats the purpose).
- **Open unknowns that MUST be resolved on paper first:**
  1. The OTHER seams (iso cos(2x) inflections at x10/x13/x7; atan inflections;
     denominator zeros) are NOT straightened by u=h+c. Does the transform leave
     them unchanged, or complicate them? If it relocates the staircase to another
     seam, the lever fails.
  2. Krawczyk contraction in transformed coords: the Jacobian transforms by J^{-1};
     conditioning near u=pi/2 (the straightened edge) must be checked — straightening
     the domain edge may or may not improve the constraint conditioning there.
  3. The registered box B_sphere (TABLE1-derived hull, widened) must be re-expressed
     and its domain interpretation re-validated in new coords.
- **Soundness work:** substantial — a full re-derivation + Gate-M re-validation of
  the transformed pipeline. This is a methodological move on the scale of the
  original substrate, NOT a pre-filter patch.
- **Plausible closure:** POTENTIALLY HIGH if the non-acos seams survive the
  transform; UNCERTAIN until unknown (1) is checked. High variance.

---

## PATH 3 (INTERMEDIATE) — Boundary-aware split PRIORITY (no substrate rebuild)
Capture PART of Path 2's upside at Path 1's risk: keep boxes axis-aligned in
(b,c,d,e,g,h) and the substrate unchanged, and change only WHICH already-sound split
is chosen first. "Priority", not a new criterion: it adds no mathematical test, it
only reorders splits that are all individually sound.

It does NOT straighten the diagonal boundary — axis-aligned splits in
(b,c,d,e,g,h) cannot straighten a diagonal surface. It preferentially reduces the
signed seam intervals h+c-pi/2 and h+d-pi/2 (a faster staircase), before falling
back to widest-axis splitting.

**Deterministic split rule (so the experiment is reproducible, not "whatever seems
best"):**
```
For each box compute the signed seam intervals:
  S_c = [h_lo + c_lo - pi/2,  h_hi + c_hi - pi/2]
  S_d = [h_lo + d_lo - pi/2,  h_hi + d_hi - pi/2]
If NEITHER S_c nor S_d straddles 0:
  use the v2 widest-axis split (unchanged).
If one or both straddle 0:
  test candidate splits along h, c, d; choose the split dimension whose two
  children MINIMIZE total post-split seam-straddle width.
  Tie-break: larger coordinate width, then deterministic order h, c, d.
```

- **What it changes:** driver split-dimension choice only (like the FIFO change was
  driver-only). Substrate, classify, Krawczyk all unchanged.
- **Attacks:** staircase efficiency — fewer boxes to carve the diagonal — without
  reformulating coordinates.
- **Soundness work:** LOW. Split CHOICE does not affect soundness (any split is
  sound; only efficiency changes). Gate-M unaffected (same as FIFO: split/traversal
  order does not change which boxes certify/exclude). Just re-measure.
- **Plausible closure:** UNKNOWN, likely between Path 1 and Path 2. Cheap to test.
- **Why it is attractive:** cheapest test of whether boundary-aware subdivision helps
  at all. A clear win is strong evidence the full coordinate-straightening (Path 2)
  would pay — de-risking the big move. A null result means the volume problem is
  deeper than boundary alignment and Path 2's upside is doubtful.

---

## Recommendation
The FIFO result says the bulk is not the binding cost — the curved boundary is. So
Path 1 (bulk exclusion) is low-risk but unlikely to close. Path 2 (straightening)
attacks the actual obstacle but is a substrate-scale reformulation with a real open
unknown (the non-acos seams) and the axis-aligned-hull volume caveat.

**Decision: build Path 3 next** as the cheap, substrate-free probe of whether
boundary-aware subdivision helps — same discipline as FIFO (driver-only, flagged
copy, Gate-M unaffected). Comparison rows at the standard 400k budget:
```
  v2 cone-edge LIFO (widest-axis)          baseline (unfinished 154,097)
  v3 cone-edge FIFO                        negative reference
  v4 cone-edge boundary-aware-split LIFO   the test
```
Success signal is NOT "closes". It is:
```
  - unfinished work drops materially below 154,097
  - max-depth unresolved drops
  - domain/constraint exclusions appear earlier
  - queue does not explode (stays LIFO-bounded, ~hundreds)
```
A clear Path-3 win de-risks and motivates the full coordinate-straightening (Path 2,
scoped on paper first — the non-acos-seam check before any code). A Path-3 null
result means the volume problem is deeper than boundary alignment, Path 2 becomes a
gamble, and the conservative full-chain analytic filters (Path 1) may be the better
low-risk next step. Path 1 can be done anytime as a low-cost composable improvement,
but should not be expected to close.

This keeps the pattern: cheapest informative experiment next, big methodological
move only after the data supports it. No build until this path is chosen (it is).

SHA-256 hash for this file is recorded in `docs/SHA256SUMS`