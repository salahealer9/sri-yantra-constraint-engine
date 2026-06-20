# Pre-registration — Altitude-resolved classification of the well-posed subsets of the Rao (1998) Śrīyantra constraint system on the sphere

- **Author:** Salah-Eddin Gherbi, Independent Researcher, [ORCID: 0009-0005-4017-1095](https://orcid.org/0009-0005-4017-1095)
- **Date of registration:** 2026-06-21
- **This document (version DOI):** [10.5281/zenodo.20778921](https://doi.org/10.5281/zenodo.20778921)
- **Companion registration:** Plane census pre-registration, [10.5281/zenodo.20630790](https://doi.org/10.5281/zenodo.20630790). This document mirrors its structure section-for-section so the two censuses are directly comparable; the differences are the **spherical amendments**, flagged inline.
- **Frozen engine under test:** the spherical engine `sriyantra.py`, the spherical Gate-4 validity constructor `spherical_geo_check.py`, and the existence-interval mapper `spherical_existence_mapper.py`, to be released and hash-pinned before the confirmatory run. The spherical→plane **bridge result** is archived at [10.5281/zenodo.20772247](https://doi.org/10.5281/zenodo.20772247).
- **Type:** Confirmatory enumeration study. Pre-registered before any well-posed subset is classified under the registered altitude-resolved procedure beyond the exploratory probes that motivated it.

---

## Principal amendment relative to the plane census

The plane census classified each well-posed subset as a binary outcome —
*feasible / infeasible* — for an isolated figure at fixed r ≡ 1. The exploratory
phase (Stages 0–3) established that on the sphere **altitude h is a continuous
variable that behaves as a bifurcation parameter**: the natural object is not a
point but a one-parameter family with an *altitude existence interval*, and a
subset's status can change with h through folds, ordering failures, point
collisions, and domain limits. The principal amendment is therefore to reframe
the spherical census from *exists / does not exist* to **for which altitudes, and
in what existence sense, does a valid figure exist** — studied on the **same 815
subsets** as the plane census so the two are directly comparable.

(The companion plane registration scoped the spherical form as the 3044 determined
six-constraint systems. Those isolated figures are recovered here as the
intersections of the size-five family branches with a fourth chosen constraint;
their enumeration is a **derived secondary study, deferred** until the family-level
altitude structure registered here is mapped.)

## Lessons learned from exploratory reconnaissance (audit trail)

Every amendment below traces to a concrete failure mode the exploratory phase
exposed *before* the census — the same discipline the plane project learned from
its isotropic-box issue. The amendments are decision rules; they do not depend on
whether any exploratory count was correct.

| Amendment | Concrete failure mode it exists to prevent |
| --- | --- |
| Degree-normalized solving (Gate 5) | observed κ(J) ∝ 1/α near the pole |
| Pseudo-arclength continuation (§6) | natural-parameter continuation failed at folds and near the pole |
| Gate-4 validity constructor (Gate 4) | algebraic roots are not realizable figures |
| Altitude existence intervals (§7–§8) | existence is not binary; it changes with altitude |
| Pole-domain stop condition (Gate 6) | protect the certified plane census from silent contradiction |

## 1. Scope

This pre-registration covers the **altitude-resolved enumeration and
classification** of the size-five constraint subsets ({F₁,F₂} + 3 of the
remaining eighteen) of Rao's (1998) formulation, studied as one-parameter
spherical families in altitude h. **Optimisation** — any search for a "best" or
"closest-to-tradition" figure — is explicitly **excluded** and deferred, as in the
plane registration. The determined six-constraint spherical enumeration is likewise
deferred (see Principal amendment).

## 2. Confirmatory research question

> What is the complete altitude-resolved classification, under the pre-registered
> normalized solver, pseudo-arclength continuation, Gate-4 validity, and
> boundary-typing procedures, of all well-posed subsets of the Śrīyantra constraint
> system — with respect to algebraic existence, Gate-4-valid existence, the altitude
> intervals of each, and the boundary mechanism that terminates each interval?

The confirmatory deliverable is **the altitude-resolved classification map and its
direct tabulated outputs** (§11) — not any count of curvature-confined figures, nor
any claim that the landscape exhibits structure, nor that constraints F₇ or F₈ are
privileged. Those are properties of results not yet completely observed and are
exploratory by construction (§3).

## 3. Confirmatory / exploratory demarcation

**Confirmatory outputs** (direct products of the registered procedure):
- The five-way classification (§8) of every well-posed subset.
- The **algebraic existence interval** and the **Gate-4-valid existence interval**
  per subset (§7).
- The boundary mechanism terminating each interval endpoint (§7).
- Fold presence per family (pseudo-arclength branch reversal).
- The pole-domain (census-integrity) status per subset (Gate 6).
- The α→0 consistency check against the certified plane classification (§6).

**Exploratory outputs** (labelled as such wherever they appear; admissible as
confirmatory only via a prospective stamped amendment, §10):
- Any count of "spherical-only" or curvature-confined subsets. No count is asserted
  in this registration. Exploratory probing identified examples of curvature-confined
  valid figures, which motivated including SPHERICAL_ONLY as a pre-registered
  classification category (§8); the count is an output of the registered procedure,
  never an input to it.
- Families, clusters, or symmetry classes.
- Over-representation of particular constraints (the F₇/F₈ hypotheses, §9).
- Relationships to historical specimens, density in parameter space, any privileged
  "number of distinct spherical Śrīyantras."

## 4. Materials and enumeration scope

The frozen engine provides: the validated spherical engine (`sriyantra.py`,
cross-checked against Rao's Table 1), the independent **spherical Gate-4 coordinate
constructor** (`spherical_geo_check.py`, a great-circle realization agreeing with
the engine's chain to ~10⁻¹⁵ and independently flagging Rao's one under-converged
table row), and the **existence-interval mapper** (`spherical_existence_mapper.py`,
pseudo-arclength branch tracer). F₁ (concurrency) and F₂ (concentricity) are
essential in every subset.

- **Subject universe (this registration):** the **815 well-posed size-five
  subsets** ({F₁,F₂} + 3 of {F₃,…,F₂₀}); of the C(18,3)=816 systems, one
  ({1,2,8,9,16}) is certified rank-deficient. Studied as families in
  h ∈ (0, π/2), with curvature scale α = π/2 − h.
- **Established foundation (not re-derived here).** The spherical→plane reduction
  law Gᵢ(α) = α^{dᵢ}·Fᵢ + O(α^{dᵢ+2}) (bridge deposit) and its computational
  corollary κ(J) ∝ 1/α, removed exactly by degree-normalization. These are the
  basis for the normalized-solver rule (Gate 5).

**Pre-census action item (resolved).** The single subset labelled ALGEBRAIC_EMPTY
by the exploratory mapper — (1,2,7,12,17) — was investigated and is **not**
algebraically empty: aggressive seeding finds roots and Gate-4-valid figures at
multiple altitudes. The label was a **seeding artifact** — the subset shares ≤ 3
constraints with every plane survivor, so it received no warm start, and the random
seeding missed a small basin. Two decision rules follow: (i) the registered seeding
budget includes a **warm-start fallback** for subsets with no constraint-sharing
survivor; (ii) the figures found are **near-degenerate** (two intercepts collapsing
toward zero on a high-symmetry locus), which motivates the near-degeneracy floor in
Gate 4. Consequently ALGEBRAIC_EMPTY may not occur for any subset (cf. H3, §9).

## 5. Validation criteria (outcome-neutral gates)

Conditions under which the experiment is *trustworthy*; not outcomes. Any failure
triggers **halt-and-diagnose**, never a revision of results. All gates run against
the hash-pinned engine.

**Gate 1 — Degeneracy consistency.** The certified rank-deficient subset must not
return a solution isolated by *both* a full-rank Jacobian (σ-ratio ≥ 10⁻⁷) and the
absence of a nearby continuum.

**Gate 2 — Constraint-residual consistency.** At every accepted solution, all
imposed **normalized** constraints satisfy |F̃ᵢ| ≤ 10⁻⁶, and both exact radial
identities hold: |F₈ − F₉ + F₁₆| < 10⁻⁶ and |F₁₆ − F₁₇ − F₁₈ + F₁₉| < 10⁻⁶.

**Gate 2b — Independent-coordinate consistency.** The spherical Gate-4 constructor
is an independent implementation path. At every accepted solution the
coordinate-grounded quantities (r₁₆…r₁₉, x₁₆…x₁₉, base-point feet) recomputed
through the constructor must agree with the engine chain to ≤ 10⁻⁹ (demonstrated
~10⁻¹⁵). This is the standing guard on the geometry.

**Gate 3 — Historical reproduction.** Before enumeration, the engine must reproduce
Rao's Table 1 to ~10⁻⁷, and the Gate-4 constructor must validate 7 of the 8 rows,
flagging only the documented under-converged row (1,2,3,6,16,19) for the correct
reason (non-closure).

**Gate 4 — Geometric validity.** A converged solution is a **valid figure** only if
the spherical constructor yields a non-degenerate realization: base-point ordering
along the axis preserved, every pair of points required distinct separated by
> 10⁻⁶ · r, the figure closes (point 11 coincides with 11a within the solver
floor), and **no near-degeneracy** — every basic intercept (b,c,d,e,g) and every
required separation exceeds a registered floor τ_deg · r (τ_deg = 10⁻³). Figures
with a quantity between 10⁻⁶·r and τ_deg·r (geometric near-collapses such as the
(1,2,7,12,17) symmetric locus) pass distinctness but are flagged **near-degenerate**
and reported separately; distinct-figure counts (§7) are reported both including and
excluding them. A solution failing Gate 4 is recorded as an algebraic solution but
**not** a valid figure.

**Gate 5 — Conditioning / normalization (spherical amendment).** All solving,
continuation, and residual evaluation are performed on the **degree-normalized
constraints F̃ᵢ = Fᵢ/α^{dᵢ}** (dᵢ = 2 for {F₃,F₄,F₆}, else 1). The normalized
Jacobian condition number must remain O(10) across the altitude range (verified
against the raw 1/α blow-up). Continuation uses **pseudo-arclength** (robust through
folds and near-pole conditioning); natural-parameter continuation is not used for
interval endpoints.

**Gate 6 — Pole-domain consistency (pre-registered STOP condition; spherical
amendment).** This gate is a **consistency theorem between the two censuses**, not
merely a validation check. As the registered stop condition:

> If any plane-certified-infeasible subset develops a Gate-4-valid branch whose α→0
> (pole) limit lies inside the registered plane domain B, the spherical census
> **HALTS GLOBALLY** and the plane census is re-opened for re-examination.

Such a figure would be a valid in-domain plane figure for a subset the plane census
certified to have none — a contradiction the two results cannot both survive. The
halt is mandatory and stops the entire run, not just the offending subset. For the
134 plane-**feasible** subsets an in-box pole limit is the *expected*
bridge-consistency outcome (class PLANE_CONTINUATION, §8), not a halt. The
exploratory probe observed **zero** in-box limits among 261 pole-reaching infeasible
branches; this gate makes that a permanent precondition of trust rather than a past
observation.

## 6. Methods

**Tier 1 (primary) — normalized multistart Newton over an altitude grid.** For each
subset, seeds are drawn over an altitude grid (h ∈ {≈16°…80°}) from an axis-aligned
box derived from Rao's tables widened 50 % and intersected with the valid domain
(positivity; g < c; b+c < r; d+e < r; chain-defined arc arguments), plus warm
starts scaled from constraint-sharing plane survivors; **subsets with no
constraint-sharing survivor receive a registered warm-start fallback** (a denser
random budget plus seeds scaled from the nearest survivors by constraint overlap),
so seeding coverage does not depend on survivor adjacency. The RNG seed is fixed and
reported. Convergence floor |F̃ᵢ| ≤ 10⁻⁶, reported with all results. Tier 1 yields
*figure found / not found at the grid altitudes*; **a Tier-1 negative is never
reported as infeasibility at all altitudes.**

**Branch completeness — pseudo-arclength existence-interval mapping.** From any
seed on a subset's branch, the branch is traced in both directions through folds and
conditioning trouble until it ends at the pole, a constructibility boundary, or a
stall. Along the branch, algebraic existence (a root) and Gate-4 validity are
recorded per altitude, yielding the two existence intervals (§7) and the boundary
mechanisms. This replaces the plane Tier-2 homotopy as the completeness instrument
for the altitude structure; spherical completeness over **all** altitudes is
transcendental and is reported as best-effort, never as a proof of non-existence
outside the traced range.

**α→0 consistency (bridge gate).** Each subset's classification must be consistent
with its certified plane classification in the limit h → π/2: plane survivors'
valid branches must reach an in-box pole limit; plane-infeasible subsets must not
(Gate 6). Disagreement is halt-and-diagnose.

## 7. Existence intervals, equivalence, and distinct-figure counting

**Three existence intervals (spherical amendment).** Per subset:
- **Algebraic existence interval** — the h-range over which the traced branch
  carries a root.
- **Constructible existence interval** — the h-range over which the figure
  realizes (chain defined, all intersections exist). On the branch this coincides
  with the algebraic interval (a root cannot be solved where the chain is
  undefined); it is reported separately only where they differ.
- **Gate-4-valid existence interval** — the h-sub-range where the realized figure
  passes Gate 4.

The robust nesting is **algebraic (≡ constructible on-branch) ⊇ Gate-4-valid**.

**Boundary mechanism (registered vocabulary).** Each interval endpoint is typed as
exactly one of: **ordering** (base-point ordering failure), **collision**
(point-separation → 0 / vanishing triangle), **closure** (figure fails to close),
**fold** (pseudo-arclength turning point), **constructibility** (chain becomes
undefined), **pole** (branch reaches h → π/2), or **pole-domain** (pole reached with
out-of-box limit).

**Equivalence and distinct-figure counting.** Figure equivalence is defined on the
constructed coordinate vector exactly as in the plane registration (max
point-to-point geodesic distance over the fixed point set, canonical constructor
order, r-normalized), **evaluated at a fixed reference altitude** stated per report;
distinct-figure counts are reported as a function of altitude and of the tolerance
τ ∈ {10⁻²,10⁻³,10⁻⁴,10⁻⁵}. **No single count is privileged**, and counts below the
realized coordinate floor are flagged as noise-limited.

## 8. Classification scheme — algorithmic decision procedure (spherical amendment)

The class is a **deterministic function** of the traced branch set and the
registered predicates; a reader determines a subset's class without interpretation.

Predicates. **ROOT** — a root is present (true along a traced branch); **VALID** —
passes Gate 4, including the near-degeneracy floor; **POLE** — h ≥ π/2 − δ
(δ = 1°, registered); **INBOX** — the α→0 limit p = lim(x/α) lies in the registered
plane domain B; **PLANE_FEASIBLE** — the subset's certified plane status.

Apply in order; the **first** matching rule assigns the class:

1. No ROOT at any altitude under the registered seeding-and-tracing budget
   → **ALGEBRAIC_EMPTY**.
2. Else no traced point is VALID at any altitude → **ALGEBRAIC_ONLY**.
3. Else (some VALID figure exists); examine the VALID points that satisfy POLE:
   - **(3a)** none — every VALID interval caps below π/2 − δ → **SPHERICAL_ONLY**
     (curvature-confined; recorded with valid interval, fold flag, boundary mechanism).
   - **(3b)** some VALID point has POLE; take its limit p:
     - p ∉ B → **POLE_OUT_OF_DOMAIN**.
     - p ∈ B and PLANE_FEASIBLE → **PLANE_CONTINUATION** (the certified plane figure
       is the α→0 limit; bridge-consistent).
     - p ∈ B and ¬PLANE_FEASIBLE → **HALT (PLANE_INCONSISTENCY)** — the Gate-6 global
       stop condition; the run halts and the plane census is re-examined.

Roll-up for plane comparison: **NO_VALID** := ALGEBRAIC_EMPTY ∪ ALGEBRAIC_ONLY. The
scheme reduces to the plane binary at the pole — PLANE_CONTINUATION ↔ plane-feasible,
and {NO_VALID, SPHERICAL_ONLY, POLE_OUT_OF_DOMAIN} ↔ plane-infeasible — while
carrying the altitude structure the plane census could not see.

## 9. Pre-registered exploratory hypotheses

Filed as exploratory questions, **not findings**; confirmatory testing of any of
them requires a stamped amendment specifying the test in advance (§10).

- **H1.** Among SPHERICAL_ONLY (curvature-confined) subsets, constraint **F₇** is
  over-represented relative to its base rate.
- **H2.** Among fold-containing families, constraint **F₈** is over-represented.
- **H3.** Algebraic emptiness may not occur at all: most or all exclusions arise
  from validity, ordering, collision, domain, or branch structure rather than from
  the absence of roots. (The single exploratory ALGEBRAIC_EMPTY case proved to be a
  seeding artifact, §4; the hypothesis is that no subset is genuinely root-free
  across altitude.)

## 10. Amendment protocol

Amendments are filed as `prereg/spherical-amendment-NN.md`, committed, GPG-signed,
and OpenTimestamps-stamped — provably dated before any analysis they license. **No
retroactive reclassification.** A genuinely unanticipated finding is reported as
exploratory; any confirmatory claim about it requires a stamped amendment filed
before the corresponding analysis.

## 11. Reporting schema

For each well-posed subset, the deposited outputs record:

| Subset | Class (§8) | Algebraic interval | Gate-4-valid interval | Fold | Boundary mechanism(s) | Pole-domain status | Completeness |
| --- | --- | --- | --- | --- | --- | --- | --- |

Notes column records halt-and-diagnose events, Gate-4 rejections, near-zero-width
(tangency) valid intervals, and α→0 consistency outcomes. **Every traced branch and
every individual solution** is retained in the machine-readable deposit, with the
fixed RNG seed, the solver convergence floor, the realized coordinate spread, and
the pseudo-arclength step record.

## 12. Deposit and reproducibility

The analysis code (the normalized solver, the pseudo-arclength existence-interval
mapper, the spherical Gate-4 constructor, and the gate harness) is released and
hash-pinned **before** the confirmatory run at the following blob hashes:

- `sriyantra.py`: `13a7fe2c3e42f0460a74eb592ba9f1f8ad1fbdc4`
- `enumeration/spherical_geo_check.py`: `3d7b9384bb6f121d24e457e8abdc0330bf26a34b`
- `enumeration/spherical_existence_mapper.py`: `fd553d088a14ceadf663b1880aabcb979db82d7d`

This pre-registration references the bridge deposit by its DOI and the engine by
its frozen hash. Results, this protocol, and any amendments are deposited with GPG
signatures and OpenTimestamps stamps under the project's concept DOI,
cross-referenced to the plane registration for direct comparability.

## Reference

Rao, C. S. (1998). Śrīyantra — A Study of Spherical and Plane Forms. *Indian
Journal of History of Science*, 33(3), 203–227.
