# Gate-4's base-point ORDERING COMPONENT is a genuine Rao-validity condition (confirmed vs Rao 1998)

## Source
C.S. Rao (1998), "Sriyantra - A Study of Spherical and Plane Forms", Indian J. History of Science,
33(3), pp. 203-227. Key references below: eq (2.2) p.209; construction pp.209-213; Table 1 p.218;
Conclusions p.226.

## The question
Is Gate-4's base-point ordering ([-r,-(b+c),-c,-g,0,d,d+e,r] strictly increasing, all within
(-r,r)) a genuine validity requirement of Rao's formulation, or a stricter mapper-internal
convention? -> Needed to interpret the 4 Gate-4-rejected certified roots.

## Direct evidence from Rao (1998) -- answer: GENUINE Rao condition
1. Eq (2.2), p.209:  r = a + b + c = d + e + f = pi/2 - h.
   The intercepts sum to r on EACH side of the centre P_c along the axis of symmetry. So by
   construction every base point lies within [-r, +r]:
       P1 = -(a+b+c) = -r ... P_c = 0 ... P10 = +(d+e+f) = +r.
   Equivalently, in the intercept variables a = r-(b+c) and f = r-(d+e): ordering/containment is
   exactly requiring these OUTER SEGMENTS to remain POSITIVE. A certified root with b+c > r (or
   d+e > r) makes a < 0 (or f < 0): base point P1 = -(b+c) falls BEYOND -r (or P9 = d+e beyond +r),
   OUTSIDE the bounding circle. This is Rao's own coordinate identity (2.2), not a mapper choice.
2. Conclusions, p.226 (paraphrased): Rao reports that for SOME constraint sets the conditions were
   incompatible, shown by variables reaching values outside the permitted ranges during program
   execution. (A GENERAL remark, not about specific subsets.) That is precisely the phenomenon of an 
   algebraically-real root that is not a valid figure -- i.e., our Gate-4-rejected roots.
3. Construction (pp.209-213): the base points P1..P9 are located by intercepts b,c,d,e,g (and
   derived v8,v9,U7,...) measured from P_c within [-r,r]; the whole triangle complex is inscribed
   in the circum-circle of angular radius r. Points lying outside r are not constructible.

## Conclusion (now a Rao-grounded statement, not just Huet-grounded)
The 4 Gate-4-rejected certified roots -- (1,2,3,4,6,7)[benchmark], (1,2,3,4,6,13), (1,2,3,6,7,13),
(1,2,4,6,7,13), all with b+c>r and/or d+e>r -- are algebraically-real roots of the constraint
subsystem but are GEOMETRICALLY INVALID under Rao's OWN formulation (a base point falls outside the
[-r,r] axis interval / bounding circle). This matches Rao's explicit remark that incompatible
constraint sets drive variables outside permitted ranges. Gate-4's ORDERING/CONTAINMENT COMPONENT is 
therefore a faithful encoding of a Rao-validity condition, NOT an over-strict mapper convention. 
(Full Gate-4 also includes constructibility and figure-closure checks; those are separate. The 4 
rejected roots fail specifically on ordering/containment, which is the component confirmed here.)

Scope note (still precise): "outside permitted ranges / base point outside the circle" is the
specific invalidity. Full Gate-4 also checks figure closure; the 4 here fail on ORDERING
(containment), the primary Rao condition. No overclaim beyond this.

## Consequence for the census (two-layer, now Rao-justified)
    Layer 1: 26 certified roots of the chosen 6-constraint subsystem            (algebraic result)
    Layer 2: 22 are geometrically valid Rao figures (within [-r,r], constructible);
              4 are algebraically-real but geometrically INVALID under Rao (base point outside r).
Both true and now both grounded in Rao (1998). The benchmark is a valid CERTIFICATION target but
NOT a valid Rao figure -- consistent, and expected given Rao's own "outside permitted ranges" note.

## Interesting corroboration from Rao's tables
Rao's Table 1 (constrained spherical figures) lists 8 configurations; 7 of them are the very roots
our warm-start certified and that pass Gate-4. Rao's own tabulated figures satisfy the containment
condition -- consistent with Gate-4 being Rao's validity notion. Rao also notes (p.222) the global
optimum occurs as h -> pi/2 (r -> 0), i.e. deep in the well-contained regime.

## Files / Provenance / Copyright

**Source:** C. S. Rao (1998), "Śrīyantra — A Study of Spherical and Plane Forms," Indian Journal of 
History of Science, 33(3), 203–227. Key references: eq 2.2 (p. 209), Table 1 (p. 218), construction 
(pp. 209–213), conclusions (p. 226). PDF SHA-256 (provenance; PDF not committed — copyright): 
`0edae8770ed83b55b9c552fa27b1df0cf797529b2ea9270662593fbf7fe97ea9`

**Copyright notice:** The full Rao (1998) PDF is copyrighted and must NOT be committed to a public 
repository. This repository includes only the citation, page references, and a SHA-256 hash of the 
PDF for provenance verification. The PDF itself is kept in a private evidence bundle or local path 
only.

**Artifacts:** `gate4_census_audit.py` and `gate4_status.json` carry the per-root Layer-2 
classification results.

SHA-256 hash for this file in this unit is recorded in `docs/SHA256SUMS`