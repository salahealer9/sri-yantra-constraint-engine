# Amendment 04 — Admissible-domain exclusion for the plane Tier-2 enumeration (coordinate blow-up seams)

- **Amends / extends:** Amendment 02, *"Plane Tier-2 completeness via certified
  real-box enumeration (affine-arithmetic interval-Newton),"* which installed the
  Route-3 method (§B2–§B8). This amendment **extends** that method with an explicit
  admissible-domain exclusion realizing the §6 valid-domain clause "chain-defined
  arc arguments in range." It adds to §B2 (enumeration) and §B5 (recorded
  invariants) and interacts with §B3 (completeness criterion); it withdraws and
  replaces nothing.
- **Builds on:** Amendment 03 (corrected confirmatory region B_plane), filed
  2026-06-14, DOI [10.5281/zenodo.20692921](https://doi.org/10.5281/zenodo.20692921).
- **Author:** Salah-Eddin Gherbi, Independent Researcher,
  [ORCID 0009-0005-4017-1095](https://orcid.org/0009-0005-4017-1095).
- **Filed:** 2026-06-15 — before the §B8 tooling freeze and before any confirmatory
  enumeration over B_plane.
- **Frozen engine under test:** unchanged — Sri Yantra Constraint Engine v0.1.0
  ([10.5281/zenodo.20617730](https://doi.org/10.5281/zenodo.20617730)).
- **Status:** Permanent part of the pre-registration record per §8 of the
  original. GPG-signed and OpenTimestamps-stamped on deposit.

---

## D0. Nature and limits of this amendment

The §6 search-region definition requires the enumeration to be confined to the
**valid domain** — positivity, c, d < r, and "chain-defined arc arguments in
range." The Route-3 enumeration of Amendment 02 enclosed the constraints F₁…F₂₀
but gave no operational realization of the "arc arguments in range" clause. This
amendment supplies one: an **admissible-domain exclusion** that removes boxes
provably containing no real, in-range figure, evaluated under the same
outward-rounded interval arithmetic that §B2(iv) already binds.

**The admissibility exclusion is a completeness-enabling mechanism, not a
correctness requirement.** No confirmatory claim depends on it being complete
(D3). The amendment is therefore **conservative**, and it registers **only
validated machinery** — preserving the invariant that the *registered method*, the
*validated implementation*, and the *frozen tool* are one and the same object.
It is **prospective only**; the diagnostic runs and the validation panel cited as
evidence were obtained before this filing and are **exploratory**, not
confirmatory, and are not reclassifiable. The §8 protocol governs and is
reaffirmed in full.

The amendment rests on three propositions.

## D1. (M1) Coordinate blow-up seams exist

The plane figure construction divides by chain-defined quantities that can vanish
within an axis-aligned box even where the basic variables are positive. When such
a denominator approaches zero the dependent figure coordinate diverges, and the
configuration is not a real in-range figure.

**Observed instance.** For the coordinate x11a = (v9 + c − g)/(v9 + c + d − v12)·x13,
the denominator surface **v9 + c + d − v12 = 0** drives x11a → ∞. In a diagnostic
enumeration of {1,2,3,4,8} over the legacy box, the unresolved (depth-capped)
population localized **entirely** to this one surface: of the unresolved boxes
classified, 100 % lay on v9 + c + d − v12 ≈ 0, none were near-singular in any
independent sense, and none were near a solution (multistart Newton from those
centres, 400 starts, found no root). The seam is a denominator surface — not a
solution manifold and not a numerical artifact.

## D2. (M2) Division-free exclusion resolves the observed seam

A box contains no admissible figure if a figure coordinate is provably outside its
geometric range. All coordinates of Rao's tabulated figures satisfy |xᵢ| ≤ 0.975
(r ≡ 1), so the bound **RMAX = 2** cannot clip any real figure. The exclusion is:
**a box is excluded if any implemented figure coordinate's interval enclosure lies
entirely outside [−RMAX, RMAX]**, together with the positivity conditions.

Where a coordinate is produced by a vanishing denominator, the range test is
evaluated in **division-free form**, so it never touches the singular reciprocal.
For x11a — the observed seam — this is

> exclude if  min |num · x13|  >  RMAX · max |den|,
> where num = v9 + c − g, den = v9 + c + d − v12,

with min/max taken over the box's outward-rounded enclosures. It fires hardest
exactly on tight straddling boxes (small |den|), where the reciprocal would
otherwise be undefined.

**Observed effect** (diagnostic, {1,2,3,4,8} over the legacy box): unresolved
boxes 4452 → 0; maximum subdivision depth ≈ 11 900 → 44; peak queue ≈ 11 800 → 28.
The rule does **not** over-exclude: Rao's root neighbourhood is not excluded and is
still certified unique by the AA-Krawczyk step.

The division-free reformulation is a general technique; the frozen implementation
applies it to the **one coordinate where a seam was observed, diagnosed, and
validated (x11a)**. It is deliberately not extended to coordinates where a seam was
only hypothesized (D4, D6).

## D3. (M3) Completeness is safeguarded even without exclusion — a correctness guarantee

This proposition is what makes the amendment conservative, and it is a
**correctness guarantee, not merely a procedural convenience**. If a seam were ever
left uncaught, the affected boxes accumulate as unresolved and exhaust the frozen
subdivision budget; by the §B3 completeness criterion the subset is then
**downgraded to a Tier-1 negative** ("no solution found"), never asserted as
completeness-bearing:

```
uncaught seam  ->  unresolved boxes  ->  depth cap / budget exhaustion
               ->  §B3 Tier-1 downgrade  ->  no false completeness claim
```

The exclusion's role is to **resolve** seam regions so an affected subset can
achieve a completeness-bearing result instead of downgrading. No "provably no real
in-range solution" statement depends on the exclusion being complete; it depends
only on the §B3 criterion, which is unchanged. The safety net, not the exclusion,
carries the correctness burden.

## D4. Registered admissibility conditions and parameters

The admissible-domain exclusion, evaluated per box under §B2(iv) outward-rounded
arithmetic, excludes a box if **any** of the following is provably violated over
the whole box:

1. **sqrt-domain constraints:** 1 − c² > 0 and 1 − d² > 0;
2. **positivity constraints:** b + c − g > 0, v8 > 0, v9 > 0, v12 > 0;
3. **coordinate-range constraints** for the implemented figure coordinates
   x₁…x₁₉: each has |xᵢ| ≤ RMAX;
4. **the x11a division-free rule** of D2.

**Explicit safeguard (scope of the frozen implementation).** Other potential
denominator loci — including the U20 and U21 loci of F13/F14/F15 (governed by
Q20 + 1 = 0 and Q21 + 1 = 0) — are **not** assigned dedicated exclusion rules in
the frozen implementation. Under §B3, any unresolved seam results in **downgrade to
a Tier-1 negative** rather than a completeness claim. This is an explicit
safeguard, not a gap: the registered exclusion is exactly the validated machinery,
and any locus it does not resolve is conservatively downgraded.

**Frozen parameters** (hash-pinned at §B8):

- **RMAX = 2** — a geometric coordinate bound, chosen to exceed all observed
  coordinate magnitudes (max |xᵢ| ≈ 0.975 across Rao's figures) while remaining
  well inside obviously non-constructible regions. Conservative and geometrically
  motivated; it cannot clip a real figure.
- **MAX_DEPTH = 200** — a **computational safeguard, not a geometric parameter**.
  It does not assert that legitimate subdivision beyond depth 200 is impossible
  (legitimate panel runs reached depth 15–51; the pathological legacy behaviour
  reached ≈ 11 900). It asserts only that a search exceeding this finite threshold
  without resolving is **conservatively downgraded under §B3**. The correctness
  burden again rests on the safety net.

## D5. Recorded diagnostics (extends §B5)

For each subset the campaign records, in addition to the §B5 invariants:
`domain_excl_count` (admissibility-exclusion activity), the count and surface
classification of any unresolved boxes (the nearest known seam locus, or
"not-a-known-seam"), maximum subdivision depth, and peak queue. These make any
future failure **interpretable** — distinguishing a denominator seam from a
rank-deficiency continuum from a near-singular cluster — rather than mysterious.

## D6. Exploratory evidence (validation panel on B_plane)

A three-objective panel over B_plane was run before this filing and is recorded as
**exploratory** evidence:

- **Regression** ({1,2,3,4,8}, {1,2,4,5,10}, {1,2,3,10,15}): all complete, Rao root
  recovered, 0 unresolved.
- **Admissibility stress**: three well-posed subsets clean (correct presence /
  certified absence, 0 unresolved); the rank-deficient {1,2,8,9,16} correctly
  refuses certification, its unresolved population classified as a continuum
  (not a seam).
- **Seam discovery** (F13 → U20; F14/F15 → U21): {1,2,3,4,13}, {1,2,6,14,19},
  {1,2,3,4,14}, {1,2,13,14,15} all complete with 0 unresolved; no U20/U21 seam
  manifests in B_plane.

`domain_excl_count = 0` on every panel subset: the exclusion lay **dormant** in
B_plane. Consistent with M3, this is the expected outcome of a well-conditioned
corrected region. The evidentiary asymmetry is the basis for the D4 scope: the
x11a seam was **observed, diagnosed, fixed, and validated**, whereas the U20/U21
loci were **hypothesized, exercised by targeted subsets, and did not manifest** —
so dedicated rules for them would freeze unvalidated behaviour. The panel is a
sample of 11 subsets, not a proof of seam absence across the full 815; the
per-subset §B3 criterion remains operative.

## D7. Tooling and freeze

The confirmatory tool (`enumeration/campaign.py`) implements **exactly** the
registered method of D4 — preserving registered = validated = frozen. It loads
B_plane from `enumeration/B.json` (Amendment 03), applies the admissibility
exclusion of D4 under outward-rounded arithmetic, records the D5 diagnostics, and
applies the §B3 downgrade on budget/depth exhaustion. The §B8 tooling freeze
hash-pins, at minimum: `generate_B.py`, `B.json`, `campaign.py`, the admissibility
and arithmetic modules, the plane chain, and the engine, together with the frozen
parameters of D4 and the Route-3 parameters of Amendment 02. Gate M (§B7) runs on
those exact hashes after the freeze and before any confirmatory enumeration.

This document is a permanent part of the record per §8, GPG-signed and
OpenTimestamps-stamped on deposit, filed before the freeze and before any
confirmatory run. Prospective only.
