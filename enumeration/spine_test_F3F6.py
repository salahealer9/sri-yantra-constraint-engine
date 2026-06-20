"""
Spine test, Beam 2: the isosceles family F3, F6 (Rao eq 6.13).

Rao 6.13 reduction:   cos A - cos(2x)/cos(x)   ->   -A^2/2 + (3/2) x^2
PLANE forms (frozen engine):
    F3 = -V8^2/2 + 1.5 x10^2     (A=V8=d+g+v8,  x=x10)
    F6 = -V7^2/2 + 1.5 x7^2      (A=V7=d+g-U7,  x=x7)
SPHERICAL lift (scale a = 1/R):
    G_i(a) = cos(a*A_i) - cos(2*a*x_i)/cos(a*x_i)
Predicted (series): G_i(a) = a^2 * F_i  +  a^4 * (A_i^4/24 + x_i^4/8) + O(a^6)
  -> coefficient C_i = 1 EXACTLY (Rao's reduced form *is* F_i), unlike F8.
This is a different identity (6.13) and an independent part of the algebra
from the radial (6.14) family, so agreement = pattern, not the same trick twice.
Scope: one beam each; plane CHAIN held at frozen values, only the CONSTRAINT lifted.
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

def Gi(vals, alpha, which):
    s = S.chain(*vals)
    if which == 3:  A, x = m(s['V8']), m(s['x10'])
    else:           A, x = m(s['V7']), m(s['x7'])
    al = mp.mpf(alpha)
    return mp.cos(al*A) - mp.cos(2*al*x)/mp.cos(al*x), A, x

def run(label, vals, which):
    L   = m(S.constraints(*vals)[which])            # exact plane constraint value
    _,A,x = Gi(vals, mp.mpf(1), which)
    c4  = A**4/24 + x**4/8                           # predicted alpha^4 coefficient
    print(f"\n=== {label}  (testing F{which}) ===")
    print(f"  plane F{which}                 = {mp.nstr(L,6)}")
    print(f"  predicted lim G/a^2       = F{which} (coeff C=1 exactly)")
    print(f"  predicted a^4 coeff       = A^4/24 + x^4/8 = {mp.nstr(c4,6)}")
    print(f"  {'alpha':>8} {'G(alpha)':>16} {'G/alpha^2':>18} {'G/alpha^2 - F':>15}")
    for k in range(0, 7):
        al = mp.mpf(10)**(-k)
        g,_,_ = Gi(vals, al, which)
        ratio = g/(al*al)
        print(f"  {mp.nstr(al,2):>8} {mp.nstr(g,6):>16} {mp.nstr(ratio,10):>18} {mp.nstr(ratio-L,4):>15}")

# Generic point (imposes only F1,F2): F3,F6 both nonzero -> proves identity off-variety.
run("GENERIC (plane optimum)", S.PLANE_OPT, 3)
run("GENERIC (plane optimum)", S.PLANE_OPT, 6)

# Certified roots on each variety -> alpha^2 term dies, residual ~ alpha^4.
CERT_F3 = (0.4637519730157872, 0.22325476217509888, 0.2889901265664934,
           0.48818086442246117, 0.10615733111334424)   # {1,2,3,4,8}, res 4.9e-13
CERT_F6 = (0.4003921329376827, 0.20403429976742082, 0.32390079235245506,
           0.4572832152314182, 0.13338242287861302)    # {1,2,4,6,11}, res 3.4e-13
run("CERTIFIED {1,2,3,4,8} root (F3~0)", CERT_F3, 3)
run("CERTIFIED {1,2,4,6,11} root (F6~0)", CERT_F6, 6)

# alpha^4 coefficient recovery on the certified roots
print("\n=== a^4 coefficient recovery on certified roots (G - a^2 F)/a^4 -> A^4/24 + x^4/8 ===")
for label, vals, which in [("F3", CERT_F3, 3), ("F6", CERT_F6, 6)]:
    L = m(S.constraints(*vals)[which]); _,A,x = Gi(vals, mp.mpf(1), which)
    pred = A**4/24 + x**4/8
    print(f"  {label}: predicted = {mp.nstr(pred,8)}")
    for k in range(1, 5):
        al = mp.mpf(10)**(-k); g,_,_ = Gi(vals, al, which)
        c4 = (g - al*al*L)/al**4
        print(f"     alpha={mp.nstr(al,2):>7}  (G - a^2 F)/a^4 = {mp.nstr(c4,8)}")
