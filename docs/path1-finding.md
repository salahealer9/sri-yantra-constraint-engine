# Path 1 (Full-Chain Analytic Domain Pre-filter Extension) — FINDING: empty as scoped

**Status.** Exploratory analysis (no new code; a verified negative finding). Path 1
was scoped as "extend the cone-edge analytic pre-filter to the remaining full-chain
acos domain edges (r16..r19) and other domain inequalities." The mathematics, then
verified empirically, shows there is nothing to extend: the cone-edge pre-filter
already captures every acos DOMAIN exclusion.

## The form distinction (the reason Path 1 is empty)
The six acos nodes split by argument FORM:
  - x1 = acos(cos(r)/cos(c)), x2 = acos(cos(r)/cos(d)) — RATIO form. A ratio of
    cosines CAN exceed 1 (when r<c or r<d), so there is a genuine domain edge at
    arg=1, i.e. h+c=pi/2 / h+d=pi/2. This is the cone-edge pre-filter (already built).
  - r16..r19 = acos(cos(A)*cos(B)) — PRODUCT form (A,B sums/arcs). Since |cos|<=1,
    |cos(A)*cos(B)| <= 1 ALWAYS. The acos is ALWAYS defined; there is NO domain edge.

## Verification (verify, don't assert)
1. Radial acos args over 80,000 evaluations on engine-valid points:
     |arg| > 1 (would be a domain edge): 0      (product form confirmed always in range)
     |arg| < 0.02 (near acos INFLECTION at 0):  3,702   (this is SPLIT pressure, not domain)
2. Over 20,000 random boxes, full-chain domain exclusions vs cone-edge pre-filter:
     full-chain guard returned 'domain'         : 8,049
     of those NOT already a cone-edge case       : 0
   => EVERY full-chain domain exclusion is already a cone-edge pre-filter case.
   (The cone-edge fired 9,204 times — MORE than the AA guard's 8,049 — because it is
    analytically stricter than the loose AA enclosure near the boundary, as
    established previously. It loses nothing the guard catches.)

## Conclusion
Path 1 as scoped is EMPTY. The cone-edge pre-filter (h+c>pi/2, h+d>pi/2) is COMPLETE
for acos domain exclusion. The radial acos nodes have no domain edge (product form).
Other domain conditions (tan poles at derived-arc values, sin-denominator zeros at
measure-zero surfaces like b+c+d=pi) do not admit clean entirely-invalid base-coord
analytic exclusions of the cone-edge kind, and were not part of the dominant cost.
Building a full-chain acos domain pre-filter would produce a filter that never fires.

## Redirect (where the remaining content actually is)
The remaining full-chain SPLIT pressure is NOT domain exclusion; it is INFLECTION and
denominator straddle:
  - radial acos INFLECTION at arg=0 (3,702/80,000 near 0) -> SplitNeeded;
  - atan / cos(2x) inflections; denominator straddles (e.g. U20's Q20+cos(S20)).
These are SPLIT conditions (the box is valid, just needs subdivision), addressable by
LEVER 2 (monotone across-inflection enclosure): atan and acos are MONOTONE, so their
VALUE range across the inflection at 0 is just [f(endpoints)] — only the tight affine
form needs the single-sign condition. Replacing SplitNeeded-at-inflection with a
rigorous monotone enclosure would convert a large fraction of these splits into
direct (looser but valid) enclosures, reducing subdivision WITHOUT touching the
genuine acos domain edge (which must still split where acos is undefined).

## Recommended next coding lever
LEVER 2 (across-inflection monotone enclosure) is the next lever with actual content
— it attacks the remaining split pressure the cone-edge filter cannot. Path 2
(coordinate-straightening) remains a paper-scoping task. Path 1 is closed as empty.

SHA-256 hash for this file is recorded in `docs/SHA256SUMS`