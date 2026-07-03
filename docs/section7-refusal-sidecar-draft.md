# Section 7 — Refusal and sidecar populations (draft)

The census partitions the 3044 subsets into 888 certified-feasible, 50 certification refusals, and
2106 with no certifier-bound candidate. This section characterises the two populations that are
neither certified nor empty: the 50 refusals, and the candidates set aside by the declared filters.
Both are recorded and auditable; neither is discarded.

## 7.1 The 50 certification refusals

The 50 UNRESOLVED_CERT_FAILED subsets are those for which a candidate was proposed but no certified
root was obtained. Because the census certifies under the registered extended-radius list, these are
refusals under that policy -- not artifacts of a coarse radius floor. Re-running the certifier over
the 50 subsets' candidates under the extended radii converts none of them (0 of 50), so the residue is
stable and uniformly post-extended-radii. Bucketing the refusals by mechanism gives Table A.

    Table A. Certification-refusal mechanisms across the 50 UNRESOLVED_CERT_FAILED subsets.
    (Mechanism is that of the first refused candidate per subset; kraw:empty is also
     reported per candidate, since it is a candidate-level local exclusion.)
    --------------------------------------------------------------------------------------
    mechanism            subsets   interpretation                       claim status
    --------------------------------------------------------------------------------------
    guard-never-clean       44     no clean interval box at any radius;  refused, not disproven
                                   heavy interval dependency (near-
                                   singular fringe)
    kraw:split               4     Krawczyk operator splits at every     refused, not disproven
                                   tested radius; locally degenerate
    kraw:empty               2     Krawczyk excludes the candidate root  local negative on the
                                   within the tested box                 candidate(s)
    --------------------------------------------------------------------------------------
    total                   50
    --------------------------------------------------------------------------------------
    candidates tested: 91.  kraw:empty at the candidate level: 4 candidates (across the 2 subsets).

The dominant mechanism, guard-never-clean (44 subsets), is the interval-arithmetic signature of
near-singular structure: no box at any tested radius yields a clean uniqueness certificate. The
kraw:split subsets (4) are locally degenerate at every radius. The kraw:empty subsets (2, comprising 4
candidates) are the only refusals carrying a NEGATIVE certificate: for those specific candidates the
Krawczyk operator excludes a root within the tested certification box despite a small residual --
these candidates are numerical near-roots whose tested certification boxes contain no root -- a LOCAL
exclusion on the candidate, not a claim that the subset has no root. Thus the interval method here does not merely
fail to certify; on four candidates it actively excludes.

None of the 50 is an absence result at the subset level (Section 8.3).

## 7.2 The sidecar populations

Two populations of candidates are set aside by declared filters BEFORE certification. Neither is
census input; both are retained as audit evidence.

    Table B. Filtered candidate populations (retained, not census input).
    -----------------------------------------------------------------------------------------------
    sidecar            candidates   distinct subsets   why set aside                  future-work value
    -----------------------------------------------------------------------------------------------
    high-condition        10,405         1,232         cond(J) > COND_MAX = 1e8;      near-singular /
                                                       outside the certifier-bound    degenerate strata
                                                       stream (no candidate above     study
                                                       cond ~1e6 ever certified in
                                                       the diagnostic sample)
    super-hemispheric        972           553         h <= 0 (r > pi/2); real roots  registered-domain
                                                       outside the registered Meru    extension
                                                       domain (0, pi/2)
    -----------------------------------------------------------------------------------------------

The high-condition sidecar is large (10,405 candidates across 1,232 subsets), and it is the main
reason the unreached population is not empty: many subsets with no CERTIFIER-BOUND candidate
nonetheless produce near-singular candidates above the conditioning cutoff. This is NUMERICAL evidence
of near-singular structure in parts of the constraint variety; it is not a proof of positive-
dimensional solution components, and we make no such claim here. The super-hemispheric sidecar (972
candidates) collects genuine real roots of the trigonometric system that lie outside the registered
altitude domain; they are excluded by registration, not by any defect, and are the natural object of a
future registered-domain extension.

## 7.3 Summary of the non-certified universe

    certification refusals (Table A)          50 subsets  (44 guard / 4 split / 2 empty)
    no certifier-bound candidate            2106 subsets
    ------------------------------------------------------------
    non-certified total                     2156 subsets  (= 3044 - 888)

Every subset in the universe therefore carries a definite status with a recorded reason: certified,
refused with a named mechanism, or unreached under the tested budget -- and every filtered candidate
is retained in an auditable sidecar.

---
## Notes (author; delete before submission)
- Table A counts exact (extended-radii recertify, 0/50 convert): guard-never-clean 44, kraw:split 4,
  kraw:empty 2 subsets / 4 candidates. 44+4+2=50. candidates tested 91.
- kraw:empty subsets: (1,2,6,7,9,19), (1,2,6,9,19,20). kraw:split subsets: (1,2,3,4,16,17),
  (1,2,4,5,13,16), (1,2,4,10,16,17), (1,2,6,10,16,17). Use as in-text anchors if desired.
- Section 8.3 exact number: kraw:empty = 4 CANDIDATES (not "a small number") -> update 8.3.
- Table B: high-cond 10,405 candidates / 1,232 subsets (full+k12 highcond files, census-relevant
  only, NOT shard-era). super-hemispheric 972 (full_domainok filter meta n_removed). Keep the
  1e6-observed / 1e8-cutoff distinction. "not a positive-dimension proof" scoping per Section 8.
- 7.3: 2156 = 3044-888 = 50+2106. Reconciles.
- FEEDS FROM: refusal-structure-finding.md (d972c657), r2-findings, k12-findings, recertify pass.
