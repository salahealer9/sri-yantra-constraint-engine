"""
STAGE 1 — fold analysis (exploratory).

Reproduces the three confirmed Stage-1 results on the spherical engine:
  1. Degree-normalized conditioning:  kappa(J) ~ 2.4/alpha, removed by F~_i = F_i/alpha^{d_i}.
  2. sigma_min(J~) diagnostic over the early-terminating survivor branches.
  3. Pseudo-arclength continuation: a true altitude fold reverses in h.

All solving uses the degree-normalized constraints (the standing spherical rule).
Engine: sriyantra.py.  Solver: stage1b_landscape.newton (normalized).
"""
import os, sys, math, json
_here = os.path.dirname(os.path.abspath(__file__))
_root = _here
while _root != os.path.dirname(_root):
    if os.path.exists(os.path.join(_root, "sriyantra_plane.py")):
        break
    _root = os.path.dirname(_root)
for _p in (_here, _root, os.path.join(_root, "enumeration")):
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)
import numpy as np
import sriyantra as RAO
import stage1b_landscape as L      # normalized newton + DI

PI2 = math.pi/2; DEG = math.pi/180; DI = L.DI

def _roots():
    census = os.path.join(os.path.dirname(__file__), "campaign_results", "roots.jsonl")
    return {tuple(json.loads(l)["subset"]): json.loads(l)["roots"][0]["coords"]
            for l in open(census)
            if json.loads(l).get("roots")}

# ---- normalized constraint vector and its Jacobian (square 5x6 / 5x5) ----
def Ftil(sub, z):                       # z = (b,c,d,e,g,h)
    b,c,d,e,g,h = z; a = PI2 - h
    try: F = RAO.constraints(b,c,d,e,g,h)
    except Exception: return None
    v = np.array([F[i]/a**DI[i] for i in sub])
    return v if np.all(np.isfinite(v)) else None

def jac6(sub, z, eps=1e-7):             # 5x6 Jacobian in (b,c,d,e,g,h)
    f0 = Ftil(sub, z)
    if f0 is None: return None
    J = np.zeros((5,6))
    for k in range(6):
        zp = z.copy(); zp[k]+=eps; fp = Ftil(sub, zp)
        if fp is None: return None
        J[:,k] = (fp-f0)/eps
    return J

def jac5(sub, x, h, eps=1e-7):          # 5x5 Jacobian in (b,c,d,e,g) at fixed h
    return jac6(sub, np.array([*x, h]))[:, :5]

# ---- 1. conditioning verification ----
def conditioning_table(sub, root):
    print(f"[1] conditioning of {sub}:  raw vs degree-normalized")
    print(f"    {'h(deg)':>9} {'alpha':>10} {'kappa raw':>12} {'kappa F~':>12}")
    for hd in (89, 89.9, 89.99, 89.999, 89.9999):
        h = hd*DEG; a = PI2-h; x = np.array(root)*a
        def cond(norm):
            def vec(xx):
                b,c,d,e,g = xx; F = RAO.constraints(b,c,d,e,g,h)
                return np.array([F[i]/(a**DI[i] if norm else 1.0) for i in sub])
            f0 = vec(x); J = np.zeros((5,5))
            for k in range(5):
                xp = x.copy(); xp[k]+=1e-7; J[:,k] = (vec(xp)-f0)/1e-7
            return np.linalg.cond(J)
        print(f"    {hd:9.4f} {a:10.2e} {cond(False):12.3e} {cond(True):12.3e}")

# ---- 2. sigma_min diagnostic along a downward branch ----
def sigma_min_scan(sub, root, h_hi=89.0, h_lo=15.0, dh=0.1):
    x = np.array(root)*(PI2-h_hi*DEG); h = h_hi; traj=[]
    while h >= h_lo-1e-9:
        xs,res,ok,c = L.newton(sub, x, h*DEG, maxit=80)
        if not ok: break
        J = jac5(sub, xs, h*DEG)
        smin = np.linalg.svd(J, compute_uv=False)[-1]
        traj.append((h, xs.copy(), smin)); x = xs; h -= dh
    return traj

# ---- 3. pseudo-arclength continuation (turns folds) ----
def tangent(sub, z, prefer=None):
    J = jac6(sub, z)
    if J is None: return None
    _,_,vt = np.linalg.svd(J); t = vt[-1]
    if prefer is not None: t = t if np.dot(t, prefer) >= 0 else -t
    elif t[5] > 0: t = -t                       # default: decreasing h
    return t/np.linalg.norm(t)

def arclength(sub, z0, ds=0.0015, n=2500):
    z = z0.copy(); t = tangent(sub, z); path=[z.copy()]
    if t is None: return np.array(path)
    for _ in range(n):
        zc = z + ds*t; conv=False
        for _ in range(80):
            f = Ftil(sub, zc)
            if f is None: break
            rhs = np.concatenate([f, [np.dot(zc-z, t) - ds]])
            if np.max(np.abs(rhs)) < 1e-11: conv=True; break
            J = jac6(sub, zc)
            if J is None: break
            try: dz = np.linalg.solve(np.vstack([J, t]), -rhs)
            except np.linalg.LinAlgError: break
            zc = zc + dz
        if not conv: break
        z = zc; path.append(z.copy()); tn = tangent(sub, z, prefer=t)
        if tn is None: break
        t = tn
    return np.array(path)

def seed_at(sub, root, h0, dh=0.5):
    x = np.array(root)*(PI2-89*DEG); h = 89.0
    while h > h0:
        xs,res,ok,c = L.newton(sub, x, h*DEG, maxit=60)
        if ok: x = xs
        h -= dh
    return np.array([*x, h0*DEG])

def confirm_fold(sub, root, h0):
    P = arclength(sub, seed_at(sub, root, h0))
    if len(P) < 5: return None, None, False
    h = P[:,5]/DEG
    reversed_ = h[-1] > h.min() + 0.2
    return h.min(), reversed_, True

if __name__ == "__main__":
    R = _roots()
    conditioning_table((1,2,3,4,8), R[(1,2,3,4,8)])
    print("\n[3] pseudo-arclength fold confirmation (h reverses = fold):")
    for sub, h0 in [((1,2,5,8,15),64),((1,2,8,10,14),53),((1,2,8,11,19),83),((1,2,8,10,11),79)]:
        hmin, rev, ok = confirm_fold(sub, R[sub], h0)
        tag = "FOLD" if rev else ("unresolved" if ok else "n/a")
        print(f"    {str(sub):16s} h* = {hmin:.2f}  ->  {tag}" if ok else f"    {sub}: n/a")
