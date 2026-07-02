# Layer-1 shard 0:100 — the viol stratum is decisively justified (but yield is NOT universe-representative)

## Scope / caution (read first)
Shard 0:100 is the LEXICOGRAPHIC HEAD of the sorted 3044 universe: every subset is (1,2,3,4,...),
i.e. the benchmark's own neighborhood. This is the WORST region for Gate-4 validity (the benchmark
family is containment-violating). So the certified RATE (37/40) and the invalid-heavy split
(23 rejected vs 17 valid) are NOT representative of the universe. This shard validates the
PIPELINE and the DESIGN; a STRIDED SPREAD shard (e.g. universe[::30]) is required before ANY yield
estimate. Candidate files are scratch (regenerable, biased) and are gitignored, not committed.

## Decisive result: the viol stratum finds roots a filtered generator structurally misses
From diagnose_layer1_certify.py (certify_2b_general decides; collapse_certified for distinct roots):
    VIOL-STRATUM-ONLY certified roots (reached by NO other stratum): 8
        of which Gate-4 REJECTED (Rao-invalid): 6
        of which Gate-4 valid:                  2
These 6 certified Rao-INVALID roots live in the containment-violating region (b+c>R and/or d+e>R)
and were reachable ONLY because the viol stratum deliberately seeds there. A Gate-4-filtered
generator (e.g. mapper _candidates, which imposes b+c<R, d+e<R at the SEEDING stage) would
STRUCTURALLY MISS them. This directly justifies the full-domain Layer-1 design: the invalid family
is larger than the 4 known from warm-start -- this single (biased) shard already adds 6 more.

## Multiplicity: first root_lower_bound > 1 in the census
certified DISTINCT roots (disjoint-box collapse): 42 across 37 subsets.
multi-root subsets (>1 DISJOINT certified root): 4.
Warm-start structurally could not see this (one basin per subset). collapse_certified confirms
these are genuinely distinct roots (disjoint Krawczyk boxes), not duplicate candidates.
3 subsets carry BOTH a Gate-4-valid and a Gate-4-rejected distinct root.

## Cross-generator corroboration
Independent-generator agreement (Fable diagnose_layer1_shard.py): 2/2. On the two already-certified
subsets in this shard, Layer-1 re-found the known warm-start roots (|dx|<1e-9). Layer-1 and
warm-start share NO seeds, so agreement is real corroboration -- two independent methods on the
same geometry.

## Pipeline health
Layer-1 certified subsets: 37/40 candidate subsets.  NOT_CERTIFIED: 5 (clean certifier refusals;
good proposal quality, 42/47 certified).  Determinism verified in smoke.
per-stratum proposed/certified: box 31/28, viol 8/8, logwide 5/3, neardeg 3/3.
displacement: min 0.281, median 0.826, MAX 4.762. The 4.76 case is a large-basin "lucky jump"
(fine for discovery -- certifier decides -- but reach at the margins is seed-schedule-sensitive;
worth watching, not alarming).
Gate-4 metadata in diagnose_layer1_certify.py is computed with closure_tol=1e-7,
matching the mapper / census convention. Re-running after pinning this tolerance
left the shard counts unchanged.

## What is NOT claimed
- NO universe-wide yield estimate (shard is biased; strided spread shard pending).
- NO census merge (scratch only; committed CENSUS_CHECKPOINT_TRANSFER_P0_P3 untouched).
- Gate-4 tags here are on certified centers (authoritative), but the COUNTS are shard-local.

## Next
1. Strided spread shard universe[::30] (--stride if supported; else add) -> honest yield estimate.
2. Compare 3 shards (head + spread + one more) before budgeting the full ~3017 run.
3. Only after concordant yield: full run -> scratch census -> compare to checkpoint -> merge decision.

## Files
    diagnose_layer1_shard.py     Stage-1 candidate analysis (non-mutating, no certification)
    diagnose_layer1_certify.py   Stage-2 certification + disjoint-box collapse + viol split
    (candidates_layer1_shard0.jsonl: SCRATCH, gitignored, regenerable, lexicographically biased)

SHA-256 hashes for all files in this unit are recorded in `docs/SHA256SUMS`