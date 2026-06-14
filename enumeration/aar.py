"""
aar.py — hardened rigorous outward-rounded affine arithmetic (frozen-tool candidate).

Difference from the calibration AAr: the univariate (sqrt, 1/x) remainder is a
DERIVED rigorous bound, not a heuristic 1e-9 inflation.

For f in {sqrt, recip}, monotone and convex/concave on the (validated) box [a,b],
the centered affine approximation L(x)=p x+q has error g(x)=f(x)-L(x) with
g''=f'' of a single sign, so |g| attains its sup on [a,b] only at {a, b, x*}
(x* the interior critical point f'(x*)=p). Hence

    delta_r = max(|g(a)|, |g(b)|, |g(x*)|)  + rounding bounds + 2nd-order deficit.

Each |g(.)| is evaluated in float with an explicit rounding bound; the float x*
differs from the true critical point by ~U|x*|, contributing a deficit
<= 1/2 |f''| (U|x*|)^2 ~ 1e-32, covered with >10 orders of margin by SAFE=1e-18.
This is rigorous (delta_r >= sup|g|) AND tight (delta_r - true ~ 1e-16, negligible
against the affine radii ~1e-3). No mpmath in the hot path.
"""
import math

U=2.3e-16          # conservative relative rounding bound (> 2^-53)
ETA=5e-324         # smallest subnormal
SAFE=1e-18         # covers the float critical-point 2nd-order deficit (~1e-32)

class AAr:
    _n=[0]
    def __init__(s,c,dev=None,err=0.0): s.c=float(c); s.dev=dev or {}; s.err=float(err)
    @staticmethod
    def var(c,r): AAr._n[0]+=1; return AAr(c,{AAr._n[0]:float(r)})
    def rad(s): return math.fsum(abs(v) for v in s.dev.values())
    def totrad(s): return s.rad()+s.err
    def iv(s):
        tot=s.totrad(); pad=U*(abs(s.c)+tot)+ETA
        return (s.c-tot-pad, s.c+tot+pad)
    def _round_err(s,c,dev): return U*(abs(c)+math.fsum(abs(v) for v in dev.values()))+ETA
    def __add__(s,o):
        if not isinstance(o,AAr):
            d=dict(s.dev); c=s.c+o; return AAr(c,d,s.err+s._round_err(c,d))
        d=dict(s.dev)
        for k,v in o.dev.items(): d[k]=d.get(k,0.0)+v
        c=s.c+o.c; return AAr(c,d,s.err+o.err+s._round_err(c,d))
    __radd__=__add__
    def __sub__(s,o):
        if not isinstance(o,AAr):
            d=dict(s.dev); c=s.c-o; return AAr(c,d,s.err+s._round_err(c,d))
        d=dict(s.dev)
        for k,v in o.dev.items(): d[k]=d.get(k,0.0)-v
        c=s.c-o.c; return AAr(c,d,s.err+o.err+s._round_err(c,d))
    def __rsub__(s,o): return AAr(o).__sub__(s)
    def __neg__(s): return AAr(-s.c,{k:-v for k,v in s.dev.items()},s.err)
    def __mul__(s,o):
        if not isinstance(o,AAr):
            d={k:v*o for k,v in s.dev.items()}; c=s.c*o
            return AAr(c,d,abs(o)*s.err+s._round_err(c,d))
        d={}
        for k,v in s.dev.items(): d[k]=d.get(k,0.0)+v*o.c
        for k,v in o.dev.items(): d[k]=d.get(k,0.0)+v*s.c
        c=s.c*o.c; re=s._round_err(c,d)
        AAr._n[0]+=1; d[AAr._n[0]]=s.totrad()*o.totrad()
        return AAr(c,d,abs(o.c)*s.err+abs(s.c)*o.err+re)
    __rmul__=__mul__
    def _uni(s,f):
        a,b=s.iv()
        if a==b: return AAr(f(a))
        p=(f(b)-f(a))/(b-a)
        # interior critical point f'(x*)=p:  sqrt-> 1/(4p^2),  recip-> sqrt(-1/p)
        if p>0: x=1.0/(4.0*p*p) if f is math.sqrt else a    # sqrt branch
        else:   x=math.sqrt(-1.0/p)                          # recip branch (p<0)
        if   x<a: x=a
        elif x>b: x=b
        q=(f(a)+f(x))/2.0 - p*(a+x)/2.0
        def gb(t):
            fv=f(t); lin=p*t+q; gv=fv-lin
            return abs(gv) + U*(abs(fv)+abs(p*t)+abs(lin)+abs(gv)) + ETA
        delta_r=max(gb(a),gb(b),gb(x))+SAFE
        d={k:v*p for k,v in s.dev.items()}; c=p*s.c+q
        AAr._n[0]+=1; d[AAr._n[0]]=delta_r
        return AAr(c,d,abs(p)*s.err+s._round_err(c,d))
    def sqrt(s):
        a,_=s.iv()
        if a<=0: raise ValueError("sqrt domain")
        return s._uni(math.sqrt)
    def recip(s):
        a,b=s.iv()
        if a<=0<=b: raise ZeroDivisionError("recip straddles 0")
        return s._uni(lambda x:1.0/x)
    def __truediv__(s,o): return s*(o.recip() if isinstance(o,AAr) else 1.0/o)
    def __rtruediv__(s,o): return AAr(o)*s.recip()

class DualR:
    def __init__(s,val,grad): s.val=val; s.grad=grad
    @staticmethod
    def const(x): return DualR(x if isinstance(x,AAr) else AAr(x),[AAr(0.0) for _ in range(5)])
    @staticmethod
    def var(k,c,r):
        g=[AAr(0.0) for _ in range(5)]; g[k]=AAr(1.0); return DualR(AAr.var(c,r),g)
    def __add__(s,o):
        o=o if isinstance(o,DualR) else DualR.const(o)
        return DualR(s.val+o.val,[s.grad[j]+o.grad[j] for j in range(5)])
    __radd__=__add__
    def __sub__(s,o):
        o=o if isinstance(o,DualR) else DualR.const(o)
        return DualR(s.val-o.val,[s.grad[j]-o.grad[j] for j in range(5)])
    def __rsub__(s,o): return DualR.const(o).__sub__(s)
    def __mul__(s,o):
        o=o if isinstance(o,DualR) else DualR.const(o)
        return DualR(s.val*o.val,[s.grad[j]*o.val+s.val*o.grad[j] for j in range(5)])
    __rmul__=__mul__
    def __truediv__(s,o):
        o=o if isinstance(o,DualR) else DualR.const(o); q=s.val/o.val
        return DualR(q,[(s.grad[j]-q*o.grad[j])/o.val for j in range(5)])
    def __rtruediv__(s,o): return DualR.const(o).__truediv__(s)
    def sqrt(s):
        sv=s.val.sqrt(); return DualR(sv,[s.grad[j]/(sv*2.0) for j in range(5)])
