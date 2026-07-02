# First complete Layer-1 census of the spherical Sri Yantra constraint universe

## Registered domain enforcement
Basic variable h is registered positive (Meru domain, r = pi/2 - h in (0, pi/2)). The generator
enforces h in (COORD_FLOOR, pi/2) with COORD_FLOOR=1e-8 and r >= 5e-3; filter_altitude_domain.py
enforces the same on any banked candidate file (keep h >= 1e-8), routing out-of-domain
constraint-roots to a *_removed_outofdomain.jsonl audit sidecar (super-hemispheric caps r > pi/2 --
real solutions of the trig system, out of registered scope). in_bsphere cross-tab on removed
candidates: all 'out' -- the certifier's own B_SPHERE box independently agrees they are out-of-domain.
Domain-clean displacement max is 2.33 (< the ~3.9 in-domain geometric bound sqrt(6)*pi/2).

## Headline (DOMAIN-CLEAN; presence-first lower bounds; certify_2b_general decides; Gate-4 metadata)
                                  checkpoint (transfer p0/p3)   Layer-1 full (clean)
    FEASIBLE_CERTIFIED subsets           26                        836        (of 3044)
    Certified DISTINCT roots             26                        916        (disjoint-box collapse)
    Gate-4 per-ROOT: valid                                         503
    Gate-4 per-ROOT: rejected                                      413        (503+413=916 checks)
    Gate-4 per-SUBSET: >=1 valid root    22                        478
    Gate-4 per-SUBSET: only-rejected      4                        358        (478+358=836 checks)
    per-subset BOTH valid & rejected      3                         26        (overlap)
    multi-root subsets (lb>1)             0                         77
    UNRESOLVED_CERT_FAILED                                          78
    UNRESOLVED_NO_CANDIDATE                                       2130        (836+78+2130=3044 checks)
Lower bounds: unreached subsets stay UNRESOLVED_NO_CANDIDATE (never fabricated absence).

## Cross-checks (all hold, DOMAIN-CLEAN)
- Arithmetic closes: 836+78+2130=3044; per-root 503+413=916; per-subset 478+358=836; upgrades
  810=836-26.
- INDEPENDENT-GENERATOR AGREEMENT: 26/26 baseline roots re-found (<1e-9). No shared seeds.
- viol stratum justified universe-wide: 119 viol-only certified roots (78 rejected, 41 valid) that
  a Gate-4-filtered generator would structurally miss.
- multi-root universe-wide: 77 subsets with >1 disjoint certified root; 26 carry BOTH validity types
  -> Gate-4 validity is irreducibly PER-ROOT.
- WRITE-PATH GATE PASS (6/6): candidate_source=layer1; per-root gate4 closure_tol=1e-7; 77 multi-root
  preserved; class invariance asserted; baseline preserved-or-upgraded (0 contradictions); ALL
  certified roots in (0, pi/2) [check 6, the new domain guard]. certified-root h in [0.0085, 1.4874].

## Two-layer geography (domain-clean)
Per-root split 503 valid / 413 rejected (~55% valid). Universe is MAJORITY-VALID but the invalid
family is substantial (413 Rao-invalid certified roots), densest near the benchmark, not confined
there. Honest: "majority-valid universe-wide; substantial invalid minority, benchmark-densest."

## The removed population (a real, auditable finding)
The 972 removed candidates are constraint-roots of Rao's trig system on super-hemispheric caps
(r > pi/2), excluded by the registered domain. Legitimate one-sentence remark for the write-up:
"the trig system has a substantial solution population beyond the hemisphere, excluded by the
registered Meru domain" -- backed by the sidecar, not hand-waving.

## Scope / caution
- Presence LOWER BOUND under this generator / k=6 / cond<1e8 filter / registered h-domain. 3044-836
  =2208 subsets remain unresolved (78 had candidates that failed certification; 2130 had no
  in-domain candidate). Higher k or a different generator could certify more.
- Gate-4 tags authoritative per-root on certified centers (subset-level Layer-2 = has >=1 valid root).
- Write-path check 6 (all certified roots in (0, pi/2)) structurally guarantees domain compliance.

## Next
Merge -> CENSUS_CHECKPOINT_LAYER1 (union transfer-p0-p3 + layer1-clean); upgrade-only lattice;
per-root gate4 backfill onto the union's 26; every prior label preserved or upgraded. (Fable building.)

## Files
    candidates_layer1_full.jsonl (banked, contaminated -- keep for provenance),
    candidates_layer1_full_domainok.jsonl (CLEAN, census input),
    candidates_layer1_full_domainok_removed_outofdomain.jsonl (super-hemispheric sidecar),
    filter_altitude_domain.py, census_layer1_scratch.py (v2, check 6), layer1_candidates.py (v3, h>0).

SHA-256 hashes for all files in this unit are recorded in `docs/SHA256SUMS`