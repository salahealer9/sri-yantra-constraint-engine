#!/usr/bin/env python3
"""
run_pilot.py — official frozen pilot execution for the size-six spherical subset
{1,2,3,4,6,7}. Runs domain_sphere.enum() at FROZEN budget (no overrides) and
writes a forensic record. Classification is applied mechanically from the output
per pilot-preregistration v1.2; this script does NOT decide the verdict by hand.

Frozen budget (from domain_sphere.enum defaults): wall_clock 7200s, max_depth 200,
r_cert 3e-3, max_boxes 3_000_000, single-threaded.

Run:  python3 enumeration/run_pilot.py
"""
import sys, os, json, time, platform, hashlib, traceback
_here = os.path.dirname(os.path.abspath(__file__))
_root = _here
while _root != os.path.dirname(_root):
    if os.path.exists(os.path.join(_root, "sriyantra.py")):
        break
    _root = os.path.dirname(_root)
for _p in (_here, _root, os.path.join(_root, "enumeration")):
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)
import domain_sphere as D

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                   "spherical_census", "pilot_forensic.json")

def sha(path):
    try:
        return hashlib.sha256(open(path, "rb").read()).hexdigest()
    except Exception:
        return None

def main():
    meta = {
        "subset": D.S6,
        "B_sphere": D.B_SPHERE,
        "frozen_budget": {"wall_clock_s": 7200, "max_depth": 200, "r_cert": 3e-3,
                          "max_boxes": 3_000_000, "threads": 1},
        "instrument_sha256": {
            "domain_sphere.py": sha(os.path.join(os.path.dirname(__file__), "domain_sphere.py")),
        },
        "python": platform.python_version(),
        "host": platform.node(),
        "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    error_kind = "none"; r = None
    t0 = time.time()
    try:
        # call enum at FROZEN defaults — log_every for progress visibility only
        r = D.enum(log_every=100000)
    except KeyboardInterrupt:
        error_kind = "interrupt"
    except MemoryError:
        error_kind = "oom"
    except Exception:
        error_kind = "exception"
        meta["traceback"] = traceback.format_exc()
    elapsed = round(time.time() - t0, 1)

    # ---- mechanical three-way classification (prereg v1.2) ----
    # CLOSES        : queue exhausted (complete=True), no technical failure
    # BUDGET-EXHAUSTED: hit a frozen resource limit (max_boxes OR wall_clock) with
    #                   unresolved>0 or queue_left>0, no technical failure
    # TECHNICAL     : crash / oom / interrupt / unreadable result
    if error_kind != "none" or r is None:
        verdict = "TECHNICAL INCONCLUSIVE"
        bound_by = error_kind
    elif r["complete"]:
        verdict = "CLOSES"
        bound_by = "queue_exhausted"
    else:
        verdict = "BUDGET-EXHAUSTED"
        # which frozen limit bound the run
        if r["boxes"] >= 3_000_000:
            bound_by = "max_boxes"
        elif elapsed >= 7200:
            bound_by = "wall_clock"
        else:
            bound_by = "stack_empty_but_marked_incomplete?"  # should not happen

    rec = dict(meta)
    rec.update({
        "elapsed_s": elapsed,
        "error_kind": error_kind,
        "result": r,
        "verdict": verdict,
        "bound_by": bound_by,
        "finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    })
    # certified roots are full lists; keep them but also count
    if r is not None:
        rec["n_certified"] = len(r.get("cert", []))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(rec, f, indent=2, default=list)

    print("\n================= PILOT RESULT =================")
    print(f"  verdict   : {verdict}")
    print(f"  bound_by  : {bound_by}")
    print(f"  error_kind: {error_kind}")
    if r is not None:
        for k in ("boxes","dom","excl","unres","maxd","maxq","queue_left","secs","complete"):
            print(f"  {k:11s}: {r[k]}")
        print(f"  certified : {len(r.get('cert',[]))}")
    print(f"  forensic  : {os.path.abspath(OUT)}")
    print("===============================================")

if __name__ == "__main__":
    main()
