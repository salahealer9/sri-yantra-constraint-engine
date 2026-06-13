# Independent soundness cross-check: multistart Newton on the panel subsets.
# If Newton finds an in-box root that the AA enumerator EXCLUDED, that's a bug.
import os,sys; sys.path.insert(0,'/home/claude'); sys.path.insert(0,'.')
import sriyantra_plane as SP
import numpy as np
from scipy.optimize import fsolve
np.random.seed(0)
BOX=[(0.20,0.80),(0.10,0.45),(0.15,0.45),(0.25,0.75),(0.03,0.25)]
def inbox(x): return all(BOX[i][0]<=x[i]<=BOX[i][1] for i in range(5))
def resid(x,S):
    F=SP.constraints(*x); return [F[k] for k in S]
def multistart(S, n=4000):
    roots=[]
    for _ in range(n):
        x0=[np.random.uniform(*BOX[i]) for i in range(5)]
        try:
            x,info,ier,_=fsolve(resid,x0,args=(S,),full_output=True)
        except Exception: continue
        if ier==1 and inbox(x) and max(abs(v) for v in resid(x,S))<1e-9:
            if not any(max(abs(x[i]-r[i]) for i in range(5))<1e-4 for r in roots):
                roots.append(tuple(x))
    return roots
for name,S in [("Rao A",(1,2,3,4,8)),("Rao B",(1,2,4,5,10)),
               ("coord-heavy",(1,2,11,12,17)),("random",(1,2,6,10,19)),
               ("dense",(1,2,3,4,6))]:
    R=multistart(S)
    print(f"{name:12s} {str(S):16s}: Newton finds {len(R)} in-box root(s)")
    for r in R: print("     "+", ".join(f"{v:.4f}" for v in r))
