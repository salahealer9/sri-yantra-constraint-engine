"""
PILOT — confirm the registered five-way classifier and the Gate-6 stop condition on
known cases before the full confirmatory sweep. Not the census; a conformance test of
the (now spec-conformant) existence-interval mapper.
"""
import os, sys, math
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

surv, fail = M.load(); surv_items = list(surv.items()); survset = set(surv.keys())
def warm(sub):
    for thr in (4,3):
        w=[r for s,r in surv_items if len(set(sub)&set(s))>=thr][:6]
        if w: return w
    return []
def feasible(sub): return tuple(sub) in survset

# registered pilot sample: one known case per category + the (1,2,7,12,17) regression
SAMPLE = [
    ((1,2,3,4,8),  "PLANE_CONTINUATION", "plane survivor -> valid branch to in-box pole"),
    ((1,2,5,8,15), "PLANE_CONTINUATION", "plane survivor with fold -> fold + in-box pole"),
    ((1,2,3,4,6),  "SPHERICAL_ONLY",     "infeasible, curvature-confined (ordering cap)"),
    ((1,2,3,6,13), "SPHERICAL_ONLY",     "infeasible, curvature-confined (ordering cap)"),
    ((1,2,4,6,8),  "POLE_OUT_OF_DOMAIN", "infeasible, valid branch to out-of-box pole"),
    ((1,2,3,4,7),  "ALGEBRAIC_ONLY",     "infeasible, root exists but never Gate-4-valid"),
    ((1,2,7,12,17),"SPHERICAL_ONLY",   "reproducible, but a near-zero-width tangency (flagged, sec.7)"),
]

print("="*92)
print("PILOT 1 — five-way classifier on known cases")
print("="*92)
npass=0
for sub, expected, why in SAMPLE:
    r = M.map_subset(sub, warm(sub), feasible(sub))
    got = r["cls"]
    ok = (got == expected)
    npass += ok
    vi = f"[{r['valid'][0]:.0f},{r['valid'][1]:.0f}]" if r['valid'] else "-"
    print(f"  {('PASS' if ok else 'FAIL')}  {str(sub):16s} got={got:22s} expect={expected:20s} "
          f"valid={vi} fold={r['fold']} neardegen={r.get('near_degenerate')} zerowidth={r.get('near_zero_width')}")
    print(f"        ({why})")
print(f"\n  classifier: {npass}/{len(SAMPLE)} known cases as expected")

print("\n"+"="*92)
print("PILOT 2 — Gate 6 stop condition is live AND discriminating")
print("="*92)
# same in-box-pole subset, classified both ways
sub=(1,2,3,4,8)
r_feas = M.map_subset(sub, warm(sub), True)      # truthful: plane-feasible
r_inf  = M.map_subset(sub, warm(sub), False)     # counterfactual: pretend infeasible
print(f"  in-box-pole subset {sub}:")
print(f"    as plane-FEASIBLE   -> {r_feas['cls']:26s} halt={r_feas.get('halt')}   (expect PLANE_CONTINUATION, no halt)")
print(f"    as plane-INFEASIBLE -> {r_inf['cls']:26s} halt={r_inf.get('halt')}   (expect HALT, census stops)")
g6_live = (r_feas['cls']=="PLANE_CONTINUATION" and not r_feas.get('halt')
           and r_inf.get('halt') and "HALT" in r_inf['cls'])
print(f"\n  Gate 6 behaves correctly (fires iff infeasible+in-box): {g6_live}")

print("\n"+"="*92)
print(f"PILOT RESULT: classifier {npass}/{len(SAMPLE)}, Gate-6 {'OK' if g6_live else 'FAIL'}")
print("="*92)
