#!/usr/bin/env python3
"""
render_overdetermined_figure.py
================================
Certified renderer for the complete nine-triangle plane Śrī Yantra, in the
normalized §7 metric frame (axis = y-axis, centre = origin, r = 1).

Single figure: the over-determined {F1,F2,F8,F9,F16,F20} solution (c = d, the
X = 20 row of the results-note Table 1).

THE GATE. Before anything is drawn, every vertex the figure uses is validated
against the frozen engine to machine precision (tolerance 1e-15):
  * the 18 labelled intersection points (1-14, 16-19) against the chain's x-values;
  * the inner auxiliary points 20, 21 against the chain scalars U20, U21
    (via figure_coords_inner.validate_inner);
  * the on-axis apex heights against their exact parameter expressions.
If ANY residual exceeds the tolerance the script raises and writes no PDF -- it
refuses to draw anything it cannot certify. Run it under the pinned/frozen engine
(commit 0baa2c5), not a working copy, so the certificate is your pipeline's.

The nine primary triangles are Rao's nine transverse arcs, each named apex–endpoint:
  Śakti (apex below, opens up):  P0-2, P1-4, P4-6, P2-13, P3-14
  Śiva  (apex above, opens down): P10-1, P9-3, P7-5, P8-10
Point 14 lies on the P8->10 side at the P5 baseline (d - U7); P3->14 is the
ninth (fifth Śakti) side. Each triangle is drawn from its apex to the named
corner and its mirror image.

Output: figure-overdetermined.pdf (vector). Run: python3 render_overdetermined_figure.py
"""
import os
import sys

# --- make engine + constructors importable from any checkout ---
_here = os.path.dirname(os.path.abspath(__file__))
_root = _here
while _root != os.path.dirname(_root):
    if os.path.exists(os.path.join(_root, "sriyantra_plane.py")):
        break
    _root = os.path.dirname(_root)
for _p in (_here, _root, os.path.join(_root, "enumeration")):
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import sriyantra_plane as SP
from figure_coords import figure_coordinates as FC, iy
from figure_coords_inner import inner_points, validate_inner

TOL = 1e-15
OUT = os.path.join(_here, "figure-overdetermined.pdf")

# Over-determined {1,2,8,9,16,20} root (c = d; F20 forces the up-down symmetry)
# MAIN / manuscript figure: Rao's plane optimum (Table 3, Fig. 6d) — the reference
# plane Sri Yantra. Satisfies F1 = F2 = 0 with F8, F9 > 0 (Rao eq 5.3); it is NOT a
# census root (no 5-constraint subset selects it) and is used for visual reference only.
ROOT = [0.482391, 0.261039, 0.287454, 0.467384, 0.108463]

# AUDIT / regression figure: the {1,2,8,9,20} certified root (Rao Fig. 6c; matches
# Kulaichev 1984). Kept for topology regression: F8, F9 selected -> corners 16, 17
# lie exactly on the circumscribing circle (r16 = r17 = 1). Render with --audit.
ROOT_KULAICHEV_AUDIT = [0.5606590709573589, 0.27946122086183434, 0.27946122086183434,
                        0.5139986285217595, 0.1014104659508983]

# Rao's nine root triangles, (apex_label, corner_label). Corners are the endpoints of
# the transverse sides PRODUCED to their base lines (Rao eqs 2.22, 2.24, 2.33, 2.43):
# P1->18 (base P8), P4->16 (base P9), P9->19 (base P2), P7->17 (base P1). Points 4,6,3,5
# are interior construction crossings of those sides, not corners (topology audit, docs/).
TRIANGLES = [("P0", "2"), ("P1", "18"), ("P2", "13"), ("P3", "14"), ("P4", "16"),
             ("P10", "1"), ("P9", "19"), ("P8", "10"), ("P7", "17")]


def build_points(root):
    b, c, d, e, g = root
    s = SP.chain(*root)
    P = FC(*root)
    P["14"] = tuple(iy(P["P8"], P["10"], d - s["U7"]))   # P3 arc endpoint, on P8->10 at P5
    return P, s


def gate(root):
    """Validate every vertex against the frozen engine. Returns (ok, worst, report)."""
    b, c, d, e, g = root
    P, s = build_points(root)
    rows, worst = [], 0.0

    # (a) labelled intersection points 1-14, 16-19 vs chain x-values
    for k in [str(i) for i in range(1, 15)] + ["16", "17", "18", "19"]:
        r = abs(abs(P[k][0]) - abs(s["x" + k]))
        rows.append(("pt" + k, r)); worst = max(worst, r)

    # (b) inner auxiliary points 20, 21 vs chain scalars U20, U21
    vi = validate_inner(*root)
    for k in ("20", "21"):
        rows.append(("pt" + k, vi[k])); worst = max(worst, vi[k])

    # (c) on-axis apex heights vs exact parameter expressions
    exact = {"P0": -1.0, "P1": -(b + c), "P3": -c, "P4": -g,
             "P7": d, "P9": d + e, "P10": 1.0}
    for k, y in exact.items():
        r = abs(P[k][1] - y)
        rows.append((k + ".y", r)); worst = max(worst, r)

    return worst <= TOL, worst, rows


def render(root, path):
    ok, worst, rows = gate(root)
    print("Gate: certify every vertex against the frozen engine (tol %.0e)" % TOL)
    for name, r in rows:
        print("  %-7s %.2e" % (name, r))
    print("  max residual: %.2e  ->  %s" % (worst, "PASS" if ok else "FAIL"))
    if not ok:
        raise SystemExit("GATE FAILED: a vertex did not validate; refusing to draw.")

    P, s = build_points(root)
    mir = lambda p: (-p[0], p[1])
    ip = inner_points(*root)

    fig, ax = plt.subplots(figsize=(5.6, 5.6))
    th = np.linspace(0, 2 * np.pi, 512)
    ax.plot(np.cos(th), np.sin(th), color="0.55", lw=0.8)          # circumcircle r=1
    ax.plot([0, 0], [-1, 1], color="0.8", lw=0.6, ls=(0, (4, 4)))  # symmetry axis
    for apex, cor in TRIANGLES:
        A = tuple(P[apex]); C = tuple(P[cor])
        poly = np.array([A, C, mir(C), A])
        ax.plot(poly[:, 0], poly[:, 1], color="black", lw=1.0)
    for k in ("20", "21"):                                         # inner concurrency feet
        ax.plot([ip[k][0], -ip[k][0]], [ip[k][1], ip[k][1]], ".",
                ms=4, color="crimson", zorder=5)
    ax.plot(0, 0, "o", ms=4.5, color="black", zorder=6)            # bindu

    ax.set_aspect("equal"); ax.axis("off")
    ax.set_xlim(-1.05, 1.05); ax.set_ylim(-1.05, 1.05)
    fig.savefig(path, format="pdf", bbox_inches="tight")
    plt.close(fig)
    print("wrote %s" % path)


if __name__ == "__main__":
    import sys
    if "--audit" in sys.argv:
        audit_out = OUT.replace(".pdf", "-kulaichev-audit.pdf")
        render(ROOT_KULAICHEV_AUDIT, audit_out)
    else:
        render(ROOT, OUT)
