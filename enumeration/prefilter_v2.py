"""
prefilter_v2.py — EXPLORATORY v2 analytic domain pre-filter (cone-edge scope).

NOT wired into the frozen instrument. A cheap, rigorous, sound shortcut that
excludes boxes PROVABLY entirely non-physical for the base acos nodes x1, x2,
WITHOUT any acos/AA evaluation. It can only agree with the existing full-chain
domain guard on the boxes it fires on (it is a strict subset of that guard's
'domain' verdicts) — it just reaches them cheaply.

Soundness (the critical property): x1 = acos(cos(r)/cos(c)), r = pi/2 - h, with
r,c in (0,pi/2) -> cos positive & decreasing -> x1 real iff h <= pi/2 - c.
A box is ENTIRELY invalid for x1 iff its most-validity-favorable point (smallest h
AND smallest c, maximizing pi/2 - c - h) still violates the bound:
        h_lo + c_lo > pi/2     (x1)        h_lo + d_lo > pi/2     (x2)
Using c_lo / d_lo (not c_hi/d_hi) is essential: testing the easiest point means a
fire guarantees ALL points invalid. The reverse would exclude valid sub-regions.
"""
import math
HALF_PI = math.pi / 2.0

def prefilter_excludes(box):
    """True iff the box is PROVABLY entirely non-physical for x1 or x2 (cone edge).
    box: list of 6 (lo,hi) for (b,c,d,e,g,h). Cheap: 2 comparisons, no acos."""
    (_b, (c_lo, _c_hi), (d_lo, _d_hi), _e, _g, (h_lo, _h_hi)) = box
    if h_lo + c_lo > HALF_PI:   # every point has r < c  -> cos(r)/cos(c) > 1  -> x1 undefined
        return True
    if h_lo + d_lo > HALF_PI:   # every point has r < d  -> x2 undefined
        return True
    return False
