"""
probe_f4_trigpair.py — TAN-FREE / trig-pair reformulation of the F4 cone.
Carry each constructed angle as a (sin,cos) pair (or its tan = pre-atan argument)
instead of forming the angle and re-applying trig. Uses addition/double-angle
identities. Attacks the deep-chain wrapping the node scan localized to the U-nodes
(U8,U9,U12) where Q=(sin/sin)(tan(x_i)/tan(x_j)) accumulates atan->tan round-trips.
Question (first-order only): does a better chain representation make AA tight?
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
import domain_sphere_v2_prefilter as v2
HALF=v2.HALF_PI; B=v2.B_SPHERE; cone_F=v2.cone_F
K=4

# ---- (sin,cos) pair helpers over a generic FN (FN.sin/cos/sqrt etc.) ----
class TP:
    """Trig-pair: carries (s,c) ~ (sin t, cos t). Built so no angle is re-formed."""
    def __init__(s, sin, cos): s.s=sin; s.c=cos
def _sqrt(x, FN): return FN.sqrt(x) if hasattr(FN,'sqrt') else x**0.5

def tp_from_tan(W, FN):
    # t=atan(W) in (-pi/2,pi/2): cos>0. (sin,cos)=(W,1)/sqrt(1+W^2)
    den=_sqrt(1.0+W*W, FN); return TP(W/den, 1.0/den)
def tp_from_acosarg(z, FN):
    # t=acos(z), t in (0,pi): sin>=0. (sin,cos)=(sqrt(1-z^2), z)
    return TP(_sqrt(1.0-z*z, FN), z)
def tp_from_ND(N, D, FN):
    # t=atan(N/D), pair=(N,D)/sqrt(N^2+D^2); sign of cos = sign of D (assume D>0, guarded)
    den=_sqrt(N*N+D*D, FN); return TP(N/den, D/den)
def tp_from_angle(theta, FN):
    # for variable linear combos used as angles: single sin/cos application
    return TP(FN.sin(theta), FN.cos(theta))
def tp_sub(P, Q): return TP(P.s*Q.c - P.c*Q.s, P.c*Q.c + P.s*Q.s)   # P - Q
def tp_add(P, Q): return TP(P.s*Q.c + P.c*Q.s, P.c*Q.c - P.s*Q.s)   # P + Q
def tp_tan(P): return P.s/P.c

def f4_trigpair_value(b,c,d,e,g,h,FN):
    """Return F4 (and G4) built tan-free. FN provides sin,cos,tan,atan,acos,sqrt."""
    sin,cos=FN.sin,FN.cos
    r=HALF-h
    # x1,x2 via acos-arg pairs (cone)
    z1=cos(r)/cos(c); z2=cos(r)/cos(d)
    X1=tp_from_acosarg(z1,FN); X2=tp_from_acosarg(z2,FN)
    t_x1=tp_tan(X1); t_x2=tp_tan(X2)
    # x3,x4,x5,x6 are atan(W): tan = W exactly (no round-trip)
    W3=sin(r-c)/sin(r+d)*t_x2;  t_x3=W3; X3=tp_from_tan(W3,FN)
    W4=sin(r-d)/sin(r+c)*t_x1;  t_x4=W4
    W5=sin(b)/sin(b+c+d)*t_x4;  t_x5=W5
    W6=sin(e)/sin(c+d+e)*t_x3;  t_x6=W6
    # U9 = atan(sin(S9)/(Q9+cos(S9))) ; v9 = r - c - U9
    S9=r+d; Q9=(sin(c+d)/sin(r+d))*(t_x2/t_x5)
    U9=tp_from_ND(sin(S9), Q9+cos(S9), FN)
    rc=tp_from_angle(r-c,FN); V9=tp_sub(rc, U9)          # (sin,cos) of v9 = (r-c) - U9
    # U8 = atan(sin(S8)/(Q8+cos(S8))) ; v8 = r - d - U8
    S8=r+g; Q8=(sin(d+g)/sin(r+c))*(t_x1/t_x6)
    U8=tp_from_ND(sin(S8), Q8+cos(S8), FN)
    rd=tp_from_angle(r-d,FN); V8=tp_sub(rd, U8)          # v8 = (r-d) - U8
    # x10 = atan(W10): tan = W10
    W10=sin(b+c-g)/sin(b+c+d)*t_x4; t_x10=W10
    # U12 = atan(sin(S12)/(Q12+cos(S12))), S12 = d+g+v8 ; v12 = d+g - U12
    # sin(S12),cos(S12) via (d+g) + v8 pair:  dg + V8
    dg=tp_from_angle(d+g,FN); S12pair=tp_add(dg, V8)     # (sin,cos) of d+g+v8
    sinS12=S12pair.s; cosS12=S12pair.c
    # sin(d+g+v8)/sin(d+g): need sin(d+g+v8)=sinS12 ; sin(d+g)=sin(d+g)
    Q12=(sinS12/sin(d+g))*(t_x6/t_x10)
    U12=tp_from_ND(sinS12, Q12+cosS12, FN)
    V12=tp_sub(dg, U12)                                  # v12 = (d+g) - U12
    # x13 = atan(W13), W13 = sin(e+v12)/sin(c+d+e) * t_x3 ; sin(e+v12) via e + v12
    epair=tp_from_angle(e,FN); EV12=tp_add(epair, V12)   # (sin,cos) of e+v12
    W13=(EV12.s/sin(c+d+e))*t_x3                          # tan(x13)=W13
    # F4 = cos(A) - cos(2 x13)/cos(x13),  A = c+d+v9-v12
    # cos(x13)=1/sqrt(1+W13^2) (>0); cos(2x13)=(1-W13^2)/(1+W13^2)
    # => cos(2x13)/cos(x13) = (1-W13^2)/sqrt(1+W13^2)
    sec_term=(1.0-W13*W13)/_sqrt(1.0+W13*W13, FN)
    # A = (c+d) + v9 - v12  -> cos(A) via (c+d) + V9 - V12
    cd=tp_from_angle(c+d,FN); Apair=tp_sub(tp_add(cd, V9), V12)
    cosA=Apair.c
    F4=cosA - sec_term
    G4=cosA*(1.0/_sqrt(1.0+W13*W13, FN)) - (1.0-W13*W13)/(1.0+W13*W13)  # cos A cos x13 - cos 2x13
    return F4, G4, U12.c   # also return cos(U12) for any sign diagnostics

# float FN with sqrt
import math as M
class FL:
    sin=staticmethod(M.sin);cos=staticmethod(M.cos);tan=staticmethod(M.tan)
    atan=staticmethod(M.atan);acos=staticmethod(M.acos);sqrt=staticmethod(M.sqrt)

# ---- AA function-set WITH sqrt (for trig-pair AAr evaluation) ----
class AAFN_SQ:
    sin=staticmethod(AA_FN.sin);cos=staticmethod(AA_FN.cos);tan=staticmethod(AA_FN.tan)
    atan=staticmethod(AA_FN.atan);acos=staticmethod(AA_FN.acos);sqrt=staticmethod(lambda x:x.sqrt())

def aa_orig(x0,rad):
    AAr._n=[0]
    try: return cone_F(*[AAr.var(x0[i],rad) for i in range(6)], AA_FN)[K].iv()
    except Exception: return None
def aa_trigpair(x0,rad):
    AAr._n=[0]
    try: return f4_trigpair_value(*[AAr.var(x0[i],rad) for i in range(6)], AAFN_SQ)[0].iv()
    except Exception: return None
def sampled(x0,rad,n=3):
    axes=[[x0[i]-rad+2*rad*k/(n-1) for k in range(n)] for i in range(6)]
    lo=1e9;hi=-1e9
    for pt in itertools.product(*axes):
        try: v=f4_trigpair_value(*pt,FL)[0]
        except Exception: continue
        lo=min(lo,v);hi=max(hi,v)
    return lo,hi

if __name__=='__main__':
    # (1) POINT verification vs RAO
    pts=[[0.45,0.40,0.50,0.45,0.30,0.35],
         [0.6246238466927992,0.7044304165359816,0.7482768099360514,0.6307397242292889,0.3136386632298885,0.39528],
         [0.5,0.6,0.55,0.4,0.25,0.42]]
    print('(1) POINT verification: trig-pair F4 vs RAO F4')
    for x0 in pts:
        f4tp,_,_=f4_trigpair_value(*x0,FL); rao=RAO.constraints(*x0)[K]
        print('  tp=%.15f rao=%.15f | match=%s'%(f4tp,rao,abs(f4tp-rao)<1e-12))
    print()
    # (2) CONTAINMENT (soundness of trig-pair AA)
    print('(2) CONTAINMENT harness: trig-pair AA must contain random point evals')
    random.seed(13); ck=0; fail=0
    for _ in range(20000):
        if ck>=80: break
        c=random.uniform(0.3,0.85); d=random.uniform(0.3,0.85); h=random.uniform(0.2,0.5)
        if h+c>HALF-0.1 or h+d>HALF-0.1: continue
        b=random.uniform(0.2,0.6); e=random.uniform(0.2,0.6); g=random.uniform(0.1,0.5)
        rad=random.choice([0.005,0.01,0.02]); x0=[b,c,d,e,g,h]
        if not all(B[i][0]<=x0[i]-rad and x0[i]+rad<=B[i][1] for i in range(6)): continue
        enc=aa_trigpair(x0,rad)
        if enc is None: continue
        ck+=1
        for _ in range(60):
            pt=[x0[i]+random.uniform(-rad,rad) for i in range(6)]
            try: v=f4_trigpair_value(*pt,FL)[0]
            except Exception: continue
            if v<enc[0]-1e-9 or v>enc[1]+1e-9: fail+=1; break
    print('  boxes %d | containment failures %d | SOUND: %s'%(ck,fail,fail==0))
    print()
    # (3) WIDTH on non-straddling boxes (isolate wrapping)
    print('(3) WIDTH on non-straddling boxes (rad 0.02): AA_orig vs AA_trigpair vs sampled')
    def straddles(x0,rad):
        r=HALF-x0[5]
        args=[r+x0[2], r+x0[4], r+x0[1], x0[2]+x0[4], x0[1]+x0[2]]
        return any(abs(a-HALF)<rad+0.03 for a in args)
    random.seed(7); rad=0.02; got=0; orig_r=[]; tp_r=[]
    for _ in range(40000):
        if got>=8: break
        c=random.uniform(0.3,0.85); d=random.uniform(0.3,0.85); h=random.uniform(0.2,0.5)
        if h+c>HALF-0.1 or h+d>HALF-0.1: continue
        b=random.uniform(0.2,0.6); e=random.uniform(0.2,0.6); g=random.uniform(0.1,0.5)
        x0=[b,c,d,e,g,h]
        if not all(B[i][0]<=x0[i]-rad and x0[i]+rad<=B[i][1] for i in range(6)): continue
        if straddles(x0,rad): continue
        ao=aa_orig(x0,rad); at=aa_trigpair(x0,rad)
        if ao is None or at is None: continue
        sr=sampled(x0,rad); sw=sr[1]-sr[0]; got+=1
        orig_r.append((ao[1]-ao[0])/max(sw,1e-9)); tp_r.append((at[1]-at[0])/max(sw,1e-9))
    if orig_r: print('  median AA_orig/sampled=%.1fx | AA_trigpair/sampled=%.1fx (LOWER=tighter)'%(statistics.median(orig_r),statistics.median(tp_r)))
    print()
    # (4) EXCLUSION-RADIUS (full grid)
    print('(4) EXCLUSION-RADIUS (full grid): AA(orig) vs AA(trig-pair) vs UNION')
    random.seed(20260629); radii=[0.05,0.04,0.03,0.02,0.015,0.01,0.005,0.002]
    def largest(x0b,fn):
        if x0b[5]+x0b[1]>HALF-0.05 or x0b[5]+x0b[2]>HALF-0.05: return None
        for rr in radii:
            if not all(B[i][0]<=x0b[i]-rr and x0b[i]+rr<=B[i][1] for i in range(6)): continue
            v=fn(x0b,rr)
            if v is None: continue
            if not (v[0]<=0<=v[1]): return rr
        return None
    got=0; ge=0; ratios=[]; un_ratios=[]
    for _ in range(20000):
        if got>=15: break
        c=random.uniform(0.3,0.85); d=random.uniform(0.3,0.85); h=random.uniform(0.2,0.5)
        if h+c>HALF-0.1 or h+d>HALF-0.1: continue
        b=random.uniform(0.2,0.6); e=random.uniform(0.2,0.6); g=random.uniform(0.1,0.5)
        x0b=[b,c,d,e,g,h]
        ro=largest(x0b,aa_orig); rt=largest(x0b,aa_trigpair)
        if ro is None and rt is None: continue
        got+=1; un=max(ro or 0, rt or 0)
        if rt and (not ro or rt>=ro): ge+=1
        if ro and rt: ratios.append(rt/ro)
        if ro: un_ratios.append(un/ro)
    print('  trig-pair >= orig: %d/%d'%(ge,got))
    if ratios: print('  RAW   median trigpair/orig = %.2fx | mean %.2fx'%(statistics.median(ratios),statistics.mean(ratios)))
    if un_ratios: print('  UNION median U/orig = %.2fx | mean %.2fx'%(statistics.median(un_ratios),statistics.mean(un_ratios)))
    print('  NOTE: any exclusion lift is from avoiding the cos(2x13) inflection split, NOT tighter')
    print('        enclosure -- the WIDTH test (3) shows trig-pair is LOOSER than original.')
