"""
Independent coordinate-geometry construction of the plane Sri Yantra.
Builds the figure by straight-line intersections (NO trig recursion),
then compares x16..x19, r16..r19 and base-point heights to the validated
chain in sriyantra_plane.  Grounds the 5 table-untested constraints:
  F7 = x18 - x19,  F12 = x16 - x17,  F17 = r18 - r19,
  F18 = r16 - r18, F11 = (P9P6) - (P6P2)  [intercepts equal].

Axis of symmetry = y-axis, centre Pc=(0,0), circumradius r.
Directly-defined base points (heights on the axis from the intercepts):
  Pc=0, P0=-r, P1=-(b+c), P3=-c, P4=-g, P7=+d, P9=+(d+e), P10=+r.
Everything else (points 1..19 and base points P2,P5,P6,P8) is found by
intersecting the actual construction lines.
"""
import math
import numpy as np
import sriyantra_plane as SP

def iy(P, Q, y):
    """Point on line P->Q at given height y."""
    (x1,y1),(x2,y2) = P,Q
    t = (y - y1)/(y2 - y1)
    return (x1 + t*(x2 - x1), y)

def ii(P, Q, R, S):
    """Intersection of line P-Q with line R-S."""
    (x1,y1),(x2,y2) = P,Q; (x3,y3),(x4,y4) = R,S
    den = (x1-x2)*(y3-y4) - (y1-y2)*(x3-x4)
    px = ((x1*y2-y1*x2)*(x3-x4) - (x1-x2)*(x3*y4-y3*x4))/den
    py = ((x1*y2-y1*x2)*(y3-y4) - (y1-y2)*(x3*y4-y3*x4))/den
    return (px, py)

def build(b, c, d, e, g, r=1.0):
    Pc=(0,0); P0=(0,-r); P1=(0,-(b+c)); P3=(0,-c); P4=(0,-g)
    P7=(0,d); P9=(0,d+e); P10=(0,r)
    p1 = (math.sqrt(r*r-c*c), -c)        # base line P3 ∩ circle
    p2 = (math.sqrt(r*r-d*d),  d)        # base line P7 ∩ circle
    p3 = iy(P0, p2, -c)                  # transverse P0-2 ∩ baseline(P3)
    p4 = iy(P10, p1, d)                  # transverse P10-1 ∩ baseline(P7)
    p5 = iy(P1, p4, -c)                  # transverse P1-4 ∩ baseline(P3)
    p6 = iy(P9, p3, d)                   # transverse P9-3 ∩ baseline(P7)
    p8 = ii(P4, p6, P10, p1)             # transverse P4-6 ∩ transverse P10-1
    p9 = ii(P7, p5, P0, p2)              # transverse P7-5 ∩ transverse P0-2
    yP8 = p8[1]; yP2 = p9[1]             # base points P8, P2 = feet of pts 8, 9
    p10 = iy(P1, p4, -g)                 # baseline(P4) extended ∩ transverse P1-4
    p12 = ii(P4, p6, (0,yP8), p10)       # transverse P4-6 ∩ transverse P8-10
    yP6 = p12[1]                         # base point P6 = foot of pt 12
    # the four points behind the untested constraints
    p16 = iy(P4, p6, d+e)                # baseline(P9) ∩ transverse P4-6 extended
    p17 = iy(P7, p5, -(b+c))             # baseline(P1) ∩ transverse P7-5 extended
    p18 = iy(P1, p4, yP8)                # baseline(P8) ∩ transverse P1-4 produced
    p19 = iy(P9, p3, yP2)                # baseline(P2) ∩ transverse P9-3
    return dict(
        x16=p16[0], r16=math.hypot(*p16),
        x17=p17[0], r17=math.hypot(*p17),
        x18=p18[0], r18=math.hypot(*p18),
        x19=p19[0], r19=math.hypot(*p19),
        yP8=yP8, yP2=yP2, yP6=yP6,
        P9P6=(d+e)-yP6, P6P2=yP6-yP2,
    )

if __name__ == "__main__":
    rng = np.random.default_rng(7)
    print("Coordinate construction vs trig chain (max over 200 random figures).\n")
    keys = ['x16','x17','x18','x19','r16','r17','r18','r19']
    worst = {k:0.0 for k in keys}
    worst_yP8=worst_yP2=0.0
    f11_ratios=[]
    n=0
    while n < 200:
        b=rng.uniform(0.35,0.55); c=rng.uniform(0.18,0.30); d=rng.uniform(0.24,0.33)
        e=rng.uniform(0.40,0.52); g=rng.uniform(0.08,0.13)
        try:
            G = build(b,c,d,e,g); s = SP.chain(b,c,d,e,g); F = SP.constraints(b,c,d,e,g)
        except Exception:
            continue
        n+=1
        for k in keys:
            worst[k] = max(worst[k], abs(G[k]-s[k]))
        # base heights: chain reads P8 at d+v8, P2 at -(c+v9)
        worst_yP8 = max(worst_yP8, abs(G['yP8'] - (d+s['v8'])))
        worst_yP2 = max(worst_yP2, abs(G['yP2'] - (-(c+s['v9']))))
        # does F11 measure (P9P6 - P6P2)?
        geo = G['P9P6'] - G['P6P2']
        if abs(geo) > 1e-9: f11_ratios.append(F[11]/geo)

    print("  quantity   max|coord - chain|")
    for k in keys:
        print(f"    {k:4s}      {worst[k]:.2e}")
    print(f"\n  base-point heights (independent line-intersection vs chain):")
    print(f"    P8 height vs (d+v8):   {worst_yP8:.2e}   -> confirms r18 uses d+v8 (y8==v8)")
    print(f"    P2 height vs -(c+v9):  {worst_yP2:.2e}   -> confirms r19 uses c+v9 (y9==v9)")
    r = np.array(f11_ratios)
    print(f"\n  F11 / (geometric P9P6 - P6P2):  mean={r.mean():+.6f}  std={r.std():.2e}")
    print("    (constant ratio => F11 faithfully encodes 'intercepts P9P6, P6P2 equal')")
