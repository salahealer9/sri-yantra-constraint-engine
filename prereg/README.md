# Pre-registration record

Pre-registration for the complete classification of the well-posed subsets of the
Rao (1998) Śrīyantra constraint system. This directory is the authoritative record;
each version is a Zenodo deposit, GPG-signed and OpenTimestamps-stamped, and a
signed git tag. Amendments are prospective only and predate any confirmatory run.

## Version history

| Version | Date | File(s) | Git tag | DOI |
|---------|------|---------|---------|-----|
| prereg-v1.0 | 2026-06-10 | `preregistration.md` | `prereg-v1.0` | [10.5281/zenodo.20630790](https://doi.org/10.5281/zenodo.20630790) |
| prereg-v1.1 | 2026-06-12 | `amendment-01.md` | `prereg-v1.1` | [10.5281/zenodo.20672072](https://doi.org/10.5281/zenodo.20672072) |
| prereg-v1.2 | 2026-06-13 | `amendment-02.md` | `prereg-v1.2` | [10.5281/zenodo.20677502](https://doi.org/10.5281/zenodo.20677502) |
| prereg-v1.3 | 2026-06-14 | `amendment-03.md` | `prereg-v1.3` | [10.5281/zenodo.20692921](https://doi.org/10.5281/zenodo.20692921) |
| prereg-v1.4 | 2026-06-14 | `amendment-04.md` | `prereg-v1.4` | [10.5281/zenodo.20693741](https://doi.org/10.5281/zenodo.20693741) |

The Zenodo **concept DOI** (resolves to the latest version):
[10.5281/zenodo.20617729](https://doi.org/10.5281/zenodo.20617729)

## Amendment summaries

- **Amendment 01** (superseded) — plane Tier-2 via coefficient-parameter homotopy.
  Withdrawn: found infeasible (BKK mixed-volume / symbolic-collapse obstruction).
- **Amendment 02** (active) — plane Tier-2 via certified real-box enumeration
  (affine-arithmetic AA-Krawczyk interval-Newton). Supersedes Amendment 01 in full.
- **Amendment 03** (active) — corrects the plane Tier-2 confirmatory region to
  `B_plane` (deterministic, plane-only; `generate_B.py` → `B.json`). Surgical;
  retains the §6 Tier-1 sampling box. Re-points Amendment 02 §B2(i).
- **Amendment 04** (active) — admissible-domain exclusion realizing §6 "arc
  arguments in range"; completeness-enabling, §B3-safeguarded; registers the
  validated exclusion set + x11a division-free rule. RMAX=2, MAX_DEPTH=200.

## Tier-2 tooling freeze (§B8)

The plane Tier-2 confirmatory tooling was frozen on **2026-06-15** (10:46:18 UTC),
at commit `f0581fe` on `tier2-dev`, **before** the official Gate M (§B7) and the
confirmatory campaign. The freeze hash-pins the exact tree those runs execute
against; results carrying confirmatory status are produced only on this tree.

- **Manifest:** `prereg/tier2-freeze.sha256` — SHA-256 of every frozen file plus
  the recording environment and parameters; GPG-signed (`.asc`) and
  OpenTimestamps-stamped (`.ots`).
- **Environment (campaign host):** Python 3.11.2 (Linux x86_64, glibc 2.36);
  numpy 2.4.4, scipy 1.17.1, mpmath 1.3.0.
- **Frozen parameters:** `R_CERT=0.003  MAX_DEPTH=200  RMAX=2.0  MAX_BOXES=3000000
  TLIM=1800.0  GATE2_TOL=1e-9  DEDUP_TOL=0.006  BISECTION=widest-coordinate
  POLISH=True`.
- **Frozen tree (8 files):** `enumeration/{generate_B.py, B.json, campaign.py,
  admissibility.py, aar.py, plane_chain.py, gate_m.py}` and `sriyantra_plane.py`
  (engine under test, v0.1.0).
- **Reproducibility anchor:** `enumeration/B.json`, sha256
  `3de3e0db9a3052385607b520c5778c8269532219c2654721a63fd06c1ab9365c` — verified
  byte-identical across two independent machines; regenerable by
  `python3 enumeration/generate_B.py`.

Verify the frozen tree against the signed manifest, from the repo root:

    grep -v '^#' prereg/tier2-freeze.sha256 | sha256sum -c -    # every file -> OK
    gpg --verify prereg/tier2-freeze.sha256.asc                 # signature
    ots  verify  prereg/tier2-freeze.sha256.ots                 # timestamp

## Verification

Each version: `git tag -v prereg-vX.Y` (signature), `ots verify <file>.ots`
(timestamp). The tooling freeze: `git tag -v tier2-freeze` and the manifest
verification above. The engine under test is frozen at v0.1.0
([10.5281/zenodo.20617730](https://doi.org/10.5281/zenodo.20617730)).

## Frozen artifacts

- **`prereg/tier2-freeze.sha256`** — §B8 tooling-freeze manifest (signed +
  timestamped); pins the 8-file confirmatory tree, environment, and parameters.
- `enumeration/generate_B.py` → `enumeration/B.json` — deterministic generator of
  the plane confirmatory region `B_plane` from Rao Table 3.
- `enumeration/{campaign.py, admissibility.py, aar.py, plane_chain.py, gate_m.py}`
  — the confirmatory enumerator, admissibility exclusion (Amendment 04), rigorous
  affine arithmetic, validated F1–F20 chain, and Gate M harness.
- `sriyantra_plane.py` — engine under test, frozen at v0.1.0.
- `enumeration/make_freeze.py` — regenerates the freeze manifest deterministically.
- `enumeration/archive/` — superseded box B, retained for provenance only.
