"""Amendment-01 validation: run the pilot sample TWICE; require identical
classification hash, category counts, and flagged-case list (bit-for-bit determinism)."""
import sys, os, hashlib, json
_here = os.path.dirname(os.path.abspath(__file__))
_root = _here
while _root != os.path.dirname(_root):
    if os.path.exists(os.path.join(_root, "sriyantra_plane.py")):
        break
    _root = os.path.dirname(_root)
for _p in (_here, _root, os.path.join(_root, "enumeration")):
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)
import spherical_existence_mapper as M
from collections import Counter
surv,_=M.load(); surv_items=list(surv.items()); survset=set(surv)
def warm(sub):
    for thr in (4,3,2):
        w=[r for s,r in surv_items if len(set(sub)&set(s))>=thr][:6]
        if w: return w
    return []
def feas(sub): return tuple(sub) in survset
SAMPLE=[(1,2,3,4,8),(1,2,5,8,15),(1,2,3,4,6),(1,2,3,6,13),(1,2,4,6,8),(1,2,3,4,7),(1,2,7,12,17)]

def run():
    rows=[]
    for sub in SAMPLE:
        r=M.map_subset(sub, warm(sub), feas(sub))
        vi=(round(r['valid'][0],2),round(r['valid'][1],2)) if r['valid'] else None
        rows.append((sub, r['cls'], r.get('tier'), vi))
    h=hashlib.sha256(json.dumps(rows, default=str).encode()).hexdigest()[:16]
    counts=dict(Counter(x[1] for x in rows))
    flagged=[(x[0],x[2]) for x in rows if x[2] in ("tangency","near_degenerate")]
    return rows, h, counts, flagged

print("RUN 1 ..."); r1,h1,c1,f1=run()
for sub,cls,tier,vi in r1: print(f"   {str(sub):16s} {str(cls):20s} tier={str(tier):16s} valid={vi}")
print("RUN 2 ..."); r2,h2,c2,f2=run()

print("\n--- determinism ---")
print(f"  classification hash:  run1={h1}  run2={h2}  identical={h1==h2}")
print(f"  category counts:      {c1}   identical={c1==c2}")
print(f"  flagged cases:        {f1}   identical={f1==f2}")
print(f"\n  ALGEBRAIC_EMPTY count: {c1.get('ALGEBRAIC_EMPTY',0)}")
target=[x for x in r1 if x[0]==(1,2,7,12,17)][0]
print(f"  (1,2,7,12,17): class={target[1]}, tier={target[2]}  -> "
      f"{'SPHERICAL_ONLY tangency (restored, excluded from robust counts)' if target[1]=='SPHERICAL_ONLY' and target[2]=='tangency' else 'CHECK'}")
ok = (h1==h2 and c1==c2 and f1==f2)
print(f"\n  AMENDMENT-01 DETERMINISM: {'PASS' if ok else 'FAIL'}")
