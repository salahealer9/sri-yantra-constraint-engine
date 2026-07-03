# Section 1 — The Rao spherical system and the registered subset universe (draft)

## 1.1 The spherical Sri Yantra construction

The Sri Yantra is a traditional sacred diagram whose central figure is a network of interpenetrating
triangles inscribed in a circle. Rao (1998) formalized the SPHERICAL form of this figure -- the
triangles drawn as arcs of great circles on a sphere (the Kurma-prishtha Meru form) -- and reduced
its construction to a system of nonlinear equations in a small number of angular variables.

In Rao's formulation the triangular complex is built on a vertical axis of symmetry, with a circum-
circle of angular radius r about the figure's centre. Nine base points along the axis are located by
their signed angular distances from the centre. Rao takes six of these intercepts as the basic
variables -- b, c, d, e, g, and the altitude h (all in radians) -- with the remaining geometry
determined by the construction. The circum-radius and altitude satisfy

    r = a + b + c = d + e + f = pi/2 - h                                    (Rao 1998, eq. 2.2)

so the base points a = r - (b+c) and f = r - (d+e) are fixed once the basic variables are chosen, and
every base point lies within the axial interval [-r, r] by construction. (This containment condition
becomes central in Section 2.)

## 1.2 The constraint functions

Rao derives twenty geometric conditions F1, ..., F20 that a correctly-drawn figure must satisfy --
concurrency of triples of lines, equalities of arc lengths, points lying on the circum-circle, and so
on -- each expressed as a function of the basic variables that must vanish. Because there are six
basic variables, a determinate figure is specified by requiring SIX of the twenty conditions to hold
simultaneously; the resulting six-equation system in six unknowns is then solved for a figure. Rao
solved individual such systems numerically; the present work certifies and enumerates their solutions
systematically.

## 1.3 The registered subset universe

Two of the twenty conditions, F1 (concurrency) and F2 (concentricity), are treated by Rao as
essential and are included in every system. A candidate figure-defining system is therefore {F1, F2}
together with a choice of four further conditions from the remaining eighteen, giving C(18,4) = 3060
candidate six-constraint subsets.

Not all of these are well-posed: some choices yield a Jacobian that is rank-deficient at generic
points, so the six conditions do not locally determine the six variables. We exclude these by a rank
scan -- evaluating the Jacobian rank at seeded sample points under a fixed degeneracy tolerance -- and
remove the 16 rank-deficient subsets. This leaves a REGISTERED UNIVERSE of

    3060 - 16 = 3044 well-posed six-constraint subsets,

which is fixed in advance and is the object of the census. The word "registered" throughout signals
that the universe, the certification radii, the geometric-validity test, and the altitude domain are
all declared before enumeration, not adjusted to the results.

## 1.4 The registered altitude domain

The altitude h is a physical elevation, so the figure is registered on the domain h in (0, pi/2),
equivalently the circum-radius r = pi/2 - h in (0, pi/2). Solutions of the constraint system with
h <= 0 (super-hemispheric caps, r > pi/2) are real roots of the trigonometric equations but lie
outside the registered Meru domain; they are excluded from the census and retained separately (see
Sections 4 and 7). Fixing this domain in advance matters because Rao's base-point construction, and
the geometric-validity test built on it, are only meaningful within it.

---
## Notes (author; delete before submission)
- 1.1: check the arc/base-point description against Rao Fig 2.1/2.2 and eq 2.2 wording before final.
  The "nine base points P1..P9 on the axis within [-r,r]" framing is from the construction pages.
- 1.2: "twenty conditions F1..F20" and "F1 concurrency / F2 concentricity essential" from Rao's
  constraint section (F1..F20) and the "any 6 constraints" remark. Confirm F1/F2 labels against the
  engine's constraint indexing (concurrency/concentricity = the two always-included essentials).
- 1.3: 3060=C(18,4); 16 rank-deficient; 3044. Confirm the "16" and the rank-scan parameters
  (DEG_TOL, seed) against analyze_deps / generate_universe before final; cite the exact tolerance.
- 1.4: super-hemispheric exclusion forward-refs Sections 4/7; keep consistent with the h-domain
  incident's appendix treatment.
- Rao (1998) cited, NOT redistributed (copyright); page/eq refs only.
