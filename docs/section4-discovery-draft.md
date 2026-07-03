# Section 4 — Candidate discovery (draft)

Certification (Section 3) decides which candidates are roots, but it must be given candidates.
Discovery is the complementary task: proposing approximate roots for each subset. Discovery only ever
PROPOSES; it never certifies, and it never writes a feasibility label. This separation -- discovery
proposes, the certifier decides, the census records -- is maintained throughout, so that no property
of the search can inflate the certified count.

We used a sequence of discovery tiers of increasing cost, each feeding the same certifier.

## 4.1 Warm-start transfer

The first tier seeds Newton from roots already known: the benchmark configuration, the figures
tabulated by Rao, and -- as the census grew -- previously certified roots, transferred as seeds to
neighbouring subsets. This is cheap and certifies subsets clustered near known figures, but its reach
is limited: successive transfer rounds showed sharply diminishing returns (each round adding fewer new
certifications than the last), because a known root only seeds subsets in its immediate basin. Warm
start certified 26 subsets and then saturated.

## 4.2 A validity-neutral domain-wide generator

To reach subsets far from any known root, the second tier abandons warm starts and searches the whole
registered domain by multistart. Its design is governed by the per-root observation of Section 2: a
generator that enforces the containment condition at the seeding stage can only propose candidates in
the geometrically-valid region and will structurally miss the rejected roots. To enumerate ALL
certified constraint-roots, the generator must be NEUTRAL with respect to Layer-2 validity.

Concretely, the generator seeds across the registered domain in several strata -- a bounded box
region, a broad log-uniform spread, a near-degenerate-locus stratum, and, crucially, a
CONTAINMENT-VIOLATING stratum that deliberately seeds the region where b + c > r or d + e > r. It
applies NO ordering or containment filter at the seeding stage; the only filters are domain-hygiene
conditions (positive coordinates within the domain, a minimum circum-radius, and single-intercept
domain sanity checks that do NOT enforce the composite containment conditions b+c <= r or d+e <= r).
These exclude degenerate non-candidates, not geometrically-rejected roots; the containment condition
whose violation defines a rejected root is left entirely free at the seeding stage. Every converged candidate is passed to the certifier, which decides; the Gate-4 tag is attached
afterward as metadata.

Seeding is deterministic: each subset's seeds derive from a fixed global seed by a per-subset hash, so
the entire candidate set regenerates byte-identically. This tier produced the bulk of the census,
certifying 810 subsets beyond the warm-start 26.

The neutral design is vindicated directly by the results: a number of certified roots -- including
geometrically-rejected ones -- were found ONLY in the containment-violating stratum, i.e. by
candidates that a containment-enforcing generator would never have proposed (Section 6). This is the
concrete payoff of validity-neutral discovery.

A note on a superseded instrument: an existing geometry-first construction routine, which solves for a
figure at a fixed altitude, cannot serve as the census generator -- on a six-constraint subset it
solves a five-variable system at fixed altitude and its Jacobian is structurally rank-deficient for
the six-variable problem, so it does not converge from generic seeds. It remains valid for its
original fixed-altitude purpose but is not used as a census candidate source.

## 4.3 Extended-radius re-certification

The third tier changes not the candidates but the certification radii. As explained in Section 3.2, a
too-coarse radius floor leaves genuine, well-conditioned roots uncertified through affine-arithmetic
overestimation. Re-certifying the previously-refused candidates over the extended radii list recovered
40 further subsets, each certifying at a radius below the former floor, with the root itself unchanged.
This tier adds no new search; it corrects a certification-parameter deficiency, transparently, with
the radius used recorded per root.

## 4.4 Pre-registered budget escalation

The final tier increases the multistart budget on the still-unreached subsets. The budget parameter
is k, escalated as k=6 -> 12 -> 24. Because the higher-budget seed set contains the lower-budget one, and the escalation targets only subsets with no prior
candidate, every new certification is genuine incremental yield. We fixed a stopping rule BEFORE
running: escalate the per-subset budget by doublings, and stop when a doubling yields fewer than
twenty-five new certified subsets. Doubling the budget added twelve new certifications -- below the
threshold -- so the rule terminated escalation, and the next doubling was not run. The escalation
curve is thus closed by a criterion fixed in advance, not by exhaustion of patience.

## 4.5 The domain audit

Across all search tiers, candidates that converge outside the registered altitude domain (h <= 0,
super-hemispheric caps with r > pi/2) are real solutions of the trigonometric system but lie outside
the registered scope. A domain-audit stage detects and excludes them, routing them to a sidecar
(Section 7); they are not counted in the census. (The audit's discovery and the enforcement that
closed it are described in the reproducibility appendix.)

---
## Notes (author; delete before submission)
- 4.1: warm-start 26; diminishing returns (14 -> 4 across transfer rounds) from the discovery findings.
- 4.2: 810 = layer1-new (verified: 836 = 26 + 810). Strata: box/logwide/neardeg/viol. Deterministic
  blake2b seeding. "structurally rank-deficient" = the retired find_seed/L.newton finding (6x5
  Jacobian). Keep scoped: it's a fixed-altitude 5-var solver, valid for its own purpose.
- 4.3: R2 +40; AA-overestimation; radius_used recorded. Ties to Section 3.2.
- 4.4: pre-registered N<25; k=12 gave 12; k=24 not run. Curve: 26 -> 836 -> 876 -> 888 (Section 5).
  "doublings" phrasing: the budget parameter is k (6 -> 12 -> 24); state k explicitly if the venue
  wants the concrete parameter, or keep "doublings" for readability.
- 4.5: super-hemispheric = 972 sidecar; full incident (impossible displacement) -> appendix per skeleton.
- FEEDS FROM: gate4-two-layer-findings.md, layer1-full-census-finding.md (45cfe0db),
  refusal-structure-finding.md, r2-findings (3714a543), k12-findings (cb159549),
  k-escalation-preregistration.md (60b4c296).
