# Large-Box Interior Exclusion — Diagnostic Findings (Day 2 of Direction B)

**Status.** Exploratory probes (no driver changes). Target from yesterday: make interior
exclusion fire on larger boxes. These probes locate the bottleneck precisely and rule out
the first-order remedies, pointing to the one fix that addresses the root cause. Frozen
v1.2 UNCHANGED.

## Benchmark
Exclusion-radius test: on off-root physical-interior boxes, the LARGEST radius at which a
method proves some selected constraint excludes 0. Larger radius = exclusion fires on
bigger boxes = shallower subdivision. Coordinate-independent (run in OLD coords; the frozen
engine and 2b both benefit).

## Diagnostic (indicative, not a certificate): the limit appears to be ENCLOSURE
## LOOSENESS, not true constraint behavior
On every exclusion-FAILING box (radius 0.02), at least one selected constraint has its
SAMPLED true range (dense grid) MISSING 0 while the AA enclosure CONTAINS 0:
  AA-enclosure width / sampled-range width = 1.5x .. 3.7x (typically ~3x).
CAVEAT: the sampled true range is DIAGNOSTIC, not a certificate -- a finite grid can miss
a sign change between samples, so this INDICATES (does not prove) that a tighter rigorous
enclosure should exclude. It is enough to identify the bottleneck and choose the target;
only a rigorous second-order enclosure can actually certify exclusion.
=> A ~3x tighter enclosure SHOULD exclude these boxes at radius 0.02, where the current AA
   needs ~0.005-0.01. Across 6 dimensions, firing 2-4x larger per dim is a large depth cut.
   The wall appears to be enclosure strength, and it looks tightenable.

## First-order remedies RULED OUT (they inherit AA's first-order error)
The natural cone_F enclosure is already AFFINE arithmetic (first-order, correlation-
tracking), not a crude interval extension. So forms built from the same AA value/Jacobian
do not help:
  - CENTERED mean-value F(x0)+J(X).(X-x0): 13 ties, 2 worse, 0 wins vs natural.
  - PRECONDITIONED KRAWCZYK exclusion (C=inv(midpoint J); K(X) and X disjoint): same radius
    as natural in 18/18, 0 wins.
  Reason: AA's value enclosure AND its Jacobian enclosure are BOTH ~3x loose; the
  mean-value/Krawczyk remainder Sum rad(J(X)).r inherits that ~3x. Algebraically these are
  first-order forms over the same loose AA quantities.
  - 1-LEVEL MINCE (slice the box, union the slice enclosures, exclusion-test only): ~1.25x
    larger radius (7/12) at 3-5x eval cost -- modest, and it is just "subdivide for the
    test", trading cost for tightness like B&P itself.

## aar.py is not over-condensing
AAr keeps all noise symbols (no capping/merging). Each mul and transcendental adds ONE
fresh uncorrelated symbol for its nonlinear remainder; over ~40 nodes these accumulate to
the ~3x over-estimate. There is no cheap condensation knob to relax -- the looseness is
inherent to FIRST-ORDER AA.

## The lever: SECOND-ORDER enclosure (Taylor models), F3 as highest-leverage target
First-order is exhausted; the principled fix tracks the polynomial part EXACTLY and bounds
only the high-order remainder, reaching near the true range:
  - TAYLOR MODELS / quadratic forms for the cone constraints: the only method that attacks
    the ~3x first-order looseness at its root. Substantial build (degree-2 polynomial +
    interval remainder through the chain), but it is the right tool.
  - CONSTRAINT-SPECIFIC F3 FIRST: F3 is consistently the TIGHTEST (1.5x) and its SAMPLED
    range is consistently NEGATIVE (misses 0) on the failing boxes -- its AA enclosure barely
    straddles 0 (e.g. [-0.38, +0.04]). A targeted second-order/analytic tightening of F3
    ALONE may fire rigorous exclusion on most failing boxes at the cheapest cost. Start here.

## Recommended next build
A Taylor-model (or quadratic-form) enclosure probe, PRIORITIZING F3, benchmarked on the
exclusion-radius test. Success criterion: enclosure within ~2x of the true range, so
exclusion fires at >=2x larger radius than current AA on the failing interior boxes. Keep
it a PROBE (constraint enclosure only, no driver) until the radius win is demonstrated.

## Ruled-out this session (record)
centered mean-value (first-order) - no gain; preconditioned Krawczyk exclusion - no gain;
1-level mince - ~1.25x only. Root cause: first-order AA ~3x loose. Next: second-order.

## Files
  probe_exclusion_centered.py     centered + preconditioned-Krawczyk exclusion probes
  exclusion-strength-findings.md  this report (probes inline, reproducible)

SHA-256 hashes for all files in this unit are recorded in `docs/SHA256SUMS`