# Gate X — Full-Fiber Monodromy Feasibility Benchmark (preregistration)

**Type.** Benchmark / execution preregistration. **NOT a methodological amendment.**
It does not change H4, the universe (3044), the outcome definition, the agreement
criterion, or the solver role. It asks a single feasibility question about the
already-selected homotopy path.

**Question.** Can full-fiber monodromy on the regularized v2 spherical lift reach
trace-test completeness for the benchmark subset within a realistic, pre-declared,
census-scale per-subset resource budget?

**Status at freeze.** Parameters fixed below before execution. Outcome to be
recorded against the rule in §4; the rule is declared here so the verdict cannot
be reinterpreted after the run.

---

## 1. Scope and non-amendment statement

Gate X tests computational feasibility of an instrument already chosen and frozen
(global homotopy continuation on the spherical lift; Amendment 04 §3). It changes
no scientific commitment. It carries no amendment number. A FAIL does not by
itself change any method; it authorizes the *next* exploratory step (a
base-coordinate pilot), after which a separate methodological amendment would be
required before any confirmatory census run on a different instrument.

## 2. Frozen instrument and provenance

| field | value |
|---|---|
| benchmark subset | {1,2,3,4,6,7} |
| lift | lift-generator-v2 (spec SHA-256 5db1f12f19f17fc343de5be1c78cadf0aaccfcc6c65e1602a63313ff6e3d64e9) |
| v2 system hash (this subset) | c540c04f22a9c7d8f2afdc1d7888781d07c6ebdde46cdda83b9559e76d4f1c0e |
| seed root | polished v2 seed for this subset (full-precision vector archived with the run) |
| HC.jl version | 2.20.0 |
| JULIA_NUM_THREADS / cores | 8 |
| wall-clock cap | 2 hours |
| max_loops_no_progress | 10 |
| random seed | 20260624 |
| completeness verdict (PASS) | is_success(MR) |
| verify_solution_completeness | run if available; forensic only; not part of PASS/FAIL |
| hardware | earthgrid-python (8-core); recorded with the run |

The seed root, p_gen generation, and the exact monodromy call are part of the
instrument and are archived with the run for reproducibility.

## 3. Census-scale justification for the 2-hour cap

The cap encodes a realistic per-subset budget. At 2 h/subset × 3044 subsets on a
single 8-core machine, the census would take on the order of 250 machine-days
(~8 months). Therefore: if one well-instrumented subset cannot reach trace-test
completeness in 2 h on 8 cores, full-fiber monodromy is not a viable census-scale
instrument on this hardware — documented under a fixed budget, not inferred from
capped samples. The cap is generous relative to the 17-minute exploratory run, so
the homotopy route is not being abandoned prematurely.

## 4. Outcome rule (three-way; declared before execution)

- **PASS** — `is_success(MR) == true` within the 2-hour budget, with intact logs.
- **FAIL** — the run reaches the declared resource limit (2-hour wall-clock OR the
  no-progress threshold) **without** `is_success(MR) == true`, with intact logs and
  no technical failure. A deliberate cap-termination is the expected FAIL path, not
  an inconclusive one.
- **TECHNICAL INCONCLUSIVE** — crash, out-of-memory, corrupted output, solver
  exception, unusable log, or **inability to evaluate `is_success(MR)`**. Triggers
  a re-run; never counts as PASS or FAIL.

A failure or exception from the optional `verify_solution_completeness` call is
**not** TECHNICAL INCONCLUSIVE and does **not** affect PASS/FAIL — it is recorded
in the forensic layer only. Only inability to read the **primary** verdict
(`is_success`) is inconclusive.

## 5. Scaling-interpretation clause

The benchmark subset is one subset, chosen because it is the best-instrumented and
has a known valid seed. It is **not** assumed to represent all 3044 subsets.
- A **FAIL** documents that full-fiber monodromy is not viable as a census-scale
  instrument *under this budget on this hardware*; it is not a claim about the
  difficulty of the other 3043 subsets individually.
- A **PASS** shows the route is plausible for this subset; it does **not** by
  itself establish census-wide viability (the other subsets are unmeasured).
Either way, the result is read as evidence about *plausibility of the instrument
at census scale*, not as a property of the remaining universe.

## 6. Forensic archive (required on EVERY exit path, incl. cap-kill)

The runner must write, regardless of outcome — including when terminated at the
wall-clock cap:
- final generic solution count and the per-loop log (tracked / queued / new),
- no-change (no-progress) loop count and the stopping reason,
- `is_success(MR)` verdict; `verify_solution_completeness` result if attempted,
- candidate real roots tracked back to the true system (p=0), with residuals,
- Gate-4 verdicts on the recovered admissible candidates,
- the raw solver log, and the full provenance block (§2),
- elapsed wall-clock and the outcome classification (§4).

A FAIL with this archive is a complete decision input for the base-coordinate
pilot. (Bonus on a PASS or a saturating FAIL: the track-back yields the first
*certified* admissible-real count for {1,2,3,4,6,7} — the data point that resolves
the open "1 vs 3 vs crash" discrepancy.)

## 7. Sequence this gate sits in

1. Three-subset structural diagnostic — complete (generic-fiber memo, frozen).
2. **Gate X** — this benchmark (run once; re-run only on TECHNICAL INCONCLUSIVE).
3. If FAIL → pause the homotopy route for census scale (documented).
4. Base-coordinate interval/Krawczyk **pilot** on the same subset (exploratory; no
   amendment).
5. Decide — with the advisory — whether a methodological amendment to switch the
   confirmatory instrument is warranted. Only after the pilot result exists.

---

**Freeze line.** This preregistration is frozen prior to execution.
Gate X preregistration SHA-256: <recompute on commit>
