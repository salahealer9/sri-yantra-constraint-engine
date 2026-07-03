# k-escalation pre-registration (TO BE COMMITTED BEFORE THE k=12 RUN)

Pre-registered 2026-07-03, before running k=12. This note fixes the stopping rule, the radii policy,
and the yield definition IN ADVANCE, so "exhaustion" is a pre-stated criterion and not fatigue, and
so a provenance shift between budgets is not later misread as non-determinism.

## Objective
Turn the presence census's budget from a single point (k=6) into a CURVE by escalating the
domain-wide multistart budget on the still-unreached population, measuring new certified yield per
doubling until a pre-stated stop.

## Population (restriction)
Escalate ONLY on the UNRESOLVED_NO_CANDIDATE subsets of the current checkpoint
(CENSUS_CHECKPOINT_LAYER1_R2): 2130 subsets. These have ZERO main-file candidates at k=6 by
definition, so at higher k every main-file candidate is genuinely NEW yield (no overlap to subtract).
The 876 already-certified and 38 CERT_FAILED are NOT re-run (--restrict-class UNRESOLVED_NO_CANDIDATE).

## Nested-seed property (why escalation is a clean diff, not a re-run)
k=12 seed sets CONTAIN k=6 seed sets. Verified: a k=6 and a k=12 run reach the identical root to
2.76e-15 (floating-point identity of centers, <= ~1e-14), differing only in first-finder provenance
(seed/stratum/altitude) because a different Newton path found it first. STATED FOR THE RECORD:
  - k=12 root sets contain k=6 root sets up to floating-point identity of centers (<= ~1e-14).
  - First-finder provenance (seed, stratum, altitude) may LEGITIMATELY differ between budgets.
  - For the 2130 (zero k=6 main-file candidates by definition), every k=12 main-file candidate is
    new yield regardless of provenance.
A provenance shift between budgets is NOT non-determinism; each budget is itself deterministic
(blake2b per-subset seeding).

## Radii policy (registered; certifier engine UNCHANGED)
From 2026-07-03, Layer-1 certification passes use the REGISTERED EXTENDED-RADII LIST
    [3e-3, 1e-3, 3e-4, 1e-4, 3e-5, 1e-5, 3e-6, 1e-6, 3e-7, 1e-7]
passed EXPLICITLY to the certifier (NOT by editing certify_2b_general.DEFAULT_RADII). The certifier
engine is unchanged (hash de64edfa4979); radius_used is recorded per certified root. Justification:
R2 proved the old 1e-5 floor left 40 certifiable roots behind (AA-overestimation at large boxes).
Using the extended list from the START of k=12 avoids leaving the same class for a later R-pass.

## Guards that MUST ride along at every k (or contamination returns)
Higher k explores more of the domain and proposes MORE out-of-domain and high-cond candidates, so:
  - h-domain enforcement (h in (1e-8, pi/2)) active in-generator + filter_altitude_domain
    (belt-and-suspenders; current generator should yield zero removals).
  - cond filter COND_MAX=1e8, high-cond -> sidecar (NOT census input).
  - registered extended radii at certification.
  - deterministic per-subset seeding (blake2b), parent-only writes.

## STOPPING RULE (pre-stated; the editorial choice made BEFORE the run)
Escalate k: 6 -> 12 -> 24 on the remaining NO_CANDIDATE population. STOP when EITHER:
  (a) a doubling produces fewer than N = 25 NEW CERTIFIED SUBSETS, OR
  (b) runtime or candidate volume exceeds the declared budget (a run must fit the ~2.5-3h
      pre-reboot window at 4 workers; ~2130 x 912 seeds ~ 1.94M Newtons at k=12 is comparable to
      the k=6 full run, so k=12 fits; k=24 doubles again -> shard or split if it would overrun).
N = 25 chosen before running (editorial: below ~25 new certified per doubling, the marginal subset
is not worth the compute doubling; the curve has flattened). Report the full curve regardless of
where it stops (k, new-certified, cumulative-certified, runtime).
FORWARD NOTE: if k=12 produces R3, then k=24 restricts against R3's remaining UNRESOLVED_NO_CANDIDATE,
NOT R2's. Each escalation restricts against the LATEST checkpoint's unreached population, so no
already-certified subset is ever re-run and every doubling's yield is measured against the current
frontier.

## Yield definition (what counts as "new certified")
A subset counts as newly certified at k iff it was UNRESOLVED_NO_CANDIDATE at the prior checkpoint
AND acquires >=1 certified root (certify_2b_general, registered radii) at this k. Certified DISTINCT
roots via collapse_certified. Gate-4 tagged per-root as metadata (never a filter, never a relabel).

## Merge / provenance
k=12 results -> scratch census (registered radii) -> upgrade-only merge onto R2 -> CHECKPOINT ...R3
(own checkpoint, NOT an edit to R2). Every prior label preserved or upgraded. LAYER1 and R2 remain
valid tagged baselines; R3 supersedes in coverage, not in validity. candidate_source=layer1_k12;
radius_used per root; k recorded per subset.

## What is NOT claimed by escalation
- Escalation raises the presence LOWER BOUND; it never certifies absence. Subsets still unreached
  after the k-curve remain UNRESOLVED_NO_CANDIDATE ("no in-domain candidate under tested budget"),
  NEVER "infeasible" / "absent".
- The paper does not depend on this: the R2 result (876/956/523-433/77/38/2130) already stands as a
  complete two-layer presence census. Escalation strengthens coverage; it is not load-bearing.

## Opening command (mechanical, after this note is committed)
    python3 enumeration/layer1_candidates.py --k 12 --workers 4 \
        --restrict-census docs/census_checkpoint_layer1_r2/spherical_roots.jsonl \
        --restrict-class UNRESOLVED_NO_CANDIDATE \
        --out docs/candidates_layer1_k12.jsonl
    # then: filter_altitude_domain (expect 0 removals) -> diagnostics -> scratch (registered radii)
    #       -> upgrade-only merge -> R3. Compare new-certified against N=25 to decide k=24.
