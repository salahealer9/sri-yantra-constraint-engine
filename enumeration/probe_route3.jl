# Route-3 decisive probe: certified real-root enumeration for subset {1,2,3,4,8}
# via interval-Newton (Krawczyk) contraction + branch-and-prune.
#
# DEV / pre-confirmatory. The Python probe (route3_probe.py) established the
# preconditions: the engine constraints are cleanly interval-evaluable (F2 in
# w = sqrt(x7^2+V7^2) form, no transcendentals), pruning works, and the search
# has no breadth explosion. What naive exclusion could NOT do is LOCALIZE roots
# (interval overestimation leaves a fuzzy candidate cloud). Krawczyk contraction
# is the standard fix: it contracts boxes onto true roots and certifies
# existence + uniqueness, collapsing the cloud to isolated certified points.
#
# This is the test that decides whether real-box completeness is feasible.
#
# Run:  julia -t 4 probe_route3.jl
# Requires: julia -e 'using Pkg; Pkg.add(["IntervalArithmetic","IntervalRootFinding","StaticArrays"])'
#
# API NOTE: IntervalRootFinding.jl's surface has shifted across versions
# (roots signature, Root.region vs .interval, status symbols). If a call errors,
# it is a one-line API fix for your installed version, NOT a method failure --
# treat it like the earlier HomotopyContinuation.jl signature fixes.

using IntervalArithmetic, IntervalRootFinding, StaticArrays

# ---- the five {1,2,3,4,8} constraints, r = 1 (rational + sqrt; F2 via w-form) ----
function F(X)
    b, c, d, e, g = X[1], X[2], X[3], X[4], X[5]
    x1  = sqrt(1 - c^2)
    x2  = sqrt(1 - d^2)
    x3  = (1 - c)/(1 + d) * x2
    x4  = (1 - d)/(1 + c) * x1
    x5  = b/(b + c + d) * x4
    x6  = e/(c + d + e) * x3
    Q7  = (d + g)/(c + d) * (x5/x6); U7 = (d + g)/(Q7 + 1); V7 = (d + g) - U7
    x7  = U7/(c + d) * x5
    w   = sqrt(x7^2 + V7^2)
    rT  = x7*(w - x7)/V7
    Q8  = (d + g)/(1 + c) * (x1/x6); U8 = (1 + g)/(Q8 + 1); V8 = (1 + g) - U8
    v8  = 1 - U8 - d
    x16 = (d + e + g)/(d + g) * x6
    x11 = (d + g)/(c + d) * x5
    Q9  = (c + d)/(1 + d) * (x2/x5); U9 = (1 + d)/(Q9 + 1); v9 = 1 - U9 - c
    x10 = (b + c - g)/(b + c + d) * x4
    S12 = d + g + v8; Q12 = S12/(d + g) * (x6/x10); U12 = S12/(Q12 + 1); v12 = d + g - U12
    x13 = (e + v12)/(c + d + e) * x3
    x11a = (v9 + c - g)/(v9 + c + d - v12) * x13
    r16 = sqrt((d + e)^2 + x16^2)
    F1 = x11 - x11a
    F2 = d - U7 - rT
    F3 = -(V8^2)/2 + 1.5*x10^2
    F4 = -((c + d + v9 - v12)^2)/2 + 1.5*x13^2
    F8 = 1 - r16
    return SVector(F1, F2, F3, F4, F8)
end

# ---- admissible search box (contains Rao's solution; ~ Rao-range +50%) ----
# (IntervalBox was removed in IntervalArithmetic v0.22; the box is a vector.)
X = [interval(0.20, 0.80),   # b
     interval(0.10, 0.45),   # c
     interval(0.15, 0.45),   # d
     interval(0.25, 0.75),   # e
     interval(0.03, 0.25)]   # g

println("Route-3 certified root enumeration, subset {1,2,3,4,8}")
println("box: b[0.20,0.80] c[0.10,0.45] d[0.15,0.45] e[0.25,0.75] g[0.03,0.25]")

t = @elapsed rts = roots(F, X; contractor = Krawczyk)

# --- version-robust accessors (Root fields/helpers moved across releases) ---
function reg(r)
    try; return r.region; catch; end
    try; return root_region(r); catch; end
    try; return r.interval; catch; end
    error("cannot get region from Root; inspect typeof/fieldnames below")
end
function sta(r)
    try; return r.status; catch; end
    try; return root_status(r); catch; end
    error("cannot get status from Root; inspect typeof/fieldnames below")
end

println("\nRoot type: ", isempty(rts) ? "(none)" : typeof(rts[1]))
if !isempty(rts)
    println("Root fields: ", fieldnames(typeof(rts[1])))
    println("first root (raw): ", rts[1])
end

nun = count(r -> sta(r) == :unique,  rts)
nuk = count(r -> sta(r) == :unknown, rts)
println("\nroots returned : ", length(rts))
println("  :unique  (certified existence + uniqueness) : ", nun)
println("  :unknown (needs refinement / boundary)      : ", nuk)
println("wall time: ", round(t, digits=2), "s")

rao = [0.463752, 0.223255, 0.288990, 0.488181, 0.106157]
for r in rts
    m = mid.(reg(r))
    near = maximum(abs.(m .- rao)) < 0.02 ? "   <- Rao {1,2,3,4,8}" : ""
    println("  ", sta(r), "  (b,c,d,e,g) = ", round.(m, digits=5), near)
end

println("\nVERDICT:")
if nuk == 0 && nun >= 1
    println("  DECISIVE — every root certified :unique, none :unknown.")
    println("  Real-box completeness is FEASIBLE: this box's admissible figures")
    println("  are enumerated with a rigorous certificate. Route 3 works.")
elseif nun >= 1
    println("  PROMISING but ", nuk, " :unknown box(es) remain — tighten tolerance")
    println("  or subdivide the :unknown regions; not yet a full certificate.")
else
    println("  No certified roots — check the box / API / tolerance before concluding.")
end
