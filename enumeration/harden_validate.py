# Validate hardened AAr: rigorous (contains truth) AND tight (not a strawman).
import os,sys,math,random
sys.path.insert(0,'/home/claude'); sys.path.insert(0,'.')
import numpy as np, sriyantra_plane as SP
from aar import AAr
from route3_panel import cons_full
from route3_enum import AA          # float AA baseline
random.seed(1)

# ---- Test 1: scalar remainder rigour + tightness (sqrt, recip) ----
def scalar_test(name, mk_aar, ftrue, n=4000, samples=400):
    worst_over=0.0; escapes=0; loose=0.0
    for _ in range(n):
        c=random.uniform(0.05,3.0); r=random.uniform(1e-4,0.4*c)
        x=AAr.var(c,r); y=mk_aar(x); lo,hi=y.iv()
        a,b=c-r,c+r
        tr=[ftrue(a+ (b-a)*i/samples) for i in range(samples+1)]
        tlo,thi=min(tr),max(tr)
        for t in (a+ (b-a)*i/samples for i in range(samples+1)):
            v=ftrue(t)
            if not (lo<=v<=hi): escapes+=1
        over=(hi-lo)/((thi-tlo) if thi>tlo else 1e-30)
        worst_over=max(worst_over,over)
    print(f"  {name:8s}: escapes={escapes} (must be 0)   worst width/true-range={worst_over:.3f}")
    return escapes

e1=scalar_test("sqrt", lambda x:x.sqrt(), math.sqrt)
e2=scalar_test("recip", lambda x:x.recip(), lambda t:1.0/t)

# ---- Test 2: full-chain rigorous containment (Monte-Carlo, zero escapes) ----
def chain_contain(center, r, N=20000):
    AAr._n=[0]
    F=cons_full(*[AAr.var(center[k],r) for k in range(5)])
    enc={k:F[k].iv() for k in range(1,21)}
    esc=0; checked=0
    for _ in range(N):
        p=[center[k]+random.uniform(-r,r) for k in range(5)]
        try: E=SP.constraints(*p)
        except Exception: continue
        checked+=1
        for k in range(1,21):
            lo,hi=enc[k]
            if not (lo<=E[k]<=hi): esc+=1
    return esc, checked
rao=[0.463752,0.223255,0.288990,0.488181,0.106157]
for r in (3e-3, 1e-2):
    esc,chk=chain_contain(rao,r)
    print(f"  chain containment @ r={r}: {esc} escapes over {chk} samples x 20 constraints "
          f"({'PASS' if esc==0 else 'FAIL'})")

# ---- Test 3: width ratio vs float (still ~1, not inflated) ----
AA._n=[0];  Ff=cons_full(*[AA.var(rao[k],3e-3)  for k in range(5)])
AAr._n=[0]; Fr=cons_full(*[AAr.var(rao[k],3e-3) for k in range(5)])
ratios=[]
for k in range(1,21):
    lf,hf=Ff[k].iv(); lr,hr=Fr[k].iv()
    ratios.append((hr-lr)/(hf-lf))
print(f"  width ratio (hardened/float) over 20 constraints: "
      f"min {min(ratios):.4f}  max {max(ratios):.4f}")

# ---- Test 4: mpmath.iv independent ground-truth cross-check (sqrt) ----
import mpmath as mp
mp.mp.prec=80
ok=True
for _ in range(2000):
    c=random.uniform(0.05,3.0); r=random.uniform(1e-4,0.4*c)
    y=AAr.var(c,r).sqrt(); lo,hi=y.iv()
    iv=mp.iv.sqrt(mp.iv.mpf([c-r,c+r]))      # rigorous true-range superset
    if not (lo<=float(iv.a) and hi>=float(iv.b)): ok=False; break
print(f"  mpmath.iv cross-check (AAr contains rigorous sqrt range): {'PASS' if ok else 'FAIL'}")
print(f"\nVERDICT: {'HARDENED AAr rigorous & tight' if (e1==0 and e2==0 and ok) else 'INSPECT'}")
