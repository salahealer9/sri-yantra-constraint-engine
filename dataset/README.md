# Certified enumeration of C. S. Rao's plane Śrī Yantra constraint system

**A 134 / 681 feasibility partition realizing 128 distinct admissible figures, within B_plane**

This dataset is the confirmatory computational record for the *plane* form of the
Śrī Yantra geometry as formalized by C. S. Rao (1998, *Indian Journal of History of
Science* 33(3), 203–227). It deposits, as a fixed and independently verifiable
research object, the certified enumeration of every well-posed plane constraint
subset over a registered parameter region, an independent cross-check of that
enumeration, and the distinct-figure analysis derived from it.

Every quantitative claim in this dataset is scoped to **the plane form** and to the
**registered axis-aligned region B_plane**; it is not a statement about the full
spherical system or about all of parameter space. That scope is stated with each
result below and should be preserved in any citation.

## Headline results

1. **Certified classification (computational result).** Within B_plane, the 815
   well-posed plane constraint subsets partition into **134 feasible** and **681
   infeasible** subsets, with zero unresolved boxes and zero Tier-1 downgrades.
   Each feasible subset admits **exactly one** certified real figure in B_plane.
   The 681 infeasible verdicts are *certified absences* — machine-checked proofs
   that no real admissible figure exists in B_plane for those subsets — not failed
   searches.

2. **Distinct geometric figures (geometric result).** The 134 feasible subsets
   realize **128 distinct admissible plane figures**. The gap of six is exactly
   accounted for by the algebraic identity **F8 − F9 + F16 ≡ 0** (one of the two
   exact linear dependencies in the rank-4 radial matroid of the 20 constraints):
   three figures are so over-determined that they satisfy a sixth constraint
   automatically, each appearing three times in the five-subset census
   (`{1,2,X,8,9,16}` for X ∈ {3, 6, 20}). The count is verified two independent
   ways — under the §7 figure metric and directly in parameter space — and the
   three collapses agree to 10⁻¹² – 10⁻¹⁵.

These are different objects and are kept distinct throughout: **134 feasible
constraint subsets realize 128 distinct admissible plane figures within B_plane.**

The dependency lattice predicted the rank-deficiency *analytically*; the same
structure reappears *geometrically* in the certified figures and again in the raw
*parameters*. That algebra → computation → geometry triangulation is the deepest
finding here.

## Method (summary)

A registered two-tier design (pre-registration in `prereg/`):

- **Tier 2 (confirmatory).** Certified real-box enumeration of each subset over
  B_plane by branch-and-prune: rigorous outward-rounded affine arithmetic for
  exclusion, and an affine-arithmetic Krawczyk interval-Newton test that certifies a
  unique real root in a box or certifies its absence. A subset is
  completeness-bearing only if the queue is exhausted within a frozen budget with no
  box left unresolved. The confirmatory toolchain is hash-pinned, GPG-signed and
  OpenTimestamps-stamped (`prereg/tier2-freeze.sha256{,.asc,.ots}`, tag
  `tier2-freeze-2`), and validated by **Gate M** before use.

- **Tier 1 (independent cross-check).** Multistart Newton over B_plane,
  reproducing the certified partition and flagging any disagreement. It reproduced
  134 / 681 with zero contradictions — and, in the original run, it is what detected
  a boundary over-certification (see Erratum 01), which was diagnosed, corrected at
  the tool level, re-frozen, and re-run. The protocol detecting and correcting its
  own implementation error is itself part of the result.

- **§7 distinct-figure analysis.** The certified solutions are mapped to labeled
  figure coordinates in a normalized frame (r = 1, centre origin, axis = y, no
  alignment) and counted distinct under a max-point metric across a τ sweep; an
  independent parameter-space verification removes any dependence on the figure
  construction.

## Contents

```
README.md                     this file
CITATION.cff                  how to cite this dataset
LICENSE
PROVENANCE.md                 commit hashes, tags, DOIs, signatures, verification steps
SHA256SUMS.txt                checksums of every file below (GPG-signed separately)

sriyantra_plane.py            the engine under test (v0.1.0; corrected per the corrigendum)

prereg/
    preregistration.md        registered design (prereg v1.0)
    amendment-0{1..4}.md       registered amendments (homotopy; Route-3 method;
                               box correction; admissibility exclusion)
    erratum-tier2-01.md        certification-geometry conformance (isotropic cube -> box X)
    tier2-freeze.sha256        frozen-tool manifest (tag tier2-freeze-2)
    tier2-freeze.sha256.asc    detached GPG signature of the manifest
    tier2-freeze.sha256.ots    OpenTimestamps stamp of the manifest

enumeration/
    B.json, generate_B.py      registered region B_plane and its deterministic generator
    campaign.py                confirmatory enumerator (frozen)
    admissibility.py           registered domain exclusion (frozen)
    aar.py                     rigorous affine arithmetic + forward-mode AD (frozen)
    aa_krawczyk.py             AA-Krawczyk certification kernel
    plane_chain.py             polymorphic F1..F20 AA chain (frozen)
    gate_m.py                  validation gate (frozen)
    make_freeze.py             deterministic freeze-manifest generator
    tier1_crosscheck.py        Tier-1 multistart cross-check (validation)
    figure_coords.py           §7 figure coordinate constructor (validation)
    distinct_figures.py        §7 distinct-figure count (validation)
    verify_param_collapse.py   parameter-space verification of the count (validation)
    campaign_results/          results.csv, roots.jsonl, campaign.log  (the census)
    crosscheck_results/        crosscheck.csv
    figure_results/            distinct_figures.csv, param_collapse_verification.txt
    legacy_campaign_v1/        superseded first census + note (boundary-leak provenance)
```

## How to verify

1. **Checksums:** `sha256sum -c SHA256SUMS.txt` (every line OK).
2. **Manifest signature:** `gpg --verify prereg/tier2-freeze.sha256.asc prereg/tier2-freeze.sha256`,
   and `ots verify prereg/tier2-freeze.sha256.ots` for the independent timestamp.
3. **Frozen tree integrity:** `sha256sum -c prereg/tier2-freeze.sha256` reproduces
   the eight hash-pinned confirmatory artifacts.
4. **Re-derive the results:** run `enumeration/gate_m.py` (must PASS), then
   `enumeration/campaign.py 0 815` (→ 134 / 681, 0 unresolved), then
   `enumeration/tier1_crosscheck.py` (→ full agreement), then
   `enumeration/distinct_figures.py` and `enumeration/verify_param_collapse.py`
   (→ 128 distinct, three identical-parameter classes). See PROVENANCE.md for exact
   commit hashes and expected outputs.

## Scope and caveats

- All results are for the **plane** form and **within B_plane**. The spherical
  Tier-2 enumeration is deferred. Feasibility/infeasibility statements are claims
  about B_plane, not about all of parameter space.
- The §7 figure constructor (`figure_coords.py`) emits 27 of the 30 labeled points
  (points 14, 15 and base point P5 omitted); each emitted point is validated to
  ~10⁻¹⁶ against the engine chain. The metric over this subset is a rigorous lower
  bound on the full 30-point metric, so the distinct count of 128 is exact (the
  identical-figure collapses occur at machine epsilon and are confirmed
  independently in parameter space).
- This dataset depends on the corrected engine. The transcription errata in Rao
  (1998) that the engine fixes are the subject of a separate corrigendum (submitted
  to IJHS); this dataset builds on the corrected engine and should be read alongside
  it.

## Related objects

- **This dataset:** Zenodo `10.5281/zenodo.20708336` (concept: `10.5281/zenodo.20708335`).
- **Engine software** (v0.1.0): Zenodo `10.5281/zenodo.20617730`.
- **Pre-registration lineage:** Zenodo `10.5281/zenodo.20630790` (v1.0) and the
  amendment depositions listed in PROVENANCE.md.
- **Corrigendum** to Rao (1998): submitted, IJHS (manuscript IJHS-D-26-00161).

## License & citation

Code under the repository LICENSE; data (CSV/JSONL/manifests) released for reuse with
attribution. Cite via `CITATION.cff`. Author: Salah-Eddin Gherbi
(ORCID 0009-0005-4017-1095).
