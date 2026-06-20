"""
STAGE 2 — Gate-4 probes: classify singular events by GEOMETRIC mechanism.

Uses the spherical Gate-4 constructor (spherical_geo_check.py) as a scientific
instrument. For each subset branch that terminates, the constructor reports
observables far more diagnostic than the Jacobian's smallest singular value:
  - figure validity (Gate-4) and the altitude at which it first fails,
  - minimum pairwise point separation (point collision / vanishing triangle),
  - base-point ordering, closure.
These separate three distinct mechanisms:

  FOLD               : Gate-4 valid with healthy separation up to a turning point;
                       pseudo-arclength reverses in h (two valid figures merge at h*).
  VALIDITY BOUNDARY  : Gate-4 fails (base-point ordering) at an altitude ABOVE the
                       altitude where the algebraic root finally disappears.
  COLLISION/COLLAPSE : minimum point separation -> 0 (a vanishing triangle).

This makes concrete the spherical project's layered notion of existence:
  algebraic solution  ⊋  realizable figure  ⊋  Gate-4-valid (census) figure,
with each boundary occurring at its own altitude.
"""
import os, sys, math, json
_here = os.path.dirname(os.path.abspath(__file__))
_root = _here
while _root != os.path.dirname(_root):
    if os.path.exists(os.path.join(_root, "sriyantra_plane.py")):
        break
    _root = os.path.dirname(_root)
for _p in (_here, _root, os.path.join(_root, "enumeration")):
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)
import numpy as np
import spherical_geo_check as GC
import stage1b_landscape as L
import stage1_fold_analysis as FA

PI2 = math.pi/2; DEG = math.pi/180

def _roots():
    census = os.path.join(os.path.dirname(__file__), "campaign_results", "roots.jsonl")
    return {tuple(json.loads(l)["subset"]): json.loads(l)["roots"][0]["coords"]
            for l in open(census)
            if json.loads(l).get("roots")}

def figure_diag(x, h):
    """(min pairwise separation / r, Gate-4 valid, reason) or None if not constructible."""
    G = GC.build(*x, h)
    if G is None: return None
    keys = ('p1','p2','p3','p4','p5','p6','p8','p9','p10','p12','p13','p16','p17','p18','p19')
    P = [G[k] for k in keys]
    minsep = min(GC.gdist(P[i],P[j]) for i in range(len(P)) for j in range(i+1,len(P)))/G['r']
    ok, why = GC.gate4(*x, h, closure_tol=1e-7)
    return minsep, ok, why

def classify(sub, root, h_hi=89.0, h_lo=12.0, dh=0.25):
    x = np.array(root)*(PI2-h_hi*DEG); rows=[]; stop=h_lo
    for hd in np.arange(h_hi, h_lo, -dh):
        xs,res,ok,c = L.newton(sub, x, hd*DEG, maxit=70)
        if not ok: stop=hd; break
        x = xs; d = figure_diag(xs, hd*DEG)
        if d is not None: rows.append((hd, *d))
    first_invalid = next(((hd,why) for hd,ms,v,why in rows if not v), None)
    last_sep = rows[-1][1] if rows else None
    valid_floor = next((hd for hd,ms,v,why in rows if v), None)  # highest h that is valid (since descending)
    # last valid altitude = smallest hd among valid rows
    valid_rows = [hd for hd,ms,v,why in rows if v]
    census_valid_until = min(valid_rows) if valid_rows else None
    if first_invalid and 'ordering' in first_invalid[1]:
        mech = "VALIDITY BOUNDARY (ordering)"
    elif last_sep is not None and last_sep < 0.02 and not first_invalid:
        mech = "COLLISION/COLLAPSE"
    elif not first_invalid:
        mech = "FOLD-signature (valid, healthy sep at turning point)"
    else:
        mech = f"other: {first_invalid[1]}"
    return dict(mech=mech, solver_stop=stop, census_valid_until=census_valid_until,
                first_invalid=first_invalid, last_sep=last_sep)

def confirm_fold(sub, root, h0, ds=0.0008, n=4000):
    P = FA.arclength(sub, FA.seed_at(sub, root, h0), ds=ds, n=n)
    if len(P) < 5: return None, False
    h = P[:,5]/DEG
    return h.min(), (h[-1] > h.min()+0.2)

if __name__ == "__main__":
    R = _roots()
    targets = [
        ((1,2,5,8,15), 64.0, "confirmed fold (control)"),
        ((1,2,8,10,14),53.0, "confirmed fold (control)"),
        ((1,2,8,10,11),79.0, "Stage-1 unresolved"),
        ((1,2,8,11,19),83.0, "Stage-1 unresolved"),
        ((1,2,3,11,15),17.0, "Stage-1 unresolved"),
        ((1,2,3,10,14),24.0, "{.,14} boundary (control)"),
    ]
    print(f"{'subset':16s} {'tag':26s} {'mechanism':40s} {'h* / boundary':>14}")
    for sub,h0,tag in targets:
        c = classify(sub, R[sub])
        extra=""
        if c['mech'].startswith("FOLD"):
            hstar, rev = confirm_fold(sub, R[sub], h0)
            extra = f"h*={hstar:.1f} {'(reversed: FOLD)' if rev else '(no reversal)'}"
        elif "BOUNDARY" in c['mech']:
            fi = c['first_invalid'][0] if c['first_invalid'] else None
            extra = f"valid->{fi:.1f}, alg->{c['solver_stop']:.1f}"
        print(f"{str(sub):16s} {tag:26s} {c['mech']:40s} {extra:>14}")

    # layered-existence example
    print("\nLayered existence (example (1,2,3,10,14)):")
    c = classify((1,2,3,10,14), R[(1,2,3,10,14)])
    print(f"   census-valid figure until h≈{c['first_invalid'][0]:.1f}  >  "
          f"algebraic root until h≈{c['solver_stop']:.1f}   (gap = {c['first_invalid'][0]-c['solver_stop']:.1f} deg)")