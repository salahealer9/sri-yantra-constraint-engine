# Minimal affine arithmetic (diagnostic, float; rigor would use rounded AA / TaylorModels.jl).
# Goal: show the SCALE-INVARIANT ~10-15x first-order overestimation collapses to O(r^2)
# under AA -> Krawczyk-style certification becomes feasible. Also extract the Jacobian
# directly from AA linear coefficients and check vs the finite-difference Jacobian.
import os, sys, math
sys.path.insert(0,'/home/claude'); sys.path.insert(0,'.')
import sriyantra_plane as SP
import numpy as np

class AA:
    _n=[0]
    def __init__(s,c,dev=None): s.c=float(c); s.dev=dev or {}
    @staticmethod
    def var(c,r):
        AA._n[0]+=1; return AA(c,{AA._n[0]:float(r)})
    def rad(s): return sum(abs(v) for v in s.dev.values())
    def iv(s): r=s.rad(); return (s.c-r,s.c+r)
    def _bin(s,o,fc):
        o=o if isinstance(o,AA) else AA(o); d=dict(s.dev)
        for k,v in o.dev.items(): d[k]=d.get(k,0.0)+ (v if fc=='+' else -v)
        return d,o
    def __add__(s,o):
        if not isinstance(o,AA): return AA(s.c+o,dict(s.dev))
        d,_=s._bin(o,'+'); return AA(s.c+o.c,d)
    __radd__=__add__
    def __sub__(s,o):
        if not isinstance(o,AA): return AA(s.c-o,dict(s.dev))
        d,_=s._bin(o,'-'); return AA(s.c-o.c,d)
    def __rsub__(s,o): return (AA(o)-s) if not isinstance(o,AA) else o-s
    def __neg__(s): return AA(-s.c,{k:-v for k,v in s.dev.items()})
    def __mul__(s,o):
        if not isinstance(o,AA):
            return AA(s.c*o,{k:v*o for k,v in s.dev.items()})
        d={}
        for k,v in s.dev.items(): d[k]=d.get(k,0.0)+v*o.c
        for k,v in o.dev.items(): d[k]=d.get(k,0.0)+v*s.c
        cross=s.rad()*o.rad()                      # nonlinear remainder -> new symbol
        AA._n[0]+=1; d[AA._n[0]]=cross
        return AA(s.c*o.c,d)
    __rmul__=__mul__
    def _affine_uni(s,f,fp,conv):
        a,b=s.iv()
        if a==b: return AA(f(a))
        p=(f(b)-f(a))/(b-a)
        # min-max (Chebyshev) affine approx; u where f'(u)=p
        u=conv(p)
        q=(f(a)+f(u))/2 - p*(a+u)/2
        delta=abs(f(u)-(p*u+q))
        d={k:v*p for k,v in s.dev.items()}
        AA._n[0]+=1; d[AA._n[0]]=delta
        return AA(p*s.c+q,d)
    def sqrt(s):
        return s._affine_uni(math.sqrt, lambda x:0.5/math.sqrt(x),
                             lambda p: 1.0/(4*p*p))      # f'(u)=p => u=1/(4p^2)
    def recip(s):
        a,b=s.iv()
        return s._affine_uni(lambda x:1.0/x, lambda x:-1.0/(x*x),
                             lambda p: math.sqrt(-1.0/p))  # u where -1/u^2=p
    def __truediv__(s,o):
        return s* (o.recip() if isinstance(o,AA) else (1.0/o))
    def __rtruediv__(s,o): return AA(o)*s.recip()

def chain_AA(b,c,d,e,g):
    one=1.0; H=1.5
    x1=(one-c*c).sqrt(); x2=(one-d*d).sqrt()
    x3=(one-c)/(one+d)*x2; x4=(one-d)/(one+c)*x1
    x5=b/(b+c+d)*x4; x6=e/(c+d+e)*x3
    Q7=(d+g)/(c+d)*(x5/x6); U7=(d+g)/(Q7+one); V7=(d+g)-U7
    x7=U7/(c+d)*x5; w=(x7*x7+V7*V7).sqrt(); rT=x7*(w-x7)/V7
    Q8=(d+g)/(one+c)*(x1/x6); U8=(one+g)/(Q8+one); V8=(one+g)-U8
    v8=one-U8-d; x16=(d+e+g)/(d+g)*x6; x11=(d+g)/(c+d)*x5
    Q9=(c+d)/(one+d)*(x2/x5); U9=(one+d)/(Q9+one); v9=one-U9-c
    x10=(b+c-g)/(b+c+d)*x4
    S12=d+g+v8; Q12=S12/(d+g)*(x6/x10); U12=S12/(Q12+one); v12=d+g-U12
    x13=(e+v12)/(c+d+e)*x3; x11a=(v9+c-g)/(v9+c+d-v12)*x13
    r16=((d+e)*(d+e)+x16*x16).sqrt()
    F1=x11-x11a; F2=d-U7-rT; F3=-(V8*V8)*0.5+H*x10*x10
    F4=-((c+d+v9-v12)*(c+d+v9-v12))*0.5+H*x13*x13; F8=one-r16
    return [F1,F2,F3,F4,F8]

rao=[0.463752,0.223255,0.288990,0.488181,0.106157]; cons=[1,2,3,4,8]
def Fvec(p): F=SP.constraints(*p); return np.array([F[k] for k in cons])
def Jfd(h=1e-6):
    M=np.zeros((5,5))
    for j in range(5):
        pp=list(rao);pm=list(rao);pp[j]+=h;pm[j]-=h
        M[:,j]=(Fvec(pp)-Fvec(pm))/(2*h)
    return M
Jm=Jfd()

print("AA overestimation vs naive (true half-width ~ sum_j|J_ij|*r):\n")
from route3_probe import cons_iv, boxiv
for r in (1e-3,3e-3,1e-2):
    AA._n=[0]
    vs=[AA.var(v,r) for v in rao]
    Fa=chain_AA(*vs)
    Fn=cons_iv(*boxiv([(v-r,v+r) for v in rao]))
    print(f"r={r:.0e}:")
    for i,k in enumerate(cons):
        aa_hw=Fa[i].rad(); nv_hw=(float(Fn[i].b)-float(Fn[i].a))/2
        tr=float(np.sum(np.abs(Jm[i]))*r)
        print(f"   F{k}: AA x{aa_hw/tr:5.2f}   naive x{nv_hw/tr:6.1f}   (true~{tr:.2e})")
    print()
print("scale check: AA overestimation should shrink toward 1 as r->0 (O(r^2) remainder),")
print("unlike the constant ~10-15x of naive arithmetic.\n")

# Jacobian from AA linear coefficients (symbols 1..5 are the seeded inputs at r)
AA._n=[0]; r=1e-3; vs=[AA.var(v,r) for v in rao]; Fa=chain_AA(*vs)
syms=[id_ for id_ in range(1,6)]
Jaa=np.array([[Fa[i].dev.get(syms[j],0.0)/r for j in range(5)] for i in range(5)])
print("max |J_AA - J_fd| =", np.max(np.abs(Jaa-Jm)), " (AA recovers the Jacobian)")
