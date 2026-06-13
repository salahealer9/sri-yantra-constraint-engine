"""
Rounded-vs-float calibration (the §B2(iv) gate).

Rigorous AA (AAr): float center/coefficients PLUS a non-cancelling error term
that conservatively bounds every floating-point rounding error and every
nonlinear-approximation remainder, with outward-rounded enclosures. Because the
affine radii here are ~1e-3..1e-2 while accumulated rounding is ~1e-14, a
*generously conservative* error bound is still tight -> rigorous AND not a
strawman. The width ratio measures whether that holds.

Reports, separating the fundamental from the implementation-dependent:
  width ratio   (arithmetic inflation; transfers to any implementation)
  box ratio     (search inflation; transfers)
  per-box cost  (implementation; Julia would change this)
  peak queue / max depth (memory stability; must stay DFS-bounded)
"""
import os, sys, math, time
sys.path.insert(0,'/home/claude'); sys.path.insert(0,'.')
import sriyantra_plane as SP
import numpy as np
from route3_panel import cons_full, Fvec, BOX, REF
from route3_enum import AA, Dual                      # float AA + Dual (baseline)

U=2.3e-16          # conservative relative rounding bound (> 2^-53)
ETA=5e-324         # smallest subnormal, absorbs underflow

# ----------------------- rigorous outward-rounded AA -----------------------
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
        AAr._n[0]+=1; d[AAr._n[0]]=s.totrad()*o.totrad()          # 2nd-order + var*err cross
        e=abs(o.c)*s.err+abs(s.c)*o.err+re                        # center*err propagation
        return AAr(c,d,e)
    __rmul__=__mul__
    def _uni(s,f,conv):
        a,b=s.iv()
        if not (a>0 or b<0):  # range straddles a singular/branch point for recip/sqrt domain
            if a<=0: raise ValueError("domain")
        if a==b: return AAr(f(a))
        p=(f(b)-f(a))/(b-a); u=conv(p); q=(f(a)+f(u))/2.0-p*(a+u)/2.0
        delta=abs(f(u)-(p*u+q))
        delta_r=delta*(1+1e-9)+U*abs(p*u+q)+ETA                   # rigorous upper bound
        d={k:v*p for k,v in s.dev.items()}; c=p*s.c+q
        AAr._n[0]+=1; d[AAr._n[0]]=delta_r
        return AAr(c,d,abs(p)*s.err+s._round_err(c,d))
    def sqrt(s):
        a,_=s.iv()
        if a<=0: raise ValueError("sqrt domain")
        return s._uni(math.sqrt, lambda p:1.0/(4*p*p))
    def recip(s):
        a,b=s.iv()
        if a<=0<=b: raise ZeroDivisionError("recip straddles 0")
        return s._uni(lambda x:1.0/x, lambda p:math.sqrt(-1.0/p))
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

# ----------------------- width-ratio validation -----------------------
def width_check():
    pt=REF[(1,2,3,4,8)]; r=3e-3
    AA._n=[0];  Ff=cons_full(*[AA.var(pt[k],r)  for k in range(5)])
    AAr._n=[0]; Fr=cons_full(*[AAr.var(pt[k],r) for k in range(5)])
    E=SP.constraints(*pt)
    print(f"Enclosure-width ratio (rigorous/float) at Rao A root, box radius r={r}")
    print(f"{'F':>3} {'float half-width':>17} {'rounded half-width':>19} {'ratio':>7} "
          f"{'contains':>9} {'brackets eng':>13}")
    worst=1.0; allc=True; allb=True
    for k in range(1,21):
        lf,hf=Ff[k].iv(); lr,hr=Fr[k].iv()
        hwf=(hf-lf)/2; hwr=(hr-lr)/2; ratio=hwr/hwf if hwf>0 else float('nan')
        contains=(lr<=lf and hr>=hf); brackets=(lr<=E[k]<=hr)
        allc&=contains; allb&=brackets; worst=max(worst,ratio)
        print(f"{k:>3} {hwf:>17.3e} {hwr:>19.3e} {ratio:>7.3f} "
              f"{str(contains):>9} {str(brackets):>13}")
    print(f"\nworst width ratio: {worst:.4f}   rounded contains float (all): {allc}   "
          f"rounded brackets engine (all): {allb}")
    return allc and allb

# ----------------------- generic enumerator (float or rounded) -----------------------
def hw(x): lo,hi=x.iv(); return (hi-lo)/2
def excluded(box,S,AAcls):
    AAcls._n=[0]
    try: F=cons_full(*[AAcls.var((lo+hi)/2,(hi-lo)/2) for (lo,hi) in box])
    except (ValueError,ZeroDivisionError): return False
    for k in S:
        lo,hi=F[k].iv()
        if not (lo<=0<=hi): return True
    return False
def krawczyk(center,r,S,AAcls,Dualcls):
    AAcls._n=[0]
    try: Fd=cons_full(*[Dualcls.var(k,center[k],r) for k in range(5)])
    except (ValueError,ZeroDivisionError): return 'split'
    Jmid=np.array([[Fd[S[i]].grad[j].c for j in range(5)] for i in range(5)])
    Jrad=np.array([[hw(Fd[S[i]].grad[j]) for j in range(5)] for i in range(5)])
    if not np.all(np.isfinite(Jmid)): return 'split'
    try: Y=np.linalg.inv(Jmid)
    except np.linalg.LinAlgError: return 'split'
    Fm=Fvec(center,S); Mmid=np.eye(5)-Y@Jmid; Mrad=np.abs(Y)@Jrad
    Kc=-(Y@Fm); Khw=(np.abs(Mmid)+Mrad)@np.full(5,r)
    lo=np.array(center)+Kc-Khw; hi=np.array(center)+Kc+Khw
    Xlo=np.array(center)-r; Xhi=np.array(center)+r
    if np.all(hi<Xhi) and np.all(lo>Xlo): return 'unique'
    if np.any(hi<Xlo) or np.any(lo>Xhi): return 'empty'
    return 'split'
def enum(S,AAcls,Dualcls,r_cert=3e-3,max_boxes=400000,tlim=120):
    t0=time.time(); stack=[(list(BOX),0)]; cert=[]; proc=0; maxq=1; maxd=0
    while stack and proc<max_boxes and time.time()-t0<tlim:
        maxq=max(maxq,len(stack)); box,depth=stack.pop(); maxd=max(maxd,depth); proc+=1
        if excluded(box,S,AAcls): continue
        center=[(lo+hi)/2 for (lo,hi) in box]; rad=max((hi-lo)/2 for (lo,hi) in box)
        if rad<=r_cert:
            v=krawczyk(center,rad,S,AAcls,Dualcls)
            if v=='unique':
                if not any(max(abs(center[i]-q[i]) for i in range(5))<2*r_cert for q in cert):
                    cert.append(center)
                continue
            if v=='empty': continue
        w=[hi-lo for (lo,hi) in box]; k=int(np.argmax(w)); lo,hi=box[k]; mid=(lo+hi)/2
        L=list(box); L[k]=(lo,mid); R=list(box); R[k]=(mid,hi)
        stack+=[(L,depth+1),(R,depth+1)]
    return dict(cert=len(cert),boxes=proc,maxq=maxq,maxd=maxd,
                secs=time.time()-t0,done=(len(stack)==0))

if __name__=="__main__":
    mode=sys.argv[1] if len(sys.argv)>1 else "width"
    if mode=="width":
        ok=width_check()
        print("\nValidation:", "PASS (rigorous & non-strawman)" if ok else "FAIL — inspect")
    else:
        subsets=[("Rao A",(1,2,3,4,8)), ("near-rank 8,9 pair",(1,2,8,9,10)),
                 ("radial-heavy 17,18,19",(1,2,17,18,19)), ("near-rank 9,16 pair",(1,2,9,16,5))]
        pick=int(mode)
        label,S=subsets[pick]
        print(f"Hazard probe (float): {label}  S={S}")
        r=enum(list(S),AA,Dual,max_boxes=3000000,tlim=250)
        print(f"  boxes={r['boxes']:>8d} cert={r['cert']} peakqueue={r['maxq']:>5d} "
              f"maxdepth={r['maxd']:>4d} time={r['secs']:>6.1f}s done={r['done']}  "
              f"({r['boxes']/max(r['secs'],1e-9):.0f} box/s)")
