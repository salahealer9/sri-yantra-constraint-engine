"""
aar_sphere.py — rigorous outward-rounded AA transcendentals for the spherical
Sri Yantra chain.  INHERITS the frozen plane substrate aar.py; does NOT modify it.

The plane substrate's _uni remainder (aar.py) is rigorous ONLY when f'' has a
single sign on the box [a,b]: then g = f - L (affine error) is convex/concave and
sup|g| is attained at {a, b, x*} (x* the interior chord-critical point, f'(x*)=p).
sqrt/recip satisfy this automatically. The transcendentals sin/cos/tan/atan/acos
do NOT: each has an inflection (f''=0) and/or a domain edge inside its range.

Rigorous handling (this file):
  * If the AA quantity's interval [a,b] is free of f-inflections AND inside the
    valid domain, the min-range affine form _uni_mono is applied (rigorous +
    tight, same construction as aar._uni, with x* by bisection on f'(x)=p).
  * If [a,b] straddles an inflection of f, or straddles a domain edge, we raise
    SplitNeeded: the *input* box must be subdivided (the branch-and-prune driver
    catches it), shrinking downstream intervals until they are inflection-free.
    This is the transcendental analogue of the safe_acos / pole domain guards:
    a composite condition handled by split/exclude, never a silently-wrong bound.
  * If [a,b] is provably entirely outside the domain (e.g. acos arg outside
    [-1,1]), we raise DomainError (the box is excluded).

Rigor of the SAFE margin: x* is found by bisection to ~2^-80 of the box width;
the resulting 2nd-order deficit in gb(x*) is ~|f''|(Δx*)^2 ~ 1e-48, covered by
SAFE=1e-18 with >25 orders of margin — the same argument aar.py makes for
sqrt/recip. delta_r therefore rigorously bounds sup|g|.

================================================================================
ANALYTIC REMAINDER DERIVATION  (the PROOF; the harness only VALIDATES on samples)
================================================================================
Random-box containment tests are validation, not proof. The proof that each form
is a rigorous enclosure is the analytic remainder argument below. The core lemma
is shared; each function differs only in (i) its domain precondition, (ii) the
location of its f''=0 inflection(s)/poles that must be split out, and (iii) the
sign of f'' on a clean sub-box.

SHARED LEMMA (min-range affine bound on a single-sign-f'' interval).
  Let f be C^2 on [a,b] with f'' of one sign (≠0) on (a,b). Let L(x)=p x+q be any
  affine function and g=f-L. Then g''=f'' keeps one sign, so g is strictly convex
  (f''>0) or concave (f''<0) on [a,b]; hence g' is strictly monotone and g has at
  most one interior stationary point x* with g'(x*)=0, i.e. f'(x*)=p. A convex (or
  concave) function on a compact interval attains its extrema only at the endpoints
  or its single interior stationary point, so
        sup_{[a,b]} |g| = max( |g(a)|, |g(b)|, |g(x*)| ).
  We take p = (f(b)-f(a))/(b-a) (the secant slope) and
        q = (f(a)+f(x*))/2 - p(a+x*)/2
  (the midpoint between the secant and the parallel tangent at x*), which centres
  the error and minimises sup|g|. delta_r := max(|g(a)|,|g(b)|,|g(x*)|) + rounding
  + SAFE then satisfies delta_r >= sup|g|, so [center ± (affine radii ⊕ delta_r)]
  rigorously encloses f over [a,b]. Outward rounding: every float op in gb() is
  inflated by U·(|operands|) + ETA (see gb), and SAFE=1e-18 covers the bisection
  x*-deficit (~1e-48). The PRECONDITION (single-sign f'') is enforced BEFORE
  calling _uni_mono by the per-function inflection/domain guards; if it cannot be
  guaranteed, SplitNeeded/DomainError is raised instead. This is what makes the
  bound certifying rather than merely accurate.

PER-FUNCTION (domain precondition; inflections split; f'' sign on clean box):
  sin :  domain ℝ. f''=-sin, zeros at kπ. Guard: no kπ strictly inside (a,b)
         (SplitNeeded). On a clean box f'' has one sign (box lies within one
         (kπ,(k+1)π) lane). f'=cos used for x*.
  cos :  domain ℝ. f''=-cos, zeros at π/2+kπ. Guard: no π/2+kπ inside (a,b).
         f'=-sin used for x*.
  tan :  domain ℝ minus {π/2+kπ}. TWO guards: (1) no pole π/2+kπ in [a,b] (else the
         function is unbounded — SplitNeeded; a pole is a point and may only be
         pushed to a boundary, so pathological boxes subdivide to max_depth =
         unresolved, by design); (2) f''=2sec²·tan, zeros at kπ — no kπ inside
         (a,b). On a clean box (one (kπ-π/2, kπ+π/2) ∩ lane), f'' is one sign.
         f'=sec²=1+tan² used for x*.
  atan:  domain ℝ. f''=-2x/(1+x²)², single zero at 0. Guard: box not straddling 0
         (a<0<b ⇒ SplitNeeded); then f''<0 for x>0, f''>0 for x<0 — one sign.
         f'=1/(1+x²) used for x*.
  acos:  domain [-1,1]. f''=-x/(1-x²)^{3/2}, single interior zero at 0, and the
         derivative blows up at ±1. Guards: box entirely outside [-1,1] ⇒
         DomainError (exclude); box straddling ±1 ⇒ SplitNeeded; box straddling 0
         ⇒ SplitNeeded. On a clean box (in (-1,0) or (0,1)), f'' is one sign and
         f'=-1/√(1-x²) is finite. NOTE: as the box approaches ±1 the secant slope
         p and the remainder grow (f'→∞); such boxes subdivide heavily — the
         expected acos-seam subdivision named in the pilot pre-registration.
================================================================================
"""
import math
from math import pi, sin, cos, tan, atan, acos
import aar
from aar import AAr, U, ETA, SAFE


class SplitNeeded(Exception):
    """The AA quantity's interval straddles a transcendental inflection or a
    domain edge. The input box must be subdivided. Caught by the prune driver."""
    pass


class DomainError(Exception):
    """The AA quantity's interval is provably entirely outside the function
    domain. The box is excluded."""
    pass


def _uni_mono(s, f, fp):
    """Rigorous min-range affine form of f on s.iv()=[a,b].
    PRECONDITION (caller-guaranteed): f'' has a single sign on [a,b], so g=f-L is
    convex/concave and sup|g| is at {a,b,x*}. Returns a new AAr."""
    a, b = s.iv()
    if a == b:
        return AAr(f(a))
    p = (f(b) - f(a)) / (b - a)
    # x* in [a,b] with f'(x*) = p. f' is monotone on a single-sign-f'' box, so
    # f'(x)-p changes sign at most once -> bisection. If it doesn't change sign,
    # the chord-critical point is at an endpoint; gb({a,b}) then dominates.
    glo, ghi = fp(a) - p, fp(b) - p
    if glo == 0.0:
        xs = a
    elif ghi == 0.0:
        xs = b
    elif glo * ghi > 0.0:
        xs = a                      # no interior critical pt; endpoints dominate
    else:
        lo, hi = a, b
        for _ in range(80):
            mid = 0.5 * (lo + hi)
            fm = fp(mid) - p
            if fm == 0.0:
                lo = hi = mid
                break
            if (fm > 0.0) == (glo > 0.0):
                lo, glo = mid, fm
            else:
                hi, ghi = mid, fm
        xs = 0.5 * (lo + hi)
    q = (f(a) + f(xs)) / 2.0 - p * (a + xs) / 2.0

    def gb(t):
        fv = f(t); lin = p * t + q; gv = fv - lin
        return abs(gv) + U * (abs(fv) + abs(p * t) + abs(lin) + abs(gv)) + ETA

    delta_r = max(gb(a), gb(b), gb(xs)) + SAFE
    d = {k: v * p for k, v in s.dev.items()}
    c = p * s.c + q
    AAr._n[0] += 1
    d[AAr._n[0]] = delta_r
    return AAr(c, d, abs(p) * s.err + s._round_err(c, d))


def _has_multiple_inside(a, b, period, phase):
    """True if any point (phase + k*period), k integer, lies strictly in (a,b)."""
    # smallest k with phase + k*period > a
    k = math.ceil((a - phase) / period)
    x = phase + k * period
    return a < x < b


# ---------------------------------------------------------------- transcendentals
def aa_sin(s):
    a, b = s.iv()
    # f''=-sin, inflections at k*pi
    if _has_multiple_inside(a, b, pi, 0.0):
        raise SplitNeeded(f"sin: box straddles inflection k*pi in ({a:.6g},{b:.6g})")
    return _uni_mono(s, math.sin, math.cos)


def aa_cos(s):
    a, b = s.iv()
    # f''=-cos, inflections at pi/2 + k*pi
    if _has_multiple_inside(a, b, pi, pi / 2.0):
        raise SplitNeeded(f"cos: box straddles inflection pi/2+k*pi in ({a:.6g},{b:.6g})")
    return _uni_mono(s, math.cos, lambda x: -math.sin(x))


def aa_tan(s):
    a, b = s.iv()
    # poles at pi/2 + k*pi
    if _has_multiple_inside(a, b, pi, pi / 2.0):
        raise SplitNeeded(f"tan: box contains/straddles pole pi/2+k*pi in ({a:.6g},{b:.6g})")
    # f''=2 sec^2 tan, inflections at k*pi
    if _has_multiple_inside(a, b, pi, 0.0):
        raise SplitNeeded(f"tan: box straddles inflection k*pi in ({a:.6g},{b:.6g})")
    return _uni_mono(s, math.tan, lambda x: 1.0 / math.cos(x) ** 2)


def aa_atan(s):
    a, b = s.iv()
    # f''=-2x/(1+x^2)^2, single inflection at 0
    if a < 0.0 < b:
        raise SplitNeeded(f"atan: box straddles inflection 0 in ({a:.6g},{b:.6g})")
    return _uni_mono(s, math.atan, lambda x: 1.0 / (1.0 + x * x))


def aa_acos(s):
    a, b = s.iv()
    # domain [-1,1]
    if b < -1.0 or a > 1.0:
        raise DomainError(f"acos: box entirely outside [-1,1] ({a:.6g},{b:.6g})")
    if a < -1.0 or b > 1.0:
        raise SplitNeeded(f"acos: box straddles domain edge +-1 ({a:.6g},{b:.6g})")
    # f''=-x/(1-x^2)^1.5, single inflection at 0
    if a < 0.0 < b:
        raise SplitNeeded(f"acos: box straddles inflection 0 in ({a:.6g},{b:.6g})")
    return _uni_mono(s, math.acos, lambda x: -1.0 / math.sqrt(1.0 - x * x))


SCALARS = {"sin": aa_sin, "cos": aa_cos, "tan": aa_tan, "atan": aa_atan, "acos": aa_acos}


# ====================================================================
# DualRS — 6-variable forward-mode AD over rigorous AA.
# Carries val:AAr and grad:[AAr]*6  (partials wrt b,c,d,e,g,h).
# Arithmetic mirrors aar.DualR (5-var) but with 6 partials and the
# transcendental chain rules:
#     d sin(u) =  cos(u) du      d cos(u) = -sin(u) du
#     d tan(u) =  (1+tan(u)^2) du
#     d atan(u)=  du/(1+u^2)      d acos(u)= -du/sqrt(1-u^2)
# Each derivative factor is itself an AAr (rigorous), so grad entries are
# rigorous AA enclosures of the partials over the box — exactly what the
# AA-Krawczyk Jacobian enclosure needs.
# ====================================================================
NV = 6   # b,c,d,e,g,h

class DualRS:
    __slots__ = ("val", "grad")
    def __init__(s, val, grad): s.val = val; s.grad = grad      # val:AAr, grad:list[AAr] len NV
    @staticmethod
    def const(x):
        return DualRS(x if isinstance(x, AAr) else AAr(x), [AAr(0.0) for _ in range(NV)])
    @staticmethod
    def var(k, c, r):
        g = [AAr(0.0) for _ in range(NV)]; g[k] = AAr(1.0)
        return DualRS(AAr.var(c, r), g)
    def __add__(s, o):
        o = o if isinstance(o, DualRS) else DualRS.const(o)
        return DualRS(s.val + o.val, [s.grad[j] + o.grad[j] for j in range(NV)])
    __radd__ = __add__
    def __sub__(s, o):
        o = o if isinstance(o, DualRS) else DualRS.const(o)
        return DualRS(s.val - o.val, [s.grad[j] - o.grad[j] for j in range(NV)])
    def __rsub__(s, o): return DualRS.const(o).__sub__(s)
    def __neg__(s): return DualRS(-s.val, [-s.grad[j] for j in range(NV)])
    def __mul__(s, o):
        o = o if isinstance(o, DualRS) else DualRS.const(o)
        return DualRS(s.val * o.val,
                      [s.grad[j] * o.val + s.val * o.grad[j] for j in range(NV)])
    __rmul__ = __mul__
    def __truediv__(s, o):
        o = o if isinstance(o, DualRS) else DualRS.const(o)
        q = s.val / o.val
        return DualRS(q, [(s.grad[j] - q * o.grad[j]) / o.val for j in range(NV)])
    def __rtruediv__(s, o): return DualRS.const(o).__truediv__(s)


def _dual_uni(s, scalar_fn, deriv_val_fn):
    """Apply a scalar AA transcendental `scalar_fn` to s.val and propagate the
    chain rule with derivative-factor AA `deriv_val_fn(s.val)`.
    scalar_fn / deriv_val_fn take and return AAr; SplitNeeded/DomainError from
    the underlying scalar form propagate unchanged (box must be split/excluded)."""
    fval = scalar_fn(s.val)             # AAr; may raise SplitNeeded/DomainError
    dfac = deriv_val_fn(s.val)          # AAr derivative factor over the box
    return DualRS(fval, [dfac * s.grad[j] for j in range(NV)])

def d_sin(s):  return _dual_uni(s, aa_sin,  lambda u: aa_cos(u))
def d_cos(s):  return _dual_uni(s, aa_cos,  lambda u: -aa_sin(u))
def d_tan(s):  return _dual_uni(s, aa_tan,  lambda u: AAr(1.0) + aa_tan(u) * aa_tan(u))
def d_atan(s): return _dual_uni(s, aa_atan, lambda u: AAr(1.0) / (AAr(1.0) + u * u))
def d_acos(s): return _dual_uni(s, aa_acos, lambda u: -(AAr(1.0) / (AAr(1.0) - u * u).sqrt()))

DUALS = {"sin": d_sin, "cos": d_cos, "tan": d_tan, "atan": d_atan, "acos": d_acos}
