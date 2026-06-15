"""
tier1_crosscheck.py — Tier-1 multistart Newton cross-check of the Tier-2 census (§6).

PROTOCOL COMPLETION, not additional evidence: Tier-2's certified results stand on
their own (a certified absence is a proof). This confirms the two-tier design
agrees with itself — that multistart Newton recovers the Tier-2 feasible solutions
and finds nothing in B_plane that Tier-2 certified absent.

Registered Tier-1 (§6): 200 Latin-hypercube starts + Rao plane seeds, RNG 20260610,
Newton to |F_i| <= 1e-6. Scoped to B_plane per Amendment 03 C3 (the cross-check
region), so starts are drawn over B_plane (dense coverage of the confirmatory
region) rather than the larger exploratory pooled box.

Reads the frozen Tier-2 outputs (campaign_results/{results.csv,roots.jsonl}) and
writes crosscheck_results/{crosscheck.csv, report.md}.
"""
import os, sys, csv, json, ast, time
HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import numpy as np
import sriyantra_plane as SP
from scipy.optimize import fsolve
from scipy.stats import qmc

with open(os.path.join(HERE,"B.json")) as f: _B=json.load(f)["box"]
BOX=[tuple(_B[k]) for k in ("b","c","d","e","g")]
LO=np.array([b[0] for b in BOX]); HI=np.array([b[1] for b in BOX])
RAO_PLANE=[v for _,v in SP.TABLE3]            # 6 plane seeds (in B_plane)
RNG_SEED=20260610; N_LHS=200; CONV=1e-6; MATCH_TOL=1e-3; DEDUP=1e-5
RES=os.path.join(HERE,"campaign_results"); OUT=os.path.join(HERE,"crosscheck_results")
os.makedirs(OUT,exist_ok=True)

def in_box(x): return bool(np.all(x>=LO-1e-9) and np.all(x<=HI+1e-9))

def tier1(S, idx):
    """Return de-duplicated in-B_plane Newton solutions for subset S."""
    def resid(x):
        try: F=SP.constraints(*x); return [F[k] for k in S]
        except Exception: return [1e3]*5
    starts=qmc.scale(qmc.LatinHypercube(d=5, seed=RNG_SEED+idx).random(N_LHS), LO, HI)
    starts=np.vstack([starts, np.array(RAO_PLANE)])     # + deterministic Rao plane seeds
    sols=[]
    for x0 in starts:
        try: x,_,ier,_=fsolve(resid, x0, full_output=True)
        except Exception: continue
        if ier!=1 or not in_box(x): continue
        if max(abs(v) for v in resid(x))>CONV: continue
        if not any(np.max(np.abs(x-s))<DEDUP for s in sols): sols.append(np.array(x))
    return sols

def load_tier2():
    feas={}; roots={}
    for r in csv.DictReader(open(os.path.join(RES,"results.csv"))):
        S=tuple(ast.literal_eval(r["subset"])); feas[S]=(r["feasible"]=="1", r["complete"]=="True")
    for line in open(os.path.join(RES,"roots.jsonl")):
        d=json.loads(line); S=tuple(d["subset"])
        roots[S]=[rt["coords"] for rt in d.get("roots",[])]
    return feas, roots

def main(start=0, end=815):
    t0=time.time(); feas,roots=load_tier2()
    pop=sorted(feas.keys())
    cats={"agree_feasible":0,"agree_infeasible":0,"t1_missed":0,"t1_extra":0}
    disc=[]; rows=[]
    def close(s,r): return max(abs(s[i]-r[i]) for i in range(5))<MATCH_TOL
    for idx in range(start, min(end,len(pop))):
        S=pop[idx]; t2_feas,_=feas[S]; t2_roots=roots.get(S,[])
        sols=tier1(S, idx); t1_feas=len(sols)>0
        matched=[s for s in sols if any(close(s,r) for r in t2_roots)]
        extra  =[s for s in sols if not any(close(s,r) for r in t2_roots)]  # T1 found, not in T2
        missed =[r for r in t2_roots if not any(close(s,r) for s in sols)]  # T2 root T1 missed
        if extra:       cat="t1_extra"        # CRITICAL: contradicts Tier-2 completeness
        elif missed:    cat="t1_missed"       # coverage gap only (Tier-2 certified)
        elif t2_feas:   cat="agree_feasible"
        else:           cat="agree_infeasible"
        cats[cat]+=1
        if cat in ("t1_extra","t1_missed"):
            disc.append((S,cat,len(sols),len(t2_roots),len(extra),len(missed)))
        rows.append([idx,str(S),t2_feas,t1_feas,len(sols),len(matched),len(extra),len(missed),cat])
    with open(os.path.join(OUT,"crosscheck.csv"),"w",newline="") as f:
        w=csv.writer(f); w.writerow(["idx","subset","t2_feasible","t1_feasible","t1_sols","matched","extra","missed","category"])
        w.writerows(rows)
    crit=cats["t1_extra"]
    print(f"Tier-1 cross-check — {len(rows)} subsets, {round(time.time()-t0)}s")
    print(f"  agree feasible      : {cats['agree_feasible']}")
    print(f"  agree infeasible    : {cats['agree_infeasible']}")
    print(f"  Tier-1 missed (cov) : {cats['t1_missed']}   (multistart coverage gap; Tier-2 result is certified)")
    print(f"  Tier-1 EXTRA        : {cats['t1_extra']}   <-- CRITICAL if >0: a real in-B_plane solution Tier-2 did not certify")
    if disc:
        print("  flagged:")
        for S,cat,n1,n2,ne,nm in disc[:60]:
            print(f"    {S} {cat} t1_sols={n1} t2_roots={n2} extra={ne} missed={nm}")
    ok = (crit==0)
    print(f"\n  CROSS-CHECK: {'PASS — two-tier design closed (full agreement)' if ok and cats['t1_missed']==0 else ('PASS — no Tier-1 solution contradicts Tier-2; '+str(cats['t1_missed'])+' coverage gap(s) noted' if ok else 'HALT-AND-DIAGNOSE: Tier-1 found solution(s) absent from certified Tier-2')}")

if __name__=="__main__":
    a=sys.argv[1:]
    if len(a)==2: main(int(a[0]),int(a[1]))
    else: main()
