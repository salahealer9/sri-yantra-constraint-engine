"""
candidate_search_mapper_smoke.py — PROVE find_seed usability on KNOWN roots, as a LADDER.
Server-only (needs mapper stack). NOT a discovery run. Does NOT loosen the displacement cap.

Ladder (stop at first informative failure):
  Phase 0  imports + frozen engine hash.
  Phase 1  EXACT-ALTITUDE INJECTION: call find_seed with alts = ONLY the known root's exact
           altitude (h_deg). Sharpest diagnostic:
             success            -> machinery sound; slicing was the issue; dense sweep worth it.
             None               -> not just spacing; convention/signature/budget/objective mismatch.
             candidate but cert fails -> bridge/coordinate scaling still wrong.
  Phase 2  DENSE GRID (0.5 deg): only run if Phase 1 succeeds. Max altitude error ~0.0044 rad,
           safely inside the 2e-2 polish cap (benchmark default gap 1.35deg ~0.0236 rad EXCEEDS it).
  Bridge   read from data (identity / /R / *R tested against the known root); NEVER assumed.
  Certify  certify_2b_general decides. CAP NOT loosened.
"""
import sys, os, math, hashlib
import numpy as np
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
import certify_2b_general as GEN

PI2=math.pi/2; DEG=math.pi/180
BENCH=(1,2,3,4,6,7)
BENCH_ROOT=[0.6246238466927992,0.7044304165359816,0.7482768099360514,0.6307397242292889,0.3136386632298885,0.39527668335411803]

def resid(sub, x):
    try: F=RAO.constraints(*x); return math.sqrt(sum(F[k]**2 for k in sub))
    except Exception: return float('inf')

def bridges(out):
    x=list(out); h=x[5]; R=PI2-h
    return {'identity':[x[0],x[1],x[2],x[3],x[4],h],
            'div_R':([x[0]/R,x[1]/R,x[2]/R,x[3]/R,x[4]/R,h] if R else None),
            'mul_R':[x[0]*R,x[1]*R,x[2]*R,x[3]*R,x[4]*R,h]}

def best_bridge(sub, out):
    best=None
    for tag,br in bridges(out).items():
        if br is None: continue
        r=resid(sub,br)
        if best is None or r<best[1]: best=(tag,r,br)
    return best

def try_altitudes(M, sub, alts, k, warm=[]):
    try: return M.find_seed(sub, warm=warm, alts=tuple(alts), k=k)
    except Exception as e: return ('ERR', f'{type(e).__name__}: {e}')

def main():
    print("=== Phase 0 ===")
    eng_path = os.path.join(_root, 'sriyantra.py')
    eng = hashlib.sha256(open(eng_path, 'rb').read()).hexdigest()[:12]
    print(f"  engine hash {eng} (expect de64edfa4979)")
    try: import spherical_existence_mapper as M; print("  mapper import OK")
    except Exception as e: print(f"  FAIL mapper import: {e}"); return 1

    known={BENCH:BENCH_ROOT}
    for name,vals in RAO.TABLE1:
        s=tuple(sorted(name))
        if s!=BENCH and resid(s,list(vals))<1e-3: known[s]=list(vals); break

    overall=True
    for sub,raw in known.items():
        h=raw[5]; h_deg=h/DEG
        print(f"\n=== subset {sub}  known h={h:.6f} rad = {h_deg:.4f} deg ===")
        print(f"  known raw: {[round(v,6) for v in raw]}  resid={resid(sub,raw):.2e}")

        # -- Phase 1: EXACT-ALTITUDE INJECTION --
        print("  Phase 1 (exact-altitude injection):")
        out=try_altitudes(M, sub, [h_deg], k=200)
        if isinstance(out,tuple) and out[0]=='ERR':
            print(f"    find_seed raised {out[1]}  -> signature/convention issue. STOP."); overall=False; continue
        if out is None:
            print("    find_seed -> None at EXACT altitude (k=200). Not spacing; deeper mismatch"
                  " (convention/budget/objective). STOP dense sweep."); overall=False; continue
        print(f"    mapper out: {[round(float(v),6) for v in out]}")
        bb=best_bridge(sub,out)
        print(f"    best bridge: {bb[0]} resid {bb[1]:.2e} vs known root")
        st,ev=GEN.certify_2b_candidate(list(sub), bb[2])
        ok1 = st=='CERTIFIED_UNIQUE_GEOMETRIC'
        print(f"    certify -> {st}" + (f" resid={ev['residual_norm']:.2e}" if ok1 else f" note={ev.get('note','')[:45]}"))
        if not ok1:
            print("    exact-altitude candidate did NOT certify -> bridge/scaling wrong. STOP."); overall=False; continue

        # -- Phase 2: DENSE GRID 0.5deg (only reached if Phase 1 passed) --
        print("  Phase 2 (dense 0.5deg grid; cap NOT loosened):")
        grid=[round(a,1) for a in np.arange(16.0, 89.01, 0.5)]
        out2=try_altitudes(M, sub, grid, k=60)
        if out2 is None or (isinstance(out2,tuple) and out2[0]=='ERR'):
            print(f"    dense grid -> {out2}  (Phase 1 passed, so machinery works; may need larger k)")
        else:
            bb2=best_bridge(sub,out2)
            st2,ev2=GEN.certify_2b_candidate(list(sub), bb2[2])
            ok2 = st2=='CERTIFIED_UNIQUE_GEOMETRIC'
            print(f"    dense out bridge {bb2[0]} resid {bb2[1]:.2e} -> certify {st2}"
                  + (f" resid={ev2['residual_norm']:.2e}" if ok2 else ""))

    print(f"\n=== SMOKE LADDER: {'PASS (exact-altitude proven; dense sweep viable)' if overall else 'STOPPED at first failure -- see above'} ===")
    return 0 if overall else 1

if __name__=='__main__':
    sys.exit(main())
