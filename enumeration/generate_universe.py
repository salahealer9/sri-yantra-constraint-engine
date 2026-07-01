"""
generate_universe.py — reproduce the COMMITTED C(18,4) well-posed subset universe for the
spherical presence-first census, faithfully reusing analyze_deps.py's generic-rank scan.

Universe: {1,2} u T for T in combinations(F3..F20, 4)  [C(18,4)=3060 systems], minus the
generically rank-deficient (ratio_over_points < DEG_TOL) ones. Records the ACTUAL well-posed
count produced on this machine (not a memory-forced number) plus a content hash of the subset
list, so downstream drivers bind to the exact universe by sha256.
"""
import os, sys, json, hashlib
import numpy as np
from itertools import combinations
_here = os.path.dirname(os.path.abspath(__file__))
_root = _here
while _root != os.path.dirname(_root):
    if os.path.exists(os.path.join(_root, "sriyantra.py")):
        break
    _root = os.path.dirname(_root)
for _p in (_here, _root, os.path.join(_root, "enumeration")):
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)
from sriyantra import constraints, chain, DomainError, TABLE1

DEG_TOL = 1e-7
CHOOSABLE = list(range(3,21))   # F3..F20
ESS = [0,1]                      # F1,F2 (0-indexed rows)

def Fvec(p):
    F = constraints(*p); return np.array([F[i] for i in range(1,21)], float)
def numjac(p, eps=1e-6):
    J=np.empty((20,6))
    for j in range(6):
        pp=list(p); pm=list(p); pp[j]+=eps; pm[j]-=eps
        J[:,j]=(Fvec(pp)-Fvec(pm))/(2*eps)
    return J

def build_sample_jacobians():
    rng=np.random.default_rng(0)              # SAME seed as analyze_deps.py -> reproducible
    seeds=[vals for _,vals in TABLE1]; points=[]; attempts=0
    while len(points)<8 and attempts<5000:
        attempts+=1
        base=seeds[rng.integers(len(seeds))]
        cand=tuple(np.array(base)+rng.normal(0,0.02,6))
        try:
            J=numjac(cand)
            if np.all(np.isfinite(J)) and np.all(np.isfinite(Fvec(cand))): points.append(cand)
        except (DomainError,ValueError,ZeroDivisionError): pass
    return [numjac(p) for p in points]

def main():
    Js=build_sample_jacobians()
    def ratio(rows):
        best=0.0
        for J in Js:
            sv=np.linalg.svd(J[rows,:],compute_uv=False); best=max(best, sv[-1]/sv[0])
        return best
    wellposed=[]; degenerate=[]
    for T in combinations(CHOOSABLE,4):
        rows=ESS+[t-1 for t in T]
        (degenerate if ratio(rows)<DEG_TOL else wellposed).append(tuple(sorted((1,2)+T)))
    wellposed.sort()
    subs_json=json.dumps([list(s) for s in wellposed])
    subs_sha=hashlib.sha256(subs_json.encode()).hexdigest()
    eng_sha=hashlib.sha256(open(os.path.join(_root,'sriyantra.py'),'rb').read()).hexdigest()
    out=dict(
        schema_version='subset_universe_v1',
        generator='generate_universe.py (faithful reuse of analyze_deps.py C(18,4) rank scan)',
        base='{1,2} u T, T in combinations(F3..F20, 4)', n_total=3060,
        n_degenerate=len(degenerate), n_wellposed=len(wellposed),
        DEG_TOL=DEG_TOL, n_sample_points=len(Js),
        subsets_sha256=subs_sha, engine_sha256=eng_sha,
        subsets=[list(s) for s in wellposed],
    )
    json.dump(out, open(os.path.join(_root,'docs','subset_universe.json'),'w'))
    print(f"C(18,4) = {out['n_total']}")
    print(f"  rank-deficient : {out['n_degenerate']}")
    print(f"  WELL-POSED     : {out['n_wellposed']}   <- actual count (universe)")
    print(f"  subsets_sha256 : {subs_sha[:16]}...")
    print(f"  benchmark {{1,2,3,4,6,7}} in universe: {tuple([1,2,3,4,6,7]) in set(wellposed)}")
    print("wrote subset_universe.json")

if __name__=='__main__': main()
