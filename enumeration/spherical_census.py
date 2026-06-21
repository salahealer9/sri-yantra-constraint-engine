"""
SPHERICAL CENSUS RUNNER (parallel, resumable) — Amendment 02 build.

Subsets are independent and stable-seeded, so multiprocessing gives results identical
to a sequential run (the canonical hash is computed from sorted output, order-independent).
  - COMPLETENESS AUDIT: each NEGATIVE class (ALGEBRAIC_ONLY / ALGEBRAIC_EMPTY) is re-probed
    aggressively at the highest registered altitude before being finalized (--no-audit to skip).
  - GLOBAL HALT GUARD: any HALT (PLANE_INCONSISTENCY) stops the run (Gate 6).
  - RESUMABLE: rows written as they complete; restart skips done subsets.
  - sec.6 SELF-CHECK: after the run, every plane survivor must be PLANE_CONTINUATION.
  - sec.11 schema + cross-machine reproducibility hash over (subset->class).

Usage:
  python spherical_census.py --jobs 8
  python spherical_census.py --fresh --jobs 8        # after a seed-schedule change
  python spherical_census.py --limit 24 --jobs 4     # smoke test
"""
import os, sys, csv, json, hashlib, argparse, multiprocessing as mp
_here = os.path.dirname(os.path.abspath(__file__))
_root = _here
while _root != os.path.dirname(_root):
    if os.path.exists(os.path.join(_root, "sriyantra_plane.py")):
        break
    _root = os.path.dirname(_root)
for _p in (_here, _root, os.path.join(_root, "enumeration")):
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)
import spherical_existence_mapper as M

HERE = os.path.dirname(os.path.abspath(__file__))
SCHEMA = ["subset","class","tier","valid_lo","valid_hi","alg_lo","alg_hi","fold",
          "near_degenerate","near_zero_width","boundary","pole_inbox","branch_ends","notes"]
_SURV=None
def _ensure():
    global _SURV
    if _SURV is None:
        surv,_=M.load(); _SURV=(list(surv.items()), set(surv))
    return _SURV
def _warm(sub, items):
    for thr in (4,3,2):
        w=[r for s,r in items if len(set(sub)&set(s))>=thr][:6]
        if w: return w
    return []
def classify_one(args):
    sub, audit = args
    items, survset = _ensure()
    return sub, M.map_subset(sub, _warm(sub, items), tuple(sub) in survset, audit=audit)
def universe():
    for cand in (os.path.join(HERE,"results.csv"), "results.csv", 
                 os.path.join(HERE,"..","results.csv"),
                 os.path.join(HERE,"campaign_results","results.csv")):
        if os.path.exists(cand):
            return [tuple(eval(r["subset"])) for r in csv.DictReader(open(cand))]
    sys.exit("results.csv not found (place it beside the script or in the run dir)")
def row_of(sub, r):
    vl=f"{r['valid'][0]:.2f}" if r['valid'] else ""; vh=f"{r['valid'][1]:.2f}" if r['valid'] else ""
    al=f"{r['alg'][0]:.2f}" if r['alg'] else ""; ah=f"{r['alg'][1]:.2f}" if r['alg'] else ""
    return [list(sub), r['cls'], r.get('tier'), vl, vh, al, ah, r['fold'],
            r.get('near_degenerate'), r.get('near_zero_width'), r['vbound'] or "",
            r.get('pole_inbox'), ";".join(r['ends']), r.get('notes',"")]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out", default="spherical_census.csv")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--jobs", type=int, default=os.cpu_count() or 1)
    ap.add_argument("--fresh", action="store_true")
    ap.add_argument("--no-audit", action="store_true")
    args=ap.parse_args(); audit=not args.no_audit
    items, survset = _ensure()
    subs=universe()
    if args.limit: subs=subs[:args.limit]
    done=set()
    if os.path.exists(args.out) and not args.fresh:
        done={tuple(eval(r["subset"])) for r in csv.DictReader(open(args.out))}
        print(f"resuming: {len(done)} of {len(subs)} already classified")
    todo=[s for s in subs if s not in done]
    f=open(args.out, "a" if done else "w", newline=""); w=csv.writer(f)
    if not done: w.writerow(SCHEMA)
    print(f"classifying {len(todo)} subsets on {args.jobs} workers (audit={'on' if audit else 'off'}) ...")
    n=0
    with mp.Pool(args.jobs) as pool:
        for sub, r in pool.imap_unordered(classify_one, [(s,audit) for s in todo], chunksize=1):
            if r.get("halt"):
                w.writerow([list(sub),"HALT_PLANE_INCONSISTENCY","","","","","","","","","",
                            r.get("pole_inbox"),";".join(r["ends"]),"Gate 6 stop condition"]); f.flush()
                print("\n"+"!"*72)
                print(f"  GATE 6 HALT — PLANE_INCONSISTENCY at {sub}.  Census STOPPED.")
                print("  A plane-infeasible subset has a Gate-4-valid in-box pole limit;")
                print("  the plane census must be re-examined before proceeding.")
                print("!"*72)
                pool.terminate(); f.close(); sys.exit(2)
            w.writerow(row_of(sub, r)); n+=1
            if n % 25 == 0: f.flush(); print(f"  {n}/{len(todo)} ...")
    f.close()
    rows=[r for r in csv.DictReader(open(args.out)) if not r["class"].startswith("HALT")]
    from collections import Counter
    counts=Counter(r["class"] for r in rows)
    robust=[r for r in rows if r["class"]=="SPHERICAL_ONLY" and r["tier"]=="robust"]
    flagged=[(r["subset"],r["tier"]) for r in rows if r["tier"] in ("tangency","near_degenerate")]
    canon=sorted((r["subset"], r["class"]) for r in rows)
    class_hash=hashlib.sha256(json.dumps(canon).encode()).hexdigest()[:16]
    robust_hash=hashlib.sha256(json.dumps(sorted(r["subset"] for r in robust)).encode()).hexdigest()[:16]
    print("\n"+"="*60); print(f"SPHERICAL CENSUS — {len(rows)} subsets classified"); print("="*60)
    for k in ("PLANE_CONTINUATION","SPHERICAL_ONLY","POLE_OUT_OF_DOMAIN","ALGEBRAIC_ONLY","ALGEBRAIC_EMPTY"):
        print(f"  {k:22s} {counts.get(k,0)}")
    print(f"  --- SPHERICAL_ONLY robust (excl. tangency/near_degenerate): {len(robust)}")
    print(f"  flagged (excluded from robust counts): {len(flagged)}")
    print(f"  reclassified by completeness audit: {sum('audit' in r['notes'] for r in rows)}")
    snp=sorted(r["subset"] for r in rows if tuple(eval(r["subset"])) in survset and r["class"]!="PLANE_CONTINUATION")
    if snp:
        print("\n  *** sec.6 CONSISTENCY DIAGNOSE: survivors NOT reaching an in-box pole ***")
        for x in snp: print("       ",x)
    else:
        print(f"\n  sec.6 alpha->0 consistency: all {len(survset)} plane survivors -> PLANE_CONTINUATION  OK")
    print(f"\n  CANONICAL class hash (cross-machine invariant): {class_hash}")
    print(f"  robust SPHERICAL_ONLY set hash:                 {robust_hash}")
    if counts.get("ALGEBRAIC_EMPTY",0)==0: print("\n  ALGEBRAIC_EMPTY = 0  -> consistent with H3.")
    print(f"  results: {args.out}")

if __name__=="__main__":
    main()
