# Stage 1 — exploratory memorandum (spherical Śrī Yantra census)

**Status:** exploratory. This memorandum records what Stage-1 reconnaissance
established about the spherical solution landscape. It is **not** the
preregistration; it is the evidence base the spherical prereg will be written
against. No confirmatory claims are made here.

Author: Salah-Eddin Gherbi. Engine: `sriyantra.py` (validated spherical engine,
bridge-deposit v1.0.0). Curvature scale α = r = π/2 − h (h = altitude).

Framing: a plane-census subset is {1,2} + 3 others (5 constraints, 5 unknowns
b,c,d,e,g). Fixing h makes the spherical slice a square 5×5 system, and h → π/2
is the certified plane engine. Branches are tracked from certified plane roots
(near the pole) downward in altitude.

---

## Finding 1 — Degree-normalized conditioning (a computational corollary of the bridge)

The unscaled Jacobian of the spherical subset system is ill-conditioned toward the
plane limit, with

> **κ(J) ≈ 2.4 / α  as  α = π/2 − h → 0.**

Measured for (1,2,3,4,8): κ = 1.37×10² → 1.37×10³ → 1.37×10⁴ → 1.35×10⁵ at
h = 89° → 89.9° → 89.99° → 89.999° — exactly one decade per decade of α.

This is not a numerical accident; it is the reduction law made operational. The
constraints carry mixed orders dᵢ (dᵢ = 2 for the cosine-isosceles F₃/F₄/F₆,
dᵢ = 1 for the other seventeen), so the Jacobian rows scale as α versus α² and
their magnitude ratio α drives κ ∝ 1/α. Degree-normalizing the constraints,

> **F̃ᵢ = Fᵢ / α^{dᵢ},**

removes the blow-up completely: the normalized condition number is flat at ≈ 9
from h = 89° to h = 89.9999° (where the raw value is 1.2×10⁶).

**Recommendation (methodology):** all spherical solving, continuation, and
interval work is done on the degree-normalized constraints F̃ᵢ. This is a standing
rule for the spherical project, justified by the bridge theorem, and stated as
such in the prereg. Phrased as a corollary:

> The mixed-order reduction structure induces a 1/α pole singularity in the
> unscaled Jacobian, which is removed exactly by degree-normalized constraint
> scaling.

---

## Finding 2 — Altitude folds are real

Continuing the 134 certified plane survivors downward in altitude (normalized
solver), most extend smoothly; **two subsets exhibit confirmed folds in altitude:**

| subset | fold altitude h\* | confirmation |
|---|---|---|
| (1, 2, 5, 8, 15) | ≈ **62.8°** | σ_min(J̃) → 0; pseudo-arclength branch reversal; interior (min chain quantity ≈ 0.03, min intercept/r ≈ 0.13) |
| (1, 2, 8, 10, 14) | ≈ **51.7°** | σ_min(J̃) → 0; pseudo-arclength branch reversal to the pole |

Each branch descends in h, reaches a turning point where ∂F/∂x is singular with
the figure still non-degenerate, then reverses and re-ascends toward the pole. So
**two valid solution branches coexist for h above h\*** and merge at the fold.
These passed the strongest available test (singular Jacobian + pseudo-arclength
reversal + interior location); they are not solver artifacts. **There is no plane
analog** — altitude is the spherical-only parameter, and the fold is a genuine
structural feature of the spherical system.

---

## Finding 3 — Algebraic roots ≠ valid figures (the Stage-1 methodological lesson)

An early sweep appeared to show ~72/120 plane-failure subsets "gaining" spherical
roots under curvature. **This was an artifact.** The probe counted F = 0 solutions
with only a positivity check; the plane census classifies on *valid figures*
(Gate 4: distinct points separated by > 10⁻⁶·r, base-point ordering, no degenerate
triangles) within a registered domain. Re-checking dissolved the effect: the
"clean" candidates ((1,2,3,4,7), (1,2,3,4,6)) drop to **zero valid roots at every
altitude**, and the pole-reaching ones scale, at the plane limit, to configurations
**outside the valid plane domain** (e.g. d + e > r). Authoritatively, **all 681
plane-failure subsets are *certified* infeasible** (`results.csv`:
complete, unresolved = 0, feasible = 0) — not "not found."

This is the spherical analog of the plane project's isotropic-box lesson. It
imposes a hard requirement on the preregistration: it must separate, as distinct
objects,

1. **algebraic roots** (F = 0),
2. **valid spherical figures** (a geometric realizability predicate — spherical Gate 4),
3. **census classifications** (feasible / certified-infeasible / unresolved).

Root-counting without a validity layer is meaningless on the spherical side, and
the question "can curvature create valid figures absent in the plane" **remains
open** — it cannot be answered until a spherical realization constructor exists.

---

## Classification of the 17 early terminations

| status | count | subsets |
|---|---|---|
| coarse-step artifacts (continue to floor with fine steps) | 6 | (1,2,3,10,15), (1,2,8,9,20), (1,2,8,16,20), (1,2,9,16,20), (1,2,10,16,20), (1,2,16,18,20) |
| confirmed altitude folds | 2 | (1,2,5,8,15), (1,2,8,10,14) |
| constructibility-boundary candidates (healthy σ_min, no valid root below) | 6 | (1,2,3,10,14), (1,2,3,11,14), (1,2,4,10,14), (1,2,4,11,14), (1,2,6,10,14), (1,2,6,11,14) |
| unresolved singular events (σ_min → 0, arclength did not reverse) | 3 | (1,2,8,11,19), (1,2,8,10,11), (1,2,3,11,15) |

The {·,14} cluster is suggestive of geometry rather than noise, but with a
non-singular Jacobian at the stop it reads as a constructibility boundary, not a
fold. One honest loose end: continuation tracked a root up to the stop while cold
multistart finds none below it, so whether the tracked branch is still a *valid*
figure at the edge is undetermined with current tools.

---

## Open items and why they route through a spherical Gate 4

The unresolved singular events and the boundary candidates cannot be cleanly
classified — fold vs cusp vs branch merger vs constructibility loss vs geometric
degeneracy — using continuation and Jacobians alone. A spherical realization
constructor (the analog of the plane `geo_check.py`, with great-circle/geodesic
intersections) would supply the missing diagnostics: point collisions, vanishing
triangles, coincident geodesics, ordering failures, loss of realizability. Several
currently ambiguous events are expected to become obvious once realizability can
be tested directly. Building it is **Stage 2**, and it is prerequisite to the
preregistration.

---

## Forward plan

- **Stage 1 (this memorandum) — closure.** Findings 1–3, the termination
  classification, the open singularities, the motivation for spherical Gate 4. No
  claims beyond these.
- **Stage 2 — build the spherical Gate-4 validity constructor.** Not the census;
  just the geometric realization and validity layer. Every open question above
  routes through it.
- **Stage 3 — draft the spherical preregistration**, with the conditioning
  strategy (normalized constraints), continuation strategy (pseudo-arclength),
  validity criteria (spherical Gate 4), known failure modes (folds, constructibility
  boundaries), and the algebraic-root / valid-figure / classification separation
  baked in from the start.

Two hidden issues that the plane prereg lacked and had to acquire by amendment —
**mixed-order conditioning** and **algebraic roots ≠ valid figures** — were exposed
here, before launch. That is the exploratory phase doing its job.

---

## Artifacts (Stage-1 scripts)

- `stage1_recon.py` — initial reconnaissance: continuation from plane roots,
  conditioning vs altitude, multistart root counts.
- `stage1b_landscape.py` — degree-normalized solver, 134-survivor continuation
  sweep, near-feasible failure probe. *(The failure-probe output is superseded by
  Finding 3 and retained only for provenance; do not read its gainer counts as
  results.)*
- `stage1_fold_analysis.py` — normalized-conditioning verification, σ_min
  diagnostic over the terminating subsets, and pseudo-arclength fold confirmation
  (produces the two confirmed folds).

Reproducibility: engine `sriyantra.py`; all solving on F̃ᵢ = Fᵢ/α^{dᵢ}; RNG seeds
fixed in each script.

## Reference

Rao, C. S. (1998). *Śrīyantra — A Study of Spherical and Plane Forms.* Indian
Journal of History of Science, 33(3), 203–227.
