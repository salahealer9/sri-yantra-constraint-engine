#!/usr/bin/env python3
"""
generate_B.py  --  deterministic construction of the plane confirmatory box B.

SPECIFICATION CORRECTION (supersedes the hand-derived box of prereg ts6).
-----------------------------------------------------------------------
The originally registered box pooled the per-variable extrema of BOTH Rao
Table 1 (spherical: 6 angular variables in RADIANS, r = pi/2 - h) and Rao
Table 3 (plane: 5 length variables, r == 1).  Those are heterogeneous
parameterizations: a spherical radian value and a plane length value do not
share a coordinate system, so their pooled extrema do not describe a box in
plane-variable space.  The hand-derived literals were additionally not
reproducible by any single rule (b,g kept the pooled maximum; c,d,e dropped
each variable's largest value).

Corrected rule (this script, dimensionally coherent and reproducible):
    The plane confirmatory box is derived from the PLANE reference data only
    (Rao Table 3), in the plane variables (b,c,d,e,g):

      1. per variable, take [min, max] across the 6 plane rows;
      2. widen by 50% of the range on each side  (lo-0.5R, hi+0.5R), R=max-min;
      3. intersect with the valid domain:
           positivity   -> clamp lower bounds to EPS > 0;
           c, d < r = 1 -> clamp those upper bounds below 1.
         (For Table-3 data both clamps are inactive; logged if they ever fire.)

Spherical Table 1 is intentionally NOT used: the plane constraint systems are
self-contained in the plane variables, so the plane search inherits nothing
from the spherical solution set.  Output is written to B.json.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sriyantra_plane as pl

VARS = ['b', 'c', 'd', 'e', 'g']
WIDEN = 0.50          # fraction of range added on each side
EPS = 1e-6            # positivity clamp for lower bounds
R = 1.0               # plane normalization
CDLIM = R             # c, d < r

def build():
    rows = [v for _, v in pl.TABLE3]              # 6 plane rows, (b,c,d,e,g)
    assert all(len(v) == 5 for v in rows), "Table 3 rows must be (b,c,d,e,g)"
    B, log = {}, []
    for i, nm in enumerate(VARS):
        col = [r[i] for r in rows]
        lo, hi = min(col), max(col)
        rng = hi - lo
        wlo, whi = lo - WIDEN * rng, hi + WIDEN * rng
        # valid-domain clamps
        clo = max(EPS, wlo)
        if clo != wlo: log.append(f"{nm}: lower clamped {wlo:.6f} -> {clo:.6f} (positivity)")
        chi = whi
        if nm in ('c', 'd') and chi >= CDLIM:
            chi = CDLIM - EPS
            log.append(f"{nm}: upper clamped {whi:.6f} -> {chi:.6f} (c,d<r)")
        B[nm] = [clo, chi]
    return B, rows, log

def main():
    B, rows, log = build()
    # provenance + self-checks
    print("Plane confirmatory box B (from Rao Table 3, plane-only, widen 50%):")
    for nm in VARS:
        print(f"  {nm}: [{B[nm][0]:.6f}, {B[nm][1]:.6f}]")
    print("\n  clamps activated:", log if log else "none (box is interior to valid domain)")
    # check: B contains every plane Rao root it was built from
    ok = True
    for cons, v in pl.TABLE3:
        inside = all(B[VARS[i]][0] <= v[i] <= B[VARS[i]][1] for i in range(5))
        if not inside: ok = False; print(f"  !! Rao row {cons} NOT contained:", v)
    print("  contains all 6 plane Rao roots:", ok)
    # check: corner-free (no variable lower bound near 0) and c,d safely < 1
    print("  min lower bound across vars:", round(min(B[nm][0] for nm in VARS), 4),
          "| max c,d upper:", round(max(B['c'][1], B['d'][1]), 4))
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "B.json")
    meta = dict(source="Rao Table 3 (plane)", rule="per-var [min,max] over 6 rows, widen 50%/side, clamp positivity & c,d<r",
                widen=WIDEN, eps=EPS, r=R, box=B)
    with open(out, "w") as f: json.dump(meta, f, indent=2)
    print("\n  written:", out)

if __name__ == "__main__":
    main()
