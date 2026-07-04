"""
spherical_lift.py — geodesic construction of Rao points 7 and 14 on the unit
sphere, the great-circle analogue of the validated plane point-14 lift. Uses the
existing spherical constructor's conventions (axis, geodesic/base-line meets,
right-half y>0 disambiguation) — adds NO new orientation assumptions.

  point 7  = geodesic(P4->6) ∩ geodesic(P7->5)          [same topology as plane ii(P4,6,P7,5)]
  P5       = axis(foot(point 7))                        [P5 is the axial foot of point 7]
  point 14 = geodesic(P8->10) ∩ base-line(P5)           [plane iy(P8,10, d-U7); here at P5 foot]

Both intersections are great-circle meets disambiguated to the right half (y>0),
exactly as every other constructed point 1..19. Arcs x7, x14 are read back with
the constructor's tarc() and validated against sriyantra.chain (frozen numeric).
"""
import math
import numpy as np
import spherical_geo_check as SGC
from spherical_geo_check import axis, foot, tarc, radius, geod_geod, geod_base, gdist

def lift_7_14(b, c, d, e, g, h):
    G = SGC.build(b, c, d, e, g, h)
    if G is None:
        return None
    P4, P7 = G['P4'], G['P7']
    p5, p6, p10 = G['p5'], G['p6'], G['p10']
    P8b = axis(G['yP8'])
    # point 7 = (P4-6) ∩ (P7-5)
    p7 = geod_geod(P4, p6, P7, p5)
    if p7 is None:
        return None
    yP5 = foot(p7)                       # P5 = axial foot of point 7
    # point 14 = (P8-10) ∩ base-line(P5)
    p14 = geod_base(P8b, p10, yP5)
    if p14 is None:
        return None
    return dict(p7=p7, p14=p14, yP5=yP5,
                x7=tarc(p7, yP5), x14=tarc(p14, yP5),
                r7=radius(p7), r14=radius(p14),
                ymin=min(abs(p7[1]), abs(p14[1])))   # right-half margin (disambig safety)

# ---------------------------------------------------------------------------
# STEP 1 (topology correction, plane viewer v1.0.1): the rendered triangle
# sides are PRODUCED to Rao's corners (P1->18, P4->16, P7->17, P9->19; Rao eqs
# 2.33, 2.22, 2.24, 2.43). The lift above is UNCHANGED by that correction:
# geodesic(P4->6) and geodesic(P4->16) are the same great circle exactly when
# point 6 is an interior point of the produced side — verified per root below.
# Points 4, 6, 5, 3 remain construction data; they are not triangle corners.
# ---------------------------------------------------------------------------
_PRODUCED_SIDES = [("P1", "p4", "p18"), ("P4", "p6", "p16"),
                   ("P7", "p5", "p17"), ("P9", "p3", "p19")]

def verify_produced_sides(b, c, d, e, g, h):
    """For each produced side (apex -> corner), verify the old truncation point
    is an INTERIOR point of the SAME great circle: |triple(apex, mid, corner)|
    ~ 0 (coplanarity with the origin) and 0 < arc parameter < 1. Returns
    dict(worst_triple, t_by_side) or None if the figure does not build."""
    G = SGC.build(b, c, d, e, g, h)
    if G is None:
        return None
    out = {}
    worst = 0.0
    for apex_key, mid_key, cor_key in _PRODUCED_SIDES:
        A = np.asarray(G[apex_key], float)
        M = np.asarray(G[mid_key], float)
        C = np.asarray(G[cor_key], float)
        triple = abs(float(np.dot(A, np.cross(M, C))))      # 0 <=> same great circle
        t = gdist(A, M) / max(gdist(A, C), 1e-300)          # interior iff 0 < t < 1
        out[apex_key] = (triple, t)
        worst = max(worst, triple)
    return dict(worst_triple=worst, t_by_side=out)
