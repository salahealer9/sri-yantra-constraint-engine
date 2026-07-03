"""
census_layer1_scratch.py — SCRATCH write-path test for Layer-1 candidates. Server-only.

Purpose: exercise the census WRITE path (census_io recording) with a layer1 candidates
file, in a scratch directory — the one link the shard diagnostics (read-only, in-memory)
did not exercise. This is the dry-run driver flow with two deliberate differences:

  1. CERTIFIER = certify_2b_general (the committed dry-run driver imports certify_2b,
     the S6-only certifier, and would refuse every non-benchmark subset).
  2. PER-ROOT Gate-4 metadata: after classification, each certified root entry gains
         root['gate4'] = {valid, reason, closure_tol=1e-7, scope:'metadata_only'}
     Locked decision (2026-07-02): Gate-4 is a property of the ROOT, not the subset —
     the shard found subsets carrying BOTH valid and rejected certified roots.
     Annotation happens strictly AFTER classify_feasibility/make_record and is asserted
     to leave class / root counts / lower bounds unchanged (Layer-1 never relabeled).

Hard guards:
  - refuses to write into docs/census_union or docs/census_dryrun (protected);
  - refuses to overwrite an existing scratch spherical_roots.jsonl without --force;
  - census_io guardrails unchanged (absence still impossible to emit, engine_sha strict).

Then a COMPARISON GATE against the committed union checkpoint (read-only on baseline):
  - overlap FEASIBLE/FEASIBLE  -> every baseline root must be re-found (<1e-9): agreement
  - baseline UNRESOLVED -> scratch FEASIBLE : upgrade preview (the merge would gain these)
  - baseline FEASIBLE -> scratch NO_CANDIDATE: out-of-scope (layer1 shard didn't cover it;
    NOT a downgrade — this scratch is a single-source census, merge preserves the union)
  - baseline FEASIBLE -> scratch CERT_FAILED/TECH_FAIL: CONTRADICTION (must be zero)

Usage:
  python3 enumeration/census_layer1_scratch.py \
      --candidates docs/candidates_layer1_shard0.jsonl \
      --candidate-source layer1 \
      --outdir docs/census_layer1_shard0_scratch \
      --baseline docs/census_union/spherical_roots.jsonl
  (add --compare-only to re-run just the comparison on an existing scratch dir)
"""
import os, sys, json, hashlib, datetime, argparse
import numpy as np
_here = os.path.dirname(os.path.abspath(__file__))
_root = _here
while _root != os.path.dirname(_root):
    if os.path.exists(os.path.join(_root, "sriyantra.py")):
        break
    _root = os.path.dirname(_root)
for _p in (_here, _root, os.path.join(_root, "enumeration")):
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)
import certify_2b_general as C              # GENERAL certifier (not certify_2b)
import spherical_census_io as IO
from spherical_geo_check import gate4

GATE4_CLOSURE_TOL = 1e-7
PROTECTED_DIRS = {'census_union', 'census_dryrun'}
MATCH_TOL = 1e-9

def sha_or_none(path):
    return hashlib.sha256(open(path,'rb').read()).hexdigest() if path and os.path.exists(path) else "none"

def load_candidates(path):
    d={}
    if not path or not os.path.exists(path): return d
    for line in open(path):
        line=line.strip()
        if not line: continue
        j=json.loads(line); d[tuple(j['subset'])]=[list(c) for c in j.get('candidates',[])]
    return d

def annotate_gate4_per_root(record):
    """Additive per-root Gate-4 metadata. MUST NOT change classification.
    Returns (record, n_tagged, n_gate4_errors) and asserts class invariance."""
    before = (record['class'], record['num_certified_roots'], record['root_lower_bound'])
    n=0; nerr=0
    for root in record['roots']:
        coords = root.get('coords')
        try:
            v, why = gate4(*[float(t) for t in coords], closure_tol=GATE4_CLOSURE_TOL)
            root['gate4'] = {'valid': bool(v), 'reason': str(why),
                             'closure_tol': GATE4_CLOSURE_TOL,
                             'scope': 'metadata_only; does not affect class'}
        except Exception as ex:
            root['gate4'] = {'valid': None, 'reason': f'gate4 raised {type(ex).__name__}',
                             'closure_tol': GATE4_CLOSURE_TOL,
                             'scope': 'metadata_only; does not affect class'}
            nerr += 1
        n += 1
    after = (record['class'], record['num_certified_roots'], record['root_lower_bound'])
    assert before == after, f"Gate-4 annotation changed classification on {record['subset']}: {before}->{after}"
    return record, n, nerr

def _guard_outdir(outdir):
    parts = set(os.path.normpath(os.path.abspath(outdir)).split(os.sep))
    hit = parts & PROTECTED_DIRS
    if hit:
        raise SystemExit(f"REFUSED: outdir {outdir} targets protected directory {sorted(hit)}; "
                         f"use a scratch dir like docs/census_layer1_shard0_scratch")

def run(universe_path, candidates_path, candidate_source, outdir, force=False,
        radii=None, restrict_census=None, restrict_class=None):
    _guard_outdir(outdir)
    jsonl=os.path.join(outdir,'spherical_roots.jsonl')
    if os.path.exists(jsonl) and not force:
        raise SystemExit(f"REFUSED: {jsonl} exists; pass --force to overwrite the SCRATCH output")
    os.makedirs(outdir, exist_ok=True)
    U=json.load(open(universe_path))
    subsets=[tuple(s) for s in U['subsets']]
    cands=load_candidates(candidates_path)
    n_restricted=0
    if restrict_census and restrict_class:
        allowed={tuple(json.loads(l)['subset']) for l in open(restrict_census)
                 if json.loads(l)['class']==restrict_class}
        n_restricted=len(cands)-len({s for s in cands if s in allowed})
        cands={s:c for s,c in cands.items() if s in allowed}
    csvp=os.path.join(outdir,'spherical_census.csv')
    manifest=os.path.join(outdir,'spherical_census_manifest.json')
    shasums=os.path.join(outdir,'SHA256SUMS')
    logp=os.path.join(outdir,'spherical_census.log')
    log=IO.CensusLog(logp)
    t0=datetime.datetime.now(datetime.timezone.utc).isoformat()
    log.log(f"SCRATCH layer1 census write-path test: {len(subsets)} subsets, "
            f"candidate_source={candidate_source}, certifier=certify_2b_general, "
            f"radii={'DEFAULT' if radii is None else radii}"
            + (f", restricted to {restrict_class} in {restrict_census} "
               f"({n_restricted} subsets' candidates dropped)" if restrict_census else ""))
    log.log(f"universe_sha256={U['subsets_sha256']} candidates_sha256={sha_or_none(candidates_path)}")

    records=[]; tagged=0; g4err=0; invariance_checked=0
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
                                 notes="layer1_scratch" if sub_cands else "layer1_scratch:no_candidate_supplied")
            rec, n, ne = annotate_gate4_per_root(rec)      # AFTER classification; asserted invariant
            tagged+=n; g4err+=ne; invariance_checked+=1
        except AssertionError:
            raise
        except Exception as e:
            rec = IO.make_record(sub, "TECH_FAIL", 0, [], "none",
                                 notes=f"layer1_scratch:exception:{type(e).__name__}:{e}")
        records.append(rec)
        if (i+1)%500==0: log.log(f"  ...{i+1}/{len(subsets)} processed")

    IO.write_jsonl(records, jsonl)
    IO.derive_csv(jsonl, csvp)
    t1=datetime.datetime.now(datetime.timezone.utc).isoformat()
    log.log(f"done: {len(records)} records; gate4-tagged roots={tagged} (errors={g4err})")
    log.close()
    cert_sha=sha_or_none(os.path.abspath(C.__file__))
    man=IO.write_manifest(manifest, jsonl, csvp, logp,
                          commit="SCRATCH", prereg="preregistration.md",
                          n_subsets=len(subsets), subset_universe_sha256=U['subsets_sha256'],
                          command=' '.join(sys.argv), timestamp_start=t0, timestamp_end=t1,
                          certifier_sha=cert_sha)
    m=json.load(open(manifest))
    m.update(SCRATCH=True, layer='layer1',
             candidate_source=candidate_source,
             candidate_file_sha256=sha_or_none(candidates_path),
             candidate_meta_sha256=sha_or_none(candidates_path.replace('.jsonl','_meta.json')),
             certifier='certify_2b_general.py',
             certifier_radii=('DEFAULT [3e-3..1e-5]' if radii is None else list(radii)),
             restriction=(dict(census=restrict_census, cls=restrict_class,
                               n_subsets_dropped=n_restricted) if restrict_census else None),
             gate4_per_root=True, gate4_closure_tol=GATE4_CLOSURE_TOL,
             gate4_roots_tagged=tagged, gate4_tag_errors=g4err,
             gate4_invariance_asserted_on=invariance_checked)
    json.dump(m, open(manifest,'w'), indent=2, sort_keys=True)
    IO.write_sha256sums(shasums, [jsonl, csvp, manifest, logp])
    return jsonl, m['status_counts']

# ---------------- comparison gate (read-only on baseline) ----------------
def _load_jsonl(path):
    return {tuple(json.loads(l)['subset']): json.loads(l) for l in open(path)}

def compare(scratch_jsonl, baseline_jsonl, candidate_source):
    scr=_load_jsonl(scratch_jsonl); base=_load_jsonl(baseline_jsonl)
    assert set(scr)==set(base), "universe mismatch between scratch and baseline"
    same=0; out_of_scope=[]; upgrades=[]; contradictions=[]; transitions=[]
    agree_roots=0; disagree=[]; extra_roots=0; multi=[]
    src_ok=True; g4_missing=[]; g4_errors=[]
    for sub in sorted(scr):
        s,b=scr[sub],base[sub]
        # advisor check 1: candidate_source recorded correctly
        if s['roots'] or s['class'] in ('UNRESOLVED_CERT_FAILED',):
            if s['candidate_source']!=candidate_source: src_ok=False
        # advisor check 2: per-root gate4 present with pinned tolerance
        for r in s['roots']:
            g=r.get('gate4')
            if not g or g.get('closure_tol')!=GATE4_CLOSURE_TOL: g4_missing.append(sub)
            elif g.get('valid') is None: g4_errors.append((sub,g.get('reason')))
        if s['num_certified_roots']>1: multi.append((sub, s['num_certified_roots']))
        sc,bc=s['class'],b['class']
        F='FEASIBLE_CERTIFIED'
        if bc==F and sc==F:
            for br in b['roots']:
                dmin=min(float(np.linalg.norm(np.array(br['coords'])-np.array(sr['coords'])))
                         for sr in s['roots'])
                if dmin<MATCH_TOL: agree_roots+=1
                else: disagree.append((sub,dmin))
            extra_roots += max(0, len(s['roots'])-len(b['roots']))
        elif bc==F and sc=='UNRESOLVED_NO_CANDIDATE': out_of_scope.append(sub)
        elif bc==F: contradictions.append((sub,bc,sc))
        elif bc!=F and sc==F: upgrades.append(sub)
        elif bc==sc: same+=1
        else: transitions.append((sub,bc,sc))

    # Gate-4 split, BOTH granularities (per-root vs per-subset — locked distinction:
    # Gate-4 is a property of the ROOT; subsets can carry both validity types)
    import math as _m
    r_valid=r_rej=r_err=0; s_any_valid=[]; s_only_rej=[]; s_both=[]
    h_all=[]; h_bad=[]
    for sub in sorted(scr):
        roots=scr[sub]['roots']
        if not roots: continue
        for r in roots:
            h=float(r['coords'][5]); h_all.append(h)
            if h<=0 or h>=_m.pi/2: h_bad.append((sub, round(h,4)))
        vs=[r.get('gate4',{}).get('valid') for r in roots]
        r_valid+=sum(1 for v in vs if v is True)
        r_rej  +=sum(1 for v in vs if v is False)
        r_err  +=sum(1 for v in vs if v is None)
        has_v=any(v is True for v in vs); has_r=any(v is False for v in vs)
        if has_v: s_any_valid.append(sub)
        if has_r and not has_v: s_only_rej.append(sub)
        if has_v and has_r: s_both.append(sub)
    print("\n=== Gate-4 split (metadata; classification untouched) ===")
    print(f"  per-root   : valid={r_valid}  rejected={r_rej}"
          + (f"  gate4-errors={r_err}" if r_err else ""))
    print(f"  per-subset : >=1 valid root={len(s_any_valid)}  only-rejected={len(s_only_rej)}"
          f"  BOTH types={len(s_both)} {sorted(s_both)[:6]}{'...' if len(s_both)>6 else ''}")
    if h_all:
        print(f"  certified-root altitude domain: h in [{min(h_all):.4f}, {max(h_all):.4f}]"
              f"  (registered: (0, pi/2))"
              + ("  ALL IN-DOMAIN" if not h_bad else f"  OUT-OF-DOMAIN ROOTS: {h_bad[:8]}"))

    print("\n=== COMPARISON GATE: scratch (layer1-only) vs committed union baseline ===")
    print(f"  identical-class rows                          : {same}")
    print(f"  UPGRADE preview (baseline UNRESOLVED -> FEAS.): {len(upgrades)}")
    print(f"  overlap FEASIBLE/FEASIBLE baseline roots re-found: {agree_roots} "
          f"({'ALL AGREE' if not disagree else 'DISAGREEMENTS: '+str(disagree)})")
    print(f"  extra distinct roots on overlap subsets       : {extra_roots}")
    print(f"  out-of-scope (baseline FEAS., shard no cand.) : {len(out_of_scope)}  [expected; merge preserves union]")
    print(f"  other transitions                             : {transitions if transitions else 0}")
    print(f"  CONTRADICTIONS (baseline FEAS. -> failed)     : {contradictions if contradictions else 0}")
    print("\n=== advisor checks ===")
    print(f"  1. candidate_source=='{candidate_source}' on all candidate rows : {'PASS' if src_ok else 'FAIL'}")
    print(f"  2. per-root gate4 with closure_tol={GATE4_CLOSURE_TOL} on every root : "
          f"{'PASS' if not g4_missing else 'FAIL '+str(g4_missing[:5])}"
          + (f"  (gate4 errors: {g4_errors})" if g4_errors else ""))
    print(f"  3. multi-root subsets preserved (num_certified_roots>1)   : "
          f"{len(multi)} {sorted(multi)}")
    print(f"  4. class invariance under gate4 annotation                : asserted per-record during write")
    print(f"  5. baseline preserved-or-upgraded (no contradictions)     : "
          f"{'PASS' if not (contradictions or disagree) else 'FAIL'}")
    print(f"  6. all certified roots in registered h-domain (0, pi/2)   : "
          f"{'PASS' if not h_bad else 'FAIL '+str(h_bad[:5])}")
    ok = src_ok and not g4_missing and not contradictions and not disagree and not h_bad
    print(f"\n=== SCRATCH WRITE-PATH GATE: {'PASS — write path proven; safe to plan the merge' if ok else 'FAIL — fix before any merge'} ===")
    return 0 if ok else 1

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--universe', default=os.path.join(_root,'docs','subset_universe.json'))
    ap.add_argument('--candidates', default=os.path.join(_root,'docs','candidates_layer1_shard0.jsonl'))
    ap.add_argument('--candidate-source', default='layer1')
    ap.add_argument('--outdir', default=os.path.join(_root,'docs','census_layer1_shard0_scratch'))
    ap.add_argument('--baseline', default=os.path.join(_root,'docs','census_union','spherical_roots.jsonl'))
    ap.add_argument('--compare-only', action='store_true')
    ap.add_argument('--force', action='store_true')
    ap.add_argument('--radii', default='', help="comma-separated certification radii, e.g. "
                    "'3e-3,1e-3,3e-4,1e-4,3e-5,1e-5,3e-6,1e-6,3e-7,1e-7' (default: certifier's)")
    ap.add_argument('--restrict-census', default='', help='census jsonl; certify only subsets '
                    'whose class there equals --restrict-class')
    ap.add_argument('--restrict-class', default='')
    a=ap.parse_args()
    jsonl=os.path.join(a.outdir,'spherical_roots.jsonl')
    if not a.compare_only:
        radii=[float(x) for x in a.radii.split(',')] if a.radii else None
        jsonl, counts = run(a.universe, a.candidates, a.candidate_source, a.outdir, force=a.force,
                            radii=radii, restrict_census=(a.restrict_census or None),
                            restrict_class=(a.restrict_class or None))
        print("=== SCRATCH status counts ==="); [print(f"  {k:34s} {v}") for k,v in sorted(counts.items())]
        print("outputs ->", a.outdir)
    sys.exit(compare(jsonl, a.baseline, a.candidate_source))
