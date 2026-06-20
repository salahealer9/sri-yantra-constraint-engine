"""
Finite-alpha audit: my un-reduced prototype  vs  sriyantra.py (Rao's direct
transcription) at Rao's actual spherical Table-1 points.
Mapping: sriyantra uses arcs (b,c,d,e,g) with bounding arc r = pi/2 - h.
My prototype uses plane-lengths scaled by alpha, bounding arc = alpha*1.
=> set alpha = pi/2 - h,  my inputs = (b,c,d,e,g)/alpha.  Then arcs match exactly.
A match across all 20 constraints at FINITE alpha proves finite-alpha faithfulness.
"""
import sys, os;
_here = os.path.dirname(os.path.abspath(__file__))
_root = _here
while _root != os.path.dirname(_root):
    if os.path.exists(os.path.join(_root, "sriyantra_plane.py")):
        break
    _root = os.path.dirname(_root)
for _p in (_here, _root, os.path.join(_root, "enumeration")):
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)
import mpmath as mp
import sriyantra_plane as PLANE
mp.mp.dps = 50
import mpmath as mp
import sriyantra as RAO          # direct Rao transcription (float)
import spherical_engine as ME    # my un-reduced prototype (mpmath)
mp.mp.dps = 40
HALFPI = mp.pi/2

worst_all = mp.mpf(0)
for cons, (b,c,d,e,g,h) in RAO.TABLE1:
    al = HALFPI - mp.mpf(repr(h))                      # alpha = r = pi/2 - h
    inv = [float(mp.mpf(repr(v))/al) for v in (b,c,d,e,g)]  # my inputs = arc/alpha
    try:
        Fme  = ME.constraints_sph(*inv, al)
        Frao = RAO.constraints(b,c,d,e,g,h)
    except Exception as ex:
        print(f"{str(cons):26s}  ERROR {ex}"); continue
    diffs = {i: abs(Fme[i] - mp.mpf(repr(Frao[i]))) for i in range(1,21)}
    w = max(diffs.values()); worst_all = max(worst_all, w)
    bad = {i:mp.nstr(diffs[i],2) for i in range(1,21) if diffs[i] > mp.mpf('1e-9')}
    tag = "MATCH" if w < mp.mpf('1e-9') else "DIFF "
    print(f"[{tag}] h={float(h):.4f} alpha={mp.nstr(al,4):>7}  max|dF|={mp.nstr(w,3):>9}"
          + (f"   outliers: {bad}" if bad else ""))
print(f"\nWorst |my_F - Rao_F| over all Table-1 rows, all 20 constraints: {mp.nstr(worst_all,3)}")
print("(limited by sriyantra.py float precision ~1e-12; <1e-9 = faithful match)")
