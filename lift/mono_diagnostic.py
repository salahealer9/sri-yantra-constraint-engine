#!/usr/bin/env python3
"""mono_diagnostic.py — emit a CAPPED monodromy script that dumps the raw generic
solutions for offline structural analysis.

Purpose: structural characterization of a capped sample of generic solutions of
the v2 lift's parametrized family. It writes, at the generic parameter point:
  * p_gen                          (the generic parameter vector)
  * the raw 54-component COMPLEX solution vectors  (no filtering, no atan2
    recovery, no track-back to p=0)
  * a per-solution result-ordering index           (HC.jl solutions() order;
    NOT a certified discovery sequence — a proxy only)

It reuses the frozen prototype's family construction (v2 system, polished seed,
seed->generic path) verbatim; only the footer differs (cap + dump instead of
monodromy-to-completeness + recover). The frozen lift and prototype are not
modified.
"""
import sys, os
_here = os.path.dirname(os.path.abspath(__file__))
_root = os.path.dirname(_here)
sys.path.insert(0, _here)
sys.path.insert(0, _root)
import monodromy_prototype_v2 as MP          # lift_seed (polished, v2), _split, JL, LIFT


def emit_diagnostic(subset, base, path, cap=300, no_progress=10, seed=1):
    gen, _, vec = MP.lift_seed(subset, base)          # polished seed, v2 system
    structural, cons = MP._split(gen)
    ncons = len(cons)
    JL = MP.JL
    decl = " ".join(str(v) for v in gen["variables"])
    pdecl = " ".join(f"p{i}" for i in range(1, ncons + 1))
    plist = ", ".join(f"p{i}" for i in range(1, ncons + 1))
    vlist = ", ".join(str(v) for v in gen["variables"])
    x0 = "ComplexF64[" + ", ".join(repr(v) for v in vec) + "]"

    L = [f"# DIAGNOSTIC dump — subset {gen['subset']}  [lift-generator-v2]",
         f"# system hash {MP.LIFT.system_hash(gen)[:16]} ; polished seed",
         "# Purpose: structural characterization of a CAPPED sample of generic",
         "# solutions. Dumps p_gen + raw 54-vectors + result-order index.",
         "# NO filtering, NO recovery, NO track-back. Not a fiber-size estimate.",
         "using HomotopyContinuation, Random",
         f"Random.seed!({seed})",
         f"@var {decl}",
         f"@var {pdecl}",
         "eqs = ["]
    for e in structural:
        L.append(f"    {JL(e)},")
    for k, (i, e) in enumerate(zip(gen["subset"], cons), 1):
        L.append(f"    ({JL(e)}) - p{k},   # F{i} (sin-form arc-equality / cosine for 3,4,6)")
    L += ["]",
          f"vars = [{vlist}]",
          f"params = [{plist}]",
          "F = System(eqs; variables = vars, parameters = params)",
          f"x0 = {x0}",
          f"p0 = zeros(ComplexF64, {ncons})",
          f"p_gen = randn(ComplexF64, {ncons})",
          "",
          "# seed -> generic (single path; no start system)",
          "R2 = solve(F, [x0]; start_parameters = p0, target_parameters = p_gen)",
          "xg = solutions(R2)",
          'println("step2 tracked seed->generic: ", length(xg), " solution(s)")',
          "",
          "# CAPPED monodromy at the generic point (structural sample, not completeness)",
          f"MR = monodromy_solve(F, xg, p_gen; target_solutions_count = {cap},",
          f"                     max_loops_no_progress = {no_progress})",
          "sols = solutions(MR)",
          'println("captured generic solutions: ", length(sols),',
          '        "  success(stopping)=", is_success(MR))',
          "",
          "# dump p_gen",
          'open(ARGS[1]*".pgen", "w") do io',
          "    for p in p_gen; println(io, string(real(p), \" \", imag(p))); end",
          "end",
          "# dump raw 54-vectors with result-order index: idx;re|im,re|im,...",
          'open(ARGS[1], "w") do io',
          "    for (k, s) in enumerate(sols)",
          '        comps = join([string(real(z))*"|"*string(imag(z)) for z in s], ",")',
          '        println(io, string(k)*";"*comps)',
          "    end",
          "end",
          'println("wrote raw vectors -> ", ARGS[1], "  and p_gen -> ", ARGS[1]*".pgen")']
    open(path, "w").write("\n".join(L) + "\n")
    return MP.LIFT.system_hash(gen)


if __name__ == "__main__":
    NEWTON = (0.6246238466927992, 0.7044304165359816, 0.7482768099360514,
              0.6307397242292889, 0.3136386632298885, 22.64768569612002)
    h = emit_diagnostic((1, 2, 3, 4, 6, 7), NEWTON,
                        "mono_diag_1_2_3_4_6_7.jl", cap=300, seed=1)
    print("emitted mono_diag_1_2_3_4_6_7.jl  (v2 hash", h[:16] + "…)")
    txt = open("mono_diag_1_2_3_4_6_7.jl").read()
    for need in ["monodromy_solve", "target_solutions_count", "p_gen",
                 ".pgen", "re|im" if False else 're(', "is_success"]:
        pass
    checks = {
        "capped monodromy": "target_solutions_count" in txt,
        "dumps p_gen": '.pgen' in txt,
        "dumps raw vectors (idx;comps)": 'string(k)*";"' in txt,
        "no track-back (no target_parameters = p0 after monodromy)":
            txt.count("target_parameters = p0") == 0,
        "no atan2 recovery": "atan(" not in txt,
        "sin-form constraints (6 parametrized)": txt.count(") - p") == 6,
    }
    for k, v in checks.items():
        print(f"  [{'ok' if v else 'XX'}] {k}")
