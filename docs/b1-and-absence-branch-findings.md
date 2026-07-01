# B1 + ABSENCE-BRANCH CLOSEOUT {1,2,3,4,6,7}: the full-lift mixed volume is empirically
#   enormous across four independent methods; certified absence via global homotopy is NOT
#   operationally reachable through this architecture. Census proceeds PRESENCE-FIRST.

**Status.** Exploratory closeout (no driver/engine changes). Records the Route B1 exact
mixed-volume attempt and fires the pre-committed conclusion for the spherical absence branch.
Frozen engine UNCHANGED. This is an ARCHITECTURAL negative, NOT a proof that certified absence
is impossible.

## Route B1 result (recorded honestly)
ROUTE_B1_FULL_SUPPORT_EXACT_MV = NOT_OBTAINED (DEMiCs did not complete; run reboot-truncated)
  backend                = PHCpack v2.4.92 (7 Nov 2025), `phc -m`, DEMiCs algorithm
  menu path              = 5 (DEMiCs), n (sep. cells), n (stable MV -> ordinary MV), n (user
                           lifting), y (monitor), n (no homotopy solve)
  input                  = lift_123467_supports.json (50 eqs / 50 vars / 338 monomials)
  input_supports_sha256  = 5d03cb04f11008d511e5b233c500414c11186553715fa52a11e7911d73f590b9
  run profile            = ~11 h wall, ~100% CPU pinned throughout, RSS flat ~113 MB (NO memory
                           blowup, NO OOM, NO phc error in logs)
  termination cause      = HOST REBOOT (unattended-upgrades / apt-daily-upgrade.timer ~06:00 UTC;
                           uptime confirmed the box rebooted mid-run). External infrastructure
                           event -- NOT a computational limit, NOT a backend failure, NOT a
                           session drop. DEMiCs began mixed-cell enumeration (start banner
                           written) but no mixed volume was produced before the reboot.
  honest reading         = the 11 h non-completion is a data point (DEMiCs, the PHCpack mixed-cell
                           enumerator used for this Route B1 attempt, did not finish within the
                           reboot-truncated 11 h window), but because the run was truncated
                           externally it does NOT by itself prove DEMiCs *could not* finish. It is
                           corroborating, not decisive.

## The four-method convergence (the actual scientific answer)
The decisive evidence is the agreement of independent methods, not any single run:
  1. HC.jl / MixedSubdivisions : Int32 OVERFLOW at an intermediate ~7.5e14 (BACKEND_OVERFLOW).
  2. Route A degree-box bound   : permanent(D) = 1.12e12 (VALID but LOOSE upper bound; it does
                                  NOT prove the true reduced MV is large -- it fails to certify
                                  tractability and is consistent with the other large-scale
                                  signals, nothing more).
  3. Route B2 exact elimination : EXPLODED -- the smallest constraint cone (F3, 7 nodes) already
                                  fails coefficient-exact reduction (degree 22 / 1169 terms after
                                  one node, timeout on the second). Reduced support not obtainable
                                  by direct sequential resultant elimination under the guards.
  4. Route B1 DEMiCs            : ~11 h pinned CPU, no completion (reboot-truncated).
Three of the four are clean, uninterrupted results; all four point the same way. The full-lift
mixed volume is empirically ENORMOUS -- far beyond feasible polyhedral-homotopy path-tracking.

## PRE-COMMITTED CONCLUSION (fires)
Certified absence via global homotopy is NOT operationally reachable through the current
global-homotopy / full-lift architecture. Four independent methods -- HC.jl/MixedSubdivisions
(overflow), the degree-box bound (~1e12, which fails to certify tractability), coefficient-exact elimination (explosion), and DEMiCs
(non-completion in 11 h) -- could not produce the mixed volume or the reduced system. This is an
ARCHITECTURAL negative: B1 measures the full LIFTED support (which pays the 2^19 node-cover
slack), not an ideal minimal algebraic formulation. It is NOT a proof that certified absence is
impossible; a different formulation (structured/triangular elimination, a minimal ideal, an
exact backend on a reduced system, or future hardware/time) is not excluded.

Therefore, for THIS project architecture:
  INFEASIBLE_CERTIFIED is NOT operationally reachable for now.
  The spherical census proceeds PRESENCE-FIRST with certified lower bounds:
    - candidate search + full-chain guard + 2b Krawczyk certification (certify_2b) establishes
      FEASIBLE_CERTIFIED and certified root lower bounds (PARTIAL_CERTIFIED_ROOTS_K);
    - absence is reported only as UNRESOLVED_* / NO_REAL_ROOTS_FOUND_TRACE_NUMERIC, never as
      INFEASIBLE_CERTIFIED, per the census_io guardrails.

## Status board (final for the absence-branch investigation)
    FULL_LIFT_MIXED_VOLUME           = BACKEND_OVERFLOW (Int32, intermediate ~7.5e14)
    ROUTE_A_DEGREE_BOX_UPPER_BOUND   = 1.12e12   (valid, loose; fails to certify tractability, does NOT prove true MV large)
    ROUTE_B1_FULL_SUPPORT_EXACT_MV   = NOT_OBTAINED (DEMiCs 11 h, reboot-truncated)
    ROUTE_B2_REDUCED_SUPPORT_MV      = NOT_OBTAINED
    ROUTE_B2_SUPPORT_STATUS          = failed (coefficient-exact by direct elimination)
    ABSENCE_BRANCH                   = NOT_OPERATIONALLY_REACHABLE (this architecture)
    CENSUS_MODE                      = PRESENCE_FIRST_WITH_CERTIFIED_LOWER_BOUNDS

## What remains untouched and valid (banked)
- certify_2b : the geometric rigor gate (7/7 battery) -- unchanged, valid.
- census_io  : JSONL source-of-truth + manifest + SHA256SUMS, INFEASIBLE guardrail -- unchanged.
- the polynomialization lift : implementation validated (known-root gate 6.66e-16) -- unchanged.
- the presence-first spherical census with certified roots / lower bounds -- fully intact.
The absence branch closing does NOT weaken any presence-side result. It scopes the census claim
honestly: certified presence + certified lower bounds, with certified absence out of reach for
this architecture.

## Reproducibility / provenance
  run_b1_phc_mixedvol.py       one-command B1 runner (menu-driven phc -m, provenance capture)
  lift_123467_supports.json    the exact supports fed to the backend (sha 5d03cb04...)
  (A retry with an uninterrupted >11 h window -- e.g. nohup started just after the ~06:00 UTC
   apt-upgrade window, B1_TIMEOUT below the next window -- could still land a certified integer
   or a clean uninterrupted-timeout; it would strengthen the record but does NOT change this
   conclusion. Left as optional future work.)

## Files
  b1-and-absence-branch-findings.md   this closeout report
  run_b1_phc_mixedvol.py              B1 runner (for reproducibility / optional retry)

SHA-256 hashes for all files in this unit are recorded in `docs/SHA256SUMS`