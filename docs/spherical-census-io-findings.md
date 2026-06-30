# Spherical Census Output Layer — built + integrity-verified (mirrors plane census)

**Status.** Exploratory build (no driver/engine changes). Component 2 of the hybrid
finisher: the reproducible output layer the 3044 pass writes into. Integrity battery PASS.
Frozen v1.2 + frozen engine UNCHANGED.

## Architecture (mirrors the plane census; JSONL is source of truth)
  spherical_roots.jsonl        AUTHORITATIVE. One JSON record/subset; carries the FULL
                               certify_2b evidence bundle per root (unflattened, re-auditable).
  spherical_census.csv         DERIVED from the jsonl (never the reverse). Lightweight index.
  spherical_census_manifest.json  provenance: engine_sha, certifier_sha, status_counts (from
                               jsonl), output hashes, platform/python/seed/command/timestamps.
  SHA256SUMS                   hashes of jsonl + csv + manifest + log.
  spherical_census.log         per-subset execution log.

## Record schema (spherical_census_v1)
schema_version, subset, class, root_lower_bound, num_certified_roots, completeness_status,
trace_status, candidate_source, roots[ {coords, radius, residual, cond_J, engine_hash,
evidence:{full certify_2b bundle}} ], agree{status,sources,notes}, notes.

Classification (class) is SEPARATED from completeness (completeness_status/trace_status) so a
numeric non-proof can never masquerade as a certified absence. All 8 honest labels carried:
  FEASIBLE_CERTIFIED, INFEASIBLE_CERTIFIED, PARTIAL_CERTIFIED_ROOTS_K, UNRESOLVED_NO_CANDIDATE,
  UNRESOLVED_CERT_FAILED, UNRESOLVED_TRACE_FAILED, NO_REAL_ROOTS_FOUND_TRACE_NUMERIC, TECH_FAIL.

## Hard guardrails (encoded, tested)
 - INFEASIBLE_CERTIFIED is emitted ONLY if completeness_status=='complete' AND
   trace_status=='passed' AND no certified real root. make_record() ASSERTS this and raises
   otherwise. Tested: unfounded INFEASIBLE_CERTIFIED raises; numeric_only->INFEASIBLE raises.
 - NO_REAL_ROOTS_FOUND_TRACE_NUMERIC / numeric traces can only downgrade, never upgrade.
 - DOMAIN_INVALID / failed candidates classify as UNRESOLVED_CERT_FAILED, NEVER infeasible.
 - engine_sha must RESOLVE (env SRIYANTRA_ENGINE or known paths); writing 'unknown' into the
   manifest RAISES -- no silent provenance hole. (The server battery showed engine_hash=
   'unknown' because the engine isn't at /mnt/project there; set SRIYANTRA_ENGINE on the
   server so certificates tie to the frozen engine.)

## De-duplication wired into classification
classify_feasibility collapses overlapping certified boxes to one representative per cluster
(via certify_2b.collapse_certified), so roots[] is de-duplicated and num_certified_roots ==
root_lower_bound == #disjoint clusters. k distinct roots <=> k pairwise-disjoint certified
boxes.

## Integrity battery (test_census_io.py) -- ALL PASS
  known root            -> FEASIBLE_CERTIFIED (1 root, evidence preserved, engine_hash present)
  off-root far          -> UNRESOLVED_CERT_FAILED
  out-of-domain         -> UNRESOLVED_CERT_FAILED (NOT infeasible)
  no candidate          -> UNRESOLVED_NO_CANDIDATE
  two overlapping certs -> 1 root in jsonl, lower_bound 1
  two disjoint certs    -> 2 roots in jsonl, lower_bound 2
  verified: jsonl parses line-by-line; csv derives from jsonl (rows+classes); manifest hashes
  match outputs; engine_sha resolved (64-char, not 'unknown'); SHA256SUMS matches all;
  status_counts match jsonl; both INFEASIBLE guardrails raise.

## Role + next
The certifier feeds the JSONL; classification feeds the CSV; the manifest ties the run.
Every later experiment writes into this evidence format (no ad hoc logs). Next per the locked
order: polynomialize the {1,2,3,4,6,7} chain + estimate mixed volume / path count -> decides
whether the absence branch (INFEASIBLE_CERTIFIED) is realistic before it is defined.

## Files
  spherical_census_io.py   output layer (jsonl/csv/manifest/sha/log + guardrails)
  test_census_io.py        integrity battery (reproducible)
  spherical-census-io-findings.md  this report

SHA-256 hashes for all files in this unit are recorded in `docs/SHA256SUMS`