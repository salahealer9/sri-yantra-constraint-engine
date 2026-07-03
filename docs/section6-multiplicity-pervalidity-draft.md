# Section 6 — Multiplicity and per-root geometric validity (draft)

Section 2 argued that geometric validity must be attached per-root rather than per-subset. This
section quantifies that claim against the final census and reports the associated multiplicity
structure.

## 6.1 Multiplicity: subsets with several certified roots

A six-constraint subset need not determine a unique figure. When a subset admits more than one real
constraint-root, our procedure certifies each separately and counts distinct roots by a disjoint-box
collapse: two certified candidates count as the same root only if their validated enclosures overlap,
and as distinct roots only if their enclosures are provably disjoint. This makes the per-subset root
count a rigorous lower bound rather than a numerical estimate.

Across the 888 certified-feasible subsets, the census certifies 968 distinct roots. Of these subsets,
77 admit more than one certified root; the remaining 811 carry a single certified root. Equivalently,
the census contains 80 certified roots beyond the one-root-per-subset baseline (968 - 888). Multiplicity
is thus a real and recurring feature of the system, not an isolated anomaly.

    Table 3. Root multiplicity across certified-feasible subsets.
    ------------------------------------------------------------
    certified roots per subset        subsets
    ------------------------------------------------------------
    exactly 1                             811
    more than 1                            77
    ------------------------------------------------------------
    total certified-feasible subsets      888
    total certified distinct roots        968
    ------------------------------------------------------------

## 6.2 Geometric validity at the root level

Each certified root carries a Layer-2 geometric-validity tag. At the root level the split is

    525 geometrically valid roots  +  443 roots rejected by the registered Gate-4/Rao-validity test
    =  968 certified roots,

so a majority (about 54%) of certified roots are valid Rao figures, with a substantial minority of
algebraically-real roots that fail the registered validity test. We refer to the latter as
geometrically rejected roots in what follows.

## 6.3 Geometric validity at the subset level, and why it cannot replace the root level

Projecting these tags to the subset level produces the geography in Table 4. A subset is
"valid-bearing" if it carries at least one valid certified root and "rejected-bearing" if it carries
at least one rejected root; a subset may be both.

    Table 4. Gate-4/Rao geometric-validity geography by subset.
    ------------------------------------------------------------
    subset type                                subsets
    ------------------------------------------------------------
    valid-only     (>=1 valid, no rejected)        474
    rejected-only  (>=1 rejected, no valid)        388
    both-type      (>=1 valid AND >=1 rejected)     26
    ------------------------------------------------------------
    total certified-feasible                       888
    ------------------------------------------------------------
    (valid-bearing 500 + rejected-bearing 414 - both 26 = 888)

The 26 both-type subsets are the decisive entries. Each certifies at least one geometrically valid
root AND at least one geometrically rejected root for the SAME six-constraint subsystem. No single
validity label can be assigned to such a subset without discarding certified information: the subset
is neither "valid" nor "rejected" as a whole. This is the empirical content of the per-root claim of
Section 2 -- subset-level tagging is not merely lossy but incapable of representing the 26 both-type
subsets correctly -- and it is why geometric validity is recorded as per-root metadata throughout the
census. The subset (1,2,3,4,6,13) is a concrete instance: it carries both a rejected and a valid
certified root.

## 6.4 Where the rejected roots live

The geometrically rejected roots are not uniformly distributed over the universe. They are prominent
near the benchmark family, where the containment margins a = r-(b+c) and f = r-(d+e) readily go
negative, but they are not confined to that region. A further structural point supports the neutral-generator design of Section 4: a
number of the rejected roots were reached ONLY by the containment-violating search stratum, i.e. by
candidates a containment-enforcing generator would never have proposed. These "stratum-unique"
rejected roots are direct evidence that enumerating all certified constraint-roots requires a
discovery procedure neutral to Layer-2 validity.

---
## Notes (author; delete before submission)
- 6.1: 811 single-root = 888 - 77. Confirm the 77 multi-root count from CENSUS_CHECKPOINT_LAYER1_K12
  (matches CURRENT_CHECKPOINT.md). Disjoint-box collapse = the census's distinct-root method.
- 6.2: 525/443 from CURRENT_CHECKPOINT.md; ~54% = 525/968. State exactly if the venue wants it.
- 6.3: Table 4 (474/388/26) verified from K12; valid-bearing 500 = 474+26, rejected-bearing 414 =
  388+26; 500+414-26 = 888 (inclusion-exclusion). (1,2,3,4,6,13) verified both-type.
- 6.4: "stratum-unique rejected roots" = the viol-only-certified count. From the FULL-run diagnostic
  the universe-wide viol-only was 119 (78 rejected / 41 valid); if you want the exact number in the
  text, cite the K12/full figure and confirm which checkpoint's viol-only you report. The qualitative
  claim (some rejected roots reached ONLY by the viol stratum) is robust regardless.
  [VERIFY before final: the exact viol-only count to quote, and its rejected/valid split, from the
  checkpoint you cite. The narrative claim needs only "> 0 rejected viol-only", which holds.]
- FEEDS FROM: gate4-two-layer-findings.md, layer1-full-census-finding.md, k12-findings.
