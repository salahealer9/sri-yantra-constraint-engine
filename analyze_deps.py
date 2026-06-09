"""
Dependency lattice of Rao's 20 Sri Yantra constraints (spherical, 6 variables).

(A) Exact linear identities among F1..F20  (analytic, verified numerically).
(B) Completeness certificate: how many CONSTANT linear dependencies exist.
(C) Generic-rank degeneracy of every enumeration system {F1,F2} u T, |T|=4.
"""
import numpy as np
from itertools import combinations
from sriyantra import constraints, chain, DomainError, TABLE1

VARS = ['b','c','d','e','g','h']

def Fvec(p):
    F = constraints(*p)
    return np.array([F[i] for i in range(1,21)], float)

def numjac(p, eps=1e-6):
    """Central-difference Jacobian, shape (20, 6): dF_i/dvar_j."""
    J = np.empty((20,6))
    for j in range(6):
        pp = list(p); pm = list(p)
        pp[j]+=eps; pm[j]-=eps
        J[:,j] = (Fvec(pp)-Fvec(pm))/(2*eps)
    return J

# ---- build several valid, generic sample points (perturb Table-1 rows) ----
rng = np.random.default_rng(0)
seeds = [vals for _,vals in TABLE1]
points = []
attempts = 0
while len(points) < 8 and attempts < 5000:
    attempts += 1
    base = seeds[rng.integers(len(seeds))]
    cand = tuple(np.array(base) + rng.normal(0, 0.02, 6))
    try:
        J = numjac(cand)
        if np.all(np.isfinite(J)) and np.all(np.isfinite(Fvec(cand))):
            points.append(cand)
    except (DomainError, ValueError, ZeroDivisionError):
        pass
print(f"Using {len(points)} valid generic sample points.\n")

Js = [numjac(p) for p in points]   # each 20x6

# ===== (A)+(B) constant linear dependencies among the 20 gradients =====
# alpha (len 20) is a constant dependency iff alpha^T J(p) = 0 for all p.
# Stack horizontally: B = [J(p1) | ... | J(pP)]  (20 x 6P); left-null space = dependencies.
B = np.hstack(Js)                    # 20 x (6P)
U,S,Vt = np.linalg.svd(B)
tol = 1e-6 * S[0]
ndep = int(np.sum(S < tol))
print("=== (B) Completeness certificate ===")
print("singular values of stacked gradient matrix (20 x 6P):")
print("  largest:", np.array2string(S[:3], precision=3))
print("  smallest:", np.array2string(S[-4:], precision=3))
print(f"  number of CONSTANT linear dependencies among F1..F20 = {ndep}\n")

# verify the two proposed radial identities explicitly
R1 = np.zeros(20); R1[7]=+1; R1[8]=-1; R1[15]=+1          # F8 - F9 + F16
R2 = np.zeros(20); R2[15]=+1; R2[16]=-1; R2[17]=-1; R2[18]=+1  # F16 - F17 - F18 + F19
print("=== (A) Exact identities (residual = max over sample points of |alpha^T J|) ===")
for name,a in [("F8 - F9 + F16            == 0", R1),
               ("F16 - F17 - F18 + F19    == 0", R2)]:
    res = max(np.max(np.abs(a @ J)) for J in Js)
    print(f"  {name}   residual = {res:.2e}")
# also check value-level identity (not just gradient) at the sample points
v1 = max(abs(R1 @ Fvec(p)) for p in points)
v2 = max(abs(R2 @ Fvec(p)) for p in points)
print(f"  value-level: max|F8-F9+F16| = {v1:.2e},  max|F16-F17-F18+F19| = {v2:.2e}\n")

# rank of the radial family {8,9,16,17,18,19} (constraint indices -> rows 7,8,15,16,17,18)
radial_rows = [7,8,15,16,17,18]
ranks = [np.linalg.matrix_rank(J[radial_rows,:], tol=1e-7) for J in Js]
print(f"=== Radial family rank (constraints 8,9,16,17,18,19) over points: {ranks} ===\n")

# ===== (C) generic-rank degeneracy of enumeration systems {1,2} u T =====
choosable = list(range(3,21))            # F3..F20
ess_rows = [0,1]                          # F1, F2
def ratio_over_points(rows):
    best = 0.0
    for J in Js:
        sv = np.linalg.svd(J[rows,:], compute_uv=False)
        best = max(best, sv[-1]/sv[0])    # min/max singular value
    return best                            # full-rank -> not tiny at >=1 point

DEG_TOL = 1e-7
degenerate = []
for T in combinations(choosable, 4):
    rows = ess_rows + [t-1 for t in T]
    if ratio_over_points(rows) < DEG_TOL:
        degenerate.append(T)

print("=== (C) Generic-rank scan of all C(18,4)=3060 spherical systems {1,2}+T ===")
print(f"  degenerate (generically rank-deficient) systems: {len(degenerate)} of 3060")
print(f"  well-posed systems: {3060-len(degenerate)} of 3060\n")

# classify degenerate ones by which radial circuit they contain
C1={8,9,16}; C2={16,17,18,19}; C3={8,9,17,18,19}
def cause(T):
    s=set(T); tags=[]
    if C1<=s: tags.append("contains {8,9,16}")
    if C2<=s: tags.append("contains {16,17,18,19}")
    if C3<=s: tags.append("contains {8,9,17,18,19}")
    return tags if tags else ["** NON-RADIAL **"]

from collections import Counter
cnt = Counter()
nonradial = []
for T in degenerate:
    tg = cause(T); cnt[tuple(tg)] += 1
    if tg == ["** NON-RADIAL **"]:
        nonradial.append(T)
print("  breakdown by cause:")
for k,v in cnt.items():
    print(f"    {v:4d}  {' & '.join(k)}")
if nonradial:
    print("\n  NON-RADIAL degenerate systems (new structure!):")
    for T in nonradial[:40]:
        print("    ", (1,2)+T)
else:
    print("\n  -> every degeneracy is explained by the radial matroid. No new sources.")
