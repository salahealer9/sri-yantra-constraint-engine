"""
SPHERICAL CENSUS RUNNER — confirmatory sweep of the 815 well-posed subsets.

Executes the registered procedure (spherical_existence_mapper, Amendment 01) over the
same 815 subsets as the plane census, with:
  - GLOBAL HALT GUARD: any HALT (PLANE_INCONSISTENCY) stops the census immediately and
    flags the plane census for re-examination (Gate 6).
  - RESUMABLE CHECKPOINTING: rows are flushed incrementally; on restart, already-classified
    subsets are skipped (re-reading the output CSV).
  - sec.11 REPORTING SCHEMA: full per-subset record.
  - REPRODUCIBILITY INVARIANT: a canonical hash over (subset -> five-way class) only — the
    cross-machine-stable quantity. Interval endpoints and the tier sub-label of EXCLUDED
    cases (tangency / near_degenerate) are float-sensitive at thresholds and are reported
    but NOT part of the canonical hash; the robust-set hash is reported separately.

Usage:
  python spherical_census.py                       # full 815, resuming if out exists
  python spherical_census.py --limit 20            # smoke test
  python spherical_census.py --out census.csv --fresh
"""
import os, sys, csv, json, math, hashlib, argparse
_here = os.path.dirname(os.path.abspath(__file__))
_root = _here
while _root != os.path.dirname(_root):
    if os.path.exists(os.path.join(_root, "sriyantra_plane.py")):
        break
    _root = os.path.dirname(_root)
import spherical_existence_mapper as M

HERE = os.path.dirname(os.path.abspath(__file__))
SCHEMA = ["subset","class","tier","valid_lo","valid_hi","alg_lo","alg_hi","fold",
          "near_degenerate","near_zero_width","boundary","pole_inbox","branch_ends","notes"]

def universe():
    """The 815 well-posed subsets — read from the plane census results.csv so the spherical
    census runs on the identical subset universe (direct comparability)."""
    path=None
    for cand in (os.path.join(HERE,"results.csv"), "results.csv",
                 os.path.join(HERE,"..","results.csv"),
                 os.path.join(HERE,"campaign_results","results.csv")):
        if os.path.exists(cand): path=cand; break
    if path is None:
        sys.exit("results.csv not found (place it beside the script or in the run dir)")
    subs=[]
    with open(path) as f:
        for r in csv.DictReader(f):
            subs.append(tuple(eval(r["subset"])))
    return subs

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out", default="spherical_census.csv")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--fresh", action="store_true", help="ignore any existing output and start over")
    args=ap.parse_args()

    surv,_=M.load(); surv_items=list(surv.items()); survset=set(surv)
    def warm(sub):
        for thr in (4,3,2):
            w=[r for s,r in surv_items if len(set(sub)&set(s))>=thr][:6]
            if w: return w
        return []
    def feasible(sub): return tuple(sub) in survset

    subs=universe()
    if args.limit: subs=subs[:args.limit]

    done={}
    if os.path.exists(args.out) and not args.fresh:
        for r in csv.DictReader(open(args.out)):
            done[tuple(eval(r["subset"]))]=r["class"]
        print(f"resuming: {len(done)} of {len(subs)} already classified")

    new = not done
    f=open(args.out, "a" if done else "w", newline="")
    w=csv.writer(f)
    if new: w.writerow(SCHEMA)

    n=len(subs); i0=len(done)
    for i,sub in enumerate(subs):
        if sub in done: continue
        r=M.map_subset(sub, warm(sub), feasible(sub))
        # ---- GLOBAL HALT GUARD (Gate 6) ----
        if r.get("halt"):
            w.writerow([list(sub),"HALT_PLANE_INCONSISTENCY",r.get("tier"),"","","","","",
                        "","","", r.get("pole_inbox"), ";".join(r["ends"]),
                        "Gate 6: in-box pole limit for a plane-infeasible subset"])
            f.flush()
            print("\n"+"!"*72)
            print(f"  GATE 6 HALT — PLANE_INCONSISTENCY at {sub}")
            print("  A plane-certified-infeasible subset has a Gate-4-valid branch whose")
            print("  pole limit lies inside the registered plane domain. Census STOPPED.")
            print("  The plane census must be re-examined before proceeding.")
            print("!"*72)
            f.close(); sys.exit(2)
        vl=f"{r['valid'][0]:.2f}" if r['valid'] else ""; vh=f"{r['valid'][1]:.2f}" if r['valid'] else ""
        al=f"{r['alg'][0]:.2f}" if r['alg'] else ""; ah=f"{r['alg'][1]:.2f}" if r['alg'] else ""
        w.writerow([list(sub), r['cls'], r.get('tier'), vl, vh, al, ah, r['fold'],
                    r.get('near_degenerate'), r.get('near_zero_width'), r['vbound'] or "",
                    r.get('pole_inbox'), ";".join(r['ends']), ""])
        if (i+1) % 10 == 0:
            f.flush()
            print(f"  {i+1}/{n} classified ...")
    f.close()

    # ---- summary + reproducibility invariants ----
    rows=list(csv.DictReader(open(args.out)))
    rows=[r for r in rows if r["class"]!="HALT_PLANE_INCONSISTENCY"]
    from collections import Counter
    counts=Counter(r["class"] for r in rows)
    robust_spherical=[r for r in rows if r["class"]=="SPHERICAL_ONLY" and r["tier"]=="robust"]
    flagged=[(r["subset"],r["tier"]) for r in rows if r["tier"] in ("tangency","near_degenerate")]
    # canonical class hash (cross-machine-stable): subset -> class only
    canon=sorted((r["subset"], r["class"]) for r in rows)
    class_hash=hashlib.sha256(json.dumps(canon).encode()).hexdigest()[:16]
    robust_hash=hashlib.sha256(json.dumps(sorted(r["subset"] for r in robust_spherical)).encode()).hexdigest()[:16]

    print("\n"+"="*60); print(f"SPHERICAL CENSUS — {len(rows)} subsets classified"); print("="*60)
    for k in ("PLANE_CONTINUATION","SPHERICAL_ONLY","POLE_OUT_OF_DOMAIN","ALGEBRAIC_ONLY","ALGEBRAIC_EMPTY"):
        print(f"  {k:22s} {counts.get(k,0)}")
    print(f"  --- SPHERICAL_ONLY robust (excl. tangency/near_degenerate): {len(robust_spherical)}")
    print(f"  flagged (excluded from robust counts): {len(flagged)}")
    print(f"\n  CANONICAL class hash (cross-machine invariant): {class_hash}")
    print(f"  robust SPHERICAL_ONLY set hash:                 {robust_hash}")
    print(f"  results: {args.out}")
    if counts.get("ALGEBRAIC_EMPTY",0)==0:
        print("\n  ALGEBRAIC_EMPTY = 0  -> consistent with H3 (algebraic emptiness may not occur).")

if __name__=="__main__":
    main()
