"""
Rao (1998) spherical Sri Yantra: construction chain + 20 constraint functions.
Transcribed directly from the paper's equations (2.2)-(2.44) and (3.1)-(3.20).
Basic variables: b, c, d, e, g, h  (radians).  r = pi/2 - h.

Goal of this file: VALIDATION. Evaluate the constraint functions at the
published Table 1 solution points and check the relevant Fn ~ 0.
"""
import math
from math import sin, cos, tan, atan, acos, pi

class DomainError(Exception):
    pass

def safe_acos(x):
    if x < -1.0 or x > 1.0:
        raise DomainError(f"acos arg {x}")
    return acos(x)

def chain(b, c, d, e, g, h):
    """Return dict of all intermediate quantities."""
    r = pi/2 - h
    S = {}
    S['r'] = r
    # base arcs
    x1 = safe_acos(cos(r)/cos(c))                      # (2.3)
    x2 = safe_acos(cos(r)/cos(d))                      # (2.4)
    x3 = atan(sin(r-c)/sin(r+d) * tan(x2))             # (2.5)
    x4 = atan(sin(r-d)/sin(r+c) * tan(x1))             # (2.6)
    x5 = atan(sin(b)/sin(b+c+d) * tan(x4))             # (2.7)
    x6 = atan(sin(e)/sin(c+d+e) * tan(x3))             # (2.8)
    # point 7
    S7 = d + g                                         # (2.9)
    Q7 = (sin(d+g)/sin(c+d)) * (tan(x5)/tan(x6))       # (2.12)
    U7 = atan(sin(S7)/(Q7 + cos(S7)))                  # (2.13)
    V7 = S7 - U7
    x7 = atan(sin(U7)/sin(c+d) * tan(x5))              # (2.14)
    # point 8
    S8 = r + g                                         # (2.15)
    Q8 = (sin(d+g)/sin(r+c)) * (tan(x1)/tan(x6))       # (2.18) [labelled Q7 in paper; typo]
    U8 = atan(sin(S8)/(Q8 + cos(S8)))                  # (2.19)
    V8 = S8 - U8
    x8 = atan(sin(U8)/sin(r+c) * tan(x1))              # (2.20)
    v8 = r - U8 - d                                    # (2.21)
    # more base arcs
    x16 = atan(sin(d+e+g)/sin(d+g) * tan(x6))          # (2.22) [paper's sin(r+c) is a misprint]
    x11 = atan(sin(d+g)/sin(c+d) * tan(x5))            # (2.23)
    x17 = atan(sin(b+c+d)/sin(c+d) * tan(x5))          # (2.24)
    # point 9
    S9 = r + d                                         # (2.25)
    Q9 = (sin(c+d)/sin(r+d)) * (tan(x2)/tan(x5))       # (2.28)
    U9 = atan(sin(S9)/(Q9 + cos(S9)))                  # (2.29)
    V9 = S9 - U9
    x9 = atan(sin(U9)/sin(r+d) * tan(x2))              # (2.30)
    v9 = r - U9 - c                                    # (2.31)
    # points 10, 18
    x10 = atan(sin(b+c-g)/sin(b+c+d) * tan(x4))        # (2.32)
    x18 = atan(sin(b+c+d+v8)/sin(b+c+d) * tan(x4))     # (2.33)
    # point 12
    S12 = d + g + v8                                    # (2.34)
    Q12 = (sin(d+g+v8)/sin(d+g)) * (tan(x6)/tan(x10))  # (2.37)
    U12 = atan(sin(S12)/(Q12 + cos(S12)))              # (2.38)
    x12 = atan(sin(U12)/sin(d+g) * tan(x6))            # (2.39)
    v12 = d + g - U12                                  # (2.40)
    # point 14
    x14 = atan(sin(U7+v8)/sin(d+g+v8) * tan(x10))      # (2.41)
    # points 13, 19
    x13 = atan(sin(e+v12)/sin(c+d+e) * tan(x3))        # (2.42)
    x19 = atan(sin(c+d+e+v9)/sin(c+d+e) * tan(x3))     # (2.43)
    # point 11a
    x11a = atan(sin(v9+c-g)/sin(v9+c+d-v12) * tan(x13))  # (2.44)

    # radial distances
    r16 = safe_acos(cos(d+e)*cos(x16))                 # (3.8a)
    r17 = safe_acos(cos(b+c)*cos(x17))                 # (3.9a)
    r18 = safe_acos(cos(d+v8)*cos(x18))                # (3.18a) [y8 := v8]
    r19 = safe_acos(cos(c+v9)*cos(x19))                # (3.18b) [y9 := v9]

    # concentricity helpers
    t   = atan(tan(d+g-U7)/sin(x7))                    # (3.2b)
    rT  = atan(sin(x7)*tan(t/2))                        # (3.2c)

    # U20, U21 for F13, F14
    S20 = c + d + v8 + v9                               # (3.13c)
    Q20 = (sin(c+d+v9-v12)/sin(d+g+v8))*(tan(x10)/tan(x13))  # (3.13b)
    U20 = atan(sin(S20)/(Q20 + cos(S20)))              # (3.13a)
    S21 = b + c + d + e                                 # (3.14c)
    Q21 = (sin(b+c+d+v8)/sin(c+d+e+v9))*(tan(x19)/tan(x18))  # (3.14b) corrected: x19/x18, not x10/x13
    U21 = atan(sin(S21)/(Q21 + cos(S21)))              # (3.14a)

    S.update(dict(x1=x1,x2=x2,x3=x3,x4=x4,x5=x5,x6=x6,x7=x7,x8=x8,x9=x9,
                  x10=x10,x11=x11,x12=x12,x13=x13,x14=x14,x16=x16,x17=x17,
                  x18=x18,x19=x19,x11a=x11a,
                  U7=U7,V7=V7,U8=U8,V8=V8,U9=U9,V9=V9,U12=U12,v8=v8,v9=v9,v12=v12,
                  r16=r16,r17=r17,r18=r18,r19=r19,t=t,rT=rT,U20=U20,U21=U21))
    return S

def constraints(b, c, d, e, g, h):
    s = chain(b, c, d, e, g, h)
    r = s['r']
    F = {}
    F[1]  = s['x11'] - s['x11a']                                    # (3.1)
    F[2]  = d - s['U7'] - s['rT']                                   # (3.2)
    F[3]  = cos(s['V8']) - cos(2*s['x10'])/cos(s['x10'])            # (3.3) [d+g+v8 == V8]
    F[4]  = cos(c+d+s['v9']-s['v12']) - cos(2*s['x13'])/cos(s['x13'])  # (3.4) [paper's +g is spurious]
    F[5]  = s['x10'] - s['x13']                                     # (3.5)
    F[6]  = cos(d+g-s['U7']) - cos(2*s['x7'])/cos(s['x7'])          # (3.6)
    F[7]  = s['x18'] - s['x19']                                     # (3.7)
    F[8]  = r - s['r16']                                            # (3.8)
    F[9]  = r - s['r17']                                            # (3.9)
    F[10] = b + c - d - 2*g - s['v8']                               # (3.10)
    F[11] = c + d + s['v9'] - 2*s['v12'] - e                        # (3.11)
    F[12] = s['x16'] - s['x17']                                     # (3.12)
    F[13] = s['U7'] - (s['U20'] - s['v8'] + s['v12'])/2             # (3.13)
    F[14] = s['v12'] - (s['U21'] - e)/2                             # (3.14)
    F[15] = g + (d + e - c - s['U21'])/2                            # (3.15)
    F[16] = s['r16'] - s['r17']                                     # (3.16)
    F[17] = s['r18'] - s['r19']                                     # (3.17)
    F[18] = s['r16'] - s['r18']                                     # (3.18)
    F[19] = s['r17'] - s['r19']                                     # (3.19)
    F[20] = c - d                                                   # (3.20)
    return F

# ---- Table 1 (spherical constrained figures), p.218 ----
# (constraint set) : (b, c, d, e, g, h)
TABLE1 = [
    ((1,2,3,5,10,19),  (0.105036,0.054376,0.065419,0.105517,0.024275,1.344437)),
    ((1,2,3,6,16,19),  (0.450462,0.442391,0.445729,0.425478,0.183904,0.539209)),
    ((1,2,3,10,19,20), (0.244730,0.158369,0.158369,0.225411,0.060166,1.042990)),
    ((1,2,4,5,10,19),  (0.231687,0.120012,0.146680,0.230471,0.053009,1.076084)),
    ((1,2,4,8,13,19),  (0.463973,0.753761,0.890177,0.375039,0.466743,0.261736)),
    ((1,2,4,10,15,19), (0.252893,0.132925,0.160863,0.249384,0.057987,1.031951)),
    ((1,2,6,8,9,10),   (0.449590,0.332617,0.328263,0.430650,0.129804,0.722398)),
    ((1,2,8,9,16,19),  (0.543803,0.343194,0.361271,0.466999,0.107003,0.353166)),
]

if __name__ == "__main__":
    print("Validation against Rao Table 1 (spherical). For each row, the listed")
    print("constraints should evaluate to ~0 at the published solution.\n")
    worst_overall = 0.0
    for cons, vals in TABLE1:
        try:
            F = constraints(*vals)
            residuals = {k: F[k] for k in cons}
            worst = max(abs(v) for v in residuals.values())
            worst_overall = max(worst_overall, worst)
            status = "OK " if worst < 1e-5 else "FAIL"
            print(f"[{status}] constraints {str(cons):24s} max|F|={worst:.2e}")
            if worst >= 1e-5:
                for k,v in residuals.items():
                    print(f"          F{k} = {v:+.3e}")
        except DomainError as ex:
            print(f"[ERR ] constraints {str(cons):24s} domain error: {ex}")
    print(f"\nWorst residual across all rows: {worst_overall:.2e}")
