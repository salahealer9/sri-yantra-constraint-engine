#!/usr/bin/env python3
"""seed_lifter.py — lift a base spherical root (b,c,d,e,g,h) to the full
canonical lift coordinate vector (lift-generator-v1) and report the residual
of every polynomial equation, grouped by block.

Purpose (per the agreed sequencing): BEFORE any monodromy work, verify the one
object everything downstream depends on — that the lifted Newton root actually
satisfies the frozen polynomial system. The lift is performed by the FROZEN
generator's own engine_aux map (not re-derived here); this script only
evaluates and classifies. No Julia, no Gate-4 needed.

Two questions are separated on purpose:
  * STRUCTURAL blocks (atomic Pythagorean, angle defining eqs, angle
    Pythagorean, ratio defining eqs) must vanish to ~machine precision at ANY
    valid base point. They test whether the LIFT is correct.
  * CONSTRAINT blocks vanish only at a true root; their residual can be no
    better than the base solver's convergence tolerance. They test the ROOT.
"""
import sys, math, os
_here = os.path.dirname(os.path.abspath(__file__))
_root = os.path.dirname(_here)
sys.path.insert(0, _root)
sys.path.insert(0, _here)
import sympy as sp
import lift_generator as LG

DEG = math.pi / 180.0


def lift(subset, b, c, d, e, g, h_deg):
    """Return (gen, full vector in canonical order, chain dict)."""
    r = math.pi / 2 - h_deg * DEG
    sub, chain = LG.engine_aux(b, c, d, e, g, r)        # FROZEN lift map
    gen = LG.generate(subset)                            # FROZEN system
    vec = [float(sub[v]) for v in gen["variables"]]
    return gen, sub, vec, chain


def block_labels(gen):
    labs = [("atomic_pyth", n) for n in LG.ATOMIC_NAMES]
    for n in gen["angles"]:
        labs += [("angle_def", n), ("angle_pyth", n)]
    labs += [("ratio_def", n) for n in gen["ratios"]]
    labs += [("constraint", f"F{i}") for i in gen["subset"]]
    return labs


def residuals(gen, vec):
    f = sp.lambdify(gen["variables"], gen["equations"], modules=["math"])
    return [abs(float(v)) for v in f(*vec)]


def recover_base(vec):
    a = math.atan2
    b = a(vec[1], vec[0]); c = a(vec[3], vec[2]); d = a(vec[5], vec[4])
    e = a(vec[7], vec[6]); g = a(vec[9], vec[8]); r = a(vec[11], vec[10])
    return b, c, d, e, g, (math.pi / 2 - r) / DEG


def report(subset, base, label=""):
    b, c, d, e, g, h = base
    gen, sub, vec, chain = lift(subset, b, c, d, e, g, h)
    res = residuals(gen, vec)
    labs = block_labels(gen)
    assert len(res) == len(labs) == len(gen["variables"])

    print(f"\n=== seed-lift residual report  subset={subset}  {label} ===")
    print(f"  base (b,c,d,e,g,h_deg) = "
          f"({b:.12f}, {c:.12f}, {d:.12f}, {e:.12f}, {g:.12f}, {h:.10f})")
    print(f"  lift dimension = {len(vec)}  (system_hash={LG.system_hash(gen)[:16]}...)")

    blocks = {}
    for (kind, nm), r in zip(labs, res):
        blocks.setdefault(kind, []).append((r, nm))
    order = ["atomic_pyth", "angle_def", "angle_pyth", "ratio_def", "constraint"]
    struct_max = 0.0
    print("  block                 count   max|F_i|        (worst eq)")
    for k in order:
        if k not in blocks:
            continue
        mx, nm = max(blocks[k])
        if k != "constraint":
            struct_max = max(struct_max, mx)
        print(f"    {k:18s}  {len(blocks[k]):4d}   {mx:.3e}     {nm}")
    cons_max = max((r for (kind, _), r in zip(labs, res) if kind == "constraint"),
                   default=0.0)
    overall = max(res)

    rb = recover_base(vec)
    rt = max(abs(rb[i] - base[i]) for i in range(6))

    print(f"  --------------------------------------------------------")
    print(f"  STRUCTURAL max  (lift correctness) : {struct_max:.3e}")
    print(f"  CONSTRAINT max  (root quality)     : {cons_max:.3e}")
    print(f"  OVERALL max |F_i|                  : {overall:.3e}")
    print(f"  round-trip atan2 recovery error    : {rt:.3e}")
    struct_ok = struct_max < 1e-11
    print(f"  VERDICT: lift {'CORRECT' if struct_ok else 'SUSPECT'} "
          f"(structural < 1e-11: {struct_ok})")
    return struct_max, cons_max, overall, rt


if __name__ == "__main__":
    # Newton's real root for {1,2,3,4,6,7} from the server smoke test
    SUB = (1, 2, 3, 4, 6, 7)
    NEWTON = (0.6246238466927992, 0.7044304165359816, 0.7482768099360514,
              0.6307397242292889, 0.3136386632298885, 22.64768569612002)
    report(SUB, NEWTON, "Newton root (server smoke test)")
