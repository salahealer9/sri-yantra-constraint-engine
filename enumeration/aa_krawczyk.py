# In-sandbox PROOF that route-3 certification works: Krawczyk operator with an
# AA-tight Jacobian enclosure. If K(X) ⊆ int(X), a unique root is CERTIFIED in X.
# (Float-coefficient AA -> proof of principle; rigorous certificate needs rounded
#  AA / TaylorModels.jl, which is the production port.)
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, '.')
import sriyantra_plane as SP
import numpy as np
from aa_test import AA, chain_AA   # reuse validated AA + chain

# ---- forward-mode AD over AA: Dual carries value-AA and 5 partial-AAs ----
class Dual:
    def __init__(s, val, grad): s.val=val; s.grad=grad      # val:AA, grad:list[AA] len5
    @staticmethod
    def const(x): return Dual(x if isinstance(x,AA) else AA(x), [AA(0.0) for _ in range(5)])
    @staticmethod
    def var(k, center, r):
        g=[AA(0.0) for _ in range(5)]; g[k]=AA(1.0)
        return Dual(AA.var(center, r), g)
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
        return Dual(s.val*o.val,[s.grad[j]*o.val + s.val*o.grad[j] for j in range(5)])
    __rmul__=__mul__
    def __truediv__(s,o):
        o=o if isinstance(o,Dual) else Dual.const(o)
        q=s.val/o.val
        return Dual(q,[(s.grad[j]-q*o.grad[j])/o.val for j in range(5)])
    def __rtruediv__(s,o): return Dual.const(o).__truediv__(s)
    def sqrt(s):
        sv=s.val.sqrt()
        return Dual(sv,[s.grad[j]/(sv*2.0) for j in range(5)])

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
    F1=x11-x11a; F2=d-U7-rT; F3=H*x10*x10-(V8*V8)*0.5
    F4=H*x13*x13-((c+d+v9-v12)*(c+d+v9-v12))*0.5; F8=one-r16
    return [F1,F2,F3,F4,F8]

rao=[0.463752,0.223255,0.288990,0.488181,0.106157]; cons=[1,2,3,4,8]
def Fvec(p): F=SP.constraints(*p); return np.array([F[k] for k in cons])
def Jm_fd(h=1e-7):
    M=np.zeros((5,5))
    for j in range(5):
        pp=list(rao);pm=list(rao);pp[j]+=h;pm[j]-=h
        M[:,j]=(Fvec(pp)-Fvec(pm))/(2*h)
    return M

def krawczyk(center, r):
    AA._n=[0]
    vs=[Dual.var(k, center[k], r) for k in range(5)]
    Fd=chain_dual(*vs)
    # tight interval Jacobian over the box from AA partials
    JX=np.empty((5,5),dtype=object)
    for i in range(5):
        for j in range(5):
            lo,hi=Fd[i].grad[j].iv(); JX[i,j]=(lo,hi)
    Jm=Jm_fd()
    Y=np.linalg.inv(Jm)
    Fm=Fvec(center)                                   # F at center (thin)
    # M = I - Y*J(X)  (interval matrix); use midpoint-radius
    Jmid=np.array([[ (JX[i,j][0]+JX[i,j][1])/2 for j in range(5)] for i in range(5)])
    Jrad=np.array([[ (JX[i,j][1]-JX[i,j][0])/2 for j in range(5)] for i in range(5)])
    Mmid=np.eye(5)-Y@Jmid
    Mrad=np.abs(Y)@Jrad                               # radius of (I-Y J(X))
    YFm=Y@Fm
    # K_i - m_i = -(Y Fm)_i + sum_l M_il*[-r,r]; half-width = sum_l (|Mmid_il|+Mrad_il)*r
    Kc = -YFm                                         # center offset of K-m
    Khw= (np.abs(Mmid)+Mrad) @ (np.full(5, r))        # half-width of K-m
    # K_i in [m_i + Kc_i - Khw_i, m_i + Kc_i + Khw_i]; certified if ⊂ (m_i-r, m_i+r)
    lo = np.array(center)+Kc-Khw; hi=np.array(center)+Kc+Khw
    Xlo=np.array(center)-r; Xhi=np.array(center)+r
    interior = (lo>Xlo) & (hi<Xhi)
    contr = np.max(np.abs(Mmid)+Mrad)                 # ~ ||I - Y J(X)|| proxy (<1 needed)
    return interior, contr, (lo,hi,Xlo,Xhi)

print("AA-Krawczyk certification of Rao's {1,2,3,4,8} root\n")
for r in (1e-2, 3e-3, 1e-3):
    interior, contr, _ = krawczyk(rao, r)
    print(f"r={r:.0e}:  contraction ||I-YJ(X)||~{contr:.3f}   "
          f"K⊂int(X) per coord: {list(map(bool,interior))}   "
          f"CERTIFIED={'YES' if interior.all() and contr<1 else 'no'}")
print("\n(K(X) ⊆ int(X) with contraction <1  ==>  a UNIQUE root is certified in X.)")
