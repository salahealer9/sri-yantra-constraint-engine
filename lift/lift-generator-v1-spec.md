# lift-generator-v1 — Emitted-System and Root-Format Specification

**Status:** freeze candidate. Instrument documentation — describes what the
frozen generator already does; introduces no new methodological decision.
Pairs with Amendment 04 (which froze the universe, solver roles, and agreement
criterion) and supplies the fixed definition of the homotopy instrument.

- Generator source: `lift_generator.py`
  SHA-256 `b59ab3b26777ebbec69e50a554c32c97ab78e5026161a6c7d7f31b4f4c39529f`
- Spec version tag: `lift-generator-v1`
- Reference: frozen spherical engine `sriyantra.py` (chain/constraints of record),
  frozen universe `size6_universe_v1.csv`
  (SHA-256 `e6b6e8b0…45e61e7bc0d05510c9431931`† — see Amendment 04 §8 for full).

---

## 1. Role

For any well-posed size-six subset {F₁,F₂}+4-of-{F₃…F₂₀}, the generator emits a
**square** polynomial system whose admissible real roots are the isolated
spherical solutions of that subset (r free). It is the authoritative census
instrument of Amendment 04 §3. Correctness is **derived, not asserted**: a
single chain registry holds each quantity's lifted equation, and the dependency
graph is read from the equations' own free symbols, so the two cannot drift.

## 2. Emitted-system specification

### 2.1 Polynomialization
Every arc is carried as a (cos, sin) pair; r is a free variable carried as
(cr, sr). cos/sin of any integer arc-combination is built by angle addition.
Each chain *angle* gets a (cos, sin) auxiliary fixed by one cleared-denominator
defining equation plus its Pythagorean closure. The five elementary forms:

| chain step | engine form | lifted equation (=0) |
|---|---|---|
| base | `arccos(cos r / cos φ)` | `c_x·c_φ − c_r` |
| ψ | `arctan((sinA/sinB)·tanX)` | `s_x·sB·c_X − c_x·sA·s_X` |
| ratio Q | `(sP/sQ)(tanU/tanV)` | `Q·sQ·c_U·s_V − sP·s_U·c_V` |
| U | `arctan(sinS/(Q+cosS))` | `s_U·(Q+cS) − c_U·sS` |
| ρ | `arccos(cosP·cosX)` | `c_ρ − cP·c_X` |

with the two helpers `t = arctan(tanV₇/sin x₇)` →
`s_t·cV₇·s_{x7} − c_t·sV₇` and `rT = arctan(sin x₇·tan(t/2))`,
`tan(t/2)=s_t/(1+c_t)` → `s_rT·(1+c_t) − c_rT·s_{x7}·s_t`.

The combinations V₇,V₈,V₉,v₈,v₉,v₁₂ are **not** variables; their cos/sin are
expanded from atomic + U auxiliaries, so referencing one pulls its U into the
dependency closure automatically.

### 2.2 Constraint lift forms
- **Cosine constraints** F₃,F₄,F₆ (`cos V − cos2X/cosX`): lift
  `cV·cX − (2cX² − 1)`, factor `cos X` relative to the engine constraint.
- **All other constraints** (an integer arc/angle combination set to zero):
  lift `cos(combination) − 1`. For F₁₃,F₁₄,F₁₅ the engine's ½ is cleared by
  doubling the combination (same zero set), so the lift equals `cos(2Fᵢ) − 1`.

### 2.3 Canonical variable ordering (frozen)
1. atomic (cos, sin) pairs, order b, c, d, e, g, r → 12 variables;
2. chain-angle (cos, sin) pairs, in registry order `ANGLE_NAMES`, included only
   if in the subset's dependency closure;
3. ratio variables, in registry order `RATIO_NAMES`, included only if needed.

### 2.4 Canonical equation ordering (frozen)
A. atomic Pythagorean, order b…r (6 equations);
B. per included angle, (defining equation, Pythagorean), `ANGLE_NAMES` order;
C. per included ratio, defining equation, `RATIO_NAMES` order;
D. constraint lifts, **ascending constraint index**.

### 2.5 Invariants
- **Squareness:** atomic contributes 12 vars / 6 eqs, each angle 2/2, each ratio
  1/1, constraints +6 eqs → variables = equations for every size-six subset, by
  construction (verified on every generated system).
- **Determinism:** `system_hash(generate(S))` is a SHA-256 over the ordered
  variable names and the expanded ordered equations; identical for repeated
  generation of the same subset. Reproducible across versions iff §2.3–2.4 hold.
- **Input guards:** non-size-six input and the two rank-deficient supports
  ({8,9,16}, {16,17,18,19}) raise rather than emit a system.

## 3. Validation suite (`validate_sample`)
On random well-posed subsets at random valid near-planar spherical figures
(frozen-engine auxiliaries), the suite checks: every chain/Pythagorean equation
vanishes (~1e-15) at the engine's values; every constraint polynomial equals the
engine constraint up to its known factor (cosine: `cosX·Fᵢ`; doubled: `cos2Fᵢ−1`;
others: `cosFᵢ−1`) to ~1e-15; squareness; and deterministic system hashes. The
acceptance bar before census is a sample exercising **every** constraint
F₃…F₂₀ at least once with both maxima ≤ 1e-14. Last run: 36 subsets (full
coverage), max chain residual 2.4e-16, max constraint residual 3.7e-16.

## 4. Root-format specification (homotopy → census)
1. **Solve** the emitted system with HomotopyContinuation.jl; obtain isolated
   complex solutions as vectors in canonical variable order (§2.3).
2. **Certify** the solutions found with `certify()` (Smale α-theory / interval
   arithmetic) — Level-C for the points returned. *Completeness* (all isolated
   solutions found) is a separate property of the path-tracking/monodromy and is
   argued separately, not implied by `certify()`.
3. **Admissible-real filter:** imaginary part ≤ 1e-8; sign branches `s_{x1},
   s_{x2}, s_{x7} > 0`; atomic arcs > 0; domain c, d < r.
4. **Recover arcs** by `atan2(s, c)` for b, c, d, e, g, r; set h = π/2 − r.
5. **Round-trip residual:** evaluate the frozen engine constraints at the
   recovered (b,c,d,e,g,h); accept the root iff `max_{i∈S}|Fᵢ| < 1e-7`.
6. **Emit** each accepted root to the runner's ingest contract
   (`RootIngestAdapter`):
   `{"subset": [...], "roots": [{"coords": [b,c,d,e,g], "h": <deg>}, ...]}`.
   The runner then applies Gate-4, residual, tier, and the size-six class labels
   of Amendment 04 §5. Both Gate-4-valid and invalid recovered roots are
   archived (audit trail).

## 5. What this freeze fixes
Once tagged, the homotopy instrument is fixed in the same sense as the frozen
census engine and the bridge-paper core: the polynomial system for any size-six
subset, its variable/equation ordering, its hash, the admissibility filter, and
the root format are all determined. The 3044 run becomes *apply frozen
instrument to frozen universe under frozen H4*.

†Full universe hash:
`e6b6e8b0968876bd3b3d0654d3705f9843699e9e7e08ff4d946e36187627c45b`.
