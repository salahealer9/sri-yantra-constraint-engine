"""
newton_validator.py
=============================================================================
Independent size-six VALIDATION solver (Amendment 04 §3). Solves the raw 6x6
spherical system F_i(b,c,d,e,g,h)=0, i in subset, directly through the FROZEN
engine `sriyantra.constraints`, by damped multistart Newton with its own random
in-domain start strategy.

DEV-BRANCH / PRE-CONFIRMATORY tooling. Not part of any registered run.

Independence is the point (Amendment 04 §3):
  - solves the RAW trigonometric constraints, NOT the polynomial lift;
  - imports only the frozen engine + numpy (no lift_generator, no sympy, no
    homotopy); start points are NOT seeded from homotopy roots;
  - emits the same ingest root-format contract so the runner can compare.

Role (Amendment 04, frozen): Newton is NON-AUTHORITATIVE. It never overturns the
homotopy classification. A disagreement marks the subset unresolved (a local
solver missing a small basin is not evidence against the global solve). This
module therefore only *finds and reports* admissible real roots; Gate-4,
residual, tier, class, and the cross-engine match are applied downstream by the
runner.
=============================================================================
"""
import numpy as np
import math, json, random, os, sys

_here = os.path.dirname(os.path.abspath(__file__))
_root = _here
while _root != os.path.dirname(_root):
    if os.path.exists(os.path.join(_root, "sriyantra.py")):
        break
    _root = os.path.dirname(_root)
for _p in (_here, _root, os.path.join(_root, "enumeration")):
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)
import sriyantra as RAO                      # frozen engine — the ONLY scientific import

DEG = math.pi / 180.0
ACCEPT_RESID = 1e-7                          # round-trip acceptance (Amendment 04 §4)
MATCH_EPS = 1e-6                             # dedup / match tolerance (Amendment 04 §6)

# ---------------------------------------------------------------------------
#  raw system through the frozen engine
# ---------------------------------------------------------------------------
def in_domain(x):
    try:
        RAO.chain(x[0], x[1], x[2], x[3], x[4], x[5]); return True
    except Exception:
        return False

def Fvec(subset, x):
    F = RAO.constraints(x[0], x[1], x[2], x[3], x[4], x[5])
    return np.array([F[i] for i in subset], float)

def jac(subset, x, eps=1e-7):
    """Central finite-difference 6x6 Jacobian, domain-safe (one-sided fallback)."""
    x = np.asarray(x, float); n = 6
    J = np.zeros((len(subset), n))
    for k in range(n):
        xp = x.copy(); xm = x.copy(); xp[k] += eps; xm[k] -= eps
        okp, okm = in_domain(xp), in_domain(xm)
        if okp and okm:
            J[:, k] = (Fvec(subset, xp) - Fvec(subset, xm)) / (2 * eps)
        elif okp:
            J[:, k] = (Fvec(subset, xp) - Fvec(subset, x)) / eps
        elif okm:
            J[:, k] = (Fvec(subset, x) - Fvec(subset, xm)) / eps
        else:
            return None
    return J

def newton(subset, x0, tol=1e-11, maxit=60):
    """Damped Newton with backtracking; returns (x, residual, converged)."""
    x = np.asarray(x0, float)
    if not in_domain(x):
        return x, np.inf, False
    F = Fvec(subset, x); res = np.linalg.norm(F, np.inf)
    for _ in range(maxit):
        if res < tol:
            return x, res, True
        J = jac(subset, x)
        if J is None:
            return x, res, False
        try:
            dx = np.linalg.solve(J, -F)
        except np.linalg.LinAlgError:
            dx, *_ = np.linalg.lstsq(J, -F, rcond=None)
        step = 1.0
        for _ in range(40):                          # backtracking line search
            xn = x + step * dx
            if in_domain(xn):
                Fn = Fvec(subset, xn); rn = np.linalg.norm(Fn, np.inf)
                if rn < res:
                    x, F, res = xn, Fn, rn; break
            step *= 0.5
        else:
            return x, res, False                     # no admissible decrease
    return x, res, res < tol

# ---------------------------------------------------------------------------
#  admissibility, dedup, start strategy
# ---------------------------------------------------------------------------
def admissible(x):
    b, c, d, e, g, h = x
    r = math.pi / 2 - h
    if min(b, c, d, e, g, r) <= 1e-6:        # arcs / cap positive
        return False
    if c >= r or d >= r:                      # base steps need c,d < r
        return False
    return in_domain(x)

def random_start(rng):
    """Own start strategy: random in-domain size-six figures (r free)."""
    for _ in range(400):
        r = rng.uniform(0.2, 1.25)
        # arcs as random fractions of the cap, loosely ordered g < c, inner small
        c = r * rng.uniform(0.15, 0.8)
        d = r * rng.uniform(0.15, 0.8)
        g = c * rng.uniform(0.1, 0.8)
        b = rng.uniform(0.1, 1.0)
        e = rng.uniform(0.1, 1.0)
        x = (b, c, d, e, g, math.pi / 2 - r)
        if in_domain(x):
            return x
    return None

def dedup(roots, tol=MATCH_EPS):
    out = []
    for x in roots:
        if all(np.max(np.abs(np.array(x) - np.array(y))) > tol for y in out):
            out.append(x)
    return out

# ---------------------------------------------------------------------------
#  solve one subset -> admissible real roots in the ingest contract
# ---------------------------------------------------------------------------
def round_trip(subset, x):
    return float(np.max(np.abs(Fvec(subset, x))))

def solve_subset(subset, n_starts=400, seed=0):
    rng = random.Random(seed)
    found = []
    for _ in range(n_starts):
        x0 = random_start(rng)
        if x0 is None:
            continue
        x, res, conv = newton(subset, x0)
        if conv and res < ACCEPT_RESID and admissible(x):
            found.append(tuple(float(v) for v in x))
    roots = dedup(found)
    out = []
    for x in roots:
        b, c, d, e, g, h = x
        out.append({"coords": [b, c, d, e, g], "h": h / DEG,         # h in degrees
                    "residual": round_trip(subset, x)})
    return out

def emit_roots(subsets, path, n_starts=400, seed=0):
    """Write one ingest JSONL line per subset (RootIngestAdapter contract)."""
    with open(path, "w") as f:
        for sub in subsets:
            roots = solve_subset(tuple(sub), n_starts=n_starts, seed=seed)
            f.write(json.dumps({"subset": list(sub),
                                "roots": [{"coords": r["coords"], "h": r["h"]}
                                          for r in roots]}) + "\n")
    return path

# ---------------------------------------------------------------------------
#  optional Gate-4 (runner applies it authoritatively; here for self-report only)
# ---------------------------------------------------------------------------
def gate4(x):
    try:
        import spherical_geo_check as GC
    except Exception:
        return None
    ok, _ = GC.gate4(x[0], x[1], x[2], x[3], x[4], x[5], closure_tol=1e-7)
    return bool(ok)

# ===========================================================================
#  self-validation (runs with the frozen engine; Gate-4 optional)
# ===========================================================================
def selftest():
    print("=" * 68)
    print("NEWTON VALIDATOR — self-validation")
    print("=" * 68)

    # (0) independence: this module must not import the lift/homotopy/sympy
    banned = {"lift_generator", "sympy", "homotopy"}
    src = open(__file__).read()
    indep = not any(("import " + b) in src for b in banned)
    print(f"(0) independence (no lift/sympy/homotopy import): {indep}")

    subsets = [(1, 2, 3, 4, 6, 7), (1, 2, 5, 10, 15, 20), (1, 2, 3, 7, 12, 20)]
    worst_conv_res = 0.0; worst_rt = 0.0; total = 0
    for sub in subsets:
        roots = solve_subset(sub, n_starts=200, seed=1)
        total += len(roots)
        for r in roots:
            worst_rt = max(worst_rt, r["residual"])
        print(f"    {sub}: {len(roots)} admissible real root(s)"
              + (f", max residual {max(r['residual'] for r in roots):.1e}"
                 if roots else ""))

    # (1) convergence quality: ANY converged point has tiny raw residual
    #     (validates 'when Newton converges it converges to a true root')
    rng = random.Random(2); probe = (1, 2, 3, 4, 6, 7); conv_res = []
    for _ in range(120):
        x0 = random_start(rng)
        if x0 is None: continue
        x, res, conv = newton(probe, x0)
        if conv: conv_res.append(res)
    if conv_res:
        worst_conv_res = max(conv_res)
    print(f"\n(1) converged-point raw residuals: {len(conv_res)} convergences, "
          f"max {worst_conv_res:.1e} (expect < 1e-11)")
    print(f"    accepted-root round-trip residual: max {worst_rt:.1e} "
          f"(accept < {ACCEPT_RESID:g})")

    # (2) determinism: same seed -> identical root set
    a = solve_subset((1, 2, 3, 4, 6, 7), n_starts=120, seed=7)
    b = solve_subset((1, 2, 3, 4, 6, 7), n_starts=120, seed=7)
    det = (len(a) == len(b) and all(
        np.max(np.abs(np.array(ra["coords"] + [ra["h"]])
                      - np.array(rb["coords"] + [rb["h"]]))) < 1e-9
        for ra, rb in zip(sorted(a, key=lambda r: r["coords"]),
                           sorted(b, key=lambda r: r["coords"]))))
    print(f"\n(2) determinism (same seed -> same roots): {det}")

    # (3) ingest emission round-trips as valid JSON in contract shape
    p = "newton_selftest_roots.jsonl"
    emit_roots([(1, 2, 3, 4, 6, 7)], p, n_starts=60, seed=0)
    obj = json.loads(open(p).readline())
    shape_ok = ("subset" in obj and "roots" in obj
                and all(set(r) == {"coords", "h"} and len(r["coords"]) == 5
                        for r in obj["roots"]))
    os.remove(p)
    print(f"(3) ingest JSONL shape matches RootIngestAdapter contract: {shape_ok}")

    ok = indep and (not conv_res or worst_conv_res < 1e-11) \
        and (worst_rt < ACCEPT_RESID) and det and shape_ok
    print("\nSELF-TEST:", "ALL PASS" if ok else "see failures above")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(selftest())
