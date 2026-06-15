# End-to-end route-3 enumeration for {1,2,3,4,8}: branch-and-prune with
#   (a) naive-interval EXCLUSION to discard empty regions (cheap), and
#   (b) AA-Krawczyk CERTIFICATION (tight Jacobian) to certify unique real roots.
# Answers the research question for this subset: how many real figures in the box,
# each with a uniqueness certificate. (Float-coeff AA => proof-of-principle rigor;
# production rigor = rounded AA / TaylorModels.jl. Contraction margins are huge,
# so FP rounding cannot flip the verdicts.)
import os, sys, math, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, '.')
import sriyantra_plane as SP
import numpy as np
from route3_probe import cons_iv, boxiv          # guarded import: naive interval chain

# ---------- affine arithmetic ----------
class AA:
    _n=[0]
    def __init__(s,c,dev=None): s.c=float(c); s.dev=dev or {}
    @staticmethod
    def var(c,r): AA._n[0]+=1; return AA(c,{AA._n[0]:float(r)})
    def rad(s): return sum(abs(v) for v in s.dev.values())
    def iv(s): r=s.rad(); return (s.c-r,s.c+r)
    def __add__(s,o):
        if not isinstance(o,AA): return AA(s.c+o,dict(s.dev))
        d=dict(s.dev)
        for k,v in o.dev.items(): d[k]=d.get(k,0.0)+v
        return AA(s.c+o.c,d)
    __radd__=__add__
    def __sub__(s,o):
        if not isinstance(o,AA): return AA(s.c-o,dict(s.dev))
        d=dict(s.dev)
        for k,v in o.dev.items(): d[k]=d.get(k,0.0)-v
        return AA(s.c-o.c,d)
    def __rsub__(s,o): return AA(o).__sub__(s)
    def __neg__(s): return AA(-s.c,{k:-v for k,v in s.dev.items()})
    def __mul__(s,o):
        if not isinstance(o,AA): return AA(s.c*o,{k:v*o for k,v in s.dev.items()})
        d={}
        for k,v in s.dev.items(): d[k]=d.get(k,0.0)+v*o.c
        for k,v in o.dev.items(): d[k]=d.get(k,0.0)+v*s.c
        AA._n[0]+=1; d[AA._n[0]]=s.rad()*o.rad()
        return AA(s.c*o.c,d)
    __rmul__=__mul__
    def _uni(s,f,conv):
        a,b=s.iv()
        if a==b: return AA(f(a))
        p=(f(b)-f(a))/(b-a); u=conv(p); q=(f(a)+f(u))/2-p*(a+u)/2
        delta=abs(f(u)-(p*u+q))
        d={k:v*p for k,v in s.dev.items()}; AA._n[0]+=1; d[AA._n[0]]=delta
        return AA(p*s.c+q,d)
    def sqrt(s): return s._uni(math.sqrt, lambda p:1.0/(4*p*p))
    def recip(s): return s._uni(lambda x:1.0/x, lambda p:math.sqrt(-1.0/p))
    def __truediv__(s,o): return s*(o.recip() if isinstance(o,AA) else 1.0/o)
    def __rtruediv__(s,o): return AA(o)*s.recip()

class Dual:
    def __init__(s,val,grad): s.val=val; s.grad=grad
    @staticmethod
    def const(x): return Dual(x if isinstance(x,AA) else AA(x),[AA(0.0)]*5)
    @staticmethod
    def var(k,c,r):
        g=[AA(0.0) for _ in range(5)]; g[k]=AA(1.0); return Dual(AA.var(c,r),g)
    def __add__(s,o):
        o=o if isinstance(o,Dual) else Dual.const(o)
        return Dual(s.val+o.val,[s.grad[j]+o.grad[j] for j in range(5)])
    __radd__=__add__
    def __sub__(s,o):
        o=o if isinstance(o,Dual) else Dual.const(o)
        return Dual(s.val-o.val,[s.grad[j]-o.grad[j] for j in range(5)])
    def __rsub__(s,o): return Dual.const(o).__sub__(s)
    def __mul__(s,o):
        o=o if isinstance(o,Dual) else Dual.const(o)
        return Dual(s.val*o.val,[s.grad[j]*o.val+s.val*o.grad[j] for j in range(5)])
    __rmul__=__mul__
    def __truediv__(s,o):
        o=o if isinstance(o,Dual) else Dual.const(o); q=s.val/o.val
        return Dual(q,[(s.grad[j]-q*o.grad[j])/o.val for j in range(5)])
    def __rtruediv__(s,o): return Dual.const(o).__truediv__(s)
    def sqrt(s):
        sv=s.val.sqrt(); return Dual(sv,[s.grad[j]/(sv*2.0) for j in range(5)])

def chain_dual(b,c,d,e,g):
    one=Dual.const(1.0); H=1.5
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
    return [x11-x11a, d-U7-rT, H*x10*x10-(V8*V8)*0.5,
            H*x13*x13-((c+d+v9-v12)*(c+d+v9-v12))*0.5, one-r16]

def chain_AA(b,c,d,e,g):                # plain-AA (no gradients) for tight exclusion
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
    return [x11-x11a, d-U7-rT, H*x10*x10-(V8*V8)*0.5,
            H*x13*x13-((c+d+v9-v12)*(c+d+v9-v12))*0.5, one-r16]

cons=[1,2,3,4,8]
def Fvec(p): F=SP.constraints(*p); return np.array([F[k] for k in cons])

def krawczyk(center, r):
    """returns 'unique' | 'empty' | 'split' for box center±r."""
    AA._n=[0]
    Fd=chain_dual(*[Dual.var(k,center[k],r) for k in range(5)])
    Jmid=np.array([[Fd[i].grad[j].c for j in range(5)] for i in range(5)])
    Jrad=np.array([[Fd[i].grad[j].rad() for j in range(5)] for i in range(5)])
    try: Y=np.linalg.inv(Jmid)
    except np.linalg.LinAlgError: return 'split'
    Fm=Fvec(center)
    Mmid=np.eye(5)-Y@Jmid; Mrad=np.abs(Y)@Jrad
    Kc=-(Y@Fm); Khw=(np.abs(Mmid)+Mrad)@np.full(5,r)
    lo=np.array(center)+Kc-Khw; hi=np.array(center)+Kc+Khw
    Xlo=np.array(center)-r; Xhi=np.array(center)+r
    if np.all(hi<Xhi) and np.all(lo>Xlo): return 'unique'
    if np.any(hi<Xlo) or np.any(lo>Xhi): return 'empty'
    return 'split'

def excluded(box):
    AA._n=[0]
    try:
        F=chain_AA(*[AA.var((lo+hi)/2,(hi-lo)/2) for (lo,hi) in box])
    except (ValueError, ZeroDivisionError):
        return False                     # can't enclose (e.g. range crosses sqrt domain): keep
    for I in F:
        lo,hi=I.iv()
        if not (lo<=0<=hi): return True
    return False

def enumerate_box(box0, r_cert=3e-3, max_boxes=400000, tlim=240):
    t0=time.time(); stack=[box0]; certified=[]; processed=0; maxq=1
    while stack and processed<max_boxes and time.time()-t0<tlim:
        maxq=max(maxq,len(stack)); box=stack.pop(); processed+=1
        if excluded(box): continue
        center=[(lo+hi)/2 for (lo,hi) in box]
        rad=max((hi-lo)/2 for (lo,hi) in box)
        if rad<=r_cert:
            v=krawczyk(center, rad)
            if v=='unique':
                if not any(max(abs(center[i]-c[i]) for i in range(5))<2*r_cert for c in certified):
                    certified.append(center)
                continue
            if v=='empty': continue
        # subdivide widest
        w=[hi-lo for (lo,hi) in box]; k=int(np.argmax(w)); lo,hi=box[k]; mid=(lo+hi)/2
        L=list(box); L[k]=(lo,mid); R=list(box); R[k]=(mid,hi); stack+=[L,R]
    return certified, processed, maxq, time.time()-t0, len(stack)

if __name__=="__main__":
    box0=[(0.20,0.80),(0.10,0.45),(0.15,0.45),(0.25,0.75),(0.03,0.25)]
    print("Route-3 ENUMERATION, subset {1,2,3,4,8}, box "
          "b[.20,.80] c[.10,.45] d[.15,.45] e[.25,.75] g[.03,.25]\n")
    cert,proc,maxq,secs,rem=enumerate_box(box0)
    print(f"boxes processed: {proc}   max queue: {maxq}   "
          f"time: {secs:.1f}s   remaining: {rem}")
    print(f"CERTIFIED unique real roots in box: {len(cert)}")
    rao=[0.463752,0.223255,0.288990,0.488181,0.106157]
    for c in cert:
        Fres=np.max(np.abs(Fvec(c)))
        tag="  <- Rao" if max(abs(c[i]-rao[i]) for i in range(5))<0.01 else ""
        print(f"   (b,c,d,e,g)=({', '.join(f'{v:.5f}' for v in c)})  |F|max={Fres:.1e}{tag}")
    print("\n(each = a certified-unique real figure; 'remaining=0' => complete over the box.)")
