# Exploratory v2 Lever — Cone-Edge Analytic Domain Pre-filter (standalone, frozen unit)

**Status.** Exploratory. Standalone, NOT wired into the frozen v1.2 instrument.
Frozen here as its own provenance unit before any driver integration.

## What it is
A cheap, rigorous shortcut that excludes boxes PROVABLY entirely non-physical for
the base acos nodes x1, x2, with zero acos/AA evaluation. Targets the dominant
seam identified by the frozen v1.2 pilot (acos domain edge at arg=1; curved
surfaces r=c, r=d).

## Soundness — proof-by-inequality (this is the proof)
x1 = acos(cos(r)/cos(c)), r = pi/2 - h, with r,c in (0,pi/2): cos positive and
decreasing, so x1 is real iff cos(r)/cos(c) <= 1 iff r >= c iff h <= pi/2 - c.
A box is ENTIRELY invalid for x1 iff its most-validity-favorable point already
fails. That point maximizes (pi/2 - c - h): smallest h AND smallest c. Hence

        box entirely invalid for x1  <=>  h_lo + c_lo > pi/2           (x2: + d_lo)

Quantifier direction is essential: c_lo / d_lo (the easiest point), NOT c_hi/d_hi.
If even the easiest point fails, all points fail. The reverse would exclude valid
sub-regions. Excluding such a box is sound under full-chain-real semantics because
x1 (a chain node) is undefined at every point, so no valid figure exists in the box.

## Implementation validation — harness (this validates the code, not the math)
harness_prefilter_v2b.py, 20,000 random boxes in B_sphere:
  - soundness violations (excluded box containing an engine-valid point): 0   [req 0]
  - AA-rigor red flags (guard 'ok' on an excluded box): 0                      [req 0]
  - guard breakdown on fired boxes: 6326 'domain' (agree), 2089 'split'
    (pre-filter soundly STRICTER than the loose AA enclosure), 0 'ok'.
The 'split' disagreements are desirable: the analytic test proves empty where the
AA enclosure of cos(r)/cos(c) straddles 1 and can only subdivide.

## Standalone yield (uniform grid, comparable to smoke diagnostics)
  K=4: excludes 30% with 0 acos (full guard domain-excludes 12%)
  K=5: excludes 34% with 0 acos (full guard domain-excludes 18%)

## What is NOT yet established
Whether wiring this into the driver CLOSES the size-six subset or merely MOVES the
wall. The cone-edge filter does not catch boundary-STRADDLING boxes (those still
need subdivision or a full-chain extension). That is the next, purely empirical,
measurement: branch-and-prune box-count vs the frozen v1.2 baseline
(boxes 3,000,000 / domain 52,300 / excluded 0 / unresolved 1,447,632 /
queue ~137 / certified 0 / bound_by max_boxes).

## Files (this frozen unit)
  prefilter_v2.py            the sound cone-edge pre-filter (proof in docstring)
  harness_prefilter_v2b.py   soundness + ok/split breakdown + AA-rigor check
  harness_prefilter_v2.py    soundness + consistency + yield
  prefilter-v2-report.md     this report

SHA-256 hashes for all files in this unit are recorded in `docs/SHA256SUMS`