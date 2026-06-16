#!/usr/bin/env python3
"""
Reproduce the residual table in the figure-boundary provenance note.

Validates the two figure-boundary points that this session pinned beyond the
original deposited constructor, against the engine chain, across the six Rao
Table-3 plane roots:

    point 14  = iy(P8, point 10, d - U7)   on the existing P8->10 Siva side
                                           (this is the P5 baseline, P5 = d - U7)
    point 11a = iy(P2, point 13, -g)       on the P2 Sakti side (line P2-13)

Each should match the chain's x14 / x11a to machine precision (<= ~1 ULP).
Plane form only. Residuals are tied to the current sriyantra_plane.chain and
figure_coords.figure_coordinates; commit this next to the note so the table is
re-runnable from a checkout rather than merely asserted.

Run:   python3 validate_figure_boundary.py
Exit:  0 iff every residual <= TOL, else 1 (usable as a regression check).
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

import sriyantra_plane as SP
from figure_coords import figure_coordinates, iy

TOL = 1e-15

# six Rao Table-3 plane roots   (subset label : [b, c, d, e, g])
ROOTS = [
    ("{1,2,3,4,8}",   [0.4637519730157872,  0.22325476217509888, 0.2889901265664934,  0.48818086442246117, 0.10615733111334424]),
    ("{1,2,3,10,15}", [0.45644883997437774, 0.23696658114287963, 0.28256012354252913, 0.4562670665912084,  0.10482186374164669]),
    ("{1,2,4,5,10}",  [0.4382374774890513,  0.21837144756622662, 0.2694897469377774,  0.4401819402846863,  0.09671637157352615]),
    ("{1,2,5,6,19}",  [0.4672982883672679,  0.2612238331881562,  0.3045526143474027,  0.47151256472874475, 0.12013376868568548]),
    ("{1,2,6,14,19}", [0.4687099322187803,  0.25707121151023815, 0.30819964644445685, 0.4805815685697558,  0.12178989580536266]),
    ("{1,2,8,9,20}",  [0.5606590709573589,  0.27946122086183434, 0.27946122086183434, 0.5139986285217595,  0.1014104659508983]),
]


def residuals(p):
    """Return (resid_x14, resid_x11a) for one root, comparing |constructed| to |chain|."""
    b, c, d, e, g = p
    s = SP.chain(*p)
    P = figure_coordinates(*p)
    p14 = iy(P["P8"], P["10"], d - s["U7"])   # point 14 on the P8->10 side, at P5 = d - U7
    p11a = iy(P["P2"], P["13"], -g)           # point 11a on the P2 side (line P2-13), at -g
    return (abs(abs(p14[0]) - abs(s["x14"])),
            abs(abs(p11a[0]) - abs(s["x11a"])))


def main():
    print("root              | resid x14 (P8->10) | resid x11a (P2--13)")
    print("-" * 60)
    worst = 0.0
    for name, p in ROOTS:
        r14, r11a = residuals(p)
        worst = max(worst, r14, r11a)
        print("%-17s |   %.2e        |   %.2e" % (name, r14, r11a))
    print("-" * 60)
    print("max residual over all roots: %.2e   (tol %.0e)" % (worst, TOL))
    ok = worst <= TOL
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
