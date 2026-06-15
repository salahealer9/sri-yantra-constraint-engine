# Legacy box B — superseded (provenance record)

**Status:** Superseded by **Amendment 03** (parameterization-coherence correction
of the plane Tier-2 confirmatory region). Retained for provenance only. **Not
active tooling.**

## Original literals

The hand-derived box that the plane Tier-2 enumeration initially inherited:

| var | lower | upper |
|-----|-------|-------|
| b | 1e-6 | 0.788471 |
| c | 1e-6 | 0.636399 |
| d | 1e-6 | 0.635884 |
| e | 1e-6 | 0.679513 |
| g | 1e-6 | 0.687977 |

(Lower bounds were positivity clamps at 1e-6.)

## Provenance audit

§6 specifies B as the per-variable [min, max] across **all rows of Rao's Tables 1
and 3**, widened 50 % each side, intersected with the valid domain. Audited
against the engine's hash-pinned tables, the realized literals are **not generated
by any single rule**:

- **b, g** reproduce the all-14-row pooled maximum exactly (*keep-largest*):
  b = 0.788471, g = 0.687977.
- **c, d, e** reproduce the all-14-row pooled range with each variable's single
  largest value removed (*drop-largest*): c = 0.636398, d = 0.635884, e = 0.679513.

No consistent procedure yields all five bounds; the realized box was a collection
of hand-applied literals rather than a deterministic construction.

## Reason for supersession

1. **Heterogeneous parameterization.** "All rows of Tables 1 and 3" pools Table 1
   (spherical, six variables in **radians**, r = π/2 − h) with Table 3 (plane,
   five variables as **lengths**, r ≡ 1). Pooled radian-and-length extrema do not
   describe a region in plane-variable space.

2. **Inconsistency with §7.** §7 fixes all plane confirmatory length thresholds in
   **units of r (r = 1; not radians)**. A radian-pooled completeness region
   contradicts the units in which completeness is certified.

3. **Non-reproducibility** (provenance audit above): a confirmatory region must be
   regenerable from a written rule; this one was not.

4. **Degenerate corner.** The 1e-6 lower bounds placed the box against the
   degenerate corner (b+c+d, c+d+e, d+g → 0), the direct cause of the enumeration
   runaway observed before the correction.

## Replacement

The plane Tier-2 enumeration now runs over **B_plane**, generated deterministically
by `enumeration/generate_B.py` from Rao Table 3 only (plane variables, r ≡ 1) and
emitted to `enumeration/B.json`. See Amendment 03 §C2.

## Confirmatory record

**No confirmatory result was produced using this legacy box.** It appeared only in
exploratory diagnostic runs (provenance audit and corrected-box canary), which are
not part of the confirmatory record. The correction (Amendment 03) precedes the
tooling freeze and the confirmatory campaign in their entirety.
