# Amendment 01 — Plane Tier-2 completeness via coefficient-parameter homotopy

- **Amends:** Pre-registration *"Complete classification of the well-posed subsets
  of the Rao (1998) Śrīyantra constraint system,"* version DOI
  [10.5281/zenodo.20630790](https://doi.org/10.5281/zenodo.20630790), registered
  2026-06-10.
- **Author:** Salah-Eddin Gherbi, Independent Researcher,
  [ORCID 0009-0005-4017-1095](https://orcid.org/0009-0005-4017-1095).
- **Filed:** 2026-06-12 — before any well-posed subset outside Rao's published
  tables has been solved under the amended procedure, and before the Tier-2
  tooling freeze (§A7).
- **Frozen engine under test:** unchanged — Sri Yantra Constraint Engine v0.1.0
  ([10.5281/zenodo.20617730](https://doi.org/10.5281/zenodo.20617730)).
- **Status:** Permanent part of the pre-registration record per §8 of the
  original. GPG-signed and OpenTimestamps-stamped on deposit.

---

## A0. Nature and limits of this amendment

This amendment replaces the **method and completeness certificate** of the
plane-form Tier-2 step — the clause headed *"Tier 2 (completeness, plane form,
815 subsets) — homotopy continuation"* in §6 of the original — and adds the
associated recorded invariants (§A4) and a mandatory pre-run validation (§A6).
It changes **nothing else**. In particular it does not alter the scope (§1), the
confirmatory research question (§2), the confirmatory/exploratory demarcation
(§3), the enumeration scope (§4), Gates 1–4 (§5), the **Tier-1** procedure (§6),
the equivalence metric and τ sweep (§7), or the reporting schema (§9).

The §8 amendment protocol governs this document and is reaffirmed in full,
including **no retroactive reclassification**: no result obtained before this
amendment's timestamp is confirmatory under it, and this amendment expands the
registered procedure **prospectively only**.

**Why amend rather than rely on the original wording.** The original Tier-2
clause certifies completeness *per subset*, by that subset's own ab-initio path
tracking. The method below certifies completeness *once per degree type* (a
generic solve plus a trace test) and continues that certificate to each subset.
Both are "homotopy continuation enumerating all isolated complex solutions," but
the **inferential basis** for a subset's statement *"provably no real in-range
solution"* changes: it now rests partly on a shared, generic solve. Registering
that change explicitly and prospectively is required for the completeness claim
to remain honest.

---

## A1. Superseded text

Within the §6 plane Tier-2 clause, the sentences specifying the per-subset
solving method and its completeness criterion — from *"solved by homotopy
continuation to enumerate all isolated complex solutions"* through the criterion
*"all continuation paths tracked to endpoints, no path failures or
non-convergent endpoints"* — are **superseded** by §A2–§A3 below.

**Retained** from the same clause, unchanged: that the plane system is
polynomialised with auxiliary variables carrying their defining equations; that
real, in-domain solutions are extracted from the complex set; the
**downgrade-to-Tier-1 rule**; and the licensing statement that only a certified
Tier-2 run permits *"provably no real in-range solution."* The spherical Tier-2
paragraph (secondary / best-effort) and the **Cross-check** paragraph are
unchanged.

---

## A2. Replacement method — coefficient-parameter family homotopy

The 815 well-posed plane subsets (plus the one certified rank-deficient triple,
retained in the sweep as a Gate-1 check) share an identical fixed system: the
28-equation lifted chain together with F₁ and F₂ — 30 equations in 33 lifted
variables. Subsets differ **only** in which three of the 18 non-essential
constraints {F₃,…,F₂₀} are appended. The campaign is therefore organised as
**coefficient-parameter homotopy** (Sommese–Wampler), valid here because the slot
coefficients enter the system **linearly**:

**(i) Stratification by degree type.** In the lifted variables each pool
constraint has degree 1 — *linear:* F₅,F₇,F₁₀,F₁₁,F₁₂,F₁₃,F₁₄,F₁₅,F₂₀ — or
degree 2 — *quadratic:* F₃,F₄,F₆,F₈,F₉,F₁₆,F₁₇,F₁₈,F₁₉. The three appended slots
give four degree types (3,0), (2,1), (1,2), (0,3) with 84, 324, 324, 84 subsets
respectively. One generic family is solved per type.

**(ii) Generic solve.** For each type the three slots are independent generic
linear combinations, with random complex coefficients **p₀**, of the pool
constraints of the slot's degree class. The resulting 33×33 system is solved ab
initio by monodromy (`monodromy_solve`), run **twice** from independent generic
parameters and unioned at common parameters, yielding the generic solution set
of size **N\***.

**(iii) Completeness certificate.** The generic set is certified complete by the
trace test (`verify_solution_completeness`; Leykin–Rodriguez–Sottile). The
boolean `trace_test_passed` is the family's completeness certificate.

**(iv) Continuation to subsets.** Each subset is the parameter point whose 0/1
coefficients select its three constraints. Its isolated solutions are obtained by
parameter homotopy from p₀ to that point, tracking exactly N\* paths. By the
parameter-continuation theorem, for a trace-certified generic start every
isolated solution of every target subset is an endpoint of those N\* paths. Real,
in-domain solutions are extracted by the admissibility filter (square-root sign
branches x₁,x₂,w > 0; no cleared denominator vanishing) and confirmed by
**round-trip** through the frozen trigonometric engine: the recovered
(b,c,d,e,g) is re-evaluated by v0.1.0 and the imposed constraints must satisfy
Gate 2.

The squared radial forms used in the lifting (F₈ = r₁₆²−r², F₁₆ = r₁₆²−r₁₇²,
F₁₇ = r₁₈²−r₁₉², F₁₈ = r₁₆²−r₁₈², F₁₉ = r₁₇²−r₁₉²) introduce no new square-root
auxiliaries and, over the reals with nonnegative radii, no spurious branches;
their zero sets coincide with the engine constraints up to the strictly-nonzero
factors recorded in the tooling and re-verified under §A6.

---

## A3. Replacement completeness criterion (plane Tier-2)

A plane subset's negative is **completeness-bearing** — licensing *"provably no
real in-range solution"* — only if **both** hold:

- **(a)** its degree type's family **trace test passed**
  (`trace_test_passed = true`); **and**
- **(b)** the subset's own parameter homotopy completed with **zero genuine path
  failures**, where a genuine failure is a path that is neither a tracked success
  nor certified at infinity (`is_at_infinity`). Paths ending at infinity are not
  failures.

If either condition fails, the subset's negative is **downgraded to a Tier-1
negative** ("no solution found"), as in the original clause. In particular, **a
family-level trace-test failure downgrades every subset of that degree type.**
This shared dependency is registered here as a known and accepted property of the
method, not as a result.

---

## A4. Recorded invariants (new outputs)

Per degree type the run records **N\***, the two-run monodromy agreement, and
`trace_test_passed`. N\* is a direct product of the registered procedure and is
recorded as a **confirmatory** raw count, on the same footing as the per-subset
numerical-solution count of §3.

Any **interpretation** of N\* or of the chain-variety degree — for example, as a
uniform a priori bound on the number of distinct admissible figures, or as
evidence of structure in the landscape — is **exploratory** under §3 and is
admissible as confirmatory only by a further prospective amendment.

---

## A5. Gate interaction

Gates 1–4 (§5) are unchanged and continue to run, per accepted solution, against
the hash-pinned v0.1.0 engine.

For **Gate 1**: under parameter homotopy the certified rank-deficient triple
{1,2,8,9,16} is included as a target. It **passes** if it yields no solution that
is isolated by **both** the full-rank-Jacobian (singular-value ratio ≥ 10⁻⁷) and
no-continuum criteria of §5. Its expected operational signature under the new
method — path coalescence, divergence, or singular / at-infinity endpoints, and
no certified isolated admissible solution — is the same Gate-1 evidence required
by §5, now produced by the continuation rather than by an independent ab-initio
solve.

---

## A6. Mandatory pre-run method validation (Gate M)

Before any plane Tier-2 family run is admitted as confirmatory, and **after** the
tooling freeze (§A7):

- **(M1) Engine-equivalence re-verification.** The family lifter's equivalence to
  the frozen v0.1.0 engine is re-established — chain identities and every
  pool-polynomial factor relation to ≤ 10⁻¹², at Rao's six Table 3 rows, the
  plane optimum, and randomly sampled valid figures.
- **(M2) Two-way cross-validation on {1,2,3,4,8}.** Subset {1,2,3,4,8} is solved
  **both** ways — ab initio (its own polyhedral solve, `solve_1_2_3_4_8.jl`) and
  by the family parameter homotopy. The **full admissible real solution sets must
  agree** (set-equal under the §7 metric at τ = 10⁻⁵) and must contain Rao's
  Table 3 row (0.463752, 0.223255, 0.288990, 0.488181, 0.106157). The F₃, F₄, F₈
  pool polynomials are byte-identical between the two routes, so agreement tests
  the family machinery and the continuation, not the lifting.

Failure of M1 or M2 is a **halt-and-diagnose** condition (§5): it blocks the
confirmatory campaign and is never resolved by revising results.

---

## A7. Tooling freeze and reproducibility

The Tier-2 tooling — `enumeration/lift_family.py`, `enumeration/family_solve.jl`,
and the Julia environment (`Project.toml`, `Manifest.toml`) — is frozen and
hash-pinned **after** smoke-test debugging and **before** any confirmatory run.
The frozen manifest (`prereg/tier2-freeze.sha256`) is GPG-signed and
OpenTimestamps-stamped under the project concept DOI, mirroring the v0.1.0 engine
pin. The HomotopyContinuation.jl version resolved into the frozen `Manifest.toml`
is part of the record. The frozen **engine under test** remains v0.1.0 and is not
touched by this amendment. Any change to the tooling after the freeze requires a
further amendment.

---

*End of Amendment 01.*
