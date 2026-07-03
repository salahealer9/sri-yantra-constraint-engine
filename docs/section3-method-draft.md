# Section 3 — Certification method (draft)

The census separates PROPOSING candidate roots from CERTIFYING them. Discovery (Section 4) proposes
approximate roots by numerical search; certification decides, rigorously and independently, whether a
proposed point encloses a true, locally-unique root of the six-constraint system. This section
describes the certifier; it is a single frozen component, unchanged across all tiers.

## 3.1 From a numerical candidate to a certified root

A candidate is a point in the six variables at which the six constraint residuals are numerically
small. Certification must answer a stronger question: does a small box around (a refinement of) that
point provably contain exactly one real root? We answer it with an interval Newton / Krawczyk test.

Given a candidate, the certifier first refines it by a real Newton iteration on the six-by-six system
(all six variables free, including the altitude h), producing a polished point at which the residual
is at the level of machine precision. It then forms an axis-aligned box about the polished point and
applies the Krawczyk operator to that box. If the Krawczyk image is contained in the interior of the
box, the operator certifies that the box contains a unique real root of the system: the candidate is
certified as a locally unique real root. If the test is
inconclusive at a given box size, a smaller box is tried; if no tested box yields a conclusive
verification, the candidate is not certified (Section 7).

## 3.2 The interval-radius policy

The Krawczyk test is applied over a registered list of box radii,

    [3e-3, 1e-3, 3e-4, 1e-4, 3e-5, 1e-5, 3e-6, 1e-6, 3e-7, 1e-7],

tried in order; the certifier returns on the first radius that verifies uniqueness, and records the
radius used with each certified root. The list is passed to the certifier explicitly as a pipeline
parameter; the certifier engine itself is never modified.

The reach down to very small radii is not cosmetic. Affine-arithmetic bounding of the Jacobian range
over a box overestimates that range, and the overestimate grows with box size; at a too-large radius
floor the overestimate can defeat the uniqueness test for a genuine, well-conditioned root. Shrinking
the box removes the overestimate without changing the root -- the local conditioning is identical
across radii, only the box changes -- so a smaller registered radius recovers certifications that a
coarser floor would miss. A dedicated re-certification pass over previously-refused candidates, using
the extended radii, recovered a substantial number of genuine roots on exactly this mechanism
(Section 4).

## 3.3 Conditioning policy and the candidate stream

Not every numerically-converged candidate is a good target for interval certification. Candidates at
which the Jacobian is extremely ill-conditioned are, empirically, never certified: across the
diagnostic sample, no candidate with Jacobian condition number above roughly 1e6 was ever certified.
To keep the certifier's work bounded and its input stream meaningful, we declare a conditioning cutoff
COND_MAX = 1e8: candidates with condition number above the cutoff are routed to an audit sidecar
rather than to the certifier (Section 7). The cutoff is set two orders of magnitude above the highest
condition number at which any certification has been observed, so it is conservative -- it excludes
only candidates far beyond the observed certifiable range -- and the excluded candidates are retained,
not discarded.

## 3.4 Distinct roots and multiplicity

A single subset may yield several certified candidates. To count DISTINCT roots we collapse certified
candidates by their validated enclosures: two certified boxes that overlap are treated as the same
root; boxes that are provably disjoint are treated as distinct roots. The resulting per-subset count
is therefore a rigorous lower bound on the number of roots, and it is this collapsed count that
underlies the multiplicity figures of Section 6.

## 3.5 What the certifier does and does not decide

The certifier decides Layer 1 only: presence and local uniqueness of a real root in the registered
domain. It does not decide Layer-2 geometric validity; the Gate-4/Rao tag (Section 2) is computed separately
and attached as metadata, and never affects whether a root is certified. The frozen certifier is
identified by a fixed engine hash and is byte-identical across every tier and checkpoint reported
here, so a certification is reproducible from the subset, candidate, frozen engine, registered domain, and
recorded radius.

---
## Notes (author; delete before submission)
- 3.1: prose says "certified as a locally unique real root"; the pipeline status name
  CERTIFIED_UNIQUE_GEOMETRIC is kept for the methods appendix / code table (the word "geometric"
  there is a pipeline label, NOT Layer-2 geometric validity -- avoid it in prose to prevent
  confusion with Section 2). real Newton = certify_2b_general._real_newton (6x6, h free); "2b
  coordinate transform" (uv=[b,h+c,h+d,e,g,h]) -> appendix per venue detail tolerance.
- 3.2: radii list verbatim from the registered policy; AA-overestimation mechanism from
  refusal-structure-finding.md / r2-findings. R2 recovered 40 on this mechanism (state in Section 4).
- 3.3: "no candidate above ~1e6 certified" = the 0/294 diagnostic figure; COND_MAX=1e8 the declared
  cutoff. Keep the 1e6-observed / 1e8-cutoff distinction (per the section-7 wording fix).
- 3.4: disjoint-box collapse = collapse_certified; the distinct-root method underlying 968 and the 77
  multi-root subsets.
- 3.5: engine hash de64edfa4979 (short); full SHA-256 in Section 9.
- FEEDS FROM: certify_2b-findings.md, refusal-structure-finding.md (d972c657), r2-findings (3714a543).
