"""
diagnose_layer1_shard.py — READ-ONLY diagnostic of a layer1 candidates file against the
committed census. Writes nothing, certifies nothing. Answers, before certification:

  1. COVERAGE  — how many candidate subsets are currently UNRESOLVED_NO_CANDIDATE
                 (potential new certifications) vs already FEASIBLE_CERTIFIED?
  2. AGREEMENT — for already-certified subsets: does a layer1 candidate land on the
                 known census root (|dx| < 1e-9), a DIFFERENT root (multiplicity!),
                 or both?
  3. MULTIPLICITY — subsets with >1 distinct candidate (root_lower_bound may rise).
  4. STRATUM YIELD — which seed families actually produce candidates; in particular
                 whether 'viol' (containment-violating region) earns its place.
  5. GATE-4 SPLIT — provisional metadata tally (authoritative tags come later, on
                 certified centers).

Usage:
    python3 enumeration/diagnose_layer1_shard.py \
        --candidates docs/candidates_layer1_shard0.jsonl \
        --roots docs/census_union/spherical_roots.jsonl
"""
import json, argparse
import numpy as np
from collections import Counter, defaultdict

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--candidates', required=True)
    ap.add_argument('--roots', default='docs/census_union/spherical_roots.jsonl')
    ap.add_argument('--match-tol', type=float, default=1e-9)
    a=ap.parse_args()

    census={}
    for line in open(a.roots):
        j=json.loads(line)
        census[tuple(j['subset'])]=j

    rows=[json.loads(l) for l in open(a.candidates)]
    n_c=sum(len(r['candidates']) for r in rows)
    print(f"candidates file: {len(rows)} subsets, {n_c} candidates\n")

    strat=Counter(); g4=Counter(); alts=Counter()
    new_subsets=[]; known_subsets=[]; mult=[]
    for r in rows:
        sub=tuple(r['subset']); prov=r['provenance']
        for p in prov:
            strat[p['stratum']]+=1
            g4['valid' if p['gate4_valid'] else ('invalid' if p['gate4_valid'] is False else 'error')]+=1
            alts[p['alt_seed_deg']]+=1
        if len(prov)>1: mult.append((sub, len(prov)))
        cj=census.get(sub)
        if cj is None:
            new_subsets.append((sub, prov, 'NOT IN CENSUS FILE (?)')); continue
        cls=cj['class']
        if cls=='FEASIBLE_CERTIFIED' and cj.get('roots'):
            kr=np.array(cj['roots'][0]['coords'])
            ds=[float(np.linalg.norm(np.array(p['coords'])-kr)) for p in prov]
            hit=any(d<a.match_tol for d in ds)
            other=sum(1 for d in ds if d>=a.match_tol)
            known_subsets.append((sub, hit, other, min(ds)))
        else:
            new_subsets.append((sub, prov, cls))

    print("=== 1/2. coverage vs committed census ===")
    print(f"  subsets already FEASIBLE_CERTIFIED : {len(known_subsets)}")
    agree=sum(1 for _,h,_,_ in known_subsets if h)
    extra=sum(o for _,_,o,_ in known_subsets)
    print(f"    of which layer1 re-found the known root: {agree}/{len(known_subsets)}"
          f"   (independent-generator agreement check)")
    if extra: print(f"    ADDITIONAL distinct candidates on certified subsets: {extra} (possible extra roots)")
    miss=[(s,d) for s,h,_,d in known_subsets if not h]
    for s,d in miss: print(f"    NOTE {s}: known root NOT re-found (nearest {d:.1e}) — different root(s) proposed")
    print(f"  subsets currently UNRESOLVED_NO_CANDIDATE with layer1 candidates: {len(new_subsets)}")
    print(f"    -> these are the potential NEW certifications from this shard")

    print("\n=== 3. multiplicity ===")
    if mult:
        for s,n in sorted(mult): print(f"  {s}: {n} distinct candidates")
    else:
        print("  none (1 candidate per subset)")

    print("\n=== 4. stratum / altitude yield (per candidate) ===")
    print("  stratum:", dict(strat))
    print("  alt_seed_deg (top 8):", dict(alts.most_common(8)))

    print("\n=== 5. gate4 metadata (PROVISIONAL — authoritative tags on certified centers) ===")
    print(" ", dict(g4))

    print("\n=== new-coverage subsets (candidate gate4 metadata) ===")
    for sub,prov,cls in sorted(new_subsets):
        tags=','.join(('V' if p['gate4_valid'] else 'X' if p['gate4_valid'] is False else '?')
                      +'/'+p['stratum'][:3] for p in prov)
        print(f"  {str(sub):24s} [{cls[:22]:22s}] n={len(prov)} {tags}")
    print("\nREAD-ONLY diagnostic done. Nothing was certified; nothing was written.")

if __name__=='__main__':
    main()
