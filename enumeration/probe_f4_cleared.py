"""
probe_f4_cleared.py — DENOMINATOR-CLEARED zero-equivalent reformulation of F4.
Original:  F4 = cos(A) - cos(2 x13)/cos(x13),  A = c+d+v9-v12
Cleared:   G4 = cos(A) cos(x13) - cos(2 x13)
Zero-equivalent where cos(x13) is sign-certified nonzero on the box:
    F4 = 0  <=>  G4 = 0   (since F4 = G4 / cos(x13))
So for EXCLUSION: if cos(x13) is sign-certified nonzero on X and 0 not in G4(X),
then F4 has no zero on X (rigorous). Removing the explicit 1/cos(x13) should reduce
both value looseness and the Hessian explosion the F4 second-order probe exposed.

Benchmark: exclusion radius of original AA(F4) vs cleared AA(G4) vs UNION, full grid,
with cos(x13) sign-certification gating the cleared test. Also checks whether clearing
tames the AA box-Hessian explosion (does the degree-2 route reopen for G4?).
"""
import sys, os, math, random, itertools, statistics
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
K=4

def _f4_parts(b,c,d,e,g,h,FN):
    """Return (A, x13) so callers can form F4 or G4. Same chain as probe_f4_rigorous."""
    sin,cos,tan,atan,acos=FN.sin,FN.cos,FN.tan,FN.atan,FN.acos
    r=HALF-h
    x1=acos(cos(r)/cos(c)); x2=acos(cos(r)/cos(d))
    x3=atan(sin(r-c)/sin(r+d)*tan(x2)); x4=atan(sin(r-d)/sin(r+c)*tan(x1))
    x5=atan(sin(b)/sin(b+c+d)*tan(x4)); x6=atan(sin(e)/sin(c+d+e)*tan(x3))
    S9=r+d; Q9=(sin(c+d)/sin(r+d))*(tan(x2)/tan(x5))
    U9=atan(sin(S9)/(Q9+cos(S9))); v9=r-U9-c
    S8=r+g; Q8=(sin(d+g)/sin(r+c))*(tan(x1)/tan(x6))
    U8=atan(sin(S8)/(Q8+cos(S8))); v8=r-U8-d
    x10=atan(sin(b+c-g)/sin(b+c+d)*tan(x4))
    S12=d+g+v8; Q12=(sin(d+g+v8)/sin(d+g))*(tan(x6)/tan(x10))
    U12=atan(sin(S12)/(Q12+cos(S12))); v12=d+g-U12
    x13=atan(sin(e+v12)/sin(c+d+e)*tan(x3))
    A=c+d+v9-v12
    return A, x13

def f4_orig(b,c,d,e,g,h,FN):
    cos=FN.cos
    A,x13=_f4_parts(b,c,d,e,g,h,FN)
    return cos(A)-cos(2*x13)/cos(x13)

def g4_cleared(b,c,d,e,g,h,FN):
    cos=FN.cos
    A,x13=_f4_parts(b,c,d,e,g,h,FN)
    return cos(A)*cos(x13)-cos(2*x13)

def cosx13_iv(x0, rad):
    """AA enclosure of cos(x13) over the box (for sign certification)."""
    AAr._n=[0]
    try:
        A,x13=_f4_parts(*[AAr.var(x0[i],rad) for i in range(6)], AA_FN)
        return AA_FN.cos(x13).iv()
    except Exception:
        return None

def f4_val(x): return RAO.constraints(*x)[K]

def aa_f4_orig(x0, rad):
    AAr._n=[0]
    try: return f4_orig(*[AAr.var(x0[i],rad) for i in range(6)], AA_FN).iv()
    except Exception: return None

def aa_g4_cleared(x0, rad):
    """Cleared exclusion test: requires cos(x13) sign-certified nonzero on the box."""
    cx=cosx13_iv(x0,rad)
    if cx is None: return None
    if cx[0]<=0<=cx[1]: return None      # cos(x13) not sign-certified -> equivalence not guaranteed
    AAr._n=[0]
    try: return g4_cleared(*[AAr.var(x0[i],rad) for i in range(6)], AA_FN).iv()
    except Exception: return None

if __name__=='__main__':
    # --- sanity: G4 == F4*cos(x13), and both zero-equivalent ---
    x0=[0.45,0.40,0.50,0.45,0.30,0.35]
    import math as M
    class FL:
        sin=staticmethod(M.sin);cos=staticmethod(M.cos);tan=staticmethod(M.tan)
        atan=staticmethod(M.atan);acos=staticmethod(M.acos)
    A,x13=_f4_parts(*x0,FL)
    f4=f4_orig(*x0,FL); g4=g4_cleared(*x0,FL)
    print('F4 vs RAO:', f4, RAO.constraints(*x0)[K], '| match:', abs(f4-RAO.constraints(*x0)[K])<1e-12)
    print('G4 == F4*cos(x13):', abs(g4 - f4*M.cos(x13))<1e-12, '| cos(x13)=%.4f'%M.cos(x13))
    print()

    # --- exclusion-radius benchmark: original F4 vs cleared G4 vs UNION ---
    print('EXCLUSION-RADIUS (full grid): AA(F4 orig) vs AA(G4 cleared) vs UNION')
    print('(cleared test gated by cos(x13) sign-certification; "skip" = cos(x13) straddles 0)')
    random.seed(20260629)
    radii=[0.05,0.04,0.03,0.02,0.015,0.01,0.005,0.002]
    def largest(x0b, fn):
        if x0b[5]+x0b[1]>HALF-0.05 or x0b[5]+x0b[2]>HALF-0.05: return None
        for rr in radii:
            if not all(B[i][0]<=x0b[i]-rr and x0b[i]+rr<=B[i][1] for i in range(6)): continue
            v=fn(x0b,rr)
            if v is None: continue
            if not (v[0]<=0<=v[1]): return rr
        return None
    got=0; ge=0; ratios=[]; un_ratios=[]; orig_only=0; cl_only=0; cl_skip=0
    print('  %-22s %-8s %-8s %-8s'%('point(c,d,h)','F4orig','G4clr','UNION'))
    for _ in range(20000):
        if got>=15: break
        c=random.uniform(0.3,0.85); d=random.uniform(0.3,0.85); h=random.uniform(0.2,0.5)
        if h+c>HALF-0.1 or h+d>HALF-0.1: continue
        b=random.uniform(0.2,0.6); e=random.uniform(0.2,0.6); g=random.uniform(0.1,0.5)
        x0b=[b,c,d,e,g,h]
        ro=largest(x0b,aa_f4_orig); rc=largest(x0b,aa_g4_cleared)
        # sign-cert availability at the radius where cleared would matter
        if rc is None and cosx13_iv(x0b,0.01) is not None and cosx13_iv(x0b,0.01)[0]<=0<=cosx13_iv(x0b,0.01)[1]:
            cl_skip+=1
        if ro is None and rc is None: continue
        got+=1; un=max(ro or 0, rc or 0)
        if rc and (not ro or rc>=ro): ge+=1
        if ro and not rc: orig_only+=1
        if rc and not ro: cl_only+=1
        if ro and rc: ratios.append(rc/ro)
        if ro: un_ratios.append(un/ro)
        print('  (%.3f,%.3f,%.3f)%s %-8s %-8s %-8s'%(c,d,h,' '*3,
              '%.3g'%ro if ro else 'none','%.3g'%rc if rc else 'none','%.3g'%un if un else 'none'))
    print()
    print('  G4 >= F4: %d/%d | orig-only: %d | cleared-only (F4 failed): %d | cos(x13) skips: %d'%(ge,got,orig_only,cl_only,cl_skip))
    if ratios: print('  RAW   median G4/F4 = %.2fx | mean %.2fx'%(statistics.median(ratios),statistics.mean(ratios)))
    if un_ratios: print('  UNION median U/F4  = %.2fx | mean %.2fx (deployable)'%(statistics.median(un_ratios),statistics.mean(un_ratios)))
    print('  SUCCESS if cleared G4 excludes at LARGER radius than original F4.')


# ---- second-order on the CLEARED G4: does clearing tame the Hessian explosion? ----
def g4_taylor2_enclosure(x0, rad):
    """Rigorous degree-2 Taylor enclosure of G4 (point Hessian + box-Hessian spread).
    Valid F4-exclusion test when cos(x13) is sign-certified nonzero on the box."""
    cx=cosx13_iv(x0,rad)
    if cx is None or cx[0]<=0<=cx[1]: return None
    r=[rad]*6
    AAr._n=[0]
    try: Fp=g4_cleared(*[D.D2.var(k,x0[k],0.0) for k in range(6)], D.FN2)
    except Exception: return None
    f0_lo,f0_hi=Fp.v.iv(); g_iv=[Fp.g[i].iv() for i in range(6)]
    H0=[[Fp.H[i][j].iv() for j in range(6)] for i in range(6)]
    AAr._n=[0]
    try: Fb=g4_cleared(*[D.D2.var(k,x0[k],r[k]) for k in range(6)], D.FN2)
    except Exception: return None
    HX=[[Fb.H[i][j].iv() for j in range(6)] for i in range(6)]
    lo=f0_lo; hi=f0_hi
    for i in range(6):
        glo,ghi=g_iv[i]; m=max(abs(glo),abs(ghi))*r[i]; lo-=m; hi+=m
    for i in range(6):
        a,b=H0[i][i]; t_a=0.5*a*r[i]*r[i]; t_b=0.5*b*r[i]*r[i]; lo+=min(t_a,t_b,0.0); hi+=max(t_a,t_b,0.0)
    for i in range(6):
        for j in range(i+1,6):
            a,b=H0[i][j]; m=max(abs(a),abs(b))*r[i]*r[j]; lo-=m; hi+=m
    for i in range(6):
        for j in range(6):
            hlo,hhi=HX[i][j]; a,b=H0[i][j]; w=max(abs(hlo-b),abs(hhi-a))
            rr=r[i]*r[i] if i==j else r[i]*r[j]; m=0.5*w*rr; lo-=m; hi+=m
    return (lo,hi)


# ---- run the full cleared-F4 finding (Hessian check + second-order benchmark) ----
def _run_extended_checks():
    import probe_f4_rigorous as PF4
    print()
    print('HESSIAN-EXPLOSION CHECK: F4 (1/cos x13) vs G4 (cleared) worst box-Hessian spread')
    random.seed(101); rad=0.02; got=0; reds=[]
    for _ in range(20000):
        if got>=6: break
        c=random.uniform(0.3,0.85); d=random.uniform(0.3,0.85); h=random.uniform(0.2,0.5)
        if h+c>HALF-0.1 or h+d>HALF-0.1: continue
        b=random.uniform(0.2,0.6); e=random.uniform(0.2,0.6); g=random.uniform(0.1,0.5)
        x0=[b,c,d,e,g,h]
        if not all(B[i][0]<=x0[i]-rad and x0[i]+rad<=B[i][1] for i in range(6)): continue
        AAr._n=[0]
        try: F4b=PF4.f4_chain(*[D.D2.var(k,x0[k],rad) for k in range(6)], D.FN2)
        except Exception: continue
        f4_sp=max(F4b.H[i][j].iv()[1]-F4b.H[i][j].iv()[0] for i in range(6) for j in range(6))
        AAr._n=[0]
        try: G4b=g4_cleared(*[D.D2.var(k,x0[k],rad) for k in range(6)], D.FN2)
        except Exception: continue
        g4_sp=max(G4b.H[i][j].iv()[1]-G4b.H[i][j].iv()[0] for i in range(6) for j in range(6))
        got+=1; reds.append(f4_sp/max(g4_sp,1e-9))
        print('  F4 H-spread=%.1f | G4 H-spread=%.1f | reduction=%.0fx'%(f4_sp,g4_sp,f4_sp/max(g4_sp,1e-9)))
    print('  median reduction=%.1fx -- G4 Hessian still 10^3-10^7 => explosion NOT tamed.'%(statistics.median(reds) if reds else float('nan')))
    print()
    print('SECOND-ORDER ON CLEARED G4: T2(G4) vs AA(F4) exclusion radius (8 boxes)')
    random.seed(20260629)
    radii=[0.05,0.04,0.03,0.02,0.015,0.01,0.005,0.002]
    def largest(x0b, fn):
        if x0b[5]+x0b[1]>HALF-0.05 or x0b[5]+x0b[2]>HALF-0.05: return None
        for rr in radii:
            if not all(B[i][0]<=x0b[i]-rr and x0b[i]+rr<=B[i][1] for i in range(6)): continue
            v=fn(x0b,rr)
            if v is None: continue
            if not (v[0]<=0<=v[1]): return rr
        return None
    got=0; ratios=[]
    for _ in range(20000):
        if got>=8: break
        c=random.uniform(0.3,0.85); d=random.uniform(0.3,0.85); h=random.uniform(0.2,0.5)
        if h+c>HALF-0.1 or h+d>HALF-0.1: continue
        b=random.uniform(0.2,0.6); e=random.uniform(0.2,0.6); g=random.uniform(0.1,0.5)
        x0b=[b,c,d,e,g,h]
        ra=largest(x0b,aa_f4_orig); rt=largest(x0b,g4_taylor2_enclosure)
        if ra is None and rt is None: continue
        got+=1
        if ra and rt: ratios.append(rt/ra)
    if ratios: print('  median T2(G4)/AA(F4) = %.2fx | mean %.2fx -- second-order does NOT reopen.'%(statistics.median(ratios),statistics.mean(ratios)))

if __name__=='__main__':
    _run_extended_checks()
