"""
chain_sphere.py — Rao (1998) spherical chain + constraints, arithmetic-generic.

Mirrors sriyantra.py (the FROZEN census truth source) node-for-node, equation by
equation, same order, same r = pi/2 - h. Written once over a function-namespace
FN so the IDENTICAL code runs over:
  * AAr     (rigorous value enclosures, FN = AA_FN)     — for constraint exclusion
  * DualRS  (rigorous value + 6-var Jacobian, FN = DUAL_FN) — for AA-Krawczyk

Transcendentals come from aar_sphere (rigorous, with inflection/domain guards);
+,-,*,/ are the overloaded AAr / DualRS operators. A SplitNeeded / DomainError
raised by any node propagates to the caller (branch-and-prune splits/excludes the
box). Validated against sriyantra.py by the Gate-M point-agreement battery before
any exclusion claim (see harness_gate_m_chain.py).
"""
import math
import aar_sphere as _S
from aar import AAr
from aar_sphere import DualRS, SplitNeeded, DomainError

HALF_PI = math.pi / 2.0


class _FN:
    __slots__ = ("sin", "cos", "tan", "atan", "acos")
    def __init__(s, sin, cos, tan, atan, acos):
        s.sin = sin; s.cos = cos; s.tan = tan; s.atan = atan; s.acos = acos

AA_FN   = _FN(_S.aa_sin, _S.aa_cos, _S.aa_tan, _S.aa_atan, _S.aa_acos)
DUAL_FN = _FN(_S.d_sin,  _S.d_cos,  _S.d_tan,  _S.d_atan,  _S.d_acos)


def chain_sph(b, c, d, e, g, h, FN):
    """Full spherical chain, mirroring sriyantra.chain node-for-node.
    b..h are AAr or DualRS (matching FN). Returns dict of chain quantities."""
    sin, cos, tan, atan, acos = FN.sin, FN.cos, FN.tan, FN.atan, FN.acos
    r = HALF_PI - h                                    # r = pi/2 - h
    # base arcs
    x1 = acos(cos(r) / cos(c))                         # (2.3)
    x2 = acos(cos(r) / cos(d))                         # (2.4)
    x3 = atan(sin(r - c) / sin(r + d) * tan(x2))       # (2.5)
    x4 = atan(sin(r - d) / sin(r + c) * tan(x1))       # (2.6)
    x5 = atan(sin(b) / sin(b + c + d) * tan(x4))       # (2.7)
    x6 = atan(sin(e) / sin(c + d + e) * tan(x3))       # (2.8)
    # point 7
    S7 = d + g                                         # (2.9)
    Q7 = (sin(d + g) / sin(c + d)) * (tan(x5) / tan(x6))      # (2.12)
    U7 = atan(sin(S7) / (Q7 + cos(S7)))                # (2.13)
    V7 = S7 - U7
    x7 = atan(sin(U7) / sin(c + d) * tan(x5))          # (2.14)
    # point 8
    S8 = r + g                                         # (2.15)
    Q8 = (sin(d + g) / sin(r + c)) * (tan(x1) / tan(x6))      # (2.18)
    U8 = atan(sin(S8) / (Q8 + cos(S8)))                # (2.19)
    V8 = S8 - U8
    x8 = atan(sin(U8) / sin(r + c) * tan(x1))          # (2.20)
    v8 = r - U8 - d                                    # (2.21)
    # more base arcs
    x16 = atan(sin(d + e + g) / sin(d + g) * tan(x6))  # (2.22)
    x11 = atan(sin(d + g) / sin(c + d) * tan(x5))      # (2.23)
    x17 = atan(sin(b + c + d) / sin(c + d) * tan(x5))  # (2.24)
    # point 9
    S9 = r + d                                         # (2.25)
    Q9 = (sin(c + d) / sin(r + d)) * (tan(x2) / tan(x5))      # (2.28)
    U9 = atan(sin(S9) / (Q9 + cos(S9)))                # (2.29)
    V9 = S9 - U9
    x9 = atan(sin(U9) / sin(r + d) * tan(x2))          # (2.30)
    v9 = r - U9 - c                                    # (2.31)
    # points 10, 18
    x10 = atan(sin(b + c - g) / sin(b + c + d) * tan(x4))     # (2.32)
    x18 = atan(sin(b + c + d + v8) / sin(b + c + d) * tan(x4))# (2.33)
    # point 12
    S12 = d + g + v8                                    # (2.34)
    Q12 = (sin(d + g + v8) / sin(d + g)) * (tan(x6) / tan(x10))   # (2.37)
    U12 = atan(sin(S12) / (Q12 + cos(S12)))            # (2.38)
    x12 = atan(sin(U12) / sin(d + g) * tan(x6))        # (2.39)
    v12 = d + g - U12                                  # (2.40)
    # point 14
    x14 = atan(sin(U7 + v8) / sin(d + g + v8) * tan(x10))     # (2.41)
    # points 13, 19
    x13 = atan(sin(e + v12) / sin(c + d + e) * tan(x3))       # (2.42)
    x19 = atan(sin(c + d + e + v9) / sin(c + d + e) * tan(x3))# (2.43)
    # point 11a
    x11a = atan(sin(v9 + c - g) / sin(v9 + c + d - v12) * tan(x13))   # (2.44)
    # radial distances
    r16 = acos(cos(d + e) * cos(x16))                  # (3.8a)
    r17 = acos(cos(b + c) * cos(x17))                  # (3.9a)
    r18 = acos(cos(d + v8) * cos(x18))                 # (3.18a)
    r19 = acos(cos(c + v9) * cos(x19))                 # (3.18b)
    # concentricity helpers
    t  = atan(tan(d + g - U7) / sin(x7))               # (3.2b)
    rT = atan(sin(x7) * tan(t / 2))                    # (3.2c)
    # U20, U21
    S20 = c + d + v8 + v9                               # (3.13c)
    Q20 = (sin(c + d + v9 - v12) / sin(d + g + v8)) * (tan(x10) / tan(x13))  # (3.13b)
    U20 = atan(sin(S20) / (Q20 + cos(S20)))            # (3.13a)
    S21 = b + c + d + e                                 # (3.14c)
    Q21 = (sin(b + c + d + v8) / sin(c + d + e + v9)) * (tan(x19) / tan(x18))# (3.14b)
    U21 = atan(sin(S21) / (Q21 + cos(S21)))            # (3.14a)
    return dict(r=r, b=b, c=c, d=d, e=e, g=g,
                x1=x1, x2=x2, x3=x3, x4=x4, x5=x5, x6=x6, x7=x7, x8=x8, x9=x9,
                x10=x10, x11=x11, x12=x12, x13=x13, x14=x14, x16=x16, x17=x17,
                x18=x18, x19=x19, x11a=x11a,
                U7=U7, V7=V7, U8=U8, V8=V8, U9=U9, V9=V9, U12=U12,
                v8=v8, v9=v9, v12=v12, r16=r16, r17=r17, r18=r18, r19=r19,
                t=t, rT=rT, U20=U20, U21=U21)


def constraints_sph(b, c, d, e, g, h, FN, want=None):
    """Spherical constraints F_i, mirroring sriyantra.constraints.
    `want` (iterable of ints) restricts which F_i are built (the others are
    skipped to avoid unnecessary transcendental nodes); None = all 20.
    Returns {i: F_i}. Chain quantities are pulled from chain_sph."""
    sin, cos, tan, atan, acos = FN.sin, FN.cos, FN.tan, FN.atan, FN.acos
    s = chain_sph(b, c, d, e, g, h, FN)
    r = s['r']
    def iso(V, x): return cos(V) - cos(x * 2) / cos(x)   # cos V - cos2x/cosx
    W = set(range(1, 21)) if want is None else set(want)
    F = {}
    if 1  in W: F[1]  = s['x11'] - s['x11a']
    if 2  in W: F[2]  = d - s['U7'] - s['rT']
    if 3  in W: F[3]  = iso(s['V8'], s['x10'])
    if 4  in W: F[4]  = iso(c + d + s['v9'] - s['v12'], s['x13'])
    if 5  in W: F[5]  = s['x10'] - s['x13']
    if 6  in W: F[6]  = iso(d + g - s['U7'], s['x7'])
    if 7  in W: F[7]  = s['x18'] - s['x19']
    if 8  in W: F[8]  = r - s['r16']
    if 9  in W: F[9]  = r - s['r17']
    if 10 in W: F[10] = b + c - d - 2 * g - s['v8']
    if 11 in W: F[11] = c + d + s['v9'] - 2 * s['v12'] - e
    if 12 in W: F[12] = s['x16'] - s['x17']
    if 13 in W: F[13] = s['U7'] - (s['U20'] - s['v8'] + s['v12']) / 2
    if 14 in W: F[14] = s['v12'] - (s['U21'] - e) / 2
    if 15 in W: F[15] = g + (d + e - c - s['U21']) / 2
    if 16 in W: F[16] = s['r16'] - s['r17']
    if 17 in W: F[17] = s['r18'] - s['r19']
    if 18 in W: F[18] = s['r16'] - s['r18']
    if 19 in W: F[19] = s['r17'] - s['r19']
    if 20 in W: F[20] = c - d
    return F
