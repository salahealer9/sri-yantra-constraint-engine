"""
probe_path2_native.py — MICRO-PROBE for Path 2 (NOT an engine). Tests whether native
(u,v) coordinates (u=h+c, v=h+d as split axes) straighten the acos domain wall WITHOUT
the c=u-h value-smearing reintroducing a new looseness wall. Reuses the frozen old-coord
chain via an interval inverse map. Short dive only.
"""
import sys, os, math, time
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
import domain_sphere_v2_prefilter as v2
from prefilter_v2 import prefilter_excludes
HALF = v2.HALF_PI
B = v2.B_SPHERE
(BL,BH),(CL,CH),(DL,DH),(EL,EH),(GL,GH),(HL,HH) = B
classify = v2.classify

# native (u,v) hull: u=h+c, v=h+d ranges; b,e,g,h unchanged
B_UV = [(BL,BH),(HL+CL,HH+CH),(HL+DL,HH+DH),(EL,EH),(GL,GH),(HL,HH)]

def map_uv_to_old(box_uv):
    """(b,u,v,e,g,h) intervals -> old (b,c,d,e,g,h) with c=u-h, d=v-h (smeared),
    intersected with the registered physical c,d range. Returns None if non-physical."""
    (b,u,v,e,g,h) = box_uv
    c = (u[0]-h[1], u[1]-h[0])           # interval c = u - h  (dependency-smeared)
    d = (v[0]-h[1], v[1]-h[0])
    c = (max(c[0],CL), min(c[1],CH))     # intersect physical range
    d = (max(d[0],DL), min(d[1],DH))
    if c[0] >= c[1] or d[0] >= d[1]:
        return None                       # non-physical (c or d empty)
    return [b,c,d,e,g,h]

def classify_uv(box_uv):
    (b,u,v,e,g,h) = box_uv
    # NATIVE domain edge (exact, axis-aligned — the straightening):
    if u[0] > HALF or v[0] > HALF:
        return 'domain'                   # entirely past u=pi/2 / v=pi/2 -> invalid
    old = map_uv_to_old(box_uv)
    if old is None:
        return 'nonphysical'
    # constraint exclusion/certification via the frozen old chain (c,d smeared):
    if prefilter_excludes(old):
        return 'domain'
    return classify(old)

def split_uv(box_uv):
    """Prefer splitting u or v at pi/2 when straddling (the native straightening);
    else widest axis."""
    (b,u,v,e,g,h) = box_uv
    if u[0] < HALF < u[1]: return 1, HALF      # split u at pi/2
    if v[0] < HALF < v[1]: return 2, HALF      # split v at pi/2
    w=[hi-lo for lo,hi in box_uv]; k=int(np.argmax(w))
    lo,hi=box_uv[k]; return k,(lo+hi)/2

def dive_uv(max_boxes=120000, max_depth=200):
    stack=[(list(B_UV),0)]; proc=0
    dom=nonphys=excl=cert=unres=0; maxd=0; unresolved_boxes=[]
    while stack and proc<max_boxes:
        box,dep=stack.pop(); proc+=1; maxd=max(maxd,dep)
        cls=classify_uv(box)
        if cls=='domain': dom+=1; continue
        if cls=='nonphysical': nonphys+=1; continue
        if cls=='excluded': excl+=1; continue
        if cls=='certified': cert+=1; continue
        if dep>=max_depth: unres+=1; unresolved_boxes.append(box); continue
        k,mid=split_uv(box)
        lo,hi=box[k]
        L=list(box); L[k]=(lo,mid); R=list(box); R[k]=(mid,hi)
        stack.append((L,dep+1)); stack.append((R,dep+1))
    return dict(proc=proc,dom=dom,nonphys=nonphys,excl=excl,cert=cert,unres=unres,
               maxd=maxd,qleft=len(stack),unresolved=unresolved_boxes)

if __name__=='__main__':
    print('Path 2 MICRO-PROBE (native u,v short dive) vs old-coord v2 baseline')
    print('B_UV hull: u=[%.3f,%.3f] v=[%.3f,%.3f]' % (B_UV[1][0],B_UV[1][1],B_UV[2][0],B_UV[2][1]))
    print()
    t=time.time(); r=dive_uv(max_boxes=120000); el=time.time()-t
    unfin=r['unres']+r['qleft']
    print('native (u,v) dive: proc=%d dom=%d nonphys=%d excl=%d cert=%d unres=%d qleft=%d UNFIN=%d maxd=%d (%.1fs)'
          % (r['proc'],r['dom'],r['nonphys'],r['excl'],r['cert'],r['unres'],r['qleft'],unfin,r['maxd'],el))
    t=time.time(); rb=v2.enum(max_boxes=120000, tlim=200, max_depth=200, r_cert=3e-3); el2=time.time()-t
    ubf=rb['unres']+rb['queue_left']
    print('old-coord v2 dive: proc=%d dom=%d excl=%d cert=%d unres=%d qleft=%d UNFIN=%d maxd=%d (%.1fs)'
          % (rb['boxes'],rb['dom'],rb['excl'],len(rb['cert']),rb['unres'],rb['queue_left'],ubf,rb['maxd'],el2))
    print()
    print('  UNFINISHED: old %d  ->  native(u,v) %d   (%+.1f%%)' % (ubf,unfin,100*(unfin-ubf)/max(ubf,1)))
    # diagnose the native unresolved boxes: still on a (smeared) seam, or new looseness?
    ur=r['unresolved']
    if ur:
        straddle_uv=sum(1 for (b,u,v,e,g,h) in ur if (u[0]<HALF<u[1]) or (v[0]<HALF<v[1]))
        print('  native unresolved boxes: %d ; still straddling u/v=pi/2: %d (%.1f%%)'
              % (len(ur),straddle_uv,100*straddle_uv/len(ur)))
        print('  (low %% straddling => the acos edge is straightened; remaining cost is the')
        print('   c=u-h value-smearing / other seams, the real Path-2 trade.)')
