# Spherical presence-first census — CHECKPOINT (26 certified) + scoped next step (mapper smoke test)

## Current state (committed)
CENSUS_CHECKPOINT_TRANSFER_P0_P3 (union of direct + transfer p=0 + transfer p=3, general certifier):
    FEASIBLE_CERTIFIED       26   (benchmark + 25 non-benchmark)
    UNRESOLVED_CERT_FAILED    1   (candidate proposed, certifier declined -- honest refusal)
    UNRESOLVED_NO_CANDIDATE  3017
    INFEASIBLE_CERTIFIED      0
    (3044 = 26 + 1 + 3017)

Yield curve (warm-start reach, diminishing as shell-adjacency predicts):
    direct (Table1 + benchmark)   8 certified subsets
    transfer p=0                +14 new
    transfer p=3                 +4 new
    ------------------------------------
    total                        26 certified subsets

READ: warm-start / seed-transfer is productive but clearly diminishing (14 -> 4). The remaining
~3017 subsets were NOT reached by the tested warm-start/transfer search (p=0, p=3) from the known
roots -- a statement about THIS method's reach, not a geometric claim that no basin access exists
(other perturbations, seed distributions, or mapper strategies may reach them). --perturb 10 would
likely yield little. The next increment is a DIFFERENT generator: DOMAIN-WIDE per-subset search.

## Committed toolchain (this arc)
Universe : generate_universe.py -> subset_universe.json (3044, sha b37f4312)
Certify  : certify_2b_general.py (wired all 3044; certified on 8 real systems; gate 8/8)
Regress  : first_nonbenchmark_certified_root.json + gate_nonbenchmark_regression.py (PASS)
Discover : candidate_search_warmstart.py (serial), candidate_search_parallel.py (--workers,
           deterministic per-subset blake2b seed, parent-only write; equivalence gate PASS)
Merge    : merge_candidates.py (schema-robust union; raw 6-float arrays; preserves all candidates)
Diagnose : diagnose_transfer.py (yield + failure-mode breakdown)
Census   : spherical_presence_census_dryrun.py + spherical_census_io.py (JSONL/CSV/manifest/SHA)
Absence  : CLOSED as architectural negative (four-method convergence); INFEASIBLE_CERTIFIED not
           operationally reachable this architecture -> census is PRESENCE-FIRST by design.

## NEXT (fresh session): mapper integration SMOKE TEST -- not a full run
The domain-wide generator already exists: spherical_existence_mapper.find_seed does genuine
per-subset multistart (box-preferential + domain-wide log-uniform + near-degenerate locus,
multiple altitudes, stable-hash reproducible) -> can reach subsets far from known roots.

DANGER POINT: coordinate bridge. find_seed works in R=(pi/2 - h) scaled proportions and returns
[b,c,d,e,g, h_rad]; certify_2b_general wants RAW (b,c,d,e,g,h). DO NOT assume the convention from
comments -- PROVE it by round-trip.

Build candidate_search_mapper_smoke.py that does ONLY:
  1. import spherical_existence_mapper.find_seed on the server
  2. confirm its dependency stack imports cleanly (stage1b_landscape, spherical_geo_check,
     stage1_fold_analysis) alongside the FROZEN sriyantra.py (engine hash de64edfa unchanged)
  3. run find_seed on the BENCHMARK subset {1,2,3,4,6,7} only
  4. inspect raw coordinate output
  5. bridge coords -> raw (b,c,d,e,g,h)
  6. pass bridged candidate to certify_2b_general
  7. REQUIRE CERTIFIED_UNIQUE_GEOMETRIC at the same root scale (resid ~1e-15, cond ~137)
  8. repeat on ONE non-benchmark Table 1 certified subset (e.g. (1,2,3,5,10,19))
GATE: mapper output -> bridge -> certify_2b_general -> SAME certified root. Trust nothing until pass.

ONLY after the smoke gate passes:
  - build candidate_search_mapper.py (SAME discipline: mapper PROPOSES, certifier DECIDES,
    census_io RECORDS; propose-only, provenance = seed policy/altitude/Gate-4 status)
  - run a SMALL SHARD first (50-100 unresolved subsets), diagnose, then scale
  - use the parallel harness (deterministic per-subset seed, parent-only write) for the full run
  - respect the ~06:00 UTC reboot window (shard or disable auto-reboot for long runs)

## Discipline invariants (do not regress)
  * discovery PROPOSES; certify_2b_general DECIDES; census_io RECORDS. No fabricated coverage.
  * no candidate -> UNRESOLVED_NO_CANDIDATE (never fake absence).
  * INFEASIBLE_CERTIFIED only if complete+trace-passed+lb==0 (census_io guardrail); not reachable now.
  * every artifact regenerable from committed source (no inline-snippet orphans).
  * coordinate bridges proven by round-trip on known roots, never assumed from comments.

SHA-256 hash for this file in this unit is recorded in `docs/SHA256SUMS`