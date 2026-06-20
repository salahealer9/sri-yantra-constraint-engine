# The Spherical-to-Plane Reduction of Rao's Śrī Yantra Constraint System

**A technical note.** Salah-Eddin Gherbi (ORCID 0009-0005-4017-1095).

## Abstract

Rao (1998) formulates the Śrī Yantra construction twice: once on the sphere
(variables *b, c, d, e, g, h*; equations 2.x and 3.x) and once in the plane
(variables *b, c, d, e, g*; obtained in his §6 by a small-angle reduction). He
asserts the two systems are consistent but does not write the asymptotic map that
connects them constraint by constraint. This note makes that map explicit, states
it as a reduction law with an order classification, and validates it from both
ends: against a certified plane engine in the flat limit, and against Rao's
published spherical solutions at finite curvature. The leading coefficient of each
spherical constraint, in the curvature scale α, is exactly the corresponding plane
constraint; the order at which it appears is fixed by the constraint's geometric
form. A previously unrecorded transcription error in Rao's reduced equation (6.12)
is identified and corrected.

## 1. The two systems

**Spherical system (Rao §2–§3).** On a unit sphere the figure occupies a cap whose
bounding circle has angular radius

> **r = π/2 − h**,

where *h* is Rao's altitude parameter. The five intercepts *b, c, d, e, g* are arcs
(radians); *h* fixes the angular scale. A construction chain (eqs 2.2–2.44) locates
all auxiliary points by spherical trigonometry — arc ratios of the form
`tan x = [sin P / sin Q] tan y`, point recurrences `tan U = sin S / (Q + cos S)`,
right-triangle relations `cos x = cos r / cos c`, and the concentricity relations
(3.2b)/(3.2c). Twenty constraint functions F₁…F₂₀ (eqs 3.1–3.20) must vanish for a
valid figure. Reference implementation: `sriyantra.py`.

**Plane system (frozen, certified).** Rao's §6 reduces each spherical relation by
`sin(arc) → arc`, `tan(arc) → arc`, `cos(arc) → 1 − arc²/2`, retaining genuine
angles unchanged. The result is a five-variable system with *r ≡ 1*. This system
is frozen (`sriyantra_plane.py`), validated against Rao's plane Table 3, and is the
basis of the certified plane enumeration. Its constraints are the plane functions
F₁ᵖ…F₂₀ᵖ.

**Errata carried.** Both engines incorporate four documented corrections to Rao's
printed equations — (2.22) x₁₆ denominator, (3.3) V₈/v₈, (3.4) spurious +g, (3.14b)
Q₂₁ ratio — plus the new (6.12) correction of §5 below.

## 2. The curvature scale

Let α denote the angular scale of the figure, identified with the bounding arc:
α = r = π/2 − h. A plane figure with intercepts (b, c, d, e, g) and r = 1 is lifted
to the sphere by taking every length to the arc α·(length); the plane system is
recovered as α → 0. With the plane-length profile held fixed, each spherical
constraint becomes a function Gᵢ(α) of the single scale α, and Gᵢ(α) → 0 as the
cap shrinks.

## 3. The reduction law

> **Reduction law.** For each i, with the plane-length profile fixed,
> **Gᵢ(α) = α^{dᵢ}·Fᵢᵖ + O(α^{dᵢ+2})**,
> where the leading coefficient is exactly the plane constraint Fᵢᵖ, and
> **dᵢ = 2 for i ∈ {3, 4, 6}** and **dᵢ = 1 for the other seventeen constraints**.

Each spherical constraint is therefore the *first nonzero curvature coefficient* of
its plane ancestor. The expansion contains only even corrections beyond the leading
term (powers dᵢ, dᵢ+2, dᵢ+4, …), reflecting the parity of the underlying arc and
cosine functions.

## 4. The dᵢ = 1 / dᵢ = 2 classification

The order is determined by the *functional form* in which Rao writes the residual,
which is in turn fixed by the geometry:

- **Arc-difference constraints (dᵢ = 1).** Residuals that are signed sums of arcs
  along a common geodesic — F₁ = x₁₁ − x₁₁ₐ, F₂ = d − U₇ − rₜ, F₅ = x₁₀ − x₁₃,
  F₇, F₈ = r − r₁₆, F₉, F₁₀, F₁₁, F₁₂, F₁₃, F₁₄, F₁₅, F₁₆–F₁₉, F₂₀ = c − d. Arc
  length is odd in α, so the leading term is α¹.
- **Metric (cosine) constraints (dᵢ = 2).** The three isosceles relations F₃, F₄, F₆,
  each of Rao's form `cos A − cos 2x / cos x`. The cosine embedding annihilates the
  α⁰ and α¹ terms (cos(α·) = 1 − α²·²/2 + …), so the leading term is α².

*Proof strategy.* The mechanism above gives the order by inspection of each
residual's form. The leading coefficient is obtained by Taylor expansion: for an
arc difference Σ sᵢ·arcᵢ, the α¹ coefficient is Σ sᵢ·(length)ᵢ = Fᵢᵖ; for
`cos A − cos 2x/cos x`, the α² coefficient is −A²/2 + (3/2)x² = Fᵢᵖ. The leading
coefficient is therefore Fᵢᵖ in every case.

*Remark (non-uniqueness of form).* A single incidence may admit residual forms of
different order sharing one zero set. The radial incidence "point 16 lies on the
bounding circle" can be written either as the arc difference r − r₁₆ (dᵢ = 1, Rao's
and the engine's form) or as the metric residual cos r − cos(d+e)·cos x₁₆ (dᵢ = 2);
both vanish on the same variety. The classification above refers to Rao's chosen
forms. (The metric variant is the form examined in the Beam-1 spine test.)

## 5. Correction to Rao eq (6.12)

Rao's spherical concentricity relation is, correctly, (3.2c):

> tan(rₜ) = sin(x₇)·**tan(t/2)**,  with  tan(t) = tan(d+g−U₇)/sin(x₇)  (3.2b).

Its small-angle reduction (sin x₇ → x₇; t is a genuine angle, retained) is
rₜ = x₇·tan(t/2). Rao's printed reduced equation (6.12) instead reads
rₜ : tan(rₜ) = x₇·(**t/2**) — the half-angle tangent has lost its "tan". Because
t ≈ 54° at a typical solution, tan(t/2) and t/2 differ by ≈ 8%, shifting F₂ by
≈ 5×10⁻³. The correct form is confirmed three independent ways: it is what the
spherical (3.2c) reduces to; it is what both frozen engines compute; and Rao's own
plane Table 3 satisfies F₂ to ~10⁻⁷ under tan(t/2) but only to ~5×10⁻³ under t/2.
This joins the four errata of §1 as a transcription error confined to the printed
reduction step; Rao's spherical equation and numerical results are correct.

## 6. Independent validation chain

The law and the engines are validated by a four-link chain in which the two middle
links are independent implementations that agree to machine precision:

> **Rao's Table 1  →  `sriyantra.py`  ≡  spherical prototype  →  frozen plane engine.**

1. **Rao's published spherical solutions (Table 1) → `sriyantra.py`.** The direct
   transcription reproduces seven of Rao's eight published spherical figures to
   ≤ 10⁻⁶ on their imposed constraints; the eighth, (1,2,3,6,16,19), is the row
   documented as under-converged in Rao's table.
2. **`sriyantra.py` ≡ spherical prototype (finite α).** An independent engine,
   obtained by un-reducing the frozen plane engine to its spherical ancestors and
   parameterized by α, agrees with the transcription across **all twenty
   constraints at all eight Table-1 figures**, for α ∈ [0.23, 1.31] rad: worst
   |ΔFᵢ| = 1.3×10⁻¹⁵. This is finite-curvature agreement at Rao's real solutions,
   not merely in the flat limit.
3. **Spherical prototype → frozen plane engine (α → 0).** Every chain quantity
   satisfies arc/α → plane value at O(α²), and every constraint satisfies the
   reduction law of §3 at its predicted order, verified system-wide (relative error
   ~10⁻⁶ at α = 10⁻³, empirical order matching dᵢ for all twenty).

The per-constraint analytic content is established directly for a representative of
each class: the radial metric residual at α² (Beam 1), the isosceles family at α²
with the α⁴ coefficient A⁴/24 + x⁴/8 recovered to 8 significant figures (Beam 2),
and the concentricity residual at α¹ with odd-power structure (Beam 3).

## 7. Status and scope

The bridge between Rao's spherical and plane systems is now explicit, classified,
and validated from both ends by mutually independent implementations. This is a
self-contained structural result: it does not depend on, and is not superseded by,
any enumeration. A certified *spherical census* — Tier-2 completeness over the 3044
well-posed four-constraint subsets in six variables — is a separate undertaking;
because the spherical system carries genuine transcendental terms with no
guaranteed polynomial certificate, completeness there is expected to be partial,
and it is deferred to follow-up work.

## Artifacts

`enumeration/spine_test_F8.py`, `enumeration/spine_test_F3F6.py`,
`enumeration/spine_test_F2.py` — per-class analytic spine tests (Beams 1–3).
`enumeration/spherical_engine.py` — un-reduced prototype, system-wide α → 0 recovery.
`enumeration/spherical_finite_alpha_audit.py` — finite-α cross-validation against
the Rao transcription.

Reference engines: `sriyantra.py` (spherical, Rao's direct transcription) and
`sriyantra_plane.py` (frozen plane), both at repo root.

## References

Rao, C. S. (1998). *Śrīyantra — A Study of Spherical and Plane Forms.* Indian
Journal of History of Science, 33(3), 203–227.
