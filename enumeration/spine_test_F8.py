"""
Spine test, beam 1: the radial geodesic-incidence constraint F8.

PLANE constraint (frozen engine):
    F8 = r - r16,   r16 = sqrt((d+e)^2 + x16^2),  r = 1
  i.e. point 16 lies on the bounding circle of radius r  <=>  r^2 = (d+e)^2 + x16^2.

SPHERICAL lift (Rao eq 6.14: right spherical triangle, cos(hyp)=cos(leg)cos(leg)):
  geodesic radial distance rho16 to point 16 satisfies
      cos(a*rho16) = cos(a*(d+e)) * cos(a*x16),     a = curvature scale = 1/R
  "point 16 on bounding geodesic circle of radius r"  <=>  rho16 = r, hence
      G(a) := cos(a*r) - cos(a*(d+e)) * cos(a*x16) = 0.

Claim to verify (the spine):
      G(a)/a^2  -->  (1/2)(r^2 - (d+e)^2 - x16^2) = (1/2)(r - r16)(r + r16) = (1/2)(r+r16)*F8
  as a->0. So the spherical equation, flattened, IS the plane constraint F8
  (vanishes on exactly the same variety), with no free choice introduced.

Scope: ONE beam. The plane CHAIN (x16, etc.) is held at its frozen values;
only the CONSTRAINT is lifted. A fuller lift would also make the chain spherical.
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

def G(vals, alpha):
    """Spherical radial residual for point 16, chain held at frozen plane values."""
    s = S.chain(*vals)
    a = mp.mpf(repr(vals[2])) + mp.mpf(repr(vals[3]))     # d + e
    b = mp.mpf(repr(s['x16']))                            # x16
    c = mp.mpf(repr(s['r']))                              # r (=1)
    al = mp.mpf(alpha)
    return mp.cos(al*c) - mp.cos(al*a)*mp.cos(al*b)

def analytic_limit_and_F8(vals):
    s = S.chain(*vals)
    a = mp.mpf(repr(vals[2])) + mp.mpf(repr(vals[3]))
    b = mp.mpf(repr(s['x16']))
    c = mp.mpf(repr(s['r']))
    L = (a*a + b*b - c*c)/2                               # exact lim G/a^2 = (1/2)(r16^2 - r^2)
    F8 = S.constraints(*vals)[8]                          # plane constraint value
    r16 = mp.sqrt(a*a + b*b)
    return L, mp.mpf(repr(F8)), r16, c

def run(label, vals):
    L, F8, r16, c = analytic_limit_and_F8(vals)
    print(f"\n=== {label} ===")
    print(f"  plane F8 = r - r16        = {mp.nstr(F8, 6)}")
    print(f"  exact  lim G/a^2          = (1/2)(r16^2 - r^2)           = {mp.nstr(L,6)}")
    print(f"  identity check -(1/2)(r+r16)*F8 = {mp.nstr(-(c+r16)/2*F8,6)}  [should equal exact limit]")
    print(f"  {'alpha':>8} {'G(alpha)':>16} {'G/alpha^2':>18} {'G/alpha^2 - L':>16}")
    for k in range(0, 7):
        al = mp.mpf(10)**(-k)
        g = G(vals, al)
        ratio = g/(al*al)
        print(f"  {mp.nstr(al,2):>8} {mp.nstr(g,6):>16} {mp.nstr(ratio,10):>18} {mp.nstr(ratio-L,4):>16}")

# Generic point (imposes only F1,F2): F8 is appreciably nonzero -> proves the
# reduction is an IDENTITY between spherical and plane constraint, not a root artifact.
run("GENERIC point (plane optimum, F8 != 0)", S.PLANE_OPT)

# Certified root that IMPOSES F8 (engine residual ~5e-13): F8 ~ 0, so the alpha^2
# term must vanish and G should fall like alpha^4. Confirms it sits on the variety.
CERT_1234_8 = (0.4637519730157872, 0.22325476217509888, 0.2889901265664934,
               0.48818086442246117, 0.10615733111334424)
run("CERTIFIED {1,2,3,4,8} root (imposes F8, F8 ~ 0)", CERT_1234_8)

# Show the alpha^4 falloff explicitly on the certified root
print("\n=== alpha^4 falloff on certified root (G/alpha^4 should tend to a finite const) ===")
for k in range(0, 7):
    al = mp.mpf(10)**(-k)
    g = G(CERT_1234_8, al)
    print(f"  alpha={mp.nstr(al,2):>8}   G/alpha^2={mp.nstr(g/al**2,4):>12}   G/alpha^4={mp.nstr(g/al**4,8):>14}")
