"""diag_find_seed.py — open the find_seed black box on the benchmark. Server-only."""
import sys, os, math
import numpy as np
_here = os.path.dirname(os.path.abspath(__file__))
_root = _here
while _root != os.path.dirname(_root):
    if os.path.exists(os.path.join(_root, "sriyantra.py")):
        break
    _root = os.path.dirname(_root)
for _p in (_here, _root, os.path.join(_root, "enumeration")):
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)
import sriyantra as RAO
import spherical_existence_mapper as M

PI2=math.pi/2; DEG=math.pi/180
BENCH=(1,2,3,4,6,7)
KNOWN=[0.6246238466927992,0.7044304165359816,0.7482768099360514,0.6307397242292889,0.3136386632298885,0.39527668335411803]
h=KNOWN[5]; hd=h/DEG; R=PI2-h

def rresid(xraw):
    try: F=RAO.constraints(*xraw); return math.sqrt(sum(F[k]**2 for k in BENCH))
    except Exception: return None

print(f"known raw b..h: {[round(v,5) for v in KNOWN]}")
print(f"h={h:.5f}rad hd={hd:.4f}deg R=PI2-h={R:.6f}\n")

L=getattr(M,'L',None); GC=getattr(M,'GC',None)
print("mapper has L (newton module):", L is not None, " GC (gate4):", GC is not None)
print("L module name:", getattr(L,'__name__','?'), " GC module name:", getattr(GC,'__name__','?'))
print()

print("=== L.newton seeded BY the known root, testing which coord convention it wants ===")
for tag,x0 in [("raw", np.array(KNOWN[:5],float)),
               ("raw/R", np.array(KNOWN[:5],float)/R),
               ("raw*R", np.array(KNOWN[:5],float)*R)]:
    try:
        x,res,ok,c = L.newton(BENCH, x0.copy(), hd*DEG, maxit=90)
        cands={'id':list(np.asarray(x))+[h],'divR':[v/R for v in np.asarray(x)]+[h],'mulR':[v*R for v in np.asarray(x)]+[h]}
        scored={k:rresid(v) for k,v in cands.items()}
        bestk=min(scored,key=lambda k:(scored[k] if scored[k] is not None else 9e9))
        print(f"  seed={tag:6s} -> ok={ok} res={res:.2e} returned_x={[round(float(v),4) for v in np.asarray(x)]}")
        print(f"                 best raw-bridge={bestk} resid={scored[bestk]}")
    except Exception as e:
        print(f"  seed={tag:6s} -> raised {type(e).__name__}: {e}")

print("\n=== does gate4 accept the known root? (find_seed requires gate4 valid, else stores as 'best') ===")
try:
    v,info = GC.gate4(*KNOWN[:5], hd*DEG, closure_tol=1e-7)
    print(f"  gate4(known root) -> valid={v}  info={info}")
except Exception as e:
    print(f"  gate4 raised {type(e).__name__}: {e}")
    try:
        v,info = GC.gate4(*(np.array(KNOWN[:5])/R), hd*DEG, closure_tol=1e-7)
        print(f"  gate4(known/R)   -> valid={v}")
    except Exception as e2: print(f"  gate4(known/R) raised {e2}")
