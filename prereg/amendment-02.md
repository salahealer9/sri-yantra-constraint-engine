# Amendment 02 — Plane Tier-2 completeness via certified real-box enumeration (affine-arithmetic interval-Newton)

- **Amends:** Pre-registration *"Complete classification of the well-posed subsets
  of the Rao (1998) Śrīyantra constraint system,"* version DOI
  [10.5281/zenodo.20630790](https://doi.org/10.5281/zenodo.20630790), registered
  2026-06-10.
- **Supersedes:** Amendment 01, *"Plane Tier-2 completeness via coefficient-parameter
  homotopy,"* version DOI
  [10.5281/zenodo.20672072](https://doi.org/10.5281/zenodo.20672072), filed
  2026-06-12 — superseded **in its entirety** (§B1).
- **Author:** Salah-Eddin Gherbi, Independent Researcher,
  [ORCID 0009-0005-4017-1095](https://orcid.org/0009-0005-4017-1095).
- **Filed:** 2026-06-13 — before any well-posed subset outside Rao's published
  tables has been solved under the amended procedure, and before the Tier-2
  tooling freeze (§B8).
- **Frozen engine under test:** unchanged — Sri Yantra Constraint Engine v0.1.0
  ([10.5281/zenodo.20617730](https://doi.org/10.5281/zenodo.20617730)).
- **Status:** Permanent part of the pre-registration record per §8 of the
  original. GPG-signed and OpenTimestamps-stamped on deposit.

---

## B0. Nature and limits of this amendment

This amendment again replaces the **method and completeness certificate** of the
plane-form Tier-2 step — the clause headed *"Tier 2 (completeness, plane form,
815 subsets) — homotopy continuation"* in §6 of the original, as previously
amended by Amendment 01. It supersedes Amendment 01 in full (§B1), withdraws its
homotopy method, and installs in its place the certified real-box enumeration of
§B2–§B4, with new recorded invariants (§B5), gate interaction (§B6), pre-run
validation (§B7), and tooling freeze (§B8). It changes **nothing else**: not the
scope (§1), the confirmatory research question (§2), the confirmatory/exploratory
demarcation (§3), the enumeration scope (§4), Gates 1–4 (§5), the **Tier-1**
procedure (§6), the equivalence metric and τ sweep (§7), or the reporting schema
(§9).

The §8 amendment protocol governs this document and is reaffirmed in full,
including **no retroactive reclassification**: no result obtained before this
amendment's timestamp is confirmatory under it, and this amendment expands the
registered procedure **prospectively only**. In particular, the homotopy
intractability finding (§B1) and the methodological validation pilot (§B7) were
both obtained *before* this filing and are **exploratory**: they are the recorded
basis for the method change, not confirmatory results, and they are not
reclassifiable.

---

## B1. Withdrawal of Amendment 01's method

Amendment 01 organised the plane campaign as a coefficient-parameter family
homotopy: one generic monodromy solve per degree type, trace-test certified, then
parameter continuation to each subset. On implementation this is **computationally
intractable**, for an intrinsic (not engineering) reason:

- A generic member of the dominant degree class has a mixed volume (BKK bound, the
  number of paths a parameter homotopy must track) of **2,542,016**.
- A single subset solved ab initio has mixed volume **286,144**; over ~815 subsets
  this is the same order of work as the family route and is itself infeasible.
- The bound is invariant under the conservative auxiliary-variable elimination
  attempted (BKK is preserved), and symbolic collapse to the native variables is
  blocked by the constraint degrees (F₈ degree 8, F₃ degree 14).

This is a recorded **exploratory negative result**: homotopy-based completeness,
in both the per-subset and family forms registered or contemplated, does not scale
to this system. Amendment 01's §A2–§A7 are therefore withdrawn in their entirety,
including its Gate M (§A6) and tooling freeze (§A7), which referenced the homotopy
tooling. The diagnostic scripts supporting this finding (`enumeration/lift_poc.py`,
`enumeration/lift_family.py`, `enumeration/collapse_probe.py`) are retained in the
record.

---

## B2. Superseded text and replacement method — certified real-box enumeration

The §6 plane Tier-2 method clause — as amended by Amendment 01, and in its
original homotopy wording — is **superseded** by the following. **Retained**
unchanged: that real, in-domain solutions are extracted and confirmed by
**round-trip** through the frozen v0.1.0 engine (Gate 2); the
**downgrade-to-Tier-1 rule**; the licensing statement that only a certified Tier-2
run permits *"provably no real in-range solution"*; and the spherical Tier-2
paragraph (secondary / best-effort, §B9).

The research question is recast for the plane form as: **enumerate all real
admissible figures of a subset inside the registered box.** This is the
confirmatory deliverable already named in §3 (numerical-solution and valid-figure
counts per subset); interval root-finding answers it directly and certifies
completeness *over a bounded real box*, scaling with the number of real roots and
the local geometry rather than with the complex BKK count.

**(i) Domain.** Each subset is enumerated over the axis-aligned box **B** already
defined in §6 (per basic variable, the [min, max] across Rao's Tables 1 and 3
widened by 50 % of the range on each side), with the valid-domain conditions
(positivity; c, d < r; in-range chain arc arguments; nonvanishing cleared
denominators; square-root sign branches x₁, x₂, w > 0) enforced as **admissibility
filters** during the search. The same box **B** is shared with Tier-1, so the two
tiers are directly comparable.

**(ii) Branch-and-prune.** A box is processed by: (a) a **rigorous affine-arithmetic
(AA) exclusion** test — the engine chain is evaluated in AA over the box, and the
box is discarded if 0 lies outside the AA enclosure of any imposed constraint; and
(b) when the box radius is at or below the frozen certification radius r_cert, a
**rigorous AA-Krawczyk interval-Newton** test. Boxes that are neither excluded nor
certified are bisected on the widest coordinate. The search runs until the queue is
exhausted.

**(iii) AA-Krawczyk certification.** The Jacobian over the box is enclosed by
forward-mode automatic differentiation carried in affine arithmetic (partials
propagated as affine forms), giving a tight interval matrix J(X). With
Y = (mid J(X))⁻¹ and the Krawczyk operator
K(X) = m − Y·F(m) + (I − Y·J(X))·(X − m), the test is: **K(X) ⊆ int(X)** certifies
**a unique** real root in X; **K(X) ∩ X = ∅** certifies **no** root in X. A
certified root is polished by Newton to the solver convergence floor and counted
under the §7 metric; admissibility (square-root branches, denominators) is
verified at the polished point and the imposed constraints must satisfy Gate 2 on
round-trip through v0.1.0.

**(iv) Rigour requirement (binding).** The confirmatory tool uses **outward-rounded**
interval arithmetic throughout (rigorous affine arithmetic, or equivalently
validated Taylor models), so that every enclosure is a guaranteed superset of the
true range and every certificate is a genuine mathematical proof. Float-coefficient
arithmetic is **not** admissible for a confirmatory run; it was used only in the
methodological pilot (§B7), which is consequently not itself completeness-bearing.

---

## B3. Replacement completeness criterion (plane Tier-2)

A plane subset's enumeration is **completeness-bearing** — licensing the statement
*"provably no real in-range solution"* for an empty result, or *"exactly k
admissible figures in B"* for k certified roots — only if **both** hold:

- **(a)** the branch-and-prune **terminated with an empty queue**, every box having
  been either AA-excluded or AA-Krawczyk-decided (unique / empty), under rigorous
  outward-rounded arithmetic; **and**
- **(b)** the run did not exhaust the frozen safety budget (maximum box count and
  wall-clock limit fixed in the tooling, §B8); a budget-exhausted run is **not**
  complete.

If either fails, the subset's result is **downgraded to a Tier-1 result** ("no
solution found" / "solution(s) found, completeness not certified"), exactly as in
the original clause. A complete run certifying **zero** roots is a positive,
completeness-bearing statement of **absence**, not a Tier-1 negative.

---

## B4. Recorded invariants (new outputs)

Per subset the run records, as **confirmatory** raw outputs on the same footing as
the §3 per-subset solution count: the **certified figure count**; for each
certified figure its polished coordinates and the Krawczyk **contraction factor**
‖I − Y·J(X)‖; the number of **boxes processed**; the **maximum queue depth**; and
the **completion flag** (queue-exhausted vs budget-exhausted). The frozen r_cert,
the bisection rule, and the safety budget are recorded alongside.

Any **interpretation** of these counts — a count of distinct Śrīyantras, structure
across the feasible/infeasible landscape, the meaning of queue inflation — is
**exploratory** under §3 and admissible as confirmatory only by a further
prospective amendment.

---

## B5. Gate interaction

Gates 1–4 (§5) are unchanged and continue to run, per accepted solution, against
the hash-pinned v0.1.0 engine.

For **Gate 1**: the certified rank-deficient triple {1,2,8,9,16} (plane) cannot be
certified by this method — Krawczyk certifies **isolated** roots, and a
rank-deficient subset has a positive-dimensional solution set. Its expected
operational signature is **non-termination** (the queue does not exhaust within
budget) with **no certified isolated solution** and a characteristically inflated
queue. This satisfies the §5 Gate-1 condition (no solution isolated by both the
full-rank-Jacobian and no-continuum criteria) and the subset is excluded from the
confirmatory sweep analytically, the two exact linear identities being known from
v0.1.0. Its inclusion as an explicit Gate-1 probe is optional and, if run, is
expected to be budget-exhausted, not complete.

---

## B6. Spherical form

The spherical Tier-2 paragraph remains **secondary / best-effort** and unchanged in
status. The real-box method extends in principle to the spherical form by interval
extension of its transcendental terms, attempted only where tractable; a spherical
result is completeness-bearing under the §B3 criterion when its branch-and-prune
terminates under rigorous arithmetic, and defaults to Tier-1 otherwise. No
spherical pilot has been performed; nothing here claims spherical completeness.

---

## B7. Mandatory pre-run method validation (Gate M)

Before any plane Tier-2 enumeration is admitted as confirmatory, and **after** the
tooling freeze (§B8):

- **(M1) Engine-equivalence re-verification.** The AA port's equivalence to the
  frozen v0.1.0 engine is re-established under rigorous arithmetic: the AA
  enclosure of every constraint F₁…F₂₀ must bracket the engine value at Rao's six
  Table 3 rows, the plane optimum, and randomly sampled valid figures.
- **(M2) Two-way cross-validation on {1,2,3,4,8}.** Subset {1,2,3,4,8} is solved
  **both** ways — by the rigorous AA-Krawczyk enumeration, and by an independent
  multistart-Newton search over B — and the **full admissible real solution sets
  must agree** (set-equal under the §7 metric at τ = 10⁻⁵), containing Rao's Table 3
  row (0.463752, 0.223255, 0.288990, 0.488181, 0.106157).

Failure of M1 or M2 is a **halt-and-diagnose** condition (§5): it blocks the
confirmatory campaign and is never resolved by revising results.

**Status of the methodological pilot.** An eight-subset pilot (Rao A {1,2,3,4,8},
Rao B {1,2,4,5,10}, grounded-constraint {1,2,6,14,19} and {1,2,3,10,15}, a feasible
non-reference {1,2,6,10,19}, two infeasible {1,2,11,12,17} and {1,2,3,4,6}, and the
rank-deficient {1,2,8,9,16}), with a multistart-Newton soundness cross-check, was
run **before** this filing using float-coefficient arithmetic. It established that
the method behaves correctly across these classes — certifying the published
figure where one exists, certifying absence where the subset is infeasible, and
not certifying the rank-deficient subset (whose solution continuum the cross-check
independently exhibited). This pilot is **exploratory** (§B0) and is the recorded
basis for adopting the method; it is **not** confirmatory and is not the certificate.
The deposited record is `enumeration/validation_panel/` and the conditioning,
overestimation, and contraction diagnostics in `enumeration/` (`jac_cond.py`,
`overest.py`, `aa_test.py`, `aa_krawczyk.py`).

---

## B8. Tooling freeze and reproducibility

The Tier-2 tooling — the enumeration driver and certification routines
(`enumeration/route3_enum.py`, `enumeration/route3_panel.py`,
`enumeration/aa_krawczyk.py`, `enumeration/xcheck.py`), the rigorous
outward-rounded arithmetic implementation, and the Python environment
(interpreter and pinned package versions) — together with the frozen numerical
parameters (certification radius r_cert, bisection rule, safety budget, RNG seed of
the M2 cross-check) is hash-pinned **after** validation-tooling debugging and
**before** any confirmatory run. The frozen manifest (`prereg/tier2-freeze.sha256`)
is GPG-signed and OpenTimestamps-stamped under the project concept DOI, mirroring
the v0.1.0 engine pin. The frozen **engine under test** remains v0.1.0 and is not
touched by this amendment. Any change to the tooling after the freeze requires a
further amendment.

---

*End of Amendment 02.*
