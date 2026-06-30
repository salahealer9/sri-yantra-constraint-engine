"""Writer-harness test: build a tiny census from certifier cases, verify pipeline integrity."""
import os, json, math, hashlib
import certify_2b as C
import spherical_census_io as IO

ROOT=[0.6246238466927992,0.7044304165359816,0.7482768099360514,
      0.6307397242292889,0.3136386632298885,22.64768569612002*math.pi/180]
OUT="/tmp/sph_census_test"; os.makedirs(OUT, exist_ok=True)
JL=f"{OUT}/spherical_roots.jsonl"; CSV=f"{OUT}/spherical_census.csv"
MAN=f"{OUT}/spherical_census_manifest.json"; LOG=f"{OUT}/spherical_census.log"; SHA=f"{OUT}/SHA256SUMS"
os.environ["SRIYANTRA_ENGINE"] = "/opt/sri-yantra-constraint-engine/sriyantra.py"

log=IO.CensusLog(LOG)
records=[]

# subset A: known root -> FEASIBLE_CERTIFIED
sA=[1,2,3,4,6,7]; st,ev=C.certify_2b_candidate(C.S6, ROOT)
cls,lb,cert=IO.classify_feasibility([(ROOT,st,ev)], "manual_seed")
log.log(f"subset {sA}: 1 candidate, {st} -> {cls}")
records.append(IO.make_record(sA, cls, lb, cert, "manual_seed"))

# subset B: off-root far -> UNRESOLVED_CERT_FAILED
sB=[1,2,3,4,6,8]; off=[0.50,0.55,0.90,0.45,0.50,0.30]; st,ev=C.certify_2b_candidate(C.S6, off)
cls,lb,cert=IO.classify_feasibility([(off,st,ev)], "newton")
log.log(f"subset {sB}: 1 candidate, {st} -> {cls}")
records.append(IO.make_record(sB, cls, lb, cert, "newton"))

# subset C: out-of-domain candidate -> UNRESOLVED_CERT_FAILED (NOT infeasible)
sC=[1,2,3,4,6,9]; edge=[0.5,1.40,0.70,0.55,0.30,0.40]; st,ev=C.certify_2b_candidate(C.S6, edge)
cls,lb,cert=IO.classify_feasibility([(edge,st,ev)], "monodromy")
log.log(f"subset {sC}: 1 candidate, {st} -> {cls}")
records.append(IO.make_record(sC, cls, lb, cert, "monodromy"))

# subset D: no candidate found -> UNRESOLVED_NO_CANDIDATE
sD=[1,2,3,4,6,10]
cls,lb,cert=IO.classify_feasibility([], "monodromy")
log.log(f"subset {sD}: 0 candidates -> {cls}")
records.append(IO.make_record(sD, cls, lb, cert, "monodromy"))

# subset E: two overlapping certified -> one root
sE=[1,2,3,4,6,11]
_,evA=C.certify_2b_candidate(C.S6, ROOT)
_,evB=C.certify_2b_candidate(C.S6, [ROOT[i]+(1e-5 if i==0 else 0.0) for i in range(6)])
cls,lb,cert=IO.classify_feasibility([(ROOT,"CERTIFIED_UNIQUE_GEOMETRIC",evA),
                                     (ROOT,"CERTIFIED_UNIQUE_GEOMETRIC",evB)], "trace")
records.append(IO.make_record(sE, cls, lb, cert, "trace"))

# subset F: two DISJOINT certified -> two roots, lower_bound 2
sF=[1,2,3,4,6,12]
evfar={"status":"CERTIFIED_UNIQUE_GEOMETRIC","box_bounds":[(10,10.001)]*6,
       "real_projected_center":[10]*6,"radius_used":1e-4,"residual_norm":1e-15,
       "krawczyk":["unique","cond(J)=1.0e2"],"engine_hash":ev.get("engine_hash")}
cls,lb,cert=IO.classify_feasibility([(ROOT,"CERTIFIED_UNIQUE_GEOMETRIC",evA),
                                     ([10]*6,"CERTIFIED_UNIQUE_GEOMETRIC",evfar)], "trace")
records.append(IO.make_record(sF, cls, lb, cert, "trace"))
log.log(f"subset {sF}: 2 disjoint certs -> {cls} lower_bound={lb}")
log.close()

# write pipeline
IO.write_jsonl(records, JL)
IO.derive_csv(JL, CSV)
man=IO.write_manifest(MAN, JL, CSV, LOG, command="test_census_io", random_seed=0)
IO.write_sha256sums(SHA, [JL,CSV,MAN,LOG])

# ---- VERIFY ----
print("=== census output-layer integrity ===")
# 1. jsonl parses line-by-line
nlines=0
with open(JL) as f:
    for line in f: json.loads(line); nlines+=1
print(f"  jsonl parses line-by-line: {nlines} records")
# 2. csv derives from jsonl (row count matches, classes match)
import csv as _csv
with open(CSV) as f: rows=list(_csv.DictReader(f))
csv_ok = len(rows)==nlines and all(rows[i]["class"]==records[i]["class"] for i in range(nlines))
print(f"  csv derives from jsonl (rows + classes match): {csv_ok}")
# 3. manifest hashes match files
mh_ok = (man["jsonl_sha256"]==hashlib.sha256(open(JL,'rb').read()).hexdigest()
         and man["csv_sha256"]==hashlib.sha256(open(CSV,'rb').read()).hexdigest())
print(f"  manifest hashes match outputs: {mh_ok}")
print(f"  engine_sha resolved (not 'unknown'): {man['engine_sha']!='unknown' and len(man['engine_sha'])==64}")
# 4. SHA256SUMS matches all outputs
sha_ok=True
for line in open(SHA):
    h,name=line.split(); full=f"{OUT}/{name}"
    if hashlib.sha256(open(full,'rb').read()).hexdigest()!=h: sha_ok=False
print(f"  SHA256SUMS matches all outputs: {sha_ok}")
# 5. status counts match jsonl classes
sc=IO.status_counts(JL); from collections import Counter
direct=Counter(r["class"] for r in records)
counts_ok=all(sc[k]==direct.get(k,0) for k in sc)
print(f"  manifest status_counts match jsonl: {counts_ok}")
# 6. specific-case checks
recE=records[4]; recF=records[5]
print(f"  overlap subset -> 1 root in jsonl: {len(recE['roots'])==1 and recE['root_lower_bound']==1}")
print(f"  disjoint subset -> 2 roots, lower_bound 2: {len(recF['roots'])==2 and recF['root_lower_bound']==2}")
print(f"  out-of-domain -> UNRESOLVED_CERT_FAILED (not infeasible): {records[2]['class']=='UNRESOLVED_CERT_FAILED'}")
print(f"  evidence bundle preserved (engine_hash in root): {records[0]['roots'][0]['evidence'].get('engine_hash') is not None}")
# 7. GUARDRAIL: INFEASIBLE_CERTIFIED without completeness must RAISE
try:
    IO.make_record([1,2,3,4,6,99], "INFEASIBLE_CERTIFIED", 0, [], "trace",
                   completeness_status="not_attempted", trace_status="not_run")
    guard_ok=False
except AssertionError:
    guard_ok=True
print(f"  GUARDRAIL: unfounded INFEASIBLE_CERTIFIED raises: {guard_ok}")
# 8. GUARDRAIL: numeric-only trace cannot be infeasible
try:
    IO.make_record([1,2,3,4,6,98],"INFEASIBLE_CERTIFIED",0,[],"trace",
                   completeness_status="numeric_only", trace_status="numeric_only")
    guard2=False
except AssertionError: guard2=True
print(f"  GUARDRAIL: numeric-only -> INFEASIBLE raises: {guard2}")

allok = all([nlines==6, csv_ok, mh_ok, sha_ok, counts_ok,
             len(recE['roots'])==1, len(recF['roots'])==2, records[2]['class']=='UNRESOLVED_CERT_FAILED',
             guard_ok, guard2, man['engine_sha']!='unknown'])
print()
print("ALL PASS:", allok)
