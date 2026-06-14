# Validation panel on the corrected box B_plane (exploratory)

Run before the §B8 freeze and Gate M; therefore **exploratory**, not confirmatory.
Box: B_plane (enumeration/B.json, from generate_B.py, Rao Table 3, r=1).
Method: domain_v3 admissibility exclusion + AAr exclusion + AA-Krawczyk; depth cap 200.

## Objective 1 — Regression (Table-3 rows must recover their Rao root)

| subset | complete | boxes | cert | recovered | unresolved | max_depth |
|---|---|---|---|---|---|---|
| {1,2,3,4,8}   | yes | 6853  | 1 | Rao | 0 | 26 |
| {1,2,4,5,10}  | yes | 11943 | 1 | Rao | 0 | 51 |
| {1,2,3,10,15} | yes | 10913 | 1 | Rao | 0 | 26 |

PASS — box correction broke nothing; all Rao roots recovered, 0 unresolved.

## Objective 2 — Admissibility stress (no false cert/exclusion; degenerate refuses)

| subset | complete | boxes | cert | unresolved | localization |
|---|---|---|---|---|---|
| {1,2,11,12,17} | yes | 2831 | 0 (absence) | 0 | — |
| {1,2,6,10,19}  | yes | 5767 | 1 | 0 | — |
| {1,2,3,4,6}    | yes | 2953 | 0 (absence) | 0 | — |
| {1,2,8,9,16}   | no  | 5786 | 0 | 306 | other (NOT a seam) |

PASS — well-posed subsets clean (correct presence/absence). The rank-deficient
{1,2,8,9,16} (excluded from the 815) correctly refuses certification; its
unresolved population is the rank-deficiency continuum, classified as NOT a
denominator surface — confirming the classifier distinguishes degeneracy from a seam.

## Objective 3 — Seam discovery (force F13->U20, F14/F15->U21)

| subset | constraints exercising seam | complete | cert | unresolved | new seam? |
|---|---|---|---|---|---|
| {1,2,3,4,13}   | F13 -> U20 (Q20+1) | yes | 0 (absence) | 0 | none |
| {1,2,6,14,19}  | F14 -> U21 (Q21+1) | yes | 1 (Rao)     | 0 | none |
| {1,2,3,4,14}   | F14 -> U21 (Q21+1) | yes | 0 (absence) | 0 | none |
| {1,2,13,14,15} | F13+F14+F15 -> U20+U21 | yes | 0 (absence) | 0 | none |

RESULT — no unresolved population on any subset; the U20 and U21 blow-up loci do
not manifest inside B_plane. (F15->U21 also exercised, cleanly, by the regression
subset {1,2,3,10,15}.)

## Conclusion

Across 11 subsets spanning all three objectives, B_plane produces a well-posed
enumeration: every well-posed subset completes with 0 unresolved boxes; Rao roots
are recovered where expected; absence is certified where expected; the lone
rank-deficient subset correctly refuses certification without producing a spurious
seam. No coordinate blow-up seam beyond x11a manifests in B_plane, and x11a itself
does not activate here (domain_excl = 0 on every subset). This supports the working
hypothesis that the admissible domain is governed by a finite set of coordinate
blow-up surfaces, all of which the corrected box B_plane avoids.

The admissibility exclusion (domain_v3) is retained in the frozen tool as a
rigorous completeness safeguard realizing the §6 "arc arguments in range"
condition; the panel evidences that it neither over-excludes (0 false exclusions;
all expected roots recovered) nor is stressed within B_plane. This is a sample of
11 subsets, not the full 815; the campaign's own completeness criterion (queue
exhaustion under rigorous arithmetic, depth-cap unresolved -> Tier-1 downgrade)
remains the operative guarantee per subset.
