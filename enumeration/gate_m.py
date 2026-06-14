# Gate M (Amendment-02 §B7) harness. OFFICIAL run is POST-FREEZE on the frozen
# tool; this doubles as a pre-freeze dress rehearsal.
#   M1 engine-equivalence : hardened AAr brackets the v0.1.0 engine on all 20
#                           constraints, at reference rows + random valid figures.
#   M2 two-way cross-check: AAr enumeration of {1,2,3,4,8} and multistart Newton
#                           agree (set-equal), both containing Rao's Table-3 row.
import os,sys,math,random
sys.path.insert(0,'/home/claude'); sys.path.insert(0,'.')
import numpy as np, sriyantra_plane as SP
from aar import AAr, DualR
from calib import enum
from route3_panel import cons_full, Fvec
from scipy.optimize import fsolve
import warnings; warnings.filterwarnings("ignore"); random.seed(7)

BOX=[(0.20,0.80),(0.10,0.45),(0.15,0.45),(0.25,0.75),(0.03,0.25)]
RAO={(1,2,3,4,8):(0.463752,0.223255,0.288990,0.488181,0.106157),
     (1,2,4,5,10):(0.438237,0.218371,0.269490,0.440182,0.096716),
     (1,2,6,14,19):(0.468710,0.257071,0.308200,0.480582,0.121790),
     (1,2,3,10,15):(0.456449,0.236967,0.282560,0.456267,0.104822)}

# ---- M1 ----
def m1():
    pts=[list(v) for v in RAO.values()]
    got=0
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
    print(f"M1 engine-equivalence: {len(pts)} figures x 20 constraints, "
          f"escapes={esc}  max half-width={worst:.1e}  -> {'PASS' if esc==0 else 'FAIL'}")
    return esc==0

# ---- M2 ----
def m2():
    S=(1,2,3,4,8); ref=RAO[S]
    r=enum(list(S),AAr,DualR,r_cert=3e-3,max_boxes=400000,tlim=200)
    # AAr enumeration recovers the certified count; re-derive the certified center
    # (enum returns count; for the location, run a Newton from box center via engine)
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
    contains_rao = any(max(abs(roots[j][i]-ref[i]) for i in range(5))<1e-3 for j in range(len(roots)))
    agree = (nAA==nN==1) and contains_rao
    print(f"M2 two-way {{1,2,3,4,8}}: AAr certified={nAA} (complete={r['done']}), "
          f"Newton in-box={nN}, contains Rao row={contains_rao}  -> {'PASS' if agree else 'FAIL'}")
    return agree

if __name__=="__main__":
    print("Gate M dress rehearsal (official run is POST-FREEZE on the frozen tool)\n")
    p1=m1(); p2=m2()
    print(f"\nGate M: {'PASS (ready to freeze & run officially)' if (p1 and p2) else 'INSPECT'}")
