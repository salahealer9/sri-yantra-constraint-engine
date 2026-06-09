import numpy as np
from itertools import combinations
import sriyantra_plane as SP

def Fvec(p):
    F = SP.constraints(*p)
    return np.array([F[i] for i in range(1,21)], float)

def numjac(p, eps=1e-6):
    J = np.empty((20,5))
    for j in range(5):
        pp=list(p); pm=list(p); pp[j]+=eps; pm[j]-=eps
        J[:,j] = (Fvec(pp)-Fvec(pm))/(2*eps)
    return J

rng=np.random.default_rng(1)
seeds=[v for _,v in SP.TABLE3]+[SP.PLANE_OPT]
pts=[]; tries=0
while len(pts)<8 and tries<5000:
    tries+=1
    base=seeds[rng.integers(len(seeds))]
    cand=tuple(np.array(base)+rng.normal(0,0.02,5))
    try:
        J=numjac(cand)
        if np.all(np.isfinite(J)) and np.all(np.isfinite(Fvec(cand))): pts.append(cand)
    except Exception: pass
print(f"{len(pts)} valid plane sample points\n")
Js=[numjac(p) for p in pts]

# constant linear dependencies
B=np.hstack(Js); S=np.linalg.svd(B,compute_uv=False)
ndep=int(np.sum(S<1e-6*S[0]))
print("PLANE constant linear dependencies among F1..F20 =",ndep,
      " (smallest sv:",np.array2string(S[-3:],precision=2),")")
R1=np.zeros(20);R1[7]=1;R1[8]=-1;R1[15]=1
R2=np.zeros(20);R2[15]=1;R2[16]=-1;R2[17]=-1;R2[18]=1
print("  F8-F9+F16        residual:",f"{max(np.max(np.abs(R1@J)) for J in Js):.1e}")
print("  F16-F17-F18+F19  residual:",f"{max(np.max(np.abs(R2@J)) for J in Js):.1e}\n")

# generic-rank scan: {1,2} u T, |T|=3 -> 5x5
deg=[]
for T in combinations(range(3,21),3):
    rows=[0,1]+[t-1 for t in T]
    best=max(np.linalg.svd(J[rows,:],compute_uv=False)[-1]/
             np.linalg.svd(J[rows,:],compute_uv=False)[0] for J in Js)
    if best<1e-7: deg.append(T)
print(f"PLANE generic-rank scan of C(18,3)=816 systems {{1,2}}+T:")
print(f"  degenerate: {len(deg)}   well-posed: {816-len(deg)}")
C1={8,9,16};C2={16,17,18,19};C3={8,9,17,18,19}
for T in deg:
    s=set(T); tag=[]
    if C1<=s:tag.append("{8,9,16}")
    if C2<=s:tag.append("{16,17,18,19}")
    if C3<=s:tag.append("{8,9,17,18,19}")
    print("   ",(1,2)+T," contains",tag if tag else "** NON-RADIAL **")
