"""
STAGE 3 instrument — existence-interval mapper.

Replaces fragile natural-parameter continuation with pseudo-arclength tracing of a
subset's solution branch (robust to folds and to near-pole conditioning). For each
subset it reports the per-subset object the spherical problem actually wants:

  algebraic existence interval   — h-range the branch covers (F=0 has a root)
  Gate-4-valid existence interval — h-sub-range where the figure passes Gate 4
  fold?                          — does the branch have an interior altitude turning point
  boundary mechanism             — what ends the valid interval / the branch:
                                     ordering | collision | closure | fold | pole | constructibility

On the branch, "constructible" coincides with "algebraic" (a root cannot be solved
where the chain is undefined), so the meaningful nesting is
  algebraic (= constructible) ⊇ Gate-4-valid.

Robustness: pseudo-arclength does not stop at turning points, so a fold no longer
truncates the interval; the branch ends only at the pole (h->90), a constructibility
boundary (chain undefined), or branch stall. This is the census-grade replacement for
the natural-parameter probe's upper-boundary classification.
"""
import os, sys, math, json, csv, argparse, hashlib
_here = os.path.dirname(os.path.abspath(__file__))
_root = _here
while _root != os.path.dirname(_root):
    if os.path.exists(os.path.join(_root, "sriyantra_plane.py")):
        break
    _root = os.path.dirname(_root)
for _p in (_here, _root, os.path.join(_root, "enumeration")):
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)
import numpy as np
import sriyantra as RAO
import sriyantra_plane as SP
import spherical_geo_check as GC
import stage1b_landscape as L
from stage1_fold_analysis import Ftil, jac6, tangent   # normalized constraint primitives

PI2 = math.pi/2; DEG = math.pi/180
TAU_DEG = 1e-3        # Gate-4 near-degeneracy floor (registered)
POLE_H  = 90.0 - 1.0  # POLE predicate: h >= pi/2 - delta, delta = 1 deg (registered)
NZW_DEG = 2.0         # near-zero-width (tangency) flag: valid interval width <= 2 deg
HERE = os.path.dirname(os.path.abspath(__file__))

# box B (plane) for the pole-domain check
_T = np.array([v for _, v in SP.TABLE3]); _lo, _hi = _T.min(0), _T.max(0); _rg = _hi-_lo
BLO, BHI = _lo-0.5*_rg, _hi+0.5*_rg
def in_box(p): return bool(np.all(p >= BLO) and np.all(p <= BHI))

def load():
    surv, fail = {}, []
    census = os.path.join(HERE, "campaign_results", "roots.jsonl")
    for line in open(census):
        j = json.loads(line)
        (surv.__setitem__(tuple(j["subset"]), j["roots"][0]["coords"]) if j.get("roots")
         else fail.append(tuple(j["subset"])))
    return surv, fail

def _stable_seed(sub, hd):
    key = ".".join(map(str, (*sub, round(float(hd), 3))))
    return int.from_bytes(hashlib.sha256(key.encode()).digest()[:4], "big")

def _spherical_box():
    """Registered seeding box: per-variable [min,max] of b,c,d,e,g over Rao's spherical
    Table 1 (as arc/r proportions), widened 50%, intersected with positivity (sec.6)."""
    rows=[]
    for _cons,(b,c,d,e,g,h) in RAO.TABLE1:
        r=PI2-h; rows.append([b/r,c/r,d/r,e/r,g/r])
    T=np.array(rows); lo,hi=T.min(0),T.max(0); rg=hi-lo
    return np.maximum(lo-0.5*rg, 1e-3), hi+0.5*rg
SBOX_LO, SBOX_HI = _spherical_box()

def _candidates(sub, R, rng, k):
    """Seeds for multistart.  AMENDMENT 01 — search policy != classification policy:
    we SEARCH preferentially in the Rao-spherical-box region but ACCEPT any in-domain,
    Gate-4-valid figure wherever Newton converges (the box is a seeding heuristic, not a
    validity criterion, exactly as the plane census kept in-domain Tier-2 solutions
    regardless of the Tier-1 seeding box). Three ordering-filtered seed families, all from
    the stable RNG:
      (1) box-preferential        — uniform over the spherical Table-1 box (widened 50%);
      (2) domain-wide log-uniform — full positive domain, covering small-intercept /
                                    out-of-box basins;
      (3) targeted near-degenerate— the symmetric collapse locus (b,e -> 0, c~d~g) that
          exploratory work found has thin attraction basins ordinary random seeding
          misses (documented rationale; introduced for coverage, not to favour any
          outcome)."""
    out=[]
    for _ in range(k):                                              # (1) box-preferential
        x=rng.uniform(SBOX_LO, SBOX_HI)*R; b,c,d,e,g=x
        if g<c and b+c<R and d+e<R: out.append(x)
    for _ in range(k):                                              # (2) domain-wide
        x=np.exp(rng.uniform(np.log(1e-3*R), np.log(0.97*R), 5)); b,c,d,e,g=x
        if g<c and b+c<R and d+e<R: out.append(x)
    for _ in range(max(40, k//3)):                                 # (3) near-degenerate locus
        base=rng.uniform(0.4*R, 0.97*R)
        x=np.array([rng.uniform(1e-3,0.03)*R, base, base,
                    rng.uniform(1e-3,0.03)*R, base*rng.uniform(0.95,0.999)])
        b,c,d,e,g=x
        if g<c and b+c<R and d+e<R: out.append(x)
    return out

def find_seed(sub, warm, alts=None, k=None):
    """A converged Gate-4-valid root anywhere on the branch (else any root).
    Reproducible: RNG seeded by a stable hashlib digest of (subset, altitude), NOT by
    Python's version-dependent hash(). Warm-start fallback (registered): subsets with no
    good (overlap>=3) survivor warm start (warm empty) get a larger targeted budget so
    seeding coverage does not depend on survivor adjacency or interpreter version."""
    if alts is None:
        alts=(48,40,32,56,24,64,18,72,36,28,44,52,20,68,16)
    if k is None:
        k = 50 if warm else 120
    best=None
    for hd in alts:
        R=PI2-hd*DEG; rng=np.random.default_rng(_stable_seed(sub, hd))
        cand=[np.array(w)*R for w in warm] + _candidates(sub, R, rng, k)
        for x0 in cand:
            x,res,ok,c=L.newton(sub, x0, hd*DEG, maxit=90)
            if ok:
                v,_=GC.gate4(*x, hd*DEG, closure_tol=1e-7)
                if v: return np.array([*x, hd*DEG])
                if best is None: best=np.array([*x, hd*DEG])
    return best

def trace_dir(sub, z0, sgn, ds=0.004, maxsteps=6000):
    """Trace one direction; return (records [(h_deg,valid,reason)], end_type)."""
    t=tangent(sub,z0)
    if t is None: return [], "tangent"
    t=sgn*t; z=z0.copy(); rec=[]; end="maxsteps"
    for _ in range(maxsteps):
        zc=z+ds*t; conv=undef=False
        for _ in range(80):
            f=Ftil(sub,zc)
            if f is None: undef=True; break
            rhs=np.concatenate([f,[float(np.dot(zc-z,t))-ds]])
            if np.max(np.abs(rhs))<1e-11: conv=True; break
            J=jac6(sub,zc)
            if J is None: undef=True; break
            try: dz=np.linalg.solve(np.vstack([J,t]),-rhs)
            except np.linalg.LinAlgError: break
            zc=zc+dz
        if undef: end="constructibility"; break
        if not conv: end="stall"; break
        z=zc; hd=z[5]/DEG
        v,why=GC.gate4(*z[:5],z[5],closure_tol=1e-7)
        rec.append((hd, v, why, z[:5].copy()))
        if hd>=89.7: end="pole"; break
        if hd<=8.0:  end="lowfloor"; break
        tn=tangent(sub,z,prefer=t)
        if tn is None: end="tangent"; break
        t=tn
    return rec, end

def map_subset(sub, warm, plane_feasible):
    z0=find_seed(sub,warm)
    if z0 is None:
        return dict(cls="ALGEBRAIC_EMPTY", alg=None, valid=None, fold=False, ends=(),
                    vbound=None, pole_inbox=None, near_degenerate=None,
                    near_zero_width=None, tier="-", halt=False)
    recA,endA=trace_dir(sub,z0,+1); recB,endB=trace_dir(sub,z0,-1)
    rec=recB[::-1]+[(z0[5]/DEG, *GC.gate4(*z0[:5],z0[5],closure_tol=1e-7), z0[:5])]+recA
    hs=np.array([r[0] for r in rec])
    valid_hs=np.array([r[0] for r in rec if r[1]])
    alg=(float(hs.min()), float(hs.max()))
    valid=(float(valid_hs.min()), float(valid_hs.max())) if valid_hs.size else None
    # fold: interior altitude turning point within a single direction
    def has_fold(r):
        h=np.array([x[0] for x in r]);
        if len(h)<4: return False
        d=np.diff(h); s=np.sign(d); s=s[s!=0]
        return bool(np.any(s[:-1]!=s[1:]))
    fold=has_fold(recA) or has_fold(recB)
    # boundary mechanism at the valid-interval edges: gate4 reason of nearest invalid neighbours
    vbound=None
    if valid is not None:
        reasons=set()
        for i,(hd,v,why,_) in enumerate(rec):
            if not v and any(rec[j][1] for j in (i-1,i+1) if 0<=j<len(rec)):
                key="ordering" if "ordering" in why else "collision" if "close" in why or "coincide" in why else "closure" if "close" in why else "other"
                reasons.add(key)
        # the valid interval may be ended by a branch end (pole/fold) rather than invalidity
        vbound=",".join(sorted(reasons)) if reasons else "branch-end"
    # near-degeneracy flag (Gate-4 tau_deg floor, registered tau_deg = 1e-3): the
    # least-degenerate valid figure still has a base-point GAP below tau_deg*r.
    # base-axis gaps for (b,c,d,e,g) at radius R: [R-(b+c), b, c-g, g, d, e, R-(d+e)]
    def min_gap_ratio(x, R):
        b,c,d,e,g = x
        return float(min(R-(b+c), b, c-g, g, d, e, R-(d+e))) / R
    near_degenerate=None
    if valid is not None:
        best=0.0
        for hd,v,why,x in rec:
            if v: best=max(best, min_gap_ratio(x, PI2-hd*DEG))
        near_degenerate = best < TAU_DEG
    # near-zero-width (tangency) flag (sec.7): the Gate-4-valid altitude interval is a sliver
    near_zero_width = (valid is not None) and (valid[1]-valid[0] <= NZW_DEG)
    # pole-domain check: only meaningful if a VALID figure reaches the pole
    pole_inbox=None
    if valid is not None and valid[1] >= POLE_H:
        near=[r for r in rec if r[1] and r[0] >= POLE_H]
        pole_inbox = any(in_box(np.array(r[3])/(PI2-r[0]*DEG)) for r in near)
    # classify  (frozen prereg sec.8 decision procedure)
    halt=False
    if valid is None:
        cls="ALGEBRAIC_ONLY"
    elif valid[1] >= POLE_H:                              # a VALID figure reaches the pole
        if pole_inbox:
            if plane_feasible:
                cls="PLANE_CONTINUATION"
            else:
                cls="HALT (PLANE_INCONSISTENCY)"; halt=True
        else:
            cls="POLE_OUT_OF_DOMAIN"
    else:
        cls="SPHERICAL_ONLY"
    # robustness tier (sec.7): tangency and near-degenerate figures are retained but
    # flagged and excluded from robust counts
    if valid is None:
        tier="-"
    elif near_zero_width:
        tier="tangency"
    elif near_degenerate:
        tier="near_degenerate"
    else:
        tier="robust"
    return dict(cls=cls, alg=alg, valid=valid, fold=fold, ends=(endA,endB),
                vbound=vbound, pole_inbox=pole_inbox, near_degenerate=near_degenerate,
                near_zero_width=near_zero_width, tier=tier, halt=halt)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--subsets", default="", help="comma-separated like '1-2-3-4-6,1-2-3-6-13' (default: small demo set)")
    ap.add_argument("--from-csv", default="", help="map all SPHERICAL_ONLY/POLE_FLAG rows from a probe csv")
    ap.add_argument("--out", default="spherical_existence_intervals.csv")
    args=ap.parse_args()
    surv,fail=load(); surv_items=list(surv.items())
    survset=set(surv.keys())
    def warm(sub):                       # principled warm starts only (overlap >=3); else none
        for thr in (4,3):
            w=[r for s,r in surv_items if len(set(sub)&set(s))>=thr][:6]
            if w: return w
        return []                        # overlap<3 -> find_seed escalates to targeted budget
    def feasible(sub): return tuple(sub) in survset

    if args.from_csv:
        rows=[tuple(eval(r["subset"])) for r in csv.DictReader(open(args.from_csv))
              if r["class"] in ("SPHERICAL_ONLY","POLE_FLAG")]
    elif args.subsets:
        rows=[tuple(int(x) for x in s.split("-")) for s in args.subsets.split(",")]
    else:
        rows=[(1,2,3,4,6),(1,2,3,6,13),(1,2,3,5,6),(1,2,3,4,7),(1,2,5,8,15)]

    out=open(args.out,"w",newline=""); w=csv.writer(out)
    w.writerow(["subset","class","tier","valid_lo","valid_hi","alg_lo","alg_hi","fold","near_degenerate","near_zero_width","valid_boundary","branch_ends"])
    for i,sub in enumerate(rows):
        r=map_subset(sub,warm(sub),feasible(sub))
        if r.get("halt"):
            print(f"  *** Gate 6 HALT on {sub}: PLANE_INCONSISTENCY — census stops, plane census re-examined ***")
        vl=f"{r['valid'][0]:.1f}" if r['valid'] else ""; vh=f"{r['valid'][1]:.1f}" if r['valid'] else ""
        al=f"{r['alg'][0]:.1f}" if r['alg'] else ""; ah=f"{r['alg'][1]:.1f}" if r['alg'] else ""
        w.writerow([list(sub),r['cls'],r.get('tier'),vl,vh,al,ah,r['fold'],r.get('near_degenerate'),r.get('near_zero_width'),r['vbound'] or "",";".join(r['ends'])])
        print(f"  {str(sub):16s} {r['cls']:24s} valid=[{vl},{vh}] alg=[{al},{ah}] "
              f"tier={r.get('tier')} fold={r['fold']} neardegen={r.get('near_degenerate')} bound={r['vbound']}")
        if (i+1)%25==0: out.flush()
    out.close(); print(f"\nwrote {args.out}")

if __name__=="__main__":
    main()
