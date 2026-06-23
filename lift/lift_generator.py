"""
lift_generator.py
=============================================================================
Family lift generator (toward lift-generator-v1). Given ANY well-posed
size-six subset {F1,F2}+4-of-{F3..F20}, deterministically generates the square
polynomial lift (r free) of the spherical Sri Yantra system for that subset,
validated against the frozen spherical engine.

DEV-BRANCH / PRE-CONFIRMATORY tooling. Not part of any registered run.

Design principle (per review): the generator is now part of the scientific
instrument, so correctness must be DERIVED, not asserted.

  - There is ONE chain registry (CHAIN) giving each quantity's lifted defining
    equation. Dependencies are not hand-listed; they are read off the free
    symbols of the equations themselves, so the dependency graph cannot drift
    from the equations.
  - generate(subset) computes the dependency closure from the subset's six
    constraint lifts and assembles atomic + needed-quantity variables and
    equations. Squareness is structural (each angle adds 2 vars / 2 eqs, each
    ratio 1 var / 1 eq, atomic 12 vars / 6 eqs, constraints +6 eqs), so every
    generated system is square by construction.
  - validate_sample() checks, on random subsets at random valid figures, that
    every generated equation vanishes (~1e-15) at the frozen engine's values
    and that each constraint polynomial matches the frozen engine constraint up
    to its known factor.

Note on "certified": HC.jl certify() gives Smale alpha-theory / interval
certification of the solutions FOUND (Level C for those points). Completeness
(all isolated solutions found) is a separate property resting on the
path-tracking / monodromy, not on certify(). This generator emits the system;
the solve + certify + completeness argument live on the Julia side.
=============================================================================
"""
import sympy as sp
import math, random, os, sys, hashlib, itertools, json
_here = os.path.dirname(os.path.abspath(__file__))
_root = _here
while _root != os.path.dirname(_root):
    if os.path.exists(os.path.join(_root, "sriyantra.py")):
        break
    _root = os.path.dirname(_root)
for _p in (_here, _root, os.path.join(_root, "enumeration")):
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)
import sriyantra as RAO

SPEC_VERSION = "lift-generator-v1"

# ---------------------------------------------------------------------------
#  symbols
# ---------------------------------------------------------------------------
ATOMIC_NAMES = ["b", "c", "d", "e", "g", "r"]
ANGLE_NAMES = ["x1","x2","x3","x4","x5","x6","x7","x8","x9","x10","x11","x12",
               "x13","x14","x16","x17","x18","x19","x11a",
               "U7","U8","U9","U12","U20","U21","r16","r17","r18","r19","t","rT"]
RATIO_NAMES = ["Q7","Q8","Q9","Q12","Q20","Q21"]

CA = {n: sp.Symbol("c"+n, real=True) for n in ATOMIC_NAMES}
SA = {n: sp.Symbol("s"+n, real=True) for n in ATOMIC_NAMES}
C  = {n: sp.Symbol("c"+n, real=True) for n in ANGLE_NAMES}
S  = {n: sp.Symbol("s"+n, real=True) for n in ANGLE_NAMES}
QV = {n: sp.Symbol(n, real=True) for n in RATIO_NAMES}

# symbol -> quantity-name (only chain quantities; atomic excluded)
SYM2Q = {}
for n in ANGLE_NAMES: SYM2Q[C[n]] = n; SYM2Q[S[n]] = n
for n in RATIO_NAMES: SYM2Q[QV[n]] = n

COMBOS = {"V7":["d","g","-U7"], "V8":["r","g","-U8"], "V9":["r","d","-U9"],
          "v8":["r","-U8","-d"], "v9":["r","-U9","-c"], "v12":["d","g","-U12"]}

# ---------------------------------------------------------------------------
#  angle-addition: trig = (cos, sin)
# ---------------------------------------------------------------------------
def add(A, B):
    cA, sA = A; cB, sB = B
    return (cA*cB - sA*sB, sA*cB + cA*sB)

def resolve(tok):
    if tok in ATOMIC_NAMES: return (CA[tok], SA[tok])
    if tok in ANGLE_NAMES:  return (C[tok], S[tok])
    if tok in COMBOS:       return arc(COMBOS[tok])
    raise KeyError(tok)

def arc(terms):
    acc = (sp.Integer(1), sp.Integer(0))
    for t in terms:
        neg = t.startswith("-"); name = t[1:] if neg else t
        cP, sP = resolve(name)
        acc = add(acc, (cP, -sP) if neg else (cP, sP))
    return acc

# ---------------------------------------------------------------------------
#  chain registry: name -> (kind, params).  Equations derived below.
#  kinds: base/psi/ratio/u/rho/t/rt  (see chain() in sriyantra.py)
# ---------------------------------------------------------------------------
CHAIN = [
 ("x1","base",{"phi":"c"}), ("x2","base",{"phi":"d"}),
 ("x3","psi",{"A":["r","-c"],"B":["r","d"],"X":"x2"}),
 ("x4","psi",{"A":["r","-d"],"B":["r","c"],"X":"x1"}),
 ("x5","psi",{"A":["b"],"B":["b","c","d"],"X":"x4"}),
 ("x6","psi",{"A":["e"],"B":["c","d","e"],"X":"x3"}),
 ("Q7","ratio",{"num":["d","g"],"den":["c","d"],"Xn":"x5","Xd":"x6"}),
 ("U7","u",{"S":["d","g"],"Q":"Q7"}),
 ("x7","psi",{"A":["U7"],"B":["c","d"],"X":"x5"}),
 ("Q8","ratio",{"num":["d","g"],"den":["r","c"],"Xn":"x1","Xd":"x6"}),
 ("U8","u",{"S":["r","g"],"Q":"Q8"}),
 ("x8","psi",{"A":["U8"],"B":["r","c"],"X":"x1"}),
 ("x16","psi",{"A":["d","e","g"],"B":["d","g"],"X":"x6"}),
 ("x11","psi",{"A":["d","g"],"B":["c","d"],"X":"x5"}),
 ("x17","psi",{"A":["b","c","d"],"B":["c","d"],"X":"x5"}),
 ("Q9","ratio",{"num":["c","d"],"den":["r","d"],"Xn":"x2","Xd":"x5"}),
 ("U9","u",{"S":["r","d"],"Q":"Q9"}),
 ("x9","psi",{"A":["U9"],"B":["r","d"],"X":"x2"}),
 ("x10","psi",{"A":["b","c","-g"],"B":["b","c","d"],"X":"x4"}),
 ("x18","psi",{"A":["b","c","d","v8"],"B":["b","c","d"],"X":"x4"}),
 ("Q12","ratio",{"num":["d","g","v8"],"den":["d","g"],"Xn":"x6","Xd":"x10"}),
 ("U12","u",{"S":["d","g","v8"],"Q":"Q12"}),
 ("x12","psi",{"A":["U12"],"B":["d","g"],"X":"x6"}),
 ("x14","psi",{"A":["U7","v8"],"B":["d","g","v8"],"X":"x10"}),
 ("x13","psi",{"A":["e","v12"],"B":["c","d","e"],"X":"x3"}),
 ("x19","psi",{"A":["c","d","e","v9"],"B":["c","d","e"],"X":"x3"}),
 ("x11a","psi",{"A":["v9","c","-g"],"B":["v9","c","d","-v12"],"X":"x13"}),
 ("r16","rho",{"P":["d","e"],"X":"x16"}),
 ("r17","rho",{"P":["b","c"],"X":"x17"}),
 ("r18","rho",{"P":["d","v8"],"X":"x18"}),
 ("r19","rho",{"P":["c","v9"],"X":"x19"}),
 ("t","t",{}), ("rT","rt",{}),
 ("Q20","ratio",{"num":["c","d","v9","-v12"],"den":["d","g","v8"],"Xn":"x10","Xd":"x13"}),
 ("U20","u",{"S":["c","d","v8","v9"],"Q":"Q20"}),
 ("Q21","ratio",{"num":["b","c","d","v8"],"den":["c","d","e","v9"],"Xn":"x19","Xd":"x18"}),
 ("U21","u",{"S":["b","c","d","e"],"Q":"Q21"}),
]
CHAIN_KIND = {nm: k for nm, k, _ in CHAIN}

def chain_eq(nm, kind, p):
    if kind == "base":
        return C[nm]*CA[p["phi"]] - CA["r"]
    if kind == "psi":
        sA = arc(p["A"])[1]; sB = arc(p["B"])[1]; X = p["X"]
        return S[nm]*sB*C[X] - C[nm]*sA*S[X]
    if kind == "ratio":
        sN = arc(p["num"])[1]; sD = arc(p["den"])[1]; Xn, Xd = p["Xn"], p["Xd"]
        return QV[nm]*sD*C[Xn]*S[Xd] - sN*S[Xn]*C[Xd]
    if kind == "u":
        cS, sS = arc(p["S"])
        return S[nm]*(QV[p["Q"]] + cS) - C[nm]*sS
    if kind == "rho":
        cP = arc(p["P"])[0]
        return C[nm] - cP*C[p["X"]]
    if kind == "t":            # atan(tan(V7)/sin x7): st*cV7*sx7 - ct*sV7
        cV7, sV7 = arc(COMBOS["V7"])
        return S["t"]*cV7*S["x7"] - C["t"]*sV7
    if kind == "rt":           # atan(sin x7 tan(t/2)): srT*(1+ct) - crT*sx7*st
        return S["rT"]*(1 + C["t"]) - C["rT"]*S["x7"]*S["t"]
    raise ValueError(kind)

EQ = {nm: chain_eq(nm, k, p) for nm, k, p in CHAIN}     # defining equation per quantity
def pyth(nm): return C[nm]**2 + S[nm]**2 - 1
ATOMIC_PYTH = {n: CA[n]**2 + SA[n]**2 - 1 for n in ATOMIC_NAMES}

# ---------------------------------------------------------------------------
#  constraint lifts F1..F20
# ---------------------------------------------------------------------------
CONS_ANGLE = {                       # cos(combo) - 1 = 0  ; doubled for 13,14,15
 1:["x11","-x11a"], 2:["d","-U7","-rT"], 5:["x10","-x13"], 7:["x18","-x19"],
 8:["r","-r16"], 9:["r","-r17"], 10:["b","c","-d","-g","-g","-v8"],
 11:["c","d","v9","-v12","-v12","-e"], 12:["x16","-x17"],
 13:["U7","U7","-U20","v8","-v12"], 14:["v12","v12","-U21","e"],
 15:["g","g","d","e","-c","-U21"],
 16:["r16","-r17"], 17:["r18","-r19"], 18:["r16","-r18"], 19:["r17","-r19"],
 20:["c","-d"],
}
CONS_COS = {3:(["r","g","-U8"],"x10"), 4:(["c","d","v9","-v12"],"x13"),
            6:(["d","g","-U7"],"x7")}          # V8/x10, arg/x13, V7/x7
DOUBLED = {13, 14, 15}

def constraint_lift(i):
    if i in CONS_COS:
        Vt, X = CONS_COS[i]
        return arc(Vt)[0]*C[X] - (2*C[X]**2 - 1)
    return arc(CONS_ANGLE[i])[0] - 1

# ---------------------------------------------------------------------------
#  dependency closure + generate
# ---------------------------------------------------------------------------
def closure(subset):
    seen, stack = set(), []
    for i in subset:
        if i in (1, 2):                          # F1,F2 always present
            pass
    for i in subset:
        for sym in constraint_lift(i).free_symbols:
            if sym in SYM2Q: stack.append(SYM2Q[sym])
    while stack:
        q = stack.pop()
        if q in seen: continue
        seen.add(q)
        for sym in EQ[q].free_symbols:
            if sym in SYM2Q and SYM2Q[sym] not in seen:
                stack.append(SYM2Q[sym])
    return seen

def generate(subset):
    subset = tuple(sorted(subset))
    if len(subset) != 6 or 1 not in subset or 2 not in subset:
        raise ValueError(f"size-six subset must be {{1,2}}+4-of-3..20; got {subset}")
    if {8, 9, 16} <= set(subset) or {16, 17, 18, 19} <= set(subset):
        raise ValueError(f"rank-deficient subset (singular support): {subset}")
    need = closure(subset)
    angles = [n for n in ANGLE_NAMES if n in need]
    ratios = [n for n in RATIO_NAMES if n in need]
    # --- CANONICAL VARIABLE ORDERING (lift-generator-v1, frozen) ---------
    #   block 1: atomic (cos,sin) pairs, ATOMIC_NAMES order
    #   block 2: chain-angle (cos,sin) pairs, ANGLE_NAMES order (needed only)
    #   block 3: ratio variables, RATIO_NAMES order (needed only)
    variables = []
    for n in ATOMIC_NAMES: variables += [CA[n], SA[n]]
    for n in angles:       variables += [C[n], S[n]]
    for n in ratios:       variables += [QV[n]]
    # --- CANONICAL EQUATION ORDERING (lift-generator-v1, frozen) ---------
    #   block A: atomic Pythagorean, ATOMIC_NAMES order
    #   block B: per needed angle, (defining eq, Pythagorean), ANGLE_NAMES order
    #   block C: per needed ratio, defining eq, RATIO_NAMES order
    #   block D: constraint lifts, ASCENDING constraint index
    eqs = [ATOMIC_PYTH[n] for n in ATOMIC_NAMES]
    for n in angles: eqs += [EQ[n], pyth(n)]
    for n in ratios: eqs += [EQ[n]]
    cons = {i: constraint_lift(i) for i in subset}
    eqs += [cons[i] for i in subset]
    assert len(variables) == len(eqs), (subset, len(variables), len(eqs))
    return {"subset": subset, "variables": variables, "equations": eqs,
            "angles": angles, "ratios": ratios, "constraints": cons,
            "spec": SPEC_VERSION}

def system_hash(gen):
    payload = {"subset": list(gen["subset"]),
               "vars": [str(v) for v in gen["variables"]],
               "eqs": [str(sp.expand(e)) for e in gen["equations"]]}
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()

# ---------------------------------------------------------------------------
#  frozen-engine auxiliaries (all quantities) + validation
# ---------------------------------------------------------------------------
def engine_aux(bv, cv, dv, ev, gv, rv):
    s = RAO.chain(bv, cv, dv, ev, gv, math.pi/2 - rv)
    sub = {}
    for n, val in zip(ATOMIC_NAMES, (bv, cv, dv, ev, gv, rv)):
        sub[CA[n]] = math.cos(val); sub[SA[n]] = math.sin(val)
    for n in ANGLE_NAMES:
        sub[C[n]] = math.cos(s[n]); sub[S[n]] = math.sin(s[n])
    sub[QV["Q7"]]  = (math.sin(dv+gv)/math.sin(cv+dv))*(math.tan(s["x5"])/math.tan(s["x6"]))
    sub[QV["Q8"]]  = (math.sin(dv+gv)/math.sin(rv+cv))*(math.tan(s["x1"])/math.tan(s["x6"]))
    sub[QV["Q9"]]  = (math.sin(cv+dv)/math.sin(rv+dv))*(math.tan(s["x2"])/math.tan(s["x5"]))
    sub[QV["Q12"]] = (math.sin(dv+gv+s["v8"])/math.sin(dv+gv))*(math.tan(s["x6"])/math.tan(s["x10"]))
    sub[QV["Q20"]] = (math.sin(cv+dv+s["v9"]-s["v12"])/math.sin(dv+gv+s["v8"]))*(math.tan(s["x10"])/math.tan(s["x13"]))
    sub[QV["Q21"]] = (math.sin(bv+cv+dv+s["v8"])/math.sin(cv+dv+ev+s["v9"]))*(math.tan(s["x19"])/math.tan(s["x18"]))
    return sub, s

def _figs(n, seed=3):
    prop = (0.463752, 0.223255, 0.288990, 0.488181, 0.106157)
    rng = random.Random(seed); out = []
    while len(out) < n:
        al = rng.uniform(0.08, 0.30)
        j = [1 + rng.uniform(-0.05, 0.05) for _ in range(5)]
        bv, cv, dv, ev, gv = (al*p*x for p, x in zip(prop, j))
        try:
            sub, s = engine_aux(bv, cv, dv, ev, gv, al)
            out.append((sub, s, (bv, cv, dv, ev, gv, al)))
        except Exception:
            continue
    return out

def random_universe(n, seed=11):
    """n random well-posed size-six subsets (excludes the two singular supports)."""
    pool = list(range(3, 21)); rng = random.Random(seed); out = set()
    while len(out) < n:
        combo = tuple(sorted(rng.sample(pool, 4)))
        idx = {1, 2} | set(combo)
        if {8, 9, 16} <= idx or {16, 17, 18, 19} <= idx: continue
        out.add((1, 2) + combo)
    return sorted(out)

def validate_sample(n_subsets=12, n_figs=3, verbose=True):
    figs = _figs(n_figs)
    subs = random_universe(n_subsets)
    worst_chain = worst_cons = 0.0
    sq_ok = det_ok = True
    for subset in subs:
        gen = generate(subset)
        if len(gen["variables"]) != len(gen["equations"]): sq_ok = False
        if system_hash(gen) != system_hash(generate(subset)): det_ok = False
        for sub, s, arcs in figs:
            for e in gen["equations"][:-len(subset)]:        # chain+pyth eqs
                worst_chain = max(worst_chain, abs(float(e.subs(sub))))
            F = RAO.constraints(*arcs[:5], math.pi/2 - arcs[5])
            for i, e in gen["constraints"].items():
                pv = float(e.subs(sub))
                if i in CONS_COS:
                    X = CONS_COS[i][1]; expect = float(sub[C[X]]) * F[i]
                elif i in DOUBLED:
                    expect = math.cos(2*F[i]) - 1
                else:
                    expect = math.cos(F[i]) - 1
                worst_cons = max(worst_cons, abs(pv - expect))
    if verbose:
        print(f"validated {len(subs)} random subsets x {len(figs)} figures")
        print(f"  squareness (vars==eqs) all subsets : {sq_ok}")
        print(f"  determinism (stable system hash)   : {det_ok}")
        print(f"  max |chain/pyth eq| at engine vals  : {worst_chain:.2e}  (expect ~1e-15)")
        print(f"  max |constraint - engine*factor|    : {worst_cons:.2e}  (expect ~1e-15)")
        szs = [len(generate(x)["variables"]) for x in subs]
        print(f"  generated system sizes (vars)       : min {min(szs)}, max {max(szs)}")
    return worst_chain, worst_cons, sq_ok, det_ok

def emit_julia(subset, path):
    gen = generate(subset)
    jl = lambda e: str(sp.expand(e)).replace("**", "^")
    decl = " ".join(str(v) for v in gen["variables"])
    tag = "_".join(map(str, gen["subset"]))
    L = [f"# SPHERICAL homotopy solve — subset {gen['subset']}, r free (DEV)",
         f"# Generated by lift_generator.py.  system hash {system_hash(gen)[:16]}",
         "using HomotopyContinuation", f"@var {decl}", "eqs = ["]
    names = (["pyth_"+n for n in ATOMIC_NAMES]
             + sum([[n, "pyth_"+n] for n in gen["angles"]], [])
             + gen["ratios"] + [f"F{i}" for i in gen["subset"]])
    for nm, e in zip(names, gen["equations"]):
        L.append(f"    {jl(e)},   # {nm}")
    L += ["]", f"vars = [{', '.join(str(v) for v in gen['variables'])}]",
          "F = System(eqs; variables = vars)", "result = solve(F)",
          "cert = certify(F, solutions(result))   # Level-C certify of solutions FOUND",
          'println("paths: ", length(path_results(result)), '
          '"  real: ", length(real_solutions(result)))']
    open(path, "w").write("\n".join(L) + "\n")
    return system_hash(gen)

if __name__ == "__main__":
    print("=" * 70); print("LIFT GENERATOR — family validation"); print("=" * 70)
    validate_sample()
    g = generate((1, 2, 3, 4, 6, 7))
    print(f"\n{(1,2,3,4,6,7)} -> {len(g['variables'])} vars, hash {system_hash(g)[:16]}")
