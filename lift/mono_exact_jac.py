#!/usr/bin/env python3
"""mono_exact_jac.py — exact-Jacobian recheck of the conditioning tail.

The structural diagnostic measured the singular spectrum with a central
finite-difference Jacobian. At cond ~ 1e7-1e8 (the flagged tail) finite
differences can mislead. This companion recomputes the spectrum with the EXACT
symbolic Jacobian of the v2 system, evaluated at the raw complex solution vectors
already in the dump — no new monodromy run required.

It compares EXACT vs FINITE-DIFFERENCE at BOTH:
  * flagged (worst-conditioned) indices, and
  * healthy control indices,
so a systematically pessimistic finite-difference method is distinguishable from
a genuine pathological tail (the comparison the controls make possible).

PURPOSE: verify whether the conditioning tail is a real structural feature or a
finite-difference artifact. Measurement only; no hypothesis is concluded here.

Usage:
  python3 mono_exact_jac.py <dump> "(subset)" --flagged 5,9,10,12 --healthy 0,4,18   # array positions (the i column from mono_structure_diag)
"""
import sys, os, argparse, numpy as np
_here = os.path.dirname(os.path.abspath(__file__))
_root = os.path.dirname(_here)
sys.path.insert(0, _here)
sys.path.insert(0, _root)
import sympy as sp
import lift_generator_v2 as V2


def read_dump(path):
    idx, vecs = [], []
    for line in open(path):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        k, rest = line.split(";", 1)
        comps = [complex(float(a), float(b))
                 for a, b in (tok.split("|") for tok in rest.split(","))]
        idx.append(int(k)); vecs.append(np.array(comps, dtype=complex))
    return idx, vecs


def build_exact_jac(subset):
    """Symbolic 54x54 Jacobian of the v2 system, lambdified once."""
    gen = V2.generate(subset)
    V = gen["variables"]; E = gen["equations"]
    J = sp.Matrix(E).jacobian(sp.Matrix(V))
    Jf = sp.lambdify(V, J, modules=["numpy"])
    Ff = sp.lambdify(V, E, modules=["numpy"])
    return gen, Jf, Ff


def fd_jac(Ff, vec, h=1e-6):
    n = len(vec); J = np.zeros((n, n), dtype=complex)
    for j in range(n):
        xp = vec.copy(); xm = vec.copy(); xp[j] += h; xm[j] -= h
        J[:, j] = (np.array(Ff(*xp), dtype=complex)
                   - np.array(Ff(*xm), dtype=complex)) / (2 * h)
    return J


def spectrum(J):
    s = np.linalg.svd(np.asarray(J, dtype=complex), compute_uv=False)
    return s.min(), s.max() / s.min(), s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dump")
    ap.add_argument("subset")
    ap.add_argument("--flagged", default="5,9,10,12")
    ap.add_argument("--healthy", default="0,4,18")
    a = ap.parse_args()
    subset = tuple(eval(a.subset))
    flagged = [int(x) for x in a.flagged.split(",") if x != ""]
    healthy = [int(x) for x in a.healthy.split(",") if x != ""]

    print("=" * 74)
    print(" EXACT-JACOBIAN RECHECK of the conditioning tail (v2 lift)")
    print(" Compares exact symbolic vs finite-difference at flagged + healthy idx.")
    print(" Measurement only; no hypothesis concluded.")
    print("=" * 74)

    idx, vecs = read_dump(a.dump)
    print(f"\nsubset {subset}   dump size {len(vecs)}")
    print("building exact symbolic Jacobian (once)…", flush=True)
    gen, Jf, Ff = build_exact_jac(subset)

    rows = [("flagged", i) for i in flagged] + [("healthy", i) for i in healthy]
    print(f"\n{'kind':>8s} {'pos':>4s} | {'exact sigma_min':>15s} {'exact cond':>12s} "
          f"| {'fd sigma_min':>13s} {'fd cond':>12s}  {'agree?':>7s}")
    print("-" * 80)
    real_tail = []
    for kind, i in rows:
        if not (0 <= i < len(vecs)):                  # flags are ARRAY POSITIONS
            print(f"{kind:>8s} {i:>4d} | (position out of range 0..{len(vecs)-1})")
            continue
        v = vecs[i]                                   # index vecs directly by position
        ex_sm, ex_cond, _ = spectrum(np.array(Jf(*v)))
        fd_sm, fd_cond, _ = spectrum(fd_jac(Ff, v))
        # do exact and fd agree within an order of magnitude on cond?
        agree = (0.1 <= (ex_cond / fd_cond) <= 10)
        if kind == "flagged":
            real_tail.append(ex_cond > 1e5)
        print(f"{kind:>8s} {i:>4d} | {ex_sm:>15.2e} {ex_cond:>12.2e} "
              f"| {fd_sm:>13.2e} {fd_cond:>12.2e}  {'yes' if agree else 'NO':>7s}")
    print("-" * 80)
    print("\nReadout (descriptive):")
    print("  * If exact cond ~ fd cond at the flagged points (both 1e6-1e8): tail is REAL.")
    print("  * If exact cond collapses to 1e3-1e4 at flagged points: tail was an FD artifact.")
    print("  * Healthy controls calibrate whether FD is systematically off everywhere.")
    if real_tail:
        n_real = sum(real_tail)
        print(f"\n  flagged points with exact cond > 1e5: {n_real}/{len(real_tail)}")
    print("\n[end of recheck — interpretation deferred]")
    return 0


if __name__ == "__main__":
    sys.exit(main())