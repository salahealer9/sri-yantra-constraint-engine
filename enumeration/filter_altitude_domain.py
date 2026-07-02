"""
filter_altitude_domain.py — DECLARED domain post-filter (registration enforcement).

The layer1 generator (v1/v2) enforced r = pi/2 - h >= 5e-3 (bounding h above) but
omitted the LOWER altitude bound. The preregistration's valid domain is the seed box
"intersected with the valid domain (positivity; c,d < r; chain-defined arc arguments
in range)" — h is a basic variable, so h > 0 is REGISTERED. Newton with h free can
converge to constraint-roots at h <= 0 (r >= pi/2: super-hemispheric caps, down to
h ~ -31 observed): real solutions of the trig system, OUTSIDE the registered Meru
domain. This script enforces the registered bound on an existing candidates file:

    KEEP   : COORD_FLOOR (1e-8) <= h            [r <= pi/2 - 1e-8]
    REMOVE : h < COORD_FLOOR  -> *_outofdomain.jsonl AUDIT SIDECAR (preserved, never
             discarded; a population of out-of-registered-domain constraint roots)

Deterministic, order-preserving, provenance-complete (meta with input/output shas).
Caveat recorded in meta: removing a candidate cannot create wrong entries but the
generator's round-9 dedupe means a v3 regeneration could in principle surface a
different first-finder provenance for an identical root (coords unaffected).
"""
import json, hashlib, argparse, os, math

COORD_FLOOR=1e-8; PI2=math.pi/2

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--candidates', required=True)
    ap.add_argument('--out', default='', help='default: <candidates> with _domainok suffix')
    a=ap.parse_args()
    out=a.out or a.candidates.replace('.jsonl','_domainok.jsonl')
    side=out.replace('.jsonl','')+'_removed_outofdomain.jsonl'
    n_keep=n_rm=0; s_keep=s_rm=0; rm_bsphere={'in':0,'out':0,'?':0}; h_rm=[]
    with open(out,'w') as fo, open(side,'w') as fs:
        for line in open(a.candidates):
            j=json.loads(line)
            keep=[]; rm=[]
            for p in j['provenance']:
                (keep if p['coords'][5]>=COORD_FLOOR else rm).append(p)
            if keep:
                fo.write(json.dumps(dict(subset=j['subset'],
                        candidates=[p['coords'] for p in keep], provenance=keep),
                        sort_keys=True)+'\n'); s_keep+=1; n_keep+=len(keep)
            if rm:
                fs.write(json.dumps(dict(subset=j['subset'],
                        candidates=[p['coords'] for p in rm], provenance=rm),
                        sort_keys=True)+'\n'); s_rm+=1; n_rm+=len(rm)
                for p in rm:
                    h_rm.append(p['coords'][5])
                    k='in' if p.get('in_bsphere') is True else 'out' if p.get('in_bsphere') is False else '?'
                    rm_bsphere[k]+=1
    meta=dict(schema_version='layer1_domain_filter_v1',
              criterion=f'keep h >= {COORD_FLOOR} (registered positivity of basic variable h; '
                        f'r <= pi/2; upper bound r >= 5e-3 already enforced upstream)',
              input=os.path.basename(a.candidates),
              input_sha256=hashlib.sha256(open(a.candidates,'rb').read()).hexdigest(),
              output_sha256=hashlib.sha256(open(out,'rb').read()).hexdigest(),
              removed_sha256=hashlib.sha256(open(side,'rb').read()).hexdigest(),
              n_kept=n_keep, n_removed=n_rm, subsets_kept=s_keep, subsets_with_removed=s_rm,
              removed_h_min=(min(h_rm) if h_rm else None), removed_h_max=(max(h_rm) if h_rm else None),
              removed_in_bsphere_crosstab=rm_bsphere,
              dedupe_caveat='round-9 dedupe in the generator means a v3 regeneration could '
                            'surface different first-finder provenance for identical roots')
    json.dump(meta, open(out.replace('.jsonl','_filter_meta.json'),'w'), indent=2, sort_keys=True)
    print(f"kept {n_keep} candidates ({s_keep} subsets) -> {out}")
    print(f"removed {n_rm} out-of-domain ({s_rm} subsets, h in [{meta['removed_h_min']}, {meta['removed_h_max']}]) -> {side}")
    print(f"removed in_bsphere cross-tab: {rm_bsphere}   (out = certifier's own box already excluded them)")

if __name__=='__main__':
    main()
