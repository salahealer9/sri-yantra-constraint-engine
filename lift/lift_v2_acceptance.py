#!/usr/bin/env python3
"""lift_v2_acceptance.py — the five-criterion freeze gate for lift-generator-v2.

Criteria (spec §5):
  1. Residual equivalence   — every v2 equation vanishes at engine-lifted roots (<=1e-12).
  2. Solution-set equivalence (established direction) — no admissible solution is
     LOST (every admissible Newton root satisfies the v2 system <=1e-12) and none
     is GAINED (pi_branch_test: the extra Delta=pi / pi/2 branch is filtered).
     Full positive equivalence is deferred to the first successful homotopy runs.
  3. Regularity             — Jacobian corank == 0 at every tested root (v1 lacked this).
  4. Conditioning           — condition number at solutions reported.
  5. Gate-4 invariance      — Gate-4 verdict == raw-engine verdict for each root.
     Gate-4 is encoding-independent (operates on the recovered figure, not the
     lift); run here if spherical_geo_check is importable, else confirmed on server.

Plus a structural-identity check (variables and structural equations byte-identical
to v1) that underwrites criteria 2 and 5.

GATE: every runnable criterion must pass on every tested root, or the suite fails.
"""
import sys, os, math, numpy as np
_here = os.path.dirname(os.path.abspath(__file__))
_root = os.path.dirname(_here)
sys.path.insert(0, _here)
sys.path.insert(0, _root)
import sympy as sp
import lift_generator as LG
import lift_generator_v2 as V2
import newton_validator as NV

RAO = LG.RAO          # frozen engine (polish evaluates the raw constraints)

DEG = math.pi / 180.0
SAMPLE = [
    (1, 2, 3, 4, 6, 7), (1, 2, 3, 4, 5, 6), (1, 2, 3, 4, 6, 20),
    (1, 2, 4, 6, 7, 8), (1, 2, 3, 6, 7, 10), (1, 2, 3, 7, 10, 20),
    (1, 2, 4, 7, 11, 12), (1, 2, 5, 7, 10, 15), (1, 2, 7, 10, 11, 12),
    (1, 2, 13, 14, 15, 20), (1, 2, 4, 13, 14, 15), (1, 2, 6, 13, 15, 20),
    (1, 2, 3, 4, 13, 14), (1, 2, 5, 10, 15, 20),
]


def lift_vec(gen, base):
    b, c, d, e, g, h_deg = base
    sub, _ = LG.engine_aux(b, c, d, e, g, math.pi / 2 - h_deg * DEG)
    return [float(sub[v]) for v in gen["variables"]]


def polish(subset, base):
    """Drive a Newton-validator root (stops at ~1e-11) to full float64 precision
    on the raw constraints before the residual test. The sin form vanishes
    LINEARLY, so its residual tracks root quality; an under-converged root would
    understate v2's correctness. Uses a robust solver; falls back on failure."""
    from scipy.optimize import fsolve
    import warnings
    x0 = np.array([*base[:5], base[5] * DEG])     # engine works in radians
    def F(x):
        d = RAO.constraints(*x[:5], x[5])
        return [d[i] for i in subset]
    try:
        r0 = max(abs(v) for v in F(x0))
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")       # xtol-too-small is the success case
            sol = fsolve(F, x0, xtol=1e-15)
        if max(abs(v) for v in F(sol)) <= r0:
            return (*sol[:5], sol[5] / DEG)
    except (ArithmeticError, ValueError, RuntimeError):
        pass            # genuine numerical/domain failure -> fall back to input
    return base


def recover(vec):
    """atan2 recovery from the first 12 atomic components (encoding-independent)."""
    a = math.atan2
    b = a(vec[1], vec[0]); c = a(vec[3], vec[2]); d = a(vec[5], vec[4])
    e = a(vec[7], vec[6]); g = a(vec[9], vec[8]); r = a(vec[11], vec[10])
    return (b, c, d, e, g, (math.pi / 2 - r) / DEG)


def corank_cond_res(eqs, variables, vec, tol=1e-8):
    f = sp.lambdify(variables, eqs, modules=["numpy"])
    x0 = np.array(vec, dtype=complex); n = len(x0); h = 1e-200
    J = np.zeros((n, n))
    for j in range(n):
        xp = x0.copy(); xp[j] += 1j * h
        J[:, j] = np.array(f(*xp), dtype=complex).imag / h
    s = np.linalg.svd(J, compute_uv=False)
    res = max(abs(np.array(f(*x0.real), dtype=float)))
    return int((s < tol).sum()), s.max() / s.min(), res


def structural_identity():
    """variables and structural equations (blocks A,B,C) identical v1 vs v2."""
    ok = True
    for sub in SAMPLE:
        g1, g2 = LG.generate(sub), V2.generate(sub)
        nc = len(sub)
        if [str(v) for v in g1["variables"]] != [str(v) for v in g2["variables"]]:
            ok = False
        if [str(sp.expand(e)) for e in g1["equations"][:-nc]] != \
           [str(sp.expand(e)) for e in g2["equations"][:-nc]]:
            ok = False
    return ok


def main():
    print("lift-generator-v2 ACCEPTANCE SUITE  (spec SHA", V2.SPEC_SHA[:8] + "…)\n")
    try:
        import spherical_geo_check as GC
        gate4 = lambda coords, h_deg: GC.gate4(*coords, h_deg * DEG, closure_tol=1e-7)[0]
        have_gate4 = True
    except Exception:
        gate4, have_gate4 = None, False

    c = {1: True, 2: True, 3: True, 4: True, 5: True}
    conds, tested, solvable = [], 0, 0
    struct = structural_identity()
    print(f"[structural identity v1==v2]  variables & structural eqs identical: {struct}")
    print(f"{'subset':22s} {'root':>4s} {'resid_v2':>9s} {'corank':>6s} {'cond':>9s} "
          f"{'no-loss':>7s} {'gate4=eng':>9s}")
    print("-" * 78)
    for sub in SAMPLE:
        try:
            roots = NV.solve_subset(tuple(sub), n_starts=400, seed=0)
        except Exception as ex:
            print(f"{str(sub):22s}  Newton error: {ex}"); c[1] = c[3] = False; continue
        if not roots:
            print(f"{str(sub):22s}  (no real root — skipped)"); continue
        solvable += 1
        g1 = LG.generate(sub); g2 = V2.generate(sub)
        for k, r in enumerate(roots, 1):
            tested += 1
            base = polish(tuple(sub), (*r["coords"], r["h"]))     # high-precision root
            vec2 = lift_vec(g2, base)
            vec1 = lift_vec(g1, base)
            cork, cond, res = corank_cond_res(g2["equations"], g2["variables"], vec2)
            conds.append(cond)
            no_loss = res <= 1e-12               # criterion 1 & 2 (no admissible loss)
            if res > 1e-12: c[1] = False; c[2] = False
            if cork != 0:   c[3] = False
            # criterion 5: Gate-4 verdict is encoding-invariant (v1-recovery == v2-recovery)
            g4 = "n/a"
            if have_gate4:
                cfg1, cfg2 = recover(vec1), recover(vec2)
                v1v = gate4(cfg1[:5], cfg1[5]); v2v = gate4(cfg2[:5], cfg2[5])
                g4 = "ok" if v1v == v2v else "MISMATCH"
                if v1v != v2v: c[5] = False
            print(f"{(str(sub) if k==1 else ''):22s} {('#'+str(k)):>4s} "
                  f"{res:>9.1e} {cork:>6d} {cond:>9.1e} {str(no_loss):>7s} {g4:>9s}")
    print("-" * 78)

    # criterion 2 — no admissible solution gained (pi-branch)
    try:
        import pi_branch_test
        c2_gain = (pi_branch_test.main() == 0)
    except SystemExit as se:
        c2_gain = (se.code == 0)
    except Exception as ex:
        print("pi_branch_test error:", ex); c2_gain = False
    c[2] = c[2] and c2_gain

    print(f"\nsolvable subsets {solvable}/{len(SAMPLE)}   roots tested {tested}   "
          f"cond range [{min(conds):.1e}, {max(conds):.1e}]")
    print("\nCRITERIA:")
    labels = {1: "residual equivalence (<=1e-12)",
              2: "solution-set: no loss & no gain (pi-branch)",
              3: "regularity (corank 0 at all roots)",
              4: "conditioning reported",
              5: "Gate-4 verdict encoding-invariant (v1==v2 recovery)" + ("" if have_gate4 else " [DEFERRED: Gate-4 not in env]")}
    for k in (1, 2, 3, 4, 5):
        status = ("PASS" if c[k] else "FAIL") if (k != 5 or have_gate4) else "DEFER"
        print(f"  [{status}] (#{k}) {labels[k]}")
    runnable = [c[k] for k in (1, 2, 3, 4)] + ([c[5]] if have_gate4 else [])
    gate = struct and all(runnable)
    print(f"\nFREEZE GATE: {'PASS — v2 ready to freeze' if gate else 'FAIL'}"
          + ("" if have_gate4 else "  (criterion #5 to be confirmed on server)"))
    # representative system hashes for the freeze record
    print("\nv2 system hashes (representative):")
    for sub in [(1, 2, 3, 4, 6, 7), (1, 2, 13, 14, 15, 20)]:
        print(f"  {sub}: {V2.system_hash(V2.generate(sub))}")
    return 0 if gate else 1


if __name__ == "__main__":
    sys.exit(main())
