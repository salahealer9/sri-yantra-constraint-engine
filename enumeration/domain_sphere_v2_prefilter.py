"""
domain_sphere_v2_prefilter.py — EXPLORATORY copy of frozen domain_sphere.py
with the cone-edge analytic domain pre-filter wired in behind a flag
(USE_CONE_EDGE_PREFILTER). The frozen v1.2 domain_sphere.py is UNCHANGED. The
pre-filter only adds EARLIER 'domain' exits in classify; it does not alter the
full-chain guard, cone_F, Krawczyk, or enum logic.

domain_sphere.py — certified real-box branch-and-prune for the spherical Sri
Yantra subset {1,2,3,4,6,7} over the registered box B_sphere.

Mirrors the FROZEN plane driver domain_v3.py (domain_excluded / excluded /
krawczyk / enum) structure, adapted to the sphere:
  * 6 variables (b,c,d,e,g,h), radians; r = pi/2 - h internal.
  * DOMAIN SEMANTICS = FULL-CHAIN-REAL. A box is admissible only if Rao's ENTIRE
    construction is real over it (full_chain_domain_guard runs all ~40 chain
    nodes for their domain side effects). A subset root must be a geometrically
    valid spherical figure, consistent with Gate-4: a root is not merely an
    algebraic zero of the selected equations, it must correspond to a real
    construction. Unused nodes (e.g. radial acos r16..r19) therefore still impose
    domain conditions and may exclude/split boxes.
  * CONSTRAINT EVALUATION = cone-restricted. Only the chain nodes feeding
    F1,F2,F3,F4,F6,F7 are computed for the constraint VALUES (cone_F); unused
    constraints are not evaluated. This is a performance choice that does NOT
    enlarge the admissible domain, because the full-chain domain guard runs first.
  * transcendental guards: SplitNeeded => subdivide; DomainError => box excluded.
  * AA-Krawczyk certification via the 6-var DualRS Jacobian enclosure; Krawczyk
    runs only on boxes already passed full-chain-real by classify, so certified
    roots are geometrically valid figures.

Budget (FROZEN pilot pre-registration v1.2): wall_clock 7200s, max_depth 200,
r_cert 3e-3, max_boxes 3_000_000, single-threaded. Truth source for Fm at box
centers: frozen sriyantra.py (RAO.constraints).
"""
import sys, os, time, math
_here = os.path.dirname(os.path.abspath(__file__))
_root = _here
while _root != os.path.dirname(_root):
    if os.path.exists(os.path.join(_root, "sriyantra.py")):
        break
    _root = os.path.dirname(_root)
for _p in (_here, _root, os.path.join(_root, "enumeration")):
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)
import numpy as np
import sriyantra as RAO
from aar import AAr
import aar_sphere as _S
from aar_sphere import DualRS, SplitNeeded, DomainError
from chain_sphere import AA_FN, DUAL_FN, HALF_PI
from prefilter_v2 import prefilter_excludes

USE_CONE_EDGE_PREFILTER = True   # exploratory flag; False == frozen v1.2 behaviour

S6 = [1, 2, 3, 4, 6, 7]
# frozen B_sphere (radians): pooled TABLE1 hull, widen 50%/side, positivity + 0<h<pi/2
B_SPHERE = [(1e-6, 0.763186), (1e-6, 1.103454), (1e-6, 1.302556),
            (1e-6, 0.647740), (1e-6, 0.687977), (1e-6, 1.570795)]


def cone_F(b, c, d, e, g, h, FN):
    """Compute ONLY the chain nodes feeding F1,F2,F3,F4,F6,F7. Returns {k:F_k}.
    Raises SplitNeeded / DomainError from the transcendental guards."""
    sin, cos, tan, atan, acos = FN.sin, FN.cos, FN.tan, FN.atan, FN.acos
    r = HALF_PI - h
    x1 = acos(cos(r) / cos(c))
    x2 = acos(cos(r) / cos(d))
    x3 = atan(sin(r - c) / sin(r + d) * tan(x2))
    x4 = atan(sin(r - d) / sin(r + c) * tan(x1))
    x5 = atan(sin(b) / sin(b + c + d) * tan(x4))
    x6 = atan(sin(e) / sin(c + d + e) * tan(x3))
    # point 7 + concentricity (F2, F6)
    S7 = d + g
    Q7 = (sin(d + g) / sin(c + d)) * (tan(x5) / tan(x6))
    U7 = atan(sin(S7) / (Q7 + cos(S7)))
    x7 = atan(sin(U7) / sin(c + d) * tan(x5))
    t  = atan(tan(d + g - U7) / sin(x7))
    rT = atan(sin(x7) * tan(t / 2))
    # point 8 (F3)
    S8 = r + g
    Q8 = (sin(d + g) / sin(r + c)) * (tan(x1) / tan(x6))
    U8 = atan(sin(S8) / (Q8 + cos(S8)))
    V8 = S8 - U8
    v8 = r - U8 - d
    # point 9
    S9 = r + d
    Q9 = (sin(c + d) / sin(r + d)) * (tan(x2) / tan(x5))
    U9 = atan(sin(S9) / (Q9 + cos(S9)))
    v9 = r - U9 - c
    # points 10, 18
    x10 = atan(sin(b + c - g) / sin(b + c + d) * tan(x4))
    x18 = atan(sin(b + c + d + v8) / sin(b + c + d) * tan(x4))
    # point 12 (F4)
    S12 = d + g + v8
    Q12 = (sin(d + g + v8) / sin(d + g)) * (tan(x6) / tan(x10))
    U12 = atan(sin(S12) / (Q12 + cos(S12)))
    v12 = d + g - U12
    # points 13, 19
    x13 = atan(sin(e + v12) / sin(c + d + e) * tan(x3))
    x19 = atan(sin(c + d + e + v9) / sin(c + d + e) * tan(x3))
    # x11, x11a (F1)
    x11 = atan(sin(d + g) / sin(c + d) * tan(x5))
    x11a = atan(sin(v9 + c - g) / sin(v9 + c + d - v12) * tan(x13))

    def iso(V, x): return cos(V) - cos(x * 2) / cos(x)
    return {1: x11 - x11a,
            2: d - U7 - rT,
            3: iso(V8, x10),
            4: iso(c + d + v9 - v12, x13),
            6: iso(d + g - U7, x7),
            7: x18 - x19}


def _aabox(box): return [AAr.var((lo + hi) / 2, (hi - lo) / 2) for (lo, hi) in box]


def full_chain_domain_guard(AV):
    """Domain validity is full-chain-real (NOT cone-only): a box is admissible
    only if Rao's ENTIRE construction is real over it. A subset root must be a
    geometrically valid spherical figure, so unused nodes (e.g. radial acos
    r16..r19) still impose domain conditions. Returns 'domain' (entirely
    invalid -> exclude), 'split' (straddles a domain/inflection seam -> subdivide),
    or 'ok' (full chain real over the box). Evaluated for its domain side effects;
    constraint VALUES come from cone_F."""
    from chain_sphere import chain_sph
    try:
        chain_sph(*AV, AA_FN)            # full ~40-node chain
    except DomainError:
        return 'domain'
    except SplitNeeded:
        return 'split'
    except (ValueError, ZeroDivisionError, OverflowError):
        return 'split'
    return 'ok'


def classify(box):
    """Full-chain-real domain guard FIRST, then cone-restricted constraint test.
       ('domain',)        full chain provably non-real over the box (exclude);
       ('split',)         full-chain or cone seam / undecidable (subdivide);
       ('excluded',)      some selected F_k enclosure excludes 0 (exclude);
       ('indeterminate',) all selected F_k enclosures contain 0 (subdivide/certify).
    Domain validity = full Rao chain real; constraint evaluation = selected cone.
    EXPLORATORY: a sound cone-edge analytic pre-filter may add an earlier 'domain'
    exit (proof-by-inequality: h_lo+c_lo>pi/2 or h_lo+d_lo>pi/2 => x1/x2 undefined
    everywhere). It only excludes provably-empty boxes, never a valid one."""
    if USE_CONE_EDGE_PREFILTER and prefilter_excludes(box):
        return 'domain'
    AAr._n = [0]
    AV = _aabox(box)
    # 1. full-chain-real domain guard (does NOT enlarge the admissible domain)
    g = full_chain_domain_guard(AV)
    if g == 'domain':
        return 'domain'
    if g == 'split':
        return 'split'
    # 2. selected-constraint test on the dependency cone (full chain already real)
    AAr._n = [0]
    try:
        F = cone_F(*_aabox(box), AA_FN)
    except DomainError:
        return 'domain'
    except SplitNeeded:
        return 'split'
    except (ValueError, ZeroDivisionError, OverflowError):
        return 'split'
    for k in S6:
        lo, hi = F[k].iv()
        if not (lo <= 0 <= hi):
            return 'excluded'
    return 'indeterminate'


def _hw(x): lo, hi = x.iv(); return (hi - lo) / 2


def _krawczyk_cone_only(center, rvec):
    """INTERNAL, fast. 6-var AA-Krawczyk on subset S6 over the dependency cone.
    Does NOT run the full-chain domain guard — callers MUST ensure the box is
    full-chain-real first (enum does, via classify). For an externally safe
    certificate use `certify_box`. center: list[6]; rvec: list[6] half-widths.
    Returns 'unique' | 'empty' | 'split'."""
    AAr._n = [0]
    try:
        Fd = cone_F(*[DualRS.var(k, center[k], rvec[k]) for k in range(6)], DUAL_FN)
    except (SplitNeeded, DomainError, ValueError, ZeroDivisionError, OverflowError):
        return 'split'
    Jm = np.array([[Fd[S6[i]].grad[j].c for j in range(6)] for i in range(6)])
    if not np.all(np.isfinite(Jm)):
        return 'split'
    Jr = np.array([[_hw(Fd[S6[i]].grad[j]) for j in range(6)] for i in range(6)])
    try:
        Y = np.linalg.inv(Jm)
    except np.linalg.LinAlgError:
        return 'split'
    try:
        Fm = np.array([RAO.constraints(*center)[k] for k in S6], float)
    except Exception:
        return 'split'
    rv = np.array(rvec)
    M = np.eye(6) - Y @ Jm
    Mr = np.abs(Y) @ Jr
    Kc = -(Y @ Fm)
    Kh = (np.abs(M) + Mr) @ rv
    lo = np.array(center) + Kc - Kh
    hi = np.array(center) + Kc + Kh
    Xl = np.array(center) - rv
    Xh = np.array(center) + rv
    if np.all(hi < Xh) and np.all(lo > Xl):
        return 'unique'
    if np.any(hi < Xl) or np.any(lo > Xh):
        return 'empty'
    return 'split'


def certify_box(center, rvec):
    """EXPOSED, safe certificate path. Runs the full-chain-real domain guard on
    the box FIRST, so a 'unique' result is a certificate of a geometrically valid
    spherical figure (not merely an algebraic zero of the selected constraints).
    Returns 'domain' | 'split' | 'unique' | 'empty'."""
    box = [(center[i] - rvec[i], center[i] + rvec[i]) for i in range(6)]
    AAr._n = [0]
    g = full_chain_domain_guard(_aabox(box))
    if g != 'ok':
        return g                     # 'domain' or 'split' — not a valid figure here
    return _krawczyk_cone_only(center, rvec)


def enum(tlim=7200, max_depth=200, r_cert=3e-3, max_boxes=3_000_000, log_every=0):
    t0 = time.time()
    stack = [(list(B_SPHERE), 0)]
    proc = dom = excl = unres = maxd = 0
    cert = []
    maxq = 1
    while stack and proc < max_boxes and time.time() - t0 < tlim:
        maxq = max(maxq, len(stack))
        box, dep = stack.pop()
        proc += 1
        maxd = max(maxd, dep)
        if log_every and proc % log_every == 0:
            print(f"    [{proc} boxes  q={len(stack)}  dom={dom} excl={excl} "
                  f"cert={len(cert)} unres={unres}  d={maxd}  {time.time()-t0:.0f}s]",
                  flush=True)
        cls = classify(box)
        if cls == 'domain':
            dom += 1; continue
        if cls == 'excluded':
            excl += 1; continue
        rvec = [(hi - lo) / 2 for (lo, hi) in box]
        rad = max(rvec)
        if cls == 'indeterminate' and rad <= r_cert:
            center = [(lo + hi) / 2 for (lo, hi) in box]
            v = _krawczyk_cone_only(center, rvec)   # box already full-chain-real (classify)
            if v == 'unique':
                if not any(max(abs(center[i] - q[i]) for i in range(6)) < 2 * r_cert
                           for q in cert):
                    cert.append(center)
                continue
            if v == 'empty':
                continue
        if dep >= max_depth:
            unres += 1; continue
        w = [hi - lo for (lo, hi) in box]
        k = int(np.argmax(w))
        lo, hi = box[k]; mid = (lo + hi) / 2
        L = list(box); L[k] = (lo, mid)
        R = list(box); R[k] = (mid, hi)
        stack.append((L, dep + 1)); stack.append((R, dep + 1))
    return dict(boxes=proc, cert=cert, dom=dom, excl=excl, unres=unres,
                maxd=maxd, maxq=maxq, secs=round(time.time() - t0, 1),
                complete=(len(stack) == 0), queue_left=len(stack))
