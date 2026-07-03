# A certified two-layer presence census of the spherical Sri Yantra constraint system
## Manuscript outline (skeleton — 2026-07-03, paper mode)

Numbers below are frozen; cite docs/CURRENT_CHECKPOINT.md (tag spherical-census-layer1-v1.2).
Each section lists the findings doc(s) that feed it, so the outline doubles as an index of written material.

---

## RESULT STATEMENT (draft — the two paragraphs the abstract/intro build on)

CLAIM (presence):
"The registered 3044-subset spherical Rao constraint universe contains at least 888 feasible
constraint systems, supporting 968 roots certified under Krawczyk interval validation. Each certified
root is separately classified for Rao (Gate-4) geometric validity, yielding 525 valid Rao figures and
443 algebraically-real roots rejected by the registered Gate-4/Rao-validity test. Seventy-seven subsets admit more than one certified
root; geometric validity is an irreducibly per-root property: 26 subsets carry both a valid and a
rejected certified root (verified directly from CENSUS_CHECKPOINT_LAYER1_K12)."

LIMITATION (immediately following — the reviewer-safe boundary):
"The remaining 2106 subsets are not claimed infeasible; they are unresolved under the tested
domain-wide generator budgets k in {6,12}, whose escalation terminated by a stopping rule
pre-registered before the run (fewer than 25 new certified subsets at k=12). The 50 certification
refusals are mechanism-tagged non-certifications, not negative certificates. No absence is certified;
INFEASIBLE_CERTIFIED = 0."

---

## 1. The Rao spherical system and the registered subset universe
    - Rao (1998) spherical form: 6 basic variables (b,c,d,e,g,h); eq (2.2) r=a+b+c=d+e+f=pi/2-h.
    - 20 constraint functions F1..F20; over-determined; a "figure" = 6 constraints satisfied simultaneously.
    - Well-posed universe: {1,2}+C(18,4) minus rank-deficient = 3044 (rank scan, DEG_TOL, seeded).
    - Registered Meru domain h in (0, pi/2); r=pi/2-h.
    FEEDS FROM: (universe construction notes; analyze_deps rank scan)

## 2. Two layers: constraint-root vs Rao-valid figure
    - Layer 1: certified real root of the 6-constraint subsystem (algebraic object).
    - Layer 2: Rao/Gate-4 geometric validity is the operational validity test used here. Its
      base-point ORDERING/CONTAINMENT COMPONENT (a=r-(b+c)>=0, f=r-(d+e)>=0) is grounded in Rao
      (1998) eq (2.2) and the p.226 out-of-range remark. (Full Gate-4 also includes
      constructibility/closure; the rejections here are ordering/containment -- see section 8.)
    - KEY: validity is PER-ROOT, not per-subset (26 both-type subsets). Unrepresentable under
      subset-level tagging; example (1,2,3,4,6,13) admits both a valid and a rejected root.
    FEEDS FROM: gate4-two-layer-findings.md, gate4-vs-source-finding.md (bfa9bf79)

## 3. Certification method
    - certify_2b_general: 2b coordinate transform (uv=[b,h+c,h+d,e,g,h]), real Newton (6x6, h free),
      Krawczyk interval operator, disjoint-box collapse for distinct-root count.
    - Radii policy: registered extended list [3e-3..1e-7] passed EXPLICITLY; engine frozen
      (sha de64edfa4979) and unchanged; radius_used recorded per root.
    - AA-overestimation mechanism: the 1e-5 default floor left certifiable roots uncertified;
      smaller boxes verify uniqueness (cond identical across radii -> root unchanged, box changed).
    - Cond filter COND_MAX=1e8: 0/294 candidates above cond 1e6 ever certified; high-cond -> sidecar.
    FEEDS FROM: certify_2b-findings.md, refusal-structure-finding.md (d972c657),
                census-checkpoint-layer1-r2-findings.md (radii mechanism)

## 4. Discovery tiers (the yield curve)
    - Warm-start (Table 1 + benchmark + transfer p0/p3): 26 certified. Reach exhausted (14->4 diminishing).
    - Layer-1 neutral generator: full-domain multistart, strata box/logwide/neardeg/VIOL (viol targets
      the containment-violating region a Gate-4-filtered generator structurally misses). No ordering
      seed filters; hygiene (domain) filters only. Retires find_seed/L.newton (5-var fixed-altitude,
      structurally can't solve 6-var census subsets).
    - R2: extended-radii re-certification of the 78 CERT_FAILED -> +40 (AA-overestimation).
    - k-escalation (pre-registered): k=6 -> 876; k=12 over 2130 -> +12; N<25 stop -> k=24 not run.
    - Domain audit (main text, concise): a domain-audit stage detects and excludes super-hemispheric
      candidates outside the registered h-domain (h<=0, r>pi/2); these are retained as a sidecar and
      not counted. [Full 'impossible displacement 32.3' story -> APPENDIX / reproducibility note.]
    FEEDS FROM: gate4-two-layer-findings.md, layer1-shard0-findings.md (14d1397b),
                layer1-full-census-finding.md (45cfe0db), refusal-structure-finding.md,
                census-checkpoint-layer1-r2-findings.md (3714a543),
                census-checkpoint-layer1-k12-findings.md (cb159549), k-escalation-preregistration.md (60b4c296)

## 5. Final results (CENSUS_CHECKPOINT_LAYER1_K12)
    - 888 FEASIBLE_CERTIFIED / 968 distinct roots; 50 CERT_FAILED; 2106 NO_CANDIDATE.
    - Yield curve table: k=6 (836) -> R2 (876) -> k=12 (888), with seeds/converged/certified per tier.
    - Determinism, reproducibility, hash provenance.
    FEEDS FROM: CURRENT_CHECKPOINT.md (836019a6), census-checkpoint-layer1-k12-findings.md

## 6. Multiplicity and per-root Gate-4 validity
    - 77 multi-root subsets (root_lower_bound>1); disjoint-box collapse method.
    - ROOT-LEVEL split:   525 valid / 443 rejected  (= 968 certified roots)
    - SUBSET-LEVEL geography (verified from K12; inclusion-exclusion closes to 888):
        Gate-4 status by subset type          count
        valid-only                             474
        rejected-only                          388
        both-type (valid AND rejected root)     26
        --------------------------------------------
        total feasible                         888     (500 valid-bearing + 414 rejected-bearing - 26)
    - KEY CLAIM: the 26 both-type subsets prove Rao/Gate-4 validity is NOT a property of a constraint
      subset alone -- the same six-constraint subsystem may admit multiple certified roots of
      DIFFERENT geometric-validity status. Per-root metadata is mathematically necessary, not
      bookkeeping. ANCHOR: (1,2,3,4,6,13) -- an ORIGINAL Gate-4-rejected subset (warm-start era) --
      admits a second, Gate-4-VALID certified root.
    - viol-stratum-only certified roots (roots no other stratum reaches) -> a Gate-4-filtered
      generator provably misses real Layer-1 roots. Geography: invalid family benchmark-densest,
      not benchmark-confined.
    FEEDS FROM: gate4-two-layer-findings.md, layer1-full-census-finding.md, k12-findings

## 7. Refusal and sidecar populations (COMPACT TABLES, not prose)
    TABLE A -- the 50 UNRESOLVED_CERT_FAILED (uniformly post-extended-radii):
      mechanism            | count | interpretation                        | claim status
      guard-never-clean    |  ~33  | heavy interval dependency, near-sing. | refused, not disproven
      kraw:split           |   ~3  | genuine split at all radii            | refused, not disproven
      kraw:empty           |    2  | Krawczyk excludes the candidate root in the tested box | local negative (not subset-wide)
      [+12 k=12 refusals: mechanism-tag via recertify diagnostic to complete the table]
    TABLE B -- sidecars (audit material, NOT census input):
      sidecar          | count | why excluded                    | future-work value
      high-cond sidecar | ~10k | outside declared cond-bound proposal stream (COND_MAX=1e8; 0/294 above cond 1e6 certified in diagnostic sample) | near-singular strata study
      super-hemispheric |  972 | h<=0, r>pi/2, outside registered domain | registered-extension remark
    Krawczyk cuts both ways: beyond failing to certify, it can EXCLUDE a candidate root in a tested
    box (kraw:empty) -- a local negative on that candidate, not a subset-wide nonexistence claim.
    high-cond = conditioning EVIDENCE for near-singular structure, NOT a positive-dimension proof.
    FEEDS FROM: refusal-structure-finding.md, k12-findings, r2-findings

## 8. Limitations
    - No certified absence; INFEASIBLE_CERTIFIED=0; the global-homotopy absence route is architecturally
      hard (four-method convergence, scoped negative NOT impossibility).
    - Presence lower bound under tested generator/budget/domain; unreached != infeasible.
    - Gate-4 = ordering/containment COMPONENT is Rao-grounded; full Gate-4 also has closure/constructibility.
    FEEDS FROM: b1-and-absence-branch-findings.md, gate4-vs-source-finding.md

## 9. Reproducibility bundle
    - Frozen engine sha, GLOBAL_SEED, deterministic blake2b seeding; committed source regenerates all
      candidates byte-identically; checkpoint SHA256SUMS; GPG-signed tags v1.0/v1.1/v1.2 + paper-freeze-1.
    - Rao PDF NOT redistributed (citation + SHA only, copyright).
    FEEDS FROM: CURRENT_CHECKPOINT.md, SHA256SUMS, tag lineage

---

## Open decisions for the author (NOT blockers for a complete paper)
    A. Absence sample: include a small calibrated absence sample (timeboxed 5-10 subsets) as a section,
       or defer to future work? Present result is complete WITHOUT it. Do NOT let it delay the draft.
    B. High-cond study: appendix mention vs separate follow-up paper on near-singular strata.
    C. Refusal residue: the 50 as a single mechanism table (recommended) vs deeper per-case study (defer).
    D. Bookkeeping to clear independently: plane-study Zenodo v1.1.0 deposit (pre-dates this arc).

## Status of written material
    Sections 2,3,4,5,6,7,8,9 already have findings docs feeding them (mapped above). Section 1 needs
    a short universe-construction writeup. The RESULT STATEMENT prose above is draft-ready. The paper
    is assembly + prose, not new computation.
