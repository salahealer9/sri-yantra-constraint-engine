"""
Route-3 probe: real-box completeness for subset {1,2,3,4,8} via rigorous
interval branch-and-prune.

The research question is "how many real admissible Sri Yantra figures" -- real
solutions of {F1,F2,F3,F4,F8}=0 in a bounded (b,c,d,e,g) box, NOT all complex
solutions. Interval methods certify ALL real roots in a box and scale with the
number of real roots + box geometry, not the complex BKK (which is 286,144).

This probe uses mpmath.iv (rigorous directed rounding) and the engine's own
real constraint functions (rational + sqrt; F2 via the w=sqrt(x7^2+V7^2) form,
so no transcendentals). It measures whether exclusion-based branch-and-prune
CONVERGES over the box or whether the frontier explodes from interval
overestimation. A naive exclusion test is a LOWER bound on what is achievable:
if it converges, route 3 is clearly viable (Krawczyk contraction / Julia's
IntervalRootFinding.jl only do better). If it explodes, the next step is a
contracting interval-Newton, not a verdict.
"""
import mpmath, time, os, sys
from mpmath import iv
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sriyantra_plane as SP
iv.dps = 15
ONE = iv.mpf(1)
HALF3 = iv.mpf(3)/2

def cons_iv(b, c, d, e, g):
    """The five {1,2,3,4,8} constraints in interval arithmetic (r=1)."""
    x1 = iv.sqrt(ONE - c*c)
    x2 = iv.sqrt(ONE - d*d)
    x3 = (ONE-c)/(ONE+d) * x2
    x4 = (ONE-d)/(ONE+c) * x1
    x5 = b/(b+c+d) * x4
    x6 = e/(c+d+e) * x3
    Q7 = (d+g)/(c+d) * (x5/x6); U7 = (d+g)/(Q7+ONE); V7 = (d+g) - U7
    x7 = U7/(c+d) * x5
    w  = iv.sqrt(x7*x7 + V7*V7)
    rT = x7*(w - x7)/V7
    Q8 = (d+g)/(ONE+c) * (x1/x6); U8 = (ONE+g)/(Q8+ONE); V8 = (ONE+g) - U8
    v8 = ONE - U8 - d
    x16 = (d+e+g)/(d+g) * x6
    x11 = (d+g)/(c+d) * x5
    Q9 = (c+d)/(ONE+d) * (x2/x5); U9 = (ONE+d)/(Q9+ONE); v9 = ONE - U9 - c
    x10 = (b+c-g)/(b+c+d) * x4
    S12 = d+g+v8; Q12 = S12/(d+g) * (x6/x10); U12 = S12/(Q12+ONE); v12 = d+g - U12
    x13 = (e+v12)/(c+d+e) * x3
    x11a = (v9+c-g)/(v9+c+d-v12) * x13
    r16 = iv.sqrt((d+e)*(d+e) + x16*x16)
    F1 = x11 - x11a
    F2 = d - U7 - rT
    F3 = -(V8*V8)/2 + HALF3*x10*x10
    F4 = -((c+d+v9-v12)**2)/2 + HALF3*x13*x13
    F8 = ONE - r16
    return [F1, F2, F3, F4, F8]

def contains0(I): return (I.a <= 0) and (0 <= I.b)
def boxiv(box): return [iv.mpf([lo, hi]) for (lo, hi) in box]

# ---- validation: interval at the Rao solution must bracket the float engine ----
def validate():
    bv,cv,dv,ev,gv = 0.463752,0.223255,0.288990,0.488181,0.106157
    h = 1e-9
    box = [(v-h, v+h) for v in (bv,cv,dv,ev,gv)]
    Fi = cons_iv(*boxiv(box))
    Fe = SP.constraints(bv,cv,dv,ev,gv)
    print("validation (thin box at Rao {1,2,3,4,8}; interval must bracket engine):")
    ok = True
    for i,k in enumerate((1,2,3,4,8)):
        lo,hi = float(Fi[i].a), float(Fi[i].b)
        br = lo <= Fe[k] <= hi
        ok &= br
        print(f"   F{k}: engine={Fe[k]:+.3e}  interval=[{lo:+.3e},{hi:+.3e}]  brackets={br}")
    print(f"   all bracketed: {ok}")
    return ok

# ---- exclusion + bisection branch-and-prune (boxes are float (lo,hi) tuples) ----
def prune(box0, tol=1.5e-2, ctol=5e-2, max_boxes=2000000, time_limit=240.0):
    t0 = time.time()
    stack = [box0]
    processed = pruned = nsol = 0
    clusters = []                          # incremental distinct solution regions
    maxq = 1
    while stack:
        if processed >= max_boxes or time.time()-t0 > time_limit:
            break
        maxq = max(maxq, len(stack))
        box = stack.pop()
        processed += 1
        try:
            F = cons_iv(*boxiv(box))
        except Exception:
            F = None                       # interval div by zero etc.: cannot prune
        if F is not None and any(not contains0(I) for I in F):
            pruned += 1
            continue
        widths = [hi-lo for (lo,hi) in box]
        wmax = max(widths)
        if wmax < tol:
            nsol += 1
            m = [(lo+hi)/2 for (lo,hi) in box]
            if not any(max(abs(m[i]-r[i]) for i in range(5)) < ctol for r in clusters):
                clusters.append(m)
            continue
        k = widths.index(wmax)
        lo,hi = box[k]; mid = (lo+hi)/2
        left = list(box);  left[k]  = (lo, mid)
        right = list(box); right[k] = (mid, hi)
        stack.append(left); stack.append(right)
    return dict(processed=processed, pruned=pruned, nsol=nsol, clusters=clusters,
                remaining=len(stack), maxq=maxq, secs=time.time()-t0,
                finished=(len(stack)==0))

if __name__ == "__main__":
    print("="*68); print("ROUTE-3 PROBE — interval branch-and-prune, subset {1,2,3,4,8}")
    print("="*68)
    if not validate():
        print("VALIDATION FAILED — interval chain does not bracket engine."); raise SystemExit
    # admissible search box (contains Rao's solution; illustrative of Rao-range+50%)
    box0 = [(0.20, 0.80),   # b
            (0.10, 0.45),   # c
            (0.15, 0.45),   # d
            (0.25, 0.75),   # e
            (0.03, 0.25)]   # g
    print(f"\nsearch box: b[0.20,0.80] c[0.10,0.45] d[0.15,0.45] e[0.25,0.75] g[0.03,0.25]")
    print("running exclusion+bisection (naive; lower bound on achievable)...\n")
    st = prune(box0, tol=1.5e-2, ctol=5e-2, max_boxes=2000000, time_limit=240.0)
    print(f"  boxes processed : {st['processed']}")
    print(f"  pruned (no root): {st['pruned']}  ({100*st['pruned']/max(st['processed'],1):.1f}%)")
    print(f"  solution-boxes  : {st['nsol']}  (width < tol; a fat cloud without contraction)")
    print(f"  distinct regions: {len(st['clusters'])}  (merged within {0.05})")
    print(f"  queue remaining : {st['remaining']}   max queue : {st['maxq']}")
    print(f"  wall time       : {st['secs']:.1f}s   finished: {st['finished']}")
    for r in st['clusters']:
        near = max(abs(r[i]-v) for i,v in enumerate((0.463752,0.223255,0.288990,0.488181,0.106157)))
        tag = "  <- Rao {1,2,3,4,8}" if near < 0.05 else ""
        print("     region (b,c,d,e,g) ~ (" + ", ".join(f"{v:.4f}" for v in r) + ")" + tag)
    print("\nVERDICT:")
    if st['finished']:
        print(f"  CONVERGED — frontier emptied; {len(st['clusters'])} distinct real solution region(s).")
        print("  Route 3 viable. Naive exclusion leaves a fat cloud per root; a")
        print("  Krawczyk/interval-Newton contraction (IntervalRootFinding.jl)")
        print("  collapses each to a single CERTIFIED root and is far faster.")
    elif st['maxq'] < 100:
        print(f"  WELL-BEHAVED but capped — max queue {st['maxq']} (no breadth explosion),")
        print(f"  {len(st['clusters'])} distinct region(s) so far. Finite tree; the naive")
        print("  Python rate is the only limit. Production tool: IntervalRootFinding.jl.")
    else:
        print("  EXPLODING — queue outgrows budget; needs contraction before a verdict.")
