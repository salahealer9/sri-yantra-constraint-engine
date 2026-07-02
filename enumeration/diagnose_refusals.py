"""
diagnose_refusals.py — WHY do layer1 candidates fail certification? Read-only.

Three hypotheses, three signatures:
  H1 near-duplicates (dedup-able)      : tiny nearest-neighbor distances, moderate cond(J),
                                         certifier note 'polish moved > 2e-2'
  H2 genuine proposal noise (tune k)   : scattered points, moderate cond, note
                                         'not near a real root' / krawczyk 'empty'
  H3 near-singular / non-isolated sets : HIGH cond(J) (>~1e8) at resid<=1e-8, many round-9-
     (scientific finding, NOT tunable)   distinct points in tight clusters/curves, krawczyk
                                         'split' at every radius, refusals concentrated there

CHEAP PASS (default, no certifier): per-candidate cond(J) via 6x6 finite differences +
per-subset nearest-neighbor stats + gate4/stratum cross-tabs.
CERTIFY PASS (--certify, server-only, ~1-2s/cand): note / guard / krawczyk-verdict breakdown
cross-tabbed against cond buckets.
"""
import json, math, argparse
import numpy as np
from collections import Counter, defaultdict
import sys, os
_here=os.path.dirname(os.path.abspath(__file__)); _root=_here
while _root!=os.path.dirname(_root):
    if os.path.exists(os.path.join(_root,"sriyantra.py")): break
    _root=os.path.dirname(_root)
for _p in (_here,_root,os.path.join(_root,"enumeration")):
    if os.path.isdir(_p) and _p not in sys.path: sys.path.insert(0,_p)
import sriyantra as RAO

def condJ(coords, subset):
    x=np.array(coords,float); dd=1e-7
    try: F0=np.array([RAO.constraints(*x)[k] for k in subset],float)
    except Exception: return None
    J=np.zeros((6,6))
    for j in range(6):
        xp=x.copy(); xp[j]+=dd
        try: Fp=np.array([RAO.constraints(*xp)[k] for k in subset],float)
        except Exception: return None
        J[:,j]=(Fp-F0)/dd
    s=np.linalg.svd(J, compute_uv=False)
    return float(s[0]/s[-1]) if s[-1]>0 else float('inf')

def bucket(c):
    if c is None: return 'J-undef'
    if c<1e3: return '<1e3'
    if c<1e6: return '1e3-1e6'
    if c<1e8: return '1e6-1e8'
    if c<1e10: return '1e8-1e10'
    return '>=1e10'
BUCKETS=['<1e3','1e3-1e6','1e6-1e8','1e8-1e10','>=1e10','J-undef']

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--candidates', required=True)
    ap.add_argument('--certify', action='store_true', help='also run certify_2b_general per candidate (server)')
    a=ap.parse_args()
    rows=[json.loads(l) for l in open(a.candidates)]
    GEN=None
    if a.certify:
        import certify_2b_general as GEN
    cb=Counter(); cb_g4=defaultdict(Counter); cb_strat=defaultdict(Counter)
    subrep=[]; cert_tab=defaultdict(Counter); status_by_bucket=defaultdict(Counter)
    for r in rows:
        sub=tuple(r['subset']); prov=r['provenance']
        pts=[np.array(p['coords']) for p in prov]
        # nearest-neighbor distance per candidate within the subset cloud
        nnd=[min((float(np.linalg.norm(p-q)) for j,q in enumerate(pts) if j!=i), default=float('nan'))
             for i,p in enumerate(pts)]
        conds=[]
        for i,p in enumerate(prov):
            c=condJ(p['coords'], sub); conds.append(c)
            b=bucket(c); cb[b]+=1
            g='V' if p['gate4_valid'] else ('X' if p['gate4_valid'] is False else '?')
            cb_g4[b][g]+=1; cb_strat[b][p['stratum']]+=1
            if GEN:
                st,ev=GEN.certify_2b_candidate(list(sub), p['coords'])
                note=str(ev.get('note','') or '')
                kraw=ev.get('krawczyk'); kv=kraw[0] if isinstance(kraw,(list,tuple)) else str(kraw)
                key = st if st=='CERTIFIED_UNIQUE_GEOMETRIC' else \
                      ('polish>cap' if 'polish moved' in note else
                       'left-domain' if 'refinement left domain' in note else
                       'resid-too-large' if 'residual' in note and 'too large' in note else
                       f'kraw:{kv}' if kv else st)
                cert_tab[key][bucket(c)]+=1; status_by_bucket[bucket(c)][st]+=1
        good=[c for c in conds if c is not None and np.isfinite(c)]
        subrep.append((sub, len(prov),
                       float(np.nanmedian(nnd)) if pts and len(pts)>1 else float('nan'),
                       float(np.median(good)) if good else float('nan')))
    n=sum(cb.values())
    print(f"=== refusal-structure diagnostic: {a.candidates} ({n} candidates) ===")
    print("\ncond(J) at candidate (resid<=1e-8 by construction):")
    for b in BUCKETS:
        if cb[b]:
            print(f"  {b:9s} {cb[b]:4d}   gate4 {dict(cb_g4[b])}   strata {dict(cb_strat[b])}")
    print("\nhigh-multiplicity subsets (n>=4): n_cands / median NN-dist / median cond(J)")
    for sub,nc,mnn,mc in sorted(subrep, key=lambda t:-t[1]):
        if nc>=4:
            tag=' <== near-singular signature' if (mc==mc and mc>1e8) else ''
            print(f"  {str(sub):26s} n={nc:2d}  NN~{mnn:.2e}  cond~{mc:.1e}{tag}")
    if GEN:
        print("\ncertify outcome x cond bucket:")
        hdr='  {:28s}'+''.join(' {:>9s}'.format(b) for b in BUCKETS)
        print(hdr.format('outcome'))
        for k in sorted(cert_tab):
            print(('  {:28s}'+''.join(' {:9d}'.format(cert_tab[k][b]) for b in BUCKETS)).format(k))
    print("\nREAD: refusals piling into >=1e8 cond buckets (esp. gate4-invalid, tight NN) -> H3")
    print("      'polish>cap' with tiny NN-dist -> H1 (dedup);  scattered moderate-cond -> H2 (tune)")

if __name__=='__main__':
    main()
