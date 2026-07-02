"""
smoke_layer1_gate.py — SMOKE GATE for layer1_candidates.py. Server-only. Run BEFORE any
shard/full run. Locked requirements (2026-07-02):

  1. Benchmark (1,2,3,4,6,7): generator proposes a candidate that certifies
     CERTIFIED_UNIQUE_GEOMETRIC at the known census root; Gate-4 metadata = REJECTED
     (base-point ordering) — proving the generator reaches the containment-violating
     region the mapper structurally cannot seed.
  2. Known valid non-benchmark (1,2,3,5,10,19): candidate certifies at the known census
     root; Gate-4 metadata = VALID.
  3. Layer separation: the proposer emits no census labels (no 'class'/'status'/
     'FEASIBLE'/'CERTIFIED' fields); certification labels come only from
     certify_2b_general; Gate-4 never relabels Layer 1.
  0. Plus: engine hash pin and a determinism gate (two runs byte-identical).

Known roots are read from the census SOURCE OF TRUTH (spherical_roots.jsonl), not from
Table 1 approximations (lesson: Table-1 rows sit at ~1e-6 residual, census roots at ~1e-15).

Usage:
    python3 enumeration/smoke_layer1_gate.py [--roots docs/census_union/spherical_roots.jsonl] [--k 8]
"""
import sys, os, json, math, argparse
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
import layer1_candidates as L1
import certify_2b_general as GEN

EXPECT_ENGINE='de64edfa4979'
BENCH=(1,2,3,4,6,7)
NONBENCH=(1,2,3,5,10,19)
FORBIDDEN_KEYS={'class','status','completeness_status','num_certified_roots','root_lower_bound'}

def load_known(roots_path):
    known={}
    for line in open(roots_path):
        j=json.loads(line)
        sub=tuple(j['subset'])
        if sub in (BENCH, NONBENCH) and j.get('roots'):
            known[sub]=[float(v) for v in j['roots'][0]['coords']]
    missing=[s for s in (BENCH,NONBENCH) if s not in known]
    if missing: raise SystemExit(f'known roots missing from {roots_path}: {missing}')
    return known

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--roots', default='docs/census_union/spherical_roots.jsonl')
    ap.add_argument('--k', type=int, default=8)
    a=ap.parse_args()
    ok=True

    print("=== Phase 0: engine pin + determinism ===")
    print(f"  engine hash {GEN.ENGINE_HASH} (expect {EXPECT_ENGINE})")
    if GEN.ENGINE_HASH != EXPECT_ENGINE:
        print("  FAIL: engine hash mismatch"); return 1
    r1=L1.process_subset((BENCH, a.k, L1.ALTS_DEFAULT))
    r2=L1.process_subset((BENCH, a.k, L1.ALTS_DEFAULT))
    det = json.dumps(r1[1], sort_keys=True)==json.dumps(r2[1], sort_keys=True)
    print(f"  determinism (two runs byte-identical): {'PASS' if det else 'FAIL'}")
    ok &= det

    known=load_known(a.roots)
    cases=[(BENCH,    False, 'ordering'),   # expect Gate-4 REJECTED, reason contains 'ordering'
           (NONBENCH, True,  'valid')]      # expect Gate-4 VALID
    for sub, want_valid, want_word in cases:
        print(f"\n=== subset {sub} (known census root h={known[sub][5]:.6f} rad) ===")
        sub_out,cands,ns,nc = L1.process_subset((sub, a.k, L1.ALTS_DEFAULT))
        print(f"  seeds={ns} converged={nc} candidates after declared filters={len(cands)}")
        # 3) layer separation on every provenance record
        leak=[k for c in cands for k in c if k in FORBIDDEN_KEYS]
        print(f"  layer separation (no census-label keys in proposer output): "
              f"{'PASS' if not leak else 'FAIL '+str(leak)}")
        ok &= not leak
        # 1)/2) reach: some candidate within 1e-6 of the known census root
        kr=np.array(known[sub])
        dists=[(float(np.linalg.norm(np.array(c['coords'])-kr)), c) for c in cands]
        dists.sort(key=lambda t:t[0])
        if not dists or dists[0][0] > 1e-6:
            print(f"  FAIL: generator did not reach the known root "
                  f"(nearest={dists[0][0]:.2e})" if dists else "  FAIL: no candidates at all")
            ok=False; continue
        d,best=dists[0]
        print(f"  reach: nearest candidate at {d:.2e} from known root "
              f"(stratum={best['stratum']}, alt_seed={best['alt_seed_deg']}deg, "
              f"displacement={best['displacement']:.2e})")
        # certify — the certifier decides, on the candidate as proposed
        st,ev=GEN.certify_2b_candidate(list(sub), best['coords'])
        cert = (st=='CERTIFIED_UNIQUE_GEOMETRIC')
        print(f"  certify_2b_general -> {st}"
              + (f"  resid={ev['residual_norm']:.2e} r={ev['radius_used']}" if cert
                 else f"  note={str(ev.get('note',''))[:60]}"))
        ok &= cert
        if cert:
            dc=float(np.linalg.norm(np.array(ev['real_projected_center'])-kr))
            same = dc < 1e-9
            print(f"  certified center vs known census root: |dx|={dc:.2e} "
                  f"({'same root PASS' if same else 'DIFFERENT root FAIL'})")
            ok &= same
        # Gate-4 metadata expectation
        g4 = best['gate4_valid']
        g4ok = (g4 is want_valid) and (want_word in str(best['gate4_reason']))
        print(f"  gate4 metadata: valid={g4} reason='{best['gate4_reason']}' "
              f"(expect valid={want_valid}, '{want_word}') {'PASS' if g4ok else 'FAIL'}")
        ok &= g4ok

    verdict=('PASS — Layer-1 generator proven on both known roots; safe to run a 50-100 subset shard'
             if ok else 'FAIL — do NOT run shards')
    print(f"\n=== SMOKE GATE: {verdict} ===")
    return 0 if ok else 1

if __name__=='__main__':
    sys.exit(main())
