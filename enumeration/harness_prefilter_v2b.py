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
from aar import AAr
from chain_sphere import AA_FN
from aar_sphere import aa_cos
from prefilter_v2 import prefilter_excludes
HALF=math.pi/2
random.seed(20260625); B=D.B_SPHERE
def randbox(maxhalf=0.15):
    while True:
        c=[random.uniform(lo,hi) for (lo,hi) in B]; box=[]; ok=True
        for i,(lo,hi) in enumerate(B):
            half=random.uniform(1e-4,maxhalf); l=max(lo,c[i]-half); h=min(hi,c[i]+half)
            if l>=h: ok=False; break
            box.append((l,h))
        if ok: return box
def engine_valid_anywhere(box, tries=300):
    for _ in range(tries):
        p=[random.uniform(lo,hi) for (lo,hi) in box]
        try: RAO.chain(*p); return True
        except Exception: continue
    return False

N=20000
fired=0; sound_viol=0
disg_ok=0; disg_split=0; agree_domain=0
ok_examples=[]
for _ in range(N):
    box=randbox()
    if not prefilter_excludes(box): continue
    fired+=1
    if engine_valid_anywhere(box): sound_viol+=1
    AAr._n=[0]; g=D.full_chain_domain_guard(D._aabox(box))
    if g=='domain': agree_domain+=1
    elif g=='split': disg_split+=1
    elif g=='ok':
        disg_ok+=1
        if len(ok_examples)<5: ok_examples.append(box)

print("PRE-FILTER v2 (cone-edge) — corrected analysis")
print(f"  fired (pre-filter excluded): {fired}")
print(f"  SOUNDNESS (fired but engine-valid point exists): {sound_viol}   [MUST be 0]")
print(f"  guard breakdown on fired boxes:")
print(f"     full guard agrees 'domain'      : {agree_domain}")
print(f"     guard 'split' (AA loose, pre-filter STRICTER, sound): {disg_split}")
print(f"     guard 'ok'   (RED FLAG: AA says real on invalid box) : {disg_ok}")

# If any 'ok', investigate: is the true arg of x1/x2 really >1 everywhere, and did
# the AA enclosure of that arg fail to contain it? (would be an AA rigor bug)
if ok_examples:
    print("\n  investigating 'ok' disagreements (AA arg-enclosure vs true arg range):")
    for box in ok_examples:
        (_b,(clo,chi),(dlo,dhi),_e,_g,(hlo,hhi))=box
        # true arg1 = cos(r)/cos(c) range over box; r=pi/2-h
        import itertools
        cand=[]
        for h in (hlo,hhi):
            for c in (clo,chi):
                cand.append(math.cos(HALF-h)/math.cos(c))
        print(f"     box c=[{clo:.4f},{chi:.4f}] h=[{hlo:.4f},{hhi:.4f}]  true arg1 corners=[{min(cand):.4f},{max(cand):.4f}]")
        # AA enclosure of arg1
        AAr._n=[0]
        bb=D._aabox(box)
        r=AA_FN.cos(__import__('chain_sphere').HALF_PI - bb[5])  # cos(r)
        cc=AA_FN.cos(bb[1])
        arg=r/cc; lo,hi=arg.iv()
        print(f"        AA arg1 enclosure=[{lo:.4f},{hi:.4f}]  (contains true range? {lo<=min(cand) and max(cand)<=hi})")
else:
    print("\n  no 'ok' disagreements -> all disagreements are 'split' (pre-filter soundly stricter than loose AA).")

sound = (sound_viol==0 and disg_ok==0)
print(f"\n  PRE-FILTER SOUND (no valid box excluded; no AA-rigor red flag): {sound}")
