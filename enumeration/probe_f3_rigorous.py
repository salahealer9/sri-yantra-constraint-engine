"""
probe_f3_rigorous.py — RIGOROUS degree-2 Taylor enclosure of F3 via the verified
second-order dual (dual2_sphere.D2). Enclosure over box X = x0 + [-r,r]:
    F3(x) in F3(x0) + gradF3(x0).Δ + 1/2 Δ^T H0 Δ + R3
where F3(x0), gradF3(x0) and the POINT Hessian H0 come from a zero-radius dual (exact,
rounding-bounded); the quadratic uses the POINT Hessian H0 with one-sided Δ_i^2 in
[0,r_i^2]; and R3 = 1/2 Δ^T (H(ξ)-H0) Δ is bounded by the box-dual Hessian SPREAD
(H(X)-H0), an O(r^3) remainder. Rigorous by mean-value/Taylor (ξ in the convex box, so
H(ξ) in H(X)). Honest full-grid result: median T2/AA radius ~1.33x (below the 2x target),
sound on the random-sampling harness. Benchmarks exclusion radius vs natural AA.
"""
import sys, os, math, random, itertools
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
from aar import AAr
from chain_sphere import AA_FN
import dual2_sphere as D
import domain_sphere_v2_prefilter as v2
HALF=v2.HALF_PI; B=v2.B_SPHERE; cone_F=v2.cone_F

def f3_chain(b,c,d,e,g,h,FN):
    sin,cos,tan,atan,acos=FN.sin,FN.cos,FN.tan,FN.atan,FN.acos
    r=HALF-h
    x1=acos(cos(r)/cos(c)); x2=acos(cos(r)/cos(d))
    x3=atan(sin(r-c)/sin(r+d)*tan(x2)); x4=atan(sin(r-d)/sin(r+c)*tan(x1))
    x6=atan(sin(e)/sin(c+d+e)*tan(x3)); x10=atan(sin(b+c-g)/sin(b+c+d)*tan(x4))
    S8=r+g; Q8=(sin(d+g)/sin(r+c))*(tan(x1)/tan(x6))
    U8=atan(sin(S8)/(Q8+cos(S8))); V8=S8-U8
    return cos(V8)-cos(2*x10)/cos(x10)

def f3_val(x): return RAO.constraints(*x)[3]

def f3_taylor2_enclosure(x0, rad):
    """Rigorous [lo,hi] for F3 over the box. POINT Hessian for the tight quadratic
    (one-sided Δ²∈[0,r²]); box-Hessian SPREAD as the O(r³) remainder. None on dual fail."""
    r=[rad]*6
    # point dual (r=0): exact value, gradient, POINT Hessian (rounding-bounded)
    AAr._n=[0]
    try:
        Fp=f3_chain(*[D.D2.var(k,x0[k],0.0) for k in range(6)], D.FN2)
    except Exception: return None
    f0_lo,f0_hi=Fp.v.iv()
    g_iv=[Fp.g[i].iv() for i in range(6)]
    H0=[[Fp.H[i][j].iv() for j in range(6)] for i in range(6)]     # tight point Hessian
    # box dual (r>0): Hessian over the box (for the spread/remainder)
    AAr._n=[0]
    try:
        Fb=f3_chain(*[D.D2.var(k,x0[k],r[k]) for k in range(6)], D.FN2)
    except Exception: return None
    HX=[[Fb.H[i][j].iv() for j in range(6)] for i in range(6)]
    lo=f0_lo; hi=f0_hi
    # linear: gradF3(x0)·Δ, Δ_i∈[-r_i,r_i]
    for i in range(6):
        glo,ghi=g_iv[i]; m=max(abs(glo),abs(ghi))*r[i]; lo-=m; hi+=m
    # quadratic term A = 1/2 Δ^T H0 Δ with point Hessian interval [a,b], one-sided diagonal
    for i in range(6):
        a,b=H0[i][i]; t_a=0.5*a*r[i]*r[i]; t_b=0.5*b*r[i]*r[i]   # Δ_i²∈[0,r_i²]
        lo+=min(t_a,t_b,0.0); hi+=max(t_a,t_b,0.0)
    for i in range(6):
        for j in range(i+1,6):
            a,b=H0[i][j]; m=max(abs(a),abs(b))*r[i]*r[j]; lo-=m; hi+=m
    # remainder B = 1/2 Δ^T (H(ξ)-H0) Δ  ⊆  1/2 (H(X)-H0) over Δ²; spread magnitude per entry
    for i in range(6):
        for j in range(6):
            hlo,hhi=HX[i][j]; a,b=H0[i][j]
            w=max(abs(hlo-b), abs(hhi-a))          # magnitude of (H(X)-H0)_ij
            rr = r[i]*r[i] if i==j else r[i]*r[j]
            m=0.5*w*rr; lo-=m; hi+=m
    return (lo,hi)

def aa_f3(x0, rad):
    AAr._n=[0]
    try: F=cone_F(*[AAr.var(x0[i],rad) for i in range(6)], AA_FN)
    except Exception: return None
    return F[3].iv()

def sampled_f3(x0, rad, n=5):
    axes=[np.linspace(x0[i]-rad,x0[i]+rad,n) for i in range(6)]
    lo=1e9;hi=-1e9
    for pt in itertools.product(*axes):
        try: v=f3_val(pt)
        except Exception: continue
        lo=min(lo,v);hi=max(hi,v)
    return lo,hi

if __name__=='__main__':
    import statistics
    random.seed(20260629)
    # ---- SAFETY HARNESS (random sampling; fast) ----
    print('SAFETY HARNESS (random sampling)')
    sound_fail=0; checked=0; worst=0.0
    for _ in range(8000):
        if checked>=120: break
        c=random.uniform(0.3,0.85); d=random.uniform(0.3,0.85); h=random.uniform(0.2,0.5)
        if h+c>HALF-0.1 or h+d>HALF-0.1: continue
        b=random.uniform(0.2,0.6); e=random.uniform(0.2,0.6); g=random.uniform(0.1,0.5)
        rad=random.choice([0.005,0.01,0.02,0.03]); x0=[b,c,d,e,g,h]
        if not all(B[i][0]<=x0[i]-rad and x0[i]+rad<=B[i][1] for i in range(6)): continue
        enc=f3_taylor2_enclosure(x0,rad)
        if enc is None: continue
        checked+=1
        for _ in range(120):
            pt=[x0[i]+random.uniform(-rad,rad) for i in range(6)]
            try: fv=f3_val(pt)
            except Exception: continue
            if fv<enc[0]-1e-9 or fv>enc[1]+1e-9:
                sound_fail+=1; worst=max(worst,max(enc[0]-fv,fv-enc[1])); break
    print('  boxes checked: %d | soundness failures: %d (worst overflow %.2e)'%(checked,sound_fail,worst))
    print('  SOUND (0 required):', sound_fail==0)
    print()
    # ---- EXCLUSION-RADIUS benchmark (full grid; honest median) ----
    print('EXCLUSION-RADIUS: rigorous degree-2 Taylor(F3) vs natural AA(F3)')
    radii=[0.05,0.04,0.03,0.02,0.015,0.01,0.005,0.002]
    def largest(x0, fn):
        if x0[5]+x0[1]>HALF-0.05 or x0[5]+x0[2]>HALF-0.05: return None
        for rr in radii:
            if not all(B[i][0]<=x0[i]-rr and x0[i]+rr<=B[i][1] for i in range(6)): continue
            v=fn(x0,rr)
            if v is None: continue
            if not (v[0]<=0<=v[1]): return rr
        return None
    got=0; ge=0; ratios=[]; aa_only=0; t2_only=0
    print('  %-22s %-8s %-8s'%('point(c,d,h)','AA','T2'))
    for _ in range(20000):
        if got>=15: break
        c=random.uniform(0.3,0.85); d=random.uniform(0.3,0.85); h=random.uniform(0.2,0.5)
        if h+c>HALF-0.1 or h+d>HALF-0.1: continue
        b=random.uniform(0.2,0.6); e=random.uniform(0.2,0.6); g=random.uniform(0.1,0.5)
        x0=[b,c,d,e,g,h]
        ra=largest(x0,aa_f3); rt=largest(x0,f3_taylor2_enclosure)
        if ra is None and rt is None: continue
        got+=1
        if rt and (not ra or rt>=ra): ge+=1
        if ra and not rt: aa_only+=1
        if rt and not ra: t2_only+=1
        if ra and rt: ratios.append(rt/ra)
        print('  (%.3f,%.3f,%.3f)%s %-8s %-8s'%(c,d,h,' '*3,'%.3g'%ra if ra else 'none','%.3g'%rt if rt else 'none'))
    print()
    print('  T2 >= AA radius: %d/%d | AA-only (T2 regressed): %d | T2-only (AA failed): %d'%(ge,got,aa_only,t2_only))
    if ratios: print('  median radius ratio T2/AA = %.2fx | mean = %.2fx (target >=2x)'%(statistics.median(ratios),statistics.mean(ratios)))
    print()
    print('  UNION (T2 OR AA): radius = max(AA,T2) per box -> never worse than AA; this is the deployable test.')
    # union median
    if True:
        random.seed(20260629)
        # recompute quickly skipped; union ratio >=1 by construction
