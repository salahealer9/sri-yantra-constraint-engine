"""
MINIMAL SPHERICAL ENGINE PROTOTYPE  (Rao 1998, spherical Sri Yantra)

Goal (per the agreed milestone): implement Rao's spherical chain exactly and
verify it recovers the FROZEN plane engine (sriyantra_plane.py) as the angular
scale alpha -> 0, for the whole chain and all 20 constraints simultaneously.

Construction principle (self-validating):
  The frozen plane engine is the alpha->0 reduction of Rao's spherical chain.
  This file UN-REDUCES each plane formula to its spherical ancestor:
     x = (P/Q) y           ->  tan(x)  = [sin(aP)/sin(aQ)] tan(y)      (Rao 2.39 / 6.7)
     U = S/(Q+1)           ->  tan(U)  = sin(aS)/(Q + cos(aS))         (Rao 2.38 / 6.10)
     Q = (P/Q')(A/B)       ->  Q       = [sin(aP)/sin(aQ')](tanA/tanB) (Rao 2.37 / 6.9)
     sqrt(r^2 - c^2)       ->  cos(x)  = cos(ar)/cos(ac)               (Rao 6.6 / 6.6a)
     sqrt(L1^2 + L2^2)     ->  cos(r_i)= cos(L1) cos(L2)               (Rao 6.14, radial)
     t = atan(V/x)         ->  tan(t)  = tan(V)/sin(x)                 (Rao 3.2b)
     rT = x tan(t/2)       ->  tan(rT) = sin(x) tan(t/2)               (Rao 3.2c) [NB: tan(t/2),
                                                            confirming the (6.12) print typo]
     -A^2/2 + 1.5 x^2      ->  cos(A) - cos(2x)/cos(x)                 (Rao 6.13a / 3.3)
  All length-combinations become arcs (multiply by a=alpha); chain quantities
  x_i, U_i, v_i, r_i, rT are arcs (O(alpha)); t is a genuine angle (O(1)).
  If a formula is un-reduced WRONG, its constraint fails to converge -> the
  alpha->0 test below is a correctness proof on the entire un-reduction.

NOTE on order d_i: the faithful spherical residual of an ARC-difference constraint
(e.g. F8 = r - r16) is O(alpha^1); only the three cos-based isosceles constraints
F3,F4,F6 are O(alpha^2).  (Beam 1 used a non-canonical metric lift of F8 -> alpha^2;
that is a valid alternative form, not the engine's form.)
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
import mpmath as mp
import sriyantra_plane as PLANE
mp.mp.dps = 50

def _f(x): return mp.mpf(repr(x))

def chain_sph(b, c, d, e, g, alpha, r=1.0):
    a = mp.mpf(alpha)
    b, c, d, e, g, r = map(_f, (b, c, d, e, g, r))
    S = mp.sin; C = mp.cos; T = mp.tan; AT = mp.atan; AC = mp.acos
    def rat(P, Q, y):            # P,Q are plane length-combos -> arcs aP,aQ
        return AT(S(a*P)/S(a*Q) * T(y))
    def rata(Pa, Qa, y):         # Pa,Qa already arcs
        return AT(S(Pa)/S(Qa) * T(y))
    def Uof(Sa, Q):              # tan(U)=sin(Sa)/(Q+cos(Sa))
        return AT(S(Sa)/(Q + C(Sa)))

    x1 = AC(C(a*r)/C(a*c))                         # 6.6
    x2 = AC(C(a*r)/C(a*d))
    x3 = rat(r-c, r+d, x2)                         # 6.7
    x4 = rat(r-d, r+c, x1)
    x5 = rat(b, b+c+d, x4)
    x6 = rat(e, c+d+e, x3)
    # point 7
    S7a = a*(d+g)
    Q7  = S(a*(d+g))/S(a*(c+d)) * (T(x5)/T(x6))    # 6.9
    U7  = Uof(S7a, Q7)                              # 6.10
    V7  = S7a - U7
    x7  = rata(U7, a*(c+d), x5)
    # point 8
    S8a = a*(r+g)
    Q8  = S(a*(d+g))/S(a*(r+c)) * (T(x1)/T(x6))
    U8  = Uof(S8a, Q8)
    V8  = S8a - U8
    x8  = rata(U8, a*(r+c), x1)
    v8  = a*r - U8 - a*d
    # arcs
    x16 = rat(d+e+g, d+g, x6)
    x11 = rat(d+g, c+d, x5)
    x17 = rat(b+c+d, c+d, x5)
    # point 9
    S9a = a*(r+d)
    Q9  = S(a*(c+d))/S(a*(r+d)) * (T(x2)/T(x5))
    U9  = Uof(S9a, Q9)
    V9  = S9a - U9
    x9  = rata(U9, a*(r+d), x2)
    v9  = a*r - U9 - a*c
    # points 10,18
    x10 = rat(b+c-g, b+c+d, x4)
    x18 = rata(a*(b+c+d)+v8, a*(b+c+d), x4)
    # point 12
    S12a = a*(d+g) + v8
    Q12  = S(S12a)/S(a*(d+g)) * (T(x6)/T(x10))
    U12  = Uof(S12a, Q12)
    x12  = rata(U12, a*(d+g), x6)
    v12  = a*(d+g) - U12
    # point 14
    x14 = rata(U7+v8, S12a, x10)
    # points 13,19
    x13 = rata(a*e + v12, a*(c+d+e), x3)
    x19 = rata(a*(c+d+e)+v9, a*(c+d+e), x3)
    # point 11a
    x11a = rata(v9 + a*(c-g), v9 + a*(c+d) - v12, x13)
    # radial arcs (6.14): cos(r_i)=cos(leg1)cos(leg2)
    r16 = AC(C(a*(d+e)) * C(x16))
    r17 = AC(C(a*(b+c)) * C(x17))
    r18 = AC(C(a*d + v8) * C(x18))
    r19 = AC(C(a*c + v9) * C(x19))
    # concentricity (3.2b, 3.2c)
    t  = AT(T(V7)/S(x7))
    rT = AT(S(x7) * T(t/2))
    # U20, U21
    S20a = a*(c+d) + v8 + v9
    Q20  = S(a*(c+d)+v9-v12)/S(S12a) * (T(x10)/T(x13))
    U20  = Uof(S20a, Q20)
    S21a = a*(b+c+d+e)
    Q21  = S(a*(b+c+d)+v8)/S(a*(c+d+e)+v9) * (T(x19)/T(x18))
    U21  = Uof(S21a, Q21)
    return dict(a=a, r=r, b=b, c=c, d=d, e=e, g=g,
                x1=x1,x2=x2,x3=x3,x4=x4,x5=x5,x6=x6,x7=x7,x8=x8,x9=x9,x10=x10,
                x11=x11,x12=x12,x13=x13,x14=x14,x16=x16,x17=x17,x18=x18,x19=x19,
                x11a=x11a,U7=U7,V7=V7,U8=U8,V8=V8,U9=U9,V9=V9,U12=U12,
                v8=v8,v9=v9,v12=v12,r16=r16,r17=r17,r18=r18,r19=r19,t=t,rT=rT,
                U20=U20,U21=U21)

def constraints_sph(b, c, d, e, g, alpha, r=1.0):
    s = chain_sph(b, c, d, e, g, alpha, r)
    a = s['a']; C = mp.cos
    bb,cc,dd,ee,gg,rr = s['b'],s['c'],s['d'],s['e'],s['g'],s['r']
    def iso(A, x): return C(A) - C(2*x)/C(x)       # cos A - cos2x/cosx  (d=2)
    F = {}
    F[1]  = s['x11'] - s['x11a']
    F[2]  = a*dd - s['U7'] - s['rT']
    F[3]  = iso(s['V8'], s['x10'])
    F[4]  = iso(a*(cc+dd) + s['v9'] - s['v12'], s['x13'])
    F[5]  = s['x10'] - s['x13']
    F[6]  = iso(s['V7'], s['x7'])
    F[7]  = s['x18'] - s['x19']
    F[8]  = a*rr - s['r16']
    F[9]  = a*rr - s['r17']
    F[10] = a*(bb+cc-dd-2*gg) - s['v8']
    F[11] = a*(cc+dd) + s['v9'] - 2*s['v12'] - a*ee
    F[12] = s['x16'] - s['x17']
    F[13] = s['U7'] - (s['U20'] - s['v8'] + s['v12'])/2
    F[14] = s['v12'] - (s['U21'] - a*ee)/2
    F[15] = a*gg + (a*(dd+ee-cc) - s['U21'])/2
    F[16] = s['r16'] - s['r17']
    F[17] = s['r18'] - s['r19']
    F[18] = s['r16'] - s['r18']
    F[19] = s['r17'] - s['r19']
    F[20] = a*(cc - dd)
    return F

# order d_i: 2 for the cos-based isosceles trio, 1 for everything else
DI = {i: (2 if i in (3,4,6) else 1) for i in range(1,21)}

ARCS = ['x1','x2','x3','x4','x5','x6','x7','x8','x9','x10','x11','x12','x13',
        'x14','x16','x17','x18','x19','x11a','U7','U8','U9','U12','v8','v9',
        'v12','r16','r17','r18','r19','rT','U20','U21']

if __name__ == "__main__":
    GEN = (0.45, 0.22, 0.30, 0.47, 0.11)            # generic off-variety point
    ps = PLANE.chain(*GEN); pf = PLANE.constraints(*GEN)

    print("="*70)
    print("PART A  chain recovery:  max_i |x_i_sph/alpha - x_i_plane|  -> 0")
    print("="*70)
    for k in (-1,-2,-3,-4,-5):
        al = mp.mpf(10)**k
        s = chain_sph(*GEN, al)
        worst = max(abs(s[n]/al - _f(ps[n])) for n in ARCS)
        # t is an angle (not /alpha):
        dt = abs(s['t'] - _f(ps['t']))
        print(f"  alpha=1e{k:<3d}  max|arc/a - plane| = {mp.nstr(worst,4):>10}   |t_sph - t_plane| = {mp.nstr(dt,4)}")

    print("\n" + "="*70)
    print("PART B  constraint recovery:  F_i_sph / alpha^d_i -> F_i_plane (all 20)")
    print("="*70)
    al  = mp.mpf(10)**-3
    al2 = mp.mpf(10)**-4
    Fs  = constraints_sph(*GEN, al)
    Fs2 = constraints_sph(*GEN, al2)
    print(f"  point {GEN}, alpha=1e-3 (order auto-checked vs 1e-4)\n")
    print(f"  {'F':>3} {'d_i':>3} {'F_sph/a^d':>16} {'F_plane':>16} {'rel.err':>10} {'order chk':>10}")
    allok = True
    for i in range(1,21):
        di = DI[i]
        red = Fs[i]/al**di
        pl  = _f(pf[i])
        rel = abs(red - pl)/(abs(pl)+mp.mpf('1e-30'))
        # empirical order: F_sph(a)/F_sph(a/10) ~ 10^d
        ratio = Fs[i]/Fs2[i] if Fs2[i] != 0 else mp.mpf('nan')
        demp = mp.log(abs(ratio))/mp.log(10) if ratio==ratio else mp.mpf('nan')
        ok = rel < mp.mpf('1e-4')
        allok &= ok
        print(f"  F{i:<2} {di:>3} {mp.nstr(red,8):>16} {mp.nstr(pl,8):>16} "
              f"{mp.nstr(rel,3):>10} {mp.nstr(demp,4):>10} {'' if ok else '  <-CHECK'}")
    print("\n  ALL 20 CONSTRAINTS RECOVER THE PLANE ENGINE." if allok
          else "\n  SOME CONSTRAINTS DID NOT CONVERGE -> un-reduction error.")
