# Spherical Pilot — Gate-M + Smoke-Test Findings (overnight)

> **DOMAIN-SEMANTICS CORRECTION (post-overnight).** The pilot certifies **full
> Rao-chain-real admissibility**; selected constraints are evaluated on their
> dependency cone. The overnight smoke test below was run with a *cone-only*
> domain rule and should be read as a **cone-domain smoke test**, not the final
> pilot instrument. `domain_sphere.py` has since been patched so `classify` runs a
> **full-chain domain guard first** (all ~40 Rao nodes must be real: DomainError →
> `domain`, SplitNeeded → `split`), then evaluates `cone_F` for the six selected
> constraints. This can only shrink/defer the admissible domain, never enlarge it
> (consistent with Gate-4: a root must be a geometrically valid figure, not just an
> algebraic zero of the selected equations). Re-validation after the patch: Gate-M
> c3/c4/c5 still PASS; the K=4 diagnostic is essentially unchanged (the x1/x2 acos
> edge dominates before any unused node is reached); at small box scale the guard
> engages as intended (c5: 18/400 boxes shift excluded→split, conservatively
> refusing to act where the full construction is not yet real). Soundness:
> exclusion/certification requires BOTH the full-chain guard `ok` AND `cone_F` to
> succeed, so no box with any non-real node is ever excluded or certified.


**Status.** Exploratory. Gate-M (all 5 criteria) PASSED on the frozen substrate.
A bounded smoke test + uniform-subdivision + seam diagnostics strongly preview a
**BUDGET-EXHAUSTED** pilot outcome, with a precise, actionable root cause. The
official frozen 2 h pilot run (server) is still recommended for the record, but
the smoke test strongly predicts BUDGET-EXHAUSTED and identifies the expected mechanism. NO substrate change was made
overnight — the levers below are for review.

## 1. Gate-M validation — PASS (all five criteria)

| criterion | result |
|---|---|
| 1 mirror fidelity (chain) | 1.5e-12 (≤1e-10) ✓; iso-constraint centers diagnostic per GM-1 |
| 2 enclosure containment | 0 violations (chain + all constraints), n=1000 ✓ |
| 3 domain-edge handling | all edge boxes classify cleanly, no crash ✓ |
| 4 Krawczyk certifies Newton root | `unique` at r ≤ 3e-4 ✓ (at 3e-3 it `split`s, then subdivides — root still certifies) |
| 5 exclusion off-root | 325/400 off-root boxes excluded, 0 spuriously indeterminate ✓ |

The instrument (aar_sphere + chain_sphere + domain_sphere) is validated. cone_F
matches the full chain bit-for-bit (max |cone − full| = 0).

## 2. Smoke test (bounded preview, NOT the frozen verdict)

`enum` on B_sphere, frozen knobs except tlim=280s:
- 3,000,000 boxes processed in 115 s (hit max_boxes), `complete=False`.
- domain-excluded 52,300; **constraint-excluded 0**; certified 0;
  **unresolved (max_depth) 1,447,632**; queue never grew (~137); maxd=200.

Two pathologies visible: (a) LIFO depth-first dives to max_depth=200 in a narrow
slice of the huge box (queue stays ~137); (b) more fundamentally, almost nothing
is excludable at moderate width.

## 3. Uniform-subdivision diagnostic (separates tightness from driver)

Subdivide B_sphere uniformly, classify every box:

| K | box widths | domain | excluded | split | indeterminate |
|---|---|---|---|---|---|
| 3 | ~0.25–0.52 | 0% | **0%** | **100%** | 0% |
| 4 | ~0.16–0.39 | 12% | **0%** | **88%** | 0% |
| 5 | ~0.13–0.31 | 18% | **0%** | **82%** | 0% |

At moderate width almost every box is `split` (a transcendental seam fires before
constraints can be evaluated). **0 boxes complete the chain** → nothing is
excludable until boxes are far smaller. The binding wall is **seam density**, not
affine enclosure width.

## 4. Seam diagnosis — which transcendental forces the split

Over 4096 K=4 boxes, first node to raise SplitNeeded:

| node | count | nature |
|---|---|---|
| **acos** | **3264 (80%)** | **domain edge at arg=1** (surfaces r=c, r=d, i.e. h=π/2−c, h=π/2−d) — NOT the inflection at 0 (arg = cos(r)/cos(c) > 0 always) |
| domain | 512 | acos arg entirely > 1 (excluded) |
| atan | 320 (8%) | inflection at 0 (chain quantity changes sign) |
| sin/cos/tan | 0 | — |
| complete | 0 | — |

**Root cause.** B_sphere is mostly non-physical: x1,x2 are real only where
`h ≤ π/2 − max(c,d)`. The acos domain edge (arg=1) is a *curved* surface, and
axis-aligned branch-and-prune must carve it with enormous numbers of boxes. The
search spends its entire budget separating the valid sub-region from the invalid
bulk. This is legitimate domain work made expensive by (i) a very generous box and
(ii) a curved valid/invalid boundary. The atan splits (8%) are partly
over-conservative (atan is monotone — value-enclosable across its inflection).

## 5. Interpretation

This is a bounded preview of the **BUDGET-EXHAUSTED** mechanism anticipated by the pre-registration, with a
sharper-than-expected cause: not "affine enclosures too wide" but "the acos
domain-edge surfaces force domain decomposition of a mostly-invalid box." The
pilot did its job — it did not close, and it identified precisely why.

Scaling clause holds: this is the instrument's behaviour on one subset's box; not
a claim about the other 3043.

## 6. Concrete next levers (for review — both named in the prereg BUDGET clause)

1. **Analytic domain pre-filter ("domain decomposition").** The valid region needs
   `h ≤ π/2 − c` and `h ≤ π/2 − d` (from x1,x2 real). A cheap, rigorous coordinate
   pre-test can exclude boxes with `h_lo > π/2 − c_lo` (resp. d) WITHOUT any acos
   evaluation — pruning the invalid bulk before the expensive subdivision. Likely
   the highest-leverage change. (Other chain acos args may give further analytic
   pre-filters.)
2. **Across-inflection monotone enclosure ("enclosure sharpening").** atan and
   acos are monotone; their VALUE range over an interval is [f(endpoints)] even
   across the inflection at 0 — only the *tight affine* form needs the single-sign
   condition. Replacing SplitNeeded-at-inflection with a rigorous monotone range
   (or a two-piece affine bound split at the inflection point, no subdivision)
   removes the atan splits and the acos inflection case. Does NOT remove the acos
   domain-edge split (arg=1 genuinely must be carved).
3. **(Driver) breadth/best-first instead of LIFO depth-first**, so the budget is
   spent excluding large regions early rather than diving to max_depth in one
   corner. Secondary to (1).

Each is a substrate/driver revision requiring its own rigor argument, Gate-M
re-validation, and a pre-registration amendment before the confirmatory path —
i.e. exploratory work first, then re-freeze. None done overnight.

## 7. Recommended sequence

1. (Optional, for the record) run the frozen 2 h pilot on the server → confirm
   BUDGET-EXHAUSTED with full forensic. Command:
   `python3 spherical_census/run_pilot.py` (wraps `domain_sphere.enum()` at frozen
   budget; to be committed) — or inline `enum(tlim=7200,...)`.
2. Decide on lever (1) (analytic domain pre-filter) as the first iteration — it is
   cheap, rigorous, and targets the dominant (80%) acos-domain-edge cost directly.
3. Build it as exploratory substrate v2, re-validate Gate-M, amend the
   pre-registration, then re-run.

The encouraging substrate result stands: per-node transcendental enclosures are
rigorous and tight (1.0–1.3×), the chain mirror is faithful (1.5e-12), Krawczyk
certifies the root. The wall is domain geometry (curved acos boundary over a
generous box), which is exactly the kind of thing a pre-filter addresses.
