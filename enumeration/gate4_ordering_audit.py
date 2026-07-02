"""
gate4_ordering_audit.py — classify certified roots by Gate-4's base-point-ORDERING condition,
reproduced faithfully from spherical_geo_check.gate4 (lines 104-115). This is the ORDERING part
only -- pure arithmetic on (b,c,d,e,g,h), NO mapper stack, NO L.newton, NO figure-closure (which
needs build()). We report ordering + margins; full Gate-4 (constructibility + closure) is a
SERVER step. Records geometry status as METADATA, never replacing certification.

Axis base points (from spherical_geo_check.py lines 15-16, 62-64):
    P0=-r, P1=-(b+c), P3=-c, P4=-g, Pc=0, P7=d, P9=d+e, P10=r     (r = pi/2 - h)
Ordering condition (line 110-113): the sequence [-r,-(b+c),-c,-g,0,d,d+e,r] must be strictly
increasing; else 'base-point ordering violated'. Separation (line 114): min gap >= sep*r.
"""
import sys, os, math, json
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

def gate4_ordering(b,c,d,e,g,h):
    r=PI2-h
    order=[-r, -(b+c), -c, -g, 0.0, d, d+e, r]
    labels=['P0(-r)','P1(-(b+c))','P3(-c)','P4(-g)','Pc(0)','P7(d)','P9(d+e)','P10(r)']
    viol=[i for i in range(len(order)-1) if order[i]>=order[i+1]]
    if viol:
        pairs=[f'{labels[i]}>={labels[i+1]}' for i in viol]
        return 'GEOM_REJECTED_GATE4_ORDERING', 'ordering: '+', '.join(pairs), r, order
    gaps=[order[i+1]-order[i] for i in range(len(order)-1)]
    if min(gaps) < SEP*r:
        return 'GEOM_REJECTED_GATE4_SEP', f'min gap {min(gaps):.2e} < {SEP}*r', r, order
    return 'GEOM_ORDERING_OK', 'ordering strictly increasing', r, order

def load_roots(paths):
    seen={}
    for p in paths:
        try:
            for line in open(p):
                d=json.loads(line); sub=tuple(d['subset'])
                if sub in seen: continue
                # candidate may be raw list; take first
                c=d['candidates'][0]
                coords=c['coords'] if isinstance(c,dict) else c
                seen[sub]=[float(x) for x in coords]
        except FileNotFoundError: pass
    return seen

if __name__=='__main__':
    paths=sys.argv[1:] or ['candidates_warmstart.jsonl','candidates_transfer.jsonl']
    roots=load_roots(paths)
    print(f"classifying {len(roots)} certified roots by Gate-4 ORDERING (metadata only):\n")
    from collections import Counter; cnt=Counter()
    print(f"  {'subset':24s} {'r':>7s} {'r-(b+c)':>9s} {'r-(d+e)':>9s}  status")
    for sub in sorted(roots):
        b,c,d,e,g,h=roots[sub]
        st,reason,r,order=gate4_ordering(b,c,d,e,g,h)
        cnt[st]+=1
        print(f"  {str(sub):24s} {r:7.4f} {r-(b+c):9.4f} {r-(d+e):9.4f}  {st}")
        if 'REJECTED' in st: print(f"      -> {reason}")
    print(f"\nGate-4 ordering summary (of {len(roots)} certified roots):")
    for k,v in cnt.most_common(): print(f"  {k:32s} {v}")
    print("\nNOTE: this is ORDERING+SEP only. Full Gate-4 also requires constructibility + figure")
    print("closure (build()), which is a SERVER step. Certification (26) is UNAFFECTED -- this is metadata.")
