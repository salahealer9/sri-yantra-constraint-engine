"""
STAGE 2 -> exploratory probe (NOT the census).

Question (legitimized by the Gate-4 validity layer):
  Among the 681 plane-CERTIFIED-infeasible subsets, does any admit a
  GATE-4-VALID spherical figure at any altitude?

This is the validity-filtered successor to the retracted Stage-1 root-count probe.
A subset is counted as gaining a figure ONLY if the constructor (spherical_geo_check)
returns a Gate-4-valid figure (ordering + distinctness + closure), never on F=0 alone.

For each infeasible subset we search a grid of altitudes with the degree-normalized
solver (warm starts from constraint-sharing survivors + ordering-filtered random
seeds), validate every converged root through Gate 4, and for any valid figure map
its Gate-4-valid altitude interval and test pole behaviour.

Classification:
  NO_VALID        no Gate-4-valid figure at any tested altitude        (rigidity)
  SPHERICAL_ONLY  Gate-4-valid in a bounded window that does NOT reach the pole
                  (candidate genuinely-spherical figure, no valid plane analogue)
  POLE_FLAG       Gate-4-valid branch reaching h>=89  -> must be scrutinized:
                    - plane-scaled limit OUT of plane box B  => out-of-domain (no contradiction)
                    - plane-scaled limit IN box B            => potential plane false-negative

Runtime note: the full 681-subset run is minutes-to-tens-of-minutes; use --limit for a
pilot first. Intended for a server run.

Usage:
  python spherical_infeasible_probe.py --limit 30          # pilot
  python spherical_infeasible_probe.py                     # full 681
"""
import os, sys, math, json, csv, argparse
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
import spherical_geo_check as GC
import stage1b_landscape as L
import sriyantra_plane as SP

PI2 = math.pi/2; DEG = math.pi/180
HERE = os.path.dirname(os.path.abspath(__file__))

def load_subsets():
    surv, fail = {}, []
    census = os.path.join(HERE, "campaign_results", "roots.jsonl")
    for line in open(census):
        j = json.loads(line)
        if j.get("roots"): surv[tuple(j["subset"])] = j["roots"][0]["coords"]
        else: fail.append(tuple(j["subset"]))
    return surv, fail

# box B (plane, Rao Table 3, widened 50%) — for the pole-domain check
def box_B():
    T = np.array([v for _, v in SP.TABLE3]); lo, hi = T.min(0), T.max(0); rng = hi - lo
    return lo - 0.5*rng, hi + 0.5*rng
BLO, BHI = box_B()
def in_box(p): return bool(np.all(p >= BLO) and np.all(p <= BHI))

def seeds(sub, h, k, warm):
    R = PI2 - h*DEG; out = [np.array(w)*R for w in warm]
    rng = np.random.default_rng((hash(sub) ^ int(h*1000)) & 0x7fffffff)
    tries = 0
    while len(out) < k + len(warm) and tries < 12*k:
        x = rng.uniform(0.02*R, 0.92*R, 5); tries += 1
        b,c,d,e,g = x
        if g < c and b+c < R and d+e < R: out.append(x)
    return out

def find_valid(sub, h, warm, k):
    for x0 in seeds(sub, h, k, warm):
        x,res,ok,c = L.newton(sub, x0, h*DEG, maxit=50)
        if ok:
            v, _ = GC.gate4(*x, h*DEG, closure_tol=1e-7)
            if v: return x
    return None

def valid_interval(sub, x0, h0, step=0.5):
    hi = h0; x = x0.copy()
    for hd in np.arange(h0, 89.6, step):
        xs,res,ok,c = L.newton(sub, x, hd*DEG, maxit=50)
        if ok and GC.gate4(*xs, hd*DEG, closure_tol=1e-7)[0]: x, hi = xs, hd
        else: break
    x_hi = x.copy(); h_hi = hi
    lo = h0; x = x0.copy()
    for hd in np.arange(h0, 11.0, -step):
        xs,res,ok,c = L.newton(sub, x, hd*DEG, maxit=50)
        if ok and GC.gate4(*xs, hd*DEG, closure_tol=1e-7)[0]: x, lo = xs, hd
        else: break
    return lo, h_hi, x_hi

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="probe only the first N subsets (0 = all 681)")
    ap.add_argument("--seeds", type=int, default=24)
    ap.add_argument("--out", default="spherical_infeasible_probe.csv")
    ap.add_argument("--altitudes", default="80,68,56,44,33,24,17")
    args = ap.parse_args()
    alts = [float(a) for a in args.altitudes.split(",")]

    surv, fail = load_subsets()
    surv_items = list(surv.items())
    targets = fail if args.limit == 0 else fail[:args.limit]

    out = open(args.out, "w", newline="")
    w = csv.writer(out)
    w.writerow(["subset","class","valid_alts","interval_lo","interval_hi","reaches_pole","pole_inBoxB","note"])
    counts = {"NO_VALID":0, "SPHERICAL_ONLY":0, "POLE_FLAG":0}
    n_pole_inbox = 0

    for i, sub in enumerate(targets):
        warm = [r for s, r in surv_items if len(set(sub) & set(s)) >= 4][:6]
        valid_alts, seed = [], None
        for h in alts:
            x = find_valid(sub, h, warm, args.seeds)
            if x is not None:
                valid_alts.append(h)
                if seed is None: seed = (x, h)
        if seed is None:
            counts["NO_VALID"] += 1
            w.writerow([list(sub), "NO_VALID", "", "", "", "", "", "no Gate-4-valid figure on grid"])
        else:
            lo, hi, x_hi = valid_interval(sub, seed[0], seed[1])
            reaches = hi >= 89.0
            pole_inbox = ""
            note = ""
            if reaches:
                a = PI2 - hi*DEG; p = np.array(x_hi)/a
                pole_inbox = in_box(p); n_pole_inbox += int(pole_inbox)
                note = "POTENTIAL plane false-negative (scrutinize)" if pole_inbox else "out-of-domain at pole (no contradiction)"
                counts["POLE_FLAG"] += 1; cls = "POLE_FLAG"
            else:
                counts["SPHERICAL_ONLY"] += 1; cls = "SPHERICAL_ONLY"
                note = "Gate-4-valid only in bounded altitude window"
            w.writerow([list(sub), cls, ";".join(f"{a:.0f}" for a in valid_alts),
                        f"{lo:.1f}", f"{hi:.1f}", reaches, pole_inbox, note])
        if (i+1) % 25 == 0:
            out.flush()
            print(f"  {i+1}/{len(targets)}  NO_VALID={counts['NO_VALID']} "
                  f"SPHERICAL_ONLY={counts['SPHERICAL_ONLY']} POLE_FLAG={counts['POLE_FLAG']}")
    out.close()

    print("\n==== SUMMARY ({} infeasible subsets probed) ====".format(len(targets)))
    for k in ("NO_VALID","SPHERICAL_ONLY","POLE_FLAG"): print(f"  {k:16s} {counts[k]}")
    print(f"  of POLE_FLAG, plane-scaled limit IN box B (need scrutiny): {n_pole_inbox}")
    print("\nInterpretation:")
    print("  NO_VALID dominant            -> rigidity: plane infeasibility survives curvature.")
    print("  SPHERICAL_ONLY > 0           -> candidate genuinely-spherical valid figures.")
    print("  POLE_FLAG with IN-box limits -> re-examine the plane census for those subsets.")
    print(f"  results written to {args.out}")

if __name__ == "__main__":
    main()
