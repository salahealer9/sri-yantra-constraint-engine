# Rounded-vs-float calibration (the §B2(iv) gate)

Script: `calib.py`. Rigorous AA (`AAr`) = float center/coefficients + a
non-cancelling, conservatively-bounded error term, with outward-rounded
enclosures. Validated: `AAr` encloses the float-AA enclosure and brackets the
engine on all 20 constraints.

## Fundamental quantities (transfer to any future implementation)

Enclosure-width ratio (rigorous / float) at Rao A root, box radius r = 3e-3:
**1.0000 on all 20 constraints.** Accumulated rounding (~1e-14) is negligible
against the affine radii (~1e-3), so rigorous arithmetic does not widen the
enclosures — the quantitative confirmation of the earlier margin argument
(Krawczyk contraction 0.169 cannot be flipped by 1e-14).

Box-count ratio (Rao A, both modes complete): **1.000** — 58,731 boxes
identical. The search tree is byte-for-byte the same under rigorous arithmetic.

## Implementation-dependent cost (Python; Julia would reduce)

| metric | float | rounded | ratio |
|---|---|---|---|
| box/s | 1264 | 792 | — |
| per-box cost | — | — | **1.60×** |
| runtime (Rao A) | 46.5 s | 74.2 s | 1.60× |

The entire cost of rigor is a 1.6× per-box constant in Python, from carrying the
error term. None of it is box inflation.

## Memory stability (DFS-bounded)

Peak queue and max subdivision depth, completing subsets:

| subset | class | boxes | cert | peak queue | max depth | done |
|---|---|---|---|---|---|---|
| {1,2,3,4,8} | reference | 58,731 | 1 | 24 | 33 | yes |
| {1,2,8,9,10} | near-rank (8,9 pair) | 49,483 | 1 | 22 | 33 | yes |
| {1,2,17,18,19} | radial-heavy (3 of {16,17,18,19}) | 65,597 | 0 | 18 | 25 | yes |

Max depth ~33 ≈ 5 dims × ~7 bisections, exactly the DFS bound. Peak queue stays
~20. Memory is not a campaign hazard for well-posed subsets. (DFS confirmed:
LIFO stack, depth-bounded.)

## Hazard hypothesis — not supported (so far)

Registered prediction: subsets near the radial dependency structure exhibit
above-median box counts. **Both strongest candidates behaved ordinarily** — the
8,9-pair subset (49k boxes, fewer than Rao A) and the three-of-four radial subset
(66k). This suggests a sharp dichotomy — exactly rank-deficient (non-terminating,
Gate-1 excluded) vs well-posed (uniformly tractable) — rather than a difficulty
gradient near the dependency. n = 2 on hazards; "no monster found" is not "no
monster exists," but the two most principled candidates came up empty.

## Preliminary campaign implication

All box counts observed so far (8 panel + 3 hazard subsets) sit in a ~2.5× band
(49k–130k); no order-of-magnitude tail seen. At rounded-Python rates
(~800 box/s) a typical subset is ~60–160 s, so 815 plane subsets ≈ ~25 h
single-core ≈ ~6–7 h on 4 cores — a weekend job in rigorous Python, faster in
Julia. **This is contingent on the full random-sample box-count distribution
staying in the observed band**, which the landscape study (Study A) must confirm.

## What this does not establish (owed next)

- Study A (random-sample landscape): unbiased median/quantiles of box count and
  feasible fraction across the 815. The band above is from a handful of subsets.
- Study B (hazard scan): broader targeted probing; the two probes here are not a
  scan.
- Gate M on the *frozen* rounded tool: `AAr` is a calibration vehicle; the frozen
  confirmatory implementation must pass M1/M2 after the freeze, per Amendment-02.
- Finer r_cert (if adopted) shifts absolute counts; the rigor ratios (~1) should hold.
