"""
gate4_census_audit.py — classify ALL certified roots in the census by Gate-4 geometric validity,
as Layer-2 METADATA (never replacing Layer-1 certification). Reads the certified roots from the
census JSONL (source of truth), runs Gate-4, records status per subset.

Two modes:
  --ordering-only : reproduce Gate-4 ORDERING+SEP from arithmetic (no mapper stack; runs anywhere).
  (default)       : call the REAL spherical_geo_check.gate4 (constructibility + ordering + closure);
                    SERVER-only (needs the mapper stack). Falls back to ordering-only if unavailable.

Statuses: GEOM_VALID_GATE4 | GEOM_REJECTED_GATE4 | GEOM_GATE4_UNAUDITED (+ reason).
Output: gate4_status.json {subset: {status, reason, r, margins}}, and a summary.
Certification counts are UNCHANGED; this only adds a geometry layer.
"""
import sys, os, math, json, argparse
_here = os.path.dirname(os.path.abspath(__file__))
_root = _here
while _root != os.path.dirname(_root):
    if os.path.exists(os.path.join(_root, "sriyantra.py")):
        break
    _root = os.path.dirname(_root)
for _p in (_here, _root, os.path.join(_root, "enumeration")):
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)
PI2=math.pi/2; SEP=1e-6

def ordering_only(b,c,d,e,g,h):
    r=PI2-h
    order=[-r,-(b+c),-c,-g,0.0,d,d+e,r]
    lab=['P0','P1','P3','P4','Pc','P7','P9','P10']
    viol=[f'{lab[i]}>={lab[i+1]}' for i in range(len(order)-1) if order[i]>=order[i+1]]
    if viol: return False, 'ordering: '+','.join(viol), r
    if min(order[i+1]-order[i] for i in range(len(order)-1)) < SEP*r:
        return False, 'base points too close', r
    return True, 'ordering ok', r

def load_certified(census_jsonl):
    roots={}
    for line in open(census_jsonl):
        r=json.loads(line)
        if r.get('class')=='FEASIBLE_CERTIFIED' and r.get('roots'):
            roots[tuple(r['subset'])]=[float(x) for x in r['roots'][0]['coords']]
    return roots

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--census', default='docs/census_union/spherical_roots.jsonl')
    ap.add_argument('--ordering-only', action='store_true')
    ap.add_argument('--out', default='docs/gate4_status.json')
    a=ap.parse_args()
    roots=load_certified(a.census)
    real_gate4=None
    if not a.ordering_only:
        try:
            from spherical_geo_check import gate4 as real_gate4
            print("using REAL gate4 (constructibility + ordering + closure)")
        except Exception as e:
            print(f"real gate4 unavailable ({type(e).__name__}); falling back to ordering-only")
    from collections import Counter; cnt=Counter(); out={}
    print(f"\nauditing {len(roots)} certified roots (Layer-2 metadata):\n")
    for sub in sorted(roots):
        b,c,d,e,g,h=roots[sub]
        if real_gate4:
            try:
                valid,reason=real_gate4(b,c,d,e,g,h)
                st='GEOM_VALID_GATE4' if valid else 'GEOM_REJECTED_GATE4'
            except Exception as ex:
                st,reason='GEOM_GATE4_UNAUDITED',f'{type(ex).__name__}: {ex}'
            r=PI2-h
        else:
            ok,reason,r=ordering_only(b,c,d,e,g,h)
            st='GEOM_VALID_GATE4' if ok else 'GEOM_REJECTED_GATE4'
            st += '_ORDERING'  # mark partial
        cnt[st]+=1
        out[str(sub)]=dict(status=st, reason=reason, r=r, m_bc=r-(b+c), m_de=r-(d+e))
        print(f"  {str(sub):24s} r={r:7.4f}  {st}  ({reason[:45]})")
    json.dump(out, open(a.out,'w'), indent=2, sort_keys=True)
    print(f"\nLayer-2 Gate-4 summary (of {len(roots)} CERTIFIED roots -- Layer-1 unchanged):")
    for k,v in cnt.most_common(): print(f"  {k:34s} {v}")
    print(f"\nwrote {a.out}  (metadata; certification counts unaffected)")

if __name__=='__main__': main()
