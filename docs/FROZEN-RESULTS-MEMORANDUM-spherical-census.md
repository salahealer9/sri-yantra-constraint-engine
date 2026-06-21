# FROZEN RESULTS MEMORANDUM — Śrī Yantra Spherical Census

Date frozen: 2026-06-21
## Procedure
- Preregistration: spherical v1.0.2 — DOI 10.5281/zenodo.20778921 (concept 10.5281/zenodo.20778920); Amendments 01–02.
- Engine: `spherical_existence_mapper.py` — SHA-256 `a0772717e4d07c327e744608bd0abf4f9a50d5f343b07fc3ffc119a7cd8a59af`.
- Bridge theorem: DOI 10.5281/zenodo.20772247.
- Universe: 815 well-posed size-5 subsets. Plane census of record: 134 feasible / 681 infeasible.

## Counts (815 subsets)
| Class | Count |
| --- | --- |
| PLANE_CONTINUATION | 134 |
| SPHERICAL_ONLY | 89 (76 robust + 13 flagged) |
| POLE_OUT_OF_DOMAIN | 258 |
| ALGEBRAIC_ONLY | 318 |
| ALGEBRAIC_EMPTY | 16 |
| HALT (PLANE_INCONSISTENCY) | 0 |

- Total flagged (excluded from robust counts): 16. Audit reclassifications: 0.

## Confirmatory
- 134 / 134 plane-feasible subsets continue to an in-domain pole limit.
- 0 plane-infeasible subsets produce an in-domain pole limit.
- 76 robust curvature-confined (SPHERICAL_ONLY) subsets.
- ALGEBRAIC_EMPTY = 16 — under the registered search budget (not a proof of nonexistence).

## Reproducibility
- Canonical class hash (subset→five-way class): `4ea9cbfe121a993f`.
- Robust SPHERICAL_ONLY set hash: `c76190da1ea29db1`.
- Replication: v2 ≡ v3 — two independent full executions produced identical classifications, hashes, and counts.

## Provenance

See `docs/FROZEN-RESULTS-spherical-census.md` for full provenance (commit, CSV hash, GPG signature, OpenTimestamps proof, git tag).
