"""
figure_coords_inner.py — coordinate realization of Rao's inner-triangle
auxiliary points 20 and 21, closing the (b,c,d,e,g) -> full-geometry map for
the plane Sri Yantra. Companion to figure_coords.py; same normalized frame
(axis = y-axis, centre = origin, r = 1), same pure straight-line construction.

Rao (1998), constraints 13-14 (p.216), define these points directly:
  * point 20 = (transverse arc P8->10) ∩ (transverse arc P2->13)        [eq 3.13 ff.]
  * point 21 = (transverse arc P1->18) ∩ (transverse arc P9->19)        [eq 3.14 ff.]
P1->18 is the same line as P1->4 (point 18 lies on it); P9->19 == P9->3.
Each point's HEIGHT is the engine scalar carried for F13/F14:
  * y(20) = yP8 - U20      * y(21) = (d+e) - U21
The base line through each meets the axis at P20=(0,y20), P21=(0,y21)
(Rao's P20, P21), the apex base-points of the inner Sakti/Siva triangles.

NOTE ON "POINT 15": Rao's construction (pp.209-213) numbers the intersection
points 1-14, 16-19, plus 11a. There is NO point 15 — the index is skipped in
the source (15 occurs only as a CONSTRAINT label, F15). The §7 metric set's
"points 1-19" therefore contains 18 vertices, not 19; the apparent gap is a
numbering artifact, not a missing coordinate. Constructor coverage is complete.
"""
import os
import sys

# --- make the engine + constructor importable regardless of where this sits ---
# walk up to the repo root (the dir holding sriyantra_plane.py), then expose
# the script dir, the repo root, and repo_root/enumeration.
_here = os.path.dirname(os.path.abspath(__file__))
_root = _here
while _root != os.path.dirname(_root):
    if os.path.exists(os.path.join(_root, "sriyantra_plane.py")):
        break
    _root = os.path.dirname(_root)
for _p in (_here, _root, os.path.join(_root, "enumeration")):
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)

import math
import sriyantra_plane as SP
from figure_coords import figure_coordinates as FC, ii

def inner_points(b, c, d, e, g, r=1.0):
    p = FC(b, c, d, e, g, r)
    P1, P2, P8, P9 = p['P1'], p['P2'], p['P8'], p['P9']
    p3, p4, p10, p13 = p['3'], p['4'], p['10'], p['13']
    pt20 = ii(P2, p13, P8, p10)        # P2->13  ∩  P8->10
    pt21 = ii(P1, p4,  P9, p3)         # P1->18(=P1->4) ∩ P9->19(=P9->3)
    P20  = (0.0, pt20[1])
    P21  = (0.0, pt21[1])
    return {'20': pt20, '21': pt21, 'P20': P20, 'P21': P21}

def validate_inner(b, c, d, e, g):
    s = SP.chain(b, c, d, e, g); ip = inner_points(b, c, d, e, g)
    yP8 = FC(b, c, d, e, g)['P8'][1]
    return {
        '20': abs(ip['20'][1] - (yP8 - s['U20'])),     # height vs yP8 - U20
        '21': abs(ip['21'][1] - ((d + e) - s['U21'])),  # height vs (d+e) - U21
    }

if __name__ == "__main__":
    print("Validation of inner points 20, 21 against the chain scalars U20/U21")
    print("(Rao Table-3 roots; tol 1e-15)\n")
    print(f"{'root':18s} {'resid 20 (P8-U20)':>20s} {'resid 21 (d+e-U21)':>22s}")
    print("-"*62)
    worst = 0.0
    for cons, vals in SP.TABLE3:
        r = validate_inner(*vals)
        worst = max(worst, r['20'], r['21'])
        print(f"{str(cons):18s} {r['20']:>20.2e} {r['21']:>22.2e}")
    print("-"*62)
    print(f"{'max residual':18s} {worst:>43.2e}")
    print("PASS" if worst < 1e-15 else "FAIL")
