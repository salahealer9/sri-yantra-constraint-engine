# Section 9 — Reproducibility (draft)

The census is designed so that every reported figure can be regenerated from committed source. This
section states what "reproducible" means here and what the released bundle contains.

## 9.1 Determinism

Candidate discovery is fully deterministic. Each subset's seeds are derived from a single fixed global
seed by a per-subset hash, so the multistart search draws the same seeds on every run, independent of
worker count or scheduling. The parallel and serial implementations were checked to produce
byte-identical candidate files. Consequently the main candidate files, and through the frozen
certifier the census records, regenerate byte-identically from the committed source and the recorded
global seed under the recorded software environment; the intermediate candidate files themselves need
not be stored.

## 9.2 The frozen engine and explicit policies

All certifications use one constraint engine, identified by the fixed SHA-256
de64edfa4979905830452ab7b9a423a73006ed20dbae67cd56ac29110b161667 and unchanged across every tier and
checkpoint. Where the certification behaviour is parameterised -- the interval-radius list
and the conditioning cutoff -- the parameters are passed to the engine EXPLICITLY and recorded, rather
than being baked into the engine by modification. In particular the extended radius list is a declared
pipeline parameter, not an engine edit, and each certified root records the radius at which it
certified. This keeps the engine a stable reference object while making every policy that affects the
results inspectable.

## 9.3 The registered decisions

Four decisions are REGISTERED -- fixed in advance and recorded -- rather than tuned to the outcome:
the subset universe (the 3044 well-posed subsets), the altitude domain (h in (0, pi/2)), the
interval-radius list, and the escalation stopping rule (halt when a budget doubling yields fewer than
twenty-five new certifications). The stopping rule in particular was committed to the repository before
the escalation run that it governs, so its termination is a pre-stated criterion rather than a
post-hoc judgement.

## 9.4 The released bundle and checkpoint lineage

The census is released as a hashed checkpoint bundle: the per-root records, a tabular summary, a
manifest, and a checksum file covering every file in the bundle. The final checkpoint and its
predecessors are marked by frozen checkpoint labels and, where applicable, signed annotated tags,
forming a lineage in which each checkpoint supersedes the previous in COVERAGE while remaining a valid
frozen baseline:

    tag / label                            certified subsets    tier
    ------------------------------------------------------------------------
    spherical-census-layer1-v1.0                  836           domain-wide generator, k=6
    spherical-census-layer1-v1.1                  876           + extended-radius re-certification
    spherical-census-layer1-v1.2 (current)        888           + pre-registered k=12 escalation

with an additional freeze marker (paper-freeze-1) at the documented final state. Each reported figure
derives from the current (v1.2) bundle; the earlier tags allow the intermediate states to be
reconstructed exactly. The auditable sidecar populations (near-singular candidates and
super-hemispheric roots, Section 7) are retained alongside the bundle as evidence, clearly marked as
NOT census input.

## 9.5 Byte-level provenance

The released checkpoint bundle is byte-reproducible: manifests carry no timestamps, and a single
checksum file covers the bundle, so a rebuild from committed source reproduces the same hashes. Individual root
records additionally carry their own evidence -- the certifying box, the residual, the radius used,
the conditioning, and the engine hash -- so any single certification can be re-checked in isolation
without rerunning the census.

## 9.6 Source material

The primary source for the constraint system and the geometric-validity conditions is Rao (1998),
cited by page and equation. The paper itself is not redistributed with the census; where its content
is used, it is referenced, and the specific copy consulted is identified by hash for provenance rather
than reproduced.

---
## Notes (author; delete before submission)
- 9.1: deterministic blake2b per-subset seeding; serial/parallel byte-identical (gate). GLOBAL_SEED
  recorded. State the exact seed value in the repo, not necessarily the paper.
- 9.2: full engine SHA-256 now in main text (de64edfa4979...b161667). radii list + COND_MAX=1e8.
- 9.3: universe 3044; domain (0,pi/2); radii; N<25 rule committed BEFORE the k=12 run
  (k-escalation-preregistration.md, committed pre-run). This is the reproducibility-relevant framing
  of the pre-registration.
- 9.4: tag strings named in-text. CONFIRM which are GPG-signed annotated vs plain labels before
  final (v1.0/v1.1/v1.2 signed per session; paper-freeze-1 -- confirm signed or plain). Lineage
  totals match Section 5 Table 2.
- 9.5: SHA256SUMS regenerated self-exclusion-safe (find ... ! -name SHA256SUMS). Per-root evidence
  fields from the census schema.
- 9.6: Rao PDF NOT committed to public repo (copyright); citation + page/eq refs + PDF SHA-256
  (0edae877...) for provenance only. Consistent with the gate4-vs-source finding's copyright note.
- FEEDS FROM: CURRENT_CHECKPOINT.md, checkpoint SHA256SUMS, tag lineage, k-escalation-preregistration.md,
  gate4-vs-source-finding.md (copyright note).
