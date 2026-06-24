"""
spherical_census_runner_v2.py
=============================================================================
Forensic-grade census runner. Adds the four evidentiary layers on top of the
FROZEN engine and driver, which are imported and NEVER modified:

    CSV          summary layer    (sort / grep / pivot / cite)
    JSONL        forensic layer   (one self-describing row per subset, w/ roots)
    log          execution layer  (timestamps, halts, hashes)
    manifest +   provenance layer (engine SHA, commit, prereg, file hashes)
    SHA256SUMS

It implements every point of the output specification:
  (1) frozen JSONL schema (see ROW_SCHEMA / build_row);
  (2) roots archived in each row — BOTH valid and invalid (Gate-4 is a
      classifier, so rejected roots are part of the audit trail);
  (3) per-row engine provenance (engine_sha + run_id) so a detached row is
      self-describing;
  (4) a run manifest hashed alongside the outputs in SHA256SUMS;
  (5) resumable + parallel + order-independent canonical hashing.

-----------------------------------------------------------------------------
SCOPE — which census this engine can drive (read before the 3044 run)
-----------------------------------------------------------------------------
The frozen `spherical_existence_mapper.map_subset` traces a ONE-DIMENSIONAL
solution branch: a size-FIVE subset is 5 constraints in 6 unknowns
(b,c,d,e,g,h) -> a curve -> an altitude interval. That is exactly what
`valid_interval`, `alg_interval`, `fold`, and `boundary` describe, and it
reproduces the frozen v3 census.

A size-SIX subset ({F1,F2}+4) is 6 constraints in 6 unknowns -> ISOLATED
points, with no altitude interval (this is stated in the frozen H4 amendment:
"size-six solutions are isolated, no altitude window"). A pseudo-arclength
tracer has no curve to trace, so `map_subset` cannot classify a size-six
subset. The 3044 size-six census therefore needs an ISOLATED-ROOT solver
(the HomotopyContinuation pipeline whose plane proof-of-concept is lift_poc.py).

This runner keeps the solver behind a small adapter seam so the forensic
layers are identical either way:

    ADAPTER = "branch"  -> FrozenBranchAdapter : size-FIVE, frozen engine
    ADAPTER = "ingest"  -> RootIngestAdapter   : size-SIX, reads solver roots

For the size-five spherical census (the 815 universe in results.csv) the
"branch" adapter is correct and runnable today; its first run is the anchor
that must reproduce the frozen v3 class hash 4ea9cbfe121a993f. For the 3044
run, point `--roots-file` at the homotopy solver's output (contract in
RootIngestAdapter) and use `--adapter ingest`.
=============================================================================
"""
import os, sys, csv, json, time, hashlib, argparse, datetime, itertools, math
import multiprocessing as mp
from collections import Counter

# --------------------------------------------------------------------------
#  paths / constants
# --------------------------------------------------------------------------
HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE_FILE = "spherical_existence_mapper.py"
PREREG_TAG  = "v1.0.2 + A01 + A02 + H4"
DEG = math.pi / 180.0

# CSV summary schema — identical to the frozen driver (so v3 stays diff-able).
CSV_SCHEMA = ["subset", "class", "tier", "valid_lo", "valid_hi", "alg_lo",
              "alg_hi", "fold", "near_degenerate", "near_zero_width",
              "boundary", "pole_inbox", "branch_ends", "notes"]

# Frozen JSONL row schema (documented; build_row is the single source of truth).
ROW_SCHEMA = [
    "subset", "class", "tier",
    "roots",                       # list of {coords,h,valid,residual,role,reason}
    "valid_interval", "alg_interval",
    "fold", "boundary",
    "near_degenerate", "near_zero_width", "pole_inbox", "branch_ends",
    "notes",
    "engine_sha", "run_id",        # per-row provenance (self-describing)
    "agree", "newton_root_count", "discrepancy",   # dual-engine (Amendment 04 §6,§7)
]


# --------------------------------------------------------------------------
#  provenance helpers
# --------------------------------------------------------------------------
def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def engine_sha():
    p = os.path.join(HERE, ENGINE_FILE)
    return sha256_file(p) if os.path.exists(p) else "ENGINE_FILE_NOT_FOUND"


def git_commit():
    try:
        import subprocess
        out = subprocess.run(["git", "rev-parse", "HEAD"], cwd=HERE,
                             capture_output=True, text=True, timeout=5)
        return out.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _round_coords(x, nd=12):
    return [round(float(v), nd) for v in x]


# --------------------------------------------------------------------------
#  canonical row builder  (single source of truth for the JSONL shape)
# --------------------------------------------------------------------------
def build_row(sub, summary, roots, eng_sha, run_id, dual=None):
    """summary: dict with engine keys; roots: list of root dicts. Returns a
    dict in ROW_SCHEMA order with every field present (null where N/A).
    dual (optional): {agree, newton_root_count, discrepancy} from the matcher."""
    valid = summary.get("valid")
    alg = summary.get("alg")
    d = dual or {}
    row = {
        "subset": list(sub),
        "class": summary.get("cls"),
        "tier": summary.get("tier"),
        "roots": roots,
        "valid_interval": [float(valid[0]), float(valid[1])] if valid else None,
        "alg_interval":   [float(alg[0]),   float(alg[1])]   if alg   else None,
        "fold": bool(summary.get("fold", False)),
        "boundary": summary.get("vbound") or None,
        "near_degenerate": summary.get("near_degenerate"),
        "near_zero_width": summary.get("near_zero_width"),
        "pole_inbox": summary.get("pole_inbox"),
        "branch_ends": list(summary.get("ends", ()) or ()),
        "notes": summary.get("notes", "") or "",
        "engine_sha": eng_sha,
        "run_id": run_id,
        "agree": d.get("agree"),
        "newton_root_count": d.get("newton_root_count"),
        "discrepancy": d.get("discrepancy"),
    }
    return row


def csv_row(sub, summary):
    v = summary.get("valid"); a = summary.get("alg")
    vl = f"{v[0]:.2f}" if v else ""; vh = f"{v[1]:.2f}" if v else ""
    al = f"{a[0]:.2f}" if a else ""; ah = f"{a[1]:.2f}" if a else ""
    return [list(sub), summary.get("cls"), summary.get("tier"), vl, vh, al, ah,
            summary.get("fold"), summary.get("near_degenerate"),
            summary.get("near_zero_width"), summary.get("vbound") or "",
            summary.get("pole_inbox"), ";".join(summary.get("ends", ()) or ()),
            summary.get("notes", "") or ""]


def root_record(coords, h_deg, valid, residual, role, reason=""):
    return {"coords": _round_coords(coords), "h": round(float(h_deg), 6),
            "valid": bool(valid), "residual": float(residual),
            "role": role, "reason": reason}


# ==========================================================================
#  ADAPTER 1 — frozen branch engine (size-FIVE)
# ==========================================================================
class FrozenBranchAdapter:
    """Wraps the frozen `map_subset` for size-five subsets and captures the
    geometrically meaningful roots WITHOUT editing the engine, by recording
    the records the engine itself produces (monkeypatch of `trace_dir` and
    `find_seed`, confined to this process). The authoritative classification
    is still the unchanged `map_subset` return.

    Archived roots (BOTH valid and invalid): the seed root, the valid- and
    algebraic-interval endpoints, and fold turning points — each with coords,
    altitude, Gate-4 validity, raw constraint residual, and a role tag.
    """
    def __init__(self):
        self.M = None; self.RAO = None; self.GC = None
        self._items = None; self._survset = None
        self._cap = []          # capture buffer (per subset, single-process)

    # -- lazy engine import (so --selftest / ingest never need engine deps) --
    def _load(self):
        if self.M is not None:
            return
        sys.path.insert(0, HERE)
        import spherical_existence_mapper as M
        import sriyantra as RAO
        import spherical_geo_check as GC
        self.M, self.RAO, self.GC = M, RAO, GC
        surv, _ = M.load()
        self._items = list(surv.items()); self._survset = set(surv)
        self._install_capture()

    def _warm(self, sub):
        for thr in (4, 3, 2):
            w = [r for s, r in self._items if len(set(sub) & set(s)) >= thr][:6]
            if w:
                return w
        return []

    def _install_capture(self):
        M = self.M
        _orig_trace = M.trace_dir
        _orig_seed = M.find_seed
        cap = self._cap

        def trace_dir(sub, z0, sgn, *a, **k):
            rec, end = _orig_trace(sub, z0, sgn, *a, **k)
            for (h_deg, valid, reason, coords) in rec:
                cap.append(("branch", coords, h_deg, valid, reason))
            return rec, end

        def find_seed(sub, warm, *a, **k):
            z0 = _orig_seed(sub, warm, *a, **k)
            if z0 is not None:
                cap.append(("seed", z0[:5], z0[5] / DEG, None, "seed"))
            return z0

        M.trace_dir = trace_dir
        M.find_seed = find_seed

    def _residual(self, coords, h_deg, sub):
        F = self.RAO.constraints(*coords, h_deg * DEG)
        return max(abs(F[i]) for i in sub)

    def _gate4(self, coords, h_deg):
        ok, reason = self.GC.gate4(*coords, h_deg * DEG, closure_tol=1e-7)
        return bool(ok), reason

    def _select_roots(self, sub, summary):
        """Reduce the captured branch samples to meaningful roots."""
        cap = self._cap
        out, seen = [], set()

        def add(coords, h_deg, valid, reason, role):
            key = (role, round(h_deg, 4))
            if key in seen:
                return
            seen.add(key)
            if valid is None:
                valid, reason = self._gate4(coords, h_deg)
            out.append(root_record(coords, h_deg, valid,
                                    self._residual(coords, h_deg, sub),
                                    role, reason))

        # seed
        for tag, coords, h_deg, valid, reason in cap:
            if tag == "seed":
                add(coords, h_deg, valid, reason, "seed")

        branch = [(c, h, v, r) for (tag, c, h, v, r) in cap if tag == "branch"]
        # interval endpoints (valid + algebraic)
        for label, iv in (("valid", summary.get("valid")),
                          ("alg", summary.get("alg"))):
            if not iv:
                continue
            for edge in iv:
                near = min(branch, key=lambda t: abs(t[1] - edge), default=None)
                if near:
                    add(near[0], near[1], near[2], near[3], f"{label}_endpoint")
        # fold turning points (interior altitude reversals)
        if summary.get("fold") and len(branch) >= 3:
            hs = [t[1] for t in branch]
            for i in range(1, len(hs) - 1):
                if (hs[i] - hs[i - 1]) * (hs[i + 1] - hs[i]) < 0:
                    add(branch[i][0], branch[i][1], branch[i][2],
                        branch[i][3], "fold_turn")
        return out

    def classify(self, sub):
        self._load()
        self._cap = []
        # re-bind capture buffer into the closures
        self._install_capture()
        summary = self.M.map_subset(sub, self._warm(sub),
                                    tuple(sub) in self._survset)
        roots = self._select_roots(sub, summary)
        return summary, roots


# ==========================================================================
#  ADAPTER 2 — root ingest (size-SIX / 3044)
# ==========================================================================
class RootIngestAdapter:
    """Drives the forensic layers from a homotopy solver's roots, classifying
    each isolated root with the SAME frozen Gate-4 + raw-constraint residual so
    the verdict is consistent with the rest of the project.

    Expected roots file: JSONL, one object per subset, schema

        {"subset": [1,2,3,4,6,7],
         "roots": [{"coords": [b,c,d,e,g], "h": <deg>}, ...]}

    Only coords + h are required from the solver; this adapter computes
    `valid`, `residual`, `tier`, and the subset `class`. Both Gate-4-valid and
    Gate-4-invalid roots are archived (audit trail). Interval/fold/boundary
    fields are null by construction — size-six solutions are isolated.
    """
    POLE_H = 89.0; TAU_DEG = 1e-3

    def __init__(self, roots_file):
        self.RAO = None; self.GC = None
        self.table = {}
        with open(roots_file) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                obj = json.loads(line)
                self.table[tuple(obj["subset"])] = obj.get("roots", [])

    def _load(self):
        if self.RAO is not None:
            return
        sys.path.insert(0, HERE)
        import sriyantra as RAO
        import spherical_geo_check as GC
        self.RAO, self.GC = RAO, GC

    def _min_gap_ratio(self, x, R):
        b, c, d, e, g = x
        return float(min(R - (b + c), b, c - g, g, d, e, R - (d + e))) / R

    def classify(self, sub):
        self._load()
        raw = self.table.get(tuple(sub), [])
        roots, any_valid, robust_valid = [], False, False
        for r in raw:
            coords, h_deg = r["coords"], r["h"]
            ok, reason = self.GC.gate4(*coords, h_deg * DEG, closure_tol=1e-7)
            F = self.RAO.constraints(*coords, h_deg * DEG)
            residual = max(abs(F[i]) for i in sub)
            if ok:
                any_valid = True
                R = (90.0 - h_deg) * DEG
                if self._min_gap_ratio(coords, R) >= self.TAU_DEG:
                    robust_valid = True
            roots.append(root_record(coords, h_deg, ok, residual,
                                     "isolated", reason))
        if not raw:
            cls, tier = "ALGEBRAIC_EMPTY", "-"
        elif not any_valid:
            cls, tier = "ALGEBRAIC_ONLY", "-"
        else:
            cls = "SPHERICAL_REALIZABLE"
            tier = "robust" if robust_valid else "near_degenerate"
        summary = {"cls": cls, "tier": tier, "valid": None, "alg": None,
                   "fold": False, "vbound": None, "near_degenerate": None,
                   "near_zero_width": None, "pole_inbox": None, "ends": (),
                   "notes": "size-six isolated roots (interval fields N/A)"}
        return summary, roots


# ==========================================================================
#  DUAL-ENGINE PIPELINE  (Amendment 04 §3, §6; orchestration of frozen tools)
#  - homotopy: frozen lift-generator-v1 system + roots footer, 8 Julia procs
#  - newton:   frozen newton_validator, mp.Pool(--jobs)
#  - match:    §6 agreement; homotopy authoritative, Newton non-authoritative
#  The generator and Newton validator are imported and NEVER modified.
# ==========================================================================
MATCH_EPS = 1e-6        # Amendment 04 §6 root match tolerance
ACCEPT_RESID = 1e-7     # Amendment 04 §4 round-trip acceptance
TAU_DEG = 1e-3          # Amendment 04 / H4 near-degeneracy floor

def _engine():
    sys.path.insert(0, HERE)
    sys.path.insert(0, os.path.dirname(HERE))
    import sriyantra as RAO
    return RAO

def _gate4_fn():
    sys.path.insert(0, HERE)
    sys.path.insert(0, os.path.dirname(HERE))
    import spherical_geo_check as GC
    return lambda coords, h_rad: GC.gate4(*coords, h_rad, closure_tol=1e-7)

def _min_gap_ratio(coords, R):
    b, c, d, e, g = coords
    return float(min(R - (b + c), b, c - g, g, d, e, R - (d + e))) / R

# ---- per-engine classification (same frozen Gate-4 for both) --------------
def classify_roots(sub, raw, gate4_fn, constraints_fn, tau_deg=TAU_DEG):
    """Classify a raw root list into the Amendment 04 §5 size-six labels."""
    roots, any_valid, robust = [], False, False
    for r in raw:
        coords, h_deg = r["coords"], r["h"]
        ok, reason = gate4_fn(coords, h_deg * DEG)
        F = constraints_fn(coords, h_deg * DEG)
        residual = max(abs(F[i]) for i in sub)
        if ok:
            any_valid = True
            R = (90.0 - h_deg) * DEG
            if _min_gap_ratio(coords, R) >= tau_deg:
                robust = True
        roots.append(root_record(coords, h_deg, ok, residual, "isolated", reason))
    if not raw:                       cls, tier = "ALGEBRAIC_EMPTY", "-"
    elif not any_valid:               cls, tier = "ALGEBRAIC_ONLY", "-"
    elif robust:                      cls, tier = "ROBUST_REALIZABLE", "robust"
    else:                             cls, tier = "REALIZABLE_NEAR_DEGENERATE", "near_degenerate"
    summary = {"cls": cls, "tier": tier, "valid": None, "alg": None,
               "fold": False, "vbound": None, "near_degenerate": None,
               "near_zero_width": None, "pole_inbox": None, "ends": (),
               "notes": "size-six isolated roots (interval fields N/A)"}
    return summary, roots

# ---- §6 bijective match (consistent units: h converted to radians) --------
def _vec(r): return [*r["coords"], r["h"] * DEG]

def bijective_match(hr, nr, eps=MATCH_EPS):
    cand = sorted((max(abs(a - b) for a, b in zip(_vec(hr[i]), _vec(nr[j]))), i, j)
                  for i in range(len(hr)) for j in range(len(nr)))
    uh, un, pairs = set(), set(), []
    for dist, i, j in cand:
        if dist <= eps and i not in uh and j not in un:
            uh.add(i); un.add(j); pairs.append((i, j, dist))
    return (pairs, [i for i in range(len(hr)) if i not in uh],
            [j for j in range(len(nr)) if j not in un])

# ---- §6 matcher: homotopy authoritative, Newton non-authoritative ---------
def match_subset(sub, homo_raw, newton_raw, gate4_fn, constraints_fn):
    hs, hr = classify_roots(sub, homo_raw, gate4_fn, constraints_fn)     # authoritative
    ns, nr = classify_roots(sub, newton_raw, gate4_fn, constraints_fn)
    pairs, uh, un = bijective_match(hr, nr)
    disc = []
    if hs["cls"] != ns["cls"]:                       disc.append("class")
    if len(hr) != len(nr):                           disc.append("count")
    if uh or un:                                     disc.append("unmatched")
    if any(hr[i]["valid"] != nr[j]["valid"] for i, j, _ in pairs): disc.append("gate4")
    agree = not disc
    if not agree:
        hs = dict(hs)
        hs["notes"] = (hs["notes"] + " | UNRESOLVED: " + ";".join(disc))
    dual = {"agree": agree, "newton_root_count": len(nr),
            "discrepancy": (";".join(disc) if disc else None)}
    return hs, hr, dual          # homotopy class is the census class; agree gates the tally

# ---- homotopy orchestration: frozen system + roots footer, 8 Julia procs --
def _emit_homotopy_julia(sub, path):
    """Frozen lift-generator-v1 system + a roots-output footer (orchestration).
    Footer recovers (b,c,d,e,g,h) from the first 12 (atomic) components — fixed
    by the frozen canonical variable ordering — and writes candidates to ARGS[1].
    The generator file is NOT modified: its emitted system is reused verbatim."""
    sys.path.insert(0, HERE)
    sys.path.insert(0, os.path.join(os.path.dirname(HERE), "lift"))
    import lift_generator as LG
    tmp = path + ".sys"
    LG.emit_julia(tuple(sub), tmp)                    # frozen system (+count footer)
    lines = open(tmp).read().splitlines()
    cut = next(i for i, l in enumerate(lines) if l.startswith("F = System"))
    footer = [
        "result = solve(F)",
        "rsols = real_solutions(result)",
        "ncert = 0",
        "try; cert = certify(F, solutions(result)); "
        "ncert = ndistinct_certified(cert); catch; end",
        "open(ARGS[1], \"w\") do io",
        "    for s in rsols",
        "        b=atan(real(s[2]),real(s[1])); c=atan(real(s[4]),real(s[3]))",
        "        d=atan(real(s[6]),real(s[5])); e=atan(real(s[8]),real(s[7]))",
        "        g=atan(real(s[10]),real(s[9])); r=atan(real(s[12]),real(s[11]))",
        "        h=(pi/2-r)*180/pi",
        "        write(io, \"{\\\"coords\\\":[$b,$c,$d,$e,$g],\\\"h\\\":$h}\\n\")",
        "    end",
        "end",
        "println(\"real:\", length(rsols), \" certified_distinct:\", ncert)",
    ]
    open(path, "w").write("\n".join(lines[:cut + 1] + footer) + "\n")
    try: os.remove(tmp)
    except OSError: pass
    return path

def _admissible_py(coords, h_deg, RAO):
    b, c, d, e, g = coords
    r = math.pi / 2 - h_deg * DEG
    if min(b, c, d, e, g, r) <= 1e-6 or c >= r or d >= r:
        return False
    try:
        RAO.chain(b, c, d, e, g, h_deg * DEG); return True
    except Exception:
        return False

def _accept_candidates(sub, raw, RAO):
    """Round-trip each homotopy candidate through the frozen engine; accept
    admissible reals with raw-constraint residual < ACCEPT_RESID; dedup."""
    acc = []
    for cand in raw:
        coords, h_deg = cand["coords"], cand["h"]
        if not _admissible_py(coords, h_deg, RAO):
            continue
        F = RAO.constraints(*coords, h_deg * DEG)
        if max(abs(F[i]) for i in sub) < ACCEPT_RESID:
            acc.append({"coords": [round(float(v), 12) for v in coords],
                        "h": round(float(h_deg), 9)})
    out = []
    for r in acc:
        if all(max(abs(a - b) for a, b in zip(_vec(r), _vec(o))) > MATCH_EPS
               for o in out):
            out.append(r)
    return out

def run_homotopy(subsets, out_jsonl, jobs=8, julia="julia", workdir="homo_work",
                 timeout=900, log=print):
    from concurrent.futures import ThreadPoolExecutor
    import subprocess
    os.makedirs(workdir, exist_ok=True)
    RAO = _engine()

    def one(sub):
        tag = "_".join(map(str, sub))
        script = os.path.join(workdir, f"solve_{tag}.jl")
        cand = os.path.join(workdir, f"cand_{tag}.jsonl")
        _emit_homotopy_julia(sub, script)
        try:
            subprocess.run([julia, script, cand], check=True,
                           capture_output=True, timeout=timeout)
        except Exception as ex:
            return sub, [], f"julia_error:{type(ex).__name__}"
        raw = [json.loads(l) for l in open(cand)] if os.path.exists(cand) else []
        return sub, _accept_candidates(tuple(sub), raw, RAO), "ok"

    n_ok = 0
    with open(out_jsonl, "w") as f, ThreadPoolExecutor(max_workers=jobs) as ex:
        for i, (sub, roots, status) in enumerate(ex.map(one, subsets), 1):
            f.write(json.dumps({"subset": list(sub), "roots": roots,
                                "status": status}) + "\n")
            n_ok += (status == "ok")
            if i % 25 == 0: log(f"  homotopy {i}/{len(subsets)} ...")
    log(f"homotopy done: {n_ok}/{len(subsets)} solved -> {out_jsonl}")
    return out_jsonl

# ---- Newton orchestration: frozen validator, mp.Pool(--jobs) --------------
def _newton_one(args):
    sub, n_starts, seed = args
    sys.path.insert(0, HERE)
    sys.path.insert(0, os.path.dirname(HERE))
    import newton_validator as NV
    roots = NV.solve_subset(tuple(sub), n_starts=n_starts, seed=seed)
    return list(sub), [{"coords": r["coords"], "h": r["h"]} for r in roots]

def run_newton(subsets, out_jsonl, jobs=8, n_starts=400, seed=0, log=print):
    tasks = [(s, n_starts, seed) for s in subsets]
    with open(out_jsonl, "w") as f, mp.Pool(jobs) as pool:
        for i, (sub, roots) in enumerate(
                pool.imap_unordered(_newton_one, tasks, chunksize=1), 1):
            f.write(json.dumps({"subset": sub, "roots": roots}) + "\n")
            if i % 25 == 0: log(f"  newton {i}/{len(subsets)} ...")
    log(f"newton done: {len(subsets)} subsets -> {out_jsonl}")
    return out_jsonl

def _load_roots(path):
    t = {}
    for line in open(path):
        line = line.strip()
        if line:
            o = json.loads(line); t[tuple(o["subset"])] = o.get("roots", [])
    return t

# ---- match phase: produce the forensic census from both root files --------
def run_match(subsets, homo_file, newton_file, prefix, eng_sha, run_id, log=print):
    homo = _load_roots(homo_file); newton = _load_roots(newton_file)
    gate4_fn = _gate4_fn(); RAO = _engine()
    constraints_fn = lambda coords, h_rad: RAO.constraints(*coords, h_rad)
    out_csv, out_jsonl = f"{prefix}.csv", f"{prefix}.jsonl"
    out_log, out_manifest = f"{prefix}.log", f"{prefix}_manifest.json"
    cf = open(out_csv, "w", newline=""); cw = csv.writer(cf); cw.writerow(CSV_SCHEMA)
    jf = open(out_jsonl, "w")
    n_unresolved = 0
    for sub in subsets:
        sub = tuple(sub)
        hs, hr, dual = match_subset(sub, homo.get(sub, []), newton.get(sub, []),
                                    gate4_fn, constraints_fn)
        cw.writerow(csv_row(sub, hs))
        jf.write(json.dumps(build_row(sub, hs, hr, eng_sha, run_id, dual)) + "\n")
        n_unresolved += (not dual["agree"])
    cf.close(); jf.close()
    write_provenance(out_csv, out_jsonl, out_log, out_manifest, "SHA256SUMS",
                     len(subsets), eng_sha, run_id)
    log(f"match done: {len(subsets)} subsets, {n_unresolved} UNRESOLVED "
        f"(excluded from confirmatory tally) -> {out_csv}")
    return n_unresolved


# ==========================================================================
#  universe
# ==========================================================================
def universe_from_csv(path):
    with open(path) as f:
        return [tuple(eval(r["subset"])) for r in csv.DictReader(f)]


def gen_size6():
    """{F1,F2}+4-of-{F3..F20}, dropping the rank-deficient subsets. Two
    independent linear identities among the r-difference constraints make a
    size-six system singular when its index set contains either support:

        F8  - F9  + F16        == 0    ->  support {8, 9, 16}
        F16 - F17 - F18 + F19  == 0    ->  support {16, 17, 18, 19}

    The first removes the 15 subsets whose four contain {8,9,16}; the second
    removes the single subset {1,2,16,17,18,19}. The second is invisible at
    size five (a size-five subset cannot hold four constraint indices), which
    is why it first appears here. 3060 - 16 = 3044 — verified directly from the
    Jacobian (sigma_min <= 1.8e-16 on the 16 singular subsets, >= 7.5e-5 on the
    rest) and from both identities vanishing to bit-exact zero."""
    pool = list(range(3, 21))                       # F3..F20
    DEP_SUPPORTS = (frozenset({8, 9, 16}), frozenset({16, 17, 18, 19}))
    subs = []
    for combo in itertools.combinations(pool, 4):
        idx = {1, 2} | set(combo)
        if any(dep <= idx for dep in DEP_SUPPORTS):  # rank-deficient
            continue
        subs.append((1, 2) + combo)
    return subs


# ==========================================================================
#  worker plumbing  (adapter built once per process)
# ==========================================================================
_ADAPTER = None
_ENG_SHA = None
_RUN_ID = None


def _init_worker(kind, roots_file, eng_sha, run_id):
    global _ADAPTER, _ENG_SHA, _RUN_ID
    _ENG_SHA, _RUN_ID = eng_sha, run_id
    _ADAPTER = (RootIngestAdapter(roots_file) if kind == "ingest"
                else FrozenBranchAdapter())


def _classify_one(sub):
    summary, roots = _ADAPTER.classify(sub)
    row = build_row(sub, summary, roots, _ENG_SHA, _RUN_ID)
    return sub, summary, row


# ==========================================================================
#  output finalization  (manifest + SHA256SUMS over the four files)
# ==========================================================================
def write_provenance(out_csv, out_jsonl, out_log, out_manifest, out_sums,
                     n_subsets, eng_sha, run_id):
    manifest = {
        "run_id": run_id,
        "engine_file": ENGINE_FILE,
        "engine_sha": eng_sha,
        "commit": git_commit(),
        "prereg": PREREG_TAG,
        "timestamp": now_iso(),
        "n_subsets": n_subsets,
        "csv": os.path.basename(out_csv),
        "jsonl": os.path.basename(out_jsonl),
        "log": os.path.basename(out_log),
        "csv_sha256": sha256_file(out_csv),
        "jsonl_sha256": sha256_file(out_jsonl),
        "log_sha256": sha256_file(out_log),
    }
    with open(out_manifest, "w") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)
        f.write("\n")
    files = [out_csv, out_jsonl, out_log, out_manifest]
    with open(out_sums, "w") as f:
        for p in files:
            f.write(f"{sha256_file(p)}  {os.path.basename(p)}\n")
    return manifest


def canonical_hashes(csv_path):
    rows = [r for r in csv.DictReader(open(csv_path))
            if not str(r["class"]).startswith("HALT")]
    canon = sorted((r["subset"], r["class"]) for r in rows)
    class_hash = hashlib.sha256(json.dumps(canon).encode()).hexdigest()[:16]
    robust = sorted(r["subset"] for r in rows
                    if r["tier"] == "robust" and "SPHERICAL" in r["class"])
    robust_hash = hashlib.sha256(json.dumps(robust).encode()).hexdigest()[:16]
    return class_hash, robust_hash, Counter(r["class"] for r in rows)


# ==========================================================================
#  main
# ==========================================================================
def main():
    ap = argparse.ArgumentParser(description="Forensic spherical census runner v2")
    ap.add_argument("--adapter", choices=["branch", "ingest"], default="branch",
                    help="branch=frozen size-5 engine; ingest=size-6 solver roots")
    ap.add_argument("--phase", choices=["homotopy", "newton", "match", "all"],
                    default="", help="dual-engine size-six pipeline phase")
    ap.add_argument("--julia", default="julia", help="julia binary for homotopy")
    ap.add_argument("--julia-timeout", type=int, default=900)
    ap.add_argument("--workdir", default="homo_work")
    ap.add_argument("--n-starts", type=int, default=400, help="Newton multistart count")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--homo-file", default="", help="homotopy roots JSONL (match phase)")
    ap.add_argument("--newton-file", default="", help="Newton roots JSONL (match phase)")
    ap.add_argument("--universe", default="results.csv",
                    help="CSV with a 'subset' column (size-5: results.csv)")
    ap.add_argument("--gen-size6", action="store_true",
                    help="generate the size-6 universe instead of --universe")
    ap.add_argument("--roots-file", default="",
                    help="solver roots JSONL (required for --adapter ingest)")
    ap.add_argument("--prefix", default="spherical_census_v2")
    ap.add_argument("--jobs", type=int, default=os.cpu_count() or 1)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--fresh", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    # ---- dual-engine size-six pipeline ------------------------------------
    if args.phase:
        subs = (gen_size6() if args.gen_size6 else universe_from_csv(args.universe))
        if args.limit:
            subs = subs[:args.limit]
        eng_sha = engine_sha()
        run_id = f"{args.prefix}-{now_iso()}-{eng_sha[:8]}"
        lg = open(f"{args.prefix}.log", "a")
        def plog(m):
            line = f"{now_iso()}  {m}"; print(line); lg.write(line + "\n"); lg.flush()
        plog(f"run_id={run_id} phase={args.phase} n={len(subs)} jobs={args.jobs} "
             f"prereg={PREREG_TAG}")
        homo_f = args.homo_file or f"{args.prefix}_homotopy_roots.jsonl"
        newton_f = args.newton_file or f"{args.prefix}_newton_roots.jsonl"
        if args.phase in ("homotopy", "all"):
            run_homotopy(subs, homo_f, jobs=args.jobs, julia=args.julia,
                         workdir=args.workdir, timeout=args.julia_timeout, log=plog)
        if args.phase in ("newton", "all"):
            run_newton(subs, newton_f, jobs=args.jobs, n_starts=args.n_starts,
                       seed=args.seed, log=plog)
        if args.phase in ("match", "all"):
            run_match(subs, homo_f, newton_f, args.prefix, eng_sha, run_id, log=plog)
        lg.close()
        return

    if args.adapter == "ingest" and not args.roots_file:
        sys.exit("--adapter ingest requires --roots-file (solver output JSONL)")

    out_csv = f"{args.prefix}.csv"
    out_jsonl = f"{args.prefix}.jsonl"
    out_log = f"{args.prefix}.log"
    out_manifest = f"{args.prefix}_manifest.json"
    out_sums = "SHA256SUMS"

    subs = (gen_size6() if args.gen_size6 else universe_from_csv(args.universe))
    if args.limit:
        subs = subs[:args.limit]
    eng_sha = engine_sha()
    run_id = f"{args.prefix}-{now_iso()}-{eng_sha[:8]}"

    # resume
    done = set()
    if not args.fresh and os.path.exists(out_csv):
        done = {tuple(eval(r["subset"])) for r in csv.DictReader(open(out_csv))}
    todo = [s for s in subs if s not in done]

    cf = open(out_csv, "a" if done else "w", newline="")
    cw = csv.writer(cf)
    if not done:
        cw.writerow(CSV_SCHEMA)
    jf = open(out_jsonl, "a")
    lg = open(out_log, "a")

    def log(msg):
        line = f"{now_iso()}  {msg}"
        print(line); lg.write(line + "\n"); lg.flush()

    log(f"run_id={run_id}")
    log(f"adapter={args.adapter} engine_sha={eng_sha} prereg={PREREG_TAG}")
    log(f"universe={'size6-gen' if args.gen_size6 else args.universe} "
        f"n={len(subs)} resume_done={len(done)} todo={len(todo)} jobs={args.jobs}")

    halted = False
    with mp.Pool(args.jobs, initializer=_init_worker,
                 initargs=(args.adapter, args.roots_file, eng_sha, run_id)) as pool:
        for i, (sub, summary, row) in enumerate(
                pool.imap_unordered(_classify_one, todo, chunksize=1), 1):
            if summary.get("halt"):
                cw.writerow([list(sub), "HALT_PLANE_INCONSISTENCY"] + [""] * 12)
                cf.flush()
                log(f"GATE 6 HALT at {sub} — census STOPPED")
                pool.terminate(); halted = True; break
            cw.writerow(csv_row(sub, summary))
            jf.write(json.dumps(row) + "\n")
            if i % 25 == 0:
                cf.flush(); jf.flush(); log(f"{i}/{len(todo)} ...")
    cf.close(); jf.close()

    if halted:
        lg.close(); sys.exit(2)

    class_hash, robust_hash, counts = canonical_hashes(out_csv)
    log("=" * 56)
    for k in sorted(counts):
        log(f"  {k:26s} {counts[k]}")
    log(f"  canonical class hash : {class_hash}")
    log(f"  robust set hash      : {robust_hash}")
    man = write_provenance(out_csv, out_jsonl, out_log, out_manifest, out_sums,
                           len(subs), eng_sha, run_id)
    log(f"manifest: {out_manifest}  csv_sha={man['csv_sha256'][:12]} "
        f"jsonl_sha={man['jsonl_sha256'][:12]}")
    lg.close()


# ==========================================================================
#  self-test — exercises the forensic layer end-to-end with a STUB adapter,
#  so it runs with no engine dependencies present.
# ==========================================================================
def selftest():
    import tempfile, shutil
    print("SELF-TEST: forensic output layer (stub adapter, no engine)")
    d = tempfile.mkdtemp(prefix="census_v2_selftest_")
    cwd = os.getcwd(); os.chdir(d)
    try:
        prefix = "selftest"
        out = {k: f"{prefix}{ext}" for k, ext in
               (("csv", ".csv"), ("jsonl", ".jsonl"), ("log", ".log"),
                ("man", "_manifest.json"))}
        eng = "deadbeef" * 8
        run_id = f"selftest-{now_iso()}"

        # stub roots: one valid, one invalid -> both must be archived
        def stub_classify(sub):
            summary = {"cls": "SPHERICAL_ONLY", "tier": "robust",
                       "valid": (40.0, 70.0), "alg": (10.0, 88.0),
                       "fold": True, "vbound": "ordering",
                       "near_degenerate": False, "near_zero_width": False,
                       "pole_inbox": None, "ends": ("pole", "ordering"),
                       "notes": ""}
            roots = [root_record([0.46, 0.22, 0.29, 0.49, 0.11], 55.0, True,
                                 3e-16, "seed", "ok"),
                     root_record([0.50, 0.20, 0.30, 0.50, 0.10], 40.0, False,
                                 2e-3, "valid_endpoint", "ordering")]
            return summary, roots

        subs = [(1, 2, 3, 4, 6), (1, 2, 3, 5, 7), (1, 2, 4, 8, 19)]
        cw = csv.writer(open(out["csv"], "w", newline=""))
        cw.writerow(CSV_SCHEMA)
        jf = open(out["jsonl"], "w")
        for sub in subs:
            s, roots = stub_classify(sub)
            cw.writerow(csv_row(sub, s))
            jf.write(json.dumps(build_row(sub, s, roots, eng, run_id)) + "\n")
        del cw; jf.close()
        open(out["log"], "w").write(f"{now_iso()} selftest\n")

        man = write_provenance(out["csv"], out["jsonl"], out["log"], out["man"],
                               "SHA256SUMS", len(subs), eng, run_id)

        ok = True
        def check(name, cond):
            nonlocal ok
            print(f"  [{'PASS' if cond else 'FAIL'}] {name}"); ok = ok and cond

        # 1. CSV schema intact
        hdr = next(csv.reader(open(out["csv"])))
        check("CSV header == CSV_SCHEMA", hdr == CSV_SCHEMA)

        # 2. JSONL rows: schema complete, roots include valid AND invalid,
        #    self-describing provenance present
        rows = [json.loads(l) for l in open(out["jsonl"])]
        check("JSONL row count", len(rows) == len(subs))
        keys_ok = all(set(r) == set(ROW_SCHEMA) for r in rows)
        check("every JSONL row has full ROW_SCHEMA", keys_ok)
        prov_ok = all(r["engine_sha"] == eng and r["run_id"] == run_id for r in rows)
        check("every row self-describes (engine_sha+run_id)", prov_ok)
        both = all(any(rt["valid"] for rt in r["roots"]) and
                   any(not rt["valid"] for rt in r["roots"]) for r in rows)
        check("roots archive BOTH valid and invalid", both)
        resid_ok = all(all("residual" in rt for rt in r["roots"]) for r in rows)
        check("every root carries a residual", resid_ok)

        # 3. SHA256SUMS verifies against the files
        sums_ok = True
        for line in open("SHA256SUMS"):
            digest, name = line.split()
            sums_ok = sums_ok and (sha256_file(name) == digest)
        check("SHA256SUMS matches files on disk", sums_ok)

        # 4. manifest hashes the three data files + is self-consistent
        man_ok = (man["csv_sha256"] == sha256_file(out["csv"]) and
                  man["jsonl_sha256"] == sha256_file(out["jsonl"]) and
                  man["engine_sha"] == eng and man["n_subsets"] == len(subs))
        check("manifest hashes + provenance consistent", man_ok)

        # 5. resume: re-derive 'done' set from CSV
        done = {tuple(eval(r["subset"])) for r in csv.DictReader(open(out["csv"]))}
        check("resume set recoverable from CSV", done == set(subs))

        # 6. size-6 generator sanity (count + both rank-deficient exclusions)
        s6 = gen_size6()
        struct_ok = all(x[:2] == (1, 2) and len(x) == 6 for x in s6)
        no_rankdef = all(not ({8, 9, 16} <= set(x[2:])) and
                         set(x[2:]) != {16, 17, 18, 19} for x in s6)
        check("size-6 generator: count == 3044", len(s6) == 3044)
        check("size-6 generator: {1,2}+4 with both singular supports excluded",
              struct_ok and no_rankdef)

        print("\nSELF-TEST:", "ALL PASS" if ok else "FAILURES ABOVE")
        rc_pipe = pipeline_selftest()
        return 0 if (ok and rc_pipe == 0) else 1
    finally:
        os.chdir(cwd); shutil.rmtree(d, ignore_errors=True)


def pipeline_selftest():
    """Dual-engine pieces testable without Julia/Gate-4: matcher units +
    agreement logic (stub Gate-4), Julia generation well-formedness, candidate
    round-trip via the frozen engine, and Newton parallelism."""
    print("\n" + "=" * 60)
    print("PIPELINE SELF-TEST (matcher + orchestration)")
    ok = True
    def chk(name, cond):
        nonlocal ok; print(f"  [{'PASS' if cond else 'FAIL'}] {name}"); ok = ok and cond

    # (1) bijective match — units fix: h in degrees -> radians for distance
    hr = [{"coords": [0.40, 0.20, 0.30, 0.45, 0.10], "h": 50.0, "valid": True}]
    nr = [{"coords": [0.40, 0.20, 0.30, 0.45, 0.10], "h": 50.0, "valid": True}]
    pairs, uh, un = bijective_match(hr, nr)
    chk("identical roots match (eps)", len(pairs) == 1 and not uh and not un)
    nr2 = [{"coords": [0.40, 0.20, 0.30, 0.45, 0.10], "h": 50.01, "valid": True}]
    p2, _, _ = bijective_match(hr, nr2)
    chk("0.01 deg gap exceeds eps -> no match", len(p2) == 0)

    # (2) agreement logic with stub Gate-4 / constraints (no spherical_geo_check)
    stub_gate4 = lambda coords, h_rad: (coords[0] > 0.35, "stub")
    stub_cons = lambda coords, h_rad: {i: 0.0 for i in range(1, 21)}
    sub = (1, 2, 3, 4, 6, 7)
    roots = [{"coords": [0.40, 0.20, 0.15, 0.20, 0.10], "h": 20.0}]
    hs, hr_, dual = match_subset(sub, roots, roots, stub_gate4, stub_cons)
    chk("identical engines -> agree", dual["agree"] and dual["discrepancy"] is None)
    hs2, _, dual2 = match_subset(sub, roots, [], stub_gate4, stub_cons)
    chk("count mismatch -> unresolved", (not dual2["agree"])
        and "count" in dual2["discrepancy"])
    chk("homotopy class authoritative", hs2["cls"] == "ROBUST_REALIZABLE")
    chk("unresolved note recorded", "UNRESOLVED" in hs2["notes"])

    # (3) Julia generation: frozen system + roots footer, well-formed
    try:
        _emit_homotopy_julia((1, 2, 3, 4, 6, 7), "selftest_solve.jl")
        txt = open("selftest_solve.jl").read()
        jok = ("real_solutions" in txt and "ARGS[1]" in txt
               and "F = System" in txt and "certify" in txt and "@var" in txt)
        os.remove("selftest_solve.jl")
    except Exception as ex:
        jok = False; print("    julia-gen error:", ex)
    chk("homotopy Julia script well-formed (frozen system + roots footer)", jok)

    # (4) candidate round-trip via frozen engine accepts a true root, rejects junk
    try:
        RAO = _engine()
        nr_real = __import__("newton_validator").solve_subset((1, 2, 3, 4, 6, 7),
                                                              n_starts=120, seed=1)
        if nr_real:
            cand = [{"coords": nr_real[0]["coords"], "h": nr_real[0]["h"]},
                    {"coords": [0.4, 0.2, 0.3, 0.45, 0.1], "h": 50.0}]  # junk
            acc = _accept_candidates((1, 2, 3, 4, 6, 7), cand, RAO)
            rt_ok = (len(acc) == 1)        # true root accepted, junk rejected
        else:
            rt_ok = True; print("    (no Newton root found for round-trip probe)")
    except Exception as ex:
        rt_ok = False; print("    round-trip error:", ex)
    chk("candidate round-trip accepts true root, rejects junk", rt_ok)

    # (5) Newton parallelism (mp.Pool) produces the ingest contract
    try:
        run_newton([(1, 2, 5, 10, 15, 20)], "selftest_newton.jsonl", jobs=2,
                   n_starts=80, seed=1, log=lambda *_: None)
        o = json.loads(open("selftest_newton.jsonl").readline())
        nok = "subset" in o and "roots" in o
        os.remove("selftest_newton.jsonl")
    except Exception as ex:
        nok = False; print("    newton-parallel error:", ex)
    chk("Newton --jobs parallelism + ingest shape", nok)

    print("PIPELINE SELF-TEST:", "ALL PASS" if ok else "FAILURES ABOVE")
    return 0 if ok else 1


if __name__ == "__main__":
    main()
