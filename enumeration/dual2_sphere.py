"""
dual2_sphere.py — SECOND-ORDER dual (value, gradient, Hessian) over AAr, for rigorous
degree-2 Taylor enclosures. Each of val, grad[i], hess[i][j] is an AAr enclosing the
corresponding quantity over the box. Operation rules keep correlated second-order
structure (products carry through; remainders only where AAr itself introduces them).
Verified at a point (r=0) against finite-difference of the true constraint before use.
"""
import math
from aar import AAr
from chain_sphere import AA_FN as _A

N=6
def _z(): return AAr(0.0)

class D2:
    __slots__=('v','g','H')
    def __init__(s, v, g=None, H=None):
        s.v = v if isinstance(v,AAr) else AAr(v)
        s.g = g if g is not None else [_z() for _ in range(N)]
        s.H = H if H is not None else [[_z() for _ in range(N)] for _ in range(N)]
    @staticmethod
    def var(k, c, r):
        g=[_z() for _ in range(N)]; g[k]=AAr(1.0)
        return D2(AAr.var(c,r), g, None)
    @staticmethod
    def const(x):
        return D2(x if isinstance(x,AAr) else AAr(x))
    def __add__(s,o):
        o=s._c(o)
        return D2(s.v+o.v, [s.g[i]+o.g[i] for i in range(N)],
                  [[s.H[i][j]+o.H[i][j] for j in range(N)] for i in range(N)])
    __radd__=__add__
    def __sub__(s,o):
        o=s._c(o)
        return D2(s.v-o.v, [s.g[i]-o.g[i] for i in range(N)],
                  [[s.H[i][j]-o.H[i][j] for j in range(N)] for i in range(N)])
    def __rsub__(s,o): return s._c(o).__sub__(s)
    def __neg__(s):
        return D2(-s.v, [-s.g[i] for i in range(N)],
                  [[-s.H[i][j] for j in range(N)] for i in range(N)])
    def __mul__(s,o):
        o=s._c(o); v=s.v*o.v
        g=[s.g[i]*o.v + s.v*o.g[i] for i in range(N)]
        H=[[ s.H[i][j]*o.v + s.g[i]*o.g[j] + s.g[j]*o.g[i] + s.v*o.H[i][j]
             for j in range(N)] for i in range(N)]
        return D2(v,g,H)
    __rmul__=__mul__
    def _unary(s, f0, f1, f2):
        """f0=f(v), f1=f'(v), f2=f''(v)  (all AAr).  chain rule to 2nd order."""
        v=f0
        g=[f1*s.g[i] for i in range(N)]
        H=[[ f2*s.g[i]*s.g[j] + f1*s.H[i][j] for j in range(N)] for i in range(N)]
        return D2(v,g,H)
    def recip(s):
        iv=s.v.recip()          # 1/v
        f1=-(iv*iv)             # -1/v^2
        f2=2.0*iv*iv*iv         # 2/v^3
        return s._unary(iv,f1,f2)
    def __truediv__(s,o):
        o=s._c(o); return s*o.recip()
    def __rtruediv__(s,o): return s._c(o).__truediv__(s)
    def sin(s):
        sv=_A.sin(s.v); cv=_A.cos(s.v); return s._unary(sv, cv, -sv)
    def cos(s):
        cv=_A.cos(s.v); sv=_A.sin(s.v); return s._unary(cv, -sv, -cv)
    def tan(s):
        tv=_A.tan(s.v); sec2=AAr(1.0)+tv*tv; return s._unary(tv, sec2, 2.0*tv*sec2)
    def atan(s):
        av=_A.atan(s.v); den=AAr(1.0)+s.v*s.v
        f1=den.recip(); f2=(-2.0*s.v)*(f1*f1); return s._unary(av,f1,f2)
    def acos(s):
        ac=_A.acos(s.v); one_m=AAr(1.0)-s.v*s.v
        rt=one_m.sqrt(); f1=-(rt.recip())
        f2=-(s.v)*((one_m*rt).recip())     # -x/(1-x^2)^{3/2}
        return s._unary(ac,f1,f2)
    def _c(s,o): return o if isinstance(o,D2) else D2.const(o)

class _FN2:
    sin=staticmethod(lambda x: x.sin()); cos=staticmethod(lambda x: x.cos())
    tan=staticmethod(lambda x: x.tan()); atan=staticmethod(lambda x: x.atan())
    acos=staticmethod(lambda x: x.acos())
FN2=_FN2()
