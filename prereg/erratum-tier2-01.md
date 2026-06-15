# Erratum 01 to the Tier-2 confirmatory freeze — certification-geometry conformance

**Status:** implementation-conformance patch (NOT a methodology amendment).
**Registered method unchanged.** Affects: frozen tool `campaign.py`.
**Detected:** 2026-06-15, during the registered §6 Tier-1 cross-check.
**Superseded freeze:** `tier2-freeze` (commit `f0581fe`).
**Corrected freeze:** `tier2-freeze-2` (commit TBD).

## 1. The registered specification
Amendment-02 §B2(iii) registers AA-Krawczyk certification via the operator
`K(X) = m − Y·F(m) + (I − Y·J(X))·(X − m)`, with the test **`K(X) ⊆ int(X)`**
certifying a unique real root **in the box X** and `K(X) ∩ X = ∅` certifying none.
Here `X` is *the box* — the bisected, axis-aligned (anisotropic) enumeration box of
§B2(ii). The certification radius `r_cert` (§B2(ii)(b)) is the **trigger** for *when*
to attempt certification (box radius ≤ `r_cert`); it is not the certification region.

## 2. The implementation defect
The frozen `campaign.krawczyk` substituted an **isotropic cube** `[center ± rad]`,
with `rad` the maximum coordinate half-width, for the box `X` in both places `X`
enters the operator: the affine-arithmetic Jacobian enclosure `J(X)` and the
inclusion test `K(X) ⊆ int(X)`. Because `rad` exceeds the box's half-width in its
narrower coordinates, this cube is a strict superset of `X`. Near a face of
`B_plane`, the cube extends up to `rad` beyond the face, so a real root lying within
`rad` of a face **but outside `B_plane`** can satisfy the (cube-based) test and be
certified as an in-region figure — exceeding the scope of the preregistered domain.

## 3. Observed effect (localized)
The registered §6 Tier-1 multistart cross-check, which tests strictly within
`B_plane`, flagged a single disagreement: subset **{1,2,4,11,16}**. Its sole real
root is `[0.57176, 0.24883, 0.25109, 0.50672, 0.08387]`, with `g = 0.08387` lying
**0.00030 below** `B_plane`'s lower g-face (`0.084179`). The certifying box had
g-range `[0.084179, 0.087313]` (lower edge on the face); the isotropic cube's
g-range was `[0.083327, 0.088166]`, extending `0.00085` past the face and capturing
the out-of-region root. A direct scan of every certified root in the original
`roots.jsonl` confirms this is the **only** certified root outside `B_plane`; the
cross-check independently reports `t1_extra = 0` (no in-region figure missed by
Tier-2) and `t1_missed = 1` (this subset).

## 4. Correction
`campaign.krawczyk` is corrected to certify over the **actual box X**: per-coordinate
half-widths `hwv = [(hi−lo)/2]` are used in the Jacobian enclosure (`DualR.var(k, ·,
hwv[k])`), in the `Khw` offset, and in the inclusion bounds (`Xlo = center − hwv`,
`Xhi = center + hwv`). This makes the certified region exactly `X ⊆ B_plane`,
conforming the implementation to §B2(iii). The change is **monotone** — the box is
contained in the former cube — so it can only *remove* certifications that lay
outside their box, never lose a genuine in-region root (which is re-certified by its
own enclosing box, modulo the registered dedup). No other parameter or code path is
changed.

## 5. Consequence
Under the conforming tool, {1,2,4,11,16} certifies **absent** in `B_plane`. The
corrected confirmatory classification is **134 feasible / 681 infeasible** (0
unresolved, 0 Tier-1 downgrades), independently reproduced by the strict-in-box
Tier-1 cross-check (`134 agree_feasible / 681 agree_infeasible / 0 t1_missed / 0
t1_extra`). The original run is archived under `enumeration/legacy_campaign_v1/`.

## 6. Process note
This correction is a positive instance of the registered two-tier design: Tier-2
produced a complete certified partition, the independent Tier-1 cross-check
challenged it, the lone disagreement was localized to a single boundary mechanism,
the confirmatory tool was brought into conformance with its own registered
specification, and the two tiers converged. The detection-and-correction occurred
**before** final interpretation, exactly as preregistration is intended to enable.
