import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, '.')
import sriyantra_plane as SP
import numpy as np

rao = dict(b=0.463752, c=0.223255, d=0.288990, e=0.488181, g=0.106157)
keys = ['b','c','d','e','g']; cons = [1,2,3,4,8]

def Fvec(p):
    F = SP.constraints(p['b'],p['c'],p['d'],p['e'],p['g'])
    return np.array([F[k] for k in cons])

def jac(h):
    J = np.zeros((5,5))
    for j,kk in enumerate(keys):
        pp = dict(rao); pm = dict(rao)
        pp[kk]+=h; pm[kk]-=h
        J[:,j] = (Fvec(pp)-Fvec(pm))/(2*h)
    return J

print("Jacobian of {F1,F2,F3,F4,F8} wrt (b,c,d,e,g) at Rao's point\n")
for h in (1e-4,1e-5,1e-6):
    J = jac(h)
    sv = np.linalg.svd(J, compute_uv=False)
    print(f"h={h:.0e}: det={np.linalg.det(J):+.3e}  cond={sv[0]/sv[-1]:.3e}")
    print(f"         singular values: {', '.join(f'{s:.3e}' for s in sv)}")
print()
J = jac(1e-6); sv = np.linalg.svd(J, compute_uv=False)
print(f"smallest singular value sigma_min = {sv[-1]:.3e}")
print(f"   (sigma_min ~ 0  => root is singular/non-simple => no simple root to certify)")
print(f"   (cond >> 1e8    => severely ill-conditioned for interval certification)")
# null vector direction at the (near-)singular root
U,S,Vt = np.linalg.svd(jac(1e-6))
print(f"\n approx null-direction (which variables move along the tangency), |v| weights:")
v = Vt[-1]
for kk,val in zip(keys, v):
    print(f"     {kk}: {val:+.3f}")
