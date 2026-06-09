"""
Rao (1998) PLANE Sri Yantra: r->0 reduction of the spherical chain.
Reduction rules (Sec 6; verified by Rao to equal direct plane geometry):
  cos A = cos B / cos C        ->  A^2 = B^2 - C^2          (eq 6.6)
  cos A = cos B * cos C        ->  A^2 = B^2 + C^2          (eq 6.14, radial)
  tan X = [sin P/sin Q] tan Y  ->  X = (P/Q) Y              (eq 6.7)
  tan U = sin S/(Q+cos S)      ->  U = S/(Q+1)              (eq 6.10)
  Q = [sin P/sin Q'](tanA/tanB)->  Q = (P/Q')(A/B)          (eq 6.9)
  cos A - cos2x/cos x          ->  -A^2/2 + (3/2) x^2       (eq 6.13)
Variables: b,c,d,e,g  (5). r fixed (=1). h is not a variable in the plane form.
"""
import math
from math import sqrt, atan, tan

class DomainError(Exception):
    pass

def chain(b, c, d, e, g, r=1.0):
    S = {'r': r}
    x1 = sqrt(r*r - c*c)                       # (6.6)
    x2 = sqrt(r*r - d*d)
    x3 = (r-c)/(r+d) * x2                       # (6.7)
    x4 = (r-d)/(r+c) * x1
    x5 = b/(b+c+d) * x4                         # red. of (2.7)
    x6 = e/(c+d+e) * x3                         # red. of (2.8)
    # point 7
    S7 = d + g
    Q7 = (d+g)/(c+d) * (x5/x6)                  # (6.9)
    U7 = S7/(Q7 + 1.0)                          # (6.10)
    V7 = S7 - U7
    x7 = U7/(c+d) * x5                          # red. of (2.14)
    # point 8
    S8 = r + g
    Q8 = (d+g)/(r+c) * (x1/x6)                  # red. of (2.18)
    U8 = S8/(Q8 + 1.0)
    V8 = S8 - U8
    x8 = U8/(r+c) * x1
    v8 = r - U8 - d
    # more arcs
    x16 = (d+e+g)/(d+g) * x6                    # red. of corrected (2.22)
    x11 = (d+g)/(c+d) * x5                      # (2.23)
    x17 = (b+c+d)/(c+d) * x5                    # (2.24)
    # point 9
    S9 = r + d
    Q9 = (c+d)/(r+d) * (x2/x5)
    U9 = S9/(Q9 + 1.0)
    V9 = S9 - U9
    x9 = U9/(r+d) * x2
    v9 = r - U9 - c
    # points 10,18
    x10 = (b+c-g)/(b+c+d) * x4                  # (2.32)
    x18 = (b+c+d+v8)/(b+c+d) * x4               # (2.33)
    # point 12
    S12 = d + g + v8
    Q12 = (d+g+v8)/(d+g) * (x6/x10)
    U12 = S12/(Q12 + 1.0)
    x12 = U12/(d+g) * x6
    v12 = d + g - U12
    # point 14
    x14 = (U7+v8)/(d+g+v8) * x10
    # points 13,19
    x13 = (e+v12)/(c+d+e) * x3
    x19 = (c+d+e+v9)/(c+d+e) * x3
    # point 11a
    x11a = (v9+c-g)/(v9+c+d-v12) * x13
    # radial distances (Pythagoras, eq 6.14)
    r16 = sqrt((d+e)**2 + x16*x16)
    r17 = sqrt((b+c)**2 + x17*x17)
    r18 = sqrt((d+v8)**2 + x18*x18)
    r19 = sqrt((c+v9)**2 + x19*x19)
    # concentricity helpers (6.11, 6.12): keep tan(t)
    t  = atan((d+g-U7)/x7)                      # (6.11)
    rT = x7 * tan(t/2.0)                        # (6.12) tan(rT)=x7 tan(t/2), rT small
    # U20,U21 for F13,F14,F15
    S20 = c + d + v8 + v9
    Q20 = (c+d+v9-v12)/(d+g+v8) * (x10/x13)
    U20 = S20/(Q20 + 1.0)
    S21 = b + c + d + e
    Q21 = (b+c+d+v8)/(c+d+e+v9) * (x19/x18)    # (3.14b) corrected: x19/x18, not x10/x13
    U21 = S21/(Q21 + 1.0)
    S.update(dict(x1=x1,x2=x2,x3=x3,x4=x4,x5=x5,x6=x6,x7=x7,x8=x8,x9=x9,
                  x10=x10,x11=x11,x12=x12,x13=x13,x14=x14,x16=x16,x17=x17,
                  x18=x18,x19=x19,x11a=x11a,U7=U7,V7=V7,U8=U8,V8=V8,U9=U9,V9=V9,
                  U12=U12,v8=v8,v9=v9,v12=v12,r16=r16,r17=r17,r18=r18,r19=r19,
                  t=t,rT=rT,U20=U20,U21=U21))
    return S

def constraints(b, c, d, e, g, r=1.0):
    s = chain(b, c, d, e, g, r)
    F = {}
    F[1]  = s['x11'] - s['x11a']
    F[2]  = d - s['U7'] - s['rT']
    F[3]  = -(s['V8'])**2/2 + 1.5*s['x10']**2                  # (6.13), d+g+v8==V8
    F[4]  = -(c+d+s['v9']-s['v12'])**2/2 + 1.5*s['x13']**2     # reduced (3.4), corrected arg
    F[5]  = s['x10'] - s['x13']
    F[6]  = -(s['V7'])**2/2 + 1.5*s['x7']**2                   # reduced (3.6), d+g-U7==V7
    F[7]  = s['x18'] - s['x19']
    F[8]  = s['r'] - s['r16']
    F[9]  = s['r'] - s['r17']
    F[10] = b + c - d - 2*g - s['v8']
    F[11] = c + d + s['v9'] - 2*s['v12'] - e
    F[12] = s['x16'] - s['x17']
    F[13] = s['U7'] - (s['U20'] - s['v8'] + s['v12'])/2
    F[14] = s['v12'] - (s['U21'] - e)/2
    F[15] = g + (d + e - c - s['U21'])/2
    F[16] = s['r16'] - s['r17']
    F[17] = s['r18'] - s['r19']
    F[18] = s['r16'] - s['r18']
    F[19] = s['r17'] - s['r19']
    F[20] = c - d
    return F

# ---- Table 3 (plane constrained figures, r=1), p.224 ----
TABLE3 = [
    ((1,2,3,4,8),   (0.463752,0.223255,0.288990,0.488181,0.106157)),
    ((1,2,3,10,15), (0.456449,0.236967,0.282560,0.456267,0.104822)),  # tests F15
    ((1,2,4,5,10),  (0.438237,0.218371,0.269490,0.440182,0.096716)),
    ((1,2,5,6,19),  (0.467298,0.261224,0.304553,0.471512,0.120134)),
    ((1,2,6,14,19), (0.468710,0.257071,0.308200,0.480582,0.121790)),  # tests F14
    ((1,2,8,9,20),  (0.560659,0.279461,0.279461,0.513999,0.101410)),
]
PLANE_OPT = (0.482391,0.261039,0.287454,0.467384,0.108463)   # F1,F2 only

if __name__ == "__main__":
    print("Validation against Rao Table 3 (plane). Listed constraints should be ~0.\n")
    worst=0.0
    for cons,vals in TABLE3:
        F=constraints(*vals)
        res={k:F[k] for k in cons}
        w=max(abs(v) for v in res.values()); worst=max(worst,w)
        tag="OK " if w<1e-5 else "FAIL"
        print(f"[{tag}] {str(cons):16s} max|F|={w:.2e}   " +
              " ".join(f"F{k}={F[k]:+.1e}" for k in cons))
    # essential pair on plane optimum
    Fo=constraints(*PLANE_OPT)
    print(f"\nPlane optimum  F1={Fo[1]:+.2e}  F2={Fo[2]:+.2e}  (only F1,F2 imposed)")
    print(f"\nWorst residual across Table 3: {worst:.2e}")
