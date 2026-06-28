# v4 Boundary-Aware Split Priority (Path 3) — Measurement (exploratory; NULL result)

**Status.** Exploratory. v4 = v2 cone-edge driver with the ONLY change being the
split-DIMENSION choice (deterministic boundary-aware priority, memo Path 3). Frozen
v1.2 UNCHANGED. Single variable: split-dimension selection.

## Wiring soundness
- Function-by-function: classify, cone_F, full_chain_domain_guard,
  _krawczyk_cone_only, certify_box BYTE-IDENTICAL to v2; only enum differs; new
  helpers _seam_intervals / _sw / _split_dim added.
- Gate-M c3/c4/c5 on v4: PASS, identical to v2 (split choice does not change which
  boxes certify or exclude; soundness-neutral).

## Result 1 — 400k three-row (CONFOUNDED by LIFO path-dependence)
| driver | dom | excl | unres | qleft | peakq | unfinished | maxd |
|---|---|---|---|---|---|---|---|
| v2 cone-edge LIFO | 45,963 | 0 | 153,978 | 119 | 129 | 154,097 | 200 |
| v3 cone-edge FIFO | 3,187 | 0 | 0 | 393,627 | 393,626 | 393,627 | 19 |
| v4 boundary-aware | 115 | 0 | 199,847 | 77 | 86 | 199,924 | 200 |

v4 is WORSE (unfinished 199,924 vs 154,097; domain collapses to 115). BUT the
boundary-aware rule fired only 217 times in 400k boxes -> those few splits, near
the tree ROOT, redirected the entire LIFO depth-first dive into a worse region.
This measurement is CONFOUNDED by LIFO path-dependence (a second indictment of the
depth-first driver: extreme sensitivity to early split choices), so it does not by
itself cleanly answer the Path-3 question.

## Result 2 — path-INDEPENDENT volume test (DECISIVE)
Fully resolve a FIXED seam-straddling region under each split rule to equal depth
caps; count resolved vs unresolved leaves (free of traversal path-dependence).
| rule | cap | total boxes | domain | unres | resolved% |
|---|---|---|---|---|---|
| widest-axis (v2) | 14 | 23,135 | 1,584 | 9,984 | 13.7% |
| boundary-aware (v4) | 14 | 18,355 | 552 | 8,626 | 6.0% |
| widest-axis (v2) | 16 | 83,037 | 1,664 | 39,769 | 4.2% |
| boundary-aware (v4) | 16 | 69,813 | 915 | 33,906 | 2.9% |

At equal depth, boundary-aware resolves a SMALLER fraction (6.0% vs 13.7%; 2.9% vs
4.2%) with fewer domain exclusions. It does NOT reduce the volume — it is worse.

## Verdict: this deterministic boundary-aware split-priority RULE is rejected (Path 3, as implemented)
Confirmed two independent ways (confounded LIFO three-row AND clean path-independent
test). SCOPE OF CLAIM: what is rejected is THIS specific cheap, driver-only
deterministic rule (minimize post-split seam-straddle width, h/c/d candidates). It
does NOT reject all conceivable boundary-aware subdivision — a more sophisticated
split policy could still exist; this version simply did not earn further pursuit.
Mechanism: chasing the seam spends splits on h/c/d, producing thin slivers along the
diagonal WITHOUT shrinking the non-seam dims (b,e,g) that a box needs shrunk to
become excludable. Widest-axis shrinks all dims more uniformly and resolves faster.
Concrete confirmation of the memo's caveat: axis-aligned splits cannot straighten a
diagonal, and CHASING it (this rule) is worse than ignoring it. Soundness unaffected
throughout (Gate-M identical); this is purely an efficiency null.

Success signals (memo): 0/4 met (the only 'yes', bounded queue, is trivial for LIFO).

## Implication for Path 2 (coordinate-straightening) — NOT condemned, but NOT de-risked
The memo set Path 3 as a cheap de-risking probe for Path 2. The null removes that
de-risking. HOWEVER Path 3 is NOT equivalent to Path 2:
  - Path 3 keeps the diagonal and CHASES it with axis-aligned splits (slivers) -> fails.
  - Path 2 REMOVES the diagonal (true coordinate change): the seam becomes
    axis-aligned (u=pi/2), so ONE split cleanly separates valid (domain-excludable)
    from invalid, after which normal widest-axis splitting resolves the rest.
The path-independent test actually shows WHY straightening could still help where
chasing does not: the seam region is genuinely volume-hard (cap 16, 83k boxes, still
96% unresolved under widest-axis). Straightening could turn ~40k unresolved boxes
into ~1 domain exclusion + a normally-resolvable region. So Path 2's upside is
PLAUSIBLE but UNPROVEN and now UN-DE-RISKED; it remains a substrate-scale gamble.

## Recommended next step
Per the memo's decision rule, a Path-3 null points to:
  - CONSERVATIVE Path 1 (full-chain analytic pre-filter extension) as the safe,
    low-risk, composable next lever — does not close, but reliably shaves.
  - Path 2 (straightening) only after a PAPER scoping of the open unknown (do the
    non-acos seams survive the transform?) — it is the only lever attacking the
    diagonal at its root, but it is a gamble and must be scoped before any code.
Best-first / hybrid traversal remain untested and deferred.

## Files
  domain_sphere_v4_bsplit.py   v2 driver, boundary-aware split priority only
  harness_gate_m_345_v4.py     Gate-M c3/c4/c5 on v4 (PASS)
  bsplit-v4-measurement.md     this report

SHA-256 hashes for all files in this unit are recorded in `docs/SHA256SUMS`