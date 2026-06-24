#!/usr/bin/env python3
"""regularity_audit.py — cross-subset test of the lift regularity hypothesis.

Hypothesis (to falsify, not confirm):
  * lift-generator-v1 (cos(D)-1 encoding) makes genuine solutions SINGULAR;
    corank(v1) = 6 - |subset ∩ {3,4,6}|  (only F3,F4,F6 are the curved cosine
    form; every other constraint is the flat cos(D)-1 form).
  * the sin(D) reformulation (v2 candidate) restores regularity: corank(v2)=0.

Tested at GENUINE Newton roots (base coords), across a sample chosen to cover
|∩{3,4,6}| = 0,1,2,3, the doubled family F13/F14/F15, and multiple roots where
present. Measures corank and condition number before and after, per root.

This is a DIAGNOSTIC: it builds the v2 constraint forms in-memory to measure
regularity. It does not create or freeze lift-generator-v2.
"""
import sys, os, math, numpy as np
_here = os.path.dirname(os.path.abspath(__file__))
_root = os.path.dirname(_here)
sys.path.insert(0, _root)
sys.path.insert(0, _here)
import sympy as sp, lift_generator as LG, monodromy_prototype as MP
import newton_validator as NV

DEG = math.pi / 180.0
CURVED = {3, 4, 6}                       # the cosine-form (regular) constraints


def predicted_corank(subset):
    return 6 - len(set(subset) & CURVED)


def v1_equations(gen):
    return gen["equations"]


def v2_equations(gen):
    """structural unchanged; flat cos(D)-1 constraints -> sin(D); cosine kept."""
    ncons = len(gen["subset"])
    structural = gen["equations"][:-ncons]
    newcons = []
    for i in gen["subset"]:
        if i in CURVED:
            newcons.append(gen["constraints"][i])
        else:
            newcons.append(LG.arc(LG.CONS_ANGLE[i])[1])    # sin(combo)
    return structural + newcons


def corank_cond(eqs, variables, seedvec, tol=1e-8):
    f = sp.lambdify(variables, eqs, modules=["numpy"])
    x0 = np.array(seedvec, dtype=complex); n = len(x0)
    h = 1e-200; J = np.zeros((n, n))
    for j in range(n):
        xp = x0.copy(); xp[j] += 1j * h
        J[:, j] = np.array(f(*xp), dtype=complex).imag / h
    s = np.linalg.svd(J, compute_uv=False)
    res = max(abs(np.array(f(*x0.real), dtype=float)))
    return int((s < tol).sum()), s.max() / s.min(), res


def audit_subset(subset, n_starts=300, seed=0):
    subset = tuple(sorted(subset))
    try:
        roots = NV.solve_subset(subset, n_starts=n_starts, seed=seed)
    except Exception as ex:
        return {"subset": subset, "error": str(ex), "roots": []}
    gen = LG.generate(subset)
    v1, v2 = v1_equations(gen), v2_equations(gen)
    out = {"subset": subset, "pred": predicted_corank(subset), "roots": []}
    for r in roots:
        base = (*r["coords"], r["h"])
        _, _, vec = MP_lift(gen, base)
        c1, k1, _ = corank_cond(v1, gen["variables"], vec)
        c2, k2, _ = corank_cond(v2, gen["variables"], vec)
        out["roots"].append({"corank_v1": c1, "cond_v1": k1,
                             "corank_v2": c2, "cond_v2": k2})
    return out


def MP_lift(gen, base):
    b, c, d, e, g, h_deg = base
    r = math.pi / 2 - h_deg * DEG
    sub, _ = LG.engine_aux(b, c, d, e, g, r)
    vec = [float(sub[v]) for v in gen["variables"]]
    return gen, sub, vec


SAMPLE = [
    (1, 2, 3, 4, 6, 7),     # |∩{3,4,6}|=3  -> pred 3   (known root)
    (1, 2, 3, 4, 5, 6),     # =3 -> pred 3
    (1, 2, 3, 4, 6, 20),    # =3 -> pred 3
    (1, 2, 4, 6, 7, 8),     # {4,6}=2 -> pred 4
    (1, 2, 3, 6, 7, 10),    # {3,6}=2 -> pred 4
    (1, 2, 3, 7, 10, 20),   # {3}=1 -> pred 5
    (1, 2, 4, 7, 11, 12),   # {4}=1 -> pred 5
    (1, 2, 5, 7, 10, 15),   # {}=0 -> pred 6
    (1, 2, 7, 10, 11, 12),  # {}=0 -> pred 6
    (1, 2, 13, 14, 15, 20), # doubled, {}=0 -> pred 6
    (1, 2, 4, 13, 14, 15),  # doubled + {4}=1 -> pred 5
    (1, 2, 6, 13, 15, 20),  # doubled + {6}=1 -> pred 5
    (1, 2, 3, 4, 13, 14),   # {3,4}=2 + doubled -> pred 4
    (1, 2, 5, 10, 15, 20),  # {}=0 -> pred 6   (size-5-ish root known)
]


if __name__ == "__main__":
    n_starts = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    print(f"CROSS-SUBSET REGULARITY AUDIT  (Newton n_starts={n_starts})")
    print(f"hypothesis: corank_v1 = 6-|∩{{3,4,6}}|,  corank_v2 = 0\n")
    hdr = (f"{'subset':22s} {'pred':>4s} {'#roots':>6s} "
           f"{'corank_v1':>9s} {'cond_v1':>9s} {'corank_v2':>9s} {'cond_v2':>9s}")
    print(hdr); print("-" * len(hdr))
    all_ok = True; tested = 0; solvable = 0
    for sub in SAMPLE:
        res = audit_subset(sub, n_starts=n_starts)
        if res.get("error"):
            print(f"{str(sub):22s}  ERROR {res['error'][:40]}"); continue
        if not res["roots"]:
            print(f"{str(sub):22s} {res['pred']:>4d} {'0':>6s}   (no real root — skipped)")
            continue
        solvable += 1
        for k, rr in enumerate(res["roots"]):
            tested += 1
            ok = (rr["corank_v1"] == res["pred"]) and (rr["corank_v2"] == 0)
            all_ok = all_ok and ok
            tag = str(sub) if k == 0 else ""
            flag = "" if ok else "  <-- MISMATCH"
            print(f"{tag:22s} {res['pred']:>4d} {('#'+str(k+1)):>6s} "
                  f"{rr['corank_v1']:>9d} {rr['cond_v1']:>9.1e} "
                  f"{rr['corank_v2']:>9d} {rr['cond_v2']:>9.1e}{flag}")
    print("-" * len(hdr))
    print(f"solvable subsets: {solvable}/{len(SAMPLE)}   roots tested: {tested}")
    print(f"\nVERDICT: {'hypothesis HOLDS across all tested roots' if all_ok else 'MISMATCH — hypothesis incomplete'}")
    print("  (corank_v1 matches 6-|∩{3,4,6}| in every case; corank_v2 == 0 in every case)"
          if all_ok else "  see MISMATCH rows above")
