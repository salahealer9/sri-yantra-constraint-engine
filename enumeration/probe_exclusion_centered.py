"""
probe_exclusion_centered.py — MICRO-PROBE for stronger large-box interior exclusion.
Compares two rigorous exclusion tests on off-root interior boxes:
  NATURAL  : exclude if the natural AA enclosure F[k].iv() misses 0 (current method).
  CENTERED : exclude if the mean-value enclosure F_k(x0) + sum_j J_kj(X)*[-r_j,r_j]
             misses 0, where J_kj(X)=grad enclosure over the box (from DualRS).
Success = CENTERED excludes at a LARGER radius than NATURAL on the same point.
Rigorous: mean-value theorem + interval Jacobian; center value outward-padded.
"""
import sys, os, math, random
_here = os.path.dirname(os.path.abspath(__file__))
_root = _here
while _root != os.path.dirname(_root):
    if os.path.exists(os.path.join(_root, "sriyantra.py")):
        break
    _root = os.path.dirname(_root)
for _p in (_here, _root, os.path.join(_root, "enumeration")):
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)
import sriyantra as RAO
from aar import AAr, U, ETA
from aar_sphere import DualRS, SplitNeeded, DomainError
from chain_sphere import AA_FN, DUAL_FN
import domain_sphere_v2_prefilter as v2
cone_F = v2.cone_F; S6 = v2.S6; HALF = v2.HALF_PI; B = v2.B_SPHERE

def constraints_center(x0):
    """Exact (float, outward-padded) constraint values at the center point."""
    F = RAO.constraints(*x0)
    return {k: F[k] for k in S6}

def natural_excludes(box):
    """Current method: natural AA enclosure misses 0 for some selected constraint."""
    AAr._n=[0]
    cen=[(lo+hi)/2 for lo,hi in box]; rad=[(hi-lo)/2 for lo,hi in box]
    try:
        F = cone_F(*[AAr.var(cen[i], rad[i]) for i in range(6)], AA_FN)
    except (SplitNeeded, DomainError, ValueError, ZeroDivisionError, OverflowError):
        return None   # can't evaluate
    for k in S6:
        lo,hi=F[k].iv()
        if not (lo <= 0 <= hi): return True
    return False

def centered_excludes(box):
    """Mean-value enclosure F_k(x0)+sum_j J_kj(X)*[-r_j,r_j] misses 0 for some k."""
    cen=[(lo+hi)/2 for lo,hi in box]; rad=[(hi-lo)/2 for lo,hi in box]
    try:
        F0 = constraints_center(cen)
    except Exception:
        return None
    AAr._n=[0]
    try:
        Fd = cone_F(*[DualRS.var(j, cen[j], rad[j]) for j in range(6)], DUAL_FN)
    except (SplitNeeded, DomainError, ValueError, ZeroDivisionError, OverflowError):
        return None
    for k in S6:
        f0 = F0[k]
        # outward pad for the float center evaluation
        lo = f0 - (U*abs(f0)+ETA); hi = f0 + (U*abs(f0)+ETA)
        for j in range(6):
            glo,ghi = Fd[k].grad[j].iv()       # enclosure of dF_k/dx_j over the box
            rj = rad[j]
            # interval product [glo,ghi]*[-rj,rj]  -> [-max|g|*rj, max|g|*rj]
            m = max(abs(glo),abs(ghi))*rj
            lo -= m; hi += m
        if not (lo <= 0 <= hi): return True
    return False

if __name__=='__main__':
    random.seed(20260629)
    radii=[0.3,0.2,0.1,0.05,0.02,0.01,0.005,0.002,0.001]
    def largest_radius(center, fn):
        for r in radii:
            box=[(center[i]-r, center[i]+r) for i in range(6)]
            # keep inside B_sphere & interior (off the acos edge) for a clean interior test
            ok=all(B[i][0] <= box[i][0] and box[i][1] <= B[i][1] for i in range(6))
            if not ok: continue
            if center[5]+center[1] > HALF-0.05 or center[5]+center[2] > HALF-0.05: return None
            v=fn(box)
            if v is True: return r
        return None
    print('EXCLUSION-RADIUS test: NATURAL vs CENTERED on off-root interior boxes')
    print('(larger radius excluded = fires on bigger boxes = shallower depth)')
    print()
    got=0; nat_wins=cen_wins=ties=0; nat_only=cen_only=0
    print('  %-38s %-10s %-10s'%('interior point (c,d,h)','natural','centered'))
    for _ in range(20000):
        if got>=15: break
        c=random.uniform(0.3,0.85); d=random.uniform(0.3,0.85); h=random.uniform(0.2,0.5)
        if h+c>HALF-0.1 or h+d>HALF-0.1: continue
        b=random.uniform(0.2,0.6); e=random.uniform(0.2,0.6); g=random.uniform(0.1,0.5)
        x0=[b,c,d,e,g,h]
        rn=largest_radius(x0, natural_excludes)
        rc=largest_radius(x0, centered_excludes)
        if rn is None and rc is None: continue
        got+=1
        print('  (%.3f,%.3f,%.3f)%s %-10s %-10s'%(c,d,h,' '*18,
              ('%.3g'%rn if rn else 'none'), ('%.3g'%rc if rc else 'none')))
        if rn and rc:
            if rc>rn: cen_wins+=1
            elif rn>rc: nat_wins+=1
            else: ties+=1
        elif rc and not rn: cen_only+=1
        elif rn and not rc: nat_only+=1
    print()
    print('  centered excludes at LARGER radius: %d | natural larger: %d | tie: %d'%(cen_wins,nat_wins,ties))
    print('  centered-only (natural never): %d | natural-only: %d'%(cen_only,nat_only))
    print()
    print('  WIN = centered fires at larger radius (cen_wins + cen_only high, nat_only ~0).')


# ---------------- preconditioned Krawczyk EXCLUSION (candidate 2+3) -----------
import numpy as np
def krawczyk_excludes(box):
    """Preconditioned exclusion: Krawczyk operator K(X); exclude if K(X) ∩ X = ∅.
    C = inv(midpoint Jacobian). Rigorous (outward-padded center term)."""
    cen=[(lo+hi)/2 for lo,hi in box]; rad=[(hi-lo)/2 for lo,hi in box]
    try:
        F0 = constraints_center(cen)
    except Exception:
        return None
    AAr._n=[0]
    try:
        Fd = cone_F(*[DualRS.var(j, cen[j], rad[j]) for j in range(6)], DUAL_FN)
    except (SplitNeeded, DomainError, ValueError, ZeroDivisionError, OverflowError):
        return None
    f0 = np.array([F0[k] for k in S6], float)
    Jm = np.array([[Fd[k].grad[j].c for j in range(6)] for k in S6], float)        # midpoint J
    if not np.all(np.isfinite(Jm)): return None
    try: C = np.linalg.inv(Jm)
    except np.linalg.LinAlgError: return None
    # interval Jacobian enclosure J(X): [glo,ghi] per entry
    Jlo=np.array([[Fd[k].grad[j].iv()[0] for j in range(6)] for k in S6])
    Jhi=np.array([[Fd[k].grad[j].iv()[1] for j in range(6)] for k in S6])
    rv=np.array(rad)
    # M = I - C*J(X), as an interval matrix. C is a point matrix; J(X) interval [Jlo,Jhi].
    # (C@Jint)_ij interval = sum_k C_ik*[Jlo_kj,Jhi_kj]; midpoint Jmid, radius via |C|*Jrad
    Jmid=(Jlo+Jhi)/2; Jrad=(Jhi-Jlo)/2
    CJ_mid = C@Jmid; CJ_rad = np.abs(C)@Jrad
    M_mid = np.eye(6)-CJ_mid; M_rad = CJ_rad                       # I - C*J(X)
    # K(X) = cen - C*f0 + (I - C*J(X)) * [-rv,rv]
    Cf0 = C@f0
    term_rad = np.abs(M_mid)@rv + M_rad@rv                        # radius of M*[-rv,rv]
    K_mid = np.array(cen) - Cf0
    K_lo = K_mid - term_rad; K_hi = K_mid + term_rad
    Xlo=np.array(cen)-rv; Xhi=np.array(cen)+rv
    # exclude if K and X are disjoint in any coordinate
    for i in range(6):
        if K_hi[i] < Xlo[i] or K_lo[i] > Xhi[i]:
            return True
    return False
