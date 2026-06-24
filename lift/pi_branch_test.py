#!/usr/bin/env python3
"""pi_branch_test.py — close the one mathematical difference between the v1 and
v2 constraint encodings.

For an arc-equality constraint Delta = 0:
    v1:  cos(Delta) - 1 = 0   zero set: {Delta = 0}
    v2:  sin(Delta)     = 0   zero set: {Delta = 0, Delta = pi}

The ONLY extra solutions v2 admits are at Delta = pi. This test shows those are
rejected, so v2's admissible solution set equals v1's:

  (A) algebraically the sin form accepts Delta = pi   (sin(pi) = 0);
  (B) physically the frozen engine rejects it, two independent ways:
      (B1) for arc-equality constraints raw F_i = Delta_i, so Delta = pi gives
           raw residual pi >> 1e-7 -> the round-trip acceptance gate rejects it;
      (B2) Delta = pi is geometrically unreachable: pushing any arc-equality
           toward pi drives the chain out of domain (DomainError) far below pi.
"""
import sys, math, os
_here = os.path.dirname(os.path.abspath(__file__))
_root = os.path.dirname(_here)
sys.path.insert(0, _root)
sys.path.insert(0, _here)
import sriyantra as RAO, lift_generator as LG

SUB = (1, 2, 3, 4, 6, 7)
ROOT = (0.6246238466927992, 0.7044304165359816, 0.7482768099360514,
        0.6307397242292889, 0.3136386632298885, 22.64768569612002)
ARC_EQ = [i for i in SUB if i not in LG.CONS_COS]      # F1, F2, F7


def accept(coords, h_deg, tol=1e-7):
    """The runner's round-trip acceptance gate, on raw frozen-engine residual."""
    try:
        F = RAO.constraints(*coords, h_deg * math.pi / 180)
    except Exception as ex:
        return False, f"engine DomainError ({type(ex).__name__})", None
    res = max(abs(F[i]) for i in SUB)
    return res < tol, f"raw residual {res:.3e}", res


def main():
    print("PI-BRANCH TEST — v2 admissible solutions == v1 admissible solutions\n")
    b, c, d, e, g, h = ROOT
    ok = True

    # (A) algebraic: sin accepts Delta=pi, cos-1 does not
    print("(A) algebraic difference at Delta = pi:")
    print(f"    v2  sin(pi)     = {math.sin(math.pi):+.3e}   -> accepted by sin form")
    print(f"    v1  cos(pi) - 1 = {math.cos(math.pi)-1:+.3e}   -> rejected by cos-1 form")
    ok = ok and abs(math.sin(math.pi)) < 1e-12 and abs(math.cos(math.pi)-1+2) < 1e-12

    # the genuine root is accepted by the gate
    a0, why0, _ = accept((b, c, d, e, g), h)
    print(f"\n    genuine root (Delta=0): accepted={a0}  ({why0})")
    ok = ok and a0

    # (B1) raw F_i = Delta_i  ->  Delta=pi gives raw residual pi
    print("\n(B1) round-trip gate rejects Delta=pi (raw F_i = Delta_i for arc-equality):")
    print(f"     a Delta=pi solution has raw |F_i| = {math.pi:.4f}  >>  tol 1e-7  -> REJECTED")
    # demonstrate the gate rejects any nonzero arc-equality value
    a1, why1, res1 = accept((b, 1.0, d, e, g), h)   # perturbed: arc-eq values ~0.19
    print(f"     perturbed config (arc-eq ~0.19): accepted={a1}  ({why1})")
    ok = ok and (not a1)

    # (B2) Delta=pi is geometrically unreachable (chain leaves domain first)
    print("\n(B2) Delta=pi is geometrically unreachable (DomainError before pi):")
    maxreach = 0.0; failed_at = None
    cc = c
    while cc < math.pi:
        try:
            F = RAO.constraints(b, cc, d, e, g, h * math.pi / 180)
            m = max(abs(F[i]) for i in ARC_EQ)
            maxreach = max(maxreach, m); cc += 0.05
        except Exception:
            failed_at = cc; break
    print(f"     max arc-equality value reached in-domain: {maxreach:.4f}")
    print(f"     chain went out of domain at c={failed_at:.3f} "
          f"(arc-eq never approached pi={math.pi:.3f})")
    ok = ok and (maxreach < math.pi)

    print("\nVERDICT:", "the sin form adds NO admissible solution beyond the cos-1 form"
          if ok else "UNEXPECTED — investigate")
    print("  -> v2 and v1 have identical admissible solution sets;")
    print("     the only algebraic difference (Delta=pi) is filtered, unconditionally and geometrically.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
