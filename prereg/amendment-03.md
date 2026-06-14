# Amendment 03 — Correction of the plane Tier-2 confirmatory region (parameterization coherence)

- **Amends:** Pre-registration *"Complete classification of the well-posed subsets
  of the Rao (1998) Śrīyantra constraint system,"* version DOI
  [10.5281/zenodo.20630790](https://doi.org/10.5281/zenodo.20630790), registered
  2026-06-10.
- **Object amended:** the search region used by the **plane Tier-2 enumeration** —
  i.e. the clause of Amendment 02 §B2(i) that inherits "the axis-aligned box **B**
  already defined in §6" as the plane completeness region. The §6 Tier-1 sampling
  box is **not** redefined (see C3).
- **Author:** Salah-Eddin Gherbi, Independent Researcher,
  [ORCID 0009-0005-4017-1095](https://orcid.org/0009-0005-4017-1095).
- **Filed:** 2026-06-14 — before any well-posed subset outside Rao's published
  tables has been solved under the corrected region, and before the Tier-2 tooling
  freeze (Amendment 02 §B8).
- **Frozen engine under test:** unchanged — Sri Yantra Constraint Engine v0.1.0
  ([10.5281/zenodo.20617730](https://doi.org/10.5281/zenodo.20617730)).
- **Status:** Permanent part of the pre-registration record per §8 of the
  original. GPG-signed and OpenTimestamps-stamped on deposit.

---

## C0. Nature and limits of this amendment

This amendment corrects a **specification defect in one object only**: the search
region against which the **plane Tier-2 enumeration** certifies completeness. It
replaces the pooled box **B** — as inherited by Amendment 02 §B2(i) — with a
parameterization-coherent plane box **B_plane** (C2), generated deterministically
by a committed script (C4).

It is deliberately **surgical**. It does **not** redefine the §6 Tier-1 multistart
sampling box, which remains suitable for its exploratory purpose (C3). It changes
nothing else: not the Tier-1 method, seeds, RNG seed, or convergence floor (§6);
not the Route-3 enumeration method, completeness criterion, invariants, gates, or
freeze protocol of Amendment 02 (§B2(ii)–§B8); not the equivalence metric or τ
sweep (§7); not the scope (§1–§4), Gates 1–4 (§5), or reporting (§9).

The §8 protocol governs and is reaffirmed, including **no retroactive
reclassification**: the change is **prospective only**. The provenance audit and
the corrected-box canary that motivate it were obtained *before* this filing and
are **exploratory** — the recorded basis for the change, not confirmatory results.

## C1. The defect

§6 defines **B** by pooling, per basic variable, the [min, max] across **all rows
of Rao's Tables 1 and 3**. Table 1 is the **spherical** form — six variables in
**radians** (r = π/2 − h); Table 3 is the **plane** form — five variables as
**lengths** under r ≡ 1. These are heterogeneous parameterizations: pooled
per-variable extrema of radian and length values do not describe a box in any
single coordinate space.

For Tier-1 multistart this is harmless — a broad sampling region only feeds
starting points, and Rao's 14 deterministic seeds guarantee the known roots. The
defect becomes **load-bearing only on inheritance**: Amendment 02 §B2(i) adopts
the same box as the **plane completeness region**, against which *"provably no real
in-range solution"* is asserted. There it is also inconsistent with the
pre-registration's own metric — §7 fixes τ and all confirmatory length thresholds
in **units of r (with r = 1; not radians)** — so the radian-pooled completeness
region contradicts the units in which completeness is certified.

The realized literals were additionally **non-reproducible**. Audited against the
engine's hash-pinned tables, b and g equal the pooled maximum (keep-largest) while
c, d, e equal the pooled range with each variable's single largest value removed
(drop-largest); no single rule generates all five. The completeness region was a
set of hand-applied literals, not an algorithm.

## C2. Corrected plane completeness region B_plane

The plane Tier-2 enumeration is conducted over **B_plane**, derived from **Rao
Table 3 only**, in the plane variables (b, c, d, e, g) under r ≡ 1, by the
widen-and-intersect procedure §6 already specifies:

1. per variable, [min, max] across the six plane rows;
2. widen 50 % of the range each side (lo − 0.5 R, hi + 0.5 R), R = max − min;
3. intersect the valid domain — positivity (lower clamp ε = 10⁻⁶) and c, d < r.

Realized bounds (clamps inactive; region interior to the valid domain):

| var | lower | upper |
|-----|-------|-------|
| b | 0.377026 | 0.621870 |
| c | 0.187826 | 0.310006 |
| d | 0.250135 | 0.327555 |
| e | 0.403274 | 0.550907 |
| g | 0.084179 | 0.134327 |

All six Table-3 roots lie inside B_plane by construction. The §6 valid-domain
clause "chain-defined arc arguments in range" is realized operationally as the
admissible-domain exclusion of the separate methodology amendment, applied during
enumeration; B_plane is the axis-aligned bounding region and the admissibility
conditions prune its interior.

**Primary justification.** B_plane is defined in the **same parameterization as the
variables being enumerated**, restoring consistency with the r ≡ 1 plane units of
§7. The resulting tractability of the enumeration is a corroborating consequence,
not the rationale.

## C3. The §6 Tier-1 sampling region is retained, with clarification

The §6 Tier-1 multistart sampling box is **unchanged**. The following clarification
is added to the record:

> The pooled box of §6 remains suitable as the **exploratory multistart sampling**
> region (a deliberately broad region of starting points, with Rao's tabulated
> solutions as deterministic seeds). It is **not** used as the confirmatory
> completeness region for the plane form, because it pools heterogeneous
> parameterizations (spherical radians with plane lengths); plane completeness is
> certified over **B_plane** (C2) instead.

**Nesting (recorded property).** B_plane is a strict sub-region of the §6 pooled
box in every coordinate. The plane completeness region is therefore a coherent
**subset nested inside** the broader exploratory sampling region — a narrowing, not
a relocation.

**Cross-check scope.** The §6 cross-check (every Tier-1 solution appears among the
certified Tier-2 solutions) applies **within B_plane**. A Tier-1 plane positive
that lies in the pooled box but **outside B_plane** is reported as *"solution
found, outside the confirmatory region B_plane,"* not as a cross-check failure;
should any such positive arise, it is recorded and may motivate a prospective
widening under §8, but it does not bear on completeness certified within B_plane.

*(Scope note: this amendment concerns the plane confirmatory region only. The
spherical Tier-2 of §6 remains secondary / best-effort; were it ever pursued as
confirmatory, it would require its own coherent region derived from Table 1 in
spherical coordinates, under this same principle — a matter for a future
amendment, out of scope here.)*

## C4. Determinism and provenance

B_plane is produced by `enumeration/generate_B.py` from the engine's hash-pinned
Table 3, emitting `enumeration/B.json`. The script applies the C2 rule verbatim,
logs any clamp activation (none for Table-3 data), and asserts containment of all
six Table-3 roots. Same input → same B, recomputable by any auditor. The SHA-256
of `B.json` is recorded in the Amendment 02 §B8 tooling-freeze manifest and the
script is hash-pinned alongside the enumerator.

## C5. Re-pointing within Amendment 02

Amendment 02 §B2(i) — "the axis-aligned box **B** already defined in §6" — now
reads **B_plane as defined in C2**. The enumeration method, completeness criterion,
recorded invariants, gate interaction, pre-run validation (Gate M), and tooling
freeze (§B2(ii)–§B8) are otherwise unchanged.

## C6. Archival of the superseded region

The superseded hand-derived box is **retained, not deleted**:

```
enumeration/archive/
    box_B_legacy.json   # original literals + machine-readable supersession note
    box_B_legacy.md     # provenance audit + supersession rationale
```

`box_B_legacy.md` records the original literals, the provenance audit (the
keep-largest / drop-largest inconsistency), the supersession rationale, and the
statement that **no confirmatory result was produced using the legacy box**.
Provenance is preserved and no history is rewritten.

## C7. Deposit and relationship to the methodology amendment

Permanent part of the record per §8, GPG-signed and OpenTimestamps-stamped on
deposit, filed before the Amendment 02 §B8 tooling freeze and before any
confirmatory run over B_plane. Prospective only.

The **enumeration-methodology extension** — the explicit admissible-domain /
coordinate-range exclusion and the division-free handling of blow-up seams that
realize the §6 "arc arguments in range" condition during enumeration — is filed
**separately** as Amendment 04, so that the correction of the search region and
the extension of the enumeration method remain independently auditable.
