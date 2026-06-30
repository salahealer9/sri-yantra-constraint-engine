# Polynomialization Probe — subset {1,2,3,4,6,7}: CANDIDATE root-covering lift;
#   known-root GATE PASSED; root-covering obligations enumerated (NOT yet a theorem)

**Status.** Exploratory probe (no driver/engine changes). Tests whether the absence branch
(INFEASIBLE_CERTIFIED) is feasible by building a root-covering polynomial lift, verifying the
known-root residual, and estimating the path count. Makes NO infeasibility claim. Frozen
engine UNCHANGED.

## Hard ordering (enforced in code)
  1. build (S,C)-atom lift (serial)  2. inventory exclusions/denominators
  3. GATE known-root residual (serial; STOP if fail)  4. path-count only after gate passes.

## Result
  OBSERVED
    lift: 50 variables, 50 equations (SQUARE)
    known_root_residual_max = 6.66e-16  -> GATE PASS. This VALIDATES THE IMPLEMENTATION on
                                          the benchmark solution (all defining relations,
                                          Pythagorean constraints, and 6 cone constraints
                                          hold at the known root to machine precision).
                                          It does NOT prove universal root-covering -- that
                                          remains a proof obligation, reduced (not discharged)
                                          to the enumerated cases below.
    total-degree (Bezout) bound = 1.47e24   (naive; structure NOT exploited)
    mixed_volume = backend_absent           (needs phcpy / Julia HC.jl on the 8-core server)
    zero-dimensional = numerically apparent  (square system; known root isolated by 2b)

  PROOF OBLIGATIONS (root-covering is not proven by the residual; these remain)
    6 DANGER denominators (the obligations that matter), each needs "numerator vanishes too
    OR point geometrically invalid":
        sin(x5), sin(x6), sin(x7), sin(x10)   [node sines in U/t denominators]
        sin(v9+c+d-v12)                        [node-bearing sum, x11a]
        cos(d+g-U7)                            [node-bearing sum, t]
    9 structural denominators  -> discharged by the full-chain domain guard (sin of pure
                                  base-angle sums; nonzero wherever the chain is real)
    10 branch denominators     -> discharged by atan principal branch (cos(node)>0),
                                  base cos nonzero in B_sphere, half-angle t!=pi
    branch/range obligations: atan principal branch (cos>0 excludes node=+-pi/2); acos sin>=0
                              (x1,x2); F1/F7 angle-equality via principal branch; F2 sin zero
                              unique in (-pi,pi); global zero-dimensionality.

## Lift design (root-covering, not bijective)
Each acos/atan node N carries (S_N,C_N)=(sin,cos) with S_N^2+C_N^2=1 and a defining relation
from its tangent (atan: S*den-C*num=0) or cosine (acos: C*cos(div)-cos(r)=0). Base angles
carry (s,c) atoms; r=pi/2-h. Angle SUMS use addition formulas (polynomial). Constraints:
  F1,F7  angle-equality  -> sin(xi-xj)=0  (principal branch)
  F3,F4,F6  cos(sum)-cos2x/cosx -> cos(sum)*C - (2C^2-1)=0   (cleared cos(x), cos2x=2C^2-1)
  F2  d-U7-rT=0 -> sin(d-U7-rT)=0   (range obligation)
Spurious polynomial roots are allowed (rejected later by full-chain guard + 2b certifier);
only the no-genuine-root-lost direction is required.

## Reading of the two headline numbers
  danger-denominator count = 6  -> the root-covering proof is a SHORT enumerable list, not a
                                   research problem. Encouraging for step 1 of the absence chain.
  path count: Bezout 1.47e24    -> a WARNING LABEL, not a usable path count. The naive dense
                                   bound is MEANINGLESS for feasibility: it ignores the
                                   triangular node structure (every node defined by earlier
                                   nodes + 6 base atoms). The decisive count is the sparse /
                                   MIXED VOLUME after exploiting that structure or eliminating
                                   node variables. CAUTION: elimination may still produce
                                   high-degree dense expressions, so the reduced mixed volume --
                                   NOT the structure observation -- is what decides. The
                                   structure is favorable, not decisive. Backend absent here.

## Verdict
Green with caveat. Lift implementation: passes. Absence branch: still undecided.
Next decisive number: mixed volume exploiting structure (not the naive 1.47e24).

## Conclusion (no infeasibility claim)
The IMPLEMENTATION is validated (gate passed) and the structure is favorable (triangular; only
6 danger obligations). The absence branch is NOT yet decided. The 1.47e24 naive bound is not
the path count; the decisive number is the structured/reduced mixed volume, which is unknown
until a backend computes it -- and elimination could still inflate degrees, so 'favorable
structure' is not yet 'small count'. Deciding it requires, in order: (1) a mixed-volume backend
(phcpy / Julia HC.jl) on the structured lifted system; (2) if that is inflated, symbolic/sparse
node elimination to a 6-base-variable support system; (3) mixed volume on the reduced 6-in-6.

## 8-core design
--workers defaults to min(8, cpu_count); --workers 1 deterministic fallback. Lift construction
and the residual gate are SERIAL and reproducible; only the mixed-volume step is parallel-capable
(gated on a backend). OMP_NUM_THREADS=1 set to avoid oversubscription; JULIA_NUM_THREADS honored
if a Julia backend is wired. Manifest records workers, cpu_count, seed, command, engine_sha,
probe_sha, python/platform, timestamps.

## Next
1. Stand up a mixed-volume backend on the server (phcpy or Julia HC.jl) and compute the mixed
   volume of the reduced system -> the number that decides absence-branch practicality.
2. Discharge the 6 danger denominators (numerator-also-vanishes or geometric-invalidity each).
3. Only then revisit whether INFEASIBLE_CERTIFIED is operationally reachable.

## Files
  polynomialize_probe_123467.py            the probe (lift + gate + inventory + path-count)
  polynomialize_probe_123467.manifest.json run manifest (all required fields)
  polynomialize-probe-findings.md          this report

SHA-256 hashes for all files in this unit are recorded in `docs/SHA256SUMS`