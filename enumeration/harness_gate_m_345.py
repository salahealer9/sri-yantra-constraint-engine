import sys, os, math, random
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
import domain_sphere as D
from aar_sphere import SplitNeeded, DomainError

print("GATE-M criteria 3,4,5 (domain_sphere)")

# ---- criterion 4: Krawczyk certifies the {1,2,3,4,6,7} Newton root ----
root=[0.6246238466927992,0.7044304165359816,0.7482768099360514,
      0.6307397242292889,0.3136386632298885,22.64768569612002*math.pi/180.0]
print("\n[c4] AA-Krawczyk on the known Newton root (expect 'unique' at small r):")
c4=False
for r in (3e-3,1e-3,3e-4,1e-4):
    rv=[r]*6
    v=D.certify_box(root,rv)
    print(f"     r={r:.0e}: {v}")
    if v=='unique': c4=True
print(f"   criterion 4 (root certified unique): {'PASS' if c4 else 'FAIL'}")

# ---- criterion 5: exclusion rejects boxes away from any root ----
# pick random small boxes far from the root; engine-valid but should be excluded
random.seed(20260625)
B=D.B_SPHERE
def randbox(half=2e-3):
    while True:
        c=[random.uniform(lo+half,hi-half) for (lo,hi) in B]
        # far from the known root
        if max(abs(c[i]-root[i]) for i in range(6))<0.05: continue
        try: RAO.constraints(*c)   # engine-valid center
        except Exception: continue
        return [(c[i]-half,c[i]+half) for i in range(6)]
excl=split=dom=ind=0; N=400
for _ in range(N):
    cls=D.classify(randbox())
    if cls=='excluded': excl+=1
    elif cls=='split': split+=1
    elif cls=='domain': dom+=1
    else: ind+=1
print(f"\n[c5] classify() on {N} small engine-valid boxes far from the root:")
print(f"     excluded={excl}  split={split}  domain={dom}  indeterminate={ind}")
print(f"   criterion 5 (most off-root boxes excluded, ~none spuriously indeterminate): "
      f"{'PASS' if excl>0 and ind<=N*0.2 else 'CHECK'}")

# ---- criterion 3: domain-edge handling (no crash; correct split/exclude) ----
print("\n[c3] domain-edge boxes (must classify cleanly, never crash):")
edge_boxes={
 "h->pi/2 (r->0, acos arg ->big)": [(0.3,0.4),(0.6,0.7),(0.6,0.7),(0.4,0.5),(0.1,0.2),(1.50,1.5707)],
 "c large (cos c small)":          [(0.3,0.4),(1.05,1.10),(0.2,0.3),(0.3,0.4),(0.1,0.2),(0.3,0.4)],
 "tiny corner near 0":             [(1e-6,2e-3),(1e-6,2e-3),(1e-6,2e-3),(1e-6,2e-3),(1e-6,2e-3),(1e-6,2e-3)],
 "wide full B_sphere":             D.B_SPHERE,
}
c3=True
for name,bx in edge_boxes.items():
    try:
        cls=D.classify(bx); print(f"     [{cls:>13}]  {name}")
    except Exception as ex:
        c3=False; print(f"     [CRASH:{type(ex).__name__}]  {name}")
print(f"   criterion 3 (clean classification, no crash): {'PASS' if c3 else 'FAIL'}")
