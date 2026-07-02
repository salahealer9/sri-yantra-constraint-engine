# Spherical census: two-layer result — 26 certified constraint-roots, 22 Gate-4-valid figures

## Result
Layer 1 (certification -- committed, UNCHANGED):
    FEASIBLE_CERTIFIED constraint roots = 26
Layer 2 (Gate-4 geometric validity -- NEW metadata, does not relabel Layer 1):
    GEOM_VALID_GATE4    = 22
    GEOM_REJECTED_GATE4 =  4
    GEOM_GATE4_UNAUDITED=  0
Full Gate-4 used (spherical_geo_check.gate4: constructibility + base-point ordering + figure closure).

## The 4 Gate-4-rejected roots form a coherent ORDERING-VIOLATION family (NOT scattered noise)
    (1,2,3,4,6,7)   r=1.1755   [the benchmark]
    (1,2,3,4,6,13)  r=1.1736
    (1,2,3,6,7,13)  r=1.1769
    (1,2,4,6,7,13)  r=1.1717
All 4: reason = "base-point ordering violated" (none failed on constructibility or closure).
CAUSAL SIGNAL is the ORDERING MARGIN, not the raw value of r: in this family b+c > r and/or
d+e > r, so the named base points P1=-(b+c) and/or P9=d+e fall OUTSIDE the Gate-4 ordering
interval [-r, r]. It is NOT 'high r' per se -- the 22 VALID roots span r in [0.23, 1.31], reaching
HIGHER (r=1.31) than the rejected cluster (r~1.17). The discriminant is the ordering margin
(r-(b+c), r-(d+e)) going negative, in a benchmark-adjacent constraint neighborhood ({1,2}+ from
{3,4,6,7,13}) -- call it the benchmark-adjacent ordering-violation regime, not a high-r regime.

## Claims (tightened -- do not overstate)
PROVEN:
 - 26 certified constraint-roots (Layer 1 certification unaffected by any of this).
 - L.newton coordinate convention is raw/identity (bridge danger resolved).
 - Under real Gate-4: 22 valid, 4 rejected; all 4 rejections are ordering violations.
 - The benchmark root is in the Gate-4-rejected family (not a lone outlier; a family of 4).
CONSISTENT-WITH (not proven):
 - find_seed cannot return the benchmark as a valid mapper hit because Gate-4 filters it; the
   earlier find_seed None is CONSISTENT with Gate-4 filtering, NOT proven to be "found and discarded"
   (budget/altitude sampling could also contribute).
NOT YET DETERMINED (needs geometric examination, not inference):
 - whether the 4 rejected roots are genuinely geometrically-invalid Sri Yantras, OR whether Gate-4's
   base-point-ordering convention is stricter/different from what Rao's constraint system intends.
   Evidence leans "genuinely degenerate" (clear ordering-margin violation; Rao Table 1 figures all
   pass Gate-4), but that is a lean, not a proof. The benchmark was chosen as a convenient
   certification target, not as a geometrically canonical figure.

## Consequence for the mapper (Move 3 direction)
find_seed filters to Gate-4-valid figures, so it CANNOT be a drop-in candidate source for the
Layer-1 constraint-root census (it would suppress benchmark-family roots). But its seed-generation
+ L.newton machinery CAN be reused if Gate-4 is bypassed as a return filter and recorded as
metadata. Two coherent targets, to be chosen deliberately:
    (A) Layer-1 census (all constraint-roots): mapper proposes (Gate-4 OFF as filter),
        certify_2b_general decides, Gate-4 recorded as Layer-2 metadata.
    (B) Layer-2 census (Gate-4-valid figures only): find_seed as-is is the natural generator.

## Discipline invariants (unchanged)
discovery PROPOSES; certify_2b_general DECIDES; census_io RECORDS. Gate-4 is METADATA, never a
relabel of certification. No candidate -> UNRESOLVED_NO_CANDIDATE. Artifacts regenerable from
committed source. Coordinate bridges proven by round-trip, never assumed.

## Files
    gate4_census_audit.py     full Gate-4 over certified roots -> gate4_status.json (Layer-2 metadata)
    gate4_ordering_audit.py   ordering-only variant (runs without mapper stack)
    gate4_status.json         per-subset {status, reason, r, margins}

SHA-256 hashes for all files in this unit are recorded in `docs/SHA256SUMS`