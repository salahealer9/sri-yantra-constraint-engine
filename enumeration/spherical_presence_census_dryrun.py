"""
spherical_presence_census_dryrun.py — PRESENCE-FIRST census DRY-RUN driver.

Two-layer discipline (candidate discovery is SEPARATE from certification):
  layer 1  candidate discovery  -> candidates.jsonl  (supplied; NOT invented by this driver)
  layer 2  certify_2b           -> certified geometric roots or rejection

The driver NEVER invents candidates (no global Newton wander). A subset with no supplied
candidate is honestly recorded UNRESOLVED_NO_CANDIDATE. Strict status map:
  candidate exists + certifies       -> FEASIBLE_CERTIFIED / PARTIAL_CERTIFIED_ROOTS_K
  candidate exists + fails certifier -> UNRESOLVED_CERT_FAILED
  certifier not wired for subset     -> TECH_FAIL (certify_2b returns TECH_FAIL)
  no candidate supplied              -> UNRESOLVED_NO_CANDIDATE
  technical exception                -> TECH_FAIL

Emits: spherical_roots.jsonl (source of truth), spherical_census.csv (derived), manifest
(candidate_source, candidate_file_sha256, subset_universe_sha256, n_subsets=ACTUAL), SHA256SUMS,
log. Absence is NEVER emitted as INFEASIBLE_CERTIFIED (census_io guardrails enforce this).
"""
import os, sys, json, hashlib, datetime, argparse
_here = os.path.dirname(os.path.abspath(__file__))
_root = _here
while _root != os.path.dirname(_root):
    if os.path.exists(os.path.join(_root, "sriyantra.py")):
        break
    _root = os.path.dirname(_root)
for _p in (_here, _root, os.path.join(_root, "enumeration")):
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)
import certify_2b as C
import spherical_census_io as IO

def sha_or_none(path):
    return hashlib.sha256(open(path,'rb').read()).hexdigest() if path and os.path.exists(path) else "none"

def load_candidates(path):
    """candidates.jsonl: {'subset':[...], 'candidates':[[coords],...]} per line. Keyed by subset tuple."""
    d={}
    if not path or not os.path.exists(path): return d
    for line in open(path):
        line=line.strip()
        if not line: continue
        j=json.loads(line); d[tuple(j['subset'])]=[list(c) for c in j.get('candidates',[])]
    return d

def run(universe_path, candidates_path, candidate_source, outdir, radii=None):
    os.makedirs(outdir, exist_ok=True)
    U=json.load(open(universe_path))
    subsets=[tuple(s) for s in U['subsets']]
    universe_sha=U['subsets_sha256']
    cands=load_candidates(candidates_path)
    cand_sha=sha_or_none(candidates_path)
    jsonl=os.path.join(outdir,'spherical_roots.jsonl')
    csv=os.path.join(outdir,'spherical_census.csv')
    manifest=os.path.join(outdir,'spherical_census_manifest.json')
    shasums=os.path.join(outdir,'SHA256SUMS')
    logp=os.path.join(outdir,'spherical_census.log')
    log=IO.CensusLog(logp)
    t0=datetime.datetime.now(datetime.timezone.utc).isoformat()
    log.log(f"DRY-RUN presence-first census: {len(subsets)} subsets, candidate_source={candidate_source}")
    log.log(f"universe_sha256={universe_sha}  candidates_sha256={cand_sha}")

    records=[]
    for i,sub in enumerate(subsets):
        try:
            sub_cands=cands.get(sub, [])
            certify_results=[]
            for cand in sub_cands:
                st, ev = C.certify_2b_candidate(list(sub), cand, radii=radii)
                certify_results.append((cand, st, ev))
            src = candidate_source if sub_cands else "none"
            cls, lb, reps = IO.classify_feasibility(certify_results, src)
            rec = IO.make_record(sub, cls, lb, reps, src,
                                 notes="dryrun" if sub_cands else "dryrun:no_candidate_supplied")
        except Exception as e:
            rec = IO.make_record(sub, "TECH_FAIL", 0, [], "none",
                                 notes=f"dryrun:exception:{type(e).__name__}:{e}")
        records.append(rec)
        if (i+1)%500==0: log.log(f"  ...{i+1}/{len(subsets)} processed")

    IO.write_jsonl(records, jsonl)
    IO.derive_csv(jsonl, csv)
    t1=datetime.datetime.now(datetime.timezone.utc).isoformat()
    log.log(f"done: {len(records)} records written")
    log.close()
    man=IO.write_manifest(manifest, jsonl, csv, logp,
                          commit="DRYRUN", prereg="preregistration.md",
                          n_subsets=len(subsets), subset_universe_sha256=universe_sha,
                          command=' '.join(sys.argv), timestamp_start=t0, timestamp_end=t1)
    # augment manifest with candidate provenance (dry-run specific fields)
    m=json.load(open(manifest)); m['candidate_source']=candidate_source
    m['candidate_file_sha256']=cand_sha; m['DRYRUN']=True
    json.dump(m, open(manifest,'w'), indent=2, sort_keys=True)
    IO.write_sha256sums(shasums, [jsonl, csv, manifest, logp])
    return jsonl, csv, manifest, shasums, logp, man['status_counts']

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--universe', default=os.path.join(_root,'docs','subset_universe.json'))
    ap.add_argument('--candidates', default=None)
    ap.add_argument('--candidate-source', default='none')
    ap.add_argument('--outdir', default=os.path.join(_root,'census_dryrun'))
    a=ap.parse_args()
    jsonl,csv,manifest,shasums,logp,counts=run(a.universe,a.candidates,a.candidate_source,a.outdir)
    print("=== DRY-RUN status counts ==="); [print(f"  {k:34s} {v}") for k,v in sorted(counts.items())]
    print("outputs ->", a.outdir)

