# Appendix A — Per-constraint reduction proofs

Companion to *The Spherical-to-Plane Reduction of Rao's Śrī Yantra Constraint
System.* This appendix proves the reduction law

> **Gᵢ(α) = α^{dᵢ}·Fᵢᵖ + O(α^{dᵢ+2})**

for every constraint i = 1, …, 20, with the leading coefficient equal to the plane
constraint Fᵢᵖ in each case, and dᵢ ∈ {1, 2} as classified. The proof has three
parts: an expansion lemma for the construction chain (Lemma A), then one lemma for
each constraint class (Lemmas B and C), then a per-constraint table that assigns
every Fᵢ to a lemma.

Throughout, α is the angular scale (the bounding arc, α = r = π/2 − h on the unit
sphere). A plane quantity carries the superscript p; its spherical counterpart is
written without. Plane intercepts are held fixed; an input length L is lifted to the
arc α·L exactly. We write f(α) = O(αⁿ) in the usual sense as α → 0.

---

## A.1 Scaling conventions

Rao's spherical chain (eqs 2.2–2.44) is built from four operation types, each the
un-reduction of a plane formula:

| spherical operation | plane reduction | source |
|---|---|---|
| `cos x = cos(αP)/cos(αQ)` | x² = P² − Q² | (6.6) |
| `cos ρ = cos(αP)·cos(αQ)` | ρ² = P² + Q² | (6.14) |
| `tan x = [sin(αP)/sin(αQ)]·tan y` | x = (P/Q)·y | (6.7) |
| `tan U = sin(αS)/(Q + cos(αS))` | U = S/(Q+1) | (6.10) |

together with the dimensionless ratio `Q = [sin(αP)/sin(αP′)]·(tan A/tan B)` →
`Q = (P/P′)(A/B)` (6.9), the two concentricity relations (3.2b)/(3.2c), and the
additive arc identities (sums and differences of arcs, unchanged on the sphere).

A genuine angle in the construction — the bisected angle *t* of (3.2b), tan t =
tan(α V₇)/sin(α x₇) — is **not** an arc and does not scale with α. Every other
chain quantity is an arc.

---

## A.2 Lemma A (chain expansion)

> **Lemma A.** Every chain *arc* Q — i.e. each of
> x₁,…,x₁₉, x₁₁ₐ, U₇, U₈, U₉, U₁₂, U₂₀, U₂₁, v₈, v₉, v₁₂, V₇, V₈, V₉,
> r₁₆, r₁₇, r₁₈, r₁₉, rₜ — satisfies
> **Q(α) = α·qᵖ + O(α³)**, equivalently Q(α)/α = qᵖ + O(α²), with only odd powers
> of α. The genuine angle satisfies **t(α) = tᵖ + O(α²)** (even powers).

**Proof.** By induction along the construction order. Each step shows (i) the leading
coefficient is the plane value and (ii) the expansion has the stated parity. The two
parities propagate consistently because sin, tan, atan, asin are odd and cos is even.

*Base right-triangle arcs.* For x₁ = acos(cos(αr)/cos(αc)),
```
cos(αr)/cos(αc) = [1 − α²r²/2 + α⁴r⁴/24 − …] / [1 − α²c²/2 + …]
               = 1 − (α²/2)(r² − c²) + O(α⁴)          (an even series in α)
```
Writing ε(α) = (α²/2)(r²−c²) + O(α⁴) (even, ε = O(α²)), and using
acos(1 − ε) = √(2ε)·[1 + ε/12 + O(ε²)],
```
x₁ = √(α²(r²−c²)) · [1 + O(α²)] = α·√(r²−c²) · [1 + O(α²)] = α·x₁ᵖ + O(α³).
```
Because ε is even, √(2ε) = α·(even series), so x₁ is α·(even) = an odd series. The
same argument gives x₂ = α·x₂ᵖ + O(α³). The radial arcs r₁₆ = acos(cos(α(d+e))·cos x₁₆),
etc., are identical in structure (product of two cosines → 1 − (α²/2)[(d+e)² + (x₁₆ᵖ)²] + O(α⁴)),
yielding rᵢ = α·√(legᵖ² + legᵖ²) + O(α³) = α·rᵢᵖ + O(α³).

*Arc-ratio steps.* For x = atan([sin(αP)/sin(αQ)]·tan y) with y = α·yᵖ + O(α³),
```
sin(αP)/sin(αQ) = (P/Q)·[1 + O(α²)]           (even),
tan y           = y + y³/3 + … = α·yᵖ·[1 + O(α²)],
argument        = α·(P/Q)·yᵖ·[1 + O(α²)],
x = atan(argument) = α·(P/Q)·yᵖ + O(α³) = α·xᵖ + O(α³).
```

*Point recurrences.* For U = atan(sin(αS)/(Q + cos(αS))), the dimensionless Q is
O(1) with Q = Qᵖ + O(α²) (its sin-ratio → P/P′ and its tan-ratio tan A/tan B =
(α Aᵖ)/(α Bᵖ)·[1+O(α²)] = (Aᵖ/Bᵖ)·[1+O(α²)], the α cancelling). Then
```
sin(αS)/(Q + cos(αS)) = αS·[1+O(α²)] / (Q + 1 − α²S²/2 + …)
                      = α·S/(Q+1)·[1 + O(α²)],
U = α·S/(Q+1) + O(α³) = α·Uᵖ + O(α³).
```

*Additive arcs.* v₈ = αr − U₈ − αd = α(r − d) − U₈ = α(r − d − U₈ᵖ) + O(α³) =
α·v₈ᵖ + O(α³); likewise v₉, v₁₂, and Vₖ = Sₖ − Uₖ. Sums of arcs inherit the odd
parity.

*The angle t and the arc rₜ.* From (3.2b), tan t = tan(V₇)/sin(x₇) =
(α V₇ᵖ + O(α³))/(α x₇ᵖ + O(α³)) = (V₇ᵖ/x₇ᵖ)·[1 + O(α²)], so t = atan(V₇ᵖ/x₇ᵖ) +
O(α²) = tᵖ + O(α²): t is O(1) with even corrections. From (3.2c),
rₜ = atan(sin(x₇)·tan(t/2)) = atan(α x₇ᵖ·tan(tᵖ/2)·[1+O(α²)]) = α·x₇ᵖ·tan(tᵖ/2) +
O(α³) = α·rₜᵖ + O(α³): rₜ is an arc of the stated form. ∎

Lemma A is the only place the chain's internal structure is used; the two constraint
lemmas below treat the arcs as black boxes with the established expansion.

---

## A.3 Lemma B (arc-difference constraints, dᵢ = 1)

> **Lemma B.** Let Gᵢ = Σⱼ sⱼ·Aⱼ be a finite signed combination (constant sⱼ) of
> arc quantities Aⱼ, where each Aⱼ is either a chain arc (Lemma A) or an input arc
> α·Lⱼ. Then Gᵢ(α) = α·(Σⱼ sⱼ·aⱼᵖ) + O(α³) = α·Fᵢᵖ + O(α³). Hence dᵢ = 1 with
> leading coefficient Fᵢᵖ, and the next correction is O(α³).

**Proof.** Each Aⱼ = α·aⱼᵖ + O(α³) by Lemma A (input arcs α·Lⱼ are exact, with no
correction). Linearity gives Gᵢ = α·Σⱼ sⱼ aⱼᵖ + O(α³). The plane constraint is
Fᵢᵖ = Σⱼ sⱼ aⱼᵖ by definition, and there is no α² term because no constituent arc has
one. ∎

---

## A.4 Lemma C (cosine-isosceles constraints, dᵢ = 2)

> **Lemma C.** Let Gᵢ = cos A − cos(2x)/cos(x) with A and x arcs (Lemma A). Then
> Gᵢ(α) = α²·(−(Aᵖ)²/2 + (3/2)(xᵖ)²) + O(α⁴) = α²·Fᵢᵖ + O(α⁴). Hence dᵢ = 2 with
> leading coefficient Fᵢᵖ, and the next correction is O(α⁴).

**Proof.** Using cos u = 1 − u²/2 + u⁴/24 − … and 1/cos u = 1 + u²/2 + 5u⁴/24 + …,
```
cos(2x)/cos(x) = [1 − 2x² + (2/3)x⁴ − …]·[1 + x²/2 + 5x⁴/24 + …]
              = 1 − (3/2)x² − (1/8)x⁴ + O(x⁶),
cos A − cos(2x)/cos(x) = (1 − A²/2 + A⁴/24) − (1 − (3/2)x² − (1/8)x⁴) + O(⁶)
              = (−A²/2 + (3/2)x²) + (A⁴/24 + x⁴/8) + O(⁶).
```
The expression is **even** in (A, x): substituting A = α Aᵖ + O(α³),
x = α xᵖ + O(α³) sends the quadratic bracket to α²(−(Aᵖ)²/2 + (3/2)(xᵖ)²) + O(α⁴)
(the O(α³) parts of A, x enter as α·O(α³) = O(α⁴)), and the quartic bracket to
O(α⁴). The plane constraint is Fᵢᵖ = −(Aᵖ)²/2 + (3/2)(xᵖ)², and the leading α⁴
coefficient is (Aᵖ)⁴/24 + (xᵖ)⁴/8 — the quantity recovered numerically to eight
significant figures in the Beam-2 spine test. ∎

For F₄ the cosine argument is itself an arc combination, A = α(c+d) + v₉ − v₁₂ =
α(c + d + v₉ᵖ − v₁₂ᵖ) + O(α³); Lemma C applies with Aᵖ = c + d + v₉ᵖ − v₁₂ᵖ.

---

## A.5 Per-constraint assignment

Each constraint is written in its engine form (≡ Rao §3, errata-corrected), assigned
to Lemma B or C, and its order and leading coefficient read off. "arc" denotes a
Lemma-A quantity; α·L denotes an input length lifted to an arc.

| i | Gᵢ (spherical, engine form) | constituents | lemma | dᵢ | leading coeff |
|---|---|---|---|---|---|
| 1 | x₁₁ − x₁₁ₐ | arc − arc | B | 1 | F₁ᵖ |
| 2 | α·d − U₇ − rₜ | α·L, arc, arc | B | 1 | F₂ᵖ |
| 3 | cos V₈ − cos(2x₁₀)/cos x₁₀ | A=V₈, x=x₁₀ | C | 2 | F₃ᵖ |
| 4 | cos(α(c+d)+v₉−v₁₂) − cos(2x₁₃)/cos x₁₃ | A arc, x=x₁₃ | C | 2 | F₄ᵖ |
| 5 | x₁₀ − x₁₃ | arc − arc | B | 1 | F₅ᵖ |
| 6 | cos V₇ − cos(2x₇)/cos x₇ | A=V₇, x=x₇ | C | 2 | F₆ᵖ |
| 7 | x₁₈ − x₁₉ | arc − arc | B | 1 | F₇ᵖ |
| 8 | α·r − r₁₆ | α·L, arc | B | 1 | F₈ᵖ |
| 9 | α·r − r₁₇ | α·L, arc | B | 1 | F₉ᵖ |
| 10 | α(b+c−d−2g) − v₈ | α·L, arc | B | 1 | F₁₀ᵖ |
| 11 | α(c+d) + v₉ − 2v₁₂ − α·e | α·L, arcs | B | 1 | F₁₁ᵖ |
| 12 | x₁₆ − x₁₇ | arc − arc | B | 1 | F₁₂ᵖ |
| 13 | U₇ − (U₂₀ − v₈ + v₁₂)/2 | arcs | B | 1 | F₁₃ᵖ |
| 14 | v₁₂ − (U₂₁ − α·e)/2 | arcs, α·L | B | 1 | F₁₄ᵖ |
| 15 | α·g + (α(d+e−c) − U₂₁)/2 | α·L, arc | B | 1 | F₁₅ᵖ |
| 16 | r₁₆ − r₁₇ | arc − arc | B | 1 | F₁₆ᵖ |
| 17 | r₁₈ − r₁₉ | arc − arc | B | 1 | F₁₇ᵖ |
| 18 | r₁₆ − r₁₈ | arc − arc | B | 1 | F₁₈ᵖ |
| 19 | r₁₇ − r₁₉ | arc − arc | B | 1 | F₁₉ᵖ |
| 20 | α·(c − d) | α·L − α·L | B | 1 | F₂₀ᵖ (exact) |

Three constraints (F₃, F₄, F₆) fall under Lemma C with dᵢ = 2; the remaining
seventeen fall under Lemma B with dᵢ = 1. F₂₀ = α(c − d) is exact at all orders
(pure input arcs, no chain quantity), so its expansion terminates at α¹.

---

## A.6 Parity and the order gap

In both classes the correction beyond the leading term is O(α^{dᵢ+2}), not
O(α^{dᵢ+1}):

- **Lemma B (odd).** Each arc is an odd series (Lemma A), so Gᵢ = α·Fᵢᵖ + α³·H + …
  has only odd powers; there is no α² term.
- **Lemma C (even).** cos A − cos(2x)/cos(x) is even in the odd arcs A, x, so
  Gᵢ = α²·Fᵢᵖ + α⁴·H + … has only even powers; there is no α³ term.

This is the structural reason the spherical residual is the *first nonzero* curvature
coefficient of the plane constraint, with a clean two-power gap to the next term —
the feature exploited by the spine tests, where on a certified plane root (Fᵢᵖ = 0)
the leading term vanishes and the residual falls one full order faster (α³ for
class B, α⁴ for class C).

---

## A.7 Relation to the numerical validation

Lemmas A–C establish the law analytically. The companion note
(`docs/spherical_to_plane_reduction_note.md`) records its independent numerical
confirmation: the un-reduced prototype reproduces every chain arc at O(α²) relative
accuracy and every constraint at its predicted order system-wide (empirical dᵢ
matching the table above), and agrees with Rao's direct transcription `sriyantra.py`
to 1.3×10⁻¹⁵ across all twenty constraints at Rao's eight published spherical
figures (α ∈ [0.23, 1.31] rad). The analytic leading and sub-leading coefficients
for the representative constraints F₈ (class B), F₃/F₆ (class C, with the α⁴
coefficient (Aᵖ)⁴/24 + (xᵖ)⁴/8), and F₂ (class B, odd structure) are reproduced
numerically to the precision of those tests.

## Reference

Rao, C. S. (1998). *Śrīyantra — A Study of Spherical and Plane Forms.* Indian
Journal of History of Science, 33(3), 203–227.
