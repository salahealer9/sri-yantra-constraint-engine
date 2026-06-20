"""
STAGE 1B — solution-landscape sweep (exploratory; not census/certification/inference).

Uses the NORMALIZED spherical constraints  F~_i = F_i / alpha^{d_i}  (alpha = pi/2 - h,
d_i = 2 for {3,4,6}, else 1) — verified to remove the 1/alpha pole conditioning.

(A) Continue all 134 plane survivors from h=89 -> 20 deg: persistence, peak cond, folds.
(B) Probe near-feasible plane failures (share 4/5 constraints with a survivor):
    root count vs altitude, altitude interval of existence, branch birth.

Engine: sriyantra.py.  Solver: damped Newton on F~, numerical Jacobian.

CAVEAT (see Stage-1 memorandum, Finding 3): part (B)'s "gainer" counts are
SUPERSEDED. They counted F=0 solutions with only a positivity check; once Gate-4
geometric validity is applied the apparent effect dissolves (all 681 plane
failures are certified-infeasible). Part (B) is retained for provenance only —
do NOT read its gainer numbers as results. Part (A) (survivor continuation,
normalized solver) and the conditioning result stand.
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
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
import sriyantra as RAO

PI2 = math.pi/2; DEG = math.pi/180
DI = {i:(2 if i in (3,4,6) else 1) for i in range(1,21)}

def Ftil(subset, x, h):
    a = PI2 - h; b,c,d,e,g = x
    try: F = RAO.constraints(b,c,d,e,g,h)
    except Exception: return None
    v = np.array([F[i]/a**DI[i] for i in subset], float)
    return v if np.all(np.isfinite(v)) else None

def newton(subset, x0, h, tol=1e-11, maxit=60):
    x = np.array(x0, float)
    for it in range(maxit):
        f = Ftil(subset, x, h)
        if f is None: return x, np.inf, False, np.inf
        r = np.max(np.abs(f))
        J = np.zeros((len(subset),5)); ok_j=True
        for k in range(5):
            xp = x.copy(); xp[k]+=1e-7; fp = Ftil(subset, xp, h)
            if fp is None: ok_j=False; break
            J[:,k]=(fp-f)/1e-7
        if not ok_j: return x, r, False, np.inf
        cond = np.linalg.cond(J)
        if r < tol: return x, r, True, cond
        try: dx = np.linalg.solve(J, -f)
        except np.linalg.LinAlgError: return x, r, False, cond
        lam, adv = 1.0, False
        for _ in range(40):
            xn = x+lam*dx; fn = Ftil(subset, xn, h)
            if fn is not None and np.max(np.abs(fn))<r: x, adv = xn, True; break
            lam*=0.5
        if not adv: return x, r, False, cond
    return x, r, False, cond

def count_roots(subset, h, n=30, seed=7):
    rng = np.random.default_rng(seed); R = PI2-h; roots=[]
    for _ in range(n):
        x0 = rng.uniform(0.02*R, 0.92*R, 5)
        x,res,ok,cond = newton(subset, x0, h, maxit=40)
        if ok and np.all(x>1e-6) and np.all(x<R):
            if not any(np.allclose(x,q,atol=1e-5) for q in roots): roots.append(x)
    return roots

def existence_interval(subset, x_seed, h_seed, hi=89.5, lo=12.0, step=0.5):
    up=h_seed; x=x_seed.copy()
    for hd in np.arange(h_seed, hi+1e-9, step):
        xs,res,ok,c = newton(subset, x, hd*DEG, maxit=40)
        if ok and np.all(xs>1e-6): x, up = xs, hd
        else: break
    dn=h_seed; x=x_seed.copy()
    for hd in np.arange(h_seed, lo-1e-9, -step):
        xs,res,ok,c = newton(subset, x, hd*DEG, maxit=40)
        if ok and np.all(xs>1e-6): x, dn = xs, hd
        else: break
    return dn, up

def main():
    surv=[]; fail=[]
    census_path = os.path.join(os.path.dirname(__file__), "campaign_results", "roots.jsonl")
    for line in open(census_path):
        r=json.loads(line)
        if r.get("roots"): surv.append((tuple(r["subset"]), r["roots"][0]["coords"]))
        else: fail.append(tuple(r["subset"]))
    surv_sets=[set(s) for s,_ in surv]

    # ---- (A) all 134 survivors ----
    print("="*70); print(f"(A) CONTINUE ALL {len(surv)} SURVIVORS (normalized, h:89->20)"); print("="*70)
    full=0; terminated=[]; peakconds=[]
    fcsv=open("stage1b_survivors.csv","w"); fcsv.write("subset,full_to_20,term_h,peak_cond\n")
    for sub, root in surv:
        x=np.array(root)*(PI2-89*DEG); termh=None; pk=0.0
        for hd in np.arange(89,19.9,-1.0):
            xs,res,ok,c=newton(sub,x,hd*DEG,maxit=50)
            if ok: x=xs; pk=max(pk,c if np.isfinite(c) else pk)
            else: termh=hd; break
        ok_full = termh is None
        full += ok_full; peakconds.append(pk)
        if not ok_full: terminated.append((sub,termh))
        fcsv.write(f"\"{sub}\",{int(ok_full)},{'' if termh is None else termh},{pk:.3e}\n")
    fcsv.close()
    print(f"  continued full to h=20: {full}/{len(surv)}")
    print(f"  terminated early (candidate folds): {len(terminated)} -> {terminated[:10]}")
    print(f"  peak normalized cond: median={np.median(peakconds):.1f}  max={np.max(peakconds):.1f}")

    # ---- (B) near-feasible failures ----
    near=[]
    for f in fail:
        adj=sum(1 for s in surv_sets if len(set(f)&s)==4)
        if adj>0: near.append((adj,f))
    near.sort(reverse=True)
    sample=[f for _,f in near[:120]]
    print("\n"+"="*70); print(f"(B) NEAR-FEASIBLE FAILURES: {len(near)} found; probing {len(sample)}")
    print("="*70)
    alts=[78,60,45,30,20]
    gainers=[]; gcsv=open("stage1b_failures.csv","w")
    gcsv.write("subset,"+",".join(f"n_h{a}" for a in alts)+",first_h,interval_lo,interval_hi\n")
    for j,sub in enumerate(sample):
        counts=[]; first=None; seedx=None; seedh=None
        for a in alts:
            rs=count_roots(sub, a*DEG, n=28, seed=11)
            counts.append(len(rs))
            if rs and first is None: first=a; seedx=rs[0]; seedh=a
        if first is not None:
            lo,hi=existence_interval(sub, seedx, seedh)
            gainers.append((sub,counts,first,lo,hi))
            gcsv.write(f"\"{sub}\","+",".join(map(str,counts))+f",{first},{lo:.1f},{hi:.1f}\n")
        else:
            gcsv.write(f"\"{sub}\","+",".join(map(str,counts))+",,,\n")
        if (j+1)%30==0: print(f"   probed {j+1}/{len(sample)} ... gainers so far: {len(gainers)}")
    gcsv.close()
    print(f"\n  plane failures that GAIN spherical roots: {len(gainers)}/{len(sample)}")
    if gainers:
        firsts=[g[2] for g in gainers]
        from collections import Counter
        print("  first-appearance altitude (deg) histogram:", dict(sorted(Counter(firsts).items(),reverse=True)))
        his=[g[4] for g in gainers]; los=[g[3] for g in gainers]
        reach_pole=sum(1 for h in his if h>=89.0)
        print(f"  of gainers, branches reaching pole (h>=89, i.e. ~plane): {reach_pole}")
        print(f"  existence-interval upper end: median={np.median(his):.0f} deg (so most are curvature-only)")
        print("  examples:")
        for sub,counts,first,lo,hi in gainers[:8]:
            print(f"    {str(sub):16s} counts@{alts}={counts}  first@{first}  interval[{lo:.0f},{hi:.0f}]")

    # ---- figures ----
    if gainers:
        plt.figure(figsize=(7,4.5))
        for sub,counts,first,lo,hi in gainers:
            plt.plot([hi,lo],[1,1],alpha=0.25,color='C0')
            plt.plot([hi,lo],[1,1],'.',color='C0')
        plt.gca().invert_xaxis(); plt.xlabel("altitude h (deg)"); plt.yticks([])
        plt.title(f"Altitude intervals of existence ({len(gainers)} curvature-born failure branches)")
        plt.axvline(90,ls=':',color='k'); plt.tight_layout(); plt.savefig("stage1b_intervals.png",dpi=130)
        plt.figure(figsize=(7,4.5))
        from collections import Counter
        c=Counter(g[2] for g in gainers); ks=sorted(c); 
        plt.bar([str(k) for k in ks],[c[k] for k in ks])
        plt.xlabel("first-appearance altitude (deg)"); plt.ylabel("# failure subsets")
        plt.title("Where curvature first creates roots"); plt.tight_layout()
        plt.savefig("stage1b_firstappear.png",dpi=130)
    print("\nWrote stage1b_survivors.csv, stage1b_failures.csv, figures.")

if __name__=="__main__":
    main()
