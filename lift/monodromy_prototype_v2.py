#!/usr/bin/env python3
"""monodromy_prototype_v2.py — Step B: a single-subset, seeded monodromy footer.

Answers ONE question: can a seeded continuation traverse the spherical fiber at
all, avoiding the polyhedral start-system overflow that killed `solve(F)`?

Method (coefficient-parameter homotopy + monodromy, the rigorous recipe):
  * Parametrize the CONSTRAINT equations only, additively:  g_i(x) - p_i = 0.
    The structural identities (atomic/angle Pythagorean, angle & ratio
    definitions) are held FIXED, so the lifted seed stays an exact solution of
    the family at the true parameters p0 = 0.
  * Step 1: seed x0 (frozen engine_aux lift of a base root) solves F(x0; 0)=0.
  * Step 2: track x0 from p0=0 to a GENERIC complex p_gen along one path
    (a single tracker call — no start-system construction, no overflow).
  * Step 3: monodromy_solve at p_gen, where the trace test is valid (generic
    parameters), certifying completeness of the generic fiber.
  * Step 4: track the full certified generic fiber back to the true system
    p0 = 0. The finite limits are the solutions of OUR system; some generic
    paths may diverge/collide at the special member (expected, not an error).

This module is ORCHESTRATION: it consumes the FROZEN generator's system and
serialization; it does not modify lift_generator. Julia is NOT run here — this
script generates the .jl and provides the Python preflight (verify_seed) and
result summarizer (summarize) that DO run without Julia.
"""
import sys, os, math, json
_here = os.path.dirname(os.path.abspath(__file__))
_root = os.path.dirname(_here)
sys.path.insert(0, _root)
sys.path.insert(0, _here)
import sympy as sp
import numpy as np
import lift_generator as LG
import lift_generator_v2 as V2          # regularized lift (sin-form arc-equalities)
LIFT = V2                                # active monodromy target: the regular v2 lift

DEG = math.pi / 180.0
JL = lambda e: str(sp.expand(e)).replace("**", "^")     # FROZEN serialization rule


def _split(gen):
    sub = gen["subset"]
    cons = [gen["constraints"][i] for i in sub]          # ascending, == tail
    n = len(cons)
    structural = gen["equations"][:-n]
    assert gen["equations"][-n:] == cons, "constraint tail mismatch"
    return structural, cons


def _polish(subset, base):
    """Drive the seed to full float64 precision on the raw constraints before
    lifting, so the regular v2 system gets an accurate start solution."""
    from scipy.optimize import fsolve
    import warnings
    x0 = np.array([*base[:5], base[5] * DEG])
    def F(x):
        d = LIFT.RAO.constraints(*x[:5], x[5]); return [d[i] for i in subset]
    try:
        r0 = max(abs(v) for v in F(x0))
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            sol = fsolve(F, x0, xtol=1e-15)
        if max(abs(v) for v in F(sol)) <= r0:
            return (*sol[:5], sol[5] / DEG)
    except (ArithmeticError, ValueError, RuntimeError):
        pass
    return base


def lift_seed(subset, base, polish=True):
    if polish:
        base = _polish(tuple(sorted(subset)), base)
    b, c, d, e, g, h_deg = base
    r = math.pi / 2 - h_deg * DEG
    sub, _ = LIFT.engine_aux(b, c, d, e, g, r)
    gen = LIFT.generate(subset)
    vec = [float(sub[v]) for v in gen["variables"]]
    return gen, sub, vec


def verify_seed(subset, base):
    """Preflight: confirm x0 solves the PARAMETRIZED family at p0=0, so the
    monodromy run starts on a genuine solution. Returns (struct_max, cons_max)."""
    gen, sub, vec = lift_seed(subset, base)
    structural, cons = _split(gen)
    fs = sp.lambdify(gen["variables"], structural, modules=["math"])
    fc = sp.lambdify(gen["variables"], cons, modules=["math"])
    sres = [abs(float(v)) for v in fs(*vec)]             # structural: identities
    cres = [abs(float(v)) for v in fc(*vec)]             # constraints minus p_i (p0=0)
    return max(sres), max(cres), vec


def emit(subset, base, path, seed=None):
    """Write the seeded monodromy Julia script for `subset`, seeded by `base`."""
    gen, sub, vec = lift_seed(subset, base)
    structural, cons = _split(gen)
    ncons = len(cons)
    decl = " ".join(str(v) for v in gen["variables"])
    pdecl = " ".join(f"p{i}" for i in range(1, ncons + 1))
    plist = ", ".join(f"p{i}" for i in range(1, ncons + 1))
    vlist = ", ".join(str(v) for v in gen["variables"])
    x0 = "ComplexF64[" + ", ".join(repr(v) for v in vec) + "]"

    L = [f"# SPHERICAL monodromy prototype — subset {gen['subset']}  [lift-generator-v2, regular]",
         f"# system hash {LIFT.system_hash(gen)[:16]} ; seed = polished lifted base root",
         "using HomotopyContinuation, LinearAlgebra, Random",
         f"Random.seed!({seed if seed is not None else 0})",
         f"@var {decl}",
         f"@var {pdecl}",
         "eqs = ["]
    names = (["pyth_" + n for n in LIFT.ATOMIC_NAMES]
             + sum([[n, "pyth_" + n] for n in gen["angles"]], [])
             + gen["ratios"])
    for nm, e in zip(names, structural):
        L.append(f"    {JL(e)},   # {nm}")
    for k, (i, e) in enumerate(zip(gen["subset"], cons), 1):
        L.append(f"    ({JL(e)}) - p{k},   # F{i}")
    L += ["]",
          f"vars = [{vlist}]",
          f"params = [{plist}]",
          "F = System(eqs; variables = vars, parameters = params)",
          f"x0 = {x0}",
          f"p0 = zeros(ComplexF64, {ncons})",
          "",
          "# Step 1: seed validated in Python (structural & constraint ~1e-16).",
          "# Step 2: one path from the true system to generic parameters.",
          f"p_gen = randn(ComplexF64, {ncons})",
          "R2 = solve(F, [x0]; start_parameters = p0, target_parameters = p_gen)",
          "xg = solutions(R2)",
          'println("step2 tracked seed->generic: ", length(xg), " solution(s)")',
          "",
          "# Step 3: monodromy at generic parameters (trace test valid here).",
          "MR = monodromy_solve(F, xg, p_gen)",
          'println("monodromy: nsolutions=", nsolutions(MR),',
          '        "  success(trace/complete)=", is_success(MR))',
          "complete = false",
          "try",
          "    complete = verify_solution_completeness(F, MR)",
          "catch err",
          '    println("verify_solution_completeness unavailable: ", err)',
          "end",
          'println("verify_solution_completeness=", complete)',
          "",
          "# Step 4: track the certified generic fiber back to the true system.",
          "R4 = solve(F, solutions(MR); start_parameters = p_gen,",
          "           target_parameters = p0)",
          "sols = solutions(R4; only_nonsingular = false)",
          'println("step4 finite at true system: ", length(sols), " solution(s)")',
          "",
          "# recover (b,c,d,e,g,h) from first 12 atomic components; flag imag norm",
          "open(ARGS[1], \"w\") do io",
          "    for s in sols",
          "        im = maximum(abs.(imag.(s)))",
          "        b=atan(real(s[2]),real(s[1])); c=atan(real(s[4]),real(s[3]))",
          "        d=atan(real(s[6]),real(s[5])); e=atan(real(s[8]),real(s[7]))",
          "        g=atan(real(s[10]),real(s[9])); r=atan(real(s[12]),real(s[11]))",
          "        h=(pi/2-r)*180/pi",
          "        write(io, \"{\\\"coords\\\":[$b,$c,$d,$e,$g],\\\"h\\\":$h,\\\"im\\\":$im}\\n\")",
          "    end",
          "end",
          'println("wrote candidates -> ", ARGS[1])']
    open(path, "w").write("\n".join(L) + "\n")
    return LIFT.system_hash(gen)


def summarize(subset, base, cand_path):
    """Ingest the Julia candidate file: count real / admissible (round-trip via
    the FROZEN engine), and check whether the seed base root is recovered."""
    RAO = LIFT.RAO
    raw = [json.loads(l) for l in open(cand_path) if l.strip()]
    real_ct = adm_ct = 0
    accepted = []
    for r in raw:
        is_real = r.get("im", 1.0) < 1e-8
        real_ct += is_real
        if not is_real:
            continue
        coords, h = r["coords"], r["h"]
        rr = math.pi / 2 - h * DEG
        if min(coords) <= 1e-6 or coords[1] >= rr or coords[2] >= rr:
            continue
        try:
            F = RAO.constraints(*coords, h * DEG)
        except Exception:
            continue
        if max(abs(F[i]) for i in subset) < 1e-7:
            adm_ct += 1
            accepted.append((coords, h))
    seed_found = any(max(abs(a - b) for a, b in
                         zip([*c, hh * DEG], [*base[:5], base[5] * DEG])) < 1e-6
                     for c, hh in accepted)
    print(f"  raw solutions returned : {len(raw)}")
    print(f"  real (|imag|<1e-8)     : {real_ct}")
    print(f"  admissible (round-trip): {adm_ct}")
    print(f"  seed recovered         : {seed_found}")
    return len(raw), real_ct, adm_ct, seed_found


def _selftest():
    SUB = (1, 2, 3, 4, 6, 7)
    NEWTON = (0.6246238466927992, 0.7044304165359816, 0.7482768099360514,
              0.6307397242292889, 0.3136386632298885, 22.64768569612002)
    print("MONODROMY PROTOTYPE self-test (generation + seed preflight; no Julia)")
    ok = True
    def chk(n, c):
        nonlocal ok; print(f"  [{'PASS' if c else 'FAIL'}] {n}"); ok = ok and c

    sm, cm, vec = verify_seed(SUB, NEWTON)
    print(f"    seed structural max = {sm:.3e}   constraint(@p0) max = {cm:.3e}")
    chk("seed solves parametrized family at p0=0 (structural < 1e-11)", sm < 1e-11)
    chk("seed solves constraints at p0=0 (< 1e-9)", cm < 1e-9)
    chk("seed dimension == 54", len(vec) == 54)

    h = emit(SUB, NEWTON, "monodromy_v2_1_2_3_4_6_7.jl", seed=1)
    txt = open("monodromy_v2_1_2_3_4_6_7.jl").read()
    chk("emits monodromy_solve", "monodromy_solve" in txt)
    chk("emits seed->generic path (Step 2)", "start_parameters = p0" in txt
        and "target_parameters = p_gen" in txt)
    chk("emits track-back to true system (Step 4)", "target_parameters = p0" in txt)
    chk("emits parameters block", "parameters = params" in txt)
    chk("emits trace-test/completeness check", "verify_solution_completeness" in txt)
    chk("emits ARGS[1] candidate output", "ARGS[1]" in txt)
    chk("constraint count parametrized == 6",
        txt.count(") - p") == 6)
    print("MONODROMY PROTOTYPE:", "ALL PASS" if ok else "FAILURES ABOVE")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(_selftest())
