#!/usr/bin/env python3
"""gate_x.py — instrumented runner + classifier for the Gate X feasibility
benchmark (see gate-X-preregistration.md).

Two phases:
  emit_gate_x(...)   -> writes the budget-capped monodromy Julia script.
  classify(...)      -> ingests the Julia forensic JSON, applies Gate-4 to the
                        tracked-back real candidates, assigns PASS / FAIL /
                        TECHNICAL INCONCLUSIVE per the frozen rule, prints report.

Frozen Gate X parameters (must match the preregistration):
  subset {1,2,3,4,6,7}; wall-clock 2 h; 8 threads; max_loops_no_progress 10;
  random seed 20260624; PASS = is_success(MR); verify_solution_completeness is
  forensic-only. The seed is the polished v2 seed (lift_seed, v2).

The Julia footer reuses the frozen v2 family construction verbatim and writes a
forensic JSON on EVERY exit path (clean, cap-stop, or exception), so a FAIL or a
cap-termination still leaves full diagnostics behind.
"""
import sys, os, json, math
_here = os.path.dirname(os.path.abspath(__file__))
_root = os.path.dirname(_here)
sys.path.insert(0, _here)
sys.path.insert(0, _root)
import monodromy_prototype_v2 as MP            # lift_seed (polished, v2), _split, JL, LIFT

DEG = math.pi / 180.0
GATEX = dict(subset=(1, 2, 3, 4, 6, 7), wall_clock_s=7200, threads=8,
             max_loops_no_progress=10, random_seed=20260624)


def emit_gate_x(path, subset=None, base=None, params=GATEX):
    subset = subset or params["subset"]
    if base is None:
        # default benchmark seed: the known root for {1,2,3,4,6,7}
        base = (0.6246238466927992, 0.7044304165359816, 0.7482768099360514,
                0.6307397242292889, 0.3136386632298885, 22.64768569612002)
    gen, _, vec = MP.lift_seed(subset, base)          # polished seed, v2 system
    structural, cons = MP._split(gen)
    ncons = len(cons); JL = MP.JL
    decl = " ".join(str(v) for v in gen["variables"])
    pdecl = " ".join(f"p{i}" for i in range(1, ncons + 1))
    plist = ", ".join(f"p{i}" for i in range(1, ncons + 1))
    vlist = ", ".join(str(v) for v in gen["variables"])
    x0 = "ComplexF64[" + ", ".join(repr(v) for v in vec) + "]"
    S = params["random_seed"]; T = params["wall_clock_s"]; NP = params["max_loops_no_progress"]

    L = [f"# GATE X feasibility benchmark — subset {gen['subset']}  [lift-generator-v2]",
         f"# system hash {MP.LIFT.system_hash(gen)[:16]} ; wall-clock {T}s ; "
         f"no_progress {NP} ; seed {S}",
         "# Writes forensic JSON to ARGS[1] on EVERY exit path (clean/cap/exception).",
         "using HomotopyContinuation, Random",
         f"Random.seed!({S})",
         f"@var {decl}",
         f"@var {pdecl}",
         "eqs = ["]
    for e in structural:
        L.append(f"    {JL(e)},")
    for k, (i, e) in enumerate(zip(gen["subset"], cons), 1):
        L.append(f"    ({JL(e)}) - p{k},   # F{i}")
    L += ["]",
          f"vars = [{vlist}]",
          f"params = [{plist}]",
          "F = System(eqs; variables = vars, parameters = params)",
          f"x0 = {x0}",
          f"p0 = zeros(ComplexF64, {ncons})",
          f"p_gen = randn(ComplexF64, {ncons})",
          "",
          "function write_forensic(d)",
          "    open(ARGS[1], \"w\") do io",
          "        print(io, \"{\")",
          "        ks = collect(keys(d)); ",
          "        for (n,k) in enumerate(ks)",
          "            print(io, \"\\\"\", k, \"\\\":\", d[k])",
          "            n < length(ks) && print(io, \",\")",
          "        end",
          "        print(io, \"}\")",
          "    end",
          "end",
          "",
          "t0 = time()",
          "err_kind = \"none\"; is_ok = \"null\"; n_gen = 0; vsc = \"not_attempted\"",
          "stopping = \"unknown\"; cands = String[]",
          "try",
          "    R2 = solve(F, [x0]; start_parameters = p0, target_parameters = p_gen)",
          "    xg = solutions(R2)",
          "    if length(xg) == 0",
          "        err_kind = \"seed_to_generic_failed\"",
          "    else",
          "        # CAPPED full monodromy: wall-clock timeout + no-progress stop",
          f"        MR = monodromy_solve(F, xg, p_gen; seed = UInt32({S}),",
          f"                             max_loops_no_progress = {NP}, timeout = {float(T)},",
          "                             show_progress = true)",
          "        is_ok = is_success(MR) ? \"true\" : \"false\"",
          "        n_gen = nsolutions(MR)",
          "        stopping = is_success(MR) ? \"trace_test_complete\" : \"budget_or_no_progress\"",
          "        # verify_solution_completeness — FORENSIC ONLY, never affects PASS/FAIL",
          "        try; vsc = string(verify_solution_completeness(F, MR));",
          "        catch e2; vsc = \"exception:\"*string(typeof(e2)); end",
          "        # track back to the true system p0 and emit real candidates",
          "        try",
          "            R4 = solve(F, solutions(MR); start_parameters = p_gen,",
          "                       target_parameters = p0)",
          "            for s in solutions(R4; only_nonsingular = false)",
          "                im = maximum(abs.(imag.(s)))",
          "                b=atan(real(s[2]),real(s[1])); c=atan(real(s[4]),real(s[3]))",
          "                d=atan(real(s[6]),real(s[5])); e=atan(real(s[8]),real(s[7]))",
          "                g=atan(real(s[10]),real(s[9])); r=atan(real(s[12]),real(s[11]))",
          "                h=(pi/2-r)*180/pi",
          "                push!(cands, \"{\\\"coords\\\":[$b,$c,$d,$e,$g],\\\"h\\\":$h,\\\"im\\\":$im}\")",
          "            end",
          "        catch e3; end",
          "    end",
          "catch e",
          "    err_kind = string(typeof(e))",
          "end",
          "elapsed = time() - t0",
          "",
          "d = Dict(",
          f"  \"subset\" => \"{list(gen['subset'])}\",",
          "  \"elapsed_s\" => round(elapsed, digits=1),",
          "  \"n_generic\" => n_gen,",
          "  \"is_success\" => is_ok,",
          "  \"stopping_reason\" => \"\\\"\"*stopping*\"\\\"\",",
          "  \"verify_solution_completeness\" => \"\\\"\"*vsc*\"\\\"\",",
          "  \"error_kind\" => \"\\\"\"*err_kind*\"\\\"\",",
          f"  \"wall_clock_cap_s\" => {T},",
          f"  \"max_loops_no_progress\" => {NP},",
          f"  \"random_seed\" => {S},",
          "  \"trackback_candidates\" => \"[\"*join(cands, \",\")*\"]\"",
          ")",
          "write_forensic(d)",
          'println("GATE X forensic written -> ", ARGS[1],',
          '        "  is_success=", is_ok, "  n_generic=", n_gen,',
          '        "  elapsed=", round(elapsed,digits=1), "s  err=", err_kind)']
    open(path, "w").write("\n".join(L) + "\n")
    return MP.LIFT.system_hash(gen)


def classify(forensic_path, subset=None):
    """Assign PASS / FAIL / TECHNICAL INCONCLUSIVE per the frozen rule and apply
    Gate-4 to the tracked-back real candidates."""
    subset = tuple(subset or GATEX["subset"])
    d = json.load(open(forensic_path))
    print("=" * 70)
    print(" GATE X — OUTCOME CLASSIFICATION")
    print("=" * 70)
    for k in ("subset", "elapsed_s", "n_generic", "is_success", "stopping_reason",
              "error_kind", "verify_solution_completeness", "wall_clock_cap_s",
              "max_loops_no_progress", "random_seed"):
        print(f"  {k:24s}: {d.get(k)}")

    err = str(d.get("error_kind", "")).strip('"')
    is_ok = str(d.get("is_success", "null")).strip('"')

    # outcome rule (frozen)
    if err not in ("none", "") or is_ok not in ("true", "false"):
        outcome = "TECHNICAL INCONCLUSIVE"
        why = f"primary verdict unreadable / error_kind={err!r} is_success={is_ok!r}"
    elif is_ok == "true":
        outcome = "PASS"
        why = "is_success(MR) == true within budget"
    else:
        outcome = "FAIL"
        why = "budget exhausted without trace-test completeness (clean run)"

    # Gate-4 on tracked-back candidates (forensic; resolves '1 vs 3 vs crash')
    cands = d.get("trackback_candidates", [])
    if isinstance(cands, str):
        cands = json.loads(cands)
    cert = 0
    if cands:
        try:
            import sriyantra as RAO, spherical_geo_check as GC
            for cnd in cands:
                if cnd.get("im", 1.0) >= 1e-8:
                    continue
                co, h = cnd["coords"], cnd["h"]
                try:
                    F = RAO.constraints(*co, h * DEG)
                    if max(abs(F[i]) for i in subset) < 1e-7 and \
                       GC.gate4(*co, h * DEG, closure_tol=1e-7)[0]:
                        cert += 1
                except Exception:
                    pass
            print(f"\n  tracked-back real candidates : {len(cands)}")
            print(f"  certified admissible (Gate-4): {cert}")
        except Exception as ex:
            print(f"\n  (Gate-4 unavailable here: {ex}; candidates archived, "
                  f"certify on server)")
    print(f"\n  OUTCOME: {outcome}")
    print(f"  reason : {why}")
    print("\n  (TECHNICAL INCONCLUSIVE -> re-run; never PASS/FAIL.")
    print("   verify_solution_completeness is forensic only, not part of the rule.)")
    return outcome


def _selftest():
    print("GATE X self-test (emission + classifier; no Julia)")
    ok = True
    def chk(n, c):
        nonlocal ok; print(f"  [{'PASS' if c else 'FAIL'}] {n}"); ok = ok and c
    h = emit_gate_x("gate_x_bench.jl")
    txt = open("gate_x_bench.jl").read()
    chk("emits monodromy_solve", "monodromy_solve" in txt)
    chk("embeds wall-clock timeout 7200", "timeout = 7200.0" in txt)
    chk("embeds max_loops_no_progress 10", "max_loops_no_progress = 10" in txt)
    chk("embeds random seed 20260624", "20260624" in txt)
    chk("PASS verdict via is_success", "is_success(MR)" in txt)
    chk("verify_solution_completeness present (forensic)", "verify_solution_completeness" in txt)
    chk("NOT capped by target_solutions_count", "target_solutions_count" not in txt)
    chk("tracks back to p0", "target_parameters = p0" in txt)
    chk("forensic written on every path (try/catch + write)", "write_forensic" in txt)
    chk("6 sin-form constraints parametrized", txt.count(") - p") == 6)
    os.remove("gate_x_bench.jl")

    # classifier on synthetic forensic JSONs
    import tempfile
    def mk(d):
        p = tempfile.mktemp(suffix=".json"); json.dump(d, open(p, "w")); return p
    base = {"subset": "[1, 2, 3, 4, 6, 7]", "elapsed_s": 12.0, "n_generic": 5,
            "stopping_reason": "x", "verify_solution_completeness": "y",
            "wall_clock_cap_s": 7200, "max_loops_no_progress": 10,
            "random_seed": 20260624, "trackback_candidates": "[]"}
    chk("classifies PASS",  classify(mk({**base, "is_success": "true",  "error_kind": "none"})) == "PASS")
    chk("classifies FAIL",  classify(mk({**base, "is_success": "false", "error_kind": "none"})) == "FAIL")
    chk("classifies TECH (exception)", classify(mk({**base, "is_success": "null", "error_kind": "OutOfMemoryError"})) == "TECHNICAL INCONCLUSIVE")
    chk("verify_solution_completeness exception does NOT change PASS",
        classify(mk({**base, "is_success": "true", "error_kind": "none", "verify_solution_completeness": "exception:Foo"})) == "PASS")
    print("\nGATE X SELF-TEST:", "ALL PASS" if ok else "FAILURES ABOVE")
    return 0 if ok else 1


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--emit":
        h = emit_gate_x(sys.argv[2] if len(sys.argv) > 2 else "gate_x_bench.jl")
        print("emitted (v2 hash", h[:16] + "…)")
    elif len(sys.argv) > 1 and sys.argv[1] == "--classify":
        classify(sys.argv[2])
    else:
        sys.exit(_selftest())
