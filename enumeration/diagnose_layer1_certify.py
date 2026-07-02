"""
diagnose_layer1_shard.py — read a Layer-1 shard: certify each candidate (certify_2b_general
DECIDES), split Layer-1 (all certified) vs Layer-2 (Gate-4 valid), and isolate viol-stratum-ONLY
discoveries (certified roots reached by NO other stratum). Read-only; no census write.

Answers the four shard questions:
  1. Layer-1 certified total (subsets with >=1 certified root)
  2. Gate-4-valid subset (Layer-2)
  3. Gate-4-rejected subset (algebraically real, Rao-invalid)
  4. viol-stratum-ONLY certified discoveries  <- the scientific payoff
Plus: duplicate/multi-root subsets, displacement distribution, per-stratum reach.
"""
import sys, os, json, argparse, math
from collections import Counter, defaultdict
_here = os.path.dirname(os.path.abspath(__file__))
_root = _here
while _root != os.path.dirname(_root):
    if os.path.exists(os.path.join(_root, "sriyantra.py")):
        break
    _root = os.path.dirname(_root)
for _p in (_here, _root, os.path.join(_root, "enumeration")):
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)
import certify_2b_general as GEN
from certify_2b import collapse_certified

def gate4_status(coords):
    GATE4_CLOSURE_TOL = 1e-7
    try:
        from spherical_geo_check import gate4
        b,c,d,e,g,h=coords
        v,reason = gate4(b,c,d,e,g,h, closure_tol=GATE4_CLOSURE_TOL)
        return bool(v),reason
    except Exception:
        # ordering-only fallback
        import math as _m; b,c,d,e,g,h=coords; r=_m.pi/2-h
        order=[-r,-(b+c),-c,-g,0.0,d,d+e,r]
        ok=all(order[i]<order[i+1] for i in range(len(order)-1))
        return ok, ('valid' if ok else 'base-point ordering violated')

def main(path):
    rows=[json.loads(l) for l in open(path)]
    L1=set(); L2valid=set(); L2rej=set(); notcert=Counter()
    multi=Counter()  # subset -> # distinct certified roots
    disp=[]; strat_reach=defaultdict(int); strat_cert=defaultdict(int)
    viol_only=[]   # (subset, coords) certified roots whose ONLY proposing stratum was 'viol'
    viol_stats=Counter()
    percand=[]
    for r in rows:
        sub=tuple(r['subset'])
        prov=r.get('provenance', [])
        cands=r['candidates']
        # map coords-key -> set of strata that proposed it
        strata_by_key=defaultdict(set)
        for p in prov:
            k=tuple(round(x,9) for x in (p.get('coords') or []))
            if k: strata_by_key[k].add(p.get('stratum','?'))
            if 'displacement' in p: disp.append(p['displacement'])
            strat_reach[p.get('stratum','?')]+=1
        cert_evs=[]   # (evidence, strata, coords) for each CERTIFIED candidate this subset
        for c in cands:
            coords=c if isinstance(c,list) else c.get('coords')
            st,ev=GEN.certify_2b_candidate(list(sub), coords)
            key=tuple(round(x,9) for x in coords)
            strata=strata_by_key.get(key, set())
            if st=='CERTIFIED_UNIQUE_GEOMETRIC':
                cert_evs.append((ev, strata, coords))
                for s2 in strata: strat_cert[s2]+=1
            else:
                notcert[st]+=1
        if not cert_evs: continue
        # DISTINCT roots via disjoint-box collapse (candidates != roots)
        try:
            ncount, clusters, disjoint = collapse_certified([ev for ev,_,_ in cert_evs])
            n_distinct = ncount
        except Exception:
            n_distinct = 1   # conservative: overlapping -> 1 root
        L1.add(sub); multi[sub]=n_distinct
        # Gate-4 split over DISTINCT roots (use one representative per certified candidate; a subset
        # can carry both valid and rejected distinct roots)
        for ev, strata, coords in cert_evs:
            gv,greason=gate4_status(ev['real_projected_center'])
            (L2valid if gv else L2rej).add(sub)
            # viol-stratum full split
            if 'viol' in strata: viol_stats['proposed_cert']+=1
            if strata=={'viol'}:
                viol_only.append((sub,[round(x,5) for x in coords],gv))
                viol_stats['only']+=1
                viol_stats['only_rej' if not gv else 'only_valid']+=1
            percand.append((sub, gv, sorted(strata)))
    print(f"=== Layer-1 shard diagnosis: {path} ===")
    print(f"subsets with candidates      : {len(rows)}")
    print(f"1. Layer-1 certified subsets  : {len(L1)}")
    print(f"2. Gate-4 VALID (Layer-2)     : {len(L2valid)}")
    print(f"3. Gate-4 REJECTED (Rao-inval): {len(L2rej)}")
    both=L2valid & L2rej
    if both: print(f"   (subsets with BOTH valid & rejected roots: {len(both)} -> multi-root)")
    print(f"4. VIOL-STRATUM-ONLY certified: {len(viol_only)}   <- Gate-4-filtered generator would MISS these")
    for sub,co,gv in viol_only[:12]:
        print(f"     {sub} gate4_valid={gv} coords={co}")
    total_distinct=sum(multi.values())
    print(f"\ncertified DISTINCT roots (disjoint-box collapse): {total_distinct} across {len(L1)} subsets")
    print(f"multi-root subsets (>1 disjoint certified root): {sum(1 for v in multi.values() if v>1)}")
    print(f"viol split: proposed_certified={viol_stats['proposed_cert']} only={viol_stats['only']} "
          f"only_gate4_rejected={viol_stats['only_rej']} only_gate4_valid={viol_stats['only_valid']}")
    if notcert: print("non-certified candidates:", dict(notcert))
    if disp:
        disp.sort(); n=len(disp)
        print(f"displacement: min {disp[0]:.3f} med {disp[n//2]:.3f} max {disp[-1]:.3f}")
    print("per-stratum: proposed / certified")
    for s in sorted(strat_reach): print(f"  {s:8s} {strat_reach[s]:5d} / {strat_cert.get(s,0)}")
    print(f"\nREAD: viol-only>0 -> neutral Layer-1 finds roots a filtered generator misses (justifies design).")
    print("      viol-only=0 -> invalid family likely small / warm-start-captured (also a real bound).")

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--candidates', default='docs/candidates_layer1_shard0.jsonl')
    a=ap.parse_args(); main(a.candidates)
