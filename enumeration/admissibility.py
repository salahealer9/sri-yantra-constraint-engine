"""
admissibility.py — D4 admissible-domain exclusion (Amendment 04, prereg-v1.4).

Realizes the §6 valid-domain clause "chain-defined arc arguments in range" as a
per-box exclusion: a box is removed iff it provably contains no real, in-range
plane figure. Evaluated under the same rigorous outward-rounded affine arithmetic
(aar.AAr) that §B2(iv) binds.

Registered (validated) machinery ONLY — Amendment 04 D4:
  1. sqrt-domain constraints      1-c^2 > 0, 1-d^2 > 0
  2. positivity constraints       b+c-g > 0, v8 > 0, v9 > 0, v12 > 0
  3. coordinate-range constraints  |x_i| <= RMAX for implemented coords x1..x19
  4. x11a division-free rule       |num*x13| > RMAX*|den|  (num=v9+c-g, den=v9+c+d-v12)

The U20/U21 loci of F13/F14/F15 are deliberately NOT assigned dedicated rules
(Amendment 04 D4 explicit safeguard): any unresolved seam is downgraded to a
Tier-1 negative under §B3, never asserted as completeness.

`classify_seam` is a DIAGNOSTIC ONLY (D5); it plays no part in the rigorous
exclusion and uses the float engine.
"""
import os, sys
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(_HERE)); sys.path.insert(0, _HERE)
from aar import AAr
import sriyantra_plane as SP

RMAX = 2.0   # FROZEN (Amendment 04 D4): exceeds max observed coordinate (~0.975, r=1),
             # well inside obviously non-constructible regions; cannot clip a real figure.

def _coords_aa(b, c, d, e, g):
    # All quantities UPSTREAM of x11a (no x11a reciprocal), so this is safe on the
    # v9+c+d-v12 seam; the x11a range is tested division-free by the caller.
    o = 1.0
    x1=(o-c*c).sqrt(); x2=(o-d*d).sqrt(); x3=(o-c)/(o+d)*x2; x4=(o-d)/(o+c)*x1
    x5=b/(b+c+d)*x4; x6=e/(c+d+e)*x3
    Q7=(d+g)/(c+d)*(x5/x6); U7=(d+g)/(Q7+o); x7=U7/(c+d)*x5
    Q8=(d+g)/(o+c)*(x1/x6); U8=(o+g)/(Q8+o); x8=U8/(o+c)*x1; v8=o-U8-d
    x16=(d+e+g)/(d+g)*x6; x11=(d+g)/(c+d)*x5; x17=(b+c+d)/(c+d)*x5
    Q9=(c+d)/(o+d)*(x2/x5); U9=(o+d)/(Q9+o); x9=U9/(o+d)*x2; v9=o-U9-c
    x10=(b+c-g)/(b+c+d)*x4; x18=(b+c+d+v8)/(b+c+d)*x4
    S12=d+g+v8; Q12=S12/(d+g)*(x6/x10); U12=S12/(Q12+o); x12=U12/(d+g)*x6; v12=d+g-U12
    x14=(U7+v8)/(d+g+v8)*x10
    x13=(e+v12)/(c+d+e)*x3; x19=(c+d+e+v9)/(c+d+e)*x3
    xs = {'x1':x1,'x2':x2,'x3':x3,'x4':x4,'x5':x5,'x6':x6,'x7':x7,'x8':x8,'x9':x9,
          'x10':x10,'x11':x11,'x12':x12,'x13':x13,'x14':x14,'x16':x16,'x17':x17,'x18':x18,'x19':x19}
    pos = {'v8':v8,'v9':v9,'v12':v12,'b+c-g':b+c-g}
    return xs, pos, (v9+c-g), (v9+c+d-v12), x13   # num11a, den11a, x13

def _absminmax(x):
    lo, hi = x.iv()
    amin = 0.0 if lo <= 0 <= hi else min(abs(lo), abs(hi))
    amax = max(abs(lo), abs(hi))
    return amin, amax

def domain_excluded(box):
    """True iff `box` provably contains no real, in-range plane figure (Amendment 04 D4).
    Rigorous: all tests use outward-rounded AAr enclosures. A domain error during
    coordinate evaluation is conservative (returns False -> box retained/subdivided)."""
    AAr._n = [0]
    b, c, d, e, g = [AAr.var((lo+hi)/2, (hi-lo)/2) for (lo, hi) in box]; o = 1.0
    if (o-c*c).iv()[1] <= 0 or (o-d*d).iv()[1] <= 0:            # (1) sqrt domains
        return True
    try:
        xs, pos, num, den, x13 = _coords_aa(b, c, d, e, g)
    except (ValueError, ZeroDivisionError):
        return False
    for q in pos.values():                                      # (2) positivity
        if q.iv()[1] <= 0:
            return True
    for x in xs.values():                                       # (3) coordinate range x1..x19
        lo, hi = x.iv()
        if lo > RMAX or hi < -RMAX:
            return True
    pmin, _ = _absminmax(num*x13); _, qmax = _absminmax(den)    # (4) x11a division-free
    if pmin > RMAX*qmax:
        return True
    return False

# ---------------- diagnostic only (Amendment 04 D5); NOT part of the exclusion ----------------
def classify_seam(center):
    """Label an unresolved box by the nearest known blow-up locus, else 'not-a-known-seam'."""
    b, c, d, e, g = center
    try:
        s = SP.chain(b, c, d, e, g)
        v8, v9, v12 = s['v8'], s['v9'], s['v12']
        x10, x13, x18, x19 = s['x10'], s['x13'], s['x18'], s['x19']
        Q20 = (c+d+v9-v12)/(d+g+v8)*(x10/x13)
        Q21 = (b+c+d+v8)/(c+d+e+v9)*(x19/x18)
        cand = {'x11a:v9+c+d-v12': abs(v9+c+d-v12),
                'U20:Q20+1': abs(Q20+1), 'U21:Q21+1': abs(Q21+1)}
        who = min(cand, key=cand.get)
        return who if cand[who] < 5e-3 else 'not-a-known-seam'
    except Exception:
        return 'chain_error'
