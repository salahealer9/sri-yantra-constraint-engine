# Layer-1 refusal structure: near-singular candidate clouds (stride-30 sample) + COND_MAX filter

## What prompted this
The stride-30 spread shard certified far less than the lexicographic head (25/64 candidate-subsets
vs 37/40), with 314/340 candidates NOT_CERTIFIED. Before budgeting the full run, diagnose WHY the
314 refuse -- "diagnose before scaling", as every prior tier.

## Correction of an earlier read (candidate multiplicity != root multiplicity)
An earlier read called multiplicity "universe-wide" from 43/64 subsets having multiple CANDIDATES.
That conflated candidate clouds with distinct ROOTS: after certification only 1 multi-root subset
survives on the spread. High candidate-multiplicity CO-OCCURRING with 92% refusal is the signature
of NEAR-SINGULAR structure, not many isolated roots.

## The decisive cross-tab (diagnose_refusals.py --certify, stride-30 sample)
cond(J) at candidate (resid<=1e-8 by construction) x certify outcome:
    outcome                        <1e3  1e3-1e6  1e6-1e8  1e8-1e10  >=1e10
    CERTIFIED_UNIQUE_GEOMETRIC       24        2        0         0        0
    kraw:None (no verdict reached)    1       19       22       196       70
    kraw:split (singularity verdict)  0        0        0         0        6
KEY: certification succeeded ONLY at cond(J) < 1e6 (26/26). ZERO of 294 candidates at cond>=1e6
certified (across both shards). The 1e6-1e10 mass is 218/218 Gate-4-invalid. kraw:None means the
certifier's AA/interval domain guard splits at every radius (interval widths explode under that
conditioning) -- it mostly never reaches a Krawczyk verdict; kraw:split (all >=1e10) is the direct
singularity verdict. High-multiplicity clouds show NN distances from 1e-7 (points microns apart
along a near-null direction) to 1e-1 (spread along sheets), median cond ~1e8-1e10+.

## Finding (SCOPED -- numerical conditioning, NOT a variety-dimension proof)
In the stride-30 sample, high-condition candidate clouds dominate the refusal mass. This is
NUMERICAL EVIDENCE for near-singular / non-isolated-LOOKING structure in some constraint subsets,
concentrated in the containment-violating region. It is NOT a proof of positive-dimensional
solution components. "Near-singular signature" is a conditioning observation. The universe's
well-posedness rank-check (8 sample points per subset) cannot exclude rank collapse on subvarieties;
the spread sample says such degenerate strata carry most of the converged-candidate mass. Whether
any of these sets is genuinely positive-dimensional is a SEPARATE, later question (and interesting).
Footnote: 6 Gate-4-VALID candidates at cond>=1e10 -- valid figures at near-singular roots resemble
tangency/fold configurations; not investigated here.

## The change (declared, diagnostic-justified hygiene filter -- TRIAGE not deletion)
layer1_candidates.py v2: records cond_J on every candidate; applies COND_MAX=1e8 as a DECLARED
proposer-side filter (justification string embedded in meta). Cutoff 1e8 (not 1e6): removes ~87% of
wasted certification while keeping a 100x margin above the highest bucket that ever certified, so no
plausibly-certifiable candidate is filtered after a single spread shard.
CRITICAL WORDING: high-cond candidates are NOT called "not roots". They are Newton-converged
numerical candidates OUTSIDE the declared certifier-bound proposal stream, PRESERVED in a
*_highcond.jsonl sidecar for audit. Nothing is discarded; the certifier remains the sole authority.
Layer-1 neutrality intact: the near-singular population stays in the record. Same epistemic category
as the collapse floor -- a declared hygiene filter, not an outcome bias.
Validated: split behaves as designed -- known roots stay in the main file at low cond (258, 1452);
(1,2,10,13,16,17)'s cloud splits 2 main / 20 sidecar (sidecar cond 1.2e8-4.7e10); even that
pathological subset keeps 2 candidates below the cutoff (the filter triages mass within subsets, it
does not write off subsets).

## Effect on the full run
Generation +~5% (one extra Jacobian per accepted candidate for cond). Certification afterward drops
from a projected ~4 h to well under 1 h (only ~14% of candidates survive the filter, per spread).

## Also from the spread (scoped to the stride-30 sample)
- Invalid family is BENCHMARK-LOCAL: head (benchmark neighborhood) was 25 rejected + 6 viol-only
  invalid; spread is near-even 13 rejected / 12 valid, viol-only=2 and BOTH valid. Rao-invalid
  roots cluster near the benchmark, are NOT universe-pervasive (in this sample).
- viol stratum still earns its place: finds certified roots other strata miss (viol-only>0), but
  universe-wide those are valid figures; the invalid-root payoff was benchmark-local.

## Files
    diagnose_refusals.py     cond(J) + NN-dist structure; --certify adds the outcome x cond cross-tab
    layer1_candidates.py v2  cond_J recorded; COND_MAX=1e8 declared filter + highcond sidecar
    (candidates_layer1_full.jsonl -> certification; candidates_layer1_full_highcond.jsonl -> audit,
     NOT census input but must remain auditable)

SHA-256 hashes for all files in this unit are recorded in `docs/SHA256SUMS`