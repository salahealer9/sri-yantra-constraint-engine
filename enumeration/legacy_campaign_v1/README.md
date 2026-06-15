# legacy_campaign_v1 — original Tier-2 plane census (superseded)

This directory preserves the **first** full Tier-2 confirmatory census of the 815
well-posed plane subsets, run on the frozen tree `tier2-freeze` (commit `f0581fe`,
2026-06-15). It is retained for provenance and is **superseded** by the corrected
census produced under the conformance-patched tool (`tier2-freeze-2`).

## What it contains
- `results.csv`, `roots.jsonl`, `campaign.log` — the original run, reporting
  **135 feasible / 680 infeasible**, 0 unresolved, 0 Tier-1 downgrades.

## Why it was superseded
The registered Tier-1 multistart cross-check (§6), which searches strictly within
`B_plane`, disagreed with Tier-2 on exactly one subset: **{1,2,4,11,16}**. Diagnosis
showed Tier-2 had **over-certified** it. The subset's sole real root lies at
`g = 0.08387`, which is **0.00030 below** `B_plane`'s lower g-face (`0.084179`) —
i.e. just **outside** the registered region.

Root cause: the frozen `campaign.krawczyk` ran the Krawczyk inclusion test over an
**isotropic cube** `[center ± max-half-width]` instead of the actual (anisotropic)
box `X` registered in Amendment-02 §B2(iii). Near a box face the cube extends up to
`r_cert` beyond `B_plane`, so a root just outside the face but inside the cube was
certified as in-region. The effect is confined to boundary boxes; interior
certifications are unaffected. A direct scan of all certified roots confirmed
**{1,2,4,11,16} is the only certified root lying outside `B_plane`** (and the
cross-check found `t1_extra = 0`: no in-region figure was missed by Tier-2).

## Corrected result
Under the conformance-patched tool (Krawczyk over the actual box `X`),
{1,2,4,11,16} certifies **absent** in `B_plane`. The corrected classification is
**134 feasible / 681 infeasible**, independently reproduced by the strict-in-box
Tier-1 cross-check. See `prereg/erratum-tier2-01.md`.

This correction is the registered two-tier design working as intended: a complete
Tier-2 partition, independently challenged by Tier-1, the disagreement localized to
a single boundary mechanism, the tool corrected, and the result converged.
