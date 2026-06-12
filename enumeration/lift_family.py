"""
Tier-2 FAMILY lifting: coefficient-parameter homotopy design for the full
plane enumeration campaign ({1,2} + 3 of 18, C(18,3) = 816 subsets).

DEV-BRANCH / PRE-CONFIRMATORY tooling. Not part of any registered run.

Design
------
All 816 subsets share the identical chain + F1 + F2. Only the 3 remaining
constraints vary, and each is a polynomial drawn from a pool of 18. So the
campaign is ONE parameterized family per degree type:

    chain (28 eqs) + F1 + F2 + slot_1 + slot_2 + slot_3 = 33 eqs, 33 vars

where slot_i = sum_k a_ik * P_k(x) is a GENERIC linear combination over the
pool of the slot's degree class (9 linear, 9 quadratic constraints), and each
concrete subset is the parameter point with 0/1 coefficients.

Per degree type (#linear,#quad) in {(3,0),(2,1),(1,2),(0,3)}:
  1. monodromy_solve on generic parameters p0  ->  N* generic solutions
  2. verify_solution_completeness (trace test) ->  completeness certificate
  3. parameter homotopy p0 -> each subset      ->  N* paths per subset
versus mixed_volume = 286,144 paths per subset ab initio.

Extensions over lift_poc.py (subset {1,2,3,4,8}):
  - chain extended by x17, x18, x19 and the (Q20,U20), (Q21,U21) pairs
    (7 new auxiliaries) so all 18 constraints become polynomial: 33 vars.
  - radial constraints in SQUARED form: F8 = r16^2-1, F16 = r16^2-r17^2, ...
    These need NO new sqrt auxiliaries: r16^2 = (d+e)^2+x16^2 is already a
    polynomial in chain variables, and over the reals r_a^2 = r_b^2 with
    r_a,r_b >= 0 is exactly r_a = r_b. No spurious branches introduced.

This file:
  (1) builds the 33-var master system and the 18-polynomial pool in SymPy;
  (2) validates EXACT equivalence to the frozen engine:
      (2a) chain identities ~1e-15 at random valid figures,
      (2b) each pool polynomial equals factor * engine_F at Rao's Table 3
           rows, the plane optimum, and random points (machine precision),
      (2c) full system vanishes at each Table 3 solution with its own
           subset's parameter vector;
  (3) enumerates the 816 targets, classifies by degree type, flags the one
      degenerate triple {8,9,16} (plane_deps.py);
  (4) emits family_solve.jl: monodromy + trace test + 816-target sweep with
      per-subset JSONL logging and the prereg path-failure downgrade rule.
"""
import sympy as sp
import math, random, os, sys, json, itertools
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sriyantra_plane as SP

# ======================================================================
#  symbols: 5 original + 28 auxiliary = 33
# ======================================================================
b,c,d,e,g = sp.symbols('b c d e g', real=True)
(x1,x2,x3,x4,x5,x6,x7,x10,x11,x13,x16,x17,x18,x19,
 U7,U8,U9,U12,U20,U21,Q7,Q8,Q9,Q12,Q20,Q21,x11a,w) = sp.symbols(
 'x1 x2 x3 x4 x5 x6 x7 x10 x11 x13 x16 x17 x18 x19 '
 'U7 U8 U9 U12 U20 U21 Q7 Q8 Q9 Q12 Q20 Q21 x11a w', real=True)

orig_vars = [b,c,d,e,g]
aux_vars  = [x1,x2,x3,x4,x5,x6,x7,x10,x11,x13,x16,x17,x18,x19,
             U7,U8,U9,U12,U20,U21,Q7,Q8,Q9,Q12,Q20,Q21,x11a,w]
all_vars  = orig_vars + aux_vars          # 33

# inline linear combos (never given their own variable)
V7  = d + g - U7
V8  = (1 + g) - U8        # = S8 - U8 = d+g+v8
v8  = 1 - U8 - d
v9  = 1 - U9 - c
v12 = d + g - U12
S12 = g + 1 - U8          # = d+g+v8

# ======================================================================
#  chain equations (28; each = 0). First 21 identical to lift_poc.py.
# ======================================================================
chain_eqs = {
 'x1' : x1**2 - (1 - c**2),
 'x2' : x2**2 - (1 - d**2),
 'x3' : (1 + d)*x3 - (1 - c)*x2,
 'x4' : (1 + c)*x4 - (1 - d)*x1,
 'x5' : (b + c + d)*x5 - b*x4,
 'x6' : (c + d + e)*x6 - e*x3,
 'Q7' : (c + d)*x6*Q7 - (d + g)*x5,
 'U7' : (Q7 + 1)*U7 - (d + g),
 'x7' : (c + d)*x7 - U7*x5,
 'Q8' : (1 + c)*x6*Q8 - (d + g)*x1,
 'U8' : (Q8 + 1)*U8 - (1 + g),
 'x16': (d + g)*x16 - (d + e + g)*x6,
 'x11': (c + d)*x11 - (d + g)*x5,
 'x10': (b + c + d)*x10 - (b + c - g)*x4,
 'Q9' : (1 + d)*x5*Q9 - (c + d)*x2,
 'U9' : (Q9 + 1)*U9 - (1 + d),
 'Q12': (d + g)*x10*Q12 - S12*x6,
 'U12': (Q12 + 1)*U12 - S12,
 'x13': (c + d + e)*x13 - (e + d + g - U12)*x3,
 'x11a': (1 - U9 - g + U12)*x11a - (1 - U9 - g)*x13,
 'w'  : w**2 - (x7**2 + V7**2),
 # ---- new chain steps for the full pool ----
 'x17': (c + d)*x17 - (b + c + d)*x5,                       # (2.24)
 'x18': (b + c + d)*x18 - (b + c + 1 - U8)*x4,              # (2.33), b+c+d+v8
 'x19': (c + d + e)*x19 - (d + e + 1 - U9)*x3,              # c+d+e+v9
 'Q20': S12*x13*Q20 - (1 - U9 - g + U12)*x10,               # (c+d+v9-v12)/(d+g+v8)
 'U20': (Q20 + 1)*U20 - (2 - U8 - U9),                      # S20 = c+d+v8+v9
 'Q21': (d + e + 1 - U9)*x18*Q21 - (b + c + 1 - U8)*x19,    # corrected (3.14b)
 'U21': (Q21 + 1)*U21 - (b + c + d + e),                    # S21 = b+c+d+e
}

essential_eqs = {
 'F1': x11 - x11a,                         # = engine_F1
 'F2': (d - U7)*V7 - x7*w + x7**2,         # = V7 * engine_F2
}

# ======================================================================
#  the 18-polynomial pool, with derived engine factors
#  pool[k] = (polynomial, description-of-factor, factor-fn(engine-state))
# ======================================================================
def _r16sq(): return (d + e)**2 + x16**2
def _r17sq(): return (b + c)**2 + x17**2
def _r18sq(): return (1 - U8)**2 + x18**2      # d+v8 = 1-U8
def _r19sq(): return (1 - U9)**2 + x19**2      # c+v9 = 1-U9

pool = {
 # ---- linear class (degree 1 in master variables) ----
 5 : (x10 - x13,                              lambda s: 1.0),
 7 : (x18 - x19,                              lambda s: 1.0),
 10: (b + c - 2*g - 1 + U8,                   lambda s: 1.0),
 11: (1 - U9 - d - 2*g + 2*U12 - e,           lambda s: 1.0),
 12: (x16 - x17,                              lambda s: 1.0),
 13: (2*U7 - U20 + 1 - U8 - 2*d - g + U12,    lambda s: 2.0),
 14: (2*d + 2*g - 2*U12 - U21 + e,            lambda s: 2.0),
 15: (2*g + d + e - c - U21,                  lambda s: 2.0),
 20: (c - d,                                  lambda s: 1.0),
 # ---- quadratic class (degree 2 in master variables) ----
 3 : (3*x10**2 - V8**2,                       lambda s: 2.0),
 4 : (3*x13**2 - (1 - U9 - g + U12)**2,       lambda s: 2.0),
 6 : (3*x7**2 - V7**2,                        lambda s: 2.0),
 8 : (_r16sq() - 1,                           lambda s: -(s['r16'] + 1.0)),
 9 : (_r17sq() - 1,                           lambda s: -(s['r17'] + 1.0)),
 16: (_r16sq() - _r17sq(),                    lambda s: s['r16'] + s['r17']),
 17: (_r18sq() - _r19sq(),                    lambda s: s['r18'] + s['r19']),
 18: (_r16sq() - _r18sq(),                    lambda s: s['r16'] + s['r18']),
 19: (_r17sq() - _r19sq(),                    lambda s: s['r17'] + s['r19']),
}
LIN  = [5, 7, 10, 11, 12, 13, 14, 15, 20]
QUAD = [3, 4, 6, 8, 9, 16, 17, 18, 19]
factor_doc = {5:'1',7:'1',10:'1',11:'1',12:'1',13:'2',14:'2',15:'2',20:'1',
              3:'2',4:'2',6:'2',8:'-(r16+1)',9:'-(r17+1)',16:'r16+r17',
              17:'r18+r19',18:'r16+r18',19:'r17+r19'}

DEGENERATE = frozenset({8, 9, 16})   # plane_deps.py: the single rank-deficient triple

# cleared denominators (must be nonzero at any accepted solution)
denominators = {
 '1+d':1+d, '1+c':1+c, 'b+c+d':b+c+d, 'c+d+e':c+d+e, 'c+d':c+d, 'd+g':d+g,
 'Q7+1':Q7+1, 'Q8+1':Q8+1, 'Q9+1':Q9+1, 'Q12+1':Q12+1,
 'Q20+1':Q20+1, 'Q21+1':Q21+1,
 'V7(=d+g-U7)':d+g-U7, 'x11a_den(1-U9-g+U12)':1-U9-g+U12,
 'Q20_den(S12*x13)':S12*x13, 'Q21_den((d+e+1-U9)*x18)':(d+e+1-U9)*x18,
}
positive_vars = [x1, x2, w]

# ======================================================================
#  helper: full 33-var value dict from the frozen engine
# ======================================================================
def engine_aux(bv,cv,dv,ev,gv):
    s = SP.chain(bv,cv,dv,ev,gv)
    Q7v  = (dv+gv)/(cv+dv)*(s['x5']/s['x6'])
    Q8v  = (dv+gv)/(1+cv)*(s['x1']/s['x6'])
    Q9v  = (cv+dv)/(1+dv)*(s['x2']/s['x5'])
    Q12v = (dv+gv+s['v8'])/(dv+gv)*(s['x6']/s['x10'])
    Q20v = (cv+dv+s['v9']-s['v12'])/(dv+gv+s['v8'])*(s['x10']/s['x13'])
    Q21v = (bv+cv+dv+s['v8'])/(cv+dv+ev+s['v9'])*(s['x19']/s['x18'])
    wv   = math.sqrt(s['x7']**2 + s['V7']**2)
    return {b:bv,c:cv,d:dv,e:ev,g:gv,
            x1:s['x1'],x2:s['x2'],x3:s['x3'],x4:s['x4'],x5:s['x5'],x6:s['x6'],
            x7:s['x7'],x10:s['x10'],x11:s['x11'],x13:s['x13'],x16:s['x16'],
            x17:s['x17'],x18:s['x18'],x19:s['x19'],
            U7:s['U7'],U8:s['U8'],U9:s['U9'],U12:s['U12'],
            U20:s['U20'],U21:s['U21'],
            Q7:Q7v,Q8:Q8v,Q9:Q9v,Q12:Q12v,Q20:Q20v,Q21:Q21v,
            x11a:s['x11a'],w:wv}, s

# ======================================================================
#  target enumeration and degree-type classification
# ======================================================================
def degree_type(T):
    nl = sum(1 for k in T if k in LIN)
    return (nl, 3 - nl)        # (#linear, #quadratic)

def all_targets():
    out = []
    for T in itertools.combinations(range(3, 21), 3):
        out.append({'subset': T, 'type': degree_type(T),
                    'degenerate': set(T) >= DEGENERATE or set(T) == DEGENERATE})
    return out

# ======================================================================
#  validation
# ======================================================================
def validate():
    print("="*68)
    print("FAMILY LIFTING VALIDATION — 33-var master system, 18-poly pool")
    print("="*68)

    named = {**chain_eqs, **essential_eqs,
             **{f'F{k}': p for k, (p, _) in pool.items()}}

    # (1) polynomiality
    def is_poly(eq):
        try:
            sp.Poly(eq, *all_vars)
            return eq.free_symbols <= set(all_vars)
        except sp.PolynomialError:
            return False
    nonpoly = [k for k, eq in named.items() if not is_poly(eq)]
    print(f"\n(1) Polynomiality: all {len(named)} expressions polynomial in "
          f"the {len(all_vars)} variables: {not nonpoly}"
          + (f"  [non-poly: {nonpoly}]" if nonpoly else ""))

    lam_chain = {k: sp.lambdify(all_vars, eq, 'math') for k, eq in chain_eqs.items()}
    lam_ess   = {k: sp.lambdify(all_vars, eq, 'math') for k, eq in essential_eqs.items()}
    lam_pool  = {k: sp.lambdify(all_vars, p, 'math') for k, (p, _) in pool.items()}
    def vec(subs): return [subs[v] for v in all_vars]

    # (2a) chain identities at random valid figures
    rng = random.Random(11)
    worst_chain = 0.0
    npts = 0
    while npts < 20:
        bv=rng.uniform(0.35,0.55); cv=rng.uniform(0.18,0.30); dv=rng.uniform(0.24,0.33)
        ev=rng.uniform(0.40,0.52); gv=rng.uniform(0.08,0.13)
        try: subs,_ = engine_aux(bv,cv,dv,ev,gv)
        except Exception: continue
        npts += 1
        vv = vec(subs)
        for k, f in lam_chain.items():
            worst_chain = max(worst_chain, abs(f(*vv)))
    print(f"\n(2a) max |chain_eq| over 20 random valid figures = {worst_chain:.2e}"
          f"   (expect ~1e-15)")

    # (2b) pool polynomial == factor * engine constraint, everywhere
    print("\n(2b) Pool-polynomial equivalence  poly_Fk == factor_k * engine_Fk")
    print("     (max |residual| over Table 3 rows + plane optimum + 12 random pts):")
    test_pts = [vals for _, vals in SP.TABLE3] + [SP.PLANE_OPT]
    nrand = 0
    while nrand < 12:
        bv=rng.uniform(0.35,0.55); cv=rng.uniform(0.18,0.30); dv=rng.uniform(0.24,0.33)
        ev=rng.uniform(0.40,0.52); gv=rng.uniform(0.08,0.13)
        try:
            engine_aux(bv,cv,dv,ev,gv)
            test_pts.append((bv,cv,dv,ev,gv)); nrand += 1
        except Exception: continue
    worst_pool = {}
    for k in LIN + QUAD:
        wk = 0.0
        for pt in test_pts:
            subs, s = engine_aux(*pt)
            Fe = SP.constraints(*pt)
            fac = pool[k][1](s)
            wk = max(wk, abs(lam_pool[k](*vec(subs)) - fac*Fe[k]))
        worst_pool[k] = wk
    for k in LIN:
        print(f"       F{k:<2d} (lin , factor {factor_doc[k]:>9s}) : {worst_pool[k]:.2e}")
    for k in QUAD:
        print(f"       F{k:<2d} (quad, factor {factor_doc[k]:>9s}) : {worst_pool[k]:.2e}")
    print(f"     worst over all 18: {max(worst_pool.values()):.2e}   (expect ~1e-12)")

    # F1/F2 equivalence at the same points
    wf1 = wf2 = 0.0
    for pt in test_pts:
        subs, s = engine_aux(*pt)
        Fe = SP.constraints(*pt)
        vv = vec(subs)
        wf1 = max(wf1, abs(lam_ess['F1'](*vv) - Fe[1]))
        wf2 = max(wf2, abs(lam_ess['F2'](*vv) - s['V7']*Fe[2]))
    print(f"     F1 == engine.F1: {wf1:.2e}    F2 == V7*engine.F2: {wf2:.2e}")

    # (2c) full system at each Table 3 solution with its own 0/1 parameters
    print("\n(2c) Full 33x33 system at each Rao Table 3 solution "
          "(its own subset slots):")
    for cons, vals in SP.TABLE3:
        T = tuple(k for k in cons if k not in (1, 2))
        subs, _ = engine_aux(*vals)
        vv = vec(subs)
        res = max(abs(f(*vv)) for f in lam_chain.values())
        res = max(res, *(abs(f(*vv)) for f in lam_ess.values()))
        res = max(res, *(abs(lam_pool[k](*vv)) for k in T))
        print(f"       {{1,2}}+{str(T):12s} type {degree_type(T)}  "
              f"max|eq| = {res:.2e}")
    print("     (constraint rows limited by Rao's 6-digit table, ~1e-6)")

    # (3) target census
    targets = all_targets()
    from collections import Counter
    cnt = Counter(t['type'] for t in targets)
    ndeg = sum(t['degenerate'] for t in targets)
    print("\n(3) Target census: 816 subsets")
    for ty in [(3,0),(2,1),(1,2),(0,3)]:
        print(f"       type (lin,quad)={ty}: {cnt[ty]:4d} subsets")
    print(f"       degenerate (contains {{8,9,16}}): {ndeg}  ->  "
          f"{816-ndeg} well-posed + {ndeg} Gate-1 check")

    # size report
    degs = [sp.Poly(eq, *all_vars).total_degree()
            for eq in list(chain_eqs.values()) + list(essential_eqs.values())]
    print("\n" + "-"*68)
    print("MASTER SYSTEM SIZE")
    print(f"  variables : 33  (5 original + 28 auxiliary)")
    print(f"  fixed eqs : 30  (28 chain + F1 + F2), degrees "
          f"{ {dd: degs.count(dd) for dd in sorted(set(degs))} }")
    print(f"  slots     : 3   (degree 1 or 2 by family type)")
    print(f"  families  : 4 monodromy runs replace 816 ab initio solves")
    print(f"  sqrt lifts: 3 (x1,x2,w); squared radial forms add none")

# ======================================================================
#  emit family_solve.jl
# ======================================================================
def jl(eq):
    return str(sp.expand(eq)).replace('**', '^')

def polished_seed():
    """Rao's PLANE_OPT satisfies F1,F2 only to ~1e-7 (6-digit table). Monodromy
    needs an exact start pair, so Newton-polish (b,g) at fixed (c,d,e) until
    F1 = F2 = 0 to machine precision. (F1,F2 cut the 5-dim chain in a 3-fold;
    fixing c,d,e selects one transversal point on it.)"""
    bv, cv, dv, ev, gv = SP.PLANE_OPT
    for _ in range(50):
        F = SP.constraints(bv, cv, dv, ev, gv)
        f = (F[1], F[2])
        if max(abs(f[0]), abs(f[1])) < 1e-15:
            break
        h = 1e-7
        Fb = SP.constraints(bv+h, cv, dv, ev, gv); Fb_ = SP.constraints(bv-h, cv, dv, ev, gv)
        Fg = SP.constraints(bv, cv, dv, ev, gv+h); Fg_ = SP.constraints(bv, cv, dv, ev, gv-h)
        J = [[(Fb[1]-Fb_[1])/(2*h), (Fg[1]-Fg_[1])/(2*h)],
             [(Fb[2]-Fb_[2])/(2*h), (Fg[2]-Fg_[2])/(2*h)]]
        det = J[0][0]*J[1][1] - J[0][1]*J[1][0]
        db = (J[1][1]*f[0] - J[0][1]*f[1]) / det
        dg = (J[0][0]*f[1] - J[1][0]*f[0]) / det
        bv -= db; gv -= dg
    F = SP.constraints(bv, cv, dv, ev, gv)
    print(f"\n    seed polish: |F1|={abs(F[1]):.1e} |F2|={abs(F[2]):.1e} "
          f"at b={bv:.15f} g={gv:.15f}")
    return (bv, cv, dv, ev, gv)

def emit_julia(path):
    seed_pt = polished_seed()               # chain+F1+F2 exact; slots killed by p0
    subs, _ = engine_aux(*seed_pt)
    # verify the embedded seed against the lifted fixed equations
    lam = [sp.lambdify(all_vars, eq, 'math')
           for eq in list(chain_eqs.values()) + list(essential_eqs.values())]
    vv = [subs[v] for v in all_vars]
    seed_res = max(abs(f(*vv)) for f in lam)
    print(f"    seed residual on all 30 lifted fixed equations: {seed_res:.1e}")
    assert seed_res < 1e-12, "seed not on the lifted variety"
    seed_vec = ", ".join(repr(float(subs[v])) for v in all_vars)
    var_decl = " ".join(str(v) for v in all_vars)
    idx = {str(v): i+1 for i, v in enumerate(all_vars)}   # 1-based Julia indices

    L = []
    A = L.append
    A("# Tier-2 FAMILY campaign driver — coefficient-parameter homotopy")
    A("# Generated by lift_family.py.  DEV / pre-confirmatory.")
    A("#")
    A("# Usage:")
    A("#   julia -t 4,1 family_solve.jl                    # all 4 families, all 816 targets")
    A("#   julia -t 4,1 family_solve.jl --type=Q3          # one family (L3|L2Q1|L1Q2|Q3)")
    A("#   julia -t 4,1 family_solve.jl --type=Q3 --max-targets=3   # smoke test")
    A("#")
    A("# Output: family_results.jsonl (one JSON record per subset) + stdout summary.")
    A("# Requires: julia -e 'using Pkg; Pkg.add([\"HomotopyContinuation\",\"JSON\"])'")
    A("using HomotopyContinuation, LinearAlgebra, Random")
    A("import JSON")
    A("")
    A(f"@var {var_decl}")
    A(f"vars = [{', '.join(str(v) for v in all_vars)}]")
    A("")
    A("# ---- fixed equations: 28 chain + F1 + F2 ----")
    A("fixed_eqs = [")
    for k, eq in chain_eqs.items():
        A(f"    {jl(eq)},   # {k}")
    for k, eq in essential_eqs.items():
        A(f"    {jl(eq)},   # {k}")
    A("]")
    A("")
    A("# ---- constraint pool (engine equivalence validated in lift_family.py) ----")
    A("poolpoly = Dict{Int,Expression}(")
    for k in LIN + QUAD:
        A(f"    {k} => {jl(pool[k][0])},   # F{k}, factor {factor_doc[k]}")
    A(")")
    A(f"LIN  = {list(LIN)}")
    A(f"QUAD = {list(QUAD)}")
    A("")
    A("# ---- verified start point on the chain+F1+F2 variety (plane optimum) ----")
    A(f"seed = ComplexF64[{seed_vec}]")
    A("")
    A("# ---- admissibility filter (mirrors lift_poc.py Test 5) ----")
    A(f"const iB,iC,iD,iE,iG = {idx['b']},{idx['c']},{idx['d']},{idx['e']},{idx['g']}")
    A(f"const iX1,iX2,iW = {idx['x1']},{idx['x2']},{idx['w']}")
    A(f"const iU7,iU8,iU9,iU12 = {idx['U7']},{idx['U8']},{idx['U9']},{idx['U12']}")
    A(f"const iQ7,iQ8,iQ9,iQ12,iQ20,iQ21 = "
      f"{idx['Q7']},{idx['Q8']},{idx['Q9']},{idx['Q12']},{idx['Q20']},{idx['Q21']}")
    A(f"const iX13,iX18 = {idx['x13']},{idx['x18']}")
    A("function admissible(s::Vector{Float64}; pos_tol=1e-9, den_tol=1e-7, lo=1e-6)")
    A("    s[iX1]>pos_tol && s[iX2]>pos_tol && s[iW]>pos_tol || return false")
    A("    all(s[i]>lo for i in (iB,iC,iD,iE,iG)) || return false")
    A("    s[iC]<1 && s[iD]<1 || return false")
    A("    dens = (1+s[iD], 1+s[iC], s[iB]+s[iC]+s[iD], s[iC]+s[iD]+s[iE],")
    A("            s[iC]+s[iD], s[iD]+s[iG],")
    A("            s[iQ7]+1, s[iQ8]+1, s[iQ9]+1, s[iQ12]+1, s[iQ20]+1, s[iQ21]+1,")
    A("            s[iD]+s[iG]-s[iU7], 1-s[iU9]-s[iG]+s[iU12],")
    A("            (s[iG]+1-s[iU8])*s[iX13], (s[iD]+s[iE]+1-s[iU9])*s[iX18])")
    A("    all(abs(q)>den_tol for q in dens)")
    A("end")
    A("")
    A("# ---- family construction ----")
    A("# type => (slot pools);  a subset's slots are filled lin-first, sorted")
    A("FAMS = Dict(")
    A("    \"L3\"   => [LIN, LIN, LIN],")
    A("    \"L2Q1\" => [LIN, LIN, QUAD],")
    A("    \"L1Q2\" => [LIN, QUAD, QUAD],")
    A("    \"Q3\"   => [QUAD, QUAD, QUAD],")
    A(")")
    A("famname(nl) = (\"Q3\",\"L1Q2\",\"L2Q1\",\"L3\")[nl+1]")
    A("")
    A("function build_family(fam::String)")
    A("    pools = FAMS[fam]")
    A("    params = Variable[]; slots = Expression[]")
    A("    for (j, P) in enumerate(pools)")
    A("        aj = [Variable(Symbol(\"a$(j)_$(k)\")) for k in 1:length(P)]")
    A("        append!(params, aj)")
    A("        push!(slots, sum(aj[i]*poolpoly[P[i]] for i in 1:length(P)))")
    A("    end")
    A("    F = System([fixed_eqs; slots]; variables=vars, parameters=params)")
    A("    F, pools")
    A("end")
    A("")
    A("# generic parameters vanishing at `seed`: per slot, random complex coeffs")
    A("# projected onto the hyperplane  sum_i a_i * P_i(seed) = 0")
    A("function generic_params_at_seed(pools; rng=Random.default_rng())")
    A("    p0 = ComplexF64[]")
    A("    for P in pools")
    A("        u = [ComplexF64(evaluate(poolpoly[k], vars => seed)) for k in P]")
    A("        a = randn(rng, ComplexF64, length(P))")
    A("        a .-= (transpose(u)*a / (transpose(u)*u)) .* u   # unconjugated dot")
    A("        @assert abs(sum(a .* u)) < 1e-10")
    A("        append!(p0, a)")
    A("    end")
    A("    p0")
    A("end")
    A("")
    A("# 0/1 parameter vector for a concrete subset (lin-first, sorted order)")
    A("function target_params(T::Vector{Int}, pools)")
    A("    Tl = sort([k for k in T if k in LIN]); Tq = sort([k for k in T if k in QUAD])")
    A("    chosen = vcat(Tl, Tq)")
    A("    @assert length(chosen) == length(pools)")
    A("    pt = ComplexF64[]")
    A("    for (j, P) in enumerate(pools)")
    A("        v = zeros(ComplexF64, length(P)); v[findfirst(==(chosen[j]), P)] = 1")
    A("        append!(pt, v)")
    A("    end")
    A("    pt")
    A("end")
    A("")
    A("# ---- target census ----")
    A("alltriples = [sort(collect(T)) for T in")
    A("    Iterators.filter(t -> length(t)==3,")
    A("        [ [i,j,k] for i in 3:20 for j in i+1:20 for k in j+1:20 ])]")
    A("DEGEN = Set([8,9,16])")
    A("")
    A("# ---- CLI ----")
    A("want_type = nothing; max_targets = typemax(Int)")
    A("for a in ARGS")
    A("    startswith(a, \"--type=\")        && (global want_type   = split(a,\"=\")[2])")
    A("    startswith(a, \"--max-targets=\") && (global max_targets = parse(Int, split(a,\"=\")[2]))")
    A("end")
    A("")
    A("results_io = open(\"family_results.jsonl\", \"a\")")
    A("")
    A("for fam in [\"L3\",\"L2Q1\",\"L1Q2\",\"Q3\"]")
    A("    (want_type === nothing || want_type == fam) || continue")
    A("    println(\"\\n\", \"=\"^70); println(\"FAMILY \", fam); println(\"=\"^70)")
    A("    F, pools = build_family(fam)")
    A("")
    A("    # --- two independent monodromy runs, unioned at common parameters ---")
    A("    p0 = generic_params_at_seed(pools; rng=MersenneTwister(20260612))")
    A("    t_mono = @elapsed mres = monodromy_solve(F, [seed], p0;")
    A("        max_loops_no_progress = 12, unique_points_rtol = 1e-10)")
    A("    S = solutions(mres)")
    A("    p1 = generic_params_at_seed(pools; rng=MersenneTwister(987654321))")
    A("    mres2 = monodromy_solve(F, [seed], p1;")
    A("        max_loops_no_progress = 12, unique_points_rtol = 1e-10)")
    A("    r21 = solve(F, solutions(mres2); start_parameters=p1, target_parameters=p0,")
    A("                show_progress=false)")
    A("    S = unique_points([S; solutions(r21)]; rtol = 1e-9)")
    A("    Nstar = length(S)")
    A("    agree = (Nstar == length(solutions(mres)))")
    A("    println(\"N* ($fam) = $Nstar generic solutions  \",")
    A("            \"(run1=\", length(solutions(mres)), \", union adds \",")
    A("            Nstar - length(solutions(mres)), \"; monodromy \",")
    A("            round(t_mono, digits=1), \"s)\")")
    A("")
    A("    # --- trace-test completeness certificate ---")
    A("    cert_ok = false")
    A("    try")
    A("        v = verify_solution_completeness(F, S, p0; trace_tol = 1e-10)")
    A("        cert_ok = (v === true)")
    A("        println(\"trace-test completeness: \", v)")
    A("    catch err")
    A("        println(\"trace-test completeness: ERROR \", err)")
    A("    end")
    A("    JSON.print(results_io, Dict(\"family_summary\" => fam,")
    A("        \"Nstar\" => Nstar, \"trace_test_passed\" => cert_ok,")
    A("        \"monodromy_runs_agree\" => agree,")
    A("        \"monodromy_seconds\" => round(t_mono, digits=1)))")
    A("    write(results_io, '\\n'); flush(results_io)")
    A("")
    A("    # --- sweep all targets of this family type ---")
    A("    targets = [T for T in alltriples if famname(count(in(LIN), T)) == fam]")
    A("    ndone = 0")
    A("    for T in targets")
    A("        ndone >= max_targets && break; ndone += 1")
    A("        pt = target_params(T, pools)")
    A("        t_solve = @elapsed res = solve(F, S; start_parameters=p0,")
    A("            target_parameters=pt, show_progress=false)")
    A("        pr = path_results(res)")
    A("        nfail = count(r -> !is_success(r) && !is_at_infinity(r), pr)")
    A("        rs = real_solutions(res)")
    A("        adm = [s for s in rs if admissible(s)]")
    A("        ncert = -1")
    A("        try")
    A("            ncert = ndistinct_certified(certify(F, solutions(res);")
    A("                target_parameters = pt))")
    A("        catch; end")
    A("        rec = Dict(")
    A("            \"subset\" => vcat([1,2], T), \"family\" => fam,")
    A("            \"expected_degenerate\" => issubset(DEGEN, Set(T)),")
    A("            \"Nstar_paths\" => Nstar, \"path_failures\" => nfail,")
    A("            \"n_solutions\" => nsolutions(res), \"n_real\" => length(rs),")
    A("            \"n_admissible\" => length(adm),")
    A("            \"n_certified_distinct\" => ncert,")
    A("            \"admissible_bcdeg\" => [round.(s[[iB,iC,iD,iE,iG]], digits=10)")
    A("                                    for s in adm],")
    A("            \"completeness_bearing\" => (cert_ok && nfail == 0),")
    A("            \"runtime_s\" => round(t_solve, digits=2),")
    A("        )")
    A("        JSON.print(results_io, rec); write(results_io, '\\n'); flush(results_io)")
    A("        tag = rec[\"expected_degenerate\"] ? \"  [GATE-1: expect non-isolated]\" : \"\"")
    A("        println(\"{1,2}+\", T, \"  real=\", length(rs), \" adm=\", length(adm),")
    A("                \" fail=\", nfail, \" \", round(t_solve,digits=1), \"s\", tag)")
    A("    end")
    A("end")
    A("close(results_io)")
    A("println(\"\\nDone. Records appended to family_results.jsonl\")")
    with open(path, 'w') as f:
        f.write("\n".join(L) + "\n")
    print(f"\n(4) Julia campaign driver written: {path}")

if __name__ == "__main__":
    validate()
    here = os.path.dirname(os.path.abspath(__file__))
    emit_julia(os.path.join(here, "family_solve.jl"))
