# Corrigendum and computational verification of Rao (1998), *Śrīyantra — A Study of Spherical and Plane Forms*

**Author:** Salah-Eddin Gherbi, Independent Researcher
**Date:** 09/06/2026
**Corresponds to:** C. S. Rao (1998), *Śrīyantra — A Study of Spherical and Plane Forms*, Indian Journal of History of Science **33**(3), 203–227.

---

## Abstract

Rao (1998) recast the traditional construction of the Śrīyantra as a system of
simultaneous nonlinear equations — six basic variables (spherical form) or five
(plane form) and twenty geometric constraint functions F₁…F₂₀ — solved
numerically for selected constraint subsets. Reimplementing the full
construction and constraint set in double precision, we find the formulation
sound and the published solutions reproducible, but identify **four
transcription errors** in the printed equations (eqs 2.22, 3.3, 3.4, 3.14b) that
prevent the affected constraints from vanishing at the tabulated solutions, plus
one plane-reduction correction (eq 6.12). Each correction is established both by
reproduction of the corrected figure against Rao's own solution tables and by an
independent reconstruction of the figure in Cartesian coordinates. We also note
that one row of Table 1 is under-converged in the printed digits. Corrected
equations and fully reproducible code accompany this note.

## 1. Introduction

Rao's formulation expresses the geometric "perfections" of the Śrīyantra as
constraint functions F₁…F₂₀ that must vanish for a figure to satisfy the
corresponding property; because there are only five (plane) or six (spherical)
free variables, at most that many constraints can hold at once, and Rao tabulates
numerical solutions for a selection of subsets (Tables 1 and 3). The underlying
mathematics — the spherical-trigonometric construction chain (eqs 2.2–2.44), the
constraint definitions (eqs 3.1–3.20), and the Newton–Raphson solution method —
is correct and, with the corrections below, fully reproducible.

In transcribing the published equations exactly, however, we found that four of
them, as printed, are not satisfied at Rao's own tabulated solutions. The
discrepancies are localized and each resolves to a clear typographical or
copy-template error. We report the corrections and the evidence for each.

## 2. Method of verification

The construction chain and all twenty constraints were implemented in Python
(IEEE double precision), with the spherical and plane forms as separate engines.
A constraint Fᵢ is taken as *verified* when |Fᵢ| ≲ 10⁻⁶ at every tabulated
solution point that imposes it. With the corrections of §3 applied:

- **Fifteen** constraints — F₁–F₆, F₈–F₁₀, F₁₃–F₁₆, F₁₉, F₂₀ — are exercised by
  Tables 1 and 3 and verify to ~10⁻⁷.
- **Five** constraints — F₇, F₁₁, F₁₂, F₁₇, F₁₈ — appear in no tabulated row and
  therefore cannot be checked by reproduction. We ground these by an independent
  reconstruction of the plane figure in Cartesian coordinates: the directly
  defined base points are placed on the axis, every numbered intersection point
  is located by solving the corresponding straight-line intersections, and the
  geometric quantities each constraint reports (the base arcs x₁₆…x₁₉, the radial
  distances r₁₆…r₁₉, and the axial intercepts) are read off and compared with the
  trigonometric chain. They agree to ~10⁻¹⁶, and the construction independently
  fixes the base-point heights underlying r₁₈ and r₁₉ (point P₈ at d+v₈, point P₂
  at −(c+v₉)), resolving an ambiguous symbol in eq 3.18a.

## 3. Corrections

Throughout, notation is that of Rao (1998); v₈, v₉, v₁₂ are the lowercase
construction quantities (eqs 2.21, 2.31, 2.40) and the xₙ are base arcs.

**(E1) Equation 2.22 — base arc x₁₆.**
Printed: tan x₁₆ = [sin(d+e+g) / sin(r+c)] · tan x₆.
Correct: **tan x₁₆ = [sin(d+e+g) / sin(d+g)] · tan x₆.**
Point 16 is the intersection of the base line through P₉ with the transverse line
P₄–6 extended. The two right spherical triangles sharing the vertex P₄ have
altitudes arc P₄P₇ = d+g (carrying x₆) and arc P₄P₉ = d+e+g (carrying x₁₆);
eliminating the common vertex angle gives the ratio sin(d+e+g)/sin(d+g). The
printed sin(r+c) does not arise from this pair. With the correction, F₈ = r − r₁₆
vanishes to ~10⁻⁷ at every Table 1 row imposing it, and the coordinate
construction reproduces x₁₆ to 10⁻¹⁶.

**(E2) Equation 3.3 — argument of F₃.**
Printed: F₃ = cos(d + g + V₈) − cos(2x₁₀)/cos(x₁₀), with uppercase V₈.
Correct: **F₃ = cos(d + g + v₈) − cos(2x₁₀)/cos(x₁₀)** (lowercase v₈).
Since d + g + v₈ = (r+g) − U₈ = S₈ − U₈ = V₈, the intended cosine argument is V₈
itself; the literal reading d+g+V₈ double-counts. Rao's own plane reduction (eq
6.13a) carries the lowercase v₈, confirming the intended form.

**(E3) Equation 3.4 — argument of F₄.**
Printed: F₄ = cos(c + d + g + v₉ − v₁₂) − cos(2x₁₃)/cos(x₁₃).
Correct: **F₄ = cos(c + d + v₉ − v₁₂) − cos(2x₁₃)/cos(x₁₃)** (no +g term).
At the Table 1 rows imposing F₄, the argument whose cosine equals
cos(2x₁₃)/cos(x₁₃) is c+d+v₉−v₁₂ to ~10⁻⁷, while the printed form is in error by
~10⁻².

**(E4) Equation 3.14b — quotient Q₂₁ (hence U₂₁, F₁₄, F₁₅).**
Printed: Q₂₁ = [sin(b+c+d) / sin(c+d+e)] · (tan x₁₀ / tan x₁₃).
Correct: **Q₂₁ = [sin(b+c+d+v₈) / sin(c+d+e+v₉)] · (tan x₁₉ / tan x₁₈).**
Point 21 is the intersection of the transverse arcs P₉–19 and P₁–18, so the
governing base arcs are x₁₉ = P₂–19 and x₁₈ = P₈–18 — not x₁₀, x₁₃, which belong
to point 20 and were evidently carried over from the Q₂₀ template (eq 3.13b). The
corrected form is the unique candidate consistent with all three independent
witnesses U₂₁ possesses (F₁₄ at Table 3 row 1,2,6,14,19; F₁₅ at Table 3 row
1,2,3,10,15 and Table 1 row 1,2,4,10,15,19), matching each to ≤ 2×10⁻⁶, and it
removes the F₁₄ and F₁₅ residuals in both forms simultaneously.

**(Plane-form note) Equation 6.12 — reduced inradius rT.**
In the plane limit tan(rT) ≈ rT, so the reduced concentricity inradius is
rT = x₇ · tan(t/2) with t = arctan((d+g−U₇)/x₇), and **no outer arctangent**.
Retaining an outer arctan introduces a uniform ~7×10⁻⁵ error in the essential
constraint F₂ across all of Table 3; removing it brings F₂ to ~10⁻⁷. This is a
plane-reduction detail rather than an error in the spherical formulation.

## 4. An under-converged row in Table 1

The Table 1 row with constraint set (1, 2, 3, 6, 16, 19) is under-converged in
the printed digits: at the tabulated point all six of its constraints — including
the essential concurrency condition F₁ — evaluate to ~10⁻³, whereas every other
row reaches ~10⁻⁷ after the corrections above. We note this for completeness; it
reflects the precision of the printed solution, not an error in the formulation.

## 5. Remark on exact redundancy

Two exact linear identities hold among the constraint functions for all parameter
values:

  F₈ − F₉ + F₁₆ ≡ 0   and   F₁₆ − F₁₇ − F₁₈ + F₁₉ ≡ 0.

The first is immediate (two points on the circumscribing circle are equidistant
from its centre); the second expresses that among four pairwise-equidistance
relations between four points, any three force the fourth. Consequently only
eighteen of the twenty constraints are mutually independent. A fuller structural
analysis of the constraint system is reported separately.

## Code and data availability

The two verified engines, the coordinate-geometry grounding, and scripts 
reproducing every figure in this note are archived at
[10.5281/zenodo.20617730](https://doi.org/10.5281/zenodo.20617730) and maintained at 
[https://github.com/salahealer9/sri-yantra-constraint-engine](https://github.com/salahealer9/sri-yantra-constraint-engine).

Rao's published solution tables (Tables 1 and 3) are embedded as the validation oracle.

## Reference

Rao, C. S. (1998). Śrīyantra — A Study of Spherical and Plane Forms. *Indian
Journal of History of Science*, 33(3), 203–227.
