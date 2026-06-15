# Quantify naive-interval overestimation of F over a small box around Rao,
# vs the TRUE variation implied by the (well-conditioned) float Jacobian.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, '.')
import sriyantra_plane as SP
import numpy as np
from route3_probe import cons_iv, boxiv   # reuse the validated interval chain

rao = [0.463752,0.223255,0.288990,0.488181,0.106157]
keys=['b','c','d','e','g']; cons=[1,2,3,4,8]
def Fvec(p): F=SP.constraints(*p); return np.array([F[k] for k in cons])
def J(h=1e-6):
    M=np.zeros((5,5))
    for j in range(5):
        pp=list(rao); pm=list(rao); pp[j]+=h; pm[j]-=h
        M[:,j]=(Fvec(pp)-Fvec(pm))/(2*h)
    return M
Jm=J()

print("overestimation of the interval F-enclosure vs true variation, per radius r")
print("(true half-width_i ~ sum_j |J_ij| * r ; naive = mpmath.iv chain width/2)\n")
for r in (1e-3, 3e-3, 1e-2):
    box=[(v-r, v+r) for v in rao]
    Fi=cons_iv(*boxiv(box))
    naive_hw=[ (float(I.b)-float(I.a))/2 for I in Fi ]
    true_hw =[ float(np.sum(np.abs(Jm[i]))*r) for i in range(5) ]
    print(f"r={r:.0e}:")
    for i,k in enumerate(cons):
        fac = naive_hw[i]/true_hw[i] if true_hw[i]>0 else float('inf')
        print(f"   F{k}: naive half-width={naive_hw[i]:.3e}  true~{true_hw[i]:.3e}  overest x{fac:6.1f}")
    print()
print("For Krawczyk to certify, the interval Jacobian must keep ||I - Y*J(X)|| < 1.")
print("An overestimation factor of ~10-100x on F (and worse on its derivatives)")
print("inflates J(X) enough that the contraction test fails even on tiny boxes —")
print("which is exactly the all-:unknown cloud we saw, despite cond(J)=9.")
