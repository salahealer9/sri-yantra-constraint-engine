# FROZEN RESULTS — Śrī Yantra Spherical Constraint Census

**Immutable record. All manuscripts, preregistration appendices, Zenodo deposits, and
referee responses cite THIS artifact rather than restating numbers, to prevent drift.**

- **Study:** altitude-resolved existence classification of the 815 well-posed size-5
  Śrī Yantra constraint subsets on the sphere (Rao 1998 formalization), extending the
  certified plane census.
- **Status:** confirmatory phase closed. Census outputs are stable under the strongest
  controls and reproduced exactly in an independent rerun.
- **Date frozen:** 2026-06-21

---

## 1. Procedure of record

- **Spherical preregistration** v1.0.2 — version DOI 10.5281/zenodo.20778921, concept
  DOI 10.5281/zenodo.20778920; git tag `spherical-prereg-v1.0.2`.
- **Amendment history**
  - **v1.0.0** — registered procedure (Gates 1–6, five-way classification, §6 α→0
    consistency gate, Gate-6 pole-domain HALT).
  - **Amendment 01 (v1.0.1)** — reproducible stable `hashlib` seeding (replaces
    version-unstable `hash()`); plane-faithful seeding policy (box = seeding heuristic,
    accept any in-domain Gate-4-valid figure); documented targeted near-degenerate
    seeds; retain-and-flag tiers (robust / tangency / near_degenerate).
  - **Amendment 02 (v1.0.2)** — near-pole seeding completeness (altitude grid extended
    to 76/80/84/88°); generic high-altitude completeness audit on negatives; parallel
    resumable runner with §6 survivor-consistency self-check.
- **Engine:** `spherical_existence_mapper.py`, SHA-256
  `a0772717e4d07c327e744608bd0abf4f9a50d5f343b07fc3ffc119a7cd8a59af`.
  Constructor `spherical_geo_check.py` and `sriyantra.py` unchanged from v1.0.0.
- **Bridge theorem** (degree-normalized continuation, κ ∝ 1/α): DOI
  10.5281/zenodo.20772247.
- **Plane census of record:** 815 subsets = 134 feasible / 681 infeasible
  (size-5 subsets {F1,F2} + 3 of {F3…F20}, 816 combinations minus the rank-deficient
  {1,2,8,9,16}). Plane preregistration DOI 10.5281/zenodo.20630790; plane dataset
  concept DOI 10.5281/zenodo.20708335; frozen plane engine v0.1.0 DOI
  10.5281/zenodo.20617730 (commit `75aed90`, tag `tier2-freeze-2`, blob `985c741`).

---

## 2. Census result (815 subsets)

| Class | Count |
| --- | --- |
| PLANE_CONTINUATION | 134 |
| SPHERICAL_ONLY | 89  (76 robust + 13 flagged tangency/near_degenerate) |
| POLE_OUT_OF_DOMAIN | 258 |
| ALGEBRAIC_ONLY | 318 |
| ALGEBRAIC_EMPTY | 16 |
| **HALT (PLANE_INCONSISTENCY)** | **0** |

- Total flagged across all classes (excluded from robust counts): 16.
- Reclassified by the high-altitude completeness audit: 0.
- **§6 α→0 consistency:** all 134 plane survivors → PLANE_CONTINUATION (no leakage:
  PLANE_CONTINUATION ⊆ survivors; no survivor outside it).

### Reproducibility invariants

- **Canonical class hash** (cross-machine invariant, over subset→five-way class):
  `4ea9cbfe121a993f`.
- **Robust SPHERICAL_ONLY set hash:** `c76190da1ea29db1`.
- **Replication:** two independent full executions of the registered procedure (v2,
  and a thread-pinned v3) produced **identical** classifications — both hashes and all
  counts match bit-for-bit. The robust set did not move; robust figures converge with
  margin, as a deterministic engine requires.

---

## 3. Confirmatory findings

1. **134 / 134** plane-feasible subsets continue to an in-domain pole limit.
2. **0** plane-infeasible subsets produce an in-domain pole limit (zero HALT).
3. **76** plane-certified-infeasible subsets admit **robust** Gate-4-valid spherical
   realizations over bounded altitude intervals (curvature-confined; no planar analogue).
4. Results **reproduced exactly** in an independent rerun (identical hashes).

**Abstract-grade statement.** Among the 681 plane-certified-infeasible Śrī Yantra
constraint subsets, 76 admit robust Gate-4-valid spherical realizations over bounded
altitude intervals while preserving complete consistency with the certified planar
census (134/134 feasible subsets continue to in-domain pole limits; 0 infeasible
subsets do).

The central contribution is the **pair 134/134 and 0**: the spherical extension remains
faithful to the certified planar boundary while discovering genuinely new geometry.

---

## 4. Exploratory observations (fenced — recorded, not confirmatory)

- **ALGEBRAIC_EMPTY = 16**, reproducible. **Budget-relative**: "no figure found under
  the registered search budget," NOT a proof of nonexistence.
- **H3 ("algebraic emptiness may not occur") — not supported.** Sixteen subsets remained
  algebraically empty under the preregistered procedure, reproducibly (16 > 0). This is
  a budget-relative statement, not a proof of nonexistence.
- **EO-1:** F7 appears in 32 of the 76 robust subsets (≈42%), the most frequent
  non-essential constraint (F6/F3/F4 next). Recorded only; to be tested on data that did
  not generate it.
- Fold inventory; ordering-vs-collision boundary-mechanism frequencies; constraint- and
  altitude-distribution analyses — all exploratory.

---

## 5. Classification hierarchy (conceptual outcome)

Four strictly nested existence levels, demonstrated non-equivalent by the census:

algebraic root ⊇ constructible figure ⊇ Gate-4-valid figure ⊇ pole-consistent figure.

Most of the project's retracted counts came from conflating adjacent levels; the
five-way classification exists to keep them separate.

---

## 6. Audit trail (every positive claim has an independent control)

| Claim | Control that tested it |
| --- | --- |
| Roots correspond to figures | Gate-4 constructor |
| Folds are real | Pseudo-arclength reversal |
| Validity boundaries exist | Ordering / collision diagnostics |
| Plane census integrity | Pole-domain alarm (Gate 6) |
| Curvature-only figures exist | Existence-interval mapper |
| Census completeness | Survivor-consistency gate (§6) |
| Reproducibility | Stable-seed determinism + v2 ≡ v3 replication |

---

## 7. Provenance (fill at signing)

- Repository commit (signed): `6c36754e7e42437a077ca5db8936fefb22468401`
- Engine SHA-256: `a0772717e4d07c327e744608bd0abf4f9a50d5f343b07fc3ffc119a7cd8a59af`
- Census CSV SHA-256 (v3): `220f0c04059d5a3f34f7b9dacc1edb51c7551d3ac3bcdd663297ed1ce02ab03f`
- Git tag: `spherical-prereg-v1.0.2`  (this record: tag `frozen-results-spherical-v1`)
- GPG signature: `FROZEN-RESULTS-spherical-census.md.asc`
- OpenTimestamps proof: `FROZEN-RESULTS-spherical-census.md.asc.ots`
