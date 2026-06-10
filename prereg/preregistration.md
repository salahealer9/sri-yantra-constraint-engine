# Pre-registration — Complete classification of the well-posed subsets of the Rao (1998) Śrīyantra constraint system

- **Author:** Salah-Eddin Gherbi, Independent Researcher, [ORCID: 0009-0005-4017-1095](https://orcid.org/0009-0005-4017-1095)
- **Date of registration:** 2026-06-10
- **This document (version DOI):** [10.5281/zenodo.20630790](https://doi.org/10.5281/zenodo.20630790)
- **Frozen engine under test:** Sri Yantra Constraint Engine v0.1.0, archived at [10.5281/zenodo.20617730](https://doi.org/10.5281/zenodo.20617730), pinned by its deposited `SHA256SUMS.txt` (GPG-signed, OpenTimestamps-stamped).
- **Type:** Confirmatory enumeration study. Pre-registered before any well-posed subset outside Rao's published tables has been solved.

---

## 1. Scope

This pre-registration covers the **enumeration and classification** of the
constraint subsets of Rao's (1998) formulation only. **Optimisation** — any
search for a "best" or "closest-to-tradition" figure under any objective — is
explicitly **excluded** and deferred to a separate pre-registration to be written
*after* the feasible landscape is known. Committing to an objective or a search
domain that does not yet exist would be vacuous; deferral is itself a safeguard.

## 2. Confirmatory research question

> What is the complete classification, under the pre-registered solver,
> validation, and equivalence procedures, of all well-posed subsets of the
> Śrīyantra constraint system with respect to numerical solvability, geometric
> feasibility, and distinct valid figures?

The confirmatory deliverable is **the classification map and its direct
tabulated outputs** — not any claim about how many distinct Śrīyantras exist, nor
any claim that the landscape exhibits structure, nor that any subset is
privileged. Those are properties of results not yet observed and are exploratory
by construction (§3).

## 3. Confirmatory / exploratory demarcation

**Confirmatory outputs** (direct products of the registered procedure):
- Classification of every well-posed subset (degenerate / no-solution-found / feasible).
- Numerical-solution count per subset.
- Valid-figure count per subset (Gate 4).
- Distinct-valid-figure counts as a function of the equivalence tolerance τ (§7).
- Dependency-lattice context (the certified degeneracy set, already established in v0.1.0).
- Completeness status per subset (Tier 1 only, or Tier 1 + Tier 2 certified).

**Exploratory outputs** (interpretations of the map; labelled as such wherever they appear, and admissible as *confirmatory* only via a prospective amendment under §8):
- Families, clusters, or symmetry classes of solutions.
- Structural regularities among feasible subsets.
- Relationships to historical specimens or traditions.
- Density of solutions in parameter space.
- Any single privileged estimate of "the number of distinct Śrīyantras."
- Any optimisation-derived notion of "best" or "closest."

## 4. Materials and enumeration scope

The frozen v0.1.0 engine provides: a spherical engine and a plane engine (each
validated against Rao's Tables 1 and 3), an independent coordinate constructor,
and the certified constraint-dependency lattice. F₁ (concurrency) and F₂
(concentricity) are imposed as essential in every subset.

- **Plane form** (5 variables b,c,d,e,g; r ≡ 1): choose 3 of the 18 non-essential
  constraints {F₃,…,F₂₀}. Of the C(18,3)=816 systems, **1** is certified
  rank-deficient ({1,2,8,9,16}); **815** are well-posed and in scope.
- **Spherical form** (6 variables b,c,d,e,g,h): choose 4 of 18. Of the
  C(18,4)=3060 systems, **16** are certified rank-deficient; **3044** are
  well-posed and in scope.

## 5. Validation criteria (outcome-neutral gates)

These are conditions under which the experiment is considered *trustworthy*; they
are **not** experimental outcomes. Failure of any gate triggers
**halt-and-diagnose**, never a revision of results. All gates run against the
hash-pinned v0.1.0 engine; any change to the engine invalidates prior gate
passes.

**Gate 1 — Degeneracy consistency.** The certified rank-deficient subsets (1
plane, 16 spherical) must not produce a numerically isolated solution. A returned
point is *isolated* only if its system Jacobian is full rank (smallest-to-largest
singular-value ratio ≥ 10⁻⁷) **and** no connected solution continuum is detected
near it. A degenerate subset **passes** the gate if *either* a rank-deficient
Jacobian (ratio < 10⁻⁷) *or* a solution continuum is observed; it **fails**
(halt) only if a solution isolated by **both** criteria is returned.

**Gate 2 — Constraint-residual consistency.** At every accepted solution, all
imposed constraints satisfy |Fᵢ| ≤ 10⁻⁶, and both exact radial identities hold:
|F₈ − F₉ + F₁₆| < 10⁻⁶ and |F₁₆ − F₁₇ − F₁₈ + F₁₉| < 10⁻⁶.

**Gate 2b — Independent-coordinate consistency.** The coordinate constructor is
treated as an **independent implementation path**, not a second evaluation of the
same code. At every accepted solution, the coordinate-grounded constraints
(F₇, F₁₁, F₁₂, F₁₇, F₁₈) are recomputed through the constructor and must agree
with the trigonometric-engine values to ≤ 10⁻⁹. This is independent replication
of the geometry, and is the standing guard for the five constraints that no
published table exercises.

**Gate 3 — Historical reproduction.** Before enumeration begins, the hash-pinned
engine must reproduce Rao's Tables 1 and 3 to ~10⁻⁷ (the documented under-converged
row 1,2,3,6,16,19 excepted, per the v0.1.0 errata).

**Gate 4 — Geometric validity.** A converged numerical solution is counted as
**feasible** only if it yields a valid geometric figure under the coordinate
constructor: every pair of points the construction requires to be distinct is
separated by more than **10⁻⁶ · r**, the figure closes (point 11 coincides with
point 11a within solver tolerance), and no forbidden coincidence or zero-area
primary triangle occurs. A solution failing Gate 4 is recorded as a numerical
solution but **not** a valid figure.

## 6. Methods — two-tier solving

**Tier 1 (primary, both forms) — multistart Newton.**
For each well-posed subset, 200 seeds are drawn by Latin-hypercube sampling over
an axis-aligned box B, where B is, per basic variable, the [min, max] across all
rows of Rao's Tables 1 and 3 widened by 50 % of the range on each side and
intersected with the valid domain (positivity; c, d < r; chain-defined arc
arguments in range). Rao's 14 tabulated solutions are added as deterministic
seeds. The RNG seed is fixed at **20260610**. Newton iterations run to
|Fᵢ| ≤ 10⁻⁶ (the **solver convergence floor**, reported alongside all results).
Tier 1 yields *solution found* / *no solution found*. **A Tier-1 negative is
never reported as infeasibility** — only as "no solution found (multistart, 200
seeds)."

**Tier 2 (completeness, plane form, 815 subsets) — homotopy continuation.**
The plane system is polynomialised (rational and radical relations cleared with
auxiliary variables carrying their defining equations) and solved by homotopy
continuation to enumerate **all** isolated complex solutions, from which the real,
in-domain ones are extracted. A Tier-2 result is **completeness-bearing** only if
the run's own diagnostics certify successful execution — all continuation paths
tracked to endpoints, no path failures or non-convergent endpoints. **If the
homotopy diagnostics do not certify success for a subset, that subset's negative
is downgraded to a Tier-1 negative** ("no solution found"), not a proof of
infeasibility. Only a diagnostics-certified Tier-2 run licenses the statement
"provably no real in-range solution."

**Tier 2 (spherical) — secondary / best-effort.** The spherical form carries
genuine transcendental terms and is not guaranteed to admit a clean polynomial
certificate. Spherical completeness is attempted only where tractable and is
reported as secondary; spherical negatives default to Tier-1 status.

**Cross-check.** Wherever both tiers run on a subset they must agree (every
Tier-1 solution appears among the certified Tier-2 solutions). Disagreement is a
halt-and-diagnose condition.

## 7. Equivalence and distinct-figure counting

**Definition (figure equivalence).** The object of study is the geometric figure,
so equivalence is defined directly on the figure, not on parameters. Two
solutions are **equivalent at tolerance τ** if the complete ordered coordinate
vector of the constructed figure differs by less than τ under the metric below.

**Metric (fully specified).**
- *Point set V (fixed):* the eleven base points P₀–P₁₀ and the secondary
  intersection points 1–19 in Rao's numbering — 30 points.
- *Order:* the canonical emission order of the frozen coordinate constructor
  (`figure_coordinates()`), fixed by the hash-pinned implementation.
- *Norm:* d(F⁽¹⁾,F⁽²⁾) = maxₚ∈V ‖p⁽¹⁾ − p⁽²⁾‖₂, the maximum Euclidean
  point-to-point distance.
- *Normalisation:* r ≡ 1, centre P_c at the origin, axis of symmetry along y.
  The construction has no rotational or translational freedom, so no alignment
  step is applied.

τ and all length thresholds are expressed in **units of r** (with r = 1; not
radians). The intercept vector H₁,…,H₁₀ is retained only as an **auxiliary
summary representation** and is not the equivalence relation.

**Tolerance sweep.** Distinct-valid-figure counts are reported for
**τ ∈ {10⁻², 10⁻³, 10⁻⁴, 10⁻⁵}**. **No single count is privileged**; the count is
reported as a function of τ. The finest level (10⁻⁵) is meaningful only where it
sits above the solver convergence floor; because that floor is on the constraint
residual rather than on coordinates directly, the realized coordinate spread of
accepted solutions is reported so the reader can see where τ approaches solver
noise. Counts at any τ below the realized floor are flagged as noise-limited.

## 8. Amendment protocol

Amendments are filed as `prereg/amendment-NN.md`, committed, GPG-signed, and
OpenTimestamps-stamped — provably dated before any analysis they license. The
amendment is a permanent part of the record.

**No retroactive reclassification.** Results obtained prior to an amendment
cannot be reclassified as confirmatory on the basis of the amended protocol.
Amendments may only expand hypotheses or analyses **prospectively**. A genuinely
unanticipated finding (e.g. a positive-dimensional feasible component, an
unexpected identity, an unforeseen multiplicity) is reported as **exploratory**;
any confirmatory claim about it requires a stamped amendment filed *before* the
corresponding confirmatory analysis is run.

## 9. Reporting schema

For each well-posed subset, the deposited outputs record:

| Subset | Numerical solutions | Valid figures (Gate 4) | Distinct figures (τ = 10⁻²,10⁻³,10⁻⁴,10⁻⁵) | Completeness status |
| --- | --- | --- | --- | --- |

Notes column records halt-and-diagnose events, Gate-4 rejections, and Tier-2
downgrades. **Every individual solution** (not merely cluster representatives) is
retained in the deposited machine-readable outputs, together with the fixed RNG
seed, the solver convergence floor, and the realized coordinate spread.

## 10. Deposit and reproducibility

The analysis code (enumeration driver, Tier-1 and Tier-2 solvers, the frozen
`figure_coordinates()`, and the gate harness) will be released and hash-pinned
**before** the confirmatory run; this pre-registration references the engine by
its v0.1.0 hash. Results, this protocol, and any amendments are deposited with
GPG signatures and OpenTimestamps stamps under the project's concept DOI.

## Reference

Rao, C. S. (1998). Śrīyantra — A Study of Spherical and Plane Forms. *Indian
Journal of History of Science*, 33(3), 203–227.
