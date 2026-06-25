# Gate X — Result Memorandum (frozen)

**Type.** Frozen record of a completed benchmark. Reports the outcome of the Gate
X feasibility benchmark declared in `gate-X-preregistration.md`. It records a
result; it makes no methodological change.

**Outcome.** **FAIL.** Full-fiber monodromy on the v2 spherical lift did not reach
trace-test completeness for the benchmark subset within the pre-declared budget.

---

## 1. Result

Per the frozen three-way outcome rule, the benchmark **FAILED**: the run reached
the declared resource limit without `is_success(MR) == true`, with intact logs and
no technical failure (clean budget exhaustion — the expected FAIL path, not an
inconclusive one).

| field | value |
|---|---|
| subset | {1,2,3,4,6,7} |
| outcome | **FAIL** |
| is_success(MR) | false |
| n_generic at cap | 329,452 |
| stopping_reason | budget_or_no_progress |
| error_kind | none |
| elapsed (incl. forensic + bounded corroboration) | 7512.7 s |
| wall-clock cap | 7200 s (2 h) |
| threads | 8 |
| random seed | 20260624 |

## 2. What the run shows

At the 2-hour cap the monodromy fiber had reached 329,452 generic solutions and
`is_success` was false: trace-test completeness was not reached within budget. The
measurement is stable — an earlier (procedurally TECHNICAL INCONCLUSIVE) run on
the same instrument reached 329,458, reproducing to within 6 solutions.

The failure mode is precise, and it is not merely discovery volume. The final
monodromy loop added only ~10 new solutions, i.e. discovery was near no-progress
saturation. The post-cap completeness verification then tracked all 329,452 paths
and aborted with "Lost solution during parameter homotopy" — the trace test on a
fiber of this size is both expensive and numerically fragile on this system. So
the operative obstacle is: **the generic fiber is large enough (~3×10⁵) that
trace-test completeness cannot be reached within budget**, not that the solutions
are merely slow to enumerate.

## 3. Instrument provenance (honest record)

This FAIL was produced by the corrected, smoke-test-validated runner. Three prior
runs on this benchmark were **TECHNICAL INCONCLUSIVE** due to instrument defects,
each found and fixed before this clean run:
1. an unbounded `verify_solution_completeness` call stranded the forensic write;
2. a wall-clock `timeout` passed as a `monodromy_solve` kwarg was silently dropped
   (it is a `MonodromyOptions` field, not a top-level kwarg) — no cap enforced;
3. a Julia top-level soft-scope assignment discarded the captured verdict
   (`is_success`/`n_generic` written to throwaway locals).
A fourth defect was in the *classifier* (reading layer, not the run): a JSON
boolean `false` was mis-bucketed as TECHNICAL INCONCLUSIVE; fixed, with the
underlying forensic unchanged. The corrected runner was validated by a 120-second
on-server smoke test (is_success=false, n_generic≈5225, forensic written cleanly,
no scope warnings) before the 2-hour run. The FAIL therefore rests on an
instrument whose verdict path was exercised and confirmed, not assumed.

## 4. Census-scale interpretation

The 2-hour cap encodes a realistic per-subset budget: at 2 h/subset × 3044 on a
single 8-core machine, the census would take on the order of 250 machine-days even
if every subset behaved. Therefore a single well-instrumented subset that cannot
reach trace-test completeness in 2 h on 8 cores documents — under a fixed,
pre-declared budget — that **full-fiber monodromy is not viable as the
census-scale confirmatory instrument on this hardware**. This is a measured
result, not an extrapolation from capped samples.

**Scaling-interpretation clause (held).** The benchmark subset is one subset,
chosen because it is best-instrumented. The FAIL is a statement about the
*plausibility of the instrument at census scale*; it is **not** a claim about the
individual difficulty of the other 3043 subsets.

## 5. Consequence

By the pre-registered sequence, this FAIL is the documented trigger to **pause the
homotopy route as the census-scale confirmatory instrument** and proceed to the
next, exploratory step: a base-coordinate interval/Krawczyk **pilot** on the same
subset (rigorous spherical AA chain, Gate-M validation before any certification
claim, frozen budget, three-way outcome). The pilot is exploratory — no amendment.
A methodological amendment to switch the confirmatory engine would be considered
only if the pilot shows the base-coordinate route can actually close.

This memo closes the homotopy-feasibility question for the spherical census.

---

### Provenance

- forensic JSON: `gate_x_forensic.json` — SHA-256 `8b5fd3b6802f303d0bae15774f3157db6677df0af37d32c5873eaf7c855e54af`
- runner: `gate_x.py` — SHA-256 `3162f2bb3ba8b3253857a87414bb3839b567b7992615a51e44d8e8db2f1bfe0e`
- preregistration: `gate-X-preregistration.md` — SHA-256 `0e41c039aed2cc2fa3f765efca59b9fed150175c4bfe1a9e404d6f856cb0a36c`
- lift: lift-generator-v2 (spec SHA-256 `5db1f12f19f17fc343de5be1c78cadf0aaccfcc6c65e1602a63313ff6e3d64e9`);
  v2 system hash (this subset) `c540c04f22a9c7d8f2afdc1d7888781d07c6ebdde46cdda83b9559e76d4f1c0e`
- HC.jl 2.20.0 ; JULIA_NUM_THREADS 8 ; earthgrid-python (8-core)
