import math, random
import aar; from aar import AAr
import aar_sphere_v2_monotone as M
from aar_sphere import SplitNeeded, DomainError
random.seed(20260625)

def value_contains(fn, true_f, c, rad, dense=400):
    """Apply mono value form to AAr.var(c,rad); check true f over [a,b] is enclosed."""
    AAr._n=[0]; x=AAr.var(c,rad); a,b=x.iv()
    r=fn(x); lo,hi=r.iv()
    worst=0.0
    for i in range(dense+1):
        t=a+(b-a)*i/dense; fv=true_f(t)
        if fv<lo: worst=max(worst, lo-fv)
        if fv>hi: worst=max(worst, fv-hi)
    return worst, (hi-lo)

print("LEVER 2 value-layer harness — aa_atan_mono / aa_acos_mono")
print("\nCASE 1: inflection-only boxes straddling 0 (expect NO SplitNeeded, 0 containment violation)")
for name,fn,tf,gen in (("atan",M.aa_atan_mono,math.atan,lambda:(random.uniform(-0.5,0.5),random.uniform(0.05,0.4))),
                       ("acos",M.aa_acos_mono,math.acos,lambda:(random.uniform(-0.3,0.3),random.uniform(0.05,0.3)))):
    wv=0.0; n=0; split=0
    for _ in range(8000):
        c,rad=gen()
        # ensure straddles 0 and (acos) strictly inside (-1,1)
        if not (c-rad < 0 < c+rad): continue
        if name=="acos" and (c-rad<=-1 or c+rad>=1): continue
        try:
            w,_=value_contains(fn,tf,c,rad); wv=max(wv,w); n+=1
        except (SplitNeeded,DomainError): split+=1
    print(f"  {name}: tested {n} straddle boxes, worst containment violation={wv:.2e}, unexpected splits={split}")

print("\nCASE 2: acos domain-edge boxes near +-1 (expect split/domain, NEVER silent finite enclosure)")
edge=0; dom=0; silent=0; n=0
for _ in range(8000):
    # boxes straddling +1 or entirely outside
    mode=random.choice(['straddle+1','straddle-1','outside+','outside-'])
    if mode=='straddle+1': c=random.uniform(0.95,1.05); rad=random.uniform(0.02,0.1)
    elif mode=='straddle-1': c=random.uniform(-1.05,-0.95); rad=random.uniform(0.02,0.1)
    elif mode=='outside+': c=random.uniform(1.1,1.6); rad=random.uniform(0.02,0.2)
    else: c=random.uniform(-1.6,-1.1); rad=random.uniform(0.02,0.2)
    AAr._n=[0]; x=AAr.var(c,rad); a,b=x.iv()
    n+=1
    try:
        M.aa_acos_mono(x)
        # if it returned, the box must be strictly inside [-1,1] — check it didn't silently enclose an edge box
        if a<-1 or b>1: silent+=1
    except DomainError: dom+=1
    except SplitNeeded: edge+=1
print(f"  acos near +-1: {n} boxes -> DomainError={dom}, SplitNeeded(edge)={edge}, SILENT-finite-on-edge={silent}  [silent MUST be 0]")

print("\nCASE 3: ordinary non-straddling boxes (mono form delegates to affine; identical behaviour)")
import aar_sphere as A
ok=0; mismatch=0
for _ in range(4000):
    for name,mono,aff,gen in (("atan",M.aa_atan_mono,A.aa_atan,lambda:(random.uniform(0.1,2.0),random.uniform(1e-3,0.1))),
                              ("acos",M.aa_acos_mono,A.aa_acos,lambda:(random.uniform(0.1,0.8),random.uniform(1e-3,0.05)))):
        c,rad=gen()
        if not (c-rad>0): continue   # non-straddling (same sign)
        AAr._n=[0]; xm=AAr.var(c,rad); rm=mono(xm).iv()
        AAr._n=[0]; xa=AAr.var(c,rad); ra=aff(xa).iv()
        if abs(rm[0]-ra[0])<1e-12 and abs(rm[1]-ra[1])<1e-12: ok+=1
        else: mismatch+=1
print(f"  non-straddling: {ok} identical to affine, {mismatch} mismatches  [mismatch MUST be 0: mono delegates to affine]")
