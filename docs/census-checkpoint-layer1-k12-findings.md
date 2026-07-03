# CENSUS_CHECKPOINT_LAYER1_K12 — presence program complete (pre-registered stopping rule fired)

## Final presence standing
    FEASIBLE_CERTIFIED subsets     888 / 3044   (from 26 at the start of this arc)
    UNRESOLVED_CERT_FAILED          50
    UNRESOLVED_NO_CANDIDATE       2106
    certified DISTINCT roots       968
    Gate-4 per-ROOT                525 valid / 443 rejected
    multi-root subsets              77
Presence LOWER BOUND; unreached subsets stay UNRESOLVED_NO_CANDIDATE ("no in-domain candidate under
tested generator budgets k in {6,12}"), NEVER "infeasible"/"absent".

## The escalation curve (complete, rule-governed termination)
    k=6   -> 876 certified subsets (incl. the R2 extended-radii pass)
    k=12  -> over the 2130 previously-unreached: 1.94e6 seeds, 102,916 converged, 24 certifier-bound
             candidates, 12 CERTIFIED. +2,445 high-cond candidates across 410 subsets (sidecar).
    STOP: 12 new certified < N=25 (pre-registered before the run) -> escalation terminates; k=24
          NOT run. The budget is now a CURVE with a pre-stated endpoint, not an open "try harder".
Pre-registration committed BEFORE the run (k-escalation-preregistration.md), so termination is a
criterion, not fatigue. This is the value of the committed stopping rule: the k=12 candidate count
(24 < 25) settled the k=24 question BEFORE certification even ran.

## Merge integrity (upgrade-only; R2 preserved verbatim)
888=876+12, 968=956+12, gate4 525/443=523+2/433+10, NO_CANDIDATE 2106=2130-24, CERT_FAILED 50=38+12,
multi-root 77 unchanged. Invariants asserted: no downgrade, no layer1 loss, all roots gate4-tagged,
all h in (0,pi/2). Write-path gate PASS 6/6. Registered extended radii [3e-3..1e-7] passed explicitly
(certifier engine unchanged, de64edfa4979); radius_used per root; candidate_source=layer1_k12.

## Reading the "other transitions" list (restriction made visible -- NOT an anomaly)
The scratch is layer1-only and restricted to R2's UNRESOLVED_NO_CANDIDATE, so the comparison list has
two opposite-meaning directions:
  - ~38 CF->NC : baseline CERT_FAILED subsets outside k12's scope; the layer1-only scratch says
    "no candidate" for them, and the merge lattice CORRECTLY keeps the baseline's stronger CF label
    (this is why merged CF = 50, not fewer). Not a downgrade -- the lattice preserved the label.
  - 12 NC->CF : the real content -- k12 candidates that FAILED certification under the registered
    extended radii. Because these arrive already radius-escalated, the ENTIRE 50-subset refusal
    residue is now UNIFORMLY post-extended-radii: a clean single population for the residue study,
    with NO pending "maybe a smaller box fixes it" for any of them.

## Scoped observation (hint, not claim)
The 12 deep-budget (k=12) certifications split 2 valid / 10 rejected (Gate-4). At n=12 this is a
HINT that the harder-to-reach population skews Rao-invalid, consistent with the invalid family being
denser in the less-accessible region -- but the sample is too small for a distributional claim.

## The remaining frontier is characterized, not empty
The 2106 still-unreached are NOT "nothing converges": k=12 produced 2,445 high-cond candidates across
410 of them (COND_MAX=1e8 sidecar, auditable, NOT census input). So the honest characterization is
"no CERTIFIER-BOUND candidate under tested budget", and at least 410 of the 2106 demonstrably carry
NEAR-SINGULAR candidate structure -- the entry point to the high-cond-sidecar study.

## Presence program status: DONE (by rule), not paused
The census now has a beginning (k=6 discovery), a middle (R2 radius refinement + k=12 escalation),
and a rule-governed END (pre-registered N<25 stop). No further budget escalation is planned. What
remains is downstream science, not more census machinery:
  - the 50-subset refusal residue (now uniformly post-extended-radii): mechanism-tag the 12 new ones
    (recertify diagnostic pattern) to complete the tagging; study kraw:empty pseudo-roots / kraw:split
    twin-root candidates.
  - the high-cond sidecar as a study of degenerate strata (new 410-subset k=12 entry point).
  - the write-now vs targeted-absence-sample fork (absence should strengthen the paper, not delay it).
  - bookkeeping: plane-study Zenodo v1.1.0 deposit; findings consolidation; super-hemispheric remark.

## Checkpoint lineage
LAYER1 (v1.0, 836) -> R2 (v1.1, 876) -> K12 (v1.2, 888). Each a valid tagged baseline; each supersedes
the prior in COVERAGE, not in validity. K12 is the current authoritative presence checkpoint.

## Files
    layer1_candidates.py (--k, --restrict-*), filter_altitude_domain.py, census_layer1_scratch.py
    (--radii/--restrict-*), merge_census_layer1.py (--checkpoint-name),
    docs/census_checkpoint_layer1_k12/{jsonl,csv,manifest,SHA256SUMS,log},
    k-escalation-preregistration.md (pre-run). Candidate/scratch/sidecar gitignored (regenerable,
    deterministic from committed source + GLOBAL_SEED); high-cond sidecar retained as audit material.

SHA-256 hashes for this file in this unit is recorded in `docs/SHA256SUMS`