# Section 8 — Limitations and scope of claims (draft)

This is a presence census. Its claims are deliberately bounded, and we state those bounds explicitly
here so that the positive results are not read as more than they are.

## 8.1 No certified absence

The census certifies the PRESENCE of roots; it does not certify their ABSENCE. No subset is labelled
infeasible: INFEASIBLE_CERTIFIED = 0 throughout. A subset that no tier reaches is recorded as
"unresolved, no candidate", never as "no root exists".

This is not an oversight but a reflection of where the difficulty lies. Certifying that a subset has
NO real root in the registered domain is a global claim about the whole solution set, and the natural
route to it -- a complete global homotopy that tracks every path of the polynomial system -- proved
computationally intractable for these systems. We reached that conclusion by convergent evidence from
four independent methods (mixed-volume overflow, degree-box bounding, coefficient-exact elimination,
and a polyhedral mixed-volume computation), all of which indicated that the full-lift path count is
enormous. We therefore treat certified absence as ARCHITECTURALLY out of reach for the global-homotopy
route on these systems -- a scoped statement about that route and budget, NOT a proof that absence is
impossible to certify by any method. A targeted per-subset absence procedure remains possible as
future work (Section 7 / future work), but is not attempted here.

## 8.2 Unresolved does not mean infeasible

Of the 3044 subsets, 2106 are unresolved with no certifier-bound candidate under the tested generator
budgets k in {6,12}. This is a statement about the REACH of the tested discovery procedure, not about
the existence of roots. Some of these subsets may well admit roots that a different generator, a
larger budget, or a different search strategy would find; indeed at least 410 of them are known to
carry near-singular candidate structure that our conditioning policy routes to a sidecar rather than
to the certifier (Section 7). The escalation curve (Section 5) shows the tested route saturating -- a
budget doubling from k=6 to k=12 added only 12 certifications -- which bounds the yield of MORE of the
SAME search, but says nothing about qualitatively different methods.

The certified count 888 is therefore a LOWER BOUND on the number of feasible subsets, under the tested
generator, budget, conditioning policy, and registered domain. It is not a claim that exactly 888
subsets are feasible.

## 8.3 The refusals are non-certifications, not negative certificates

The 50 certification refusals (Section 7) are subsets where a candidate was proposed but not
certified. In general these are non-certifications, not disproofs: the certifier could not validate a
unique root in the tested boxes, for named reasons (interval-dependency guards that never cleaned on
44 subsets, or an interval operator that split at every tested radius on 4 subsets; see Section 7,
Table A). Four candidates, across two subsets, are different: the interval operator EXCLUDES a root
within the tested certification box. These are local negatives on those specific candidates, not
subset-wide nonexistence claims. No refusal is promoted to an absence result.

## 8.4 The geometric-validity test is a specific, registered test

Layer-2 validity is the operational Gate-4/Rao test defined in Section 2, and its rejections in this
census are ORDERING/CONTAINMENT rejections -- base points driven outside the axial interval [-r, r].
The Rao-grounding claim used here is strongest for the ordering/containment component: base points
must remain within the axial interval [-r, r] (Rao eq. 2.2, and the p.226 remark on variables leaving
permitted ranges). The registered Gate-4 test also records the operational closure/constructibility
checks implemented in the pipeline. Thus "valid" throughout means "valid under the registered
Gate-4/Rao test"; it is not a claim of validity under every possible geometric, aesthetic, or
traditional convention for the Sri Yantra. The roots we report as REJECTED fail the registered test on
ordering/containment.

## 8.5 Domain restriction

All results are stated within the registered altitude domain h in (0, pi/2). Real solutions of the
constraint system with h <= 0 (super-hemispheric caps, r > pi/2) exist and are found by the search,
but lie outside the registered Meru domain and are excluded from the census (retained as a sidecar,
Section 7). The census is thus a census of the registered domain, not of the full real solution set of
the trigonometric system.

## 8.6 Reproducibility scope

The results are reproducible in the sense made precise in Section 9: deterministic seeding, a frozen
engine, an explicit radii policy, and hashed checkpoint bundles under signed tags. Reproducibility
here means byte-identical regeneration from committed source, not independence from the specific
numerical certifier; the guarantees are those of the Krawczyk interval method as applied, with the
radii and conditioning policies we registered.

---
## Notes (author; delete before submission)
- 8.1: four-method absence evidence from b1-and-absence-branch-findings.md (51faea4d). Keep the
  "architectural, not impossibility" scoping exactly. The four methods: HC.jl/MixedSubdivisions Int32
  overflow; Route A degree-box bound; Route B2 coeff-exact elimination explosion; Route B1 DEMiCs
  polyhedral MV. Confirm method names/framing against that findings doc before final.
- 8.2: 410 near-singular from the k=12 sidecar (k12-findings); 888 lower-bound framing consistent
  throughout. Escalation saturation from Section 5 Table 2.
- 8.3: exact counts from the section-7 recertify pass (0/50 convert): guard-never-clean 44,
  kraw:split 4, kraw:empty 2 subsets / 4 candidates. The "four candidates across two subsets" is the
  exact kraw:empty figure. Resolved.
- 8.4: ordering/containment scoping consistent with Section 2; Rao eq 2.2 + p.226.
- 8.5: super-hemispheric = 972 sidecar; consistent with Sections 1.4, 4, 7.
- FEEDS FROM: b1-and-absence-branch-findings.md, gate4-vs-source-finding.md, k12-findings.
