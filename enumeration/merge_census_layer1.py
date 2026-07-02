"""
merge_census_layer1.py — produce CENSUS_CHECKPOINT_LAYER1: the committed union baseline
(warm-start/transfer, 26 FEASIBLE) merged with the layer1 full-run scratch census
(836 FEASIBLE, per-root Gate-4 tagged). Server-only.

MERGE POLICY (upgrade-only lattice; a committed label is never downgraded):
    FEASIBLE_CERTIFIED  >  UNRESOLVED_CERT_FAILED  >  UNRESOLVED_NO_CANDIDATE
  - both FEASIBLE (the 26 overlap): merged roots = baseline roots + layer1 roots not
    within MATCH_TOL (1e-9) of any baseline root (cross-source dedupe justified by the
    measured 26/26 agreement at <1e-9); root_lower_bound/num_certified_roots updated;
    agree = {status:'multi_source_agree', sources:[baseline_source,'layer1']}.
  - one side higher in the lattice: take it verbatim (evidence bundle preserved).
  - candidate_source: overlap -> '<baseline_source>+layer1'; otherwise the winner's.
  - Gate-4 BACKFILL: any root lacking per-root 'gate4' (the union's 26 predate the
    per-root decision) is annotated with closure_tol=1e-7, asserted class-invariant.
    gate4_status.json thereby becomes a derived view, not a parallel authority.

HARD GUARDS: refuses protected dirs (census_union/census_dryrun/scratch inputs);
refuses overwrite without --force; HALTS on any would-be downgrade, any h outside
(0, pi/2) among merged certified roots, and re-verifies overlap agreement itself.

Usage:
  python3 enumeration/merge_census_layer1.py \
      --baseline docs/census_union/spherical_roots.jsonl \
      --layer1 docs/census_layer1_full_scratch/spherical_roots.jsonl \
      --outdir docs/census_checkpoint_layer1
"""
import os, sys, json, hashlib, datetime, argparse, math
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
import spherical_census_io as IO
from spherical_geo_check import gate4

GATE4_CLOSURE_TOL = 1e-7
MATCH_TOL = 1e-9
RANK = {'FEASIBLE_CERTIFIED':3, 'UNRESOLVED_CERT_FAILED':2, 'UNRESOLVED_NO_CANDIDATE':1}
PROTECTED = {'census_union','census_dryrun','census_layer1_full_scratch','census_layer1_shard0_scratch'}
CHECKPOINT = 'CENSUS_CHECKPOINT_LAYER1'

def _sha(path): return hashlib.sha256(open(path,'rb').read()).hexdigest()
def _load(path): return {tuple(json.loads(l)['subset']): json.loads(l) for l in open(path)}

def _backfill_gate4(rec):
    n=0
    before=(rec['class'], rec['num_certified_roots'], rec['root_lower_bound'])
    for root in rec['roots']:
        if 'gate4' in root: continue
        try:
            v,why=gate4(*[float(t) for t in root['coords']], closure_tol=GATE4_CLOSURE_TOL)
            root['gate4']={'valid':bool(v),'reason':str(why),'closure_tol':GATE4_CLOSURE_TOL,
                           'scope':'metadata_only; does not affect class','backfilled':True}
        except Exception as ex:
            root['gate4']={'valid':None,'reason':f'gate4 raised {type(ex).__name__}',
                           'closure_tol':GATE4_CLOSURE_TOL,
                           'scope':'metadata_only; does not affect class','backfilled':True}
        n+=1
    assert before==(rec['class'], rec['num_certified_roots'], rec['root_lower_bound'])
    return n

def merge(baseline_path, layer1_path, outdir, force=False):
    parts=set(os.path.normpath(os.path.abspath(outdir)).split(os.sep))
    if parts & PROTECTED:
        raise SystemExit(f'REFUSED: outdir targets protected directory {sorted(parts&PROTECTED)}')
    jsonl=os.path.join(outdir,'spherical_roots.jsonl')
    if os.path.exists(jsonl) and not force:
        raise SystemExit(f'REFUSED: {jsonl} exists; --force to overwrite')
    os.makedirs(outdir, exist_ok=True)
    B=_load(baseline_path); L=_load(layer1_path)
    assert set(B)==set(L), 'universe mismatch between baseline and layer1'
    t0=datetime.datetime.now(datetime.timezone.utc).isoformat()
    logp=os.path.join(outdir,'spherical_census.log'); log=IO.CensusLog(logp)
    log.log(f'{CHECKPOINT} merge: baseline={baseline_path} layer1={layer1_path}')
    log.log(f'baseline_sha256={_sha(baseline_path)} layer1_sha256={_sha(layer1_path)}')

    records=[]; n_overlap=0; n_extra_roots=0; n_backfilled=0; n_from_layer1=0; n_from_base=0
    F='FEASIBLE_CERTIFIED'
    for sub in sorted(B):
        b, l = B[sub], L[sub]
        rb, rl = RANK.get(b['class']), RANK.get(l['class'])
        if rb is None or rl is None:
            raise SystemExit(f'HALT: unexpected class on {sub}: {b["class"]} / {l["class"]}')
        if b['class']==F and l['class']==F:
            n_overlap+=1
            rec=json.loads(json.dumps(b))            # deep copy; baseline evidence preserved
            bpts=[np.array(r['coords']) for r in rec['roots']]
            # re-verify agreement (guard, independent of the scratch gate)
            lpts=[np.array(r['coords']) for r in l['roots']]
            for bp in bpts:
                if min(float(np.linalg.norm(bp-lp)) for lp in lpts) >= MATCH_TOL:
                    raise SystemExit(f'HALT: baseline root on {sub} NOT re-found by layer1')
            for r in l['roots']:                     # union in genuinely new roots
                p=np.array(r['coords'])
                if min(float(np.linalg.norm(p-bp)) for bp in bpts) >= MATCH_TOL:
                    rec['roots'].append(json.loads(json.dumps(r))); n_extra_roots+=1
            rec['num_certified_roots']=len(rec['roots'])
            rec['root_lower_bound']=max(rec['root_lower_bound'], len(rec['roots']))
            rec['candidate_source']=f"{b['candidate_source']}+layer1"
            rec['agree']={'status':'multi_source_agree',
                          'sources':[b['candidate_source'],'layer1'],
                          'notes':f'baseline roots independently re-found by layer1 (<{MATCH_TOL})'}
            rec['notes']=(rec.get('notes','') or '')+f'|{CHECKPOINT}:merged'
        elif rl>rb:
            rec=json.loads(json.dumps(l)); n_from_layer1+=1
            rec['notes']=(rec.get('notes','') or '')+f'|{CHECKPOINT}:from_layer1'
        else:
            rec=json.loads(json.dumps(b)); n_from_base+=1
            rec['notes']=(rec.get('notes','') or '')+f'|{CHECKPOINT}:from_baseline'
        n_backfilled+=_backfill_gate4(rec)
        records.append(rec)

    # merged-census invariants
    h_bad=[(tuple(r['subset']),round(float(rt['coords'][5]),4)) for r in records
           for rt in r['roots'] if not (0.0 < float(rt['coords'][5]) < math.pi/2)]
    if h_bad: raise SystemExit(f'HALT: merged certified roots outside h-domain: {h_bad[:5]}')
    mrec={tuple(r['subset']):r for r in records}
    for sub in B:
        if RANK[mrec[sub]['class']] < RANK[B[sub]['class']]:
            raise SystemExit(f'HALT: downgrade on {sub}')
        if RANK[mrec[sub]['class']] < RANK[L[sub]['class']]:
            raise SystemExit(f'HALT: layer1 result lost on {sub}')
    miss=[tuple(r['subset']) for r in records for rt in r['roots'] if 'gate4' not in rt]
    if miss: raise SystemExit(f'HALT: roots without gate4 after backfill: {miss[:5]}')

    csvp=os.path.join(outdir,'spherical_census.csv')
    manifest=os.path.join(outdir,'spherical_census_manifest.json')
    IO.write_jsonl(records, jsonl); IO.derive_csv(jsonl, csvp)
    t1=datetime.datetime.now(datetime.timezone.utc).isoformat()
    log.log(f'done: {len(records)} records; overlap={n_overlap} extra_roots={n_extra_roots} '
            f'backfilled_gate4={n_backfilled}')
    log.close()
    man=IO.write_manifest(manifest, jsonl, csvp, logp, commit=CHECKPOINT,
                          prereg='preregistration.md', n_subsets=len(records),
                          subset_universe_sha256='(see inputs)', command=' '.join(sys.argv),
                          timestamp_start=t0, timestamp_end=t1)
    m=json.load(open(manifest))
    m.update(checkpoint=CHECKPOINT,
             merge_policy='upgrade-only lattice; cross-source root union at 1e-9; '
                          'gate4 backfill closure_tol=1e-7 (class-invariant, asserted)',
             baseline_file=os.path.abspath(baseline_path), baseline_sha256=_sha(baseline_path),
             layer1_file=os.path.abspath(layer1_path), layer1_sha256=_sha(layer1_path),
             n_overlap_multisource=n_overlap, n_extra_roots_on_overlap=n_extra_roots,
             n_gate4_backfilled=n_backfilled,
             gate4_per_root=True, gate4_closure_tol=GATE4_CLOSURE_TOL)
    json.dump(m, open(manifest,'w'), indent=2, sort_keys=True)
    IO.write_sha256sums(os.path.join(outdir,'SHA256SUMS'), [jsonl,csvp,manifest,logp])

    counts=m['status_counts']
    troots=sum(len(r['roots']) for r in records)
    g4v=sum(1 for r in records for rt in r['roots'] if rt['gate4'].get('valid') is True)
    g4x=sum(1 for r in records for rt in r['roots'] if rt['gate4'].get('valid') is False)
    multi=sum(1 for r in records if r['num_certified_roots']>1)
    print(f'=== {CHECKPOINT} ===')
    for k,v in sorted(counts.items()):
        if v: print(f'  {k:34s} {v}')
    print(f'  certified roots total              {troots}')
    print(f'  gate4 per-root                     valid={g4v} rejected={g4x}')
    print(f'  multi-root subsets                 {multi}')
    print(f'  multi-source agreement subsets     {n_overlap} (+{n_extra_roots} new roots on them)')
    print(f'  gate4 backfilled onto baseline     {n_backfilled} roots')
    print(f'  invariants: no downgrade, no layer1 loss, all roots gate4-tagged, all h in (0,pi/2)')
    print('outputs ->', outdir)
    return records, m

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--baseline', default=os.path.join(_root,'docs','census_union','spherical_roots.jsonl'))
    ap.add_argument('--layer1',   default=os.path.join(_root,'docs','census_layer1_full_scratch','spherical_roots.jsonl'))
    ap.add_argument('--outdir',   default=os.path.join(_root,'docs','census_checkpoint_layer1'))
    ap.add_argument('--force', action='store_true')
    a=ap.parse_args()
    merge(a.baseline, a.layer1, a.outdir, force=a.force)
