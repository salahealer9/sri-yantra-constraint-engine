"""
layer1_candidates.py — LAYER-1 domain-wide candidate generator for the spherical census.

DESIGN (Option A, locked 2026-07-02): search the FULL declared constraint-root domain,
including the containment-violating region (b+c > r and/or d+e > r) that the mapper's
_candidates excludes by construction. Gate-4 is METADATA ONLY — never a search filter,
never a label. Two-layer discipline unchanged:

    layer1_candidates proposes  ->  certify_2b_general decides  ->  census_io records
    Gate-4 tags certified roots as GEOM_VALID_GATE4 / GEOM_REJECTED_GATE4 (reporting view)

WHY NOT stage1b_landscape.newton (L.newton): it is a 5-variable fixed-altitude solver.
On a 6-constraint census subset its Jacobian is 6x5 and np.linalg.solve raises
LinAlgError on EVERY step, so it can only "converge" when seeded already at a root
(the r<tol early-return). Verified empirically 2026-07-02 (test_lnewton_shape.py):
seed=exact root -> ok=True without ever solving; seed=root*1.001 -> ok=False,
solve_failure; 20 random seeds at the exact altitude -> 0 converged, 20 solve failures.
This fully explains the historical `find_seed -> None` results and retires the mapper
as a census candidate source (it remains a Stage-3 instrument for 5-subsets).
Polishing here uses certify_2b_general._real_newton: 6x6, h FREE (seed altitude is a
starting point only; Newton moves h), the same Newton the certifier itself trusts.

NO DISPLACEMENT CAP IN DISCOVERY (deliberate, documented): warm-start capped
displacement to keep candidates local to known roots. A domain-wide random seed is not
"near" anything; the candidate we emit is the CONVERGED point, and the certifier
re-polishes it under its own untouched MAX_POLISH=2e-2 (which then moves ~0). The
certifier's cap is a correctness guarantee and is NOT loosened; the discovery
displacement is recorded as provenance.

DECLARED CANDIDATE FILTERS (efficiency/domain hygiene, NOT verdicts — the certifier
alone decides feasibility):
    residual <= ACCEPT_RESID (1e-8), all coords finite,
    r = pi/2 - h >= R_MIN_FLOOR (5e-3 rad)   [rejects the trivial full-collapse point
                                              b..g->0, h->pi/2; genuine census roots
                                              have r >= 0.22; the mapper's pole
                                              predicate is r ~ 1.75e-2],
    1e-8 <= b,c,d,e,g < pi/2,  c < r,  d < r  [chain constructibility: acos args].
NO ordering/containment filter of any kind (b+c vs r, d+e vs r, g vs c all free).

SEED STRATA (recorded per candidate; deterministic blake2b(GLOBAL_SEED|subset|alt|stratum)):
    box     — uniform over the Rao Table-1 proportion box widened 50% (mapper's SBOX),
              WITHOUT the mapper's g<c / b+c<R / d+e<R guards;
    logwide — log-uniform over (1e-3 R, 0.97 R)^5, unfiltered;
    neardeg — symmetric near-collapse locus (thin-basin coverage), unfiltered;
    viol    — TARGETED containment-violating region: c,d in (0.45,0.93)R and
              b+c > R and/or d+e > R (mode 0=both, 1=bc only, 2=de only), the region
              the mapper structurally never seeds and where the benchmark-family
              certified roots live.

Validated locally 2026-07-02 (proto_layer1.py, engine de64edfa4979): at k=6 per
stratum per altitude, the generator reaches BOTH the Gate-4-rejected benchmark root
(1,2,3,4,6,7) and the Gate-4-valid non-benchmark root (1,2,3,5,10,19) to <1e-9, and
the declared filters reduce the converged set to exactly the known certified root in
each case. Deterministic seeding means the server reproduces those hits seed-for-seed.
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
import certify_2b_general as GEN            # _real_newton (6x6, h free), _in_bsphere, ENGINE_HASH
import spherical_geo_check as GC            # gate4 — METADATA ONLY

PI2 = math.pi/2; DEG = math.pi/180
GLOBAL_SEED   = 20260702
ACCEPT_RESID  = 1e-8
R_MIN_FLOOR   = 5e-3        # radians; rejects the trivial full-collapse limit point
COORD_FLOOR   = 1e-8
COND_MAX      = 1e8         # DECLARED conditioning filter (added 2026-07-02 after the
                            # stride-30 refusal diagnostic): certification has succeeded
                            # ONLY at cond(J)<1e6 (26/26 certified; 0/294 at cond>=1e6
                            # across head+spread shards); 1e8 keeps a 100x safety margin.
                            # Filtered candidates are NOT discarded: they are written to
                            # a *_highcond.jsonl sidecar (near-singular population, an
                            # auditable finding about the varieties, not a verdict).
NEWTON_ITERS  = 40
GATE4_CLOSURE_TOL = 1e-7    # machine-solved figures (mapper's registered value)
ALTS_DEFAULT  = (48,40,32,56,24,64,18,72,36,28,44,52,20,68,16,76,80,84,88)  # mapper's registered grid
STRATA        = ('box','logwide','neardeg','viol')

def _spherical_box():
    """Mapper's registered seeding box (Table-1 arc/r proportions widened 50%),
    reproduced verbatim — the guards are what we drop, not the box."""
    rows=[]
    for _cons,(b,c,d,e,g,h) in RAO.TABLE1:
        r=PI2-h; rows.append([b/r,c/r,d/r,e/r,g/r])
    T=np.array(rows); lo,hi=T.min(0),T.max(0); rg=hi-lo
    return np.maximum(lo-0.5*rg, 1e-3), hi+0.5*rg
SBOX_LO, SBOX_HI = _spherical_box()

def _stable_rng(sub, hd, stratum):
    h=hashlib.blake2b(f'{GLOBAL_SEED}|{tuple(sub)}|{hd}|{stratum}'.encode(), digest_size=8)
    return np.random.default_rng(int.from_bytes(h.digest(),'big'))

def _sample(stratum, R, rng):
    """One 5-vector (b,c,d,e,g) seed. NO ordering/containment filters anywhere."""
    if stratum=='box':
        return rng.uniform(SBOX_LO, SBOX_HI)*R
    if stratum=='logwide':
        return np.exp(rng.uniform(np.log(1e-3*R), np.log(0.97*R), 5))
    if stratum=='neardeg':
        base=rng.uniform(0.4*R, 0.97*R)
        return np.array([rng.uniform(1e-3,0.03)*R, base, base,
                         rng.uniform(1e-3,0.03)*R, base*rng.uniform(0.95,0.999)])
    if stratum=='viol':
        mode=int(rng.integers(0,3))          # 0: both violated, 1: b+c>R only, 2: d+e>R only
        c=rng.uniform(0.45,0.93)*R; d=rng.uniform(0.45,0.93)*R
        b=(R-c)+rng.uniform(0.02,0.30)*R if mode in (0,1) else rng.uniform(0.05,0.9)*(R-c)
        e=(R-d)+rng.uniform(0.02,0.30)*R if mode in (0,2) else rng.uniform(0.05,0.9)*(R-d)
        g=rng.uniform(0.02,0.95)*R
        return np.array([b,c,d,e,g])
    raise ValueError(f'unknown stratum {stratum}')

def _passes_declared_filters(x):
    """Domain/degeneracy hygiene on the CONVERGED point. Not a feasibility verdict."""
    if not np.all(np.isfinite(x)): return False
    r = PI2 - x[5]
    if r < R_MIN_FLOOR: return False
    if not np.all(np.array(x[:5]) >= COORD_FLOOR): return False
    if not np.all(np.array(x[:5]) <  PI2): return False
    if x[1] >= r or x[2] >= r: return False          # c<r, d<r (acos constructibility)
    return True

def _gate4_metadata(x):
    """Gate-4 status of a candidate — recorded, never filtered on. Provisional: the
    authoritative Layer-2 tag is computed census-side on CERTIFIED centers."""
    try:
        v, why = GC.gate4(*[float(t) for t in x[:5]], float(x[5]), closure_tol=GATE4_CLOSURE_TOL)
        return bool(v), str(why)
    except Exception as ex:
        return None, f'gate4 raised {type(ex).__name__}'

def _cond_J(x, sub):
    """cond of the 6x6 forward-difference Jacobian at x (same dd as the certifier's
    Newton). Numerically noisy above ~1e8 — used only as a coarse declared filter."""
    x=np.array(x,float); dd=1e-7
    try: F0=np.array([RAO.constraints(*x)[k] for k in sub],float)
    except Exception: return None
    J=np.zeros((6,6))
    for j in range(6):
        xp=x.copy(); xp[j]+=dd
        try: Fp=np.array([RAO.constraints(*xp)[k] for k in sub],float)
        except Exception: return None
        J[:,j]=(Fp-F0)/dd
    s=np.linalg.svd(J, compute_uv=False)
    return float(s[0]/s[-1]) if s[-1]>0 else float('inf')

def process_subset(args):
    """Worker: pure deterministic function of (subset, k, alts). Proposes only."""
    sub, k, alts = args
    sub=tuple(sorted(int(s) for s in sub))
    out=[]; seen=set()
    n_seeds=0; n_conv=0
    for hd in alts:
        R=PI2-hd*DEG
        for stratum in STRATA:
            rng=_stable_rng(sub, hd, stratum)
            for i in range(k):
                x5=_sample(stratum, R, rng); n_seeds+=1
                seed=[float(v) for v in x5]+[hd*DEG]
                ref=GEN._real_newton(seed, sub, iters=NEWTON_ITERS)
                if ref is None: continue
                x, resid = ref
                if resid > ACCEPT_RESID: continue
                n_conv+=1
                if not _passes_declared_filters(x): continue
                key=tuple(round(float(v),9) for v in x)
                if key in seen: continue
                seen.add(key)
                disp=math.sqrt(sum((float(x[j])-seed[j])**2 for j in range(6)))
                g4v, g4why = _gate4_metadata(x)
                cj = _cond_J(x, sub)
                out.append(dict(
                    coords=[float(v) for v in x],
                    source='layer1_domainwide',
                    stratum=stratum, alt_seed_deg=float(hd), seed_index=int(i),
                    seed=[round(v,12) for v in seed],
                    residual=float(resid), displacement=float(disp),
                    cond_J=(float(cj) if cj is not None else None),
                    in_bsphere=bool(GEN._in_bsphere(x)),
                    gate4_valid=g4v, gate4_reason=g4why))
    return sub, out, n_seeds, n_conv

def run(universe_path, out_path, k=6, alts=ALTS_DEFAULT, workers=1,
        subsets=None, shard=None):
    U=json.load(open(universe_path))
    allsubs=[tuple(s) for s in U['subsets']]
    if subsets:
        want=set(tuple(sorted(s)) for s in subsets)
        subs=[s for s in allsubs if tuple(sorted(s)) in want]
        missing=want-{tuple(sorted(s)) for s in subs}
        if missing: raise SystemExit(f'subsets not in universe: {sorted(missing)}')
    elif shard:
        a,b=shard; subs=allsubs[a:b]
    else:
        subs=allsubs
    tasks=list(zip(subs, repeat(int(k)), repeat(tuple(alts))))
    if workers and workers>1:
        import multiprocessing as mp
        with mp.get_context('spawn').Pool(workers) as pool:
            results=pool.map(process_subset, tasks, chunksize=4)
    else:
        results=[process_subset(t) for t in tasks]
    # PARENT-ONLY WRITE, stable sorted order. cond<=COND_MAX -> main file (certifier-bound);
    # cond>COND_MAX (or cond undefined) -> *_highcond.jsonl SIDECAR (recorded, not certified:
    # near-singular population; zero certifications ever observed at cond>=1e6).
    by_sub={s:(c,ns,nc) for s,c,ns,nc in results}
    side_path=out_path.replace('.jsonl','_highcond.jsonl')
    n_with=0; n_cand=0; n_side=0; n_side_sub=0; t_seeds=0; t_conv=0
    with open(out_path,'w') as f, open(side_path,'w') as fs:
        for sub in sorted(by_sub):
            cands,ns,nc=by_sub[sub]; t_seeds+=ns; t_conv+=nc
            keep=[c for c in cands if c['cond_J'] is not None and c['cond_J']<=COND_MAX]
            side=[c for c in cands if c not in keep]
            if keep:
                f.write(json.dumps(dict(subset=list(sub),
                        candidates=[c['coords'] for c in keep], provenance=keep),
                        sort_keys=True)+'\n')
                n_with+=1; n_cand+=len(keep)
            if side:
                fs.write(json.dumps(dict(subset=list(sub),
                        candidates=[c['coords'] for c in side], provenance=side),
                        sort_keys=True)+'\n')
                n_side_sub+=1; n_side+=len(side)
    meta=dict(schema_version='candidates_layer1_v1',
              design='Layer-1 domain-wide (Option A): full declared domain incl. '
                     'containment-violating region; Gate-4 metadata only, never a filter',
              declared_region=dict(coord_floor=COORD_FLOOR, coord_ceiling='pi/2',
                     r_min_floor=R_MIN_FLOOR, constructibility='c<r and d<r',
                     cond_max=COND_MAX,
                     cond_max_justification='stride-30 refusal diagnostic 2026-07-02: '
                         '0/294 certifications at cond>=1e6 (head+spread); certified only '
                         'at cond<1e6; 1e8 cutoff = 100x margin; filtered candidates '
                         'preserved in *_highcond.jsonl sidecar',
                     ordering_containment_filters='NONE (b+c vs r, d+e vs r, g vs c all free)'),
              strata=list(STRATA), alt_grid_deg=list(alts), k_per_stratum_per_alt=int(k),
              newton='certify_2b_general._real_newton (6x6, h free); L.newton excluded '
                     '(5-var fixed-h; 6x5 solve structurally fails on 6-subsets)',
              displacement_cap='none in discovery (recorded as provenance); certifier '
                               'MAX_POLISH=2e-2 untouched and authoritative',
              accept_resid=ACCEPT_RESID, gate4_closure_tol=GATE4_CLOSURE_TOL,
              global_seed=GLOBAL_SEED,
              seed_policy='blake2b(global_seed|subset|alt_deg|stratum) -> per-cell RNG',
              universe_sha256=U.get('subsets_sha256'), engine_hash=GEN.ENGINE_HASH,
              n_subsets_processed=len(subs), n_subsets_with_candidates=n_with,
              n_candidates=n_cand, n_seeds_tried=t_seeds, n_newton_converged=t_conv,
              n_highcond_candidates=n_side, n_highcond_subsets=n_side_sub,
              highcond_sidecar=os.path.basename(side_path),
              highcond_sha256=hashlib.sha256(open(side_path,'rb').read()).hexdigest(),
              command=' '.join(sys.argv),
              candidates_sha256=hashlib.sha256(open(out_path,'rb').read()).hexdigest())
    json.dump(meta, open(out_path.replace('.jsonl','_meta.json'),'w'), indent=2, sort_keys=True)
    return n_with, n_cand, meta

def _parse_subsets(s):
    return [tuple(int(x) for x in t.split('-')) for t in s.split(',') if t.strip()]

def _parse_shard(s):
    a,b=s.split(':'); return (int(a), int(b))

if __name__=='__main__':
    ap=argparse.ArgumentParser(description='Layer-1 domain-wide candidate generator (proposes only)')
    ap.add_argument('--universe', default='docs/subset_universe.json')
    ap.add_argument('--out', default='docs/candidates_layer1.jsonl')
    ap.add_argument('--k', type=int, default=6, help='seeds per stratum per altitude (default 6)')
    ap.add_argument('--alts', default='', help='comma-separated altitude degrees (default: registered 19-altitude grid)')
    ap.add_argument('--workers', type=int, default=1)
    ap.add_argument('--subsets', default='', help="e.g. '1-2-3-4-6-7,1-2-3-5-10-19' (default: universe/shard)")
    ap.add_argument('--shard', default='', help="slice of the sorted universe, e.g. '0:100'")
    a=ap.parse_args()
    alts=tuple(float(x) for x in a.alts.split(',')) if a.alts else ALTS_DEFAULT
    subs=_parse_subsets(a.subsets) if a.subsets else None
    shard=_parse_shard(a.shard) if a.shard else None
    nw,nc,meta=run(a.universe, a.out, k=a.k, alts=alts, workers=a.workers,
                   subsets=subs, shard=shard)
    print(f"layer1: {meta['n_subsets_processed']} subsets, {meta['n_seeds_tried']} seeds, "
          f"{meta['n_newton_converged']} converged -> {nc} candidates across {nw} subsets"
          f"  (+{meta['n_highcond_candidates']} high-cond to sidecar, "
          f"{meta['n_highcond_subsets']} subsets)")
    print(f"candidates_sha256={meta['candidates_sha256'][:16]}  (propose-only; certifier decides; Gate-4 is metadata)")
    print("wrote", a.out)
