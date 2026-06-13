"""
Route-2 probe: collapse the ENTIRE rational chain into the 8 genuine variables
(b,c,d,e,g, x1, x2, w) and measure the mixed volume of the resulting system.

Rationale: the 21-variable eliminated lifting has BKK = 286,144 because each
auxiliary's defining equation multiplies into the Newton-polytope product. That
product structure -- not the genuine geometry -- is what inflates the path count
(~286k paths to find ~5 non-singular solutions). If we substitute the whole
rational chain down to the original 5 variables plus the 3 true square roots
(x1=sqrt(1-c^2), x2=sqrt(1-d^2), w=sqrt(x7^2+V7^2)) and clear denominators once,
the system is 8x8 high-degree. Its mixed volume could be far smaller (no
auxiliary product) or could reveal the degree is genuinely irreducible.

This is a PROBE. It builds the collapsed system, validates it against the frozen
engine, reports degrees/Bezout, and emits probe_collapsed.jl whose headline is
the 'mixed_volume:' line.
"""
import sympy as sp
import time
import lift_poc as L          # eliminated 21-var system (import runs the elim pass)

b,c,d,e,g = L.b, L.c, L.d, L.e, L.g
x1, x2, w = L.x1, L.x2, L.w
KEEP = {b, c, d, e, g, x1, x2, w}

# chain order of the eliminated system, minus the kept variables
chain_order = [k for k in L.chain_eqs.keys() if k not in ('x1', 'x2', 'w')]
name2sym = {str(v): v for v in L.all_vars}

print("="*68)
print("ROUTE-2 PROBE — collapse chain to (b,c,d,e,g,x1,x2,w)")
print("="*68)
print(f"substituting out {len(chain_order)} rational auxiliaries: {chain_order}")

t0 = time.time()
# ---- 1. solve each rational chain eq for its variable, compose substitutions ----
subs = {}
for name in chain_order:
    v = name2sym[name]
    sol = sp.solve(L.chain_eqs[name], v)
    assert len(sol) == 1, f"{name}: expected unique rational solution, got {len(sol)}"
    subs[v] = sp.cancel(sol[0].xreplace(subs))     # compose with earlier subs
print(f"  chain solved & composed ({time.time()-t0:.1f}s)")

# ---- 2. build the 8 collapsed polynomials (clear denominators) ----
def collapse(expr):
    """substitute the rational chain, cancel, return the numerator polynomial."""
    num, den = sp.fraction(sp.cancel(expr.xreplace(subs)))
    return sp.expand(num)

t0 = time.time()
E1 = sp.expand(x1**2 - (1 - c**2))
E2 = sp.expand(x2**2 - (1 - d**2))
# w-defining eq: w^2 = x7^2 + V7^2,  V7 = d+g-U7  (both rational in x1,x2)
x7_sub = subs[name2sym['x7']]
U7_sub = subs[name2sym['U7']]
E3 = collapse(w**2 - (x7_sub**2 + (d + g - U7_sub)**2))   # already substituted; collapse clears
# the five subset constraints (F1 folded, F2 keeps w)
Fc = {k: collapse(eq) for k, eq in L.constraint_eqs.items()}
print(f"  constraints collapsed ({time.time()-t0:.1f}s)")

collapsed = {'E1':E1, 'E2':E2, 'E3':E3, **{f'{k}':Fc[k] for k in L.constraint_eqs}}
allvars8 = [b, c, d, e, g, x1, x2, w]

# ---- 3. validate against the frozen engine at Rao's {1,2,3,4,8} solution ----
subs_e, s = L.engine_aux(0.463752, 0.223255, 0.288990, 0.488181, 0.106157)
val = {v: subs_e[v] for v in allvars8}
print("\nvalidation at Rao {1,2,3,4,8} (engine x1,x2,w):")
for k, poly in collapsed.items():
    r = abs(float(poly.subs(val)))
    tag = "(sqrt/w identity, ~1e-12)" if k in ('E1','E2','E3') else "(constraint, Rao ~1e-6 * factor)"
    print(f"   {k:3s}: |poly| = {r:.2e}   {tag}")

# ---- 4. degree / size report ----
print("\n" + "-"*68)
print("COLLAPSED SYSTEM")
degs = {k: sp.Poly(p, *allvars8).total_degree() for k, p in collapsed.items()}
nterms = {k: len(sp.Add.make_args(p)) for k, p in collapsed.items()}
for k in collapsed:
    print(f"   {k:3s}:  total_degree = {degs[k]:3d}   terms = {nterms[k]}")
import functools
bez = functools.reduce(lambda a,x: a*x, degs.values(), 1)
print(f"  variables : 8  (b,c,d,e,g,x1,x2,w)")
print(f"  equations : {len(collapsed)}")
print(f"  Bezout (product of degrees) = {bez:.3e}   (BKK <= Bezout; the probe measures BKK)")

# ---- 5. emit the Julia mixed-volume probe ----
def jl(p): return str(p).replace('**','^')
lines = ["# Route-2 mixed-volume probe: collapsed 8-var system, subset {1,2,3,4,8}",
         "# DEV. Headline = the 'mixed_volume:' line (prints before tracking).",
         "using HomotopyContinuation",
         "@var b c d e g x1 x2 w",
         "eqs = ["]
for k, p in collapsed.items():
    lines.append(f"    {jl(p)},   # {k}")
lines += ["]",
          "F = System(eqs; variables = [b,c,d,e,g,x1,x2,w])",
          "result = solve(F)",
          "ns = solutions(result; only_nonsingular = true)",
          'println("paths tracked: ", length(path_results(result)))',
          'println("non-singular solutions: ", length(ns))']
import os
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "probe_collapsed.jl")
with open(out, 'w') as f:
    f.write("\n".join(lines) + "\n")
print(f"\nprobe written: {out}")
