# Śrīyantra Plane Enumeration — Campaign Plan

- **Branch:** `tier2-dev`
- **Date:** 2026-06-12
- **Status:** Phase 0 (tooling validation) in progress. Pre-confirmatory until the
  tooling freeze (§8) and Gate M (§5) pass.
- **Governs:** the confirmatory plane Tier-2 enumeration under the pre-registration
  ([10.5281/zenodo.20630790](https://doi.org/10.5281/zenodo.20630790)) **as amended by
  `prereg/amendment-01.md`** (coefficient-parameter family homotopy).
- **Engine under test:** Sri Yantra Constraint Engine v0.1.0
  ([10.5281/zenodo.20617730](https://doi.org/10.5281/zenodo.20617730)), hash-pinned.

> This is a dev-branch operational document. No run described here is confirmatory
> until (a) the Tier-2 tooling is frozen and hash-pinned, and (b) Gate M passes.
> Runs before that point are development and validation only.

---

## 1. Method in one paragraph

The 815 well-posed plane subsets (+ the one rank-deficient triple, kept as a
Gate-1 check) share an identical fixed system — the 28-equation lifted chain with
F₁ and F₂, 30 equations in 33 variables — and differ only in which three of the
18 non-essential constraints are appended. Each appended constraint is, in the
lifted variables, degree 1 (linear) or degree 2 (quadratic), giving **four degree
types** (3,0)/(2,1)/(1,2)/(0,3) with **84/324/324/84** subsets. Per type: solve
one **generic** member ab initio by monodromy (twice, unioned) → **N\*** generic
solutions; certify completeness with the **trace test**; then **parameter
homotopy** from the generic member to each subset, tracking **N\*** paths each.
Completeness-bearing status follows amendment-01 §A3. This replaces 815 ab initio
solves (≈286k paths each) with 4 generic solves plus cheap continuations.

---

## 2. Hardware and execution model

- **Server:** 4 physical cores, 15 GB RAM (~14 GB available), **no swap**.
- **Ab initio baseline** (subset {1,2,3,4,8}, `solve_1_2_3_4_8.jl`): mixed volume
  **286,144**, peak RAM **~1.4 GB**, **CPU-bound** (~400 % CPU, load ~4, swap 0),
  wall ≈ 2.7 h. Its non-singular complex count gives a **lower bound N\*(Q3) ≥ 429**.
- **Threading:** `julia -t 4,1` (4 compute threads, 1 interactive), per the
  HomotopyContinuation.jl guidance. The workload is CPU-bound and the solver
  multithreads path tracking internally, so:
  - **one Julia session per family** — generic solve + that family's full sweep in
    a single process (avoids paying precompilation per subset);
  - **subsets swept serially** within the session;
  - **no subset-level process parallelism** (4 procs × 4 threads on 4 cores
    contends and is slower; revisit only if profiling shows idle cores).
- Re-evaluate this model only if a family's generic solve does **not** fit in RAM
  alongside the Julia runtime (watch peak RSS; the no-swap box must never page).

---

## 3. Directory and artifacts

```bash
enumeration/
  lift_family.py            # 33-var master lifter + validation + emitter
  family_solve.jl           # campaign driver (monodromy + trace test + sweep)
  solve_1_2_3_4_8.jl        # ab initio PoC; cross-check anchor (Gate M2)
  CAMPAIGN_PLAN.md          # this file
  logs/                     # one log per family run
  family_results.jsonl      # per-family + per-subset records (append mode)
  family_benchmark.csv      # family-level resource table (below)
```

Standard run (per family), logged and timed:

```bash
cd /opt/sri-yantra-constraint-engine
/usr/bin/time -v julia -t 4,1 enumeration/family_solve.jl --type=Q3 \
  2>&1 | tee enumeration/logs/family_Q3.log
```

`family_benchmark.csv` header:

```csv
family,type_lin_quad,n_subsets,Nstar,run_agreement,trace_test_passed,monodromy_runtime_s,trace_runtime_s,sweep_runtime_s,peak_RAM_kb
```

`family_results.jsonl` is emitted by the driver (append mode — delete between full
reruns or records duplicate). Per-subset fields: `subset`, `family`,
`expected_degenerate`, `Nstar_paths`, `path_failures`, `n_solutions`, `n_real`,
`n_admissible`, `n_certified_distinct`, `admissible_bcdeg`, `completeness_bearing`,
`runtime_s`.

---

## 4. Phases

### Phase 0 — Tooling validation, smoke test, freeze  *(DEV, pre-confirmatory)*

0.1 **Engine-equivalence re-check (Gate M1 precheck).** `python3
enumeration/lift_family.py` on this machine; chain identities and every
pool-polynomial factor relation must match the frozen engine to ≤ 10⁻¹². *(Run
here: chain 2.8e-16, pool worst 3.3e-16 — reproduce locally.)*

0.2 **Smoke test (first Julia execution).** `julia -t 4,1
enumeration/family_solve.jl --type=Q3 --max-targets=3`. Expect to debug
HomotopyContinuation.jl signatures (likely `unique_points_rtol`,
`verify_solution_completeness` kwargs) — these are code bugs, not method failures.

0.3 **Record N\*(Q3).** The decisive number. Multiply through to size the campaign
(generic-solve time × 4, plus N\* × 816 continuation paths). Q3 is the most
expensive type; if it is tractable the linear-heavy families are cheaper.

0.4 **Gate M2 — two-way cross-check on {1,2,3,4,8}.** Solve both ways (ab initio
`solve_1_2_3_4_8.jl` and the Q3 parameter homotopy). Full **admissible real
solution sets must be set-equal** under the §7 metric at τ = 10⁻⁵ and contain
Rao's Table 3 row. Keep the ab initio run's **complete** output (all solutions,
not only admissible) as the comparison corpus.

0.5 **Freeze.** Hash-pin `lift_family.py`, `family_solve.jl`, `Project.toml`,
`Manifest.toml` → `prereg/tier2-freeze.sha256`; GPG-sign and OpenTimestamps-stamp.
The resolved HomotopyContinuation.jl version is part of the record.

**Decision gate.** Proceed to Phase 1 **only if** M1 and M2 pass and a full family
completes within acceptable wall time and RAM. Any failure is halt-and-diagnose.

### Phase 1 — Generic solves + completeness certificates  *(CONFIRMATORY, post-freeze)*

For each of the 4 types: two independent `monodromy_solve` runs unioned → **N\***;
**trace test** → `trace_test_passed`. Record N\*, run agreement, the certificate,
and timings to `family_benchmark.csv`. This is the only expensive ab initio cost
in the campaign. A family whose trace test fails makes **all** its subsets'
negatives non-completeness-bearing (amendment-01 §A3) — diagnose before accepting.

### Phase 2 — Parameter-homotopy sweep  *(CONFIRMATORY)*

Sweep all 816 targets by family (815 well-posed + {8,9,16} as the Gate-1 check).
Per subset: track N\* paths; count genuine path failures (at-infinity excluded);
apply the admissibility filter (x₁,x₂,w > 0; no cleared denominator vanishing);
**round-trip** each admissible solution through the v0.1.0 engine (Gate 2);
`certify` and count certified-distinct; write the JSONL record with
`completeness_bearing = trace_test_passed ∧ (path_failures = 0)`.

### Phase 3 — Classification map  *(CONFIRMATORY post-processing)*

Per accepted solution: **Gate 2b** (recompute F₇,F₁₁,F₁₂,F₁₇,F₁₈ through the
independent coordinate constructor, agree ≤ 10⁻⁹); **Gate 4** (geometric validity
— required-distinct points separated > 10⁻⁶·r, figure closes). Then the **τ-sweep**
distinct-figure count (§7 metric, τ ∈ {10⁻²,10⁻³,10⁻⁴,10⁻⁵}, no single τ
privileged). Populate the pre-registration reporting schema:
`Subset | Numerical solutions | Valid figures | Distinct figures (τ) | Completeness status`.

---

## 5. Stop criteria — halt-and-diagnose

**Validation.** Gate M1 or M2 failure; **Gate 1** violation ({8,9,16} returns a
solution isolated by *both* full-rank-Jacobian and no-continuum criteria); Gate 2,
2b, or 4 failure; any round-trip inconsistency; ab initio vs family disagreement
on any subset run both ways.

**Numerical.** Trace test fails for a family (downgrades the whole family —
diagnose, do not silently accept); monodromy fails to stabilise across the two
runs; genuine path failures beyond those explained by non-generic 0/1 targets;
certification failures.

**Computational.** A family's generic solve exceeds the agreed wall-time review
threshold; peak RSS approaches total RAM (no-swap box must never page); per-subset
sweep runtime departs sharply from the family norm.

Any paused run is diagnosed before the campaign proceeds. Failures never trigger a
revision of results — only diagnosis and, if a *method* change is implied, a
further prereg amendment before any confirmatory rerun.

---

## 6. Deliverables

- **N\* per family** and the chain-variety degree — recorded invariants
  (amendment-01 §A4; raw counts confirmatory, interpretation exploratory).
- The **classification map** (reporting schema, §9 of the prereg), every
  individual solution recorded — not cluster representatives.
- **Failure-mode catalog** (downgrades, Gate rejections, path failures).
- **Resource actuals**: CPU-hours and wall-clock for each family and the full
  campaign; `family_benchmark.csv` + `family_results.jsonl`.
- The realised coordinate spread and solver-convergence floor, so the reader can
  see where τ approaches solver noise.

---

## 7. Cross-references

Pre-registration `prereg/preregistration.md`
([10.5281/zenodo.20630790](https://doi.org/10.5281/zenodo.20630790)) · Amendment
`prereg/amendment-01.md` · Engine v0.1.0
([10.5281/zenodo.20617730](https://doi.org/10.5281/zenodo.20617730)) · Tooling
freeze manifest `prereg/tier2-freeze.sha256` (created at §4 step 0.5).
