# lift-generator-v2 — Specification (pre-implementation freeze)

**Status:** specification frozen prior to coding. Implementation refinement of the
spherical polynomial lift; **not** a methodological amendment (see §6).
**Supersedes for homotopy use:** lift-generator-v1 (SHA-256 `0ab7e220…`), which
remains valid as a residual-correct encoding but is unusable as a continuation
target (§1).
**Frozen instruments unchanged:** `sriyantra.py` (engine), `newton_validator.py`,
Amendment 04, the 3044 universe. No geometric result is affected.

---

## 1. Defect

lift-generator-v1 encodes every arc-equality constraint `Δ_i = 0` as

```
cos(Δ_i) − 1 = 0.
```

This is residual-correct (it vanishes exactly at solutions) but its gradient
along the base solution manifold is

```
∇_base [cos(Δ_i) − 1] = −sin(Δ_i) · ∇_base Δ_i ,
```

which is **zero at every solution** (where `Δ_i = 0`). Each such constraint
therefore contributes a null direction to the lift Jacobian, making genuine
solutions **singular** points of the polynomial system. Homotopy continuation
requires regular start solutions; a singular seed is rejected by the path
tracker's Newton corrector. The earlier validation (residual vanishing,
engine-equivalence) never tested regularity, so the defect was latent.

## 2. Mechanism (observed across the audit sample)

Only F3, F4, F6 use the curved cosine form `cos(V)·cos(X) − cos(2X)` (regular
gradient). Every other constraint is the flat `cos(Δ)−1` form. The predicted
corank of a size-six lift solution is therefore

```
corank(v1) = 6 − |subset ∩ {3,4,6}|.
```

This was an a-priori consequence of the mechanism, not a post-hoc fit. Tested at
**13 genuine Newton roots across 11 subsets**, it held **exactly** at all four
corank levels (3, 4, 5, 6), including the doubled family F13/F14/F15 and three
independent roots of one subset. Condition number at solutions: `10¹⁵–10¹⁸`
(singular). The base-coordinate constraint Jacobian is full rank 6, cond ≈ 258 —
the geometry is regular; the defect lives in the encoding.

## 3. Replacement

Encode arc-equality constraints by the **sine** of the same combo, leaving the
cosine forms untouched:

| constraint family | v1 form | v2 form |
|---|---|---|
| arc-equality (`CONS_ANGLE`: all except 3,4,6, incl. doubled 13,14,15) | `cos(combo) − 1` | `sin(combo)` |
| curved cosine (`CONS_COS` = F3, F4, F6) | `cos(V)·cos(X) − cos(2X)` | **unchanged** |

`sin(combo)` has gradient `cos(Δ)·∇Δ = ∇Δ ≠ 0` at solutions, restoring full rank.
Verified: the sine reformulation gives **corank 0** and cond `10²–10⁴` at every
one of the 13 tested roots. The system stays square (one equation per constraint).
The reformulation changes only the local defining equation of the zero set; it
does not alter the underlying geometric constraint being enforced.
The combo, variable ordering, structural blocks, and serialization are otherwise
identical to v1.

## 4. The extra branch (verified filtered)

`sin(combo) = 0` admits one branch beyond `Δ = 0`:
- non-doubled constraints: `combo = π`  ⇒ raw `|F_i| = π`;
- doubled F13/F14/F15 (combo = 2Δ): `2Δ = π` ⇒ `Δ = π/2` ⇒ raw `|F_i| = π/2`.

Both are rejected, two independent ways, with no new logic:
1. **Round-trip gate.** For arc-equality constraints raw `F_i = Δ_i`, so the
   extra branch has raw residual π or π/2, far above the acceptance tolerance
   `1e-7`. The existing engine round-trip rejects it.
2. **Geometry.** The branch is outside the admissible domain: pushing any
   arc-equality toward π drives the chain out of domain (DomainError) at
   arc-equality value ≈ 0.55, never approaching π.

Consequence: **v2 and v1 have identical admissible solution sets.** Gate-4 and
all downstream verdicts are unchanged.

## 5. Acceptance criteria (freeze gate)

lift-generator-v2 is frozen only when, on a representative subset sample:

1. **Residual equivalence** — every equation vanishes at engine-lifted roots to ≤ 1e-12.
2. **Solution-set equivalence** — no new admissible solutions are introduced by
   the reformulation (verified, §4); full solution-set equivalence will be
   verified by comparison on the first successful homotopy runs.
3. **Regularity** — Jacobian corank = 0 at every tested solution (the property
   v1 lacked; now first-class).
4. **Conditioning** — condition number at solutions reported; observed values in
   validation runs were `10²–10⁴`.
5. **Gate-4 invariance** — Gate-4 verdicts identical to the raw-engine verdicts.

These extend, not replace, the v1 validation; criterion 3 is the new permanent
lesson (residual ≠ regularity).

## 6. Scope and classification

**Not an amendment.** Amendment 04 froze the *role* — authoritative global
homotopy continuation on the spherical lift — and the agreement criterion,
universe, and outcome definition. None change. The polynomial encoding of an
arc-equality is an implementation detail of the lift; `sin(Δ)` and `cos(Δ)−1`
express the same geometric condition with identical admissible solutions (§4).
This is fixing a numerically pathological instrument implementation, documented
with full provenance, not changing the instrument's scientific role.

**Unaffected:** plane census, spherical 815, the 3044 universe, the bridge paper,
the Newton validator (base coordinates, already regular), and every frozen
geometric result.

**Affected:** the homotopy footer (orchestration, already separate from the
frozen generator) consumes v2 in place of v1; no homotopy result exists yet to
revise.

---

### Evidence appendix (diagnostics on record)

- `seed_lifter.py` — lift correctness: structural residual 4.4e-16 at a true root;
  control (perturbed non-root) → constraints 3.0e-2, structural still 2e-16.
- Jacobian audit — v1 corank 3 at the {1,2,3,4,6,7} root, cond 2e17; base
  Jacobian full rank 6, cond 258; lift map a rank-6 immersion; ratio elimination
  does not help; corank matches flat-constraint count.
- `regularity_audit.py` — `corank(v1)=6−|∩{3,4,6}|` and `corank(v2)=0` at all 13
  tested roots; cond v1 `10¹⁵–10¹⁸` → v2 `10²–10⁴`.
- `pi_branch_test.py` — the sole extra branch (Δ=π, or Δ=π/2 doubled) is filtered
  by the round-trip gate (raw = π, π/2) and is geometrically unreachable.
