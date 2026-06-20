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
import os, sys, math, json, csv, argparse
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
import sriyantra_plane as SP
import spherical_geo_check as GC
import stage1b_landscape as L
from stage1_fold_analysis import Ftil, jac6, tangent   # normalized constraint primitives

PI2 = math.pi/2; DEG = math.pi/180
HERE = os.path.dirname(os.path.abspath(__file__))

# box B (plane) for the pole-domain check
_T = np.array([v for _, v in SP.TABLE3]); _lo, _hi = _T.min(0), _T.max(0); _rg = _hi-_lo
BLO, BHI = _lo-0.5*_rg, _hi+0.5*_rg
def in_box(p): return bool(np.all(p >= BLO) and np.all(p <= BHI))

def load():
    surv, fail = {}, []
    census_path = os.path.join(os.path.dirname(__file__), "campaign_results", "roots.jsonl")
    for line in open(census_path):
        j = json.loads(line)
        (surv.__setitem__(tuple(j["subset"]), j["roots"][0]["coords"]) if j.get("roots")
         else fail.append(tuple(j["subset"])))
    return surv, fail

def find_seed(sub, warm, alts=(56,40,28,68,18,75,14), k=40):
    """A converged root anywhere on the branch (prefer Gate-4-valid)."""
    best=None
    for h in alts:
        R=PI2-h*DEG; rng=np.random.default_rng((hash(sub)^int(h))&0x7fffffff)
        cand=[np.array(w)*R for w in warm]
        while len(cand)<k+len(warm):
            x=rng.uniform(0.02*R,0.92*R,5); b,c,d,e,g=x
            if g<c and b+c<R and d+e<R: cand.append(x)
        for x0 in cand:
            x,res,ok,c=L.newton(sub,x0,h*DEG,maxit=60)
            if ok:
                v,_=GC.gate4(*x,h*DEG,closure_tol=1e-7)
                if v: return np.array([*x,h*DEG])      # valid seed: best
                if best is None: best=np.array([*x,h*DEG])
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

def map_subset(sub, warm):
    z0=find_seed(sub,warm)
    if z0 is None:
        return dict(cls="ALGEBRAIC_EMPTY", alg=None, valid=None, fold=False, ends=(), vbound=None)
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
    # pole-domain check: only meaningful if a VALID figure reaches the pole
    pole_inbox=None
    if valid is not None and valid[1] >= 88.0:
        near=[r for r in rec if r[1] and r[0] >= 88.0]
        pole_inbox = any(in_box(np.array(r[3])/(PI2-r[0]*DEG)) for r in near)
    # classify
    if valid is None: cls="ALGEBRAIC_ONLY (no Gate-4-valid h)"
    elif valid[1] >= 88.0:
        cls = "POLE_FLAG (in-box: SCRUTINIZE)" if pole_inbox else "POLE_FLAG (out-of-domain)"
    else:
        cls="SPHERICAL_ONLY (valid, capped below pole)"
    return dict(cls=cls, alg=alg, valid=valid, fold=fold, ends=(endA,endB),
                vbound=vbound, pole_inbox=pole_inbox)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--subsets", default="", help="comma-separated like '1-2-3-4-6,1-2-3-6-13' (default: small demo set)")
    ap.add_argument("--from-csv", default="", help="map all SPHERICAL_ONLY/POLE_FLAG rows from a probe csv")
    ap.add_argument("--out", default="spherical_existence_intervals.csv")
    args=ap.parse_args()
    surv,fail=load(); surv_items=list(surv.items())
    def warm(sub): return [r for s,r in surv_items if len(set(sub)&set(s))>=4][:6]

    if args.from_csv:
        rows=[tuple(eval(r["subset"])) for r in csv.DictReader(open(args.from_csv))
              if r["class"] in ("SPHERICAL_ONLY","POLE_FLAG")]
    elif args.subsets:
        rows=[tuple(int(x) for x in s.split("-")) for s in args.subsets.split(",")]
    else:
        rows=[(1,2,3,4,6),(1,2,3,6,13),(1,2,3,5,6),(1,2,3,4,7),(1,2,5,8,15)]

    out=open(args.out,"w",newline=""); w=csv.writer(out)
    w.writerow(["subset","class","valid_lo","valid_hi","alg_lo","alg_hi","fold","valid_boundary","branch_ends"])
    for i,sub in enumerate(rows):
        r=map_subset(sub,warm(sub))
        vl=f"{r['valid'][0]:.1f}" if r['valid'] else ""; vh=f"{r['valid'][1]:.1f}" if r['valid'] else ""
        al=f"{r['alg'][0]:.1f}" if r['alg'] else ""; ah=f"{r['alg'][1]:.1f}" if r['alg'] else ""
        w.writerow([list(sub),r['cls'],vl,vh,al,ah,r['fold'],r['vbound'] or "",";".join(r['ends'])])
        print(f"  {str(sub):16s} {r['cls']:34s} valid=[{vl},{vh}] alg=[{al},{ah}] "
              f"fold={r['fold']} bound={r['vbound']} ends={r['ends']}")
        if (i+1)%25==0: out.flush()
    out.close(); print(f"\nwrote {args.out}")

if __name__=="__main__":
    main()