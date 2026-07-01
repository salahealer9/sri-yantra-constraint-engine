"""
candidate_search_warmstart.py — Gap 1, cheapest discovery pass: warm-start / seed-transfer.

DISCIPLINE (load-bearing):
  * candidate search PROPOSES; certify_2b_general DECIDES. This script NEVER certifies and NEVER
    writes FEASIBLE_CERTIFIED. It only emits numerical candidates for the certifier to judge.
  * every candidate records provenance: subset, source, seed_origin, seed, residual, displacement.
  * LOCAL polish only (same _real_newton the certifier uses), capped displacement; no global wander.

Seed pool for the 6-var spherical 3044 universe (the only real 6-var material we have):
  * the benchmark root of {1,2,3,4,6,7}
  * Rao's Table 1 configurations (8 real spherical figures; 7 sit at/near roots of their labels)
Tiers:
  direct   : Table 1 config -> its labeled subset; benchmark root -> {1,2,3,4,6,7}
  transfer : for each subset, multistart Newton seeded by {benchmark, Table 1 configs} (+perturb)
Output: candidates.jsonl  (one line per subset that got >=1 in-domain converged candidate)
"""
import sys, os, json, math, hashlib, argparse
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
import certify_2b_general as GEN     # reuse the SAME numeric Newton the certifier uses

BENCH=(1,2,3,4,6,7)
BENCH_ROOT=[0.6246238466927992,0.7044304165359816,0.7482768099360514,0.6307397242292889,0.3136386632298885,0.39527668335411803]
ACCEPT_RESID=1e-8      # accept a Newton-converged point as a candidate below this residual
MAX_DISP=2e-2          # displacement cap (matches certifier's MAX_POLISH); reject far wanders

def seed_pool():
    """(origin_tag, coords) real 6-var seeds."""
    pool=[('benchmark', list(BENCH_ROOT))]
    for name,vals in RAO.TABLE1:
        pool.append((f'table1{tuple(sorted(name))}', list(vals)))
    return pool

def newton_candidate(subset, seed):
    """Local Newton (certifier's own _real_newton) on F_subset from seed. Returns (coords,resid,disp)
    if it converges in-domain within the displacement cap, else None. PROPOSE only."""
    ref = GEN._real_newton(seed, tuple(sorted(subset)), iters=30)
    if ref is None: return None
    x, resid = ref
    if not np.all(np.isfinite(x)) or resid > ACCEPT_RESID: return None
    disp = math.sqrt(sum((x[i]-seed[i])**2 for i in range(6)))
    if disp > MAX_DISP: return None       # far wander -> not a warm-start hit, reject
    return [float(v) for v in x], float(resid), float(disp)

def search(universe_path, out_path, tier='direct', perturb=0):
    U=json.load(open(universe_path)); subsets=[tuple(s) for s in U['subsets']]
    universe_sha=U['subsets_sha256']
    pool=seed_pool()
    # label -> Table1 coords, for the DIRECT tier
    t1_by_label={tuple(sorted(n)): list(v) for n,v in RAO.TABLE1}
    rng=np.random.default_rng(20260701)
    out={}   # subset -> list of candidate dicts (deduped)
    def add(sub, coords, source, origin, resid, disp):
        key=tuple(round(c,9) for c in coords)
        lst=out.setdefault(sub, [])
        for c in lst:
            if max(abs(a-b) for a,b in zip(c['coords'],coords))<1e-7: return  # dedupe
        lst.append(dict(coords=coords, source=source, seed_origin=origin,
                        residual=resid, displacement=disp))
    for sub in subsets:
        seeds=[]
        # DIRECT: Table1 config for this exact subset, and benchmark for its own subset
        if sub in t1_by_label: seeds.append((f'direct_table1', t1_by_label[sub]))
        if sub==BENCH: seeds.append(('direct_benchmark', list(BENCH_ROOT)))
        # TRANSFER: multistart from the whole pool (+ optional perturbations)
        if tier=='transfer':
            for origin,coords in pool:
                seeds.append((f'transfer:{origin}', coords))
                for _ in range(perturb):
                    seeds.append((f'transfer_perturb:{origin}',
                                  [coords[i]+rng.normal(0,0.01) for i in range(6)]))
        for origin,seed in seeds:
            res=newton_candidate(sub, seed)
            if res:
                coords,resid,disp=res
                add(sub, coords, 'warmstart', origin, resid, disp)
    # write candidates.jsonl
    n_sub=0; n_cand=0
    with open(out_path,'w') as f:
        for sub in subsets:
            if sub in out and out[sub]:
                f.write(json.dumps(dict(subset=list(sub),
                        candidates=[c['coords'] for c in out[sub]],
                        provenance=out[sub]))+'\n')
                n_sub+=1; n_cand+=len(out[sub])
    meta=dict(schema_version='candidates_warmstart_v1', tier=tier, perturb=perturb,
              universe_sha256=universe_sha, accept_resid=ACCEPT_RESID, max_disp=MAX_DISP,
              n_subsets_with_candidates=n_sub, n_candidates=n_cand,
              seed_pool=[o for o,_ in pool],
              candidates_sha256=hashlib.sha256(open(out_path,'rb').read()).hexdigest())
    json.dump(meta, open(out_path.replace('.jsonl','_meta.json'),'w'), indent=2)
    return n_sub, n_cand, meta

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--universe', default='docs/subset_universe.json')
    ap.add_argument('--out', default='census_dryrun/candidates_warmstart.jsonl')
    ap.add_argument('--tier', default='direct', choices=['direct','transfer'])
    ap.add_argument('--perturb', type=int, default=0)
    a=ap.parse_args()
    ns,nc,meta=search(a.universe, a.out, a.tier, a.perturb)
    print(f"tier={a.tier} -> {nc} candidates across {ns} subsets (propose-only; certifier decides)")
    print(f"candidates_sha256={meta['candidates_sha256'][:16]}")
    print("wrote", a.out)


