# v3 FIFO Driver-Order Lever — Measurement (exploratory; NEGATIVE result)

**Status.** Exploratory. v3 = v2 cone-edge driver with the ONLY change being
traversal order (LIFO stack.pop() -> FIFO deque.popleft()); same classify,
pre-filter, split dimension, child construction, max_depth, r_cert. Frozen v1.2
UNCHANGED. Single variable under test: breadth-first vs depth-first.

## Wiring soundness
- Function-by-function: classify, cone_F, full_chain_domain_guard,
  _krawczyk_cone_only, certify_box all BYTE-IDENTICAL to v2; only enum differs.
- enum logic change is exactly: deque + popleft + append (same L-then-R).
- Gate-M c3/c4/c5 on v3: PASS, identical to v2 (traversal does not change which
  boxes certify or exclude).

## 100k memory-curve reconnaissance
peak_queue 93,626, RSS 57 MB, depth reached 17, unres 0, excl 0, dom 3,187.
Depth histogram: pure binary doubling (1,2,4,8,16,...,1344) -> FIFO expands the
full tree level by level, pruning little. Memory safe to 400k.

## 400k three-row head-to-head (identical budget)
| driver | dom | excl | unres | qleft | peakq | UNFINISHED | cert | maxd |
|---|---|---|---|---|---|---|---|---|
| v1.2 base LIFO | 7,081 | 0 | 192,848 | 143 | 148 | 192,991 | 0 | 200 |
| v2 cone-edge LIFO | 45,963 | 0 | 153,978 | 119 | 129 | 154,097 | 0 | 200 |
| v3 cone-edge FIFO | 3,187 | 0 | 0 | 393,627 | 393,626 | **393,627** | 0 | 19 |

UNFINISHED = unres + queue_left (the honest total; LIFO marks work at max_depth,
FIFO leaves it in the queue). FIFO's unres=0 is NOT pruning success — it is
mechanical (FIFO never reaches max_depth=200 within budget). On the honest metric
FIFO is the WORST.

## Verdict: pure FIFO breadth-first REJECTED as the next lever (not driver-order in general)
The FIFO experiment is a clean negative result for PURE breadth-first traversal. It
confirms the remaining wall is not merely LIFO queue starvation: pure FIFO builds a
large shallow frontier, reaches only depth 19 at 400k boxes, produces no
exclusions/certifications, and leaves MORE unfinished work than v2 LIFO (393,627 vs
154,097). Bad-signal across the board (queue explodes, depth shallow, no exclusions,
memory grows with little pruning). Pure FIFO trades LIFO's depth starvation for
breadth explosion; it does not solve the wall.

IMPORTANT (scope of the claim): this rejects PURE FIFO as the immediate next lever.
It does NOT disprove driver-ordering in general. Best-first, hybrid DFS/BFS, and
priority search remain UNTESTED and could still be worthwhile later — just not as
the next step. Best-first is not pursued now because it was gated on FIFO showing
improvement (it did not), and pursuing it now would chase the hypothesis past the
data. The driver-order hypothesis is WEAKENED, not globally disproved.

## Refined diagnosis (the real value of this negative result)
The wall is NOT merely LIFO queue starvation. LIFO and FIFO fail at OPPOSITE ends:
LIFO reaches the resolving depth (~40-54, where boxes are small enough to
exclude/certify) but only in a narrow slice; FIFO covers breadth but cannot reach
resolving depth without an exponential frontier (~2^45 boxes). Resolving the CURVED
acos domain boundary needs depth AND breadth at once -> a box-VOLUME problem around
curved domain seams, not simply LIFO-vs-FIFO. No reordering of the same axis-aligned
subdivision tested so far escapes it (best-first/hybrid untested).

## Implication for next lever (volume reduction; SCOPE before build)
Per the pre-stated rule, the next direction is volume reduction. A short design memo
should compare two paths BEFORE any build is chosen:
  CONSERVATIVE — full-chain analytic pre-filter extension (radial r16..r19 acos
    edges and other domain inequalities). Extends the proven-sound cone-edge win;
    reduces boxes entering subdivision. Low methodological risk.
  AMBITIOUS — coordinate-straightening (UNPROVEN; scope on paper first). The
    dominant boundary r=c, r=d is DIAGONAL in (h,c)/(h,d); a change of variable
    (e.g. u=h+c) makes r=c axis-aligned (u=pi/2), so one split separates
    valid/invalid instead of staircasing a curve. BUT: the system has BOTH h+c and
    h+d seams plus the rest of Rao's chain — one transform may straighten one family
    while complicating another. It also changes the Jacobian/Krawczyk geometry, the
    registered box shape, and the TABLE1-derived domain interpretation. This is a
    bigger methodological move than the pre-filter or FIFO and must be scoped on
    paper (soundness + Jacobian-transform analysis) before any implementation.
  (Monotone across-inflection enclosures remain available for non-domain seams only;
   they cannot touch the genuine acos domain edge where acos is undefined.)
Best-first / hybrid / priority traversal remain untested and are deferred, not ruled
out.

## Files
  domain_sphere_v3_fifo.py    v2 driver, FIFO traversal only (+depth hist, peak q)
  harness_gate_m_345_v3.py    Gate-M c3/c4/c5 on v3 (PASS)
  fifo-v3-measurement.md      this report

SHA-256 hashes for all files in this unit are recorded in `docs/SHA256SUMS`