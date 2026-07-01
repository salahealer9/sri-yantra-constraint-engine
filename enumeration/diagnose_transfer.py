"""
diagnose_transfer.py — read-only analysis of a transfer-tier candidate run. Certifies every
proposed candidate and BREAKS DOWN outcomes so a low yield is diagnosed (residual vs
displacement-cap vs domain vs genuinely-not-a-root), not just counted. Changes NO logic.
"""
import sys, os, json, argparse
from collections import Counter
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

def main(cands_path, prior_path=None):
    prior=set()
    if prior_path:
        try: prior=set(tuple(json.loads(l)['subset']) for l in open(prior_path))
        except Exception: pass
    n_prop=0; cert=[]; status=Counter(); notes=Counter(); new_subs=set()
    for line in open(cands_path):
        d=json.loads(line); sub=tuple(d['subset'])
        for cand in d['candidates']:
            n_prop+=1
            st,ev=GEN.certify_2b_candidate(list(sub), cand)
            status[st]+=1
            if st=='CERTIFIED_UNIQUE_GEOMETRIC':
                cert.append(sub)
                if sub not in prior and sub!=BENCH: new_subs.add(sub)
            else:
                # classify WHY it failed (the diagnostic that decides perturb-vs-monodromy)
                note=ev.get('note','')
                if 'residual' in note:          notes['refined_residual_too_large']+=1
                elif 'polish moved' in note:     notes['displacement_cap_rejected']+=1
                elif 'domain' in note.lower():   notes['domain_invalid']+=1
                elif 'refinement left domain' in note: notes['newton_left_domain']+=1
                else:                            notes[note[:40] or st]+=1
    print(f"=== transfer diagnosis: {cands_path} ===")
    print(f"candidates proposed      : {n_prop}")
    print(f"subsets with candidates  : {sum(1 for _ in open(cands_path))}")
    print(f"CERTIFIED                : {len(cert)}  ({len(set(cert))} distinct subsets)")
    print(f"NEW non-benchmark subsets: {len(new_subs)}  (not in prior direct-tier set)")
    print(f"\nstatus breakdown:")
    for k,v in status.most_common(): print(f"  {k:32s} {v}")
    if notes:
        print(f"\nWHY non-certified (the perturb-vs-monodromy signal):")
        for k,v in notes.most_common(): print(f"  {k:32s} {v}")
    if new_subs:
        print(f"\nnew certified subsets: {sorted(new_subs)[:20]}{' ...' if len(new_subs)>20 else ''}")
    print(f"\nREAD:")
    if len(new_subs)>=5:
        print("  meaningful direct transfer -> BUILD PARALLEL, run --perturb 3/10 next.")
    elif len(new_subs)>=1:
        print("  weak-but-nonzero transfer -> perturbations MAY help; check dominant failure mode above.")
    else:
        print("  NO new direct transfer. Do NOT assume perturb saves it. If failures are dominated by")
        print("  'refined_residual_too_large'/'newton_left_domain' -> the known roots are not near other")
        print("  systems' roots -> per-subset discovery (monodromy/homotopy) is the real next tool.")

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--candidates', default='docs/candidates_transfer.jsonl')
    ap.add_argument('--prior', default='docs/candidates_warmstart.jsonl')
    a=ap.parse_args()
    main(a.candidates, a.prior)
