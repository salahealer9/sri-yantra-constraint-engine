"""Equivalence gate: serial(--workers 1) == parallel(--workers K) byte-identical, incl. perturb.
Proves per-subset deterministic seeding is order/worker-independent. Run on a slice for speed."""
import sys, json, subprocess, os
_here = os.path.dirname(os.path.abspath(__file__))
_root = _here
while _root != os.path.dirname(_root):
    if os.path.exists(os.path.join(_root, "sriyantra.py")):
        break
    _root = os.path.dirname(_root)
for _p in (_here, _root, os.path.join(_root, "enumeration")):
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)
UNI=sys.argv[1] if len(sys.argv)>1 else 'docs/subset_universe.json'
# build a deterministic slice for a fast gate
U=json.load(open(UNI)); U2=dict(U); U2['subsets']=[list(s) for s in sorted(tuple(x) for x in U['subsets'])[:200]]
json.dump(U2, open('/tmp/_uni_slice.json','w'))
def run(w,out):
    subprocess.run([sys.executable,'enumeration/candidate_search_parallel.py','--tier','transfer',
                    '--perturb','2','--workers',str(w),'--universe','/tmp/_uni_slice.json','--out',out],
                   check=True, capture_output=True)
run(1,'/tmp/_w1.jsonl'); run(4,'/tmp/_w4.jsonl')
a=open('/tmp/_w1.jsonl').read(); b=open('/tmp/_w4.jsonl').read()
print("PASS: serial == parallel (byte-identical)" if a==b else "FAIL: differ")
sys.exit(0 if a==b else 1)
