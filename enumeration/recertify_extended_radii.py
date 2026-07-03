"""
recertify_extended_radii.py — READ-ONLY extended-radii pass over UNRESOLVED_CERT_FAILED.

Motivation (2026-07-02): (1,2,6,10,16,19) — a genuine root (resid 5.9e-16, guard ok)
refused by Krawczyk 'split' at every default radius (floor 1e-5) from TWO independent
candidate sources — certifies cleanly at radius 3e-6. Mechanism: affine-arithmetic
range overestimation at the default radii, not degeneracy (cond(J)=1.77e4 unchanged
across verdicts). Extending the radii list DOWNWARD is strictly conservative: the
certifier returns on first 'unique', so prior certifications are unaffected and
refusals can only convert. radius_used is recorded per root as always.

This script certifies NOTHING into the census. It answers one question: how many of
the checkpoint's CERT_FAILED subsets convert under EXTENDED_RADII, at which radii,
and which stay refused (and why). Output decides whether an R2 census tier is built.

Usage:
  python3 enumeration/recertify_extended_radii.py \
      --census docs/census_checkpoint_layer1/spherical_roots.jsonl \
      --candidates docs/candidates_layer1_full_domainok.jsonl
"""
import os, sys, json, argparse
from collections import Counter
_here=os.path.dirname(os.path.abspath(__file__)); _root=_here
while _root!=os.path.dirname(_root):
    if os.path.exists(os.path.join(_root,"sriyantra.py")): break
    _root=os.path.dirname(_root)
for _p in (_here,_root,os.path.join(_root,"enumeration")):
    if os.path.isdir(_p) and _p not in sys.path: sys.path.insert(0,_p)
import certify_2b_general as GEN

# default list + downward extension; floor 1e-7 (comfortably above double-precision
# rounding scale for coords ~1; registered as the R2 radii list if the tier is built)
EXTENDED_RADII=[3e-3,1e-3,3e-4,1e-4,3e-5,1e-5,3e-6,1e-6,3e-7,1e-7]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--census', required=True)
    ap.add_argument('--candidates', required=True)
    a=ap.parse_args()
    failed=[tuple(json.loads(l)['subset']) for l in open(a.census)
            if json.loads(l)['class']=='UNRESOLVED_CERT_FAILED']
    cands={tuple(json.loads(l)['subset']): json.loads(l)['candidates'] for l in open(a.candidates)}
    print(f'{len(failed)} UNRESOLVED_CERT_FAILED subsets; extended radii {EXTENDED_RADII}\n')
    conv=[]; still=[]; radius_hist=Counter(); reason_hist=Counter(); nocand=[]
    for sub in sorted(failed):
        cs=cands.get(sub)
        if not cs: nocand.append(sub); continue
        best=None
        for c in cs:
            st,ev=GEN.certify_2b_candidate(list(sub), c, radii=EXTENDED_RADII)
            if st=='CERTIFIED_UNIQUE_GEOMETRIC':
                best=('CERT', ev['radius_used'], ev['residual_norm']); break
            kraw=ev.get('krawczyk'); note=ev.get('note')
            best=best or ('FAIL', kraw, note)
        if best[0]=='CERT':
            conv.append((sub,best[1])); radius_hist[best[1]]+=1
            print(f'  CONVERTS  {sub}  radius_used={best[1]:g}  resid={best[2]:.1e}')
        else:
            still.append(sub)
            k=best[1][0] if isinstance(best[1],(list,tuple)) else str(best[1])
            reason_hist[f'kraw:{k}|note:{str(best[2])[:30]}']+=1
    print(f'\n=== extended-radii result ===')
    print(f'  converts      : {len(conv)}/{len(failed)}   radius histogram: {dict(radius_hist)}')
    print(f'  still refused : {len(still)}   mechanisms: {dict(reason_hist)}')
    if nocand: print(f'  no candidates in file (unexpected): {nocand}')
    print('\nREAD-ONLY. If converts>0: build the R2 tier (scratch census with EXTENDED_RADII '
          '-> merge_census_layer1 with checkpoint name R2, upgrade-only as always).')

if __name__=='__main__':
    main()
