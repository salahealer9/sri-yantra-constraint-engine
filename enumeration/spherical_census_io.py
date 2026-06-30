"""
spherical_census_io.py — spherical census OUTPUT LAYER (mirrors the plane census).
Source of truth: spherical_roots.jsonl (one record/subset, carries full certify_2b evidence).
Derived: spherical_census.csv (lightweight index, derived FROM jsonl, never the reverse).
Provenance: spherical_census_manifest.json + SHA256SUMS + spherical_census.log.

Guardrails (hard):
 - INFEASIBLE_CERTIFIED is produced ONLY from a completeness proof (completeness_status
   =='complete' AND trace_status=='passed' AND no certifiable real root). Never from
   classification, never from a numeric trace.
 - NO_REAL_ROOTS_FOUND_TRACE_NUMERIC never upgrades to INFEASIBLE_CERTIFIED.
 - engine_sha must resolve to a real frozen-engine hash; writing 'unknown' into the
   manifest raises (no silent provenance hole).
"""
import sys, os, json, hashlib, platform, datetime, glob

SCHEMA_JSONL   = "spherical_census_v1"
SCHEMA_MANIFEST= "spherical_census_manifest_v1"

ALLOWED_CLASSES = {
    "FEASIBLE_CERTIFIED","INFEASIBLE_CERTIFIED","PARTIAL_CERTIFIED_ROOTS_K",
    "UNRESOLVED_NO_CANDIDATE","UNRESOLVED_CERT_FAILED","UNRESOLVED_TRACE_FAILED",
    "NO_REAL_ROOTS_FOUND_TRACE_NUMERIC","TECH_FAIL",
}
COMPLETENESS = {"not_attempted","complete","failed","timeout","numeric_only"}
TRACE        = {"not_run","passed","failed","timeout","numeric_only"}

def resolve_engine_path():
    """Locate the frozen engine; honor SRIYANTRA_ENGINE env, else import location."""
    p = os.environ.get("SRIYANTRA_ENGINE")
    if p and os.path.exists(p): return p
    for cand in ("/opt/sri-yantra-constraint-engine/sriyantra.py",
                 "/opt/sri-yantra-constraint-engine/enumeration/sriyantra.py"):
        if os.path.exists(cand): return cand
    try:
        import sriyantra; return sriyantra.__file__
    except Exception:
        return None

def engine_sha(strict=True):
    p = resolve_engine_path()
    if p and os.path.exists(p):
        return hashlib.sha256(open(p,'rb').read()).hexdigest()
    if strict:
        raise RuntimeError("engine_sha unresolved: set SRIYANTRA_ENGINE to the frozen "
                           "engine path; refusing to write 'unknown' into an audit record.")
    return "unknown"

def _sha256_file(path):
    return hashlib.sha256(open(path,'rb').read()).hexdigest()

# ---------------- classification (feasibility mode) ----------------
def classify_feasibility(certify_results, candidate_source, completeness_status="not_attempted",
                         trace_status="not_run"):
    """certify_results: list of (candidate, status, evidence). Returns (class, lower_bound,
    certified_evidence_list). Absence is NEVER produced here."""
    import certify_2b as C
    certified = [(cand,ev) for (cand,st,ev) in certify_results if st=="CERTIFIED_UNIQUE_GEOMETRIC"]
    found_any_candidate = len(certify_results) > 0
    if certified:
        cert_evs=[ev for _,ev in certified]
        count, clusters, _ = C.collapse_certified(cert_evs)
        # one representative evidence per cluster (de-duplicated roots in the JSONL)
        reps=[cert_evs[idxs[0]] for idxs in clusters]
        return "FEASIBLE_CERTIFIED", count, reps
    # no certified root
    if any(st=="TECH_FAIL" for (_,st,_) in certify_results):
        return "TECH_FAIL", 0, []
    if found_any_candidate:
        # candidates existed but none certified (incl DOMAIN_INVALID candidates) -> cert failed
        return "UNRESOLVED_CERT_FAILED", 0, []
    return "UNRESOLVED_NO_CANDIDATE", 0, []

def _assert_infeasible_legitimate(cls, completeness_status, trace_status, lower_bound):
    if cls == "INFEASIBLE_CERTIFIED":
        if not (completeness_status=="complete" and trace_status=="passed" and lower_bound==0):
            raise AssertionError("INFEASIBLE_CERTIFIED requires completeness_status=='complete' "
                                 "AND trace_status=='passed' AND no certified real root. "
                                 "Refusing to emit unfounded absence certificate.")

# ---------------- record construction ----------------
def _root_entry(ev):
    kraw = ev.get("krawczyk"); cond=None
    if isinstance(kraw,(list,tuple)) and len(kraw)==2 and isinstance(kraw[1],str):
        import re; m=re.search(r"cond\(J\)=([0-9.eE+-]+)", kraw[1])
        if m:
            try: cond=float(m.group(1))
            except Exception: cond=None
    return {
        "coords": ev.get("real_projected_center"),
        "radius": ev.get("radius_used"),
        "residual": ev.get("residual_norm"),
        "cond_J": cond,
        "engine_hash": ev.get("engine_hash"),
        "evidence": ev,                      # FULL bundle preserved (no flattening)
    }

def make_record(subset, cls, lower_bound, certified_evidence, candidate_source,
                completeness_status="not_attempted", trace_status="not_run",
                agree=None, notes=""):
    if cls not in ALLOWED_CLASSES: raise ValueError(f"bad class {cls}")
    if completeness_status not in COMPLETENESS: raise ValueError(f"bad completeness {completeness_status}")
    if trace_status not in TRACE: raise ValueError(f"bad trace {trace_status}")
    _assert_infeasible_legitimate(cls, completeness_status, trace_status, lower_bound)
    roots=[_root_entry(ev) for ev in (certified_evidence or [])]
    return {
        "schema_version": SCHEMA_JSONL,
        "subset": list(subset),
        "class": cls,
        "root_lower_bound": lower_bound,
        "num_certified_roots": len(roots),
        "completeness_status": completeness_status,
        "trace_status": trace_status,
        "candidate_source": candidate_source,
        "roots": roots,
        "agree": agree or {"status":"not_run","sources":[],"notes":""},
        "notes": notes,
    }

# ---------------- writers ----------------
def write_jsonl(records, path):
    with open(path,"w") as f:
        for rec in records:
            if rec["class"] not in ALLOWED_CLASSES: raise ValueError("bad class in record")
            f.write(json.dumps(rec, sort_keys=True)+"\n")

CSV_COLS=["subset","class","num_roots","root_lower_bound","cert_radius","residual","cond_J",
          "completeness_status","trace_status","candidate_source","agree_status","notes"]
def derive_csv(jsonl_path, csv_path):
    """CSV is DERIVED from the jsonl (never the reverse)."""
    import csv
    with open(jsonl_path) as f, open(csv_path,"w",newline="") as g:
        wr=csv.writer(g); wr.writerow(CSV_COLS)
        for line in f:
            r=json.loads(line)
            r0=r["roots"][0] if r["roots"] else {}
            wr.writerow([
                json.dumps(r["subset"]), r["class"], len(r["roots"]), r["root_lower_bound"],
                r0.get("radius",""), r0.get("residual",""), r0.get("cond_J",""),
                r["completeness_status"], r["trace_status"], r["candidate_source"],
                r["agree"]["status"], (r["notes"] or "").replace("\n"," "),
            ])

def status_counts(jsonl_path):
    counts={k:0 for k in ALLOWED_CLASSES}
    with open(jsonl_path) as f:
        for line in f:
            counts[json.loads(line)["class"]] += 1
    return counts

def write_manifest(path, jsonl_path, csv_path, log_path, *, commit="", prereg="",
                   n_subsets=None, subset_universe_sha256="", command="", random_seed="",
                   timestamp_start="", timestamp_end="", certifier_sha=""):
    eng = engine_sha(strict=True)            # fail loud if unresolved
    man={
        "schema_version": SCHEMA_MANIFEST,
        "engine_sha": eng,
        "certifier_sha": certifier_sha or _sha256_file("certify_2b.py") if os.path.exists("certify_2b.py") else "",
        "commit": commit, "prereg": prereg,
        "timestamp_start": timestamp_start, "timestamp_end": timestamp_end,
        "n_subsets": n_subsets if n_subsets is not None else sum(1 for _ in open(jsonl_path)),
        "subset_universe_sha256": subset_universe_sha256,
        "command": command,
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "random_seed": str(random_seed),
        "status_counts": status_counts(jsonl_path),
        "jsonl_sha256": _sha256_file(jsonl_path),
        "csv_sha256": _sha256_file(csv_path),
        "log_sha256": _sha256_file(log_path) if os.path.exists(log_path) else "",
    }
    with open(path,"w") as f: json.dump(man,f,indent=2,sort_keys=True)
    return man

def write_sha256sums(path, files):
    with open(path,"w") as f:
        for fp in files:
            if os.path.exists(fp):
                f.write(f"{_sha256_file(fp)}  {os.path.basename(fp)}\n")

class CensusLog:
    def __init__(self, path): self.f=open(path,"w"); self.path=path
    def log(self, msg):
        ts=datetime.datetime.utcnow().isoformat()
        self.f.write(f"{ts} {msg}\n"); self.f.flush()
    def close(self): self.f.close()
