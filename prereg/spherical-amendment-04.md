# Spherical Preregistration — Amendment 04

**Size-six confirmatory census: universe, solver pathway, and dual-engine agreement criterion**

Amends: spherical preregistration v1.0.2 (+ Amendments 01, 02, 03).
Amendment 03 (H4) froze the *hypothesis and test*; this amendment freezes the
*universe, solver roles, and agreement criterion* for the H4 run. Registered
**before** any size-six classification is produced. Status: frozen on signing.

---

## 1. Scope

This amendment governs the size-six census that supplies the population for the
frozen H4 test (F₇ enrichment among robust-realizable size-six systems). It does
not alter H4's predictor, outcome, statistical test, or near-degeneracy floor
(τ_deg = 1e-3), all of which remain as registered in Amendment 03.

## 2. Universe (a derived, not conventional, quantity)

The universe is the well-posed determined systems {F₁, F₂} + 4-of-{F₃…F₂₀}.
Of the C(18,4) = 3060 candidates, the rank-deficient ones are removed. Rank
deficiency arises from exactly two independent linear identities among the
radial-difference constraints (which depend on only the five quantities
r, r₁₆, r₁₇, r₁₈, r₁₉):

- F₈ − F₉ + F₁₆ ≡ 0  → support {8, 9, 16}
- F₁₆ − F₁₇ − F₁₈ + F₁₉ ≡ 0  → support {16, 17, 18, 19}

The first removes the 15 subsets whose four contain {8, 9, 16}; the second
removes the single subset {1, 2, 16, 17, 18, 19}. The second has support size
four and therefore cannot occur in the size-five universe (where a subset holds
only three free indices), which is why it is absent from the spherical 815
census and first appears here. Hence **3060 − 16 = 3044**.

Both identities vanish to bit-exact zero at generic in-domain points, and a
direct Jacobian enumeration over all 3060 candidates returns exactly 16
rank-deficient subsets (σ_min ≤ 1.8e-16 on the 16, σ_min ≥ 7.5e-5 on the rest).

The frozen universe is `size6_universe_v1.csv`
(SHA-256 `e6b6e8b0968876bd3b3d0654d3705f9843699e9e7e08ff4d946e36187627c45b`),
3044 rows, deterministic ascending order.

## 3. Solver roles (asymmetric; frozen)

The two solvers have **fixed, non-interchangeable roles**:

- **Homotopy solver — confirmatory / authoritative.** The census classification
  of every subset is derived solely from a global polynomial homotopy solve of
  the auxiliary-variable lift (square system, r free). "Global certified
  solver" is the frozen *property*: it must enumerate all isolated complex
  solutions and certify them; the specific start system and tracking strategy
  are implementation and may evolve.
- **Newton solver — validation.** An independent direct solve of the 6×6 system
  in (b, c, d, e, g, h) is run separately. "Independent" is the frozen
  property: a distinct code path with its own start strategy. It is a
  validation procedure only.

Neither solver may be used to patch, seed, or override the other. The homotopy
classification is never edited to match Newton, and Newton roots are never
substituted into the homotopy record.

## 4. Per-root acceptance (both solvers, same definitions)

A candidate solution is an **accepted admissible real root** iff:

- **real:** every coordinate's imaginary part ≤ 1e-8 (homotopy);
- **on the physical branch:** passes the branch-admissibility filter
  (square-root sign variables > 1e-9; cleared denominators |·| > 1e-7; original
  coordinates > 1e-6; domain c, d < r);
- **residual:** the raw constraint residual evaluated through the
  non-polynomial engine, max_{i∈S} |Fᵢ|, is < 1e-7 (round-trip check).

An accepted root is **Gate-4-valid** iff it passes Gate 4 at closure tolerance
1e-7 (engine default). A Gate-4-valid root is **near-degeneracy-flagged** iff
its minimum base-axis gap ratio < τ_deg = 1e-3 (per Amendment 03).

## 5. Classification (derived from the homotopy solve)

Per subset, isolated roots only — interval, fold, and boundary fields are null
by construction:

- **ROBUST_REALIZABLE** — ≥ 1 Gate-4-valid root that is not
  near-degeneracy-flagged. (This is H4's "robust-realizable".)
- **REALIZABLE_NEAR_DEGENERATE** — Gate-4-valid roots exist, all flagged.
- **ALGEBRAIC_ONLY** — accepted real roots exist, none Gate-4-valid.
- **ALGEBRAIC_EMPTY** — no accepted real roots.

The H4 outcome variable is ROBUST_REALIZABLE (binary), evaluated exactly as
registered in Amendment 03.

## 6. Dual-engine agreement criterion (frozen)

Roots are matched across engines by bijective nearest-neighbour assignment in
(b, c, d, e, g, h) by ascending pairwise max-coordinate distance. A homotopy
root and a Newton root **match** iff their distance
max_k |Δ(b,c,d,e,g,h)_k| ≤ ε, ε = 1e-6.

A subset's two solves **agree** iff **all** of:

1. identical class label (§5);
2. equal count of accepted admissible real roots;
3. every accepted root on each side matches one on the other within ε;
4. identical Gate-4-valid verdict on every matched pair.

Any failure of (1)–(4) sets `agree = false`, records the specific discrepancy
(class / count / unmatched-root / Gate-4 mismatch), and **excludes the subset
from the confirmatory tally pending investigation**. H4 is evaluated only after
every disagreement is resolved at the level of the mathematics — never by
silently choosing one engine, adjusting ε, or reconciling after the fact.

## 7. Output encoding (mechanical)

The runner (`spherical_census_runner_v2.py`, `--adapter ingest`) writes the
homotopy classification to the CSV summary and the full forensic JSONL (all
accepted roots, valid and invalid, each with coordinates, h, Gate-4 verdict,
residual). Each JSONL row additionally carries `agree`, the Newton root count,
and the discrepancy code, plus per-row `engine_sha` and `run_id`. A run manifest
and `SHA256SUMS` over CSV / JSONL / log / manifest close the provenance layer.

## 8. Provenance

- Universe: `size6_universe_v1.csv` SHA-256
  `e6b6e8b0968876bd3b3d0654d3705f9843699e9e7e08ff4d946e36187627c45b` (3044 rows)
- Spherical engine SHA-256 (Gate-4 / chain of record):
  `a0772717e4d07c327e744608bd0abf4f9a50d5f343b07fc3ffc119a7cd8a59af`
- Homotopy lift source SHA-256: ______ (backfill when the lift source is frozen)
- Newton validation source SHA-256: ______ (backfill when the Newton source is frozen)
- Runner SHA-256: ______ (backfill when the runner is frozen)
- Repository commit: resolved by the signed tag `spherical-amendment-04`. A
  document cannot contain the hash of the commit that contains it, so the
  binding is the signed, timestamped tag (tag -> commit -> tree -> this file),
  with the file's own SHA-256 recorded in the commit and tag messages.
- Git tag: `spherical-amendment-04`

This amendment freezes the *procedure* before the *instrument* is built: the
three source hashes above are filled in a later signed backfill commit, once the
homotopy lift, Newton solver, and runner are frozen.
