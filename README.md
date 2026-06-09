# Sri Yantra Constraint Engine

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20617730.svg)](https://doi.org/10.5281/zenodo.20617730)

A verified reimplementation and structural analysis of the geometric constraint
system in:

> C. S. Rao (1998), *Śrīyantra — A Study of Spherical and Plane Forms*,
> Indian Journal of History of Science **33**(3), 203–227.

This repository contains two independent engines (spherical and plane) for Rao's
20 constraint functions F₁…F₂₀, validated against his published solution tables,
together with a complete derivation of the constraint **dependency lattice** and
an independent **coordinate-geometry grounding** of every constraint.

It is a verified *base*. It does **not** yet contain the feasibility enumeration,
any optimisation, or a pre-registration — those are downstream of this work and
deliberately out of scope here.

## Verification status

All 20 constraint functions are independently grounded:

| How grounded | Constraints | Tolerance |
|---|---|---|
| Reproduced against Rao Table 1 (spherical) and Table 3 (plane) | F1 F2 F3 F4 F5 F6 F8 F9 F10 F13 F14 F15 F16 F19 F20 | ~1e-7 |
| Independent coordinate-geometry reconstruction (`geo_check.py`) | F7 F11 F12 F17 F18 | ~1e-16 |

Notes:
- Table 1 row `(1,2,3,6,16,19)` is **under-converged in the source**: all six of
  its constraints (including the essential F1) sit at ~1e-3 at the published
  point. This is a property of Rao's printed digits, not of this code; it is the
  only row that does not reach ~1e-7.
- The coordinate reconstruction also independently confirms the base-point
  heights used by r₁₈ and r₁₉ (P8 at d+v₈, P2 at −(c+v₉)), resolving an
  ambiguous symbol in eq 3.18a.

## Errata to Rao (1998)

Four transcription errors in the published equations were found and corrected;
each is confirmed by reproduction of the corrected figure and/or independent
geometry.

1. **eq 2.22 (x₁₆):** denominator is `sin(d+g)`, not `sin(r+c)`.
   Re-derived from the two right triangles sharing vertex P₄ (altitudes `d+g`
   and `d+e+g`); confirmed by point 16 landing on the circumcircle in every row
   where F8 is imposed, and by coordinate geometry.
2. **eq 3.3 (F₃):** the cosine argument is lowercase `v₈` (so `d+g+v₈ = V₈ =
   S₈−U₈`), not the uppercase `V₈` as printed. Consistent with the lowercase
   `v₈` in the plane reduction eq 6.13a.
3. **eq 3.4 (F₄):** the `+g` is spurious; the argument is `c+d+v₉−v₁₂`.
4. **eq 3.14b (Q₂₁):** should be
   `sin(b+c+d+v₈)/sin(c+d+e+v₉) · tan(x₁₉)/tan(x₁₈)`.
   Point 21 is formed by the transverse arcs P₉–19 and P₁–18, so the base arcs
   are x₁₉, x₁₈ — the printed `tan(x₁₀)/tan(x₁₃)` was copied from the Q₂₀
   template (eq 3.13b). This single fix simultaneously closed the F14 and F15
   residuals in both forms (including the previously unexplained Table 1 row-6
   discrepancy).

Plane-reduction form (implementation detail, not a spherical erratum):
- **eq 6.12 (rT):** in the plane limit `tan(rT) ≈ rT`, so `rT = x₇·tan(t/2)`
  with no outer arctangent.

For a concise, submission-ready summary of the four errata, see
[`note/corrigendum.md`](note/corrigendum.md).

## Dependency lattice

- **Exactly two** exact linear functional identities hold among F₁…F₂₀
  (verified to machine zero; a clean spectral gap certifies completeness):
  - `F₈ − F₉ + F₁₆ ≡ 0`  (points 16, 17 both on the circumcircle ⟹ equidistant)
  - `F₁₆ − F₁₇ − F₁₈ + F₁₉ ≡ 0`  (three of four pairwise-equidistance relations
    force the fourth)
- Both live in the **radial family** {F₈,F₉,F₁₆,F₁₇,F₁₈,F₁₉}, which forms a
  **matroid of rank 4** with circuits {8,9,16}, {16,17,18,19}, {8,9,17,18,19}.
- **Generic-rank degeneracy** of the enumeration systems {F₁,F₂}∪T:
  - Plane (|T|=3, 816 systems): exactly **1 degenerate** — {1,2,8,9,16}.
  - Spherical (|T|=4, 3060 systems): exactly **16 degenerate**.
  - All degeneracies are explained by the radial matroid; there are **no
    non-radial** degeneracies in either form.
- A **junction relation** (not a redundancy): when both midpoint conditions hold,
  `F₁₄ − F₁₅ = v₁₂ + (c−d)/2 − g` (the U₂₁ term cancels identically).

Consequence: of Rao's 20 "perfections" only 18 are independent, and the
ill-posed constraint subsets are characterised analytically in advance — so the
downstream enumeration must classify those systems as *degenerate*, not
*infeasible*.

## Files

| File | Contents |
|---|---|
| `sriyantra.py` | Spherical engine (chain + F₁…F₂₀) and Table 1 validation |
| `sriyantra_plane.py` | Plane engine (r→0 reduction) and Table 3 validation |
| `analyze_deps.py` | Spherical dependency lattice + completeness certificate + degeneracy scan |
| `plane_deps.py` | Plane dependency lattice + degeneracy certification |
| `geo_check.py` | Independent coordinate-geometry grounding of all 20 constraints |
| `test_rao_errors.py` | Numerical demonstration of four errata (published vs corrected residuals) |
| `note/corrigendum.md` | Stand-alone corrigendum note (four errata + verification method) |

Rao's published solution tables are embedded in the engines as `TABLE1` /
`TABLE3` (the validation oracle).

## Reproduce

```bash
pip install -r requirements.txt
bash run_all.sh          # runs all five scripts in sequence
```

## Status / scope

Done: both engines, four errata, full dependency lattice, all-20 grounding.
Not done (intentionally): feasibility enumeration of the well-posed systems
(815 plane / 3044 spherical), optimisation / alternative-optimum search,
pre-registration. Build those on top of this verified base.

## Citation

If you use this work, cite the archived release (see `CITATION.cff`) and the
original paper:

> Rao, C. S. (1998). Śrīyantra — A Study of Spherical and Plane Forms.
> *Indian Journal of History of Science*, 33(3), 203–227.
