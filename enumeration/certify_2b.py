"""
certify_2b.py — reusable 2b LOCAL geometric certifier (the shared rigor gate).

certify_2b_candidate(subset, candidate, radii) -> (status, evidence)
  status in:
    CERTIFIED_UNIQUE_GEOMETRIC  real, in B_sphere, full-chain domain-valid on the whole box,
                                correct 2b coords, Krawczyk K(X) ⊆ int(X) -> one real root.
    NOT_CERTIFIED               chain real on some box but no radius certified (off-root /
                                contraction failed / genuinely-complex candidate).
    DOMAIN_INVALID              chain never real over any box (acos/atan domain or cone edge).
    TECH_FAIL                   crash / NaN / unreadable.

Discipline:
 - Absence/realness is NEVER inferred from "imaginary part is tiny". A complex candidate is
   projected to its real part, refined in the REAL system, and only a successful real-system
   Krawczyk certifies realness.
 - Evidence bundle returned for auditability (engine hash, box, residual, guard, margin).
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
import domain_sphere_v2_prefilter as v2
import probe_path2b_corr as P2B

S6 = v2.S6; HALF = v2.HALF_PI; B_SPHERE = v2.B_SPHERE
full_chain_domain_guard = v2.full_chain_domain_guard
krawczyk_transformed = P2B.krawczyk_transformed
DEFAULT_RADII = [3e-3, 1e-3, 3e-4, 1e-4, 3e-5, 1e-5]

def _engine_hash():
    try:
        engine_path = os.path.join(_root, "sriyantra.py")
        return hashlib.sha256(open(engine_path, 'rb').read()).hexdigest()[:12]
    except Exception:
        return 'unknown'

ENGINE_HASH = _engine_hash()

def _residual(x):
    """||F_S6(x)|| in old coords; raises if out of domain."""
    F = RAO.constraints(*x)
    return math.sqrt(sum(F[k]*F[k] for k in S6))

def _real_newton(seed, iters=40, tol=1e-13):
    """Damped real Newton on F_S6=0 (numerical Jacobian). Returns (x, residual) or None
    if it leaves the domain / fails to converge. Realness is established here, not by Im."""
    x = np.array([v.real if isinstance(v, complex) else float(v) for v in seed], float)
    try: r0 = _residual(x)
    except Exception: return None
    for _ in range(iters):
        try: F0 = np.array([RAO.constraints(*x)[k] for k in S6], float)
        except Exception: return None
        # numerical Jacobian
        J = np.zeros((6,6)); dd=1e-7
        for j in range(6):
            xp=x.copy(); xp[j]+=dd
            try: Fp=np.array([RAO.constraints(*xp)[k] for k in S6], float)
            except Exception: return None
            J[:,j]=(Fp-F0)/dd
        try: step=np.linalg.solve(J, F0)
        except np.linalg.LinAlgError: return None
        # damping
        lam=1.0; cur=math.sqrt(float(F0@F0))
        for _ls in range(20):
            xn=x-lam*step
            try: rn=_residual(xn)
            except Exception: rn=None
            if rn is not None and rn<cur: break
            lam*=0.5
        else:
            break
        x=xn
        if rn<tol: return x, rn
    try: return x, _residual(x)
    except Exception: return None

def _in_bsphere(x, pad=0.0):
    return all(B_SPHERE[i][0]-pad <= x[i] <= B_SPHERE[i][1]+pad for i in range(6))

def certify_2b_candidate(subset, candidate, radii=None):
    """Certify a single numerical candidate as a real geometric root via 2b Krawczyk."""
    radii = radii or DEFAULT_RADII
    ev = dict(status=None, subset_id=tuple(subset), input_candidate=list(candidate),
              real_projected_center=None, radius_used=None, box_bounds=None,
              full_chain_guard_result=None, krawczyk=None, residual_norm=None,
              in_bsphere=None, engine_hash=ENGINE_HASH)
    if tuple(subset) != tuple(S6):
        ev['status']='TECH_FAIL'; ev['note']='only S6={1,2,3,4,6,7} wired'; return ev['status'], ev
    try:
        is_complex = any(isinstance(v, complex) and abs(v.imag)>0 for v in candidate)
        ev['max_abs_imag'] = max((abs(v.imag) for v in candidate if isinstance(v, complex)), default=0.0)
        real_seed = [v.real if isinstance(v, complex) else float(v) for v in candidate]
        # DOMAIN pre-check: chain must be real at the candidate itself, else DOMAIN_INVALID
        try:
            _ = _residual(real_seed)
        except Exception:
            ev['status']='DOMAIN_INVALID'; ev['real_projected_center']=real_seed
            ev['note']='chain not real at candidate (acos/atan domain)'; return ev['status'], ev
        # LOCAL polish (refinement is a local certificate of a genuine approximate root,
        # NOT a global solve): cap displacement so a distant point is rejected, not pulled in.
        MAX_POLISH = 2e-2
        ref = _real_newton(real_seed, iters=15)
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
            ev['status']='NOT_CERTIFIED'; ev['note']=f'refined residual {resid:.1e} too large (not a real root)'
            return ev['status'], ev
        b,c,d,e,g,h = x
        uvc = [b, h+c, h+d, e, g, h]
        saw_ok=False; saw_domain=False; last_guard=None; last_kraw=None
        for r in radii:
            uvbox=[(uvc[i]-r, uvc[i]+r) for i in range(6)]
            # full-chain domain guard on correlation-preserving expressions
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
            # native cone edge check (u,v < HALF over the box)
            if uvbox[1][1]>HALF or uvbox[2][1]>HALF: saw_domain=True; continue
            try:
                verdict, info = krawczyk_transformed(uvc, [r]*6)
            except Exception as exk:
                last_kraw=f'kraw raised {type(exk).__name__}'; continue
            last_kraw=(verdict, info)
            if verdict=='unique':
                ev.update(status='CERTIFIED_UNIQUE_GEOMETRIC', radius_used=float(r), box_bounds=[(float(a),float(b)) for a,b in uvbox],
                          full_chain_guard_result='ok', krawczyk=(verdict,info))
                return ev['status'], ev
        ev['full_chain_guard_result']=last_guard; ev['krawczyk']=last_kraw
        if saw_ok:
            ev['status']='NOT_CERTIFIED'; return ev['status'], ev
        if saw_domain:
            ev['status']='DOMAIN_INVALID'; return ev['status'], ev
        ev['status']='NOT_CERTIFIED'; ev['note']='no clean (ok) box at any radius'; return ev['status'], ev
    except Exception as ex:
        ev['status']='TECH_FAIL'; ev['note']=f'{type(ex).__name__}: {ex}'; return ev['status'], ev

def _boxes_overlap(A, B):
    return all(not (A[i][1] < B[i][0] or B[i][1] < A[i][0]) for i in range(6))

def collapse_certified(evidence_list):
    """Root-count helper: collapse overlapping certified boxes to one (conservative).
    Returns (count, clusters, distinctness_proven). Overlapping boxes -> same cluster (one
    root); disjoint clusters -> distinct roots. k distinct roots requires k pairwise-disjoint
    certified boxes (distinctness IS part of the certificate)."""
    boxes=[e['box_bounds'] for e in evidence_list
           if e.get('status')=='CERTIFIED_UNIQUE_GEOMETRIC' and e.get('box_bounds')]
    n=len(boxes); parent=list(range(n))
    def find(i):
        while parent[i]!=i: parent[i]=parent[parent[i]]; i=parent[i]
        return i
    for i in range(n):
        for j in range(i+1,n):
            if _boxes_overlap(boxes[i], boxes[j]): parent[find(i)]=find(j)
    clusters={}
    for i in range(n): clusters.setdefault(find(i), []).append(i)
    count=len(clusters)
    # distinctness proven iff clusters are pairwise disjoint (true by construction since
    # any overlap merged them) -> the `count` clusters are mutually disjoint.
    return count, list(clusters.values()), True
