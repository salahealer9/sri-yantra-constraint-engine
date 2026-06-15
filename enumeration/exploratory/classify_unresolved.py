# Phase 2: collect the unresolved (depth-capped) boxes from {1,2,3,4,8} on box B
# and classify each: domain-seam / near-singular / near-solution / other.
import sys,time; 
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from aar import AAr, DualR
from plane_chain import cons_full, Fvec
import sriyantra_plane as eng

S5=[1,2,3,4,8]
BOXB=[(1e-6,0.788471),(1e-6,0.636399),(1e-6,0.635884),(1e-6,0.679513),(1e-6,0.687977)]

def must_pos(b,c,d,e,g):
    o=1.0; out=[('1-c^2',o-c*c),('1-d^2',o-d*d),('b+c-g',b+c-g)]
    try:
        x1=(o-c*c).sqrt(); x2=(o-d*d).sqrt(); x3=(o-c)/(o+d)*x2; x4=(o-d)/(o+c)*x1
        x5=b/(b+c+d)*x4; x6=e/(c+d+e)*x3
        Q8=(d+g)/(o+c)*(x1/x6); U8=(o+g)/(Q8+o); v8=o-U8-d
        Q9=(c+d)/(o+d)*(x2/x5); U9=(o+d)/(Q9+o); v9=o-U9-c
        x10=(b+c-g)/(b+c+d)*x4
        S12=d+g+v8; Q12=S12/(d+g)*(x6/x10); U12=S12/(Q12+o); v12=d+g-U12
        out+=[('v8',v8),('v9',v9),('v12',v12),('x10',x10),('v9+c+d-v12',v9+c+d-v12)]
    except (ValueError,ZeroDivisionError): pass
    return out
def domain_excluded(box):
    AAr._n=[0]
    for _,q in must_pos(*[AAr.var((lo+hi)/2,(hi-lo)/2) for (lo,hi) in box]):
        if q.iv()[1]<=0: return True
    return False
def excluded(box):
    AAr._n=[0]
    try: F=cons_full(*[AAr.var((lo+hi)/2,(hi-lo)/2) for (lo,hi) in box])
    except (ValueError,ZeroDivisionError): return False
    for k in S5:
        lo,hi=F[k].iv()
        if not (lo<=0<=hi): return True
    return False
def hw(x): lo,hi=x.iv(); return (hi-lo)/2
def krawczyk(center,r):
    AAr._n=[0]
    try: Fd=cons_full(*[DualR.var(k,center[k],r) for k in range(5)])
    except (ValueError,ZeroDivisionError): return 'split'
    Jm=np.array([[Fd[S5[i]].grad[j].c for j in range(5)] for i in range(5)])
    if not np.all(np.isfinite(Jm)): return 'split'
    Jr=np.array([[hw(Fd[S5[i]].grad[j]) for j in range(5)] for i in range(5)])
    try: Y=np.linalg.inv(Jm)
    except np.linalg.LinAlgError: return 'split'
    Fm=Fvec(center,S5); M=np.eye(5)-Y@Jm; Mr=np.abs(Y)@Jr
    Kc=-(Y@Fm); Kh=(np.abs(M)+Mr)@np.full(5,r)
    lo=np.array(center)+Kc-Kh; hi=np.array(center)+Kc+Kh
    Xl=np.array(center)-r; Xh=np.array(center)+r
    if np.all(hi<Xh) and np.all(lo>Xl): return 'unique'
    if np.any(hi<Xl) or np.any(lo>Xh): return 'empty'
    return 'split'

def enum_collect(tlim=120,max_depth=200,r_cert=3e-3,max_boxes=400000):
    t0=time.time(); stack=[(list(BOXB),0)]; proc=0; unres=[]
    while stack and proc<max_boxes and time.time()-t0<tlim:
        box,dep=stack.pop(); proc+=1
        if domain_excluded(box): continue
        if excluded(box): continue
        center=[(lo+hi)/2 for (lo,hi) in box]; rad=max((hi-lo)/2 for (lo,hi) in box)
        if rad<=r_cert:
            v=krawczyk(center,rad)
            if v in ('unique','empty'): continue
        if dep>=max_depth: unres.append((center,rad)); continue
        w=[hi-lo for (lo,hi) in box]; k=int(np.argmax(w)); lo,hi=box[k]; mid=(lo+hi)/2
        L=list(box); L[k]=(lo,mid); R=list(box); R[k]=(mid,hi); stack+=[(L,dep+1),(R,dep+1)]
    return unres,proc

print("Collecting unresolved boxes from {1,2,3,4,8} on box B ...")
unres,proc=enum_collect(); print(f"  processed={proc}  unresolved collected={len(unres)}\n")

def fdiff_jac(x):
    h=1e-7; F0=Fvec(x,S5); J=np.zeros((5,5))
    for j in range(5):
        xp=list(x); xp[j]+=h
        try: J[:,j]=(Fvec(xp,S5)-F0)/h
        except Exception: return None
    return J
def newton(x0,iters=60):
    x=np.array(x0,float)
    for _ in range(iters):
        try: F=Fvec(list(x),S5); J=fdiff_jac(list(x))
        except Exception: return None
        if J is None or not np.all(np.isfinite(F)): return None
        try: dx=np.linalg.solve(J,F)
        except np.linalg.LinAlgError: return None
        x=x-dx
        if np.linalg.norm(dx)<1e-13: 
            return x if np.all(np.isfinite(x)) else None
    return None
def inB(x): return all(BOXB[i][0]-1e-9<=x[i]<=BOXB[i][1]+1e-9 for i in range(5))

cats={'domain_seam':0,'near_singular':0,'near_solution':0,'other':0}
seam_q={}; roots=[]; examples={k:None for k in cats}
N=len(unres)
for center,rad in unres:
    b,c,d,e,g=center
    # sign quantities via float engine
    seam=None; minq=1e9
    try:
        s=eng.chain(b,c,d,e,g)
        qs={'b+c-g':b+c-g,'x10':s['x10'],'v8':s['v8'],'v9':s['v9'],'v12':s['v12'],
            'x6':s['x6'],'d+g':d+g,'c+d+e':c+d+e,'b+c+d':b+c+d,'v9+c+d-v12':s['v9']+c+d-s['v12']}
        for nm,val in qs.items():
            if abs(val)<minq: minq=abs(val); seam=nm
    except Exception:
        seam='chain_error'; minq=0.0
    # residual + jacobian cond
    try:
        F=Fvec(center,S5); res=np.linalg.norm(F); J=fdiff_jac(center)
        cond=np.linalg.cond(J) if J is not None else 1e30
    except Exception:
        res=1e9; cond=1e30
    cat=None
    if minq<5e-3:           cat='domain_seam'; seam_q[seam]=seam_q.get(seam,0)+1
    elif res<1e-3:          cat='near_solution'
    elif cond>1e6:          cat='near_singular'
    else:                   cat='other'
    cats[cat]+=1
    if examples[cat] is None: examples[cat]=(center,seam,round(minq,5),f"res={res:.1e}",f"cond={cond:.1e}")

print("=== Classification of unresolved boxes ===")
for k,v in cats.items(): print(f"  {k:14s}: {v:5d}  ({100*v/max(N,1):.0f}%)")
print(f"\n  domain_seam breakdown (which quantity is ~0): {dict(sorted(seam_q.items(),key=lambda x:-x[1]))}")

# Newton from a sample to see if genuine solutions hide in the unresolved set
print("\nNewton from a sample of unresolved centers (looking for roots in B):")
import random; random.seed(1); samp=random.sample(unres,min(400,N))
found=[]
for center,rad in samp:
    r=newton(center)
    if r is not None and inB(r):
        if not any(np.max(np.abs(r-q))<1e-5 for q in found): found.append(r)
print(f"  distinct roots found in B from {len(samp)} starts: {len(found)}")
rao=np.array([0.463752,0.223255,0.288990,0.488181,0.106157])
for r in found[:8]:
    tag=" <-Rao" if np.max(np.abs(r-rao))<1e-2 else ""
    print(f"    {[round(x,5) for x in r]}{tag}")
print("\nExamples per category:")
for k,ex in examples.items():
    if ex: print(f"  {k}: center={[round(x,4) for x in ex[0]]} nearest0={ex[1]}({ex[2]}) {ex[3]} {ex[4]}")
