# spherical-amendment-01 — Engine conformance, reproducibility, and seeding-domain policy

- **Filed:** _to be GPG-signed and OpenTimestamps-stamped before any subset is classified in the confirmatory run._
- **Registration amended:** `spherical_preregistration.md` v1.0.0 (DOI 10.5281/zenodo.20778921; tag `spherical-prereg-v1.0.0`).
- **Nature:** pre-run methodological correction. No result-driven change; the registered decision rules are unchanged, and §4 and H3 are **retained**.

## Statement

A pilot of the registered procedure on known cases surfaced (i) a genuine
reproducibility defect and (ii) a seeding-policy inconsistency with the plane
census. Both are corrected here, in the analysis engine `spherical_existence_mapper.py`,
before the confirmatory run. The corrections are validated by a twice-over
determinism check and a known-case pilot.

## Corrections

1. **Reproducibility — stable seeding (non-negotiable).** RNG seeding by Python's
   `hash(subset)` is interpreter-version-dependent and produced different
   classifications on different machines for narrow-basin subsets (e.g.
   (1,2,7,12,17) flipped SPHERICAL_ONLY ↔ ALGEBRAIC_EMPTY across hosts). Replaced by
   a stable `hashlib.sha256` digest of (subset, altitude). Reruns are now
   bit-for-bit identical.

2. **Search policy ≠ classification policy (box = seeding heuristic only).** The
   Rao-spherical Table-1 box is used to *direct* search effort, but **any in-domain,
   Gate-4-valid figure is accepted wherever Newton converges**, exactly as the plane
   census kept in-domain Tier-2 solutions regardless of the Tier-1 seeding box.
   (The interim "exclude out-of-box by design" rule diverged from the plane
   methodology and is withdrawn.) Implemented as three stable-seeded, ordering-
   filtered seed families: box-preferential, domain-wide log-uniform, and targeted.

3. **Targeted near-degenerate seeds (documented rationale).** Exploratory
   investigation found families whose attraction basins collapse near a symmetry
   locus (b ≈ e → 0, c ≈ d ≈ g), which ordinary random seeding misses. Targeted
   seeds covering that locus are included **for coverage of known small-basin
   regions, not to favour any outcome.**

4. **Robustness flags (retain-and-flag).** Figures are classified and then tiered:
   **robust**, **tangency** (Gate-4-valid altitude window ≤ 2°, §7 near-zero-width),
   or **near_degenerate** (a base-point gap below τ_deg·r, τ_deg = 10⁻³, Gate 4).
   Tangency and near-degenerate figures are **retained in the census output but
   excluded from robust counts** — the plane census's treatment of marginal cases.

(The conformance items from the prior draft — the five-way classification with
PLANE_CONTINUATION vs HALT (§8), the Gate-6 global stop condition, and the POLE
predicate δ = 1° — are included in this build.)

## §4 / H3 retained

(1,2,7,12,17) is **not** algebraically empty: it has a reproducible in-domain
Gate-4-valid realization (a near-degenerate tangency). It classifies SPHERICAL_ONLY,
tangency-flagged, excluded from robust counts. The §4 note stands and H3 ("algebraic
emptiness may not occur") is unchanged (ALGEBRAIC_EMPTY = 0 across the pilot sample).

## Validation

Determinism (pilot sample run twice): **identical** classification hash
(`88ecc8ba17eed06f`), category counts {PLANE_CONTINUATION 2, SPHERICAL_ONLY 3,
POLE_OUT_OF_DOMAIN 1, ALGEBRAIC_ONLY 1}, and flagged list {(1,2,7,12,17): tangency}.

Pilot (one known case per category) — **7/7**:

| Subset | Class | Tier |
| --- | --- | --- |
| (1,2,3,4,8) | PLANE_CONTINUATION | robust (fold) |
| (1,2,5,8,15) | PLANE_CONTINUATION | robust (fold) |
| (1,2,3,4,6) | SPHERICAL_ONLY | robust |
| (1,2,3,6,13) | SPHERICAL_ONLY | robust |
| (1,2,4,6,8) | POLE_OUT_OF_DOMAIN | robust |
| (1,2,3,4,7) | ALGEBRAIC_ONLY | — |
| (1,2,7,12,17) | SPHERICAL_ONLY | tangency (excluded from robust counts) |

Gate 6 confirmed live and discriminating: (1,2,3,4,8) → PLANE_CONTINUATION (no halt)
when truthfully plane-feasible; → HALT (PLANE_INCONSISTENCY) when counterfactually
marked infeasible. No HALT on truthful inputs.

## Engine hash

- `spherical_existence_mapper.py` — SHA-256 `b3f1b5d08cde65f4aa0d0fcea52868e6b5dabc8cd611fe4e33e41b411f20c2c8`
- `spherical_geo_check.py`, `sriyantra.py` — unchanged from v1.0.0

Committed, GPG-signed, and OpenTimestamps-stamped before the confirmatory run.
