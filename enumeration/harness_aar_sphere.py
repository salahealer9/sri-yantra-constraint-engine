import math, random
from math import pi
import aar; from aar import AAr
import aar_sphere as S
from aar_sphere import SplitNeeded, DomainError

random.seed(20260625)
TRUE = {"sin":math.sin,"cos":math.cos,"tan":math.tan,"atan":math.atan,"acos":math.acos}

def clean_box(name):
    """random (center,rad) whose interval is inflection-free + in-domain for name."""
    while True:
        if name in ("sin","cos","tan"):
            # pick a center in a single monotone-curvature lane, small rad
            base = random.uniform(-1.3,1.3)          # within (-pi/2,pi/2) lane for tan
            rad  = random.uniform(1e-4, 0.12)
            c = base
        elif name=="atan":
            sgn = random.choice([-1,1]); c = sgn*random.uniform(0.05,3.0); rad=random.uniform(1e-4,0.2)
        else: # acos
            sgn = random.choice([-1,1]); c = sgn*random.uniform(0.05,0.9); rad=random.uniform(1e-4,0.05)
        AAr._n=[0]; x=AAr.var(c,rad)
        try:
            S.SCALARS[name](x); return c,rad
        except (SplitNeeded,DomainError):
            continue

def test_rigor_tight(name, N=4000, dense=200):
    f=TRUE[name]; worst_viol=0.0; ratios=[]; ok=0
    for _ in range(N):
        c,rad=clean_box(name)
        AAr._n=[0]; x=AAr.var(c,rad); a,b=x.iv()
        r=S.SCALARS[name](x); lo,hi=r.iv()
        # dense true samples over the INPUT interval [a,b]
        fmin=fmax=f(a)
        viol=0.0
        for i in range(dense+1):
            t=a+(b-a)*i/dense; fv=f(t)
            fmin=min(fmin,fv); fmax=max(fmax,fv)
            if fv<lo: viol=max(viol, lo-fv)
            if fv>hi: viol=max(viol, fv-hi)
        worst_viol=max(worst_viol,viol)
        exact_w=max(fmax-fmin,1e-300); ratios.append((hi-lo)/exact_w)
        ok+=1
    ratios.sort()
    med=ratios[len(ratios)//2]; p95=ratios[int(0.95*len(ratios))]; mx=ratios[-1]
    return ok,worst_viol,med,p95,mx

print("RIGOR (worst containment violation; must be 0) + TIGHTNESS (enclosure/exact width)")
print(f"  {'fn':>5} {'boxes':>6} {'worst_violation':>16} {'median':>8} {'p95':>8} {'max':>8}")
all_rig=True
for nm in ("sin","cos","tan","atan","acos"):
    ok,viol,med,p95,mx=test_rigor_tight(nm)
    rig = viol<=0.0
    all_rig &= rig
    print(f"  {nm:>5} {ok:>6} {viol:>16.3e} {med:>8.3f} {p95:>8.3f} {mx:>8.3f}  {'RIGOROUS' if rig else 'VIOLATION!'}")
print(f"\n  ALL RIGOROUS: {all_rig}")

# ---- SPLIT / DOMAIN signalling ----
print("\nSPLIT/DOMAIN signalling (must raise the right exception):")
def expect(name, c, rad, exc):
    AAr._n=[0]; x=AAr.var(c,rad)
    try:
        S.SCALARS[name](x); return f"  [FAIL] {name}(c={c},r={rad}) did NOT raise {exc.__name__}"
    except exc:
        return f"  [ok]   {name}: raised {exc.__name__} as expected"
    except Exception as e:
        return f"  [FAIL] {name}: raised {type(e).__name__}, expected {exc.__name__}"
print(expect("sin", 0.0, 0.3, SplitNeeded))      # straddles 0 (sin inflection)
print(expect("sin", pi, 0.3, SplitNeeded))       # straddles pi
print(expect("cos", pi/2, 0.3, SplitNeeded))     # straddles pi/2 (cos inflection)
print(expect("tan", pi/2, 0.2, SplitNeeded))     # straddles pole
print(expect("tan", 0.0, 0.3, SplitNeeded))      # straddles 0 (tan inflection)
print(expect("atan",0.0, 0.3, SplitNeeded))      # straddles 0
print(expect("acos",0.0, 0.3, SplitNeeded))      # straddles 0
print(expect("acos",0.98,0.05, SplitNeeded))     # straddles +1 domain edge
print(expect("acos",1.5, 0.2, DomainError))      # entirely outside [-1,1]
