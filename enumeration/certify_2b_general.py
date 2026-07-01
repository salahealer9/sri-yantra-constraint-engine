"""
certify_2b_general.py — GENERALIZED 2b LOCAL geometric certifier, WIRED for arbitrary 6-constraint
subsets among the 3044 well-posed spherical systems {1,2} u T.

SCOPE OF CLAIM (honest): this certifier can EVALUATE and ATTEMPT certification for any of the
3044 subsets (no S6-only TECH_FAIL). It is PROVEN to certify only the benchmark {1,2,3,4,6,7} so
far; certification on a real NON-benchmark root remains to be demonstrated once candidate
discovery (Gap 1) supplies one. 'wired for all 3044' != 'has certified all 3044'.

Same contract as certify_2b.py:
  certify_2b_candidate(subset, candidate, radii) -> (status, evidence)
    CERTIFIED_UNIQUE_GEOMETRIC | NOT_CERTIFIED | DOMAIN_INVALID | TECH_FAIL

Generalization (verified identical to the S6 certifier on the benchmark):
 - constraint VALUES / gradients come from chain_sphere.constraints_sph(..., want=subset), the
   arithmetic-generic full-chain evaluator (constraints_sph(want=S6) == hand-coded cone_F exactly).
 - the full-chain domain guard (v2.full_chain_domain_guard) is SUBSET-INDEPENDENT (validates the
   entire Rao chain) and is reused unchanged.
 - the 2b transform uv=[b, h+c, h+d, e, g, h] is subset-independent (all 3044 share vars b..h).
 - realness is NEVER from tiny-Im; complex candidate -> real projection -> real-system refine ->
   real-system Krawczyk. LOCAL polish only (displacement cap); no global Newton wander.
"""
import sys, os, math, hashlib
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
from aar_sphere import DualRS, SplitNeeded, DomainError
from chain_sphere import DUAL_FN, constraints_sph
import domain_sphere_v2_prefilter as v2

HALF = v2.HALF_PI; B_SPHERE = v2.B_SPHERE
full_chain_domain_guard = v2.full_chain_domain_guard
_hw = v2._hw
DEFAULT_RADII = [3e-3, 1e-3, 3e-4, 1e-4, 3e-5, 1e-5]
MAX_POLISH = 2e-2

def _engine_hash():
    try:
        engine_path = os.path.join(_root, 'sriyantra.py')
        return hashlib.sha256(open(engine_path, 'rb').read()).hexdigest()[:12]
    except Exception:
        return 'unknown'
ENGINE_HASH = _engine_hash()

def _residual(x, subset):
    F = RAO.constraints(*x)
    return math.sqrt(sum(F[k]*F[k] for k in subset))

def _real_newton(seed, subset, iters=40, tol=1e-13):
    x = np.array([v.real if isinstance(v, complex) else float(v) for v in seed], float)
    try: r0 = _residual(x, subset)
    except Exception: return None
    for _ in range(iters):
        try: F0 = np.array([RAO.constraints(*x)[k] for k in subset], float)
        except Exception: return None
        J = np.zeros((6,6)); dd=1e-7
        for j in range(6):
            xp=x.copy(); xp[j]+=dd
            try: Fp=np.array([RAO.constraints(*xp)[k] for k in subset], float)
            except Exception: return None
            J[:,j]=(Fp-F0)/dd
        try: step=np.linalg.solve(J, F0)
        except np.linalg.LinAlgError: return None
        lam=1.0; cur=math.sqrt(float(F0@F0))
        for _ls in range(20):
            xn=x-lam*step
            try: rn=_residual(xn, subset)
            except Exception: rn=None
            if rn is not None and rn<cur: break
            lam*=0.5
        else: break
        x=xn
        if rn<tol: return x, rn
    try: return x, _residual(x, subset)
    except Exception: return None

def _in_bsphere(x, pad=0.0):
    return all(B_SPHERE[i][0]-pad <= x[i] <= B_SPHERE[i][1]+pad for i in range(6))

def krawczyk_transformed_general(center_uv, rvec_uv, subset):
    """6-var AA-Krawczyk on `subset` in correlation-preserving transformed coords (b,u,v,e,g,h).
    c=u-h, d=v-h built as DualRS expressions (shared noise symbols) -> native (u,v,h) Jacobian."""
    sub = list(subset)
    AAr._n = [0]
    try:
        bt = DualRS.var(0, center_uv[0], rvec_uv[0]); ut = DualRS.var(1, center_uv[1], rvec_uv[1])
        vt = DualRS.var(2, center_uv[2], rvec_uv[2]); et = DualRS.var(3, center_uv[3], rvec_uv[3])
        gt = DualRS.var(4, center_uv[4], rvec_uv[4]); ht = DualRS.var(5, center_uv[5], rvec_uv[5])
        c = ut - ht; d = vt - ht
        Fd = constraints_sph(bt, c, d, et, gt, ht, DUAL_FN, want=set(sub))   # GENERAL evaluator
    except (SplitNeeded, DomainError, ValueError, ZeroDivisionError, OverflowError) as ex:
        return 'split', f'chain raised {type(ex).__name__}'
    try:
        Jm = np.array([[Fd[sub[i]].grad[j].c for j in range(6)] for i in range(6)])
        Jr = np.array([[_hw(Fd[sub[i]].grad[j]) for j in range(6)] for i in range(6)])
    except Exception as ex:
        return 'split', f'jacobian assembly {type(ex).__name__}'
    if not np.all(np.isfinite(Jm)): return 'split', 'nonfinite J'
    try: Y = np.linalg.inv(Jm)
    except np.linalg.LinAlgError: return 'split', 'singular J'
    cen_old = [center_uv[0], center_uv[1]-center_uv[5], center_uv[2]-center_uv[5],
               center_uv[3], center_uv[4], center_uv[5]]
    try:
        Fm = np.array([RAO.constraints(*cen_old)[k] for k in sub], float)
    except Exception as ex:
        return 'split', f'constraints raised {type(ex).__name__}'
    rv = np.array(rvec_uv); cen = np.array(center_uv)
    M = np.eye(6) - Y @ Jm; Mr = np.abs(Y) @ Jr
    Kc = -(Y @ Fm); Kh = (np.abs(M) + Mr) @ rv
    lo = cen + Kc - Kh; hi = cen + Kc + Kh
    Xl = cen - rv; Xh = cen + rv
    if np.all(hi < Xh) and np.all(lo > Xl): return 'unique', f'cond(J)={np.linalg.cond(Jm):.3e}'
    if np.any(hi < Xl) or np.any(lo > Xh): return 'empty', ''
    return 'split', f'cond(J)={np.linalg.cond(Jm):.3e}'

def certify_2b_candidate(subset, candidate, radii=None):
    radii = radii or DEFAULT_RADII
    subset = tuple(subset)
    ev = dict(status=None, subset_id=subset, input_candidate=list(candidate),
              real_projected_center=None, radius_used=None, box_bounds=None,
              full_chain_guard_result=None, krawczyk=None, residual_norm=None,
              in_bsphere=None, engine_hash=ENGINE_HASH)
    # validity: exactly 6 UNIQUE constraint indices in 1..20, canonical (well-posedness of the
    # specific 6-set is enforced upstream by the generated 3044 universe).
    ks=[int(k) for k in subset] if all(float(k).is_integer() for k in subset) else None
    if ks is None or len(ks)!=6 or len(set(ks))!=6 or any(k<1 or k>20 for k in ks):
        ev['status']='TECH_FAIL'; ev['note']='subset must be 6 UNIQUE constraint indices in 1..20'
        return ev['status'], ev
    subset=tuple(sorted(ks)); ev['subset_id']=subset
    try:
        ev['max_abs_imag'] = max((abs(v.imag) for v in candidate if isinstance(v, complex)), default=0.0)
        real_seed = [v.real if isinstance(v, complex) else float(v) for v in candidate]
        try: _ = _residual(real_seed, subset)
        except Exception:
            ev['status']='DOMAIN_INVALID'; ev['real_projected_center']=real_seed
            ev['note']='chain not real at candidate (acos/atan domain)'; return ev['status'], ev
        ref = _real_newton(real_seed, subset, iters=15)
        if ref is None:
            ev['status']='NOT_CERTIFIED'; ev['real_projected_center']=real_seed
            ev['note']='local refinement left domain / failed'; return ev['status'], ev
        x, resid = ref
        disp = math.sqrt(sum((x[i]-real_seed[i])**2 for i in range(6)))
        ev['polish_displacement']=disp
        ev['real_projected_center']=[float(v) for v in x]; ev['residual_norm']=float(resid)
        ev['in_bsphere']=_in_bsphere(x)
        if disp > MAX_POLISH:
            ev['status']='NOT_CERTIFIED'
            ev['note']=f'candidate not near a real root (polish moved {disp:.2e} > {MAX_POLISH:.0e})'
            return ev['status'], ev
        if not np.all(np.isfinite(x)):
            ev['status']='TECH_FAIL'; ev['note']='nonfinite center'; return ev['status'], ev
        if resid > 1e-6:
            ev['status']='NOT_CERTIFIED'; ev['note']=f'refined residual {resid:.1e} too large'
            return ev['status'], ev
        b,c,d,e,g,h = x
        uvc = [b, h+c, h+d, e, g, h]
        saw_ok=False; saw_domain=False; last_guard=None; last_kraw=None
        for r in radii:
            uvbox=[(uvc[i]-r, uvc[i]+r) for i in range(6)]
            AAr._n=[0]
            def avar(iv): c0=(iv[0]+iv[1])/2; r0=(iv[1]-iv[0])/2; return AAr.var(c0,r0)
            try:
                AV=[avar(uvbox[0]), avar(uvbox[1])-avar(uvbox[5]),
                    avar(uvbox[2])-avar(uvbox[5]), avar(uvbox[3]), avar(uvbox[4]), avar(uvbox[5])]
                gg=full_chain_domain_guard(AV)
            except Exception as exg:
                gg='tech'; last_guard=f'guard raised {type(exg).__name__}'
            if gg=='domain': saw_domain=True; last_guard='domain'; continue
            if gg=='split':  last_guard='split'; continue
            if gg!='ok':     continue
            saw_ok=True; last_guard='ok'
            if uvbox[1][1]>HALF or uvbox[2][1]>HALF: saw_domain=True; continue
            try:
                verdict, info = krawczyk_transformed_general(uvc, [r]*6, subset)
            except Exception as exk:
                last_kraw=f'kraw raised {type(exk).__name__}'; continue
            last_kraw=(verdict, info)
            if verdict=='unique':
                ev.update(status='CERTIFIED_UNIQUE_GEOMETRIC', radius_used=float(r),
                          box_bounds=[(float(a),float(b2)) for a,b2 in uvbox],
                          full_chain_guard_result='ok', krawczyk=(verdict,info))
                return ev['status'], ev
        ev['full_chain_guard_result']=last_guard; ev['krawczyk']=last_kraw
        if saw_ok:     ev['status']='NOT_CERTIFIED'; return ev['status'], ev
        if saw_domain: ev['status']='DOMAIN_INVALID'; return ev['status'], ev
        ev['status']='NOT_CERTIFIED'; ev['note']='no clean (ok) box at any radius'; return ev['status'], ev
    except Exception as ex:
        ev['status']='TECH_FAIL'; ev['note']=f'{type(ex).__name__}: {ex}'; return ev['status'], ev

# reuse the collapse helper unchanged
from certify_2b import collapse_certified, _boxes_overlap

if __name__=='__main__':
    print("certify_2b_general: import OK")
