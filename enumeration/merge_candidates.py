"""
merge_candidates.py — merge N candidate files into a single census-facing union.

RULE (load-bearing): candidate files MAY carry per-candidate metadata (provenance dicts,
coords/candidate/x keys), but the census-facing union exposes each subset's candidates as RAW
6-float coordinate arrays. ALL candidates per subset are preserved and deduplicated by rounded
coords -- never collapsed to one -- so PARTIAL_CERTIFIED_ROOTS_K / disjoint-box lower bounds
remain honest. certify_2b_general + collapse_certified decide true root identity downstream.
"""
import sys, json, argparse

def extract_coords(c):
    """Accept raw [floats], or {'coords'|'candidate'|'x': [...]}; return [float]*6 or None."""
    if isinstance(c, dict):
        c = c.get('coords') or c.get('candidate') or c.get('x')
    if c is None: return None
    try:
        v=[float(x) for x in c]
        return v if len(v)==6 else None
    except Exception:
        return None

def key(coords, ndig=12):
    return tuple(round(x, ndig) for x in coords)

def merge(files, out_path, dedup_ndig=12):
    by_sub={}   # subset -> {'coords_keys':set, 'candidates':[[6 floats]], 'sources':[...]}
    for f in files:
        for line in open(f):
            line=line.strip()
            if not line: continue
            d=json.loads(line); sub=tuple(d['subset'])
            rec=by_sub.setdefault(sub, dict(coords_keys=set(), candidates=[], sources=[]))
            rec['sources'].append(dict(file=f, source=d.get('source'), tier=d.get('tier')))
            for c in d.get('candidates', []):
                coords=extract_coords(c)
                if coords is None: continue
                k=key(coords, dedup_ndig)
                if k in rec['coords_keys']: continue     # preserve-all-but-dedup
                rec['coords_keys'].add(k); rec['candidates'].append(coords)
    n_sub=0; n_cand=0; multi=0
    with open(out_path,'w') as o:
        for sub in sorted(by_sub):
            cands=by_sub[sub]['candidates']
            if not cands: continue
            # census-facing: candidates are RAW 6-float arrays (no metadata leakage)
            o.write(json.dumps(dict(subset=list(sub), candidates=cands,
                    candidate_sources=by_sub[sub]['sources']), sort_keys=True)+'\n')
            n_sub+=1; n_cand+=len(cands); multi += (len(cands)>1)
    print(f"union: {n_sub} subsets, {n_cand} candidates ({multi} subsets with >1 candidate)")
    return n_sub, n_cand, multi

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('files', nargs='+', help='candidate jsonl files to merge')
    ap.add_argument('--out', default='docs/candidates_union.jsonl')
    ap.add_argument('--dedup-ndig', type=int, default=12)
    a=ap.parse_args()
    merge(a.files, a.out, a.dedup_ndig)
    print("wrote", a.out)
