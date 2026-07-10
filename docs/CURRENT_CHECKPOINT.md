# CURRENT CHECKPOINT — single source of truth

Frozen 2026-07-03. Authoritative record of the final presence-census numbers. Derivation lives in
the K12 findings doc; THIS file is the result. If a findings doc disagrees, this file is correct.

## Current checkpoint
    CENSUS_CHECKPOINT_LAYER1_K12   (tag: spherical-census-layer1-v1.2)

## Universe
    3044 well-posed spherical Rao subsets (registered)

## Final standing
    FEASIBLE_CERTIFIED:        888   / 3044
    UNRESOLVED_CERT_FAILED:     50
    UNRESOLVED_NO_CANDIDATE:  2106            (888 + 50 + 2106 = 3044)
    certified distinct roots:  968
    Gate-4 per-root:           525 valid / 443 rejected     (= 968)
    multi-root subsets:         77

## Registered policies
    h-domain:                  (0, pi/2)
    Gate-4 closure_tol:        1e-7   (per-root metadata; never a filter or relabel)
    certifier engine hash:     de64edfa4979   (unchanged; frozen reference)
    extended radii (explicit): [3e-3, 1e-3, 3e-4, 1e-4, 3e-5, 1e-5, 3e-6, 1e-6, 3e-7, 1e-7]
    k-escalation:              stopped by pre-registered N<25 rule (k=12 gave 12 < 25; k=24 not run)

## Not claimed
    - unresolved does NOT mean infeasible; INFEASIBLE_CERTIFIED = 0
    - no certified absence (unreached = "no candidate under tested budget k in {6,12}")
    - high-cond and super-hemispheric sidecars are audit material, NOT census input

## Lineage
    LAYER1 v1.0 (836) -> R2 v1.1 (876) -> K12 v1.2 (888)  [supersede in coverage, not validity]

## Record published Zenodo DOI for spherical census dataset v1.0.0
    10.5281/zenodo.21170076                                                                                                                                                                                                            
## Future work
See [FUTURE_WORK.md](FUTURE_WORK.md) for the full research roadmap, standing discipline,
and re-entry guide (2026-07-10).
