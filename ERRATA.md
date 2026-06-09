# Errata to Rao (1998), with basis

C. S. Rao, *Śrīyantra — A Study of Spherical and Plane Forms*, Indian Journal of
History of Science 33(3), 203–227 (1998).

Each correction below is established by (i) reproduction of the corrected figure
against Rao's own published solution tables, and/or (ii) independent
coordinate-geometry reconstruction. Notation follows the paper. The construction
chain (eqs 2.2–2.44) is otherwise reproduced exactly; 15 of the 20 constraints
evaluate to ~1e-7 at the published solutions once the corrections below are
applied.

---

## E1 — eq 2.22, the base arc x₁₆

**Printed:**  `tan x₁₆ = [sin(d+e+g) / sin(r+c)] · tan x₆`

**Correct:**  `tan x₁₆ = [sin(d+e+g) / sin(d+g)] · tan x₆`

**Basis.** Point 16 is the intersection of the base line through P₉ with the
transverse line P₄–6 extended. The two right spherical triangles sharing the
vertex P₄ have altitudes `arc P₄P₇ = d+g` (carrying base arc x₆) and
`arc P₄P₉ = d+e+g` (carrying base arc x₁₆). Eliminating the common vertex angle
gives `tan x₁₆ / tan x₆ = sin(d+e+g) / sin(d+g)`. The printed `sin(r+c)` does not
arise from this triangle pair. Confirmed: with the corrected denominator, point
16 lands on the circumcircle (F8 = r − r₁₆ = 0) to ~1e-7 in every Table 1 row
where F8 is imposed, and the coordinate reconstruction reproduces x₁₆ to 1e-16.

## E2 — eq 3.3, the argument of F₃

**Printed:**  `F₃ = cos(d + g + V₈) − cos(2x₁₀)/cos(x₁₀)`

**Correct:**  `F₃ = cos(d + g + v₈) − cos(2x₁₀)/cos(x₁₀)`  (lowercase v₈)

**Basis.** The construction quantity is `v₈ = r − U₈ − d` (eq 2.21), and
`d + g + v₈ = (r+g) − U₈ = S₈ − U₈ = V₈`. The intended cosine argument is
therefore `V₈`; writing the uppercase `V₈` *inside* `d+g+(·)` double-counts. The
plane reduction the paper itself gives (eq 6.13a) uses the lowercase `v₈`,
confirming the intended reading. With v₈, F₃ = 0 holds to ~1e-7 at the Table 1
rows where F₃ is imposed.

## E3 — eq 3.4, the argument of F₄

**Printed:**  `F₄ = cos(c + d + g + v₉ − v₁₂) − cos(2x₁₃)/cos(x₁₃)`

**Correct:**  `F₄ = cos(c + d + v₉ − v₁₂) − cos(2x₁₃)/cos(x₁₃)`  (no `+g`)

**Basis.** Numerically identified: at the three Table 1 rows imposing F₄, the
argument whose cosine equals `cos(2x₁₃)/cos(x₁₃)` is `c+d+v₉−v₁₂` to ~1e-7, while
the printed `c+d+g+v₉−v₁₂` is off by ~1e-2. Cross-checked against Table 3.

## E4 — eq 3.14b, the quotient Q₂₁ (hence U₂₁, F₁₄, F₁₅)

**Printed:**  `Q₂₁ = [sin(b+c+d) / sin(c+d+e)] · (tan x₁₀ / tan x₁₃)`

**Correct:**  `Q₂₁ = [sin(b+c+d+v₈) / sin(c+d+e+v₉)] · (tan x₁₉ / tan x₁₈)`

**Basis.** Point 21 is the intersection of the transverse arcs P₉–19 and P₁–18,
so the relevant base arcs are x₁₉ (= P₂–19) and x₁₈ (= P₈–18) — not x₁₀, x₁₃,
which belong to point 20 and were evidently copied from the Q₂₀ template
(eq 3.13b). The corrected form was found by requiring consistency across the two
independent witnesses U₂₁ has — F₁₄ (Table 3 row `1,2,6,14,19`) and F₁₅ (Table 3
row `1,2,3,10,15` and Table 1 row `1,2,4,10,15,19`) — and matches all three to
≤2e-6. Applying it closed the F14 and F15 residuals simultaneously in both
forms, including the Table 1 row-6 discrepancy that had no other explanation.

---

## Plane-form note — eq 6.12 (rT)

Not a spherical erratum, but a plane-reduction detail. In the plane limit
`tan(rT) ≈ rT`, so the reduced concentricity inradius is

  `rT = x₇ · tan(t/2)`,  with  `t = atan((d+g−U₇)/x₇)`,

with **no** outer arctangent. Retaining an outer `atan(...)` introduces a uniform
~7e-5 error in the essential constraint F₂ across all Table 3 rows; removing it
brings F₂ to ~1e-7.

---

## Under-converged source row (not an erratum)

Table 1 row `(1,2,3,6,16,19)` is under-converged in the printed digits: at the
published point all six of its constraints — including the essential concurrency
F₁ — evaluate to ~1e-3, whereas every other row reaches ~1e-7. This is a limit of
the source table, not a formula error.
