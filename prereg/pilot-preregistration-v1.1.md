# Base-Coordinate Interval/Krawczyk Pilot — Pre-registration  (FROZEN v1.1)

**STATUS: FROZEN v1.1** (= frozen v1.0 + pre-pilot Amendment GM-1 to Gate-M
criterion 1, §5). Budget values are locked (no placeholders), mirroring the plane
precedent `domain_v3.py` and deviating only where the spherical case forces it.
Amendment GM-1 was made before any exclusion/certification run, on the basis of a
Gate-M finding that the `cos(2x)/cos(x)` constraints F3/F4/F6 are intrinsically
ill-conditioned near x=π/2; it refines the fidelity metric without relaxing rigor
(containment unchanged) or altering the pilot outcome rules. SHA recorded at the
freeze line.

**Type.** Exploratory pilot pre-registration. **NOT a methodological amendment.**
It tests the *feasibility* of a candidate confirmatory instrument on a single
subset; it changes no frozen commitment, the universe (3044), the outcome
definition, or the current solver role. A methodological amendment to switch the
confirmatory engine would be considered only if this pilot shows the route can
close — never before.

**Question.** On subset {1,2,3,4,6,7}, can a rigorous outward-rounded
interval/affine-arithmetic branch-and-prune, with AA-Krawczyk interval-Newton
certification, over the registered spherical box `B_sphere`, certify the real
admissible root(s) **and exclude the entire rest of the box** within a
pre-declared budget? I.e. is the spherical transcendental enclosure tight enough
to close, as the polynomial plane enclosure did?

---

## 1. Scope and non-amendment statement

This pilot is the spherical analogue of the plane's exploratory step that preceded
its Amendment-02. The plane established the *procedural and architectural*
precedent — complex homotopy proved intractable (plane Amendment-01; and now the
spherical Gate X FAIL), and certified real-domain interval/Krawczyk enumeration
became the practical route. The spherical case faces the analogous strategic fork
with **one new technical risk: rigorous transcendental enclosure tightness in six
variables.** This pilot measures that risk on one subset. It is not the same
technical problem as the plane (which was polynomial in 5 variables); it is the
same fork. No amendment number; no change to H4, the universe, the outcome
definition, or the solver role.

## 2. Frozen instrument and truth source

| field | value |
|---|---|
| truth engine | **`sriyantra.py`** — `chain(b,c,d,e,g,h)`, `constraints(b,c,d,e,g,h)` |
| internal relation | `r = π/2 − h` (computed inside the engine) |
| variables | `(b,c,d,e,g,h)`, **radians-native** |
| EXCLUDED | `spherical_engine.py` — it is the bridge/α-audit engine (validated by α→0 plane recovery), **not** the census engine used by Gate X and the v2 lift. The pilot must mirror the census truth source, confirmed by import trace: `lift_generator.py` and `gate_x.py` both call `import sriyantra as RAO`. |
| pilot subset | {1,2,3,4,6,7} → constraints F1, F2, F3, F4, F6, F7 |
| arithmetic substrate | extend `aar.py` (rigorous outward-rounded AA) + `aa_krawczyk.py` kernel + `DualR` forward-mode AD — the proven plane stack |
| substrate extension (NEW) | `aar.py` currently has rigorous derived remainders for **only** `sqrt` and `recip`. The pilot must add rigorous outward-rounded AA forms for **`sin`, `cos`, `tan`, `atan`, `acos`**, each with a *derived* remainder bound (monotone/convexity + critical-point + explicit rounding deficit), in the same style as the `sqrt`/`recip` bounds. **This is the new component, and its tightness IS the experiment.** |

## 3. Registered box `B_sphere`

Derived by the same rule as the plane's `B.json` (`generate_B.py`), in the
spherical variables, from `sriyantra.py`'s `TABLE1` (eight published spherical
solutions, radians):

1. per variable, hull `[min, max]` across the 8 `TABLE1` rows;
2. widen 50% of the range on each side;
3. clamp **coordinate-wise** only: positivity (lower → ε=1e-6) and `0 < h < π/2`.

Frozen box (radians):

| var | lower | upper |
|---|---|---|
| b | 1e-6 | 0.763186 |
| c | 1e-6 | 1.103454 |
| d | 1e-6 | 1.302556 |
| e | 1e-6 | 0.647740 |
| g | 1e-6 | 0.687977 |
| h | 1e-6 | 1.570795 |

**Root-containment check (verified):** the polished {1,2,3,4,6,7} Newton root
`(b,c,d,e,g)=(0.62462,0.70443,0.74828,0.63074,0.31364)`, `h=0.395277` rad
lies inside this box on all six coordinates. The clean TABLE1-only box therefore
stands; no `B_sphere_pilot` fallback (hull ∪ seed) is needed.

**Design-protecting statement:** the benchmark seed root is used for Krawczyk
certification *testing*, but it is **not** used to define the domain box. The box
is the registered TABLE1 hull, independent of the answer.

**Primitive vs composite validity.** All of `b,c,d,e,g` upper bounds are below π/2
(max is d=1.3026 < 1.5708), so the *primitive* cosine denominators `cos(c)`,
`cos(d)`, … never cross a coordinate pole within the box. The harder validity
conditions are **composite** — `safe_acos` arguments (`cos(r)/cos(c)`,
`cos(d+e)·cos(x16)`, …), `tan` poles, and `sin` denominators. **These are NOT
coordinate-wise box clamps.** A box can straddle the valid/invalid region of a
composite `acos` argument; the correct branch-and-prune behaviour is **split or
exclude during pruning** (a `domain_excluded` condition), never a box clamp.

## 4. Pilot budget (FROZEN — mirrors plane `domain_v3.py`; locked)

Plane precedent (`domain_v3.enum`): `tlim=285, max_depth=200, r_cert=3e-3,
max_boxes=3_000_000, RMAX=2.0`, single-threaded.

| knob | frozen value | basis |
|---|---|---|
| wall_clock_cap | 7200 s (2 h) | **deviation ↑** from plane 285s: harder problem (6-D, transcendental, wide acos-seam box); fair-chance before declaring budget-exhaustion; cross-comparable with Gate X |
| max_depth | 200 | **mirror plane** |
| r_cert (certificate radius) | 3e-3 | **mirror plane.** NOT 1e-9: a tighter r_cert would force enormous subdivision and budget-exhaust *artificially*, masking the real question. If Krawczyk cannot certify at 3e-3 because transcendental Jacobian enclosures are too loose, **that is itself the pilot's finding.** |
| max_boxes | 3_000_000 | **mirror plane** |
| threads | 1 (single-threaded Python) | **mirror plane** `domain_v3`; record actual at run |

**Range/validity guard (FORCED deviation from plane scalar RMAX=2.0).** The plane
used a single scalar length bound; the sphere has heterogeneous radian ranges, so
the guard is a **domain-module rule**, not one scalar: spherical chain arcs must
remain in their valid principal ranges — `acos` outputs in `[0, π]`, `atan`
outputs in `(-π/2, π/2)` — and every `tan` / `sin` / `cos` denominator domain and
every `safe_acos` argument (∈ `[-1, 1]`) must be certified valid over the box by
the spherical `domain_excluded` module. A box that cannot be certified valid is
split or excluded during pruning (never coordinate-clamped). This rule is part of
the Gate-M-validated spherical domain module.

## 5. Gate-M validation (MUST PASS before any exclusion/certification claim)

No exclusion or certification result is trusted until the spherical AA chain passes
this battery against `sriyantra.py`. Thresholds are frozen:

1. **Point agreement.** At least **1,000 deterministic random samples** in
   `B_sphere` (seed **20260625**), excluding samples classified domain-invalid by
   the engine. For finite point evaluations, absolute discrepancy between the
   AA-chain center value and `sriyantra.chain` / `constraints` ≤ **1e-10**.
   (Standard is "agree within tolerance," **not** "bracket to machine precision":
   a rigorous AA enclosure is a deliberately-wider outer bound, not the point.)

   **Amendment GM-1 (pre-pilot, before any exclusion/certification run).** Gate-M
   mirror-fidelity is tested on **chain quantities** with absolute tolerance 1e-10
   (verified: worst chain-quantity discrepancy 1.5e-12 at rad=0). For constraints
   **F3, F4, F6**, absolute point-agreement is treated as **diagnostic, not a
   primary fidelity gate**, because these constraints contain `cos(2x)/cos(x)`
   terms whose sensitivity scales like `1/cos(x)^2` and which are therefore
   intrinsically ill-conditioned as `cos(x) → 0` (x → π/2); no faithful float
   mirror can meet an absolute 1e-10 on the constraint value there. The required
   rigorous condition for constraints is **enclosure containment** (criterion 2):
   the frozen-engine point value must lie inside the AA/interval enclosure. Any
   point-agreement discrepancy for F3/F4/F6 is reported together with the local
   conditioning indicator `|cos(x)|`, but does **not** by itself fail Gate-M when
   containment holds. Rationale: the certificate relies on enclosure containment
   and a rigorous Jacobian enclosure, **not** on the AA center matching the float
   engine — the center is a diagnostic. (Verified finding: F3/F4/F6 worst
   discrepancies 1.4e-8 / 5.1e-8 / 1.7e-9 occur exactly at `|cos(x)|` ≈ 2.9e-4 /
   9.0e-5 / 1.9e-3, i.e. x within ~1e-4–2e-3 of π/2; chain quantities at the same
   samples agree to ~1.5e-12; containment violations = 0.)
2. **Enclosure containment.** Every tested finite point value must lie **inside**
   the corresponding AA/interval enclosure (with outward-rounded margins) — the
   rigorous-enclosure property — at all ≥1,000 samples, zero violations.
3. **Domain-edge tests.** At least **20 hand-constructed probes each** for:
   `safe_acos` argument near ±1; `tan` near π/2; and denominator-near-zero
   (`sin`/`cos` denominators). The AA chain must flag/split/exclude, never silently
   produce a wrong enclosure or crash. The `safe_acos` DomainError edge is
   exercised directly.
4. **Root certification.** AA-Krawczyk certifies the known {1,2,3,4,6,7} Newton
   root (K(X) ⊆ int(X), contraction < 1 ⇒ unique root in X).
5. **Exclusion behaviour.** AA exclusion correctly rejects a set of boxes away from
   the root (some F_k enclosure excludes 0).

Gate-M is PASS only if all five hold at the frozen thresholds, as refined by
Amendment GM-1: chain-quantity mirror fidelity ≤ 1e-10 (strict); constraint
**containment** with zero violations (required); constraint center-agreement for
F3/F4/F6 reported with `|cos(x)|` as a conditioning diagnostic, not gating. Any
failure of the gating conditions blocks the pilot run.

## 6. Outcome rule (three-way; declared pre-run)

- **CLOSES (route plausible)** — the queue exhausts within budget: every box in
  `B_sphere` is either domain-excluded, constraint-excluded, or shrunk to a
  Krawczyk-certified box around an admissible root, with nothing left unresolved.
  This is a positive feasibility signal for the base-coordinate route.
- **BUDGET-EXHAUSTED (enclosure-tightness is the wall)** — the run hits the
  wall-clock / max_boxes / max_depth limit with boxes still unresolved, no
  technical failure, intact logs. **Expected failure mode: subdivision blow-up
  near the `acos` / radial-domain seams** (the wide-h box makes these seams
  large), not a generic "solver failed." This documents that the transcendental
  enclosures are not tight enough at the plane's r_cert to close in budget — a
  real finding that points to enclosure sharpening or domain decomposition.

  **Unresolved-box rule (operational).** A box with radius ≤ r_cert that is
  neither domain-excluded, nor constraint-excluded, nor Krawczyk-certified is
  recorded as **unresolved** (small-but-uncertified — a legitimate enclosure
  outcome, NOT a technical failure). The pilot outcome is BUDGET-EXHAUSTED if any
  unresolved boxes (or any boxes hitting max_depth) remain at termination with no
  technical failure. This removes the ambiguity between "small but uncertified"
  (→ BUDGET-EXHAUSTED) and a crash (→ TECHNICAL INCONCLUSIVE).
- **TECHNICAL INCONCLUSIVE** — crash, unhandled domain error, NaN/Inf in the
  certifier, corrupted output, or inability to read the primary result. Triggers a
  fix + re-run; never CLOSES/BUDGET-EXHAUSTED.

## 7. Scaling-interpretation clause

The pilot is one subset, chosen because it is the Gate X benchmark subset and has a
known Newton seed. A CLOSES result shows the route is plausible *for this subset*;
it does not establish census-wide feasibility (the other subsets are unmeasured). A
BUDGET-EXHAUSTED result documents the enclosure-tightness wall *for this subset
under this budget*; it is not a claim about the individual difficulty of the other
3043. The pilot tests *plausibility of the instrument*, not a census property.

## 8. Sequence

1. Gate X — **FAIL** (homotopy not census-viable), after correcting the
   outcome-classifier bug; the forensic JSON had `is_success=false`,
   `error_kind=none`, and an intact budget-exhaustion record (329,452 generic
   solutions at the 2 h cap). Documented, frozen.
2. **This pilot** — freeze pre-registration (v1.0), build the AA-trig extension,
   pass Gate-M, run the single-subset branch-and-prune, classify three-way.
3. If CLOSES → consider a methodological amendment to install the base-coordinate
   route as the confirmatory instrument (with its own pre-registration).
4. If BUDGET-EXHAUSTED → the enclosure-tightness wall is documented; next lever is
   enclosure sharpening (tighter AA transcendental forms / domain decomposition),
   not a census run.

---

**Freeze line (v1.0).** This pre-registration is frozen prior to building the
AA-trig extension and prior to any pilot run.
Pilot pre-registration v1.1 — provenance: resolved by signed tag `pilot-pre-v1.1`
