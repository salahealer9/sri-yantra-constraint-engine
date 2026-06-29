"""
probe_f4_rigorous.py — RIGOROUS degree-2 Taylor enclosure of F4 via the verified
second-order dual (dual2_sphere.D2). Same method as F3:
    F4(x) in F4(x0) + gradF4(x0).Δ + 1/2 Δ^T H0 Δ + R3
point value/grad/POINT Hessian H0 from a zero-radius dual; quadratic uses H0 with
one-sided Δ_i^2 in [0,r_i^2]; R3 (box-dual Hessian SPREAD, O(r^3)) bounds the remainder.
Reports BOTH raw T2/AA radius AND the deployable UNION (AA OR T2) radius, full grid,
with a soundness harness. F4 shares F3's iso form but has a deeper chain (more AA
looseness headroom) -- the decisive test of the second-order-payoff hypothesis.
"""
import sys, math, os, random, itertools, statistics
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

def f4_chain(b,c,d,e,g,h,FN):
    sin,cos,tan,atan,acos=FN.sin,FN.cos,FN.tan,FN.atan,FN.acos
    r=HALF-h
    x1=acos(cos(r)/cos(c)); x2=acos(cos(r)/cos(d))
    x3=atan(sin(r-c)/sin(r+d)*tan(x2)); x4=atan(sin(r-d)/sin(r+c)*tan(x1))
    x5=atan(sin(b)/sin(b+c+d)*tan(x4)); x6=atan(sin(e)/sin(c+d+e)*tan(x3))
    # v9
    S9=r+d; Q9=(sin(c+d)/sin(r+d))*(tan(x2)/tan(x5))
    U9=atan(sin(S9)/(Q9+cos(S9))); v9=r-U9-c
    # v8, x10 -> v12
    S8=r+g; Q8=(sin(d+g)/sin(r+c))*(tan(x1)/tan(x6))
    U8=atan(sin(S8)/(Q8+cos(S8))); v8=r-U8-d
    x10=atan(sin(b+c-g)/sin(b+c+d)*tan(x4))
    S12=d+g+v8; Q12=(sin(d+g+v8)/sin(d+g))*(tan(x6)/tan(x10))
    U12=atan(sin(S12)/(Q12+cos(S12))); v12=d+g-U12
    x13=atan(sin(e+v12)/sin(c+d+e)*tan(x3))
    return cos(c+d+v9-v12)-cos(2*x13)/cos(x13)

def f4_val(x): return RAO.constraints(*x)[K]

def f4_taylor2_enclosure(x0, rad):
    r=[rad]*6
    AAr._n=[0]
    try: Fp=f4_chain(*[D.D2.var(k,x0[k],0.0) for k in range(6)], D.FN2)
    except Exception: return None
    f0_lo,f0_hi=Fp.v.iv(); g_iv=[Fp.g[i].iv() for i in range(6)]
    H0=[[Fp.H[i][j].iv() for j in range(6)] for i in range(6)]
    AAr._n=[0]
    try: Fb=f4_chain(*[D.D2.var(k,x0[k],r[k]) for k in range(6)], D.FN2)
    except Exception: return None
    HX=[[Fb.H[i][j].iv() for j in range(6)] for i in range(6)]
    lo=f0_lo; hi=f0_hi
    for i in range(6):
        glo,ghi=g_iv[i]; m=max(abs(glo),abs(ghi))*r[i]; lo-=m; hi+=m
    for i in range(6):
        a,b=H0[i][i]; t_a=0.5*a*r[i]*r[i]; t_b=0.5*b*r[i]*r[i]
        lo+=min(t_a,t_b,0.0); hi+=max(t_a,t_b,0.0)
    for i in range(6):
        for j in range(i+1,6):
            a,b=H0[i][j]; m=max(abs(a),abs(b))*r[i]*r[j]; lo-=m; hi+=m
    for i in range(6):
        for j in range(6):
            hlo,hhi=HX[i][j]; a,b=H0[i][j]
            w=max(abs(hlo-b),abs(hhi-a)); rr=r[i]*r[i] if i==j else r[i]*r[j]
            m=0.5*w*rr; lo-=m; hi+=m
    return (lo,hi)

def aa_f4(x0, rad):
    AAr._n=[0]
    try: F=cone_F(*[AAr.var(x0[i],rad) for i in range(6)], AA_FN)
    except Exception: return None
    return F[K].iv()

if __name__=='__main__':
    # --- chain sanity ---
    x0=[0.45,0.40,0.50,0.45,0.30,0.35]
    import math as M
    class FL:
        sin=staticmethod(M.sin);cos=staticmethod(M.cos);tan=staticmethod(M.tan)
        atan=staticmethod(M.atan);acos=staticmethod(M.acos)
    print('chain F4 vs RAO:', f4_chain(*x0,FL), RAO.constraints(*x0)[K],
          '| match:', abs(f4_chain(*x0,FL)-RAO.constraints(*x0)[K])<1e-12)
    # --- dual grad/Hess verification vs finite difference ---
    AAr._n=[0]; Fd=f4_chain(*[D.D2.var(k,x0[k],0.0) for k in range(6)], D.FN2)
    g_dual=[Fd.g[i].c for i in range(6)]; H_dual=[[Fd.H[i][j].c for j in range(6)] for i in range(6)]
    dd=1e-5; g_fd=[0]*6; H_fd=[[0]*6 for _ in range(6)]
    for i in range(6):
        xp=list(x0);xm=list(x0);xp[i]+=dd;xm[i]-=dd; g_fd[i]=(f4_val(xp)-f4_val(xm))/(2*dd)
    for i in range(6):
        for j in range(6):
            a=list(x0);a[i]+=dd;a[j]+=dd; bb=list(x0);bb[i]+=dd;bb[j]-=dd
            cc=list(x0);cc[i]-=dd;cc[j]+=dd; ee=list(x0);ee[i]-=dd;ee[j]-=dd
            H_fd[i][j]=(f4_val(a)-f4_val(bb)-f4_val(cc)+f4_val(ee))/(4*dd*dd)
    gerr=max(abs(g_dual[i]-g_fd[i]) for i in range(6))
    herr=max(abs(H_dual[i][j]-H_fd[i][j]) for i in range(6) for j in range(6))
    print('max|grad_dual-grad_fd| = %.2e | GRAD OK: %s'%(gerr,gerr<1e-6))
    print('max|Hess_dual-Hess_fd| = %.2e | HESS OK: %s'%(herr,herr<1e-3))
    print()

    # --- SAFETY HARNESS (random sampling) ---
    print('SAFETY HARNESS (random sampling)')
    random.seed(20260629)
    sf=0; ck=0; worst=0.0
    for _ in range(8000):
        if ck>=80: break
        c=random.uniform(0.3,0.85); d=random.uniform(0.3,0.85); h=random.uniform(0.2,0.5)
        if h+c>HALF-0.1 or h+d>HALF-0.1: continue
        b=random.uniform(0.2,0.6); e=random.uniform(0.2,0.6); g=random.uniform(0.1,0.5)
        rad=random.choice([0.005,0.01,0.02,0.03]); x0b=[b,c,d,e,g,h]
        if not all(B[i][0]<=x0b[i]-rad and x0b[i]+rad<=B[i][1] for i in range(6)): continue
        enc=f4_taylor2_enclosure(x0b,rad)
        if enc is None: continue
        ck+=1
        for _ in range(120):
            pt=[x0b[i]+random.uniform(-rad,rad) for i in range(6)]
            try: fv=f4_val(pt)
            except Exception: continue
            if fv<enc[0]-1e-9 or fv>enc[1]+1e-9:
                sf+=1; worst=max(worst,max(enc[0]-fv,fv-enc[1])); break
    print('  boxes %d | soundness failures %d (worst %.2e) | SOUND: %s'%(ck,sf,worst,sf==0))
    print()

    # --- EXCLUSION-RADIUS benchmark (full grid): AA vs T2(F4) vs UNION(AA or T2) ---
    print('EXCLUSION-RADIUS (full grid): AA vs T2(F4) vs UNION(AA or T2)')
    random.seed(20260629)   # re-seed so points are reproducible independent of the harness
    radii=[0.05,0.04,0.03,0.02,0.015,0.01,0.005,0.002]
    def largest(x0b, fn):
        if x0b[5]+x0b[1]>HALF-0.05 or x0b[5]+x0b[2]>HALF-0.05: return None
        for rr in radii:
            if not all(B[i][0]<=x0b[i]-rr and x0b[i]+rr<=B[i][1] for i in range(6)): continue
            v=fn(x0b,rr)
            if v is None: continue
            if not (v[0]<=0<=v[1]): return rr
        return None
    got=0; ge=0; t2_ratios=[]; un_ratios=[]; aa_only=0; t2_only=0
    print('  %-22s %-7s %-7s %-7s'%('point(c,d,h)','AA','T2','UNION'))
    for _ in range(20000):
        if got>=12: break
        c=random.uniform(0.3,0.85); d=random.uniform(0.3,0.85); h=random.uniform(0.2,0.5)
        if h+c>HALF-0.1 or h+d>HALF-0.1: continue
        b=random.uniform(0.2,0.6); e=random.uniform(0.2,0.6); g=random.uniform(0.1,0.5)
        x0b=[b,c,d,e,g,h]
        ra=largest(x0b,aa_f4); rt=largest(x0b,f4_taylor2_enclosure)
        if ra is None and rt is None: continue
        got+=1; un=max(ra or 0, rt or 0)
        if rt and (not ra or rt>=ra): ge+=1
        if ra and not rt: aa_only+=1
        if rt and not ra: t2_only+=1
        if ra and rt: t2_ratios.append(rt/ra)
        if ra: un_ratios.append(un/ra)
        print('  (%.3f,%.3f,%.3f)%s %-7s %-7s %-7s'%(c,d,h,' '*3,
              '%.3g'%ra if ra else 'none','%.3g'%rt if rt else 'none','%.3g'%un if un else 'none'))
    print()
    print('  T2 >= AA: %d/%d | AA-only (T2 regressed): %d | T2-only (AA failed): %d'%(ge,got,aa_only,t2_only))
    if t2_ratios: print('  RAW   median T2/AA = %.2fx | mean %.2fx'%(statistics.median(t2_ratios),statistics.mean(t2_ratios)))
    if un_ratios: print('  UNION median U/AA  = %.2fx | mean %.2fx (deployable)'%(statistics.median(un_ratios),statistics.mean(un_ratios)))
    print('  COMPARE F3 raw median 1.33x. Hypothesis (looser->more gain): REFUTED if F4 ~1.0x.')
