# Lever 2 — Monotone Across-Inflection Enclosure (atan/acos): SOUND but INERT on the
# binding bottleneck (diagnostic result)

**Status.** Exploratory. First arithmetic-substrate change since v1.2. The substrate
(aar_sphere_v2_monotone.py, a thin EXTENSION of aar_sphere.py) is per-node validated
and sound. Wired as domain_sphere_v5_mono.py (v2 cone-edge driver, FN binding swapped
to MONO_AA_FN/MONO_DUAL_FN, all functions byte-identical to v2). Frozen v1.2 UNCHANGED.

## What the lever does
Removes INFLECTION-only SplitNeeded for atan/acos: a box straddling the inflection at
0 (but strictly inside the domain) gets a rigorous monotone enclosure (value =
endpoints; derivative = rigorous interval) instead of subdividing. PRESERVES the acos
DOMAIN-edge split/exclude (DomainError outside [-1,1]; SplitNeeded straddling +-1 or
when 1-umax^2 not certifiably > 0). No hand-tuned derivative cap.

## Per-node validation (both layers, separately) — PASS
  identity      : DualRS / SplitNeeded / DomainError / AAr all `is` aar_sphere's
                  (thin extension, no copied-infrastructure hazard).
  delegation    : off-inflection, mono == affine byte-identical (12,000 value +
                  12,000 dual boxes, 0 differ).
  value layer   : straddle-0 atan/acos 0 containment violations, 0 unexpected splits;
                  acos edge +-1 0 silent finite enclosures (split/domain only).
  derivative    : straddle-0 atan/acos 0 value & 0 gradient violations; acos near +-1
                  returns finite up to 1.93e+02 with NO cap; 0 silent on +-1.
  FN swap audit : sin/cos/tan are the SAME function objects as the affine FN; only
                  atan/acos swapped.

## Gate-M on v5 — PASS (the at-risk criterion held)
  c4 root certification: 'unique' at r=3e-4, 1e-4 (split at 3e-3, 1e-3) — SAME as v2.
     The large-but-finite near-edge acos derivative did NOT ruin contraction at root.
  c5: excluded=311 split=89 (v2: excluded=307 split=93) — a faint favorable shift on
     globally-sampled valid boxes.
  c3: domain-edge boxes classify cleanly.

## 400k head-to-head (v2 cone-edge LIFO vs v5 cone-edge + monotone LIFO) — IDENTICAL
| driver | dom | excl | unres | qleft | unfinished | maxd |
|---|---|---|---|---|---|---|
| v2 cone-edge LIFO      | 45,963 | 0 | 153,978 | 119 | 154,097 | 200 |
| v5 cone-edge+monotone  | 45,963 | 0 | 153,978 | 119 | 154,097 | 200 |

BYTE-IDENTICAL. The monotone substrate changed ZERO classifications in the 400k dive.

## Diagnosis (instrumented) — the lever is INERT here, and WHY
Over a 120k-box v5 dive, the across-inflection (monotone) branch was taken:
  atan: 0     acos: 0   (all 180,851 acos calls delegated to the affine form;
                          every arg was non-straddling or at a domain edge)
=> The LIFO + cone-edge dive is confined to the acos DOMAIN-diagonal region
   (h+c->pi/2). There, every acos arg is away from 0 (delegates, identical) or at the
   domain edge (splits/domains, identical). The acos INFLECTION (arg->0, the radial
   r16..r19 nodes; 3,702/80,000 near 0 from the Path-1 analysis) lives in the physical
   region the dive never reaches within 400k boxes — it is stuck on the domain diagonal
   first. The inflection is NOT on the critical path of the binding bottleneck.

## Verdict: sound + correct, but does not move the binding metric
This is NOT an efficiency failure (unlike v3 FIFO / v4 boundary-aware, which were
worse). Lever 2 is per-node sound, composes for free (delegates to affine off the
inflection, does not hurt on this measured path, and delegates exactly to affine off-inflection), 
and would help where the inflection binds. It simply does not address the CURRENT binding 
bottleneck (the domain diagonal), so it produces 0 change on the 400k LIFO metric. Its value 
here is DIAGNOSTIC: removing the inflection pressure and observing zero change shows the 
inflection is not the binding constraint on the measured 400k LIFO+cone-edge path., isolating t
he acos domain diagonal even more definitively as the single wall.

## Implication
Re-confirms, from a third independent angle (after cone-edge and Path-1), that the acos
DOMAIN diagonal is THE bottleneck. Cone-edge shaves its non-physical side; Path 1 is
empty; Lever 2 removes a non-binding inflection pressure. The only currently identified 
lever that removes the diagonal geometry itself is Path 2 (coordinate-straightening), 
which REMOVES it. Lever 2 should be RETAINED as a validated, available substrate 
(it may matter as a secondary bottleneck after the diagonal is addressed, e.g. post-Path-2), 
but it does not close the current gap.

## Recommended next step
Path 2 (coordinate-straightening) PAPER SCOPING — the open unknowns: do the non-acos
seams (cos(2x) / atan inflections) survive the (b, u=h+c, v=h+d, e, g, h) transform,
and what is the Krawczyk conditioning near the straightened edge u=pi/2. No code until
the scoping memo resolves these. Best-first/hybrid traversal remain untested, deferred.

## Files
  aar_sphere_v2_monotone.py   thin-extension monotone substrate (+ MONO_*_FN)
  harness_mono_value.py       value-layer per-node validation
  harness_mono_dual.py        derivative-layer per-node validation
  domain_sphere_v5_mono.py    v2 cone-edge driver, FN swapped to monotone (only change)
  harness_gate_m_345_v5.py    Gate-M c3/c4/c5 on v5 (PASS)
  lever2-monotone-finding.md  this report

SHA-256 hashes for all files in this unit are recorded in `docs/SHA256SUMS`