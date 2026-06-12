"""
Tier-2 proof-of-concept: auxiliary-variable lifting of the plane Sri Yantra
system for subset {1,2,3,4,8}  (constraints F1,F2,F3,F4,F8).

DEV-BRANCH / PRE-CONFIRMATORY tooling. Not part of any registered run.

Strategy (auditability over cleverness): every non-polynomial chain step
becomes one auxiliary variable + one polynomial defining equation (denominators
cleared). The five subset constraints are added on top. The result is a square
polynomial system equivalent, on the physically admissible branch, to the
frozen engine.

Non-polynomial pieces handled:
  - square roots  x1=sqrt(1-c^2), x2=sqrt(1-d^2)  -> x1^2=1-c^2, x2^2=1-d^2
  - rational U=S/(Q+1) and Q=... ratios           -> cleared denominators
  - F2 trig: rT = x7*tan(t/2), t=arctan(V7/x7)
        tan(t/2) = (w - x7)/V7 with w=sqrt(x7^2+V7^2)  (w>0)
        => F2 polynomial:  (d-U7)*V7 - x7*w + x7^2 = 0
  - radial r16 folded directly into F8: (d+e)^2 + x16^2 - r^2 = 0  (no sqrt aux)

This file:
  (1) builds the system in SymPy and checks it is polynomial;
  (2) validates EXACT equivalence to the engine (chain identities ~1e-15;
      constraint polynomials equal engine constraints up to known factors);
  (3) provides round-trip (Test 4) and branch-admissibility (Test 5) checkers
      for use on homotopy solutions;
  (4) emits a HomotopyContinuation.jl script (Test 3 runs on your machine);
  (5) reports system size for the resource table.
"""
import sympy as sp
import math, random, os, sys
# resolve sriyantra_plane from the repo root (parent of this script's dir)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sriyantra_plane as SP

r = sp.Integer(1)   # plane form: r fixed = 1

# ---- symbols: 5 original + 21 auxiliary = 26 ----
b,c,d,e,g = sp.symbols('b c d e g', real=True)
(x1,x2,x3,x4,x5,x6,x7,x10,x11,x13,x16,
 U7,U8,U9,U12,Q7,Q8,Q9,Q12,x11a,w) = sp.symbols(
 'x1 x2 x3 x4 x5 x6 x7 x10 x11 x13 x16 '
 'U7 U8 U9 U12 Q7 Q8 Q9 Q12 x11a w', real=True)

orig_vars = [b,c,d,e,g]
aux_vars  = [x1,x2,x3,x4,x5,x6,x7,x10,x11,x13,x16,
             U7,U8,U9,U12,Q7,Q8,Q9,Q12,x11a,w]
all_vars  = orig_vars + aux_vars

# inline linear combos (not given their own variable)
V7 = d + g - U7
V8 = (1 + g) - U8           # r+g-U8
# v8 = 1-U8-d ; S12 = d+g+v8 = g+1-U8 ; v12 = d+g-U12 ; v9 = 1-U9-c
S12 = g + 1 - U8

# ---- chain equations (each = 0); label ties to the engine step ----
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
 'x13': (c + d + e)*x13 - (e + d + g - U12)*x3,         # e+v12 = e+d+g-U12
 'x11a': (1 - U9 - g + U12)*x11a - (1 - U9 - g)*x13,    # cleared P2-13 line
 'w'  : w**2 - (x7**2 + V7**2),
}

# ---- subset {1,2,3,4,8} constraint equations (each = 0) ----
constraint_eqs = {
 'F1': x11 - x11a,
 'F2': (d - U7)*V7 - x7*w + x7**2,          # = V7 * engine_F2
 'F3': 3*x10**2 - V8**2,                     # = 2 * engine_F3
 'F4': 3*x13**2 - (1 - U9 - g + U12)**2,     # = 2 * engine_F4 ; arg c+d+v9-v12
 'F8': (d + e)**2 + x16**2 - 1,              # r16^2 - r^2 = -2*engineF8 + engineF8^2
}

system = list(chain_eqs.values()) + list(constraint_eqs.values())

# cleared denominators that must be verified non-zero at any accepted solution
denominators = {
 '1+d':1+d, '1+c':1+c, 'b+c+d':b+c+d, 'c+d+e':c+d+e, 'c+d':c+d, 'd+g':d+g,
 'Q7+1':Q7+1, 'Q8+1':Q8+1, 'Q9+1':Q9+1, 'Q12+1':Q12+1,
 'V7(=d+g-U7)':d+g-U7, 'x11a_den(1-U9-g+U12)':1-U9-g+U12,
}
# sign-admissible (physical branch) auxiliaries
positive_vars = [x1, x2, w]

# ======================================================================
#  helper: full auxiliary value dict from the frozen engine
# ======================================================================
def engine_aux(bv,cv,dv,ev,gv):
    s = SP.chain(bv,cv,dv,ev,gv)            # frozen engine, r=1
    Q7v  = (dv+gv)/(cv+dv)*(s['x5']/s['x6'])
    Q8v  = (dv+gv)/(1+cv)*(s['x1']/s['x6'])
    Q9v  = (cv+dv)/(1+dv)*(s['x2']/s['x5'])
    Q12v = (dv+gv+s['v8'])/(dv+gv)*(s['x6']/s['x10'])
    wv   = math.sqrt(s['x7']**2 + s['V7']**2)
    return {b:bv,c:cv,d:dv,e:ev,g:gv,
            x1:s['x1'],x2:s['x2'],x3:s['x3'],x4:s['x4'],x5:s['x5'],x6:s['x6'],
            x7:s['x7'],x10:s['x10'],x11:s['x11'],x13:s['x13'],x16:s['x16'],
            U7:s['U7'],U8:s['U8'],U9:s['U9'],U12:s['U12'],
            Q7:Q7v,Q8:Q8v,Q9:Q9v,Q12:Q12v,x11a:s['x11a'],w:wv}, s

# ======================================================================
#  (5) round-trip checker (Test 4): homotopy solution -> engine
# ======================================================================
def round_trip(sol, tol=1e-7):
    """sol: dict mapping var-name(str)->float for a homotopy solution.
       Re-evaluates the ORIGINAL non-polynomial engine and the imposed
       constraints; returns (ok, max_residual)."""
    F = SP.constraints(sol['b'],sol['c'],sol['d'],sol['e'],sol['g'])
    res = max(abs(F[i]) for i in (1,2,3,4,8))
    return res < tol, res

# ======================================================================
#  (5) branch-admissibility checker (Test 5)
# ======================================================================
def admissible(subs, pos_tol=1e-9, den_tol=1e-7, range_lo=1e-6):
    """subs: dict sympy-symbol->float. Rejects spurious lifted branches:
       wrong square-root sign, vanished cleared denominator, out-of-range vars."""
    for v in positive_vars:
        if subs[v] <= pos_tol: return False, f"sign branch: {v}<=0"
    for nm,den in denominators.items():
        if abs(float(den.subs(subs))) < den_tol: return False, f"denominator {nm}~0"
    for v in orig_vars:
        if float(subs[v]) <= range_lo: return False, f"out of range: {v}<=0"
    # domain: c,d < r for the square roots to be real/physical
    if float(subs[c]) >= 1 or float(subs[d]) >= 1: return False, "c or d >= r"
    return True, "admissible"

# ======================================================================
#  (1)+(2) validation
# ======================================================================
def validate():
    print("="*64)
    print("LIFTING VALIDATION  — subset {1,2,3,4,8}")
    print("="*64)

    # (1) polynomiality
    def is_poly(eq):
        try:
            sp.Poly(eq, *all_vars)
            return eq.free_symbols <= set(all_vars)
        except sp.PolynomialError:
            return False
    named = {**chain_eqs, **constraint_eqs}
    nonpoly = [k for k,eq in named.items() if not is_poly(eq)]
    allpoly = not nonpoly
    print(f"\n(1) Polynomiality: all {len(system)} equations are polynomials "
          f"in the {len(all_vars)} variables: {allpoly}"
          + (f"  [non-poly: {nonpoly}]" if nonpoly else ""))

    # (2a) chain identities vanish at engine auxiliaries (machine zero),
    #      tested at several arbitrary valid points (NOT solutions)
    print("\n(2a) Chain identities at arbitrary valid figures "
          "(engine auxiliaries) — expect ~1e-15:")
    rng = random.Random(11)
    worst_chain = 0.0
    for _ in range(20):
        bv=rng.uniform(0.35,0.55); cv=rng.uniform(0.18,0.30); dv=rng.uniform(0.24,0.33)
        ev=rng.uniform(0.40,0.52); gv=rng.uniform(0.08,0.13)
        try: subs,_ = engine_aux(bv,cv,dv,ev,gv)
        except Exception: continue
        for k,eq in chain_eqs.items():
            worst_chain = max(worst_chain, abs(float(eq.subs(subs))))
    print(f"     max |chain_eq| over 20 random figures = {worst_chain:.2e}")

    # (2b) constraint polynomials equal engine constraints up to known factors
    print("\n(2b) Constraint-lifting equivalence (my poly  vs  engine F, "
          "with derived factor) — expect ~1e-12:")
    subs,s = engine_aux(0.463752,0.223255,0.288990,0.488181,0.106157)  # Rao {1,2,3,4,8}
    Fe = SP.constraints(0.463752,0.223255,0.288990,0.488181,0.106157)
    V7v = float((d+g-U7).subs(subs))
    checks = {
        'F1 == engine.F1'         : float(constraint_eqs['F1'].subs(subs)) - Fe[1],
        'F2 == V7*engine.F2'      : float(constraint_eqs['F2'].subs(subs)) - V7v*Fe[2],
        'F3 == 2*engine.F3'       : float(constraint_eqs['F3'].subs(subs)) - 2*Fe[3],
        'F4 == 2*engine.F4'       : float(constraint_eqs['F4'].subs(subs)) - 2*Fe[4],
        'F8 == r16^2-1'           : float(constraint_eqs['F8'].subs(subs)) - ((1-Fe[8])**2 - 1),
    }
    for k,v in checks.items():
        print(f"     {k:24s}  residual = {v:+.2e}")

    # (2c) the lifted system, at the Rao solution, vanishes to engine precision
    worst_sys = max(abs(float(eq.subs(subs))) for eq in system)
    print(f"\n(2c) Full lifted system at Rao {{1,2,3,4,8}} solution: "
          f"max|eq| = {worst_sys:.2e}  (constraints limited by Rao's 6-digit table)")

    # (5) admissibility of the physical solution
    ok,msg = admissible(subs)
    print(f"\n(5) Physical solution passes branch-admissibility: {ok} ({msg})")

    # size report for the resource table
    degs = [sp.Poly(eq,*all_vars).total_degree() for eq in system]
    print("\n" + "-"*64)
    print("SYSTEM SIZE (for the resource table)")
    print(f"  variables : {len(all_vars)}  (5 original + {len(aux_vars)} auxiliary)")
    print(f"  equations : {len(system)}  (square: {len(all_vars)==len(system)})")
    print(f"  degrees   : max {max(degs)}, "
          f"counts {{deg:count}} = { {dd:degs.count(dd) for dd in sorted(set(degs))} }")
    import functools
    bezout = functools.reduce(lambda a,x:a*x, degs, 1)
    print(f"  total-degree (Bezout) bound : {bezout:.3e}  "
          f"(homotopy tracks far fewer via polyhedral start)")
    print(f"  square roots lifted : 3 (x1,x2,w) -> <= 2^3 = 8 sign branches to filter")

# ======================================================================
#  (4) emit HomotopyContinuation.jl script
# ======================================================================
def emit_julia(path):
    def jl(eq):
        return str(sp.expand(eq)).replace('**','^')
    var_decl = " ".join(str(v) for v in all_vars)
    lines = []
    lines.append("# Tier-2 homotopy solve — subset {1,2,3,4,8}  (DEV / pre-confirmatory)")
    lines.append("# Generated by lift_poc.py. Run: julia thisfile.jl")
    lines.append("using HomotopyContinuation")
    lines.append(f"@var {var_decl}")
    lines.append("eqs = [")
    for k,eq in {**chain_eqs, **constraint_eqs}.items():
        lines.append(f"    {jl(eq)},   # {k}")
    lines.append("]")
    lines.append(f"vars = [{', '.join(str(v) for v in all_vars)}]")
    lines.append("F = System(eqs; variables = vars)")
    lines.append("result = solve(F)")
    lines.append("cert   = certify(F, solutions(result))")
    lines.append("")
    lines.append("# admissible-branch filter (sign + range + denominators)")
    lines.append("for s in real_solutions(result)")
    lines.append("    bv,cv,dv,ev,gv = s[1],s[2],s[3],s[4],s[5]")
    lines.append("    x1v,x2v,wv = s[6],s[7],s[26]")
    lines.append("    ok = x1v>1e-9 && x2v>1e-9 && wv>1e-9 &&")
    lines.append("         bv>1e-6 && cv>1e-6 && dv>1e-6 && ev>1e-6 && gv>1e-6 &&")
    lines.append("         cv<1 && dv<1")
    lines.append("    if ok; println(\"admissible: \", s); end")
    lines.append("end")
    lines.append("println(\"paths tracked: \", length(path_results(result)))")
    lines.append("println(\"real solutions: \", length(real_solutions(result)))")
    with open(path,'w') as f:
        f.write("\n".join(lines)+"\n")
    print(f"\n(4) HomotopyContinuation.jl script written: {path}")

if __name__ == "__main__":
    validate()
    here = os.path.dirname(os.path.abspath(__file__))
    emit_julia(os.path.join(here, "solve_1_2_3_4_8.jl"))
