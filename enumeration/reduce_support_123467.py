"""
reduce_support_123467.py — Route A: conservative DEGREE-BOX / permanent upper bound on the
{1,2,3,4,6,7} reduced MV over 6 base DOF (no coefficient expansion, no backend). This is the
BOUNDING-BOX MV (coarser than true Newton-polytope support MV, which is Route B2).

Why: the full 50-var lift overflowed the polyhedral MV backend (Int32, ~7.5e14 intermediate).
Reduce to 6 base angles by propagating SUPPORTS/DEGREES through the triangular node chain.

Method (conservative, support-only):
 - each base angle X contributes degree 1 via its (s_X,c_X) atoms.
 - sin/cos of a sum has degree = sum of constituent degrees (product of trig factors).
 - a node N with tan(N)=num/den (linear in its own (S,C)) is, after clearing the denominator
   and resolving the degree-2 cover norm sqrt(num^2+den^2), of degree <= deg(num)+deg(den) in
   each base angle -> deg(N)[v] = deg_v(num) + deg_v(den)  (OVER-approximation; safe).
 - acos node: deg(N)[v] = deg_v(cos_expr).
 - the 6 constraints' degree vectors over the 6 base angles form a 6x6 matrix D.
 - mixed volume of the axis-parallel bounding boxes = permanent(D) >= true reduced MV.
   (Over-approx supports => larger Newton polytopes => MV upper bound. Tractable bound =>
   tractable truth. This is a CONSERVATIVE bound, NOT the exact reduced MV.)

No infeasibility claim.
"""
import sys, os, math, json, itertools
_here = os.path.dirname(os.path.abspath(__file__))
_root = _here
while _root != os.path.dirname(_root):
    if os.path.exists(os.path.join(_root, "sriyantra.py")):
        break
    _root = os.path.dirname(_root)
for _p in (_here, _root, os.path.join(_root, "enumeration")):
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)
import sympy as sp
import polynomialize_probe_123467 as P

BASE=['b','c','d','e','g','h']

def deg_in_angle(expr, v, node_deg):
    """Conservative degree of expr in base angle v. node atoms contribute node_deg[node][v]."""
    s_v=sp.Symbol('s_'+v); c_v=sp.Symbol('c_'+v)
    expr=sp.expand(expr)
    terms=expr.as_ordered_terms() if expr.is_Add else [expr]
    best=0
    for t in terms:
        d=0
        for fac, p in t.as_powers_dict().items():
            nm=getattr(fac,'name',None)
            if nm in ('s_'+v,'c_'+v): d+=int(p)
            elif nm and (nm.startswith('S_') or nm.startswith('C_')):
                node=nm[2:]; d+=int(p)*node_deg.get(node,{}).get(v,0)
        best=max(best,d)
    return best

def build_degree_matrix():
    L=P.build_lift()
    # extract num/den per node-defining eq, propagate degrees in dependency order
    node_deg={}
    order=[t[4:] for t in L.eq_tags if t.startswith('def_')]
    defeq={t[4:]:eq for t,eq in zip(L.eq_tags,L.eqs) if t.startswith('def_')}
    for nm in order:
        eq=defeq[nm]; S=sp.Symbol('S_'+nm); C=sp.Symbol('C_'+nm)
        p=sp.Poly(eq,S,C)
        if p.total_degree()!=1: raise RuntimeError('node %s not linear'%nm)
        den=eq.coeff(S,1)
        node_deg[nm]={}
        if den==0:
            # acos node: eq = coeffC*C + rest  ->  C = -rest/coeffC ; deg = deg(rest)+deg(coeffC)
            coeffC=eq.coeff(C,1); rest=sp.expand(eq - coeffC*C)
            for v in BASE:
                node_deg[nm][v]=deg_in_angle(rest,v,node_deg)+deg_in_angle(coeffC,v,node_deg)
        else:
            # atan node: eq = den*S - num*C ; node value ~ num/sqrt(num^2+den^2), clear den
            num=-eq.coeff(C,1)
            for v in BASE:
                dv_num=deg_in_angle(num,v,node_deg) if num!=0 else 0
                dv_den=deg_in_angle(den,v,node_deg) if den!=0 else 0
                node_deg[nm][v]= dv_num + dv_den
    # constraints
    con_tags=['F1','F2','F3','F4','F6','F7']
    D=[]; supports={}
    for tag in con_tags:
        eq=[e for t,e in zip(L.eq_tags,L.eqs) if t==tag][0]
        row=[deg_in_angle(eq,v,node_deg) for v in BASE]
        D.append(row); supports[tag]=dict(zip(BASE,row))
    return L, node_deg, con_tags, D

def permanent(M):
    n=len(M); idx=range(n); total=0
    for perm in itertools.permutations(idx):
        prod=1
        for i in range(n): prod*=M[i][perm[i]]
        total+=prod
    return total

def total_degree_bound(D):
    prod=1
    for row in D: prod*=max(sum(row),1)
    return prod

if __name__=='__main__':
    L,node_deg,con_tags,D=build_degree_matrix()
    print("=== Route A: support-only reduction to 6 base DOF (CONSERVATIVE) ===")
    print("base angles:", BASE)
    print()
    print("node degree propagation (conservative deg per base angle), deepest nodes:")
    for nm in ['U12','x11a','x18','x19','x13','U7']:
        print("  %-5s : %s"%(nm, node_deg[nm]))
    print()
    print("reduced constraint degree matrix D (rows=constraints, cols=base angles):")
    print("        "+"  ".join("%3s"%v for v in BASE))
    for tag,row in zip(con_tags,D):
        print("  %-4s  "%tag+"  ".join("%3d"%x for x in row))
    perm=permanent(D); td=total_degree_bound(D)
    print()
    print("CONSERVATIVE mixed-volume upper bound = permanent(D) = %s  (= %.3e)"%(f"{perm:,}",perm))
    print("total-degree (sum per row) bound        = %.3e"%td)
    print()
    print("Interpretation: permanent(D) is an UPPER BOUND on the true reduced mixed volume")
    print("(boxes over-approximate Newton polytopes). Tractable bound => tractable truth.")
    print("It is NOT the exact reduced MV. NO infeasibility claim.")
    summary=dict(
        schema="reduce_support_v1", subset=[1,2,3,4,6,7],
        n_base_variables=6, base_angles=BASE,
        reduced_degree_matrix={t:dict(zip(BASE,r)) for t,r in zip(con_tags,D)},
        max_degree_per_constraint={t:max(r) for t,r in zip(con_tags,D)},
        support_total_degree_per_constraint={t:sum(r) for t,r in zip(con_tags,D)},
        conservative_mixed_volume_upper_bound=int(perm),
        total_degree_bound=int(td),
        exactness="CONSERVATIVE upper bound (support over-approximation; degree-2 cover norm and "
                  "cleared denominators counted additively; NOT exact reduced MV)",
        full_lift_backend="BACKEND_OVERFLOW (Int32, intermediate ~7.5e14) on 50-var system",
        claim="NONE (no infeasibility)",
    )
    json.dump(summary, open('docs/reduce_support_123467.json','w'),indent=2)
    print("\nsummary -> reduce_support_123467.json")

    # ---- Route B1 artifact: full 50-var Newton supports for a portable/exact MV backend ----
    varlist=[v.name for v in L.vars]
    sup=[]
    for eq in L.eqs:
        p=sp.Poly(sp.expand(eq), *L.vars)
        sup.append([list(m) for m in p.monoms()])
    b1=dict(
        schema="lift_supports_v1", subset=[1,2,3,4,6,7],
        variables=varlist, n_vars=len(varlist), n_eqs=len(sup),
        total_monomials=sum(len(s) for s in sup),
        supports=sup,
        note="Newton-polytope supports (exponent vectors per equation) for a portable/exact "
             "mixed-volume backend (Route B1). Feed to phcpy / 64-bit MixedSubdivisions / any MV "
             "tool. The full-lift HomotopyContinuation.jl run OVERFLOWED Int32 (intermediate "
             "~7.5e14); these supports let an exact/64-bit backend compute the true mixed volume "
             "independent of that limitation.",
    )
    json.dump(b1, open('lift/lift_123467_supports.json','w'))
    print("Route B1 supports -> lift_123467_supports.json (%d eqs, %d vars, %d monomials)"
          %(len(sup),len(varlist),b1['total_monomials']))