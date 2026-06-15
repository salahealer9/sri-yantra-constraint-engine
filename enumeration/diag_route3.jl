# Route-3 diagnostic: BEFORE trusting any full-box verdict, separate
#   (a) "Julia F is transcribed wrong"      -> validate F at Rao's point
#   (b) "solver can't certify a simple root"-> certify known root in a TIGHT box
#   (c) "full-box search settings too coarse"-> compare tight vs full
#
# {1,2,3,4,8} is well-posed (no lattice identity is contained in it), so its
# 5x5 Jacobian is generically full rank and Rao's root is SIMPLE -> Krawczyk
# should certify it as :unique in a tight box. If it does, the all-:unknown
# full-box run is a tolerance/overestimation issue, not an obstruction.
#
# Run:  julia -t 4 enumeration/diag_route3.jl 2>&1 | tee enumeration/logs/diag_route3.txt

using IntervalArithmetic, IntervalRootFinding, StaticArrays

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
    return SVector(x11 - x11a,
                   d - U7 - rT,
                   -(V8^2)/2 + 1.5*x10^2,
                   -((c + d + v9 - v12)^2)/2 + 1.5*x13^2,
                   1 - r16)
end

rao = [0.463752, 0.223255, 0.288990, 0.488181, 0.106157]
# engine values at Rao (from the validated Python engine), for cross-check:
eng = [-3.469e-7, +9.659e-8, +5.838e-7, -5.292e-7, -2.670e-7]

println("="^64)
println("STAGE 0 — validate Julia F at Rao's point vs the engine")
println("="^64)
Xpt = [interval(v, v) for v in rao]      # degenerate (point) intervals
Fpt = F(Xpt)
okall = true
for i in 1:5
    fi = Fpt[i]
    ok = abs(mid(fi) - eng[i]) < 5e-7
    global okall
    okall &= ok
    println("  F$(i): julia=", round(mid(fi), sigdigits=4),
            "  engine=", eng[i], "  match=", ok)
end
println("  Julia chain matches engine: ", okall)
if !okall
    println("  >> TRANSCRIPTION BUG in Julia F — fix before any solver verdict.")
end

println()
println("="^64)
println("STAGE 1 — certify the KNOWN root in a tight box (±0.012)")
println("="^64)
h = 0.012
Xt = [interval(v - h, v + h) for v in rao]
for (name, ctor) in (("Krawczyk", Krawczyk), ("Newton", Newton))
    rts = roots(F, Xt; contractor = ctor)
    nun = count(r -> r.status == :unique,  rts)
    nuk = count(r -> r.status == :unknown, rts)
    println("  $name: ", length(rts), " root(s)  unique=", nun, "  unknown=", nuk)
    for r in rts
        m = mid.(r.region)
        near = maximum(abs.(m .- rao)) < 0.012 ? "  <- Rao" : ""
        println("     ", r.status, "  ", round.(m, digits=5), near)
    end
end

println()
println("VERDICT:")
println("  - If STAGE 0 fails  -> Julia F typo; the earlier full-box run was meaningless.")
println("  - If STAGE 1 gives :unique at Rao -> METHOD WORKS; full-box all-:unknown")
println("    was a tolerance/overestimation issue (refine search, not a wall).")
println("  - If STAGE 1 is all :unknown on a tight box around a simple root ->")
println("    deeper conditioning issue; report the box widths for diagnosis.")
