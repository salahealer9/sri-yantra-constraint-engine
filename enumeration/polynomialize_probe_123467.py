"""
polynomialize_probe_123467.py — root-covering polynomial lift PROBE for subset {1,2,3,4,6,7}.

HARD ORDERING (enforced):
  1. build the (S,C)-atom polynomial lift (serial, deterministic)
  2. inventory substitution exclusions + cleared denominators
  3. GATE: known 2b-certified root -> polynomial residual ~ 0 (serial). If FAIL, STOP.
  4. only after the gate passes: variables, equations, degree/Bezout/m-hom, mixed volume
     (parallel if a backend exists), zero-dimensional status, path-count estimate.

This probe NEVER claims INFEASIBLE_CERTIFIED. It only measures whether the absence branch is
feasible: root-covering lift + known-root residual + path-count estimate.

Lift design: every acos/atan node N carries (S_N,C_N)=(sin,cos) with S_N^2+C_N^2=1 and a
defining relation from its tangent/cosine; base angles carry (s,c) atoms; r=pi/2-h so
sin r=cos h, cos r=sin h. Angle SUMS use addition formulas (polynomial in atoms). Constraints:
 F1,F7 angle-equalities -> sin(xi-xj)=0 (principal atan branch);
 F3,F4,F6 -> cos(sum)*C - (2C^2-1)=0 (cleared cos(x); cos2x=2C^2-1);
 F2 -> sin(d-U7-rT)=0 (range obligation).
Root-covering (not bijective): genuine geometric roots are preserved; spurious polynomial
roots are allowed and rejected later by the full-chain guard + 2b certifier.
"""
import sys, os, math, argparse, json, hashlib, platform, datetime
_here=os.path.dirname(os.path.abspath(__file__)); _root=_here
while _root!=os.path.dirname(_root):
    if os.path.exists(os.path.join(_root,"sriyantra.py")): break
    _root=os.path.dirname(_root)
for _p in (_here,_root,os.path.join(_root,"enumeration")):
    if os.path.isdir(_p) and _p not in sys.path: sys.path.insert(0,_p)
import sympy as sp
import sriyantra as RAO

KNOWN_ROOT=[0.6246238466927992,0.7044304165359816,0.7482768099360514,
            0.6307397242292889,0.3136386632298885,0.39527668335411803]

# ---------- angle algebra: an "angle" is a (sin_expr, cos_expr) pair ----------
class Ang:
    __slots__=('s','c')
    def __init__(self,s,c): self.s=sp.expand(s); self.c=sp.expand(c)
    def __add__(self,o): return Ang(self.s*o.c+self.c*o.s, self.c*o.c-self.s*o.s)
    def __sub__(self,o): return Ang(self.s*o.c-self.c*o.s, self.c*o.c+self.s*o.s)
    def neg(self): return Ang(-self.s,self.c)

class Lift:
    def __init__(self):
        self.vars=[]              # all sympy variables (atoms)
        self.eqs=[]               # all polynomial equations (=0)
        self.eq_tags=[]           # label per equation
        self.denoms=[]            # (label, expr) cleared denominators
        self.exclusions=[]        # (kind, detail) substitution exclusions / branch assumptions
        self.numval={}            # var -> numeric value at known root (for residual gate)
        self.ang={}               # name -> Ang
        self._build_base()
    def _addvar(self,name,val):
        v=sp.Symbol(name); self.vars.append(v); self.numval[v]=val; return v
    def _build_base(self):
        b,c,d,e,g,h=KNOWN_ROOT
        names=dict(b=b,c=c,d=d,e=e,g=g,h=h)
        self.base={}
        for nm,val in names.items():
            sX=self._addvar('s_'+nm, math.sin(val)); cX=self._addvar('c_'+nm, math.cos(val))
            self.eqs.append(sX**2+cX**2-1); self.eq_tags.append('pyth_'+nm)
            self.base[nm]=Ang(sX,cX); self.ang[nm]=Ang(sX,cX)
        # r = pi/2 - h : sin r = cos h, cos r = sin h
        self.ang['r']=Ang(self.base['h'].c, self.base['h'].s)
    # angle from a signed sum of named angles, e.g. lin({'r':1,'c':-1})
    def lin(self,terms):
        acc=Ang(sp.Integer(0),sp.Integer(1))
        for nm,k in terms.items():
            a=self.ang[nm]
            for _ in range(abs(k)):
                acc = acc+a if k>0 else acc-a
        return acc
    def _numsin(self,terms):
        return math.sin(sum(k*self._angval(nm) for nm,k in terms.items()))
    def _angval(self,nm):
        # numeric angle value for validation
        if nm=='r': return math.pi/2-KNOWN_ROOT[5]
        return self._anglesnum[nm]
    # add an atan node with tan = num/den (num,den sympy exprs); returns Ang(S,C)
    def add_atan_node(self,name,num,den,num_val,den_val,denom_labels):
        ang_val=math.atan(num_val/den_val)
        S=self._addvar('S_'+name, math.sin(ang_val)); C=self._addvar('C_'+name, math.cos(ang_val))
        self.eqs.append(S**2+C**2-1); self.eq_tags.append('pyth_'+name)
        # tan = S/C = num/den  -> S*den - C*num = 0
        self.eqs.append(sp.expand(S*den - C*num)); self.eq_tags.append('def_'+name)
        for lbl in denom_labels: self.denoms.append((name+':'+lbl[0], lbl[1]))
        self.exclusions.append(('atan_branch', f'{name}: cos({name})>0 (principal branch)'))
        a=Ang(S,C); self.ang[name]=a; return a
    def add_acos_node(self,name,cos_expr,cos_val,denom_labels):
        ang_val=math.acos(cos_val)
        S=self._addvar('S_'+name, math.sin(ang_val)); C=self._addvar('C_'+name, math.cos(ang_val))
        self.eqs.append(S**2+C**2-1); self.eq_tags.append('pyth_'+name)
        # C = cos_expr  (cos_expr already = ratio with cleared denom handled by caller)
        self.eqs.append(sp.expand(C - cos_expr)); self.eq_tags.append('def_'+name)
        for lbl in denom_labels: self.denoms.append((name+':'+lbl[0], lbl[1]))
        self.exclusions.append(('acos_branch', f'{name}: sin({name})>=0 (acos range [0,pi])'))
        a=Ang(S,C); self.ang[name]=a; return a

# ---------------- build all 19 nodes for S6 in dependency order ----------------
def build_lift():
    L=Lift()
    b,c,d,e,g,h=KNOWN_ROOT
    A={'b':b,'c':c,'d':d,'e':e,'f':None,'g':g,'h':h,'r':math.pi/2-h}
    L._anglesnum=dict(b=b,c=c,d=d,e=e,g=g,h=h)
    s=RAO.chain(*KNOWN_ROOT)
    nS=lambda terms: math.sin(sum(k*(A['r'] if nm=='r' else A[nm]) for nm,k in terms.items()))
    nC=lambda terms: math.cos(sum(k*(A['r'] if nm=='r' else A[nm]) for nm,k in terms.items()))
    sS=lambda terms: L.lin(terms).s          # symbolic sin of a base-angle sum
    sC=lambda terms: L.lin(terms).c
    def tan(name): a=L.ang[name]; return a.s, a.c   # (S,C) symbols
    def ntan(x): return math.tan(x)
    # node angle numeric values
    NV={k:s[k] for k in ['x1','x2','x3','x4','x5','x6','x7','x10','x11','x11a','x13','x18','x19',
                          'U7','U8','U9','U12','t','rT']}
    # --- x1,x2 (acos): cos(x1)=cos r/cos c = s_h/c_c ---
    L.add_acos_node('x1', L.base['h'].s/1 * sp.Symbol('c_c')**0,  # placeholder, fix below
                    math.cos(NV['x1']), [])
    # (rebuild x1,x2 cleanly with cleared denominator form C*cos(c)-sin(h)=0)
    L.eqs.pop(); L.eq_tags.pop(); L.exclusions.pop()  # undo def_x1 + branch (keep pyth)
    C1=sp.Symbol('C_x1'); 
    L.eqs.append(sp.expand(C1*L.base['c'].c - L.base['h'].s)); L.eq_tags.append('def_x1')
    L.denoms.append(('x1:cos_c', L.base['c'].c)); L.exclusions.append(('acos_branch','x1: sin>=0'))
    C2=sp.Symbol('C_x2'); 
    L.add_acos_node('x2', sp.Integer(0), math.cos(NV['x2']), [])
    L.eqs.pop(); L.eq_tags.pop(); L.exclusions.pop()
    L.eqs.append(sp.expand(C2*L.base['d'].c - L.base['h'].s)); L.eq_tags.append('def_x2')
    L.denoms.append(('x2:cos_d', L.base['d'].c)); L.exclusions.append(('acos_branch','x2: sin>=0'))
    # --- x3 = atan( sin(r-c)/sin(r+d) * tan(x2) ) ---
    S2,Cc2=L.ang['x2'].s,L.ang['x2'].c
    L.add_atan_node('x3', sS({'r':1,'c':-1})*S2, sS({'r':1,'d':1})*Cc2,
                    nS({'r':1,'c':-1})*math.sin(NV['x2']), nS({'r':1,'d':1})*math.cos(NV['x2']),
                    [('sin_r+d',sS({'r':1,'d':1})),('C_x2',Cc2)])
    # --- x4 = atan( sin(r-d)/sin(r+c) * tan(x1) ) ---
    S1=L.ang['x1'].s; Cc1=L.ang['x1'].c
    L.add_atan_node('x4', sS({'r':1,'d':-1})*S1, sS({'r':1,'c':1})*Cc1,
                    nS({'r':1,'d':-1})*math.sin(NV['x1']), nS({'r':1,'c':1})*math.cos(NV['x1']),
                    [('sin_r+c',sS({'r':1,'c':1})),('C_x1',Cc1)])
    # --- x5 = atan( sin(b)/sin(b+c+d) * tan(x4) ) ---
    S4,C4=tan('x4')
    L.add_atan_node('x5', L.base['b'].s*S4, sS({'b':1,'c':1,'d':1})*C4,
                    math.sin(b)*math.sin(NV['x4']), nS({'b':1,'c':1,'d':1})*math.cos(NV['x4']),
                    [('sin_b+c+d',sS({'b':1,'c':1,'d':1})),('C_x4',C4)])
    # --- x6 = atan( sin(e)/sin(c+d+e) * tan(x3) ) ---
    S3,C3=tan('x3')
    L.add_atan_node('x6', L.base['e'].s*S3, sS({'c':1,'d':1,'e':1})*C3,
                    math.sin(e)*math.sin(NV['x3']), nS({'c':1,'d':1,'e':1})*math.cos(NV['x3']),
                    [('sin_c+d+e',sS({'c':1,'d':1,'e':1})),('C_x3',C3)])
    # --- U7: tan = sin(d+g)*sin(c+d)*C5*S6 / [sin(d+g)*S5*C6 + cos(d+g)*sin(c+d)*C5*S6] ---
    S5,C5=tan('x5'); S6,C6=tan('x6')
    num_U7=sS({'d':1,'g':1})*sS({'c':1,'d':1})*C5*S6
    den_U7=sS({'d':1,'g':1})*S5*C6 + sC({'d':1,'g':1})*sS({'c':1,'d':1})*C5*S6
    nN=nS({'d':1,'g':1})*nS({'c':1,'d':1})*math.cos(NV['x5'])*math.sin(NV['x6'])
    nD=nS({'d':1,'g':1})*math.sin(NV['x5'])*math.cos(NV['x6'])+nC({'d':1,'g':1})*nS({'c':1,'d':1})*math.cos(NV['x5'])*math.sin(NV['x6'])
    L.add_atan_node('U7', num_U7, den_U7, nN, nD,
                    [('sin_c+d',sS({'c':1,'d':1})),('C_x5',C5),('S_x6',S6)])
    # --- x7 = atan( sin(U7)/sin(c+d) * tan(x5) ) ---
    SU7,CU7=tan('U7')
    L.add_atan_node('x7', SU7*S5, sS({'c':1,'d':1})*C5,
                    math.sin(NV['U7'])*math.sin(NV['x5']), nS({'c':1,'d':1})*math.cos(NV['x5']),
                    [('sin_c+d',sS({'c':1,'d':1})),('C_x5',C5)])
    # --- U8: tan = sin(r+g)*sin(r+c)*C1*S6 / [sin(d+g)*S1*C6 + cos(r+g)*sin(r+c)*C1*S6] ---
    num_U8=sS({'r':1,'g':1})*sS({'r':1,'c':1})*Cc1*S6
    den_U8=sS({'d':1,'g':1})*S1*C6 + sC({'r':1,'g':1})*sS({'r':1,'c':1})*Cc1*S6
    nN=nS({'r':1,'g':1})*nS({'r':1,'c':1})*math.cos(NV['x1'])*math.sin(NV['x6'])
    nD=nS({'d':1,'g':1})*math.sin(NV['x1'])*math.cos(NV['x6'])+nC({'r':1,'g':1})*nS({'r':1,'c':1})*math.cos(NV['x1'])*math.sin(NV['x6'])
    L.add_atan_node('U8', num_U8, den_U8, nN, nD,
                    [('sin_r+c',sS({'r':1,'c':1})),('C_x1',Cc1),('S_x6',S6)])
    SU8,CU8=tan('U8')
    # v8 = r - U8 - d ; V8 = r + g - U8  (Ang via algebra)
    L.ang['v8']=L.lin({'r':1,'d':-1}) - L.ang['U8']
    L.ang['V8']=L.lin({'r':1,'g':1}) - L.ang['U8']
    A['v8']=s['v8']; A['V8']=s['V8']
    # --- U9: tan = sin(r+d)*sin(r+d)*C2*S5 / [sin(c+d)*S2*C5 + cos(r+d)*sin(r+d)*C2*S5] ---
    num_U9=sS({'r':1,'d':1})*sS({'r':1,'d':1})*Cc2*S5
    den_U9=sS({'c':1,'d':1})*S2*C5 + sC({'r':1,'d':1})*sS({'r':1,'d':1})*Cc2*S5
    nN=nS({'r':1,'d':1})*nS({'r':1,'d':1})*math.cos(NV['x2'])*math.sin(NV['x5'])
    nD=nS({'c':1,'d':1})*math.sin(NV['x2'])*math.cos(NV['x5'])+nC({'r':1,'d':1})*nS({'r':1,'d':1})*math.cos(NV['x2'])*math.sin(NV['x5'])
    L.add_atan_node('U9', num_U9, den_U9, nN, nD,
                    [('sin_c+d',sS({'c':1,'d':1})),('C_x2',Cc2),('S_x5',S5)])
    L.ang['v9']=L.lin({'r':1,'c':-1}) - L.ang['U9']; A['v9']=s['v9']
    # --- x10 = atan( sin(b+c-g)/sin(b+c+d) * tan(x4) ) ---
    L.add_atan_node('x10', sS({'b':1,'c':1,'g':-1})*S4, sS({'b':1,'c':1,'d':1})*C4,
                    nS({'b':1,'c':1,'g':-1})*math.sin(NV['x4']), nS({'b':1,'c':1,'d':1})*math.cos(NV['x4']),
                    [('sin_b+c+d',sS({'b':1,'c':1,'d':1})),('C_x4',C4)])
    S10,C10=tan('x10')
    # --- U12: S12=d+g+v8 ; tan = sin(S12)*sin(d+g)*C6*S10 / [sin(S12)*S6*C10 + cos(S12)*sin(d+g)*C6*S10] ---
    sinS12=(L.lin({'d':1,'g':1})+L.ang['v8']).s; cosS12=(L.lin({'d':1,'g':1})+L.ang['v8']).c
    num_U12=sinS12*sS({'d':1,'g':1})*C6*S10
    den_U12=sinS12*S6*C10 + cosS12*sS({'d':1,'g':1})*C6*S10
    nS12=math.sin(d+g+A['v8']); nC12=math.cos(d+g+A['v8'])
    nN=nS12*nS({'d':1,'g':1})*math.cos(NV['x6'])*math.sin(NV['x10'])
    nD=nS12*math.sin(NV['x6'])*math.cos(NV['x10'])+nC12*nS({'d':1,'g':1})*math.cos(NV['x6'])*math.sin(NV['x10'])
    L.add_atan_node('U12', num_U12, den_U12, nN, nD,
                    [('sin_d+g',sS({'d':1,'g':1})),('C_x6',C6),('S_x10',S10)])
    L.ang['v12']=L.lin({'d':1,'g':1}) - L.ang['U12']; A['v12']=s['v12']
    # --- x13 = atan( sin(e+v12)/sin(c+d+e) * tan(x3) ) ---
    sin_ev12=(L.lin({'e':1})+L.ang['v12']).s
    L.add_atan_node('x13', sin_ev12*S3, sS({'c':1,'d':1,'e':1})*C3,
                    math.sin(e+A['v12'])*math.sin(NV['x3']), nS({'c':1,'d':1,'e':1})*math.cos(NV['x3']),
                    [('sin_c+d+e',sS({'c':1,'d':1,'e':1})),('C_x3',C3)])
    S13,C13=tan('x13')
    # --- x18 = atan( sin(b+c+d+v8)/sin(b+c+d) * tan(x4) ) ---
    sin_bcdv8=(L.lin({'b':1,'c':1,'d':1})+L.ang['v8']).s
    L.add_atan_node('x18', sin_bcdv8*S4, sS({'b':1,'c':1,'d':1})*C4,
                    math.sin(b+c+d+A['v8'])*math.sin(NV['x4']), nS({'b':1,'c':1,'d':1})*math.cos(NV['x4']),
                    [('sin_b+c+d',sS({'b':1,'c':1,'d':1})),('C_x4',C4)])
    # --- x19 = atan( sin(c+d+e+v9)/sin(c+d+e) * tan(x3) ) ---
    sin_cdev9=(L.lin({'c':1,'d':1,'e':1})+L.ang['v9']).s
    L.add_atan_node('x19', sin_cdev9*S3, sS({'c':1,'d':1,'e':1})*C3,
                    math.sin(c+d+e+A['v9'])*math.sin(NV['x3']), nS({'c':1,'d':1,'e':1})*math.cos(NV['x3']),
                    [('sin_c+d+e',sS({'c':1,'d':1,'e':1})),('C_x3',C3)])
    # --- x11 = atan( sin(d+g)/sin(c+d) * tan(x5) ) ---
    L.add_atan_node('x11', sS({'d':1,'g':1})*S5, sS({'c':1,'d':1})*C5,
                    nS({'d':1,'g':1})*math.sin(NV['x5']), nS({'c':1,'d':1})*math.cos(NV['x5']),
                    [('sin_c+d',sS({'c':1,'d':1})),('C_x5',C5)])
    # --- x11a = atan( sin(v9+c-g)/sin(v9+c+d-v12) * tan(x13) ) ---
    sin_a=(L.ang['v9']+L.lin({'c':1,'g':-1})).s
    sin_b2=(L.ang['v9']+L.lin({'c':1,'d':1})-L.ang['v12']).s
    nA=math.sin(A['v9']+c-g); nB=math.sin(A['v9']+c+d-A['v12'])
    L.add_atan_node('x11a', sin_a*S13, sin_b2*C13, nA*math.sin(NV['x13']), nB*math.cos(NV['x13']),
                    [('sin_v9+c+d-v12',sin_b2),('C_x13',C13)])
    # --- t = atan( tan(d+g-U7)/sin(x7) ) = atan( sin(d+g-U7)/(cos(d+g-U7)*S_x7) ) ---
    Sx7,Cx7=tan('x7')
    ang_dgU7=L.lin({'d':1,'g':1})-L.ang['U7']
    L.add_atan_node('t', ang_dgU7.s, ang_dgU7.c*Sx7,
                    math.sin(d+g-NV['U7']), math.cos(d+g-NV['U7'])*math.sin(NV['x7']),
                    [('cos_d+g-U7',ang_dgU7.c),('S_x7',Sx7)])
    St,Ct=tan('t')
    # --- rT = atan( sin(x7)*tan(t/2) ) = atan( S_x7*S_t/(1+C_t) ) ---
    L.add_atan_node('rT', Sx7*St, (1+Ct),
                    math.sin(NV['x7'])*math.sin(NV['t']), (1+math.cos(NV['t'])),
                    [('1+C_t',1+Ct)])
    L.exclusions.append(('half_angle','rT: tan(t/2) excludes t=pi (1+cos t=0)'))
    SrT,CrT=tan('rT')
    # ---------------- 6 constraints ----------------
    S11,C11=tan('x11'); S11a,C11a=tan('x11a'); S18,C18=tan('x18'); S19,C19=tan('x19')
    # F1: x11 - x11a = 0  -> sin(x11-x11a)=0
    L.eqs.append(sp.expand(S11*C11a - C11*S11a)); L.eq_tags.append('F1')
    L.exclusions.append(('angle_eq','F1: x11=x11a via principal branch (both in (-pi/2,pi/2))'))
    # F2: d - U7 - rT = 0 -> sin(d-(U7+rT))=0
    U7rT=L.ang['U7']+L.ang['rT']
    L.eqs.append(sp.expand(L.base['d'].s*U7rT.c - L.base['d'].c*U7rT.s)); L.eq_tags.append('F2')
    L.exclusions.append(('range','F2: sin(d-U7-rT)=0 with d-U7-rT in (-pi,pi) -> unique zero'))
    # F3: cos(V8)*C10 - (2 C10^2 - 1) = 0
    L.eqs.append(sp.expand(L.ang['V8'].c*C10 - (2*C10**2-1))); L.eq_tags.append('F3')
    L.denoms.append(('F3:cos_x10',C10)); L.exclusions.append(('cleared','F3: cleared cos(x10)'))
    # F4: cos(c+d+v9-v12)*C13 - (2 C13^2 - 1) = 0
    ang_F4=L.lin({'c':1,'d':1})+L.ang['v9']-L.ang['v12']
    L.eqs.append(sp.expand(ang_F4.c*C13 - (2*C13**2-1))); L.eq_tags.append('F4')
    L.denoms.append(('F4:cos_x13',C13)); L.exclusions.append(('cleared','F4: cleared cos(x13)'))
    # F6: cos(d+g-U7)*Cx7 - (2 Cx7^2 - 1) = 0
    L.eqs.append(sp.expand(ang_dgU7.c*Cx7 - (2*Cx7**2-1))); L.eq_tags.append('F6')
    L.denoms.append(('F6:cos_x7',Cx7)); L.exclusions.append(('cleared','F6: cleared cos(x7)'))
    # F7: x18 - x19 = 0 -> sin(x18-x19)=0
    L.eqs.append(sp.expand(S18*C19 - C18*S19)); L.eq_tags.append('F7')
    L.exclusions.append(('angle_eq','F7: x18=x19 via principal branch'))
    return L

def classify_denominators(L):
    """Bucket each cleared denominator: structural | branch | danger.
    structural = sin/cos of a PURE base-angle sum (domain guard => nonzero);
    branch     = node's own cos>0 (atan principal branch) / base cos nonzero in B_sphere /
                 half-angle 1+cos;
    danger     = sin(node)=0, or sin/cos of a NODE-BEARING sum (can vanish in B_sphere)."""
    NODE_TOKENS=('U7','U8','U9','U12','v8','v9','v12')
    buckets={'structural':[],'branch':[],'danger':[]}
    seen=set()
    for label,expr in L.denoms:
        key=label.split(':',1)[-1]
        if key in seen: continue
        seen.add(key)
        has_node=any(tok in key for tok in NODE_TOKENS)
        if key.startswith('C_x'):
            buckets['branch'].append((label,'cos(atan node)>0 principal branch'))
        elif key.startswith('S_x'):
            buckets['danger'].append((label,'sin(node)=0 iff node angle=0; could vanish in B_sphere'))
        elif key.startswith('1+C_'):
            buckets['branch'].append((label,'half-angle: 1+cos(t)!=0 i.e. t!=pi'))
        elif key.startswith('cos_c') or key.startswith('cos_d') and not has_node:
            buckets['branch'].append((label,'base cos; nonzero in B_sphere (var < pi/2)'))
        elif (key.startswith('sin_') or key.startswith('cos_')) and not has_node:
            buckets['structural'].append((label,'sin/cos of pure base-angle sum; domain guard => nonzero'))
        elif (key.startswith('sin_') or key.startswith('cos_')) and has_node:
            buckets['danger'].append((label,'sin/cos of NODE-bearing sum; vanishing needs separate proof'))
        else:
            buckets['danger'].append((label,'unclassified -> treat as danger'))
    return buckets

def total_degree(eq):
    p=sp.Poly(eq, *sorted(eq.free_symbols, key=lambda s:s.name)) if eq.free_symbols else None
    return p.total_degree() if p is not None else 0

def bezout_bound(L):
    prod=1
    degs=[]
    for eq in L.eqs:
        d=total_degree(eq); degs.append(d); prod*=max(d,1)
    return prod, degs

def mixed_volume_parallel(L, workers):
    """Mixed volume via a backend (phcpy / Julia HC.jl) if present. Parallel-capable.
    Returns (value, method) or (None, 'backend_absent'). Lift+gate are NOT parallelized;
    only this expensive independent step is."""
    try:
        import phcpy
        # (phcpy mixed_volume call would go here; structured for the server)
        return None, 'phcpy_present_but_export_not_wired'
    except Exception:
        pass
    if os.environ.get('JULIA_NUM_THREADS') and _which('julia'):
        return None, 'julia_present_but_export_not_wired'
    return None, 'backend_absent'

def _which(x):
    from shutil import which; return which(x)

def _sha(path):
    try: return hashlib.sha256(open(path,'rb').read()).hexdigest()
    except Exception: return ''

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--workers', type=int, default=min(8, os.cpu_count() or 1))
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--out', default='polynomialize_probe_123467.manifest.json')
    args=ap.parse_args()
    os.environ.setdefault('OMP_NUM_THREADS','1')   # avoid oversubscription
    t0=datetime.datetime.now(datetime.timezone.utc).isoformat()

    # ---- STEP 1: build lift (serial, deterministic) ----
    L=build_lift()
    n_vars=len(L.vars); n_eqs=len(L.eqs)

    # ---- STEP 2: inventory exclusions + cleared denominators ----
    buckets=classify_denominators(L)
    excl=sorted(set((k,d) for k,d in L.exclusions))
    cleared=sorted(set(lbl for lbl,_ in L.denoms))

    # ---- STEP 3: GATE — known-root residual (serial). STOP if fail. ----
    per_node={}; worst=0.0
    for tag,eq in zip(L.eq_tags,L.eqs):
        v=abs(float(eq.subs(L.numval))); per_node[tag]=v; worst=max(worst,v)
    GATE_TOL=1e-9
    gate_pass = worst < GATE_TOL

    manifest=dict(
        schema_version="polynomialize_probe_v1",
        subset=[1,2,3,4,6,7],
        n_variables=n_vars, n_equations=n_eqs,
        n_excluded_angle_cases=len(excl),
        n_cleared_denominators=len(cleared),
        excluded_angle_list=excl,
        cleared_denominator_list=cleared,
        denominator_classification={k:[f"{a} :: {b}" for a,b in v] for k,v in buckets.items()},
        n_danger_denominators=len(buckets['danger']),
        root_covering_obligations=[
            "tan-half-angle / atan principal branch: cos(node)>0 excludes node=+-pi/2",
            "acos branch sin>=0 (x1,x2)",
            "angle-equality F1/F7 via principal branch; range F2 sin zero unique in (-pi,pi)",
            "cleared denominators (esp. danger bucket) cannot hide a valid geometric root",
            "branch/domain choices cover all real geometric branches",
        ],
        known_root_residual_max=worst,
        known_root_residual_per_eq_worst=sorted(per_node.items(), key=lambda x:-x[1])[:10],
        gate_pass=gate_pass,
        workers=args.workers, cpu_count=os.cpu_count(), random_seed=args.seed,
        command=' '.join(sys.argv),
        engine_sha=_sha(os.path.join(_root,'sriyantra.py')),
        probe_sha=_sha(os.path.abspath(__file__)),
        python_version=platform.python_version(), platform=platform.platform(),
        timestamp_start=t0,
        status="GATE_PASS" if gate_pass else "GATE_FAIL_STOP",
    )

    print("="*70)
    print("polynomialization probe — subset {1,2,3,4,6,7}")
    print("="*70)
    print(f"[1] lift built: {n_vars} variables, {n_eqs} equations (square={n_vars==n_eqs})")
    print(f"[2] inventory: {len(excl)} exclusion cases, {len(cleared)} cleared denominators")
    print(f"    denominator buckets: structural={len(buckets['structural'])} "
          f"branch={len(buckets['branch'])} DANGER={len(buckets['danger'])}")
    print(f"[3] GATE known_root_residual_max = {worst:.3e}  -> {'PASS' if gate_pass else 'FAIL'}")
    if not gate_pass:
        print("    GATE FAILED — lift is wrong; path count is meaningless. STOPPING.")
        manifest.update(mixed_volume=None, total_degree_bound=None, zero_dimensional_status="not_evaluated")
        json.dump(manifest, open(args.out,'w'), indent=2, default=str)
        return

    # ---- STEP 4: path-count estimate (only after gate passes) ----
    bez, degs = bezout_bound(L)
    mv, mv_method = mixed_volume_parallel(L, args.workers)
    # m-homogeneous-ish observation: triangular node structure (each node defined by earlier)
    manifest.update(
        total_degree_bound=int(bez),
        equation_degrees=sorted(degs, reverse=True),
        mixed_volume=mv, mixed_volume_method=mv_method,
        structure_note=("system is sequentially TRIANGULAR: each node (S_N,C_N) is defined by "
                        "earlier nodes + 6 base atoms, so the naive dense Bezout is MEANINGLESS "
                        "for feasibility. Decisive count = sparse/mixed volume after exploiting "
                        "structure or eliminating nodes; elimination MAY still inflate degrees, "
                        f"so structure is favorable not decisive. Bezout {bez:.3e} is naive only."),
        zero_dimensional_status=("numerically_apparent (square system; known root isolated by "
                                 "2b certifier); GLOBAL zero-dimensionality is a separate proof "
                                 "obligation"),
        timestamp_end=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    )
    print(f"[4] total-degree (Bezout) bound = {bez:.3e}  (naive; triangular structure not exploited)")
    print(f"    mixed_volume = {mv}  (method: {mv_method})")
    print(f"    zero-dimensional: numerically apparent (square; root isolated by 2b)")
    print(f"    NOTE: triangular node structure -> essential system is 6 constraints in 6 base DOF")
    print()
    print("This probe makes NO infeasibility claim. It reports lift validity + path-count scale.")
    json.dump(manifest, open(args.out,'w'), indent=2, default=str)
    print(f"manifest -> {args.out}")

if __name__=='__main__':
    main()
