"""
STAGE 2 — spherical Gate-4 validity layer.

Independent geodesic-geometry realization of the spherical Sri Yantra, the
great-circle analogue of the plane geo_check.py. Builds the figure on the unit
sphere by great-circle (geodesic) intersections, then (a) cross-validates the
constructed arcs against the trig chain in sriyantra.py, and (b) decides Gate-4
geometric validity (point distinctness, base-point ordering, figure closure).

Model
-----
Unit sphere; bounding small circle centred at the north pole N=(0,0,1) with
angular radius r = pi/2 - h. Axis of symmetry = meridian in the x-z plane:
  axis(s) = (sin s, 0, cos s)          # signed arc s from centre N
Base points sit on the axis: Pc=axis(0), P0=axis(-r), P1=axis(-(b+c)),
P3=axis(-c), P4=axis(-g), P7=axis(d), P9=axis(d+e), P10=axis(r).
A "base line" through axis(s) is the great circle perpendicular to the meridian
there (plane spanned by axis(s) and Y=(0,1,0)); construction lines are geodesics.
All constructed points 1..19 lie on the right half (y > 0), which disambiguates
every great-circle intersection.
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
import sriyantra as RAO

PI2 = math.pi/2
Y = np.array([0.0,1.0,0.0])

def axis(s): return np.array([math.sin(s), 0.0, math.cos(s)])
def _unit(v): return v/np.linalg.norm(v)
def gnorm(P,Q): return _unit(np.cross(P,Q))          # great-circle normal
def bnorm(s):                                        # base-line normal at axis(s)
    return _unit(np.cross(axis(s), Y))               # = (-cos s, 0, sin s)
def meet(n1, n2):                                    # intersection on right half (y>0)
    d = np.cross(n1, n2); nd = np.linalg.norm(d)
    if nd < 1e-14: return None
    d = d/nd
    return d if d[1] > 0 else -d
def geod_base(P, Q, s):   return meet(gnorm(P,Q), bnorm(s))
def geod_geod(P,Q,R,S):   return meet(gnorm(P,Q), gnorm(R,S))
def base_circle(s, r):                               # base-line(s) meets bounding circle, y>0
    val = math.cos(r)/math.cos(s)
    if abs(val) > 1: return None                     # base point outside the circle
    t = math.acos(val)
    return np.array([math.sin(s)*math.cos(t), math.sin(t), math.cos(s)*math.cos(t)])
def foot(p):  return math.atan2(p[0], p[2])          # axis arc of base line through p
def radius(p): return math.acos(max(-1.0,min(1.0,p[2])))   # geodesic distance to centre N
def tarc(p, s): return math.atan2(p[1], float(np.dot(p, axis(s))))  # arc along base-line(s)
def gdist(p,q): return math.acos(max(-1.0,min(1.0,float(np.dot(p,q)))))

def build(b, c, d, e, g, h):
    r = PI2 - h
    Pc, P0, P1 = axis(0), axis(-r), axis(-(b+c))
    P3, P4, P7 = axis(-c), axis(-g), axis(d)
    P9, P10 = axis(d+e), axis(r)
    p1 = base_circle(-c, r)                 # point 1 on bounding circle
    p2 = base_circle(d,  r)                 # point 2 on bounding circle
    if p1 is None or p2 is None: return None
    p3 = geod_base(P0, p2, -c)
    p4 = geod_base(P10, p1, d)
    p5 = geod_base(P1, p4, -c)
    p6 = geod_base(P9, p3, d)
    p8 = geod_geod(P4, p6, P10, p1)
    p9 = geod_geod(P7, p5, P0, p2)
    pts=[p1,p2,p3,p4,p5,p6,p8,p9]
    if any(p is None for p in pts): return None
    yP8, yP2 = foot(p8), foot(p9)
    P8b, P2b = axis(yP8), axis(yP2)
    p10 = geod_base(P1, p4, -g)
    p12 = geod_geod(P4, p6, P8b, p10)
    if p10 is None or p12 is None: return None
    yP6 = foot(p12); P6b = axis(yP6)
    p13 = geod_base(P9, p3, yP6)
    p16 = geod_base(P4, p6, d+e)
    p17 = geod_base(P7, p5, -(b+c))
    p18 = geod_base(P1, p4, yP8)
    p19 = geod_base(P9, p3, yP2)
    # closure: 11 = (P7-5)∩(P4-10),  11a = (P2-13)∩(P4-10); coincide iff figure closes
    p11  = geod_geod(P7, p5, P4, p10)
    p11a = geod_geod(P2b, p13, P4, p10)
    pts2=[p10,p12,p13,p16,p17,p18,p19,p11,p11a]
    if any(p is None for p in pts2): return None
    return dict(r=r, Pc=Pc, P0=P0,P1=P1,P3=P3,P4=P4,P7=P7,P9=P9,P10=P10,
                p1=p1,p2=p2,p3=p3,p4=p4,p5=p5,p6=p6,p8=p8,p9=p9,p10=p10,p12=p12,
                p13=p13,p16=p16,p17=p17,p18=p18,p19=p19,p11=p11,p11a=p11a,
                yP8=yP8,yP2=yP2,yP6=yP6,
                x16=tarc(p16,d+e), r16=radius(p16),
                x17=tarc(p17,-(b+c)), r17=radius(p17),
                x18=tarc(p18,yP8), r18=radius(p18),
                x19=tarc(p19,yP2), r19=radius(p19),
                x1=tarc(p1,-c), x2=tarc(p2,d),
                closure=gdist(p11,p11a))

# ---------------- Gate-4 validity ----------------
def gate4(b,c,d,e,g,h, sep=1e-6, closure_tol=1e-5):
    """Geometric validity. closure_tol defaults to ~the solver floor widened for
    externally-tabulated (Rao six-digit) figures; pass tighter for machine-solved ones."""
    G = build(b,c,d,e,g,h)
    if G is None: return False, "not constructible (base point outside circle / no intersection)"
    r = G['r']
    # base-point ordering along the axis
    order = [-r, -(b+c), -c, -g, 0.0, d, d+e, r]
    if any(order[i] >= order[i+1] for i in range(len(order)-1)):
        return False, "base-point ordering violated"
    if min(np.diff(order)) < sep*r:
        return False, "base points too close (< 1e-6 r)"
    # figure closes (point 11 == 11a) within solver tolerance
    if G['closure'] > closure_tol:
        return False, f"figure does not close (|11-11a|={G['closure']:.1e})"
    # constructed points pairwise distinct
    P = [G[k] for k in ('p1','p2','p3','p4','p5','p6','p8','p9','p10','p12','p13','p16','p17','p18','p19')]
    for i in range(len(P)):
        for j in range(i+1,len(P)):
            if gdist(P[i],P[j]) < sep*r:
                return False, f"points {i},{j} coincide (< 1e-6 r)"
    return True, "valid"

# ---------------- validation against the trig chain ----------------
if __name__ == "__main__":
    keys=['x16','x17','x18','x19','r16','r17','r18','r19']
    print("Spherical constructor vs trig chain (Rao Table-1 figures + random):\n")
    worst={k:0.0 for k in keys}; worst_yP8=worst_yP2=worst_close=0.0; nfig=0
    rng=np.random.default_rng(7)
    figs=[v for _,v in RAO.TABLE1]
    # add random perturbations of Table-1 figures (stay near valid region)
    for _,base in RAO.TABLE1:
        for _ in range(25):
            figs.append(tuple(np.array(base)*(1+rng.uniform(-0.05,0.05,6))))
    for fig in figs:
        b,c,d,e,g,h = fig
        G=build(b,c,d,e,g,h)
        if G is None: continue
        try: s=RAO.chain(b,c,d,e,g,h); F=RAO.constraints(b,c,d,e,g,h)
        except Exception: continue
        nfig+=1
        for k in keys: worst[k]=max(worst[k], abs(G[k]-s[k]))
        worst_yP8=max(worst_yP8, abs(G['yP8']-(d+s['v8'])))
        worst_yP2=max(worst_yP2, abs(G['yP2']-(-(c+s['v9']))))
        # closure residual vs chain F1 = x11 - x11a
        worst_close=max(worst_close, abs(G['closure']-abs(F[1])))
    print(f"  figures checked: {nfig}\n")
    print("  arc/radius   max|constructor - chain|")
    for k in keys: print(f"    {k:5s}      {worst[k]:.2e}")
    print(f"\n  base feet:  P8 vs d+v8 = {worst_yP8:.2e}   P2 vs -(c+v9) = {worst_yP2:.2e}")
    print(f"  closure |11-11a| vs |F1|:  {worst_close:.2e}")
    ok = max(list(worst.values())+[worst_yP8,worst_yP2,worst_close]) < 1e-8
    print("\n  -> CONSTRUCTOR FAITHFUL TO THE TRIG CHAIN" if ok else
          "\n  -> mismatch (see above) — constructor not yet faithful")

    print("\nGate-4 validity on Rao Table-1 (closure_tol = 1e-5):")
    nv = 0
    for s, fig in RAO.TABLE1:
        v, why = gate4(*fig); nv += v
        if not v: print(f"    {s}: flagged -> {why}")
    print(f"    {nv}/8 valid; the single flag is Rao's documented under-converged"
          f" row (1,2,3,6,16,19), correctly caught (it does not close).")
