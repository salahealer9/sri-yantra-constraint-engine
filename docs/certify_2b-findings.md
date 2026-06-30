# 2b Local Certifier — reusable rigor gate, contract proven (5-case battery PASS)

**Status.** Exploratory build (no driver/engine changes). First component of the hybrid
finishing architecture: the reusable 2b geometric certifier every candidate (presence pass
and post-homotopy) must pass. Contract proven by the full test battery. Frozen v1.2 and the
frozen engine UNCHANGED.

## Contract
certify_2b_candidate(subset, candidate, radii) -> (status, evidence_bundle)
  CERTIFIED_UNIQUE_GEOMETRIC  real, in B_sphere, full-chain domain-valid on the whole box,
                              correct 2b coords, Krawczyk K(X) ⊆ int(X) -> one real root.
  NOT_CERTIFIED               chain real near the candidate but no radius certified
                              (off-root / contraction failed / genuinely-complex / not a
                              local approximate root).
  DOMAIN_INVALID              chain not real at the candidate or over any box (acos/atan
                              domain / cone edge).
  TECH_FAIL                   crash / NaN / unreadable.

## Design decisions that make the gate honest
- REALNESS is never inferred from "imaginary part is tiny". A complex candidate is projected
  to its real part and refined in the REAL system; realness is established only by a
  successful real-system Krawczyk certificate, not by Im-smallness.
- Refinement is a LOCAL polish, not a global solve: a displacement cap (2e-2) rejects a
  candidate that Newton would otherwise drag into a distant root's basin. A genuine homotopy
  endpoint moves ~1e-15..1e-3; a random point moves O(1) and is rejected as NOT_CERTIFIED.
- DOMAIN pre-check: if the chain is not real at the candidate (RAO raises), return
  DOMAIN_INVALID before refinement.
- Status names are lexically honest: CERTIFIED_UNIQUE_GEOMETRIC names the full geometric
  certificate (not "algebraically unique"); numeric/refinement outcomes can only downgrade
  to NOT_CERTIFIED, never upgrade to certified.
- EVIDENCE BUNDLE (auditable, JSON-serializable): status, subset_id, input_candidate,
  real_projected_center, radius_used, box_bounds (uv), full_chain_guard_result,
  krawczyk (verdict + cond(J)), residual_norm, polish_displacement, in_bsphere, engine_hash.
- DUPLICATE handling (collapse_certified): overlapping certified boxes collapse to one root
  (conservative lower bound); k distinct roots requires k pairwise-disjoint certified boxes
  (distinctness is part of the certificate).

## Battery (test_certify_2b.py) -- ALL PASS
  1  known {1,2,3,4,6,7} root      -> CERTIFIED_UNIQUE_GEOMETRIC  (r=3e-4, resid=3.2e-16,
                                       cond(J)=137, polish disp 8e-16)
  2  off-root interior (far)       -> NOT_CERTIFIED               (polish moved 1.8 > 2e-2)
  3  out-of-domain / edge point    -> DOMAIN_INVALID              (acos arg > 1 at candidate)
  4  complex-near-real (Im=1e-7)   -> CERTIFIED_UNIQUE_GEOMETRIC  (refined to real, certified)
  4b genuinely complex (far real)  -> NOT_CERTIFIED               (not a local real root)
  5  two overlapping certs         -> collapsed count = 1
  5b two disjoint certs            -> collapsed count = 2         (distinctness proven)

## Role in the architecture
This is the shared rigor gate for BOTH census loops:
  - Feasibility pass: certify the first real candidate -> FEASIBLE_CERTIFIED (short-circuit).
  - Post-homotopy: classify every discovered candidate (presence side) before any
    completeness claim. Absence (INFEASIBLE_CERTIFIED) is NOT produced here -- it requires
    faithful polynomialization + a completeness theorem (next probe).
engine_hash recorded in every bundle ties each certificate to the frozen engine for
re-verification.

## Next
1. Small feasibility-candidate pass on sample subsets (uses this gate).
2. Polynomialize the {1,2,3,4,6,7} chain; estimate mixed volume / path count -> decides
   whether the absence branch (INFEASIBLE_CERTIFIED) is realistic before defining it.

## Files
  certify_2b.py        reusable certifier + collapse_certified (wraps frozen 2b machinery)
  test_certify_2b.py   the 5+2 case contract battery (reproducible)
  certify_2b-findings.md  this report

SHA-256 hashes for all files in this unit are recorded in `docs/SHA256SUMS`