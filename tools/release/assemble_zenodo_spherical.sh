#!/usr/bin/env bash
# assemble_zenodo_spherical.sh — build the Zenodo deposit bundle for the spherical census dataset.
#
# ORDER (the plane-deposit lesson, enforced): stage -> copy data -> generate ALL text files ->
# VERIFY frozen numbers against the shipped jsonl (fail loud) -> fix mtimes -> SHA256SUMS LAST
# (self-exclusion-safe) -> deterministic zip. No timestamps in any generated file except the
# declared date-released in CITATION.cff.
#
# Usage (on the server, from /opt/sri-yantra-constraint-engine):
#   bash enumeration/assemble_zenodo_spherical.sh
#   SKIP_FREEZE=1 bash ... assemble_zenodo_spherical.sh   # plumbing test only (skips number check)
set -euo pipefail

ROOT="${ROOT:-/opt/sri-yantra-constraint-engine}"
STAGE="$ROOT/dist/zenodo_spherical_v1.0.0"
VERSION="1.0.0"
DATE_RELEASED="2026-07-03"                      # CONFIRM before upload
DOI="10.5281/zenodo.21170076"
TAG="spherical-census-layer1-v1.2"
CHECKPOINT_DIR="$ROOT/docs/census_checkpoint_layer1_k12"
FIXED_MTIME="202607030000"                      # deterministic archive mtimes (UTC)

echo "== stage =="
rm -rf "$STAGE"; mkdir -p "$STAGE/census" "$STAGE/sidecars"

echo "== copy census checkpoint =="
cp "$CHECKPOINT_DIR"/spherical_roots.jsonl \
   "$CHECKPOINT_DIR"/spherical_census.csv \
   "$CHECKPOINT_DIR"/spherical_census_manifest.json \
   "$CHECKPOINT_DIR"/spherical_census.log \
   "$CHECKPOINT_DIR"/SHA256SUMS \
   "$STAGE/census/"

echo "== copy sidecars (audit evidence; NOT census input) =="
cp "$ROOT/docs/candidates_layer1_full_highcond.jsonl"                       "$STAGE/sidecars/"
cp "$ROOT/docs/candidates_layer1_k12_highcond.jsonl"                        "$STAGE/sidecars/"
cp "$ROOT/docs/candidates_layer1_full_domainok_removed_outofdomain.jsonl"   "$STAGE/sidecars/superhemispheric_removed_outofdomain.jsonl"
cp "$ROOT/docs/candidates_layer1_full_domainok_filter_meta.json"            "$STAGE/sidecars/domain_filter_meta_full.json"
cp "$ROOT/docs/candidates_layer1_k12_domainok_filter_meta.json"             "$STAGE/sidecars/domain_filter_meta_k12.json"

echo "== generate text files (ALL edits before ANY hashing) =="

cat > "$STAGE/CITATION.cff" <<EOF
cff-version: 1.2.0
message: "If you use this dataset, please cite it as below."
type: dataset
title: "Sri Yantra Spherical Constraint Census — Certified Two-Layer Presence Census (v${VERSION})"
version: "${VERSION}"
doi: "${DOI}"
date-released: "${DATE_RELEASED}"
license: "CC-BY-4.0"
authors:
  - family-names: "Gherbi"
    given-names: "Salah-Eddin"
    orcid: "https://orcid.org/0009-0005-4017-1095"
keywords:
  - "Sri Yantra"
  - "constraint systems"
  - "interval arithmetic"
  - "Krawczyk operator"
  - "certified computation"
  - "spherical geometry"
  - "computational geometry"
EOF

cat > "$STAGE/sidecars/SIDECARS_README.md" <<'EOF'
# Sidecar populations — audit evidence, NOT census input

Nothing in this directory contributes to any census count. These files preserve candidate
populations set aside by declared, registered filters, so that every exclusion is auditable.

- candidates_layer1_full_highcond.jsonl, candidates_layer1_k12_highcond.jsonl
  Converged candidates with Jacobian condition number above the declared cutoff COND_MAX = 1e8.
  In the diagnostic sample, no candidate above cond ~1e6 was ever certified; the cutoff sits two
  orders of magnitude above that. Numerical evidence of near-singular structure; not a proof of
  positive-dimensional components.
- superhemispheric_removed_outofdomain.jsonl
  Real roots of the trigonometric system with h <= 0 (r > pi/2), outside the registered Meru
  altitude domain (0, pi/2). Excluded by domain registration, not by any defect.
- domain_filter_meta_full.json, domain_filter_meta_k12.json
  Provenance of the domain filter (criterion, input/output hashes, counts).
EOF

# README with numbers injected AFTER verification (placeholder tokens now)
cat > "$STAGE/README.md" <<EOF
# Sri Yantra Spherical Constraint Census — Certified Two-Layer Presence Census (v${VERSION})

Dataset DOI: https://doi.org/${DOI}
Author: Salah-Eddin Gherbi (ORCID 0009-0005-4017-1095)

This deposit contains the final checkpoint (CENSUS_CHECKPOINT_LAYER1_K12, repository tag
\`${TAG}\`) of a certified presence census of C. S. Rao's (1998) spherical Sri Yantra
constraint system over a registered universe of 3044 well-posed six-constraint subsets.

## Headline figures (recomputed from census/spherical_roots.jsonl at bundle time)

    FEASIBLE_CERTIFIED subsets        @FEAS@
    UNRESOLVED_CERT_FAILED subsets    @CF@      (mechanism-tagged refusals)
    UNRESOLVED_NO_CANDIDATE subsets   @NC@      (unreached at tested budgets k in {6,12})
    INFEASIBLE_CERTIFIED              0         (no absence claimed)
    certified distinct roots          @ROOTS@   (disjoint-box collapse)
    Gate-4/Rao-valid roots            @G4V@
    Gate-4/Rao-rejected roots         @G4X@
    multi-root subsets                @MULTI@
    both-validity-type subsets        @BOTH@    (>=1 valid AND >=1 rejected root)

Geometric validity is per-root metadata; it never affects certification. Every certified root
record carries its certifying box, residual, radius used, conditioning, engine hash, and Gate-4 tag.

## Contents

    census/     spherical_roots.jsonl        source of truth (one record per subset)
                spherical_census.csv         derived tabular index
                spherical_census_manifest.json, spherical_census.log, SHA256SUMS
    sidecars/   audit populations (NOT census input; see sidecars/SIDECARS_README.md)
    CITATION.cff, README.md, SHA256SUMS

## Provenance

Frozen constraint engine SHA-256:
de64edfa4979905830452ab7b9a423a73006ed20dbae67cd56ac29110b161667
Candidate discovery is deterministic (fixed global seed, per-subset blake2b seeding); candidate
files regenerate byte-identically from committed source. Certification uses the Krawczyk interval
operator under the registered extended radius list [3e-3 .. 1e-7], passed explicitly; the
escalation stopping rule (N < 25 new certifications per budget doubling) was committed before the
run it governs. Checkpoint lineage: v1.0 (836) -> v1.1 (876, extended radii) -> v1.2 (888, k=12).
Rao (1998) is cited, not redistributed; the consulted copy is identified by SHA-256 in the
repository for provenance.

## Verification

    sha256sum -c SHA256SUMS
    (cd census && sha256sum -c SHA256SUMS)

## Related records

- Pre-registration — altitude-resolved classification: https://doi.org/10.5281/zenodo.20778921
- Spherical-to-plane reduction of Rao's constraint system: https://doi.org/10.5281/zenodo.20772247
- Plane census dataset v1.1.0: https://doi.org/10.5281/zenodo.20742389
- Sri Yantra Constraint Viewer — Certified Plane Atlas v1.0.0: https://doi.org/10.5281/zenodo.20747115

## License

CC-BY-4.0 (see CITATION.cff).
EOF

# Zenodo API/metadata snippet (relation types: confirm before upload)
cat > "$STAGE/zenodo_metadata.json" <<EOF
{
  "upload_type": "dataset",
  "title": "Sri Yantra Spherical Constraint Census — Certified Two-Layer Presence Census (v${VERSION})",
  "version": "${VERSION}",
  "doi": "${DOI}",
  "license": "cc-by-4.0",
  "creators": [{"name": "Gherbi, Salah-Eddin", "orcid": "0009-0005-4017-1095"}],
  "related_identifiers": [
    {"identifier": "10.5281/zenodo.20778921", "relation": "isDocumentedBy", "resource_type": "publication-preprint"},
    {"identifier": "10.5281/zenodo.20772247", "relation": "references",     "resource_type": "publication-preprint"},
    {"identifier": "10.5281/zenodo.20742389", "relation": "continues",      "resource_type": "dataset"},
    {"identifier": "10.5281/zenodo.20747115", "relation": "references",     "resource_type": "software"}
  ],
  "description": "Final checkpoint (CENSUS_CHECKPOINT_LAYER1_K12) of a certified two-layer presence census of Rao's (1998) spherical Sri Yantra constraint system: 888 certified-feasible subsets, 968 Krawczyk-certified roots with per-root Gate-4/Rao geometric-validity tags (525 valid / 443 rejected), 77 multi-root subsets, mechanism-tagged refusals, and auditable sidecar populations. Deterministic, frozen-engine, hash-verified."
}
EOF

echo "== VERIFY frozen numbers against the shipped jsonl (fail loud) =="
python3 - "$STAGE" <<'PYEOF'
import json, sys, os
stage=sys.argv[1]
rows=[json.loads(l) for l in open(os.path.join(stage,'census','spherical_roots.jsonl'))]
cls={}
for r in rows: cls[r['class']]=cls.get(r['class'],0)+1
feas=cls.get('FEASIBLE_CERTIFIED',0); cf=cls.get('UNRESOLVED_CERT_FAILED',0)
nc=cls.get('UNRESOLVED_NO_CANDIDATE',0)
roots=sum(len(r['roots']) for r in rows)
g4v=sum(1 for r in rows for t in r['roots'] if t.get('gate4',{}).get('valid') is True)
g4x=sum(1 for r in rows for t in r['roots'] if t.get('gate4',{}).get('valid') is False)
multi=sum(1 for r in rows if r['num_certified_roots']>1)
both=sum(1 for r in rows if r['roots'] and
         any(t['gate4'].get('valid') is True for t in r['roots']) and
         any(t['gate4'].get('valid') is False for t in r['roots']))
computed=dict(FEAS=feas,CF=cf,NC=nc,ROOTS=roots,G4V=g4v,G4X=g4x,MULTI=multi,BOTH=both)
frozen  =dict(FEAS=888, CF=50, NC=2106, ROOTS=968, G4V=525, G4X=443, MULTI=77, BOTH=26)
print('  computed:', computed)
if os.environ.get('SKIP_FREEZE'):
    print('  SKIP_FREEZE set: freeze check skipped (plumbing test only)')
else:
    assert computed==frozen, f'FREEZE MISMATCH: {computed} != {frozen}'
    print('  freeze check PASS: bundle numbers match the paper')
# untagged roots would be a schema violation
miss=[r['subset'] for r in rows for t in r['roots'] if 'gate4' not in t]
assert not miss, f'roots without gate4: {miss[:3]}'
# sidecar counts (reported, and injected into README)
tot=0; subs=set()
for f in ('candidates_layer1_full_highcond.jsonl','candidates_layer1_k12_highcond.jsonl'):
    for l in open(os.path.join(stage,'sidecars',f)):
        j=json.loads(l); tot+=len(j['candidates']); subs.add(tuple(j['subset']))
print(f'  sidecars: high-cond {tot} candidates / {len(subs)} subsets')
# inject numbers into README
rd=open(os.path.join(stage,'README.md')).read()
for k,v in computed.items(): rd=rd.replace(f'@{k}@', str(v))
open(os.path.join(stage,'README.md'),'w').write(rd)
assert '@' not in rd.split('## Contents')[0].split('Headline')[1], 'README placeholder not filled'
print('  README numbers injected')
PYEOF

echo "== verify shipped checkpoint's own SHA256SUMS still valid =="
( cd "$STAGE/census" && sha256sum -c SHA256SUMS )

echo "== fix mtimes; write top-level SHA256SUMS LAST (self-exclusion-safe) =="
find "$STAGE" -type f -exec touch -t "$FIXED_MTIME" {} +
( cd "$STAGE" && find . -type f ! -name SHA256SUMS | sort | xargs sha256sum > SHA256SUMS \
  && touch -t "$FIXED_MTIME" SHA256SUMS )

echo "== deterministic zip =="
( cd "$ROOT/dist" && rm -f zenodo_spherical_v${VERSION}.zip \
  && find "zenodo_spherical_v${VERSION}" -type f | sort \
     | TZ=UTC zip -X -q "zenodo_spherical_v${VERSION}.zip" -@ )
sha256sum "$ROOT/dist/zenodo_spherical_v${VERSION}.zip"

echo
echo "== DONE =="
echo "Bundle: $STAGE"
echo "Upload: $ROOT/dist/zenodo_spherical_v${VERSION}.zip  (or the individual files)"
echo "Before upload: (1) confirm DATE_RELEASED, license CC-BY-4.0, title, relation types;"
echo "(2) GPG-sign the dataset tag, e.g.:"
echo "    git tag -s spherical-census-dataset-v${VERSION} -m 'Zenodo deposit ${DOI}'"
