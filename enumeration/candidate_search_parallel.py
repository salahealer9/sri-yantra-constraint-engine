"""
candidate_search_parallel.py — parallel transfer/direct candidate discovery, same DISCIPLINE as
candidate_search_warmstart.py (proposes only; certify_2b_general decides; never writes
FEASIBLE_CERTIFIED). Adds --workers with:
  * deterministic per-subset RNG:  seed = blake2b(global_seed, subset, perturb_index, seed_id)
    -> perturbations are a pure function of (subset, indices), independent of worker/order.
  * parent-only JSONL writing: workers return records; parent SORTS by subset and writes.
  * equivalence: serial --perturb 0 == parallel --perturb 0 (no RNG at perturb 0; identical seeds).
  * provenance meta: workers, global_seed, seed policy, universe hash, command.
"""
import sys, os, json, math, hashlib, argparse
import numpy as np
from itertools import repeat
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
import certify_2b_general as GEN

BENCH=(1,2,3,4,6,7)
BENCH_ROOT=[0.6246238466927992,0.7044304165359816,0.7482768099360514,0.6307397242292889,0.3136386632298885,0.39527668335411803]
ACCEPT_RESID=1e-8; MAX_DISP=2e-2; GLOBAL_SEED=20260701

def seed_pool():
    pool=[('benchmark', list(BENCH_ROOT))]
    for name,vals in RAO.TABLE1: pool.append((f'table1{tuple(sorted(name))}', list(vals)))
    return pool
POOL=seed_pool()
T1_BY_LABEL={tuple(sorted(n)): list(v) for n,v in RAO.TABLE1}

def _stable_rng(subset, perturb_index, seed_id):
    """Deterministic per-(subset,perturb_index,seed_id) RNG -- order/worker independent."""
    h=hashlib.blake2b(f'{GLOBAL_SEED}|{tuple(subset)}|{perturb_index}|{seed_id}'.encode(),digest_size=8)
    return np.random.default_rng(int.from_bytes(h.digest(),'big'))

def newton_candidate(subset, seed):
    ref=GEN._real_newton(seed, tuple(sorted(subset)), iters=30)
    if ref is None: return None
    x,resid=ref
    if not np.all(np.isfinite(x)) or resid>ACCEPT_RESID: return None
    disp=math.sqrt(sum((x[i]-seed[i])**2 for i in range(6)))
    if disp>MAX_DISP: return None
    return [float(v) for v in x], float(resid), float(disp)

def process_subset(args):
    """Worker: pure function of (subset, tier, perturb). Returns (subset, [candidate dicts])."""
    sub, tier, perturb = args
    sub=tuple(sub); seeds=[]
    if sub in T1_BY_LABEL: seeds.append(('direct_table1', T1_BY_LABEL[sub], -1, 'direct'))
    if sub==BENCH:         seeds.append(('direct_benchmark', list(BENCH_ROOT), -1, 'direct'))
    if tier=='transfer':
        for sid,(origin,coords) in enumerate(POOL):
            seeds.append((f'transfer:{origin}', coords, -1, origin))
            for pi in range(perturb):
                rng=_stable_rng(sub, pi, sid)             # deterministic, order-independent
                seeds.append((f'transfer_perturb:{origin}',
                              [coords[i]+rng.normal(0,0.01) for i in range(6)], pi, origin))
    out=[]
    for origin,seed,pi,sid in seeds:
        res=newton_candidate(sub, seed)
        if res:
            coords,resid,disp=res
            key=tuple(round(c,9) for c in coords)
            if any(tuple(round(c,9) for c in o['coords'])==key for o in out): continue  # dedupe
            out.append(dict(coords=coords, source='warmstart_parallel', seed_origin=origin,
                            residual=resid, displacement=disp))
    return sub, out

def run(universe_path, out_path, tier='transfer', perturb=0, workers=1):
    U=json.load(open(universe_path)); subsets=[tuple(s) for s in U['subsets']]
    universe_sha=U['subsets_sha256']
    tasks=list(zip(subsets, repeat(tier), repeat(perturb)))
    if workers and workers>1:
        import multiprocessing as mp
        with mp.get_context('spawn').Pool(workers) as pool:
            results=pool.map(process_subset, tasks, chunksize=16)
    else:
        results=[process_subset(t) for t in tasks]
    # PARENT-ONLY WRITE, stable sorted order
    by_sub={s:c for s,c in results}
    n_sub=0; n_cand=0
    with open(out_path,'w') as f:
        for sub in sorted(by_sub):
            cands=by_sub[sub]
            if cands:
                f.write(json.dumps(dict(subset=list(sub),
                        candidates=[c['coords'] for c in cands], provenance=cands),
                        sort_keys=True)+'\n')
                n_sub+=1; n_cand+=len(cands)
    meta=dict(schema_version='candidates_parallel_v1', tier=tier, perturb=perturb,
              workers=workers, global_seed=GLOBAL_SEED,
              seed_policy='blake2b(global_seed|subset|perturb_index|seed_id)',
              universe_sha256=universe_sha, accept_resid=ACCEPT_RESID, max_disp=MAX_DISP,
              command=' '.join(sys.argv),
              n_subsets_with_candidates=n_sub, n_candidates=n_cand,
              candidates_sha256=hashlib.sha256(open(out_path,'rb').read()).hexdigest())
    json.dump(meta, open(out_path.replace('.jsonl','_meta.json'),'w'), indent=2, sort_keys=True)
    return n_sub, n_cand, meta

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--universe', default='docs/subset_universe.json')
    ap.add_argument('--out', default='docs/candidates_parallel.jsonl')
    ap.add_argument('--tier', default='transfer', choices=['direct','transfer'])
    ap.add_argument('--perturb', type=int, default=0)
    ap.add_argument('--workers', type=int, default=1)
    a=ap.parse_args()
    ns,nc,meta=run(a.universe,a.out,a.tier,a.perturb,a.workers)
    print(f"tier={a.tier} perturb={a.perturb} workers={a.workers} -> {nc} candidates across {ns} subsets")
    print(f"candidates_sha256={meta['candidates_sha256'][:16]}  (propose-only; certifier decides)")
    print("wrote", a.out)
