#!/usr/bin/env python3
"""lift_generator_v2.py — regularized spherical lift (lift-generator-v2).

Implements the frozen specification (lift-generator-v2-spec.md,
SHA-256 5db1f12f19f17fc343de5be1c78cadf0aaccfcc6c65e1602a63313ff6e3d64e9).

The ONLY change from the frozen lift-generator-v1 is the constraint-lift branch:
arc-equality constraints (the CONS_ANGLE family, all except F3/F4/F6, including
the doubled F13/F14/F15) are encoded as sin(combo) instead of cos(combo)-1.
This removes the regularity defect (singular continuation targets) while leaving
the admissible solution set unchanged (the only extra zero, Delta=pi or pi/2, is
filtered by the engine round-trip and is geometrically inaccessible).

Everything structural — variable set, canonical ordering, atomic/angle/ratio
blocks, dependency closure, serialization, engine_aux lift — is reused VERBATIM
from the frozen v1 module. v1 is imported, never modified. v2 builds its system
by replacing only block D of v1's output, so structural identity to v1 is exact
(asserted in the acceptance suite).
"""
import sys, os
_here = os.path.dirname(os.path.abspath(__file__))
_root = os.path.dirname(_here)
sys.path.insert(0, _here)
sys.path.insert(0, _root)
import sympy as sp
import lift_generator as LG                       # FROZEN v1 — imported, not edited

SPEC_VERSION = "lift-generator-v2"
SPEC_SHA = "5db1f12f19f17fc343de5be1c78cadf0aaccfcc6c65e1602a63313ff6e3d64e9"

# re-export frozen helpers so v2 is a drop-in replacement for v1
engine_aux   = LG.engine_aux
system_hash  = LG.system_hash
arc          = LG.arc
ATOMIC_NAMES = LG.ATOMIC_NAMES
CONS_COS     = LG.CONS_COS
CONS_ANGLE   = LG.CONS_ANGLE
DOUBLED      = LG.DOUBLED
RAO          = LG.RAO


def constraint_lift(i):
    """v2 constraint encoding (spec §3):
       * curved cosine forms F3/F4/F6 (CONS_COS): unchanged;
       * every arc-equality (CONS_ANGLE family): sin(combo) instead of cos(combo)-1.
    """
    if i in CONS_COS:
        return LG.constraint_lift(i)              # cosine form, unchanged
    return arc(CONS_ANGLE[i])[1]                  # sin(combo)   (v1 used [0]-1)


def generate(subset):
    """Reuse v1's frozen structural assembly; replace ONLY block D (constraints).
    Variables, ordering, and structural equations are therefore identical to v1."""
    gen = dict(LG.generate(tuple(sorted(subset))))     # frozen structural blocks
    ncons = len(gen["subset"])
    cons = {i: constraint_lift(i) for i in gen["subset"]}
    gen["constraints"] = cons
    gen["equations"] = gen["equations"][:-ncons] + [cons[i] for i in gen["subset"]]
    gen["spec"] = SPEC_VERSION
    return gen


def emit_julia(subset, path):
    """Emit the v2 polynomial system for HC.jl (system only; reuses the frozen
    serialization rule). Global solving uses the seeded-monodromy footer, not a
    default solve(F) (which overflows on a system of this dimension)."""
    gen = generate(subset)
    JL = lambda e: str(sp.expand(e)).replace("**", "^")
    decl = " ".join(str(v) for v in gen["variables"])
    vlist = ", ".join(str(v) for v in gen["variables"])
    L = [f"# lift-generator-v2 system  subset {gen['subset']}  hash {system_hash(gen)[:16]}",
         "using HomotopyContinuation",
         f"@var {decl}",
         "eqs = ["]
    for e in gen["equations"]:
        L.append(f"    {JL(e)},")
    L += ["]",
          f"vars = [{vlist}]",
          "F = System(eqs; variables = vars)",
          "# global solve: use the seeded coefficient-parameter + monodromy footer."]
    open(path, "w").write("\n".join(L) + "\n")
    return system_hash(gen)
