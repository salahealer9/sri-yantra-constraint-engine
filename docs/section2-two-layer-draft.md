# Section 2 — Two layers: constraint-root versus Rao-valid figure (draft)

## 2.1 The distinction

A subset of six constraints defines a system of six equations in the six basic variables. A solution
of that system -- a point at which all six constraint functions vanish -- is what we call a
CONSTRAINT-ROOT. Certifying constraint-roots is a purely algebraic task: does the system have a real
solution, and can its existence and local uniqueness be validated rigorously? This is Layer 1.

Whether such a root corresponds to a correctly-drawable Sri Yantra figure is a separate question. Not
every real solution of the six equations is a geometrically valid figure: the construction can place
a base point outside the circum-circle, or order the base points wrongly along the axis, producing a
solution that satisfies the equations but does not draw a legitimate figure. Testing geometric
validity is Layer 2.

We keep these layers strictly separate. Layer 1 (certification) is decided by interval validation and
is never overridden. Layer 2 (geometric validity) is recorded as METADATA attached to each certified
root; it never relabels, filters, or vetoes a certification. A root can be certified (Layer 1) and
geometrically rejected (Layer 2) at the same time, and such roots are first-class members of the
census.

## 2.2 The geometric-validity test and its grounding in Rao

Our operational Layer-2 test is the base-point ordering/containment condition. Recall from Section 1
that Rao's construction (eq. 2.2) fixes the outer intercepts as a = r - (b+c) and f = r - (d+e), and
places all base points within the axial interval [-r, r]. Geometric validity in this component
requires the base points to remain correctly ordered inside that interval -- equivalently, the outer
segments a and f to remain non-negative. A certified root with b + c > r (so a < 0) or d + e > r (so
f < 0) pushes a base point outside the circum-circle: it is an algebraically real constraint-root that
is not Rao-valid under the registered validity test.

This condition is not an artifact of our pipeline; its ordering/containment component is grounded in
Rao's own construction. Equation 2.2 is Rao's identity, and Rao (1998, p. 226) explicitly reports
that incompatible constraint sets can drive variables outside their permitted ranges during solution
-- precisely the phenomenon of an algebraically-real root that is not a valid figure. We therefore
treat base-point containment/ordering as a faithful encoding of a Rao-validity condition, not a
stricter convention imposed from outside. (The full geometric-validity notion also includes
constructibility and figure-closure checks; the rejections reported in this census are
ordering/containment rejections. This scoping is revisited in Section 8.)

## 2.3 Why the layers cannot be collapsed: validity is per-root

The separation is not merely methodological caution; it is forced by the data. Geometric validity is
a property of a ROOT, not of a subset. The same six-constraint subset can admit more than one
certified root, and those roots can differ in geometric-validity status: one a valid figure, another
an algebraically-real but geometrically-rejected solution. In the final census (Section 6) this occurs
for 26 subsets, which carry both a valid and a rejected certified root simultaneously. A concrete
example is the subset (1,2,3,4,6,13): it admits both a geometrically rejected certified root and a
geometrically valid certified root.

Consequently, any tagging scheme that assigns a single validity label to a subset is not merely
lossy but incorrect: it cannot represent a subset that realizes figures of both statuses. Validity
must be attached per-root, as metadata on the certified solution, which is exactly the two-layer
structure adopted here.

## 2.4 A consequence for candidate discovery

Because a decisive component of Rao-validity is a containment condition, a candidate generator that enforces
containment at the SEEDING stage -- as geometry-first constructors naturally do -- can only ever
propose candidates in the valid region, and will structurally miss the algebraically-real,
geometrically-rejected roots. A census that intends to enumerate ALL certified constraint-roots (Layer
1) must therefore use a discovery procedure that is neutral with respect to Layer-2 validity: it must
be free to seed the containment-violating region. This requirement shapes the generator described in
Section 4, and is validated there by roots found ONLY in the containment-violating stratum.

---
## Notes (author; delete before submission)
- 2.2: eq 2.2 and the p.226 "outside permitted ranges" remark are the grounding; cite Rao pages.
  Keep the "ordering/containment COMPONENT" scoping (not all of Gate-4) consistent with Section 8.
- 2.3: 26 both-type verified from CENSUS_CHECKPOINT_LAYER1_K12 (root['gate4']['valid'] schema path).
  (1,2,3,4,6,13) anchor: uses verified-only phrasing (both types present); no dependence on root
  ordering/provenance. Both-type status confirmed from CENSUS_CHECKPOINT_LAYER1_K12.
- 2.4: forward-ref to Section 4 (viol stratum) and Section 6 (viol-only certified counts). The
  "structurally misses" claim is the retired-mapper finding; keep it scoped to seed-stage containment.
- FEEDS FROM: gate4-two-layer-findings.md, gate4-vs-source-finding.md (bfa9bf79).
