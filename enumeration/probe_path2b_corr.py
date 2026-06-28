"""
probe_path2b_corr.py — MICRO-PROBE 2b: correlation-PRESERVING transformed Krawczyk.
Variables are (b,u,v,e,g,h); c=u-h and d=v-h are built as DualRS EXPRESSIONS (shared
noise symbols), so the cone Jacobian comes out as the true NATIVE (u,v,h) Jacobian by
chain rule -- NOT the correlation-losing interval version of probe 2a. Decisive question:
does the known root certify 'unique' in correlation-preserving transformed coordinates?
"""
import sys, os, math
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
import domain_sphere_v2_prefilter as v2
import sriyantra as RAO
from aar import AAr
from aar_sphere import DualRS, SplitNeeded, DomainError
from chain_sphere import DUAL_FN
cone_F = v2.cone_F; S6 = v2.S6; _hw = v2._hw; HALF = v2.HALF_PI

def krawczyk_transformed(center_uv, rvec_uv):
    """6-var AA-Krawczyk on S6 in CORRELATION-PRESERVING transformed coords (b,u,v,e,g,h).
    center_uv/rvec_uv are in transformed coords. c=u-h, d=v-h built as DualRS expressions.
    Returns 'unique'|'empty'|'split'."""
    AAr._n = [0]
    try:
        bt = DualRS.var(0, center_uv[0], rvec_uv[0])
        ut = DualRS.var(1, center_uv[1], rvec_uv[1])
        vt = DualRS.var(2, center_uv[2], rvec_uv[2])
        et = DualRS.var(3, center_uv[3], rvec_uv[3])
        gt = DualRS.var(4, center_uv[4], rvec_uv[4])
        ht = DualRS.var(5, center_uv[5], rvec_uv[5])
        c = ut - ht          # correlation-preserving: shares u(slot1) & h(slot5)
        d = vt - ht          #                          shares v(slot2) & h(slot5)
        Fd = cone_F(bt, c, d, et, gt, ht, DUAL_FN)   # old chain, transformed inputs
    except (SplitNeeded, DomainError, ValueError, ZeroDivisionError, OverflowError) as ex:
        return 'split', f'chain raised {type(ex).__name__}'
    # Jacobian is now d F / d (b,u,v,e,g,h) -- the NATIVE transformed Jacobian
    Jm = np.array([[Fd[S6[i]].grad[j].c for j in range(6)] for i in range(6)])
    if not np.all(np.isfinite(Jm)):
        return 'split', 'nonfinite J'
    Jr = np.array([[_hw(Fd[S6[i]].grad[j]) for j in range(6)] for i in range(6)])
    try:
        Y = np.linalg.inv(Jm)
    except np.linalg.LinAlgError:
        return 'split', 'singular J'
    # Fm = constraints at the center, evaluated in OLD coords (c=u-h, d=v-h at the center)
    cen_old = [center_uv[0], center_uv[1]-center_uv[5], center_uv[2]-center_uv[5],
               center_uv[3], center_uv[4], center_uv[5]]
    try:
        Fm = np.array([RAO.constraints(*cen_old)[k] for k in S6], float)
    except Exception as ex:
        return 'split', f'constraints raised {type(ex).__name__}'
    rv = np.array(rvec_uv); cen = np.array(center_uv)
    M = np.eye(6) - Y @ Jm
    Mr = np.abs(Y) @ Jr
    Kc = -(Y @ Fm)
    Kh = (np.abs(M) + Mr) @ rv
    lo = cen + Kc - Kh; hi = cen + Kc + Kh
    Xl = cen - rv; Xh = cen + rv
    if np.all(hi < Xh) and np.all(lo > Xl):
        return 'unique', f'cond(J)={np.linalg.cond(Jm):.3e}'
    if np.any(hi < Xl) or np.any(lo > Xh):
        return 'empty', ''
    return 'split', f'cond(J)={np.linalg.cond(Jm):.3e}'

if __name__ == '__main__':
    root=[0.6246238466927992,0.7044304165359816,0.7482768099360514,
          0.6307397242292889,0.3136386632298885,22.64768569612002*math.pi/180]
    b,c,d,e,g,h=root
    root_uv=[b, h+c, h+d, e, g, h]
    print('MICRO-PROBE 2b: correlation-PRESERVING transformed Krawczyk at the known root')
    print('root_uv =', [round(x,5) for x in root_uv])
    print()
    print('DECISIVE QUESTION: does the root certify unique in correlation-preserving coords?')
    print('(probe 2a, correlation-LOSING, gave indeterminate at every r down to 1e-5)')
    print()
    for r in (3e-3, 1e-3, 3e-4, 1e-4):
        rv=[r]*6
        verdict, info = krawczyk_transformed(root_uv, rv)
        print(f'  r={r:.0e}: {verdict:10s} {info}')
    print()
    print('  compare old-coord c4: split at 3e-3,1e-3; unique at 3e-4,1e-4.')


# ---------------- correlation-preserving VALUE layer + domain + dive ----------
from chain_sphere import AA_FN
from prefilter_v2 import prefilter_excludes
(BL,BH),(CL,CH),(DL,DH),(EL,EH),(GL,GH),(HL,HH) = v2.B_SPHERE
B_UV = [(BL,BH),(HL+CL,HH+CH),(HL+DL,HH+DH),(EL,EH),(GL,GH),(HL,HH)]

def classify_uv_corr(box_uv):
    """Correlation-PRESERVING classify in transformed coords. c=u-h, d=v-h built as
    AAr EXPRESSIONS (shared noise symbols) for the value layer; native u/v domain edge;
    cert via krawczyk_transformed."""
    (b,u,v,e,g,h) = box_uv
    if u[0] > HALF or v[0] > HALF:
        return 'domain'                          # native axis-aligned edge (exact)
    # physical-range guard on c=u-h, d=v-h (interval bounds, cheap):
    c_iv=(u[0]-h[1], u[1]-h[0]); d_iv=(v[0]-h[1], v[1]-h[0])
    if min(c_iv[1],CH) <= max(c_iv[0],CL) or min(d_iv[1],DH) <= max(d_iv[0],DL):
        return 'nonphysical'
    AAr._n=[0]
    try:
        ba=AAr.var(b[0]+ (b[1]-b[0])/2, (b[1]-b[0])/2) if False else None
    except Exception: pass
    # build AAr vars on the transformed box, then c=u-h, d=v-h as AAr expressions
    def avar(iv):
        c0=(iv[0]+iv[1])/2; r0=(iv[1]-iv[0])/2; return AAr.var(c0, r0)
    AAr._n=[0]
    ba=avar(b); ua=avar(u); va=avar(v); ea=avar(e); ga=avar(g); ha=avar(h)
    ca=ua-ha; da=va-ha                            # correlation-preserving
    try:
        F = cone_F(ba, ca, da, ea, ga, ha, AA_FN)
    except (SplitNeeded, DomainError, ValueError, ZeroDivisionError, OverflowError):
        return 'split'
    for k in S6:
        lo,hi=F[k].iv()
        if not (lo <= 0 <= hi):
            return 'excluded'
    # try certification at this box (transformed Krawczyk)
    cen=[(x[0]+x[1])/2 for x in box_uv]; rv=[(x[1]-x[0])/2 for x in box_uv]
    if max(rv) < 3e-3:
        verdict,_=krawczyk_transformed(cen, rv)
        if verdict=='unique': return 'certified'
        if verdict=='empty':  return 'excluded'
    return 'indeterminate'

def split_uv(box_uv):
    (b,u,v,e,g,h)=box_uv
    if u[0] < HALF < u[1]: return 1, HALF
    if v[0] < HALF < v[1]: return 2, HALF
    w=[hi-lo for lo,hi in box_uv]; k=int(np.argmax(w)); lo,hi=box_uv[k]; return k,(lo+hi)/2

def dive_corr(max_boxes=120000, max_depth=200):
    stack=[(list(B_UV),0)]; proc=0; dom=nph=excl=cert=unres=0; maxd=0; ur=[]
    while stack and proc<max_boxes:
        box,dep=stack.pop(); proc+=1; maxd=max(maxd,dep)
        cls=classify_uv_corr(box)
        if cls=='domain': dom+=1; continue
        if cls=='nonphysical': nph+=1; continue
        if cls=='excluded': excl+=1; continue
        if cls=='certified': cert+=1; continue
        if dep>=max_depth: unres+=1; ur.append(box); continue
        k,mid=split_uv(box); lo,hi=box[k]
        L=list(box); L[k]=(lo,mid); R=list(box); R[k]=(mid,hi)
        stack.append((L,dep+1)); stack.append((R,dep+1))
    return dict(proc=proc,dom=dom,nph=nph,excl=excl,cert=cert,unres=unres,maxd=maxd,qleft=len(stack),ur=ur)


# ================== BOUNDED PILOT-SUBSET RUN (correlation-preserving) ==========
# Full soundness contract: native u/v edge + hull prune + FULL-CHAIN DOMAIN GUARD
# (on correlation-preserving AAr expressions) + cone exclusion + transformed Krawczyk.
from chain_sphere import AA_FN as _AA_FN
full_chain_domain_guard = v2.full_chain_domain_guard

def _avar(iv):
    c0=(iv[0]+iv[1])/2; r0=(iv[1]-iv[0])/2
    return AAr.var(c0, r0)

def classify_uv_full(box_uv, r_cert=3e-3):
    """Correlation-preserving transformed classify with the FULL v1.2 soundness contract."""
    (b,u,v,e,g,h) = box_uv
    # 1. native axis-aligned domain edge (exact)
    if u[0] > HALF or v[0] > HALF:
        return 'domain'
    # 2. physical hull prune: c=u-h, d=v-h must meet the registered c,d range
    c_iv=(u[0]-h[1], u[1]-h[0]); d_iv=(v[0]-h[1], v[1]-h[0])
    if min(c_iv[1],CH) <= max(c_iv[0],CL) or min(d_iv[1],DH) <= max(d_iv[0],DL):
        return 'nonphysical'
    # 3. FULL-CHAIN-REAL domain guard on correlation-preserving expressions (soundness)
    AAr._n=[0]
    ba,ua,va,ea,ga,ha=_avar(b),_avar(u),_avar(v),_avar(e),_avar(g),_avar(h)
    AV=[ba, ua-ha, va-ha, ea, ga, ha]            # c=u-h, d=v-h as AAr expressions
    gg=full_chain_domain_guard(AV)
    if gg=='domain': return 'domain'
    if gg=='split':  return 'split'
    # 4. cone constraint exclusion (fresh expressions)
    AAr._n=[0]
    ba,ua,va,ea,ga,ha=_avar(b),_avar(u),_avar(v),_avar(e),_avar(g),_avar(h)
    try:
        F=cone_F(ba, ua-ha, va-ha, ea, ga, ha, _AA_FN)
    except DomainError: return 'domain'
    except (SplitNeeded,ValueError,ZeroDivisionError,OverflowError): return 'split'
    for k in S6:
        lo,hi=F[k].iv()
        if not (lo<=0<=hi): return 'excluded'
    # 5. certify (box already guard-passed -> geometric certificate), transformed Krawczyk
    cen=[(x[0]+x[1])/2 for x in box_uv]; rv=[(x[1]-x[0])/2 for x in box_uv]
    if max(rv) < r_cert:
        verdict,_=krawczyk_transformed(cen, rv)
        if verdict=='unique': return 'certified'
        if verdict=='empty':  return 'excluded'
    return 'indeterminate'

def run_pilot_uv(max_boxes=600000, max_depth=200, r_cert=3e-3, tlim=500):
    import time
    t0=time.time()
    stack=[(list(B_UV),0)]; proc=0
    dom=nph=excl=cert=unres=0; maxd=0; cert_boxes=[]
    error_kind='none'
    while stack:
        if proc>=max_boxes: bound='max_boxes'; break
        if time.time()-t0>tlim: bound='wall_clock'; break
        box,dep=stack.pop(); proc+=1; maxd=max(maxd,dep)
        try:
            cls=classify_uv_full(box, r_cert)
        except Exception as ex:
            error_kind=f'{type(ex).__name__}'; bound='error'; break
        if cls=='domain': dom+=1; continue
        if cls=='nonphysical': nph+=1; continue
        if cls=='excluded': excl+=1; continue
        if cls=='certified': cert+=1; cert_boxes.append([(x[0]+x[1])/2 for x in box]); continue
        if dep>=max_depth: unres+=1; continue
        k,mid=split_uv(box); lo,hi=box[k]
        L=list(box); L[k]=(lo,mid); R=list(box); R[k]=(mid,hi)
        stack.append((L,dep+1)); stack.append((R,dep+1))
    else:
        bound='queue_empty'
    return dict(proc=proc,dom=dom,nph=nph,excl=excl,cert=cert,unres=unres,maxd=maxd,
                qleft=len(stack),bound=bound,error_kind=error_kind,secs=round(time.time()-t0,1),
                cert_boxes=cert_boxes)
