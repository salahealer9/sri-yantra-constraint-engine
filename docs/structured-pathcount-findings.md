# Structured path-count {1,2,3,4,6,7}: node-definition COVER DEGREE = 2^19 EXACT; backend
#   artifact exported. Decisive mixed volume deferred to a backend. NO infeasibility claim.

**Status.** Exploratory probe (no driver/engine changes). Follows the polynomialization probe:
exploits the triangular structure to isolate the EXACT structural factor of the lift's path
count, and produces the turnkey artifact for an exact mixed-volume run. Frozen engine UNCHANGED.

## Structural result (verified in-sandbox, rigorous)
Every one of the 19 nodes' defining equations is LINEAR in its own (S_N,C_N):
  atan nodes:  S_N*den - C_N*num = 0   (a line through the origin)
  acos nodes:  C_N - const = 0         (x1, x2)
intersected with the unit circle S_N^2 + C_N^2 = 1. A line through the origin meets the circle
in exactly 2 antipodal points; C_N=const meets it in exactly 2 (sin=+-). VERIFIED: all 19 nodes
have degree exactly 1 in their own (S,C). Therefore each node relation is a degree-2 algebraic
cover over its inputs, and the node-DEFINITION layer is a triangular cover of

        cover degree  =  2^19  =  524,288   (EXACT)

This is the branch CAPACITY the lift introduces -- not (yet) a factor of the final path count.

## What this settles, and what it does NOT
SETTLED (rigorous, here): the node-definition layer is a triangular degree-2^19 cover of the
base variables. Hence any dense Bezout count that ignores this structure (e.g. 1.47e24) is
MEANINGLESS. The triangular structure is real and quantified, not asserted.

NOT SETTLED -- and an explicit CAUTION against the earlier overclaim: 2^19 is the node-cover
degree, NOT a proven factor of, or floor on, the full-system mixed volume. The six cone
constraints SELECT sheets: a degree-2 cover can collapse to one surviving branch once a
constraint is imposed (toy: y^2=1 has two branches; y-1=0 leaves one). How many of the 2^19
sheets survive the six constraints is EXACTLY what the mixed volume measures. So:

  full_lift_path_count  =  mixed_volume(full structured system)   <-- the decisive quantity
                           (NOT 2^19 * N_base; the constraints may cut the cover, not just filter)

The decisive number is the mixed volume of the full structured lifted system (or of a
reduced/eliminated support system), and it requires a polyhedral backend to compute.

## Backend artifact (turnkey)
  lift_123467_hc.jl  -- the full 50-var, 50-eq system in HomotopyContinuation.jl syntax, ending
  in `mixed_volume(F)`. On the 8-core server:
      julia -e 'using Pkg; Pkg.add("HomotopyContinuation")'   # once
      JULIA_NUM_THREADS=8 julia lift_123467_hc.jl
  reports the EXACT mixed volume = the decisive path count. (phcpy is an alternative backend;
  it needs the compiled PHCpack, not pip -- HC.jl is the lighter install.)

## No infeasibility claim
This probe isolates a structural factor and produces a backend artifact. It does NOT claim
INFEASIBLE_CERTIFIED, does not run 3044, does not discharge the 6 danger denominators. The
path-count number (from the backend) gates whether the absence branch is worth pursuing.

## Next
1. Run lift_123467_hc.jl on the server (JULIA_NUM_THREADS=8) -> exact mixed volume = path count.
2. Interpret:
     modest mixed volume  -> absence branch may be feasible;
     huge mixed volume    -> absence branch impractical; keep presence-first certified census;
     computation explodes -> try the reduced/eliminated 6-base support system before giving up.
3. Only if tractable: discharge the 6 danger denominators, then revisit INFEASIBLE_CERTIFIED.

## Files
  structured_pathcount_123467.py   verification of 2-per-node + HC.jl export
  lift_123467_hc.jl                the exported system (run on the server for exact MV)
  structured_pathcount_123467.json structured-decomposition summary
  structured-pathcount-findings.md this report

SHA-256 hashes for all files in this unit are recorded in `docs/SHA256SUMS`