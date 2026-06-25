import math, random
import aar; from aar import AAr
import aar_sphere as S
from aar_sphere import DualRS

# composite exercising products, divisions, and all 5 transcendentals
def f_float(b,c,d,e,g,h):
    return (math.atan(math.sin(b+c)/math.sin(c+d)*math.tan(d))
            + math.acos(math.cos(h)/math.cos(c))*math.cos(e)
            - math.tan(g)*b)

def f_dual(B):  # B: list of 6 DualRS
    b,c,d,e,g,h = B
    return (S.d_atan(S.d_sin(b+c)/S.d_sin(c+d)*S.d_tan(d))
            + S.d_acos(S.d_cos(h)/S.d_cos(c))*S.d_cos(e)
            - S.d_tan(g)*b)

pt = [0.30,0.25,0.20,0.40,0.10,0.39]   # generic clean point (acos arg in (0,1))
rad = 1e-6                              # tiny box: no inflection/domain straddle

# dual evaluation
AAr._n=[0]
B = [DualRS.var(k, pt[k], rad) for k in range(6)]
R = f_dual(B)
val_c = R.val.c
grad_c = [R.grad[k].c for k in range(6)]
grad_iv = [R.grad[k].iv() for k in range(6)]

# truth: value + central finite-difference gradient in plain float
val_true = f_float(*pt)
def fd(k,hh=1e-7):
    pp=list(pt); pm=list(pt); pp[k]+=hh; pm[k]-=hh
    return (f_float(*pp)-f_float(*pm))/(2*hh)
g_true=[fd(k) for k in range(6)]

print("DualRS verification — composite with products/divisions + all 5 transcendentals")
print(f"  value: dual center={val_c:.12f}  true={val_true:.12f}  |diff|={abs(val_c-val_true):.2e}")
print(f"\n  {'k':>2} {'var':>3} {'dual grad center':>18} {'FD partial':>16} {'|diff|':>10} {'FD in grad.iv()?':>16}")
vars6=['b','c','d','e','g','h']; allok=True; allcontain=True
for k in range(6):
    diff=abs(grad_c[k]-g_true[k])
    lo,hi=grad_iv[k]; contain = lo<=g_true[k]<=hi
    allok &= (diff<1e-6); allcontain &= contain
    print(f"  {k:>2} {vars6[k]:>3} {grad_c[k]:>18.10f} {g_true[k]:>16.10f} {diff:>10.2e} {str(contain):>16}")
print(f"\n  all gradient centers match FD (<1e-6): {allok}")
print(f"  all true partials contained in rigorous grad enclosures: {allcontain}")

# also confirm SplitNeeded/DomainError propagate through the dual layer
from aar_sphere import SplitNeeded, DomainError
def expect(desc, fn, exc):
    try: fn(); print(f"  [FAIL] {desc}: no {exc.__name__}")
    except exc: print(f"  [ok]   {desc}: {exc.__name__} propagated")
    except Exception as e: print(f"  [FAIL] {desc}: {type(e).__name__}")
print("\n  dual-layer exception propagation:")
AAr._n=[0]; expect("d_atan straddling 0", lambda: S.d_atan(DualRS.var(0,0.0,0.3)), SplitNeeded)
AAr._n=[0]; expect("d_acos out of domain", lambda: S.d_acos(DualRS.var(0,1.5,0.2)), DomainError)
