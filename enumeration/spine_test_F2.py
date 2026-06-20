"""
Spine test, Beam 3: the concentricity constraint F2 (Rao eqs 3.2b, 3.2c, 3.2).

Rao spherical originals (p.214, unit sphere):
   (3.2b)  tan t   = tan(d+g-U7) / sin(x7)          [t is an O(1) ANGLE, not an arc]
   (3.2c)  tan rT  = sin(x7) * tan(t/2)              [rT, x7 are ARCS]
   (3.2)   F2      = d - U7 - rT       (arc P_C P_T, concentricity error)
Engine (plane) reduction: sin(x7)->x7, tan(arc)->arc, t unchanged ->
   t = atan((d+g-U7)/x7),   rT = x7*tan(t/2),   F2 = d - U7 - rT.
NOTE: printed reduced eq (6.12) shows x7*(t/2); that is a PAPER TYPO (dropped 'tan').
   The spherical (3.2c) and the engine both use tan(t/2); Rao's Table 3 confirms it.

Lift with angular scale a (arc = a * plane-length), chain held at frozen plane values:
   t_s(a)  = atan( tan(a*V7) / sin(a*x7) ),   V7 = d+g-U7
   rT_s(a) = atan( sin(a*x7) * tan(t_s/2) )            [arc]
   G2(a)   = a*d - a*U7 - rT_s(a)                       [spherical concentricity arc]

Structure (additive arc relation, ODD in a):  G2(a) = a * F2_plane + O(a^3).
=> leading order a^1, NOT a^2. The metric families (F3/F6/F8) were a^2 because they
   embed via cosines; F2 is a^1 because it is a literal arc subtraction.
"""
import sys, os;
_here = os.path.dirname(os.path.abspath(__file__))
_root = _here
while _root != os.path.dirname(_root):
    if os.path.exists(os.path.join(_root, "sriyantra_plane.py")):
        break
    _root = os.path.dirname(_root)
for _p in (_here, _root, os.path.join(_root, "enumeration")):
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)
import sriyantra_plane as S
import mpmath as mp
mp.mp.dps = 60
def m(x): return mp.mpf(repr(x))

def G2(vals, alpha):
    s = S.chain(*vals); b,c,d,e,g = vals
    U7, x7 = m(s['U7']), m(s['x7']); V7 = m(d)+m(g)-U7
    al = mp.mpf(alpha)
    t_s  = mp.atan( mp.tan(al*V7) / mp.sin(al*x7) )
    rT_s = mp.atan( mp.sin(al*x7) * mp.tan(t_s/2) )
    return al*m(d) - al*U7 - rT_s

def run(label, vals):
    F2 = m(S.constraints(*vals)[2])
    print(f"\n=== {label} ===")
    print(f"  plane F2 = d - U7 - rT    = {mp.nstr(F2,6)}")
    print(f"  predicted lim G2/a        = F2 (leading order a^1, coeff 1)")
    print(f"  {'alpha':>8} {'G2(alpha)':>16} {'G2/alpha':>18} {'G2/alpha - F2':>15}")
    for k in range(0, 7):
        al = mp.mpf(10)**(-k); g2 = G2(vals, al); ratio = g2/al
        print(f"  {mp.nstr(al,2):>8} {mp.nstr(g2,6):>16} {mp.nstr(ratio,10):>18} {mp.nstr(ratio-F2,4):>15}")

# Off-variety point (not on any F-root): F2 clearly nonzero -> proves the a^1 identity.
run("OFF-VARIETY point (F2 != 0)", (0.45, 0.22, 0.32, 0.46, 0.12))
# Certified root imposing F2: F2 ~ 0 -> a^1 term dies, residual ~ a^3.
CERT = (0.4637519730157872, 0.22325476217509888, 0.2889901265664934,
        0.48818086442246117, 0.10615733111334424)  # {1,2,3,4,8}
run("CERTIFIED {1,2,3,4,8} root (F2 ~ 0)", CERT)

print("\n=== odd-power check on certified root: (G2 - a*F2)/a^3 -> finite const ===")
F2c = m(S.constraints(*CERT)[2])
for k in range(1, 6):
    al = mp.mpf(10)**(-k); g2 = G2(CERT, al)
    print(f"  alpha={mp.nstr(al,2):>7}   (G2 - a*F2)/a^3 = {mp.nstr((g2-al*F2c)/al**3,8)}")
