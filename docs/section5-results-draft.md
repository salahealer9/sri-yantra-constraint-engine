# Section 5 — Results (draft)

## 5.1 Final census standing

The census terminates at checkpoint CENSUS_CHECKPOINT_LAYER1_K12. Of the 3044 well-posed
six-constraint subsets in the registered universe, 888 are certified-feasible, carrying 968 roots
certified under Krawczyk interval validation. The remaining subsets are partitioned into 50
certification refusals (candidates proposed, certification declined, each with a recorded failure
mechanism) and 2106 subsets for which no certifier-bound candidate was found under the tested
generator budgets. No subset is certified infeasible.

    Table 1. Final census standing (CENSUS_CHECKPOINT_LAYER1_K12, universe = 3044).
    ------------------------------------------------------------------------
    status                          subsets    note
    ------------------------------------------------------------------------
    FEASIBLE_CERTIFIED                  888     >= 1 Krawczyk-certified root
    UNRESOLVED_CERT_FAILED               50     candidate(s) proposed, not certified
    UNRESOLVED_NO_CANDIDATE            2106     no certifier-bound in-domain candidate
    INFEASIBLE_CERTIFIED                  0     (no absence claimed; see Section 8)
    ------------------------------------------------------------------------
    total                              3044
    certified distinct roots            968     (disjoint-box collapse)
    ------------------------------------------------------------------------

## 5.2 The discovery-budget curve

Certification proceeded in tiers of increasing candidate-search budget. Warm-start transfer from
known roots exhausted quickly; a domain-wide neutral generator produced the bulk of the census; an
extended-radii re-certification pass (R2) recovered roots left uncertified by the default
interval-radius floor; and a pre-registered budget escalation (k=6 -> k=12) added a final increment
before terminating by rule. Because the k=12 seed set contains the k=6 set, and the escalation targets
only the previously unreached subsets, each tier's new-certified count is genuine incremental yield.

    Table 2. Discovery-budget curve. Each row's "new certified" is incremental over the prior row.
    --------------------------------------------------------------------------------
    tier                    new certified    cumulative    note
    --------------------------------------------------------------------------------
    warm-start (p0..p3)            26             26        transfer from known roots
    Layer-1 generator (k=6)      +810            836        domain-wide neutral multistart
    R2 (extended radii)           +40            876        recovered AA-overestimation refusals
    k=12 escalation               +12            888        pre-registered; then N<25 stop fires
    --------------------------------------------------------------------------------
    k=24                          not run                   terminated by stopping rule (12 < N=25)

The escalation stopping rule (stop when a budget doubling yields fewer than N=25 new certified
subsets) was fixed and committed before the k=12 run. At k=12 the increment was 12 < 25, so the rule
terminated escalation; k=24 was not run. The census budget is therefore a curve with a pre-stated
endpoint rather than an open-ended search.

## 5.3 Provenance and reproducibility

All certifications use a single frozen constraint engine (engine hash de64edfa4979; full SHA-256 in
Section 9), unchanged
throughout; the extended interval-radius list is passed explicitly as a pipeline parameter rather
than by modifying the engine, and each certified root records the radius at which it certified.
Candidate generation is deterministic under a fixed global seed (per-subset blake2b seeding), so the
full candidate set regenerates byte-identically from committed source. The checkpoint is released as
a hashed bundle under a signed tag (spherical-census-layer1-v1.2); all reported figures derive from
that bundle (see Section 9).

---
## Notes (author; delete before submission)
- Table 1 numbers: verbatim from CURRENT_CHECKPOINT.md. Arithmetic: 888+50+2106=3044; roots 968.
- Table 2 "new certified" reconciles: 26 -> 836 (+810) -> 876 (+40) -> 888 (+12). Verified on server:
  warm-start preserved in LAYER1 = 26; LAYER1-new (not in warm-start) = 810. So 836 = 26 preserved +
  810 new is a genuine decomposition, not merely 836-26 by construction.
- Section 5.2 deliberately summarizes the h-domain audit in one clause ("in-domain") and defers the
  full incident to the appendix, per the skeleton.
- engine hash de64edfa4979 is the 12-char short hash used in evidence records; give the full 64-char
  SHA-256 in Section 9 / reproducibility bundle.
