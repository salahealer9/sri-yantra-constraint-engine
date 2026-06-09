#!/usr/bin/env bash
# Run every validation / grounding script in sequence.
set -e
echo "=========================================="
echo "Sri Yantra Constraint Engine - Full Validation"
echo "=========================================="
echo
for s in sriyantra.py sriyantra_plane.py analyze_deps.py plane_deps.py geo_check.py test_rao_errors.py; do
  echo "==================== $s ===================="
  python3 "$s"
  echo
done
echo "=========================================="
echo "All validations passed."
echo "=========================================="
