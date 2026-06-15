# Gate M (Amendment-02 §B7; extended for Amendment-04 D7) — validates the FROZEN
# confirmatory tool: campaign.py + plane_chain.py + aar.py + admissibility.py.
# OFFICIAL run is POST-FREEZE on the frozen tree; this doubles as a dress rehearsal.
#   M1 soundness          : (a) rigorous AAr brackets the v0.1.0 engine on all 20
#                           constraints at reference rows + random valid figures;
#                           (b) the admissibility layer excludes no known real figure.
#   M2 two-way cross-check: campaign's AA-Krawczyk enumeration of {1,2,3,4,8} and
#                           multistart Newton agree, both containing Rao's Table-3 row.
import os,sys,random
HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,os.path.dirname(HERE)); sys.path.insert(0,HERE)
import numpy as np, sriyantra_plane as SP
from aar import AAr
from plane_chain import cons_full
from admissibility import domain_excluded
from campaign import enum_subset, BOX
from scipy.optimize import fsolve
import warnings; warnings.filterwarnings("ignore"); random.seed(7)

RAO={(1,2,3,4,8):(0.463752,0.223255,0.288990,0.488181,0.106157),
     (1,2,4,5,10):(0.438237,0.218371,0.269490,0.440182,0.096716),
     (1,2,6,14,19):(0.468710,0.257071,0.308200,0.480582,0.121790),
     (1,2,3,10,15):(0.456449,0.236967,0.282560,0.456267,0.104822)}

def m1():
    pts=[list(v) for v in RAO.values()]; got=0
    while got<300:
        p=[random.uniform(*BOX[i]) for i in range(5)]
        try: SP.constraints(*p)
        except Exception: continue
        pts.append(p); got+=1
    worst=0.0; esc=0
    for p in pts:
        try: E=SP.constraints(*p)
        except Exception: continue
        AAr._n=[0]; F=cons_full(*[AAr.var(p[k],1e-9) for k in range(5)])
        for k in range(1,21):
            lo,hi=F[k].iv(); worst=max(worst,(hi-lo)/2)
            if not (lo<=E[k]<=hi): esc+=1
    a=esc==0
    print(f"M1a engine-equivalence: {len(pts)} figures x 20 constraints, "
          f"escapes={esc}  max half-width={worst:.1e}  -> {'PASS' if a else 'FAIL'}")
    # M1b: admissibility must not exclude a known real figure
    r=2.5e-3; over=0
    for v in RAO.values():
        if domain_excluded([(x-r,x+r) for x in v]): over+=1
    b=over==0
    print(f"M1b admissibility soundness: {len(RAO)} real figures, "
          f"wrongly-excluded={over}  -> {'PASS' if b else 'FAIL'}")
    return a and b

def m2():
    S=(1,2,3,4,8); ref=RAO[S]
    r=enum_subset(S)                       # the FROZEN campaign enumerator
    def resid(x): F=SP.constraints(*x); return [F[k] for k in S]
    roots=[]
    for _ in range(3000):
        x0=[random.uniform(*BOX[i]) for i in range(5)]
        try: x,info,ier,_=fsolve(resid,x0,full_output=True)
        except Exception: continue
        if ier==1 and all(BOX[i][0]<=x[i]<=BOX[i][1] for i in range(5)) \
           and max(abs(v) for v in resid(x))<1e-9:
            if not any(max(abs(x[i]-q[i]) for i in range(5))<1e-4 for q in roots):
                roots.append(tuple(x))
    nAA=r['cert']; nN=len(roots)
    aa_has_rao = any(rt['gate2'] and max(abs(rt['coords'][i]-ref[i]) for i in range(5))<1e-3
                     for rt in r['roots'])
    agree=(nAA==nN==1) and aa_has_rao and r['complete']
    print(f"M2 two-way {{1,2,3,4,8}}: campaign certified={nAA} (complete={r['complete']}, "
          f"unres={r['unresolved']}), Newton in-box={nN}, AA root=Rao & gate2={aa_has_rao}  "
          f"-> {'PASS' if agree else 'FAIL'}")
    return agree

if __name__=="__main__":
    print("Gate M — validates campaign.py + plane_chain.py + aar.py + admissibility.py")
    print("OFFICIAL run is POST-FREEZE on the frozen tree; this is the dress rehearsal.\n")
    p1=m1(); p2=m2()
    print(f"\nGate M: {'PASS (ready to freeze & run officially)' if (p1 and p2) else 'INSPECT'}")
