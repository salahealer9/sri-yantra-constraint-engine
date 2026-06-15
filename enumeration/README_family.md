# Tier-2 family campaign — coefficient-parameter homotopy

**Status: DEV / pre-confirmatory. Not part of any registered run. To be frozen
and hash-pinned (with a prereg amendment if already deposited) before the
confirmatory campaign.**

## Why this replaces 816 ab initio solves

The single-subset proof of concept (`solve_1_2_3_4_8.jl`) reported
`mixed_volume = 286,144` — that many paths *per subset*, ab initio. At the
observed tracking rate that prices the naive campaign at roughly 233 million
paths (~order 100 days on 4 cores).

But the 816 systems are not independent: every subset shares the identical
28-equation chain + F1 + F2, and differs only in which 3 polynomials from an
18-element pool are appended. So the whole campaign is **one parameterized
family per degree type**:

    chain (28) + F1 + F2 + slot1 + slot2 + slot3  =  33 eqs in 33 vars
    slot_j = Σ_k a_jk · P_k(x)   over the slot's degree class

with each concrete subset a 0/1 parameter point. Per type:

1. `monodromy_solve` at generic complex parameters p0 → N* generic solutions
   (two independent runs, unioned at common parameters);
2. `verify_solution_completeness` (trace test, Leykin–Rodriguez–Sottile) →
   completeness certificate for the generic solve;
3. parameter homotopy p0 → each subset: **N\* paths per subset** instead of
   286,144.

By the parameter-continuation theorem (Sommese–Wampler), for a trace-certified
generic start every isolated solution of every target subset is an endpoint of
those N\* paths.

## Degree types

Pool: 9 linear {F5,F7,F10–F15,F20} and 9 quadratic {F3,F4,F6,F8,F9,F16–F19}
polynomials in the 33 master variables.

| type | (lin,quad) | subsets |
|------|-----------|---------|
| L3   | (3,0)     | 84      |
| L2Q1 | (2,1)     | 324     |
| L1Q2 | (1,2)     | 324     |
| Q3   | (0,3)     | 84      |

Total 816 = 815 well-posed + the rank-deficient triple {8,9,16} (kept in the
sweep, flagged `expected_degenerate`, as the Gate-1 consistency check: it must
NOT yield certified isolated solutions).

## What is new relative to lift_poc.py, and what was validated

- Chain extended by x17, x18, x19 and the (Q20,U20), (Q21,U21) pairs — 7 new
  auxiliaries, 33 variables total. Q21 uses the corrected (3.14b) form
  (x19/x18).
- Radial constraints in **squared form** (e.g. F16 = r16²−r17² =
  (d+e)²+x16²−(b+c)²−x17²): polynomial in existing chain variables, so **no
  new sqrt auxiliaries** and, over the reals, no spurious branches (both radii
  are nonnegative). Square-root sign branches remain only x1, x2, w.
- `lift_family.py` validation against the frozen v0.1.0 engine:
  - chain identities at 20 random valid figures: max 2.8e-16;
  - each of the 18 pool polynomials equals factor·engine_Fk at Rao's six
    Table 3 rows + plane optimum + 12 random points: worst 3.3e-16;
  - full 33×33 system vanishes at each Table 3 solution under its own subset
    parameters, at table precision (~1e-6, Rao's 6 digits);
  - monodromy seed: plane optimum Newton-polished to |F1|,|F2| < 1e-16;
    residual on all 30 lifted fixed equations 1.1e-16.

Derived factors (poly_Fk = factor · engine_Fk):
F5,F7,F10,F11,F12,F20: 1 · F13,F14,F15: 2 · F3,F4,F6: 2 ·
F8: −(r16+1) · F9: −(r17+1) · F16: r16+r17 · F17: r18+r19 ·
F18: r16+r18 · F19: r17+r19. All factors are strictly nonzero on the
admissible branch, so zero sets coincide exactly where it matters.

## Running

```bash
julia -e 'using Pkg; Pkg.add(["HomotopyContinuation","JSON"])'
python3 enumeration/lift_family.py            # regenerate + revalidate locally
julia -t 4,1 family_solve.jl --type=Q3 --max-targets=3   # smoke test
julia -t 4,1 family_solve.jl --type=Q3        # one family
julia -t 4,1 family_solve.jl                  # full campaign
```

(`-t 4,1` per the HomotopyContinuation.jl threading advice: 4 compute
threads, 1 interactive.)

Output `family_results.jsonl`: per-family summary records (N*, trace-test
verdict, run agreement) and per-subset records (paths, failures, real /
admissible / certified-distinct counts, admissible (b,c,d,e,g) vectors,
runtime). The file is opened in append mode — delete it between full reruns
or records will duplicate.

**Per-subset completeness rule (matches the pre-registration downgrade
clause):** a subset's negative is completeness-bearing only if the family's
trace test passed AND that subset's parameter homotopy had zero genuine path
failures (paths at infinity are not failures). Otherwise the record is
downgraded to "no solution found".

## Mandatory cross-check before any campaign run

Subset {1,2,3,4,8} (family Q3) must be solved both ways:

1. the finished ab initio run (`solve_1_2_3_4_8.jl`, mixed volume 286,144) —
   keep its full output;
2. the parameter homotopy from this driver.

The admissible real (b,c,d,e,g) solutions must agree (and contain Rao's
Table 3 row 0.463752, 0.223255, 0.288990, 0.488181, 0.106157). The pool
polynomials for F3, F4, F8 are byte-identical to the ab initio script's, so
agreement is a genuine test of the family machinery, not of the lifting.

## Caveats (stated, not hidden)

- The emitted Julia was written against the HomotopyContinuation.jl source
  (signatures of `monodromy_solve`, `verify_solution_completeness`,
  `unique_points`, `certify(...; target_parameters)`, `is_at_infinity`
  verified upstream) but has not itself been executed in the generating
  environment, which has no Julia. The smoke test is the first execution.
- The 0/1 target parameters are non-generic points of the family. Isolated
  target solutions are still endpoints of the N* paths, but paths may end
  singular, coalesce, or diverge there — that is expected behaviour, handled
  by the certify/distinct count and the downgrade rule, not an error.
- Monodromy completeness is heuristic until the trace test passes; the
  `trace_test_passed` field is the certificate. If it fails for a family,
  that family's negatives are not completeness-bearing (the JSONL already
  encodes this).
