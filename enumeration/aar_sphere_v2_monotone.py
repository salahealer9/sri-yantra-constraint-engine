"""
aar_sphere_v2_monotone.py — EXPLORATORY thin EXTENSION of aar_sphere.py adding a
MONOTONE across-inflection fallback for atan and acos ONLY. Imports everything
else from aar_sphere unchanged (same AAr, DualRS, exceptions, sin/cos/tan, affine
atan/acos, _uni_mono lemma) so there are NO class-identity pitfalls when wiring.

WHAT IT ADDS (atan, acos only):
  aa_atan_mono / aa_acos_mono  — value forms; tight affine where the box does not
      straddle the inflection at 0, monotone endpoint range across it.
  d_atan_mono  / d_acos_mono   — dual forms; value as above + a rigorous INTERVAL
      enclosure of the derivative factor over the box.

SOUNDNESS (validated separately by harness_mono_value / harness_mono_dual):
  value:      atan/acos are MONOTONE, so the value range over [a,b] is just the
              endpoint pair, rigorous by outward rounding, VALID across the
              inflection at 0.
  derivative: atan f'=1/(1+u^2) in (0,1], finite everywhere -> over a 0-straddling
              box f' in [1/(1+umax^2), 1]. acos f'=-1/sqrt(1-u^2): finite IFF
              umax<1; over a 0-straddling box f' in [-M,-1], M=1/sqrt(1-umax^2).
              The denominator 1-umax^2 is certified > 0 (else SplitNeeded). NO
              hand-tuned cap: a large-but-finite bound is returned for Krawczyk.

WHAT IS PRESERVED: acos DOMAIN-edge handling is untouched — DomainError entirely
outside [-1,1], SplitNeeded straddling +-1 or when 1-umax^2 is not certifiably > 0.
Only INFLECTION-at-0 SplitNeeded is removed (for the _mono forms). The original
aar_sphere.py is UNCHANGED.
"""
import math
from aar import AAr, U, ETA, SAFE
# Reuse ALL canonical objects from aar_sphere (same classes -> no identity pitfalls)
from aar_sphere import (SplitNeeded, DomainError, AAr as _AAr,
                        aa_sin, aa_cos, aa_tan, aa_atan, aa_acos,
                        DualRS, NV, d_sin, d_cos, d_tan, d_atan, d_acos)


# ---------------- value forms (monotone across-inflection fallback) ----------
def _mono_range_AAr(lo, hi):
    """Rigorous degenerate AAr enclosing a real interval [lo,hi] (lo<=hi), with
    outward padding. Used for the monotone value range across the inflection."""
    c = 0.5 * (lo + hi)
    rad = 0.5 * (hi - lo)
    pad = U * (abs(lo) + abs(hi) + abs(c)) + ETA + SAFE
    AAr._n[0] += 1
    return AAr(c, {AAr._n[0]: rad + pad}, 0.0)

def aa_atan_mono(s):
    a, b = s.iv()
    if not (a < 0.0 < b):
        return aa_atan(s)                          # tight affine where valid
    return _mono_range_AAr(math.atan(a), math.atan(b))   # increasing

def aa_acos_mono(s):
    a, b = s.iv()
    if b < -1.0 or a > 1.0:
        raise DomainError(f"acos: box entirely outside [-1,1] ({a:.6g},{b:.6g})")
    if a < -1.0 or b > 1.0:
        raise SplitNeeded(f"acos: box straddles domain edge +-1 ({a:.6g},{b:.6g})")
    if not (a < 0.0 < b):
        return aa_acos(s)                          # tight affine where valid
    return _mono_range_AAr(math.acos(b), math.acos(a))   # decreasing


# ---------------- dual forms (value + rigorous derivative-factor interval) ----
def _interval_AAr(lo, hi):
    c = 0.5 * (lo + hi); rad = 0.5 * (hi - lo)
    pad = U * (abs(lo) + abs(hi) + abs(c)) + ETA + SAFE
    AAr._n[0] += 1
    return AAr(c, {AAr._n[0]: rad + pad}, 0.0)

def d_atan_mono(s):
    a, b = s.val.iv()
    if not (a < 0.0 < b):
        return d_atan(s)
    fval = aa_atan_mono(s.val)
    umax = max(abs(a), abs(b))
    dlo = 1.0 / (1.0 + umax * umax)
    dfac = _interval_AAr(dlo * (1.0 - U) - ETA, 1.0 + U + ETA)
    return DualRS(fval, [dfac * s.grad[j] for j in range(NV)])

def d_acos_mono(s):
    a, b = s.val.iv()
    if b < -1.0 or a > 1.0:
        raise DomainError(f"acos: box entirely outside [-1,1] ({a:.6g},{b:.6g})")
    if a < -1.0 or b > 1.0:
        raise SplitNeeded(f"acos: box straddles domain edge +-1 ({a:.6g},{b:.6g})")
    if not (a < 0.0 < b):
        return d_acos(s)
    umax = max(abs(a), abs(b))
    one_minus = 1.0 - umax * umax
    if not (one_minus > 0.0):
        raise SplitNeeded(f"acos: derivative denom 1-umax^2 not certifiable>0 (umax={umax:.6g})")
    fval = aa_acos_mono(s.val)
    M = 1.0 / math.sqrt(one_minus)
    dfac = _interval_AAr(-(M * (1.0 + U) + ETA), -1.0 + U + ETA)
    return DualRS(fval, [dfac * s.grad[j] for j in range(NV)])


# ---------------- monotone FN namespaces (for chain_sph wiring) --------------
# Same container as chain_sphere.AA_FN / DUAL_FN. sin/cos/tan are the CANONICAL
# affine forms (unchanged); ONLY atan and acos swap to the monotone fallback.
from chain_sphere import _FN, AA_FN as _AFF_AA_FN, DUAL_FN as _AFF_DUAL_FN

MONO_AA_FN   = _FN(aa_sin, aa_cos, aa_tan, aa_atan_mono, aa_acos_mono)
MONO_DUAL_FN = _FN(d_sin,  d_cos,  d_tan,  d_atan_mono,  d_acos_mono)

# audit: confirm sin/cos/tan are byte-identical to the canonical affine namespace,
# and only atan/acos differ.
def _fn_swap_audit():
    same = (MONO_AA_FN.sin is _AFF_AA_FN.sin and MONO_AA_FN.cos is _AFF_AA_FN.cos
            and MONO_AA_FN.tan is _AFF_AA_FN.tan
            and MONO_DUAL_FN.sin is _AFF_DUAL_FN.sin and MONO_DUAL_FN.cos is _AFF_DUAL_FN.cos
            and MONO_DUAL_FN.tan is _AFF_DUAL_FN.tan)
    diff = (MONO_AA_FN.atan is not _AFF_AA_FN.atan and MONO_AA_FN.acos is not _AFF_AA_FN.acos
            and MONO_DUAL_FN.atan is not _AFF_DUAL_FN.atan and MONO_DUAL_FN.acos is not _AFF_DUAL_FN.acos)
    return same and diff
