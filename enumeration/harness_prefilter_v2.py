import sys, os, math, random, itertools
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
from prefilter_v2 import prefilter_excludes

# ---- SOUNDNESS (critical): every box the pre-filter excludes must contain ZERO
#      engine-domain-valid points, AND the full-chain guard must also call it 'domain'.
random.seed(20260625); B=D.B_SPHERE
def randbox(maxhalf=0.15):
    while True:
        c=[random.uniform(lo,hi) for (lo,hi) in B]
        box=[]
        ok=True
        for i,(lo,hi) in enumerate(B):
            half=random.uniform(1e-4,maxhalf)
            l=max(lo,c[i]-half); h=min(hi,c[i]+half)
            if l>=h: ok=False; break
            box.append((l,h))
        if ok: return box

def engine_valid_anywhere(box, tries=200):
    """Monte-Carlo probe: does ANY point in the box pass the frozen engine domain?"""
    for _ in range(tries):
        p=[random.uniform(lo,hi) for (lo,hi) in box]
        try:
            RAO.chain(*p); return True
        except Exception:
            continue
    return False

N=20000
fired=0; sound_viol=0; guard_disagree=0
for _ in range(N):
    box=randbox()
    if prefilter_excludes(box):
        fired+=1
        # (a) must contain no engine-valid point
        if engine_valid_anywhere(box): sound_viol+=1
        # (b) full-chain guard must also exclude as 'domain'
        AAr._n=[0]
        if D.full_chain_domain_guard(D._aabox(box))!='domain': guard_disagree+=1

print("PRE-FILTER v2 (cone-edge) — soundness + consistency")
print(f"  random boxes tested        : {N}")
print(f"  pre-filter fired (excluded): {fired}")
print(f"  SOUNDNESS violations (fired but engine-valid point exists): {sound_viol}   [MUST be 0]")
print(f"  guard disagreements (fired but full-guard != 'domain')    : {guard_disagree}   [MUST be 0]")
sound = (sound_viol==0 and guard_disagree==0)
print(f"  -> pre-filter SOUND: {sound}")

# ---- CONSISTENCY: pre-filter must NEVER fire on a box the guard passes ('ok'/'split')
inconsist=0; checked=0
for _ in range(N):
    box=randbox()
    AAr._n=[0]; g=D.full_chain_domain_guard(D._aabox(box))
    checked+=1
    if prefilter_excludes(box) and g in ('ok','split'):
        inconsist+=1
print(f"\n  consistency: pre-filter fired on a guard-ok/split box: {inconsist}/{checked}   [MUST be 0]")

# ---- YIELD: on the uniform grid (comparable to smoke diagnostics), how much does
#      the cheap pre-filter remove vs the acos-bearing full classify?
print("\nYIELD on uniform grid (cheap pre-filter vs full classify):")
for K in (4,5):
    axes=[]
    for (lo,hi) in B:
        step=(hi-lo)/K; axes.append([(lo+i*step,lo+(i+1)*step) for i in range(K)])
    tot=pf=dom_full=0
    for combo in itertools.product(*axes):
        box=list(combo); tot+=1
        if prefilter_excludes(box): pf+=1
        AAr._n=[0]
        if D.full_chain_domain_guard(D._aabox(box))=='domain': dom_full+=1
    print(f"  K={K}: {tot} boxes; cheap pre-filter excludes {pf} ({100*pf/tot:.0f}%) "
          f"with 0 acos; full guard domain-excludes {dom_full} ({100*dom_full/tot:.0f}%)")
