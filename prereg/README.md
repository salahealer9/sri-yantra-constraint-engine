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
[10.5281/zenodo.20630790](https://doi.org/10.5281/zenodo.20630790)

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

## Verification

Each version: `git tag -v prereg-vX.Y` (signature), `ots verify <file>.ots`
(timestamp). The engine under test is frozen at v0.1.0
([10.5281/zenodo.20617730](https://doi.org/10.5281/zenodo.20617730)).

## Frozen artifacts

- `enumeration/generate_B.py` — deterministic generator of the plane confirmatory
  region from Rao Table 3. Output `enumeration/B.json` (SHA-256 pinned in the
  §B8 tooling-freeze manifest).
- `enumeration/archive/` — superseded box B, retained for provenance only.