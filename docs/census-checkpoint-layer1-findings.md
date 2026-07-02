# CENSUS_CHECKPOINT_LAYER1 — first complete two-layer census of the spherical Sri Yantra constraint universe

## Headline (presence-first lower bounds; certify_2b_general decides; Gate-4 metadata, per-root)
    FEASIBLE_CERTIFIED subsets    836     (from 26 at session start)
    UNRESOLVED_CERT_FAILED         78
    UNRESOLVED_NO_CANDIDATE      2130     (836+78+2130 = 3044)
    certified DISTINCT roots      916     (disjoint-box collapse)
    Gate-4 per-ROOT               503 valid / 413 rejected   (= 916)
    Gate-4 per-SUBSET             478 valid-bearing / 358 only-rejected / 26 both
    multi-root subsets (lb>1)      77
Lower bounds: unreached subsets stay UNRESOLVED_NO_CANDIDATE (never fabricated absence).

## Merge integrity (invariants ASSERTED, not eyeballed)
Union of CENSUS_CHECKPOINT_TRANSFER_P0_P3 (26) + domain-clean layer1, upgrade-only lattice:
  - no downgrade; no layer1 loss; all roots gate4-tagged; all h in (0, pi/2).
  - 26/26 multi-source agreement: layer1 independently re-found EVERY baseline root (no shared seeds).
  - gate4 backfilled onto the 26 baseline roots -> gate4_status.json is now a DERIVED view, not a
    parallel authority. Backfilled tags byte-identical to the scratch's (503/413), cross-checking the
    22V/4X union split against layer1's re-finds months apart by a different code path.
  - root reconciliation: 26 baseline + 890 layer1-only = 916 (an earlier 918 prediction double-counted
    the overlap; the merge replaces the 26 re-found roots with baseline evidence bundles and unions the
    rest). Verified: sum of num_certified_roots across FEASIBLE = 916.
  - negative test: the merge driver HALTs on the h=-4.056 contamination root (invariant catches
    out-of-domain even if upstream missed it).

## Concrete anchors for the write-up
- PER-ROOT VALIDITY, demonstrated: the 2 overlap subsets that gained a second root are (1,2,3,4,6,13)
  and (1,2,3,8,10,14). (1,2,3,4,6,13) was one of the ORIGINAL FOUR Gate-4-REJECTED subsets (warm-start
  era); layer1 found a SECOND root there that is Gate-4-VALID. A subset previously known only as
  "Rao-invalid" admits a valid Rao figure at a different root -> under subset-level tagging this was
  unrepresentable. This is the per-root-validity decision paying off concretely.
- viol stratum justified universe-wide: 119 viol-only certified roots (78 rejected, 41 valid) that a
  Gate-4-filtered generator would structurally miss.
- Two-layer geography: ~55% of roots Gate-4-valid; invalid family substantial (413) and benchmark-
  densest but not benchmark-confined.

## The one two-source-resistant subset, precisely characterized
(1,2,6,10,16,19): baseline UNRESOLVED_CERT_FAILED, preserved under the lattice. NOT near-singular and
NOT a pseudo-root -- it is a GENUINE root (resid 5.9e-16, polish displacement 5.5e-13, chain-domain
guard clean, cond(J)=1.77e4, one candidate in the MAIN file). Refused only by Krawczyk UNIQUENESS
verification (kraw: split) at all DEFAULT radii >= 1e-5, from two independent candidate sources
(warm-start baseline + layer1). PROBE: certifies CERTIFIED_UNIQUE_GEOMETRIC at radii 3e-6 / 3e-7 /
3e-8 (cond identical across all verdicts -> the root is unchanged; only the certification box changed).
MECHANISM: affine-arithmetic overestimation of the Jacobian range at the 1e-5 default floor drowns
the certificate; below that floor Krawczyk verifies uniqueness. This is a route-specific negative
(certificate at tested radii), NOT a statement the root is uncertifiable.

## Preserved populations (each auditable, none discarded)
- 78 UNRESOLVED_CERT_FAILED: candidates proposed, certifier refused. At least (1,2,6,10,16,19) is a
  genuine root refused by AA-overestimation at default radii -> extended-radii tier likely converts a
  chunk (see Next). Others may overlap the near-singular population.
- 7,960 high-cond candidates (COND_MAX=1e8 sidecar): near-singular numerical candidates, auditable,
  NOT census input. A study of degenerate strata for later.
- 972 super-hemispheric candidates (h <= 0, r > pi/2): real constraint-roots of Rao's trig system
  outside the registered Meru domain. One-sentence remark / future registered extension.

## Methods lesson (worth writing up): the h-domain incident
The v1/v2 generator bounded h above (r >= 5e-3) but not below zero; Newton (h free) reached
super-hemispheric roots. Caught by a SINGLE impossible number -- displacement 32.293, geometrically
impossible for two in-domain points (max ~sqrt(6)*pi/2 ~ 3.9). Registered-positivity enforcement
(h >= 1e-8) in generator (v3) + filter + write-path check 6 closed it; domain-clean displacement max
is 2.33. The audit trail from "displacement 32.293" to the fix is the kind of provenance that makes
a census trustworthy: no silently-wrong number survived contact with a diagnostic.

## Next tier (tomorrow; must NOT touch this checkpoint)
recertify_extended_radii.py: read-only re-certification of all 78 CERT_FAILED candidates under an
extended radii list (below the 1e-5 floor). Decision data first: conversion count + radius_used
histogram (does AA-overestimation explain many, or was (1,2,6,10,16,19) special?). If yield justifies:
extended-radii scratch census + upgrade-only merge -> CHECKPOINT_LAYER1_R2 with the extended radii
list registered in provenance. Extending radii DOWNWARD is strictly conservative (certifier returns on
first 'unique'; existing certifications untouched; refusals can only convert). No hand-edits to
LAYER1 under any outcome.
Also open: k>6 budget escalation on the 2130 no-candidate subsets before any earns a stronger label.

## Files
    merge_census_layer1.py, docs/census_checkpoint_layer1/{jsonl,csv,manifest,SHA256SUMS,log}
    (generators/diagnostics/filters committed earlier this session; candidate + scratch files
     gitignored, deterministic from committed source + GLOBAL_SEED)

SHA-256 hashes for all files in this unit are recorded in `docs/SHA256SUMS`