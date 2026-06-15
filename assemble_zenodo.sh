#!/usr/bin/env bash
# assemble_zenodo.sh — deterministically stage the Tier-2 plane dataset for Zenodo.
# Run from anywhere; set REPO to the repository root and DOCS to where the dataset
# README.md / CITATION.cff live (rename the delivered zenodo-README.md /
# zenodo-CITATION.cff to README.md / CITATION.cff first, e.g. under $REPO/dataset/).
set -euo pipefail

REPO="${REPO:-/opt/sri-yantra-constraint-engine}"
DOCS="${DOCS:-$REPO/dataset}"          # holds README.md, CITATION.cff for the deposit
STAGE="${STAGE:-/tmp/zenodo-tier2-plane}"

cd "$REPO"
# provenance capture (do this against the exact state being deposited)
COMMIT="$(git rev-parse HEAD)"
TAG="$(git describe --tags --exact-match 2>/dev/null || echo '(no exact tag at HEAD)')"
DIRTY="$(git status --porcelain)"
[ -z "$DIRTY" ] || { echo "WARNING: working tree is dirty — deposit a clean, committed state."; }

rm -rf "$STAGE"; mkdir -p "$STAGE/prereg" "$STAGE/enumeration"

# --- top-level docs ---
cp "$DOCS/README.md"      "$STAGE/README.md"
cp "$DOCS/CITATION.cff"   "$STAGE/CITATION.cff"
cp "$REPO/LICENSE"        "$STAGE/LICENSE"
cp "$REPO/sriyantra_plane.py" "$STAGE/sriyantra_plane.py"

# --- pre-registration lineage + signed frozen manifest ---
cp "$REPO"/prereg/preregistration.md "$STAGE/prereg/"
cp "$REPO"/prereg/amendment-0*.md     "$STAGE/prereg/"
cp "$REPO"/prereg/erratum-tier2-01.md "$STAGE/prereg/"
cp "$REPO"/prereg/tier2-freeze.sha256      "$STAGE/prereg/"
cp "$REPO"/prereg/tier2-freeze.sha256.asc  "$STAGE/prereg/"
cp "$REPO"/prereg/tier2-freeze.sha256.asc.ots  "$STAGE/prereg/"

# --- tools (frozen confirmatory + validation/analysis) ---
for f in B.json generate_B.py campaign.py admissibility.py aar.py aa_krawczyk.py \
         plane_chain.py gate_m.py make_freeze.py tier1_crosscheck.py \
         figure_coords.py distinct_figures.py verify_param_collapse.py; do
    cp "$REPO/enumeration/$f" "$STAGE/enumeration/$f"
done

# --- result artifacts ---
cp -r "$REPO"/enumeration/campaign_results   "$STAGE/enumeration/"
cp -r "$REPO"/enumeration/crosscheck_results  "$STAGE/enumeration/"
cp -r "$REPO"/enumeration/figure_results      "$STAGE/enumeration/"
cp -r "$REPO"/enumeration/legacy_campaign_v1  "$STAGE/enumeration/"

# --- provenance file ---
MANHASH="$(sha256sum "$REPO/prereg/tier2-freeze.sha256" | cut -d' ' -f1)"
cat > "$STAGE/PROVENANCE.md" <<EOF
# Provenance

- Repository commit deposited: \`$COMMIT\`
- Tag at HEAD: \`$TAG\`
- Confirmatory frozen tag: \`tier2-freeze-2\` (supersedes \`tier2-freeze\`, commit f0581fe)
- Frozen-tool manifest sha256: \`$MANHASH\`  (prereg/tier2-freeze.sha256; GPG-signed .asc, OTS-stamped .ots)

## Expected results (re-derivation)
- gate_m.py            -> PASS (M1a escapes=0; M1b wrongly-excluded=0; M2 certifies Rao in-box)
- campaign.py 0 815    -> 134 feasible / 681 infeasible, 0 unresolved, 0 downgrades; 134 certified figures
- tier1_crosscheck.py  -> 134 agree_feasible / 681 agree_infeasible / 0 t1_missed / 0 t1_extra
- distinct_figures.py  -> 128 distinct (stable for tau <= 1e-4)
- verify_param_collapse.py -> 3 identical-parameter classes (1.7e-12 / 2.4e-14 / 1.4e-15); exact count 128

## Related DOIs
- Engine software v0.1.0: 10.5281/zenodo.20617730
- Pre-registration v1.0:  10.5281/zenodo.20630790
- Amendments v1.1-v1.4:   10.5281/zenodo.20672072, .20677502, .20692921, .20693741
- Corrigendum to Rao (1998): submitted to IJHS (IJHS-D-26-00161)

## Verification
sha256sum -c SHA256SUMS.txt
gpg --verify prereg/tier2-freeze.sha256.asc prereg/tier2-freeze.sha256
sha256sum -c prereg/tier2-freeze.sha256
EOF

# --- checksums of everything except the checksum file itself (no self-reference) ---
cd "$STAGE"
find . -type f ! -name SHA256SUMS.txt | LC_ALL=C sort | xargs sha256sum > SHA256SUMS.txt

echo "Staged at: $STAGE"
echo "Files: $(find "$STAGE" -type f | wc -l)   commit: $COMMIT   tag: $TAG"
echo
echo "Next:"
echo "  1. Review $STAGE (README.md headline, PROVENANCE.md hashes)."
echo "  2. Sign the checksums:  gpg --armor --detach-sign $STAGE/SHA256SUMS.txt"
echo "  3. Archive:  (cd $(dirname "$STAGE") && zip -r -X zenodo-tier2-plane.zip $(basename "$STAGE"))"
echo "  4. Upload the zip to Zenodo with the title/description from zenodo-metadata.txt;"
echo "     link related identifiers (engine DOI, prereg DOI) and add the ORCID."
echo "  5. After publishing, record the dataset DOI back into CITATION.cff and README.md."
