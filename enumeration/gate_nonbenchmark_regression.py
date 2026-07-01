"""Permanent regression: the generalized certifier must certify a real NON-benchmark root.
Turns 'wired general' into 'certification proven general on >=2 real systems'."""
import sys, os, json;
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
fx=json.load(open(os.path.join(_root, 'docs', 'first_nonbenchmark_certified_root.json')))
sub=tuple(fx['subset']); assert sub!=(1,2,3,4,6,7), "fixture must be non-benchmark"
st,ev=GEN.certify_2b_candidate(list(sub), fx['candidate'])
ok = st=='CERTIFIED_UNIQUE_GEOMETRIC' and ev['engine_hash']==fx['engine_hash']
print(f"regression: non-benchmark {sub} -> {st}  (engine {ev['engine_hash']})")
print("PASS" if ok else "FAIL"); sys.exit(0 if ok else 1)
