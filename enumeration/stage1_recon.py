"""
STAGE 1 — geometry reconnaissance (NOT census, NOT certification, NOT inference).

Tracks Rao plane-census subsets as h-parameterized spherical families.
A plane subset is {1,2}+3 others (5 constraints, 5 unknowns b,c,d,e,g); fixing the
altitude h makes the spherical slice a square 5x5 system. h -> pi/2 is the plane
limit (frozen plane engine), so we start branches from certified plane roots and
continue them downward in h.

Records per altitude: convergence, max|F|, Jacobian condition number, and (for a
few subsets) the multistart distinct-root count. Outputs a CSV and four plots.

Engine: sriyantra.py (validated spherical engine).  Solver: damped Newton with
numerical Jacobian; domain errors (acos>1 etc.) are treated as infeasible steps.
"""
import os, sys, json, math
_here = os.path.dirname(os.path.abspath(__file__))
_root = _here
while _root != os.path.dirname(_root):
    if os.path.exists(os.path.join(_root, "sriyantra_plane.py")):
        break
    _root = os.path.dirname(_root)
for _p in (_here, _root, os.path.join(_root, "enumeration")):
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import sriyantra as RAO

DEG = math.pi/180.0

# ---------- solver ----------
def F_vec(subset, x, h):
    b,c,d,e,g = x
    try:
        F = RAO.constraints(b,c,d,e,g,h)
    except Exception:
        return None
    v = np.array([F[i] for i in subset], float)
    return v if np.all(np.isfinite(v)) else None

def jac(subset, x, h, eps=1e-7):
    f0 = F_vec(subset, x, h)
    if f0 is None: return None, None
    J = np.zeros((len(subset), 5))
    for k in range(5):
        xp = x.copy(); xp[k] += eps
        fp = F_vec(subset, xp, h)
        if fp is None: return None, None
        J[:,k] = (fp - f0)/eps
    return J, f0

def newton(subset, x0, h, tol=1e-12, maxit=80):
    x = np.array(x0, float)
    for it in range(maxit):
        J, f = jac(subset, x, h)
        if J is None: return x, np.inf, it, False, np.inf
        r = np.max(np.abs(f))
        cond = np.linalg.cond(J)
        if r < tol: return x, r, it, True, cond
        try: dx = np.linalg.solve(J, -f)
        except np.linalg.LinAlgError: return x, r, it, False, cond
        lam, ok = 1.0, False
        for _ in range(40):
            xn = x + lam*dx
            fn = F_vec(subset, xn, h)
            if fn is not None and np.max(np.abs(fn)) < r:
                x, ok = xn, True; break
            lam *= 0.5
        if not ok: return x, r, it, False, cond
    return x, r, maxit, False, cond

# ---------- continuation from a certified plane root ----------
def continue_branch(subset, plane_root, h_hi=89.0, h_lo=20.0, dh=1.0):
    rows = []
    h_deg = h_hi
    r0 = math.pi/2 - h_hi*DEG
    x = np.array(plane_root, float) * r0          # arc = plane-length * bounding arc
    while h_deg >= h_lo - 1e-9:
        h = h_deg*DEG
        x_sol, res, it, ok, cond = newton(subset, x, h)
        rows.append((h_deg, ok, res, cond, x_sol.copy()))
        if not ok:
            break                                  # branch terminated / fold
        x = x_sol
        h_deg -= dh
    return rows

# ---------- multistart distinct-root count at fixed h ----------
def count_roots(subset, h, n=120, tol=1e-10, seed=0):
    rng = np.random.default_rng(seed)
    R = math.pi/2 - h
    roots = []
    for _ in range(n):
        x0 = rng.uniform(0.02*R, 0.95*R, size=5)
        x, res, it, ok, cond = newton(subset, x0, h, tol=tol, maxit=60)
        if ok and np.all(x > 0) and np.all(x < R):
            if not any(np.allclose(x, q, atol=1e-6) for q in roots):
                roots.append(x)
    return len(roots)

# ---------- driver ----------
def main():
    surv, fail = [], []
    census_path = os.path.join(os.path.dirname(__file__), "campaign_results", "roots.jsonl")
    for line in open(census_path):
        r = json.loads(line)
        if r.get("roots"): surv.append((tuple(r["subset"]), r["roots"][0]["coords"]))
        else: fail.append(tuple(r["subset"]))

    # first batch: 8 survivors (continued) + 3 failures (probed by multistart)
    pick_surv = surv[:8]
    pick_fail = fail[:3]

    csv = open("stage1_recon.csv", "w")
    csv.write("subset,kind,h_deg,ok,max_res,jac_cond,b,c,d,e,g\n")

    print("="*72); print("CONTINUATION of plane survivors  (h: 89 -> 20 deg)"); print("="*72)
    branches = {}
    for sub, root in pick_surv:
        rows = continue_branch(sub, root)
        branches[sub] = rows
        last = rows[-1]
        status = "full to 20" if last[0] <= 20.5 else f"TERMINATED at h={last[0]:.0f}"
        maxcond = max(r[3] for r in rows if np.isfinite(r[3]))
        print(f"  {str(sub):16s}  steps={len(rows):3d}  {status:18s}  "
              f"cond@89={rows[0][3]:.2e}  cond_peak={maxcond:.2e}")
        for (hd, ok, res, cond, x) in rows:
            csv.write(f"\"{sub}\",survivor,{hd:.1f},{int(ok)},{res:.3e},{cond:.3e},"
                      + ",".join(f"{v:.6f}" for v in x) + "\n")

    print("\n" + "="*72); print("MULTISTART root count of plane FAILURES  (do roots appear under curvature?)")
    print("="*72)
    for sub in pick_fail:
        line = f"  {str(sub):16s} "
        for hd in (80, 60, 40, 25):
            n = count_roots(sub, hd*DEG, n=120, seed=1)
            line += f"  h={hd}:{n}roots"
            csv.write(f"\"{sub}\",failure,{hd:.1f},,,,,,,, \n")
        print(line)

    # root count vs h for two survivors (bifurcation probe)
    print("\n" + "="*72); print("MULTISTART root count vs h for two survivors (branch structure)")
    print("="*72)
    rootcount = {}
    for sub, _ in pick_surv[:2]:
        rc = []
        for hd in range(85, 19, -5):
            rc.append((hd, count_roots(sub, hd*DEG, n=150, seed=2)))
        rootcount[sub] = rc
        print(f"  {str(sub):16s} " + " ".join(f"{hd}:{n}" for hd,n in rc))
    csv.close()

    # ---------- plots ----------
    # 1. conditioning vs h (the pole-conditioning prediction)
    plt.figure(figsize=(7,4.5))
    for sub, rows in branches.items():
        hs = [r[0] for r in rows]; cs = [r[3] for r in rows]
        plt.semilogy(hs, cs, marker='.', label=str(sub))
    plt.gca().invert_xaxis(); plt.xlabel("altitude h (deg)  [90 = plane limit]")
    plt.ylabel("Jacobian condition number"); plt.title("Conditioning vs altitude (survivor branches)")
    plt.legend(fontsize=6, ncol=2); plt.tight_layout(); plt.savefig("stage1_conditioning.png", dpi=130)

    # 2. residual vs h
    plt.figure(figsize=(7,4.5))
    for sub, rows in branches.items():
        hs = [r[0] for r in rows]; rs = [max(r[2],1e-18) for r in rows]
        plt.semilogy(hs, rs, marker='.', label=str(sub))
    plt.gca().invert_xaxis(); plt.xlabel("altitude h (deg)")
    plt.ylabel("max|F| at converged root"); plt.title("Solve residual vs altitude")
    plt.legend(fontsize=6, ncol=2); plt.tight_layout(); plt.savefig("stage1_residual.png", dpi=130)

    # 3. branch trace: d-arc vs h
    plt.figure(figsize=(7,4.5))
    for sub, rows in branches.items():
        hs = [r[0] for r in rows]; ds = [r[4][2] for r in rows]
        plt.plot(hs, ds, marker='.', label=str(sub))
    plt.gca().invert_xaxis(); plt.xlabel("altitude h (deg)")
    plt.ylabel("d (arc, rad)"); plt.title("Branch trace: intercept d vs altitude")
    plt.legend(fontsize=6, ncol=2); plt.tight_layout(); plt.savefig("stage1_branch_trace.png", dpi=130)

    # 4. root count vs h
    plt.figure(figsize=(7,4.5))
    for sub, rc in rootcount.items():
        hs = [x[0] for x in rc]; ns = [x[1] for x in rc]
        plt.plot(hs, ns, marker='o', label=str(sub))
    plt.gca().invert_xaxis(); plt.xlabel("altitude h (deg)")
    plt.ylabel("# distinct multistart roots"); plt.title("Root count vs altitude")
    plt.legend(fontsize=7); plt.tight_layout(); plt.savefig("stage1_rootcount.png", dpi=130)
    print("\nWrote stage1_recon.csv and 4 plots.")

if __name__ == "__main__":
    main()
