# CENSUS_CHECKPOINT_LAYER1_R2 — extended-radii tier (addendum to LAYER1 findings)

## What R2 is (and is not)
R2 is a CERTIFIER-PARAMETER tier, not a new discovery source. Same candidates (the 78
UNRESOLVED_CERT_FAILED subsets' already-proposed candidates), same frozen certifier, re-certified
with an EXTENDED RADII list below the 1e-5 default floor: [3e-3,1e-3,3e-4,1e-4,3e-5,1e-5,3e-6,1e-6,
3e-7,1e-7]. Because these are the SAME candidates under a different certification radius, the 40
converts are NOT independent corroborations (unlike layer1's 26/26 multi-source agreement).

## Mechanism (why extending radii DOWNWARD works and is safe)
At the 1e-5 default floor, affine-arithmetic overestimation of the Jacobian range over the
certification box drowns the Krawczyk certificate for some genuine roots (kraw:split). Below that
floor the box is small enough that AA dependency loss no longer dominates, and Krawczyk verifies
uniqueness. Confirmed on (1,2,6,10,16,19): resid 5.9e-16, cond(J)=1.77e4 IDENTICAL across radii,
certifies at 3e-6/3e-7/3e-8 -- the root is unchanged, only the box changed. Extending radii DOWNWARD
is strictly conservative: the certifier returns on the first 'unique', so existing certifications are
untouched and refusals can only convert.

## Result
Re-certification of all 78 CERT_FAILED under extended radii:
    converts     : 40/78     radius histogram: 3e-6:18, 3e-7:12, 1e-6:7, 1e-7:3
    still refused : 38
Most converts (18/40) certified at just 3e-6 -- ONE step below the old default floor -> the default
radius floor was slightly too coarse for a chunk of the census, not that those subsets were hard.
The 40 converts split evenly 20 valid / 20 rejected (Gate-4) -- the AA-overestimation refusal
mechanism is geometry-blind, unbiased toward either validity class.

## The R2 checkpoint (upgrade-only merge onto LAYER1; LAYER1 untouched)
                              LAYER1        LAYER1_R2
    FEASIBLE_CERTIFIED         836           876      (= 836 + 40)
    UNRESOLVED_CERT_FAILED      78            38      (= 78 - 40)
    UNRESOLVED_NO_CANDIDATE   2130          2130
    certified DISTINCT roots   916           956      (= 916 + 40, all singletons)
    Gate-4 per-ROOT       503v/413r     523v/433r     (= +20/+20)
    multi-root subsets          77            77      (all 40 R2 roots singletons)
Reconciliation (all exact): scratch 40/38/2966 matches the recertify diagnostic; identical-class
rows 2168 = 2130 NC/NC + 38 CF/CF; 876=836+40; 956=916+40; 523/433=503+20/413+20.
Invariants asserted: no downgrade, no layer1 loss, all roots gate4-tagged, all h in (0,pi/2).
SCOPE OPTIMIZATION: R2 scratch restricted to the 78 CERT_FAILED subsets only (--restrict-class),
so the merge PRESERVES the entire LAYER1 checkpoint verbatim -- including its 26 multi-source `agree`
records (verified: 26 preserved, 40 layer1_r2 rows) -- and lifts exactly the 40 converts. No
re-certification of the 836; a full re-run would have clumsily overwritten the agreement records.
"multi-source agreement 0" in the R2 merge print counts overlaps merged IN THIS RUN (correctly zero,
by the restriction); LAYER1's 26 pass through intact via the from_baseline branch.

## The 38-strong residue -- now mechanism-tagged (honest labels)
    33  guard-never-clean  : no clean (ok) box at any radius -- heavy interval dependency,
                             plausibly the near-singular fringe (overlaps the cond diagnostic's map).
     3  kraw:split         : genuine Krawczyk split at ALL tested radii -- locally degenerate.
     2  kraw:empty         : Krawczyk DISPROVED a root in the tested boxes despite resid <= 1e-8
                             -> these candidates are PSEUDO-ROOTS the loose 1e-8 discovery threshold
                             admitted. The census's FIRST Krawczyk-NEGATIVE evidence -- the certifier
                             cuts both ways (not just "fails to certify" but "actively disproves").

## Final standing (universe fully labelled)
876 of 3044 subsets certified; 956 certified distinct roots; per-root Gate-4 523 valid / 433 rejected;
77 multi-root subsets. Every remaining subset has a label, a route, and a reason:
    38   mechanism-tagged refusals (33 guard, 3 split, 2 pseudo-root)
    2130 unreached at k=6 (UNRESOLVED_NO_CANDIDATE -- honest: no in-domain candidate under tested
         generator/budget; never fabricated absence)
    + two auditable sidecars: 7960 high-cond (near-singular), 972 super-hemispheric (out-of-domain).

## Provenance / next
R2 arrives as its OWN checkpoint (CENSUS_CHECKPOINT_LAYER1_R2), NOT an edit to LAYER1. radii list in
the manifest; candidate_source=layer1_r2 on the 40 converts; radius_used per converted root. Open
threads for a future tier: the 33 guard-never-clean (near-singular study), k>6 on the 2130, and the
two sidecars. LAYER1 remains a valid tagged baseline; R2 supersedes it in coverage, not in validity.

## Files
    recertify_extended_radii.py (read-only diagnostic), census_layer1_scratch.py (v3: --radii,
    --restrict-census, --restrict-class), merge_census_layer1.py (v2: --checkpoint-name),
    docs/census_checkpoint_layer1_r2/{jsonl,csv,manifest,SHA256SUMS,log}

SHA-256 hashes for all files in this unit are recorded in `docs/SHA256SUMS`