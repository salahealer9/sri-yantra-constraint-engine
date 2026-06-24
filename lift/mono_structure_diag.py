#!/usr/bin/env python3
"""mono_structure_diag.py — structural characterization of a capped sample of
generic solutions of the v2 lift.

PURPOSE
  Structural characterization of a CAPPED diagnostic sample of generic solutions.
  NOT intended to estimate total fiber size, total number of base configurations,
  or asymptotic monodromy behaviour. It MEASURES; it does not conclude A/B/C/D/E.

MEASUREMENTS
  * distinct raw 54-vectors        (cluster at tol)            -> duplication (C)
  * distinct base blocks           (first 12 atomic comps)     -> lift-vs-geometry (D)
      if distinct_vectors >> distinct_base, many aux realizations share a base.
  * singular spectrum of the v2 Jacobian at sampled solutions  -> isolation (A)
      sigma_min, condition number, smallest singular values (NOT a thresholded
      rank: the spectrum is the evidence; rank=54 with sigma_min~1e-14 is a
      near-singular structure, reported as such).
  * discovery-order trace per base cluster (result ordering proxy).

INPUT: dump from mono_diagnostic.py  (lines "idx;re|im,re|im,...") and "<dump>.pgen".
"""
import sys, os, math, numpy as np
_here = os.path.dirname(os.path.abspath(__file__))
_root = os.path.dirname(_here)
sys.path.insert(0, _here)
sys.path.insert(0, _root)
import monodromy_prototype_v2 as MP
import sympy as sp
import lift_generator_v2 as V2

HEADER = """\
============================================================================
 STRUCTURAL DIAGNOSTIC — capped sample of generic solutions (v2 lift)
 Purpose: characterize the OBJECTS in a capped sample.
 NOT a fiber-size estimate, NOT a base-config count, NOT asymptotic behaviour.
 Measurements only; no A/B/C/D/E conclusion is drawn here.
============================================================================"""


def read_dump(path):
    idx, vecs = [], []
    for line in open(path):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        k, rest = line.split(";", 1)
        comps = []
        for tok in rest.split(","):
            re_, im_ = tok.split("|")
            comps.append(complex(float(re_), float(im_)))
        idx.append(int(k)); vecs.append(np.array(comps, dtype=complex))
    return idx, vecs


def cluster(vectors, tol=1e-8):
    """Greedy clustering by max-abs component distance. Returns label per item."""
    reps, labels = [], []
    for v in vectors:
        found = -1
        for j, r in enumerate(reps):
            if np.max(np.abs(v - r)) <= tol:
                found = j; break
        if found < 0:
            reps.append(v); found = len(reps) - 1
        labels.append(found)
    return labels, len(reps)


def recover_base(vec):
    """complex base (b,c,d,e,g,r) from the first 12 atomic comps via e^{i a}."""
    out = []
    for j in range(6):
        cphi, sphi = vec[2 * j], vec[2 * j + 1]
        out.append(-1j * np.log(cphi + 1j * sphi))
    return np.array(out)


def jac_spectrum(eqs_f, vec, h=1e-6):
    """Central-FD Jacobian of the v2 system at a (complex) point; SVD spectrum."""
    n = len(vec); J = np.zeros((n, n), dtype=complex)
    for j in range(n):
        xp = vec.copy(); xm = vec.copy(); xp[j] += h; xm[j] -= h
        J[:, j] = (np.array(eqs_f(*xp), dtype=complex)
                   - np.array(eqs_f(*xm), dtype=complex)) / (2 * h)
    s = np.linalg.svd(J, compute_uv=False)
    return s


def main(dump_path, subset, sample=20, tol=1e-8):
    print(HEADER)
    idx, vecs = read_dump(dump_path)
    n = len(vecs)
    print(f"\nsubset {subset}   sample size: {n} generic solutions   tol={tol:g}")
    if n == 0:
        print("empty dump."); return 1

    # --- clustering: raw vectors vs base blocks ---
    _, n_vec = cluster(vecs, tol)
    base_blocks = [v[:12] for v in vecs]
    base_labels, n_base = cluster(base_blocks, tol)
    print("\n[clustering]")
    print(f"  distinct raw 54-vectors : {n_vec} / {n}")
    print(f"  distinct base blocks    : {n_base} / {n}   (first 12 atomic comps)")
    ratio = n_vec / max(n_base, 1)
    print(f"  vectors-per-base ratio  : {ratio:.2f}")
    # regime flags keyed on the ratio (descriptive, not conclusive)
    if ratio >= 5:
        print("  regime: many distinct vectors per base block "
              "(sample consistent with many aux realizations per base)")
    elif ratio <= 1.5:
        print("  regime: distinct vectors ~ distinct base blocks "
              "(each geometry ~one vector in-sample; many-realizations-per-base not indicated)")
    else:
        print("  regime: intermediate (some aux multiplicity per base)")
    if n_vec < n:
        print(f"  duplication: {n - n_vec}/{n} vectors collapsed at tol "
              f"({100*(n-n_vec)/n:.0f}% repeated)")
    print("  NOTE: distinct-base count is a SAMPLE LOWER BOUND, not a population count.")

    # --- singular spectrum at a sample of solutions ---
    gen = V2.generate(subset)
    eqs_f = sp.lambdify(gen["variables"], gen["equations"], modules=["numpy"])
    print(f"\n[singular spectrum of the v2 Jacobian at up to {sample} sampled solutions]")
    print(f"  {'i':>3s} {'sigma_min':>11s} {'cond':>11s} {'smallest 3 sigma':>34s}")
    near_sing = 0
    for i in range(min(sample, n)):
        s = jac_spectrum(eqs_f, vecs[i])
        sm, cond = s.min(), s.max() / s.min()
        if sm < 1e-10:
            near_sing += 1
        sm3 = ", ".join(f"{x:.2e}" for x in sorted(s)[:3])
        print(f"  {i:>3d} {sm:>11.2e} {cond:>11.2e}   [{sm3}]")
    print(f"  sampled: {min(sample,n)}   with sigma_min < 1e-10: {near_sing}")
    print("  (sigma_min bounded away from 0 -> locally isolated; "
          "sigma_min ~ 1e-14 -> near-singular, reported not thresholded)")

    # --- discovery-order trace per base cluster ---
    print("\n[discovery-order trace]  (result-ordering index; proxy, not certified)")
    by_base = {}
    for k, lab in zip(idx, base_labels):
        by_base.setdefault(lab, []).append(k)
    shown = sorted(by_base.items(), key=lambda kv: len(kv[1]), reverse=True)[:8]
    for lab, ks in shown:
        ks = sorted(ks)
        span = f"first={ks[0]} last={ks[-1]} count={len(ks)}"
        print(f"  base cluster {lab:>3d}: {span}")
    print("  (early-only indices -> rediscovery of a fixed set; "
          "indices spread to the end -> new base blocks still appearing in-sample)")

    print("\n[end of measurements — interpretation deferred]")
    return 0


if __name__ == "__main__":
    dump = sys.argv[1] if len(sys.argv) > 1 else "mono_diag_out.jsonl"
    sub = eval(sys.argv[2]) if len(sys.argv) > 2 else (1, 2, 3, 4, 6, 7)
    sys.exit(main(dump, tuple(sub)))
