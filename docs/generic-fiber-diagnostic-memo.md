# Generic-Fiber Structural Diagnostic — Memorandum (frozen)

**Scope.** Structural characterization of the generic complex fibers produced by
the regularized lift (lift-generator-v2) for the spherical size-six system, across
three deliberately varied subsets. Establishes what the large monodromy solution
count *is*, and surfaces the resulting strategy fork for census completeness.

**Status.** Frozen record of a completed diagnostic. It MEASURES; it does not
select a strategy. No build follows from it directly — the fork below is a
decision, not a task.

---

## 1. What prompted this

On the regularized v2 lift, seeded monodromy for {1,2,3,4,6,7} tracked cleanly
(the v1 singular-seed pathology is gone) but the solution count grew without
saturating (3687 → 9299 over 17 min, ~+157/loop). The growth pattern alone does
not identify a cause. Four hypotheses were live: **A** positive-dimensional
component, **B** huge-but-finite generic degree, **C** numerical duplication,
**D** many auxiliary-variable realizations collapsing to few geometries. (A fifth,
**E** pathological parametrization, is not separable by these measurements.)

## 2. Method

Per subset: capped monodromy (300 generic solutions) at a generic complex
parameter p_gen, seeded from one polished real Newton root; dump raw 54-component
complex solution vectors + p_gen (no filtering, recovery, or track-back). Then,
offline: cluster raw vectors and base blocks (first 12 atomic components); compute
the singular spectrum of the v2 Jacobian at 20 sampled solutions. The conditioning
tail was independently rechecked with an **exact symbolic Jacobian** (finite
differences validated against exact across cond 10²–10⁸: agreement to displayed
precision; FD is reliable here).

## 3. Results (three subsets, varied constraint composition)

| subset | composition | distinct vectors | distinct base blocks | ratio | spectrum (cond) |
|---|---|---|---|---|---|
| {1,2,3,4,6,7} | cosine-heavy (F4) | 300/300 | 299/300 | 1.00 | mostly 10³–10⁴; tail to 2.5e8 (exact-confirmed) |
| {1,2,13,14,15,20} | doubled family, no cosine | 300/300 | 299/300 | 1.00 | mostly 10³–10⁵; spike to 2.6e10 |
| {1,2,5,7,10,15} | no cosine, alt. equality mix | 300/300 | 297/300 | 1.01 | shallow; worst 7.5e4 |

Across all three: σ_min < 1e-10 at **zero** of 60 sampled solutions (every sampled
solution is locally isolated — rank full). Monodromy was nowhere near saturation
in any subset (last-loop new counts 25 / 274 / 92 of 300).

## 4. What is established (cross-subset)

- **No collapse mechanism.** Ratio ≈ 1.0 across three varied subsets ⇒ each
  generic solution is a distinct geometry. **D is not indicated** census-wide on
  this evidence; **C** (duplication) is not indicated.
- **No positive-dimensionality in the sampled solutions.** Full rank everywhere
  sampled ⇒ **strong-A not supported** by the data collected.
- **A real conditioning tail exists in every subset**, of varying severity
  (mild for {1,2,5,7,10,15}; a 2.6e10 spike for {1,2,13,14,15,20}). Real, not a
  finite-difference artifact (exact-Jacobian confirmed on {1,2,3,4,6,7}).
- **The generic fibers are large in every subset sampled**, and monodromy does
  not saturate quickly. Correctness is not in question; per-subset cost is.

## 5. What is NOT established (restraints)

- **Replication ≠ census.** Three subsets show the pattern is not a one-subset
  artifact. They do **not** prove it holds for all 3044. Distinct-base counts are
  **sample lower bounds**, not population counts.
- **No fiber-size claim.** "Large" is observed; exact generic degrees are
  unmeasured (saturation runs not performed — deliberately).
- **The 2.6e10 point** sits beyond the range where FD was exact-validated; if that
  specific value is ever quoted, it needs an exact-Jacobian recheck first.
- **Tail-severity drivers unknown.** Whether the heavier tail tracks the doubled
  family, absence of cosine constraints, or something else is not separable from
  three subsets. Logged, not explained.

## 6. The strategic fork (decision, not task)

The verify-then-replicate sequence has delivered a real strategic question with
evidence behind it: per-subset full-fiber monodromy is expensive in every subset
looked at. Two branches for census completeness:

**Branch I — Monodromy completeness (current path).**
Certified completeness via the trace test on the complex lift. Mathematically
clean and already partly built. **Known risk: cost.** The generic complex degree
is large in all three sampled subsets and monodromy does not saturate quickly;
3044 subsets may be impractical even on 8 cores. The cost is *measured*, at least
for the sampled subsets.

**Branch II — Base-coordinate real certification.**
Sidestep the lift's complex-degree inflation: certify completeness directly in the
regular, well-conditioned 6-variable base coordinates, where the admissible *real*
set is tiny. **Known risk: feasibility.** Finding the real solutions is easy
(Newton already does); *proving no other admissible real solution exists* is the
whole difficulty. This needs certified real-exclusion machinery (interval /
exclusion methods over a 6-D transcendental domain) that is **unbuilt for this
pipeline, and unproven** — such methods have their own combinatorial subdivision
walls and may or may not close on this geometry.

**The asymmetry to keep in view.** This is *known-expensive* (Branch I, cost
measured) versus *unknown-feasibility* (Branch II, cost unmeasured because the
instrument does not exist). Branch II is attractive precisely where it is least
tested. It is not established to be cheaper; it is established to be *different*.

## 7. Open question for the strategy discussion

> Spend the innovation budget optimizing a heavy but known complex-completeness
> method (Branch I), or building certified real-exclusion machinery in the benign
> 6-variable base space (Branch II) — whose feasibility is itself unproven?

No view is recorded here; the evidence narrows the problem but does not select the
branch. The decision deserves the same pre-registration discipline as the rest of
the project: choose the branch, register the method and its acceptance criteria,
then build.

---

### Provenance

- v2 lift frozen: `lift-generator-v2-spec.md` (spec SHA 5db1f12f…).
- Diagnostic tooling: `mono_diagnostic.py`, `mono_structure_diag.py`,
  `mono_exact_jac.py`.
- Dumps: `/tmp/mono_diag_out.jsonl` ({1,2,3,4,6,7}), `mono_diag_A` ({1,2,13,14,15,20}),
  `mono_diag_B` ({1,2,5,7,10,15}); each with its `.pgen`.
- Finite-difference spectrum validated against exact symbolic Jacobian
  (agreement across cond 10²–10⁸).
