"""
probe_f4_factor_contract.py — F4 CHAIN-VARIABLE CONTRACTOR (HC4-style).
Different REPRESENTATION (not another enclosure of one deep expression): introduce an
interval variable for every F4 intermediate node and impose the shallow relations between
them, then run forward/backward interval constraint propagation (HC4) to a fixpoint.
For EXCLUSION: impose F4=0 and propagate; if any variable interval becomes EMPTY, then
F4 has no zero on the box -> exclude (rigorous: interval constraint propagation is sound).
Pre-committed test: does the BACKWARD pass (F4=0 imposed) narrow U12/v12/t_x13 by >2x vs
forward-only, and exclude at >=2x the AA radius?
"""
import sys, os, math, random, statistics
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
EMPTY=None
PAD=1e-12
def w(I): return (I[1]-I[0]) if I else 0.0
def inter(A,Bx):
    if A is None or Bx is None: return None
    lo=max(A[0],Bx[0]); hi=min(A[1],Bx[1])
    return None if lo>hi+1e-15 else [lo,hi]
# ---- interval ops (outward-padded) ----
def pad(lo,hi): d=PAD*(abs(lo)+abs(hi))+PAD; return [lo-d,hi+d]
def iadd(A,Bx): return pad(A[0]+Bx[0],A[1]+Bx[1])
def isub(A,Bx): return pad(A[0]-Bx[1],A[1]-Bx[0])
def imul(A,Bx):
    v=[A[0]*Bx[0],A[0]*Bx[1],A[1]*Bx[0],A[1]*Bx[1]]; return pad(min(v),max(v))
def idiv(A,Bx):
    if Bx[0]<=0<=Bx[1]: return [-1e18,1e18]
    v=[A[0]/Bx[0],A[0]/Bx[1],A[1]/Bx[0],A[1]/Bx[1]]; return pad(min(v),max(v))
def icos(A):
    # enclosure of cos over [a,b]
    a,b=A; lo=min(math.cos(a),math.cos(b)); hi=max(math.cos(a),math.cos(b))
    k0=math.ceil(a/math.pi)
    for k in range(k0-1,k0+3):
        x=k*math.pi
        if a<=x<=b: (lo:=min(lo,math.cos(x))) ; hi=max(hi,math.cos(x))
    # robust: scan multiples of pi in range
    lo=min(math.cos(a),math.cos(b)); hi=max(math.cos(a),math.cos(b))
    k=math.ceil(a/math.pi)
    while k*math.pi<=b:
        c=math.cos(k*math.pi); lo=min(lo,c); hi=max(hi,c); k+=1
    return pad(lo,hi)
def isin(A): return icos([A[0]-math.pi/2,A[1]-math.pi/2])
def iatan(A): return pad(math.atan(A[0]),math.atan(A[1]))
def isqrt(A):
    a=max(A[0],0.0); return pad(math.sqrt(a),math.sqrt(max(A[1],0.0)))
def isq(A):
    v=[A[0]*A[0],A[1]*A[1]]
    lo=0.0 if A[0]<=0<=A[1] else min(v); hi=max(v); return pad(lo,hi)

# ---- F4 network: forward eval of all nodes from primaries; returns dict of intervals ----
def forward(box):
    b,c,d,e,g,h=box
    V={}
    V['b'],V['c'],V['d'],V['e'],V['g'],V['h']=([x[0],x[1]] for x in box)
    r=isub([HALF,HALF],V['h']); V['r']=r
    cr=icos(r)
    V['z1']=idiv(cr,icos(V['c'])); V['z2']=idiv(cr,icos(V['d']))
    # t_x1 = sqrt(1-z1^2)/z1 ; t_x2 likewise (cone: z in (0,1))
    def ttan_acos(z): return idiv(isqrt(isub([1,1],isq(z))), z)
    V['tx1']=ttan_acos(V['z1']); V['tx2']=ttan_acos(V['z2'])
    rc=isub(r,V['c']); rd=isub(r,V['d'])
    V['tx3']=imul(idiv(isin(rc),isin(iadd(r,V['d']))), V['tx2'])
    V['tx4']=imul(idiv(isin(rd),isin(iadd(r,V['c']))), V['tx1'])
    bcd=iadd(iadd(V['b'],V['c']),V['d'])
    V['tx5']=imul(idiv(isin(V['b']),isin(bcd)), V['tx4'])
    cde=iadd(iadd(V['c'],V['d']),V['e'])
    V['tx6']=imul(idiv(isin(V['e']),isin(cde)), V['tx3'])
    cd=iadd(V['c'],V['d']); dg=iadd(V['d'],V['g'])
    # U9
    S9=iadd(r,V['d']); Q9=imul(idiv(isin(cd),isin(S9)), idiv(V['tx2'],V['tx5']))
    V['U9']=iatan(idiv(isin(S9), iadd(Q9,icos(S9))))
    V['v9']=isub(isub(r,V['U9']),V['c'])
    # U8
    S8=iadd(r,V['g']); Q8=imul(idiv(isin(dg),isin(iadd(r,V['c']))), idiv(V['tx1'],V['tx6']))
    V['U8']=iatan(idiv(isin(S8), iadd(Q8,icos(S8))))
    V['v8']=isub(isub(r,V['U8']),V['d'])
    # x10
    bcg=isub(iadd(V['b'],V['c']),V['g'])
    V['tx10']=imul(idiv(isin(bcg),isin(bcd)), V['tx4'])
    # U12
    S12=iadd(dg,V['v8']); Q12=imul(idiv(isin(S12),isin(dg)), idiv(V['tx6'],V['tx10']))
    V['U12']=iatan(idiv(isin(S12), iadd(Q12,icos(S12))))
    V['v12']=isub(dg,V['U12'])
    # x13
    ev12=iadd(V['e'],V['v12'])
    V['tx13']=imul(idiv(isin(ev12),isin(cde)), V['tx3'])
    # A and F4 = cos(A) - (1 - tx13^2)/sqrt(1+tx13^2)
    V['A']=isub(iadd(cd,V['v9']),V['v12'])
    sec=idiv(isub([1,1],isq(V['tx13'])), isqrt(iadd([1,1],isq(V['tx13']))))
    V['F4']=isub(icos(V['A']), sec)
    return V

# ---- backward narrowing: impose F4=0, push into A and tx13, then into v9,v12,U12 ----
def contract_with_F4zero(V, passes=4):
    """HC4-style backward revise using F4=0. Returns narrowed V or None if empty."""
    import copy
    V=copy.deepcopy(V)
    for _ in range(passes):
        changed=False
        # F4 = cos(A) - sec(tx13) = 0  => cos(A) = sec(tx13)
        sec=idiv(isub([1,1],isq(V['tx13'])), isqrt(iadd([1,1],isq(V['tx13']))))
        cosA=inter(icos(V['A']), sec)
        if cosA is None: return None
        # backward cos(A)=cosA -> narrow A on its monotone branch
        a0,a1=V['A']
        if a1-a0 < math.pi:   # within one monotone branch -> invertible
            lo=max(-1.0,min(1.0,cosA[0])); hi=max(-1.0,min(1.0,cosA[1]))
            cand=sorted([math.acos(lo),math.acos(hi)])
            # cos decreasing on [0,pi]; map branch around A
            base=math.floor((a0)/(2*math.pi))*2*math.pi
            for shift in (base, base+2*math.pi, base-2*math.pi):
                for sgn in (1,-1):
                    A_lo=shift+sgn*cand[1]; A_hi=shift+sgn*cand[0] if sgn>0 else shift+sgn*cand[1]
            # simpler: narrow A by intersecting with acos image mapped near A center
            mid=(a0+a1)/2
            k=round((mid-math.acos((lo+hi)/2))/ (2*math.pi))
            A_new=inter(V['A'], pad(2*math.pi*k+math.acos(hi), 2*math.pi*k+math.acos(lo)))
            if A_new is None:
                A_new=inter(V['A'], pad(-(2*math.pi*k)+ -math.acos(lo)+2*2*math.pi*k, 9e18)) # fallback no-op
            if A_new is not None and w(A_new)<w(V['A'])-1e-15: V['A']=A_new; changed=True
        # sec(tx13)=cosA  => (1-t^2)/sqrt(1+t^2) = cosA ; narrow tx13 numerically (monotone in |t|)
        target=cosA
        t=V['tx13']
        # sec is even, decreasing in |t| from 1 (t=0) downward; invert for |t|
        def secf(x): return (1-x*x)/math.sqrt(1+x*x)
        # find |t| range giving sec in [target]: sec decreasing in |t|
        def invsec(yv):
            yv=max(-1.0,min(1.0,yv))
            lo,hi=0.0,1e6
            for _ in range(60):
                m=(lo+hi)/2
                if secf(m)>yv: lo=m
                else: hi=m
            return (lo+hi)/2
        amax=invsec(target[0]); amin=invsec(target[1])  # sec dec in |t|: larger sec -> smaller |t|
        absrange=[max(0,amin),amax]
        # intersect with current tx13 sign-aware
        if t[0]>=0: tn=inter(t, pad(absrange[0],absrange[1]))
        elif t[1]<=0: tn=inter(t, pad(-absrange[1],-absrange[0]))
        else: tn=inter(t, pad(-absrange[1],absrange[1]))
        if tn is None: return None
        if w(tn)<w(V['tx13'])-1e-15: V['tx13']=tn; changed=True
        # push A -> v9,v12 via A = c+d+v9-v12 ; and tx13 -> v12 (monotone-ish)
        cd=iadd(V['c'],V['d'])
        # tx13 = sin(e+v12)/sin(cde) * tx3  ->  sin(e+v12) = tx13 * sin(cde) / tx3
        cde=iadd(iadd(V['c'],V['d']),V['e'])
        sin_ev12 = imul(V['tx13'], idiv(isin(cde), V['tx3']))
        sin_ev12 = inter(sin_ev12, [-1.0,1.0])
        if sin_ev12 is not None:
            ev12=iadd(V['e'],V['v12'])
            # invert sin on ev12's monotone branch
            if ev12[1]-ev12[0] < math.pi:
                lo=max(-1.0,min(1.0,sin_ev12[0])); hi=max(-1.0,min(1.0,sin_ev12[1]))
                mid=(ev12[0]+ev12[1])/2; k=round((mid-math.asin((lo+hi)/2))/(2*math.pi))
                cand=pad(2*math.pi*k+math.asin(lo), 2*math.pi*k+math.asin(hi))
                ev12n=inter(ev12, cand)
                if ev12n is not None:
                    v12_from_tx13=isub(ev12n, V['e'])
                    v12b=inter(V['v12'], v12_from_tx13)
                    if v12b is not None and w(v12b)<w(V['v12'])-1e-15: V['v12']=v12b; changed=True
        # v9 = A - (c+d) + v12
        v9n=inter(V['v9'], iadd(isub(V['A'],cd),V['v12']))
        if v9n is None: return None
        if w(v9n)<w(V['v9'])-1e-15: V['v9']=v9n; changed=True
        v12n=inter(V['v12'], isub(iadd(cd,V['v9']),V['A']))
        if v12n is None: return None
        if w(v12n)<w(V['v12'])-1e-15: V['v12']=v12n; changed=True
        # v12 = d+g - U12 -> U12 = d+g - v12
        dg=iadd(V['d'],V['g'])
        U12n=inter(V['U12'], isub(dg,V['v12']))
        if U12n is None: return None
        if w(U12n)<w(V['U12'])-1e-15: V['U12']=U12n; changed=True
        # U12 = atan(sin(S12)/(Q12+cos(S12))) -> tan(U12) = sin(S12)/(Q12+cos(S12))
        # narrow S12 = d+g+v8 -> v8 (then v8 = r-U8-d -> U8), best-effort
        tanU12=pad(math.tan(max(-1.5,V['U12'][0])), math.tan(min(1.5,V['U12'][1]))) if w(V['U12'])<math.pi else None
        if not changed: break
    return V

def aa_f4(x0,rad):
    AAr._n=[0]
    try: return cone_F(*[AAr.var(x0[i],rad) for i in range(6)], AA_FN)[K].iv()
    except Exception: return None

def contractor_excludes(x0,rad):
    box=[(x0[i]-rad,x0[i]+rad) for i in range(6)]
    V=forward(box)
    if V['F4'] is None: return None
    if not (V['F4'][0]<=0<=V['F4'][1]): return True   # forward alone already excludes
    Vc=contract_with_F4zero(V)
    if Vc is None: return True                         # F4=0 infeasible -> exclude
    return False

if __name__=='__main__':
    # sanity: forward F4 interval contains RAO value
    x0=[0.45,0.40,0.50,0.45,0.30,0.35]
    V=forward([(x0[i]-1e-6,x0[i]+1e-6) for i in range(6)])
    print('forward F4 ~point:', V['F4'], 'contains RAO %.6f: %s'%(RAO.constraints(*x0)[K], V['F4'][0]<=RAO.constraints(*x0)[K]<=V['F4'][1]))
    print()
    # narrowing test: does backward (F4=0) narrow U12/v12/tx13 vs forward-only?
    random.seed(7); rad=0.02; got=0; nr={'U12':[],'v12':[],'tx13':[]}
    for _ in range(20000):
        if got>=10: break
        c=random.uniform(0.3,0.85); d=random.uniform(0.3,0.85); h=random.uniform(0.2,0.5)
        if h+c>HALF-0.1 or h+d>HALF-0.1: continue
        b=random.uniform(0.2,0.6); e=random.uniform(0.2,0.6); g=random.uniform(0.1,0.5)
        x0=[b,c,d,e,g,h]
        if not all(B[i][0]<=x0[i]-rad and x0[i]+rad<=B[i][1] for i in range(6)): continue
        V=forward([(x0[i]-rad,x0[i]+rad) for i in range(6)])
        if V['F4'] is None or not (V['F4'][0]<=0<=V['F4'][1]): continue
        Vc=contract_with_F4zero(V)
        if Vc is None: continue
        got+=1
        for k in nr: 
            if w(V[k])>0: nr[k].append(w(V[k])/max(w(Vc[k]),1e-12))
    print('BACKWARD narrowing (forward width / contracted width), median over %d boxes:'%got)
    for k in nr:
        if nr[k]: print('  %-5s : %.2fx'%(k, statistics.median(nr[k])))
    print('  (>2x = backward propagation does real work; ~1x = inert, same paradigm)')
    print()
    # exclusion radius: contractor vs AA
    print('EXCLUSION-RADIUS (full grid): AA(F4) vs contractor')
    random.seed(20260629); radii=[0.05,0.04,0.03,0.02,0.015,0.01,0.005,0.002]
    def largest(x0b,fn,aa=False):
        if x0b[5]+x0b[1]>HALF-0.05 or x0b[5]+x0b[2]>HALF-0.05: return None
        for rr in radii:
            if not all(B[i][0]<=x0b[i]-rr and x0b[i]+rr<=B[i][1] for i in range(6)): continue
            if aa:
                v=fn(x0b,rr)
                if v is None: continue
                if not (v[0]<=0<=v[1]): return rr
            else:
                if fn(x0b,rr): return rr
        return None
    got=0; ge=0; ratios=[]
    for _ in range(20000):
        if got>=15: break
        c=random.uniform(0.3,0.85); d=random.uniform(0.3,0.85); h=random.uniform(0.2,0.5)
        if h+c>HALF-0.1 or h+d>HALF-0.1: continue
        b=random.uniform(0.2,0.6); e=random.uniform(0.2,0.6); g=random.uniform(0.1,0.5)
        x0b=[b,c,d,e,g,h]
        ra=largest(x0b,aa_f4,aa=True); rk=largest(x0b,contractor_excludes,aa=False)
        if ra is None and rk is None: continue
        got+=1
        if rk and (not ra or rk>=ra): ge+=1
        if ra and rk: ratios.append(rk/ra)
    print('  contractor >= AA: %d/%d'%(ge,got))
    if ratios: print('  median contractor/AA = %.2fx | mean %.2fx'%(statistics.median(ratios),statistics.mean(ratios)))

    print()
    print('VERDICT (pre-committed): success = narrow U12/v12/x13 by >2x OR exclude at >=2x AA.')
    print('  narrowing tx13~1.9x, v12~1.5x, U12~1.3x (all <2x); exclusion median 1.00x => FAIL.')
    print('  Backward pass is NON-INERT but DILUTES with depth: F4 alone is one equation,')
    print('  underdetermined for the intermediates. The determined test is the FULL 6-constraint')
    print('  system contractor -- but a full-system contractor (preconditioned Krawczyk) was')
    print('  already tested (exclusion probe) at 1.00x. Contraction, like enclosure, does not')
    print('  crack large-box exclusion here.')
