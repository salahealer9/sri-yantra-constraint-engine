# Śrī Yantra Constraint Project — Future Work & Re-entry Guide

**Status date:** 2026-07-10
**State:** All active work concluded; three manuscripts under review; project parked.

This document is the hand-off for resuming the project after a pause. It records what
is frozen, what remains, and — for each remaining thread — the motivation, current
evidence, concrete steps, decision gates, and definition of done. Read the *Standing
discipline* section before touching anything.

---

## 0. Frozen state (do not modify; everything below builds on it)

| Artifact | Identifier |
|---|---|
| Spherical census checkpoint | `CENSUS_CHECKPOINT_LAYER1_K12`, tag `spherical-census-layer1-v1.2`, paper-freeze `paper-freeze-1` |
| Census standing | 888 `FEASIBLE_CERTIFIED` / 50 `UNRESOLVED_CERT_FAILED` / 2106 `UNRESOLVED_NO_CANDIDATE`; 968 certified roots; 525 Gate-4-valid / 443 rejected per root; 77 multi-root subsets; 26 both-type subsets; `INFEASIBLE_CERTIFIED = 0` |
| Frozen engines | spherical: `de64edfa4979`; plane: `tier2-freeze-2` (engine `0baa2c5`, blob `985c741`); mapper stack hash-pinned in Part I's frozen record |
| Registered radii list | `[3e-3, 1e-3, 3e-4, 1e-4, 3e-5, 1e-5, 3e-6, 1e-6, 3e-7, 1e-7]` — passed explicitly; `DEFAULT_RADII` in the certifier is never edited |
| Deposits | spherical dataset 10.5281/zenodo.21170076 · spherical viewer 10.5281/zenodo.21257120 · plane dataset 10.5281/zenodo.20742389 · plane viewer 10.5281/zenodo.20747115 · prereg 10.5281/zenodo.20778921 · reduction record 10.5281/zenodo.20772247 |
| Manuscripts under review | Plane census: IJHS-D-26-00188 · Part I (bridge theorem + validated extension): IJPA-D-26-00923 · Part II (spherical census): IJPA-D-26-00924 |
| Key sidecars (audited, NOT census input) | high-cond: 10,405 candidates / 1,232 subsets (`COND_MAX = 1e8`) · super-hemispheric: 972 candidates / 553 subsets (h ≤ 0) |
| Escalation status | k = 6 → 12 terminated by pre-registered stopping rule (N < 25 fired at 12 new); k = 24 NOT run, by rule |

Servers: `earthgrid-python` (plane engine + census repo at `/opt/sri-yantra-constraint-engine`),
`penguin` (`~/sri_yantra_spherical_viewer`). Candidate files are gitignored regenerables:
deterministic under `GLOBAL_SEED = 20260702` with blake2b per-cell seeding.

## Standing discipline (non-negotiable on re-entry)

1. **Preregister before running.** Selection rules, budgets, stopping rules, and claim
   criteria are committed before the run they govern. The k-escalation and the plane
   Tier-2 both proved this is what makes the results citable.
2. **Layer separation.** Discovery proposes; `certify_2b_general` decides;
   `census_io` records. Gate-4 is per-root metadata, never a filter or a label.
3. **Upgrade-only merges.** New results enter through a scratch census + the merge
   driver's lattice (`FEASIBLE > CERT_FAILED > NO_CANDIDATE`). A committed label is
   never downgraded or hand-edited. New label types (see absence, below) require the
   lattice to be *extended and registered* before any merge that uses them.
4. **Wording discipline.** "Certified-feasible", "rejected by the registered validity
   test", "unreached under tested generator budgets", "local negative on the candidate".
   Never "infeasible" without a certificate; never "Rao-invalid" as an absolute.
5. **Verify-don't-assert / commit-before-claim.** Numbers are regenerated from source;
   diagnostics are read before scaling; every surprising number gets an explanation
   before the next step (the h-domain hole was caught by one impossible displacement).
6. **Timebox strategic threads.** No thread below is allowed to gate a submission or
   a revision response. The absence program in particular carries an explicit timebox.

---

## Thread 1 — The absence program (the major open scientific thread)

**Question.** Can any of the 2106 `UNRESOLVED_NO_CANDIDATE` subsets be upgraded to a
*certified absence* (`INFEASIBLE_CERTIFIED`) — or, failing full certification, to the
honest intermediate label `NO_REAL_ROOTS_FOUND_TRACE_NUMERIC` that the census schema
already reserves?

**Why it matters.** The census is presence-only by design; its one asymmetry is
`INFEASIBLE_CERTIFIED = 0`. Even a small calibrated absence sample transforms the claim
structure from "presence census" to "presence census with a measured absence direction"
— a follow-up paper, or revision-stage ammunition if a referee asks.

**What is already known (do not re-learn).**
- Global homotopy over the whole universe was previously found architecturally
  unreachable — but that negative was *route-specific* (the global approach), not a
  statement about per-subset tractability.
- The plane Tier-2 playbook exists and worked: per-subset polynomialization →
  coefficient-parameter homotopy → completeness diagnostics → certified statements.
- The census schema already contains the label ladder:
  `NO_REAL_ROOTS_FOUND_TRACE_NUMERIC` (all complex roots found by a trace-complete
  run, none real-in-domain — numerical, not certified) and `UNRESOLVED_TRACE_FAILED`.
  `INFEASIBLE_CERTIFIED` is reserved for genuinely certified absence.

**Steps.**
1. **Preregistration (first, before anything runs).** One document fixing:
   - *Sample selection rule.* Stratified from the 2106: primarily the "silent" ~1700
     (zero converged candidates anywhere — most plausibly root-free); a few from the
     ~410 with high-cond sidecar candidates as contrast (these are plausibly NOT
     root-free, so they calibrate the method's presence-detection).
     Deterministic selection (seeded), size 5–10 to start, expansion rule stated.
   - *Protocol.* Polynomialization convention (see step 2), homotopy method
     (HomotopyContinuation.jl; polyhedral start systems), completeness criteria
     (root count vs BKK bound, monodromy/trace test passing, zero path failures,
     endgame diagnostics clean), and the real/domain filter for found roots.
   - *Claim ladder.* Trace-complete + no real in-domain roots →
     `NO_REAL_ROOTS_FOUND_TRACE_NUMERIC`. Certified absence (`INFEASIBLE_CERTIFIED`)
     requires an additional certified step: certified isolation of ALL complex roots
     (e.g., alphaCertified-style or interval Newton on every root) plus certified
     exclusion of each from the real domain box. If any found root IS real-in-domain:
     that is a *presence discovery* — it goes through the standard certifier and the
     upgrade-only merge (the absence program doubles as the strongest possible
     presence source, since homotopy is exhaustive where multistart is not).
   - *Timebox and stopping rule.* E.g., "N subsets or T hours of tuning, whichever
     first; if 0/N reach even the trace-numeric label, record the scoped negative
     ('per-subset homotopy did not reach completeness under the registered protocol')
     and close the thread."
2. **Polynomialization module.** Convert the spherical trig chain to a polynomial
   system: substitute (c_i, s_i) per angle with c² + s² = 1 side conditions, or
   tan-half-angle; the plane Tier-2 code is the template. Expect dimension growth
   (6 vars → roughly 12–16 polynomial vars). Freeze and hash the module; validate it
   the proven way — inject a known certified root (from `spherical_roots.jsonl`, not
   Table 1) and require residual ~1e-15 through the polynomial system.
3. **Smoke gate before the sample.** Run the full protocol on TWO controls: one
   known-FEASIBLE subset (must rediscover its certified root(s), count matching the
   census where multi-root) and one arbitrary subset for mechanics. Same
   smoke-first discipline as every prior tier.
4. **Run the registered sample; read per-subset diagnostics before any label.**
5. **Lattice extension + merge.** Register where the new labels sit
   (`INFEASIBLE_CERTIFIED` > trace-numeric > `NO_CANDIDATE`, with `FEASIBLE` beating
   everything and CONTRADICTION = HALT if a trace-numeric subset later certifies a
   root — that would be a protocol falsification and must stop the pipeline, not be
   merged). Extend `merge_census_layer1.py`'s `RANK` accordingly, with a negative
   test (a fabricated contradiction must HALT) before the real merge. New checkpoint
   name: `CENSUS_CHECKPOINT_ABSENCE_S1` or similar.
6. **Decide output.** ≥1 certified absence or a clean trace-numeric batch → short
   follow-up paper or revision addition. 0/N → one scoped paragraph in the findings
   record; thread closed honestly.

**Effort estimate.** Prereg + polynomialization + smoke: 2–4 focused days. The sample
itself: hours per subset, dominated by tuning. **Definition of done:** the sample's
preregistered outcomes are recorded in a merged checkpoint or a scoped negative note.

---

## Thread 2 — The high-conditioning sidecar study (degenerate strata)

**Question.** What IS the 10,405-candidate near-singular population: (a) isolated but
atrociously conditioned roots, (b) near-double roots, or (c) genuine
positive-dimensional real components of the constraint varieties? (c) is a
theorem-shaped result: the universe's well-posedness rank check was pointwise (8
samples/subset) and cannot exclude rank collapse on subvarieties.

**Evidence in hand.** Zero certifications ever observed at cond(J) ≥ 1e6 (0/294 in the
diagnostic sample); the 1e6–1e10 band was 218/218 Gate-4-invalid; candidate clouds up
to 24 round-9-distinct points per subset with NN distances from 1e-7 (sliding along a
near-null direction) to 1e-1 (spread along sheets). Entry point: the 410 k12-era
sidecar subsets (unreached-but-not-silent). Worst known case: (1,2,10,13,16,17).

**Steps.**
1. Cheap numerics first (no new tooling): per-subset candidate-cloud geometry — PCA
   dimension of each cloud, SVD/rank profiles of J *along paths between* clustered
   candidates (a rank drop persisting along the path is the positive-dimension
   signature; a rank recovery mid-path suggests two isolated roots).
2. Classify the 1,232 subsets by signature; pick the 3–5 cleanest candidates for (c).
3. For those, numerical algebraic geometry on the polynomialized system (reuses
   Thread 1's module): witness sets / dimension computation in HC.jl. A confirmed
   positive-dimensional real component is the headline; document its constraint-
   combination structure (the discrete analogue already exists: the exact dependency
   F16 ≡ F9 − F8 in Rao's excluded subset — this would be its continuous cousin).
4. If confirmed: a new census annotation category needs registration
   (e.g., `DEGENERATE_COMPONENT_EVIDENCED`) — annotation, never a certification claim,
   unless a certified positive-dimension method is used.

**Effort.** Step 1 is a scripting afternoon; steps 2–4 are a real study (a follow-up
paper of its own). **Done when:** the (a)/(b)/(c) question is answered for at least the
worst subsets, with the answer's epistemic status stated (numerical evidence vs proof).

---

## Thread 3 — Refusal-residue micro-studies (small, self-contained)

The 50 refusals are mechanism-tagged (44 guard-never-clean / 4 kraw:split /
2 kraw:empty, all post-extended-radii). Three afternoon-scale dives:

1. **The 4 `kraw:split` subsets — twin-root hypothesis.** Krawczyk splitting at all
   radii down to 1e-7 with clean guards suggests two roots closer than the smallest
   box. Test: dense deterministic multistart in a ball of radius ~1e-5 around each
   candidate; if two distinct converged points < 1e-7 apart appear, the hypothesis is
   confirmed. Certification of near-twins likely needs precision beyond doubles
   (mpmath-backed Newton + smaller radii) — treat as optional; the *finding* (near-
   double roots exist, connecting to the mapper-era fold structure) is the value.
2. **The 2 `kraw:empty` subsets (4 candidates) — pseudo-root anatomy.** Krawczyk
   *disproved* roots at resid ≤ 1e-8: map the residual landscape locally (is it a
   near-tangency where |F| dips without crossing?). One plot per subset; a nice
   appendix figure someday.
3. **The 44 guard-never-clean — overlap check with Thread 2.** Cross-reference against
   the high-cond signatures; most are probably the same near-singular fringe. If some
   are NOT (moderate cond, guard still splits), those are AA-dependency cases where a
   higher-order Taylor-model guard could convert refusals — a tooling upgrade to note,
   not necessarily to build.

**Done when:** each mechanism has one paragraph of explanation backed by a script in
the repo, upgrading Table A's "interpretation" column from plausible to demonstrated.

---

## Thread 4 — Super-hemispheric extension (deferred; registration-gated)

972 real roots at h ≤ 0 (r > π/2) sit in the audit sidecar: caps larger than a
hemisphere. Currently one honest sentence in Part II. If ever pursued:
- It is a NEW registered domain (r ∈ (π/2, π)), not a widening of the old box —
  new preregistration required.
- Gate-4's constructor **wraps trigonometrically there and returns spurious 'valid'**
  (observed: h = −4.056 tagged valid). A super-hemispheric validity theory must be
  built before any Layer-2 claim; until then only Layer-1 statements are possible.
- Generator change is trivial (drop the h-floor *under the new registration*); the
  hard work is the geometry of what such figures even mean.

**Priority: low.** Only worth doing if the geometric question becomes interesting in
its own right.

---

## Thread 5 — Discovery beyond k = 12 (rule-gated; mostly superseded)

The stopping rule fired and the escalation is closed; reopening budget escalation
requires a NEW preregistration that explicitly supersedes the old one (state this in
the document — never quietly resume a stopped rule). But note: Thread 1's homotopy is
a *different source*, not an escalation — where it runs, it is exhaustive, so it
strictly dominates further multistart on those subsets. Practical consequence: don't
spend time on k = 24 or new seeding families unless Thread 1 fails AND a specific
subset population justifies it.

---

## Thread 6 — Visual-form taxonomy formalization (optional)

The five-class visual taxonomy (canonical-looking / coherent-large-cap / near-boundary
/ distorted-extreme / unclassified) is exploratory viewer metadata. If it is ever to
appear as a *result*: define each class by registered geometric predicates (the
`cap_violation` containment rule is already hard; the others need thresholds with the
geometry-grounded calibration discipline — remember the var_spread lesson, where the
naive threshold would have flagged Rao's own optimum), preregister, reclassify, and
demarcate confirmatory from the existing exploratory labels. Otherwise leave as-is;
the current firewall wording is correct and sufficient.

---

## Thread 7 — Bookkeeping, review-cycle readiness, and archive hygiene

- **Referee responses (the only time-sensitive item while parked).** Three manuscripts
  in review. Keep the frozen engines and diagnostic scripts runnable: every plausible
  referee question ("why is X refused?", "re-derive figure Y", "what happens at
  radius Z?") already has a committed tool. Re-entry for a revision = checkout tag,
  re-run the relevant diagnostic, quote the output.
- **On acceptance of any paper:** update the cross-citations in the *other*
  manuscripts (submission numbers → DOIs/volume) at their revision stages; update
  Zenodo related-identifiers (add `isCitedBy` / publication DOIs); refresh
  CURRENT_CHECKPOINT.md and both viewers' "cite as" blocks.
- **If referees force dataset changes:** new Zenodo *version* under the concept DOI,
  assembled with `assemble_zenodo_spherical.sh` (edits first, hashes last) — never
  edit a published version's files.
- **Plane-paper corrigendum:** IJHS was reviewing the corrigendum first; track its
  resolution and mirror any outcome into the plane dataset record if needed.
- **Archive hygiene:** confirm the repos' tags are GPG-signed through
  `paper-freeze-1`; confirm the k12/full candidate meta JSONs (small) are committed
  even though the candidate JSONLs are regenerable; one line in the README pointing
  at THIS document.

---

## Suggested re-entry order

1. Read *Standing discipline* + *Frozen state* above; `git log --oneline -20` on both repos.
2. Whatever the review cycle demands (Thread 7) — always first.
3. Thread 3.1 (twin roots) as the warm-up: one afternoon, self-contained, and its
   answer feeds both Thread 2's classification and any referee question about the 4 splits.
4. Thread 1 preregistration written *fresh but before any code* — it is the main event.
5. Thread 2 step 1 can run as background scripting while Thread 1's homotopy tooling
   is being built (they share the polynomialization module — build it once).
6. Threads 4–6 only by explicit later decision.

*Written 2026-07-10, at the close of the submission arc: plane census IJHS-D-26-00188;
Part I IJPA-D-26-00923; Part II IJPA-D-26-00924. Everything above starts from
`CENSUS_CHECKPOINT_LAYER1_K12` and the standing discipline. — assembled with Claude.*
