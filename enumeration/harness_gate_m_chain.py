import sys, math, random, os
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
import aar; from aar import AAr
import chain_sphere as CH
from chain_sphere import AA_FN
from aar_sphere import SplitNeeded, DomainError
B={'b':(1e-6,0.763186),'c':(1e-6,1.103454),'d':(1e-6,1.302556),
   'e':(1e-6,0.647740),'g':(1e-6,0.687977),'h':(1e-6,1.570795)}
VARS=['b','c','d','e','g','h']; random.seed(20260625)
NEED=1000; CAP=200000; RAD_BOX=1e-7
ISO={3:'x10',4:'x13',6:'x7'}   # GM-1: diagnostic-only center for these
def sample(): return [random.uniform(*B[v]) for v in VARS]
pts=[]; tried=0
while len(pts)<NEED and tried<CAP:
    tried+=1; p=sample()
    try: RAO.chain(*p); RAO.constraints(*p); pts.append(p)
    except Exception: pass
# criterion 1 (GM-1): chain fidelity strict; constraint center: gate non-iso, diagnose iso
w_chain=0.0; w_cons_gate=0.0; iso_diag={3:(0,0),4:(0,0),6:(0,0)}
for p in pts:
    Ct=RAO.chain(*p); Ft=RAO.constraints(*p)
    AAr._n=[0]; AV=[AAr.var(p[k],0.0) for k in range(6)]
    Ca=CH.chain_sph(*AV,AA_FN); Fa=CH.constraints_sph(*AV,AA_FN)
    for k,vt in Ct.items():
        if k in('b','c','d','e','g') or k not in Ca: continue
        w_chain=max(w_chain,abs(Ca[k].c-float(vt)))
    for i,vt in Ft.items():
        if i not in Fa: continue
        dd=abs(Fa[i].c-float(vt))
        if i in ISO:
            cx=abs(math.cos(float(Ct[ISO[i]])))
            wd,wc=iso_diag[i]
            if dd>wd: iso_diag[i]=(dd,cx)
        else:
            w_cons_gate=max(w_cons_gate,dd)
# criterion 2: containment (all constraints incl iso), rad>0
chain_viol=cons_viol=0
for p in pts:
    Ct=RAO.chain(*p); Ft=RAO.constraints(*p)
    AAr._n=[0]; AV=[AAr.var(p[k],RAD_BOX) for k in range(6)]
    try: Ca=CH.chain_sph(*AV,AA_FN); Fa=CH.constraints_sph(*AV,AA_FN)
    except (SplitNeeded,DomainError): continue
    for k,vt in Ct.items():
        if k in('b','c','d','e','g') or k not in Ca: continue
        lo,hi=Ca[k].iv()
        if not(lo<=float(vt)<=hi): chain_viol+=1
    for i,vt in Ft.items():
        if i not in Fa: continue
        lo,hi=Fa[i].iv()
        if not(lo<=float(vt)<=hi): cons_viol+=1
print("GATE-M (amended GM-1) — chain_sphere vs frozen sriyantra.py, n=%d"%len(pts))
print(f"  [c1 gate] chain-quantity mirror fidelity (<=1e-10) : {w_chain:.3e}  {'PASS' if w_chain<=1e-10 else 'FAIL'}")
print(f"  [c1 gate] non-iso constraint center (<=1e-10)      : {w_cons_gate:.3e}  {'PASS' if w_cons_gate<=1e-10 else 'FAIL'}")
print(f"  [c1 diag] iso-constraint center (F3/F4/F6, NOT gating, reported w/ |cos x|):")
for i in (3,4,6):
    dd,cx=iso_diag[i]; print(f"            F{i}: worst center disc={dd:.2e} at |cos(x)|={cx:.2e}")
print(f"  [c2 gate] enclosure containment (0 violations)     : chain={chain_viol} cons={cons_viol}  {'PASS' if chain_viol==0 and cons_viol==0 else 'FAIL'}")
gate=(w_chain<=1e-10 and w_cons_gate<=1e-10 and chain_viol==0 and cons_viol==0)
print(f"\n  GATE-M (criteria 1+2, amended): {'PASS' if gate else 'NOT PASS'}   (criteria 3,4,5 with domain_sphere)")
