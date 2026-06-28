import math, random
import aar; from aar import AAr
import aar_sphere_v2_monotone as M
from aar_sphere import DualRS, SplitNeeded, DomainError
random.seed(20260625)

def grad_contains(mono_dual, true_f, true_fp, k, c, rad):
    """Apply mono dual form to a DualRS var; check true value AND true partial
    (= f'(u)*1, single-var) are contained in the value/grad enclosures. Returns
    (val_viol, grad_viol, val_in, grad_in)."""
    AAr._n=[0]; x=DualRS.var(k, c, rad)
    R=mono_dual(x)
    vlo,vhi=R.val.iv(); glo,ghi=R.grad[k].iv()
    # sample true f and f' over the box [c-rad,c+rad]
    a,b=c-rad,c+rad; val_viol=grad_viol=0.0
    for i in range(401):
        t=a+(b-a)*i/400
        fv=true_f(t); fp=true_fp(t)   # single-var: ∂/∂x_k = f'(t)
        if fv<vlo: val_viol=max(val_viol,vlo-fv)
        if fv>vhi: val_viol=max(val_viol,fv-vhi)
        if fp<glo: grad_viol=max(grad_viol,glo-fp)
        if fp>ghi: grad_viol=max(grad_viol,fp-ghi)
    return val_viol, grad_viol, (ghi-glo)

print("LEVER 2 derivative-layer harness — d_atan_mono / d_acos_mono")
print("(checks BOTH value AND gradient containment, separately)")

print("\nCASE 1: inflection-straddle (0), away from domain edge")
specs=[("atan",M.d_atan_mono,math.atan,lambda t:1.0/(1.0+t*t),lambda:(random.uniform(-0.5,0.5),random.uniform(0.05,0.4))),
       ("acos",M.d_acos_mono,math.acos,lambda t:-1.0/math.sqrt(1.0-t*t),lambda:(random.uniform(-0.3,0.3),random.uniform(0.05,0.3)))]
for name,md,tf,tfp,gen in specs:
    vw=gw=0.0; n=0; gwidth=0.0
    for _ in range(8000):
        c,rad=gen()
        if not (c-rad<0<c+rad): continue
        if name=="acos" and (c-rad<=-1 or c+rad>=1): continue
        try:
            vv,gv,gwid=grad_contains(md,tf,tfp,0,c,rad)
            vw=max(vw,vv); gw=max(gw,gv); gwidth=max(gwidth,gwid); n+=1
        except (SplitNeeded,DomainError): pass
    print(f"  {name}: {n} boxes  value_viol={vw:.2e}  grad_viol={gw:.2e}  max_grad_width={gwidth:.2e}")

print("\nCASE 2 (CRITICAL): acos near +-1 — derivative blows up; must SplitNeeded, never silent")
silent=0; split=0; dom=0; n=0; maxM=0.0
for _ in range(20000):
    # boxes straddling 0 but with one endpoint very close to +-1 (umax -> 1)
    umax=random.uniform(0.9, 1.001)
    c=random.uniform(-0.05,0.05); rad=umax-abs(c) if umax>abs(c) else 0.01
    a,b=c-rad,c+rad
    if not (a<0<b): continue
    n+=1
    AAr._n=[0]; x=DualRS.var(0,c,rad)
    try:
        R=M.d_acos_mono(x); glo,ghi=R.grad[0].iv()
        # returned finite -> box must be strictly inside (-1,1); check it is
        if a<=-1 or b>=1: silent+=1
        maxM=max(maxM, abs(glo), abs(ghi))   # how large does the finite derivative get?
    except SplitNeeded: split+=1
    except DomainError: dom+=1
print(f"  {n} near-edge straddle boxes -> SplitNeeded={split} DomainError={dom} returned-finite={n-split-dom}")
print(f"  SILENT enclosure on a +-1-touching box (MUST be 0): {silent}")
print(f"  largest finite |derivative| returned (no cap; Krawczyk sees it): {maxM:.2e}")

print("\nCASE 3: non-straddling — dual mono delegates to affine dual (identical)")
import aar_sphere as A
mm=0; okc=0
for _ in range(8000):
    for name,md,ad,gen in (("atan",M.d_atan_mono,A.d_atan,lambda:(random.uniform(0.1,2.0),random.uniform(1e-3,0.1))),
                           ("acos",M.d_acos_mono,A.d_acos,lambda:(random.uniform(0.1,0.8),random.uniform(1e-3,0.05)))):
        c,rad=gen()
        if not (c-rad>0): continue
        AAr._n=[0]; x1=DualRS.var(0,c,rad); r1=md(x1).grad[0].iv()
        AAr._n=[0]; x2=DualRS.var(0,c,rad); r2=ad(x2).grad[0].iv()
        if abs(r1[0]-r2[0])<1e-12 and abs(r1[1]-r2[1])<1e-12: okc+=1
        else: mm+=1
print(f"  non-straddling: {okc} identical to affine dual, {mm} mismatches  [MUST be 0]")
