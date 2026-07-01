"""
make_nonbenchmark_fixture.py — regenerate first_nonbenchmark_certified_root.json from committed
inputs (candidates file + certify_2b_general). Deterministic: picks the SORTED-first non-benchmark
subset whose warm-start candidate certifies, and records the full certificate for the regression
gate. Closes the provenance chain (no hand-written snippets; the fixture is a build product of THIS
script). PROPOSE stays in the search; this only SELECTS an already-certifying candidate as fixture.
"""
import sys, os, json, argparse
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
BENCH=(1,2,3,4,6,7)

def main(cands_path, out_path):
    rows=[json.loads(l) for l in open(cands_path)]
    rows.sort(key=lambda j: tuple(j['subset']))
    for j in rows:
        sub=tuple(j['subset'])
        if sub==BENCH: continue
        for cand in j['candidates']:
            st,ev=GEN.certify_2b_candidate(list(sub), cand)
            if st=='CERTIFIED_UNIQUE_GEOMETRIC':
                fixture=dict(
                    subset=list(sub), candidate=list(cand),
                    expected_status='CERTIFIED_UNIQUE_GEOMETRIC',
                    real_projected_center=ev['real_projected_center'],
                    radius_used=ev['radius_used'], residual_norm=ev['residual_norm'],
                    engine_hash=ev['engine_hash'],
                    source='warm-start/Table1 via candidate_search_warmstart.py',
                    note='first (sorted) non-benchmark certified root; regression fixture')
                json.dump(fixture, open(out_path,'w'), indent=2)
                print(f"fixture subset={sub} status={st} engine={ev['engine_hash']}")
                print("wrote", out_path); return 0
    print("ERROR: no non-benchmark candidate certified"); return 1

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--candidates', default='docs/candidates_warmstart.jsonl')
    ap.add_argument('--out', default='docs/first_nonbenchmark_certified_root.json')
    a=ap.parse_args()
    sys.exit(main(a.candidates, a.out))
