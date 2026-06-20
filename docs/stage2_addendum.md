# Stage 2 — addendum to the exploratory memorandum

Companion to `stage1_notes.md`. Stage 2 built the spherical Gate-4 validity layer
(`spherical_geo_check.py`) and used it to convert ambiguous Stage-1 numerical
events into geometric statements. The Stage-1 record stands unchanged; this
addendum records what the validity layer added. Still exploratory; no confirmatory
claims.

## 1. The validity constructor and its validation

`spherical_geo_check.py` realizes the figure independently of the trig chain, by
great-circle (geodesic) intersections on the unit sphere — the spherical analogue
of the plane `geo_check.py`. It is faithful: constructed r₁₆…r₁₉, x₁₆…x₁₉ and
base-point feet match the trig chain to ~10⁻¹⁵ over Rao's Table-1 figures and
random perturbations.

The validation is independent rather than circular: Gate-4 passes 7 of Rao's 8
published spherical figures and **flags exactly the one documented under-converged
row** (1,2,3,6,16,19), by the correct reason (it does not close, |11−11a| ≈ 1.6×10⁻³).
A validator that flags the known-bad case for the right reason is the kind that
survives scrutiny.

The project now has three independent, mutually cross-checking layers:
`sriyantra.py` (Rao transcription), the un-reduced prototype (independent analytic
implementation), and `spherical_geo_check.py` (independent geometric realization).

## 2. A taxonomy of singular events

The constructor's observables (validity, minimum point separation, ordering,
closure) map Stage-1's numerical symptoms onto geometric classes:

| numerical symptom | geometric interpretation |
|---|---|
| σ_min → 0, arclength reverses, figure valid | **altitude fold** |
| healthy Jacobian, base-point ordering fails | **validity boundary** |
| minimum point separation → 0 | **geometric collision** (vanishing triangle) |
| algebraic root persists below loss of validity | **algebraic-only branch** |
| σ_min → 0, no reversal yet, geometry healthy | **unclassified turning point** |

## 3. Altitude folds — candidate proposition

> **Proposition (candidate).** There exist spherical Śrī Yantra constraint subsets
> whose Gate-4-valid solution set contains an altitude fold: two distinct valid
> realizations coalesce at a critical altitude h\* and cease to exist below it.

Three independently confirmed witnesses (σ_min → 0, pseudo-arclength reversal,
both branches Gate-4-valid, non-degenerate geometry at the turning point):

| subset | h\* |
|---|---|
| (1, 2, 5, 8, 15) | ≈ 62.8° |
| (1, 2, 8, 10, 14) | ≈ 51.7° |
| (1, 2, 8, 10, 11) | ≈ 77.5° |

**Exploratory pattern (recorded, not claimed):** three of the four fold-signature
subsets contain F8-related structure. With a fourth candidate (1,2,8,11,19) also
F8-bearing, this may be meaningful or may dissolve under larger sampling; worth
noting while still exploratory.

**(1, 2, 8, 11, 19): fold-signature, direction-unconfirmed.** Valid, non-degenerate
geometry at a turning point (h\* ≈ 81.4°), but pseudo-arclength does not reverse even
at fine step. Deliberately left unclassified — it is definitively not a collapse,
but the three confirmed folds carry the proposition without stretching the fourth.

## 4. Layered existence — three nested existence intervals

The spherical system distinguishes three notions of existence, each with its own
altitude boundary, and the prereg must use this vocabulary:

- **Algebraic existence interval** — altitudes where the constraint system has a
  real root.
- **Constructible existence interval** — altitudes where the root realizes as a
  figure (the constructor returns a figure).
- **Gate-4-valid (census) existence interval** — altitudes where that figure is a
  valid figure (distinct points, base-point ordering, closure).

These are strictly nested: algebraic ⊇ constructible ⊇ Gate-4-valid. Measured
example:

> Subset (1,2,3,10,14): Gate-4-valid existence interval extends to **h ≈ 36.2°**,
> while the algebraic existence interval extends to **h ≈ 22.5°** — a measurable
> band 22.5° < h < 36.2° (≈ 14°) where the system has a root but **no valid figure**.

(1,2,3,11,15) is a second instance (Gate-4-valid to h ≈ 43.5°, algebraic to
h ≈ 15.8°, with a point collision near the lower end).

**Consequence for the census.** A spherical census that classified subsets on
*algebraic* feasibility would be wrong not occasionally but **structurally**, by an
amount measured in tens of degrees of altitude. Feasibility on the sphere is an
**interval of altitude**, not a binary. This is the central conceptual amendment
relative to the plane preregistration, and it emerged before any census was run.

## 5. Forward

- **Stage 2 — complete:** constructor built and validated; singular-event taxonomy;
  three confirmed folds; layered-existence principle with vocabulary.
- **Next (legitimized by Stage 2, not the full census):** among the 681
  plane-certified-infeasible subsets, does any admit a *Gate-4-valid* spherical
  figure at *any* altitude? A *no* would be a rigidity result; a *yes* would be a
  genuinely spherical figure with no valid plane analogue. The instrumentation to
  trust either answer now exists.

## 6. Probe of the 681 plane-certified-infeasible subsets (exploratory result)

Exploratory probing of the 681 plane-certified-infeasible subsets, using the Gate-4
validity layer, indicates three persistent phenomena (the qualitative structure
survives controls even as headline counts shrink):

1. **Rigidity remains dominant** — many subsets (≈ half) admit no Gate-4-valid figure
   at any altitude.
2. **The certified plane census remains internally consistent** — no in-domain pole
   limits were observed (every pole-reaching branch scales, at the plane limit, to a
   configuration outside the registered plane box B; zero in-box). Nothing threatens
   the 134/681 plane result.
3. **Some plane-certified-infeasible subsets admit Gate-4-valid spherical figures over
   bounded altitude intervals**, terminating at identifiable geometric boundaries
   (ordering failure, point collision, fold). Reproducible examples include
   (1,2,3,4,6), (1,2,3,6,13), (1,2,3,5,6). This is evidence that curvature can create
   realizable figures with no planar analogue:

   > There exist constraint subsets that admit valid spherical realizations but no
   > valid planar realization.

**Precise enumeration of such subsets remains unresolved.** Interval endpoints are
sensitive to continuation strategy near the pole (a refinement reclassified a number
of "spherical-only" branches as pole-reaching, and "solver-failed" caps proved to be
numeric truncations rather than geometric boundaries), so a headline count (e.g. "94")
is *not* claimed. Resolving it requires a dedicated existence-interval classification
procedure (pseudo-arclength per candidate, three-layer boundary typing) rather than
natural-parameter continuation.

This reframes the spherical census object itself. The plane problem was binary
(exists / does not exist); the spherical problem is naturally *"for which altitudes
does it exist?"* — altitude behaves less like a parameter and more like a bifurcation
variable (folds, validity boundaries, layered existence, curvature-confined figures
all point the same way). The eventual preregistration should be built around
**existence intervals and boundary mechanisms**, not feasible/infeasible counts.

---

## Artifacts

- `spherical_geo_check.py` — spherical Gate-4 validity constructor (geometric
  realization, chain cross-validation, validity predicate).
- `spherical_gate4_probes.py` — singular-event classifier built on the constructor;
  reproduces the taxonomy, the three confirmed folds, and the layered-existence
  measurements.
- `spherical_infeasible_probe.py` — Gate-4-valid existence search over the 681
  plane-certified-infeasible subsets (the legitimized Section-5 experiment);
  pilot-then-full, intended for a server run.
