# Validation panel on the CORRECTED box B_plane. Three objectives:
#  1 regression (Table-3 rows must recover their Rao root, complete, 0 unresolved)
#  2 admissibility stress (no false cert/exclusion; degenerate refuses; 0 unresolved)
#  3 seam discovery (does any unresolved population localize to a NEW denominator surface?)
import sys,time,json,csv,os; 
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from aar import AAr, DualR
from plane_chain import cons_full, Fvec
import domain_v3 as D
import sriyantra_plane as eng

script_dir = os.path.dirname(os.path.abspath(__file__))
B_path = os.path.join(script_dir, 'B.json')
B = json.load(open(B_path))['box']; BOX=[tuple(B[k]) for k in ['b','c','d','e','g']]
TAB={tuple(c):v for c,v in eng.TABLE3}

def excluded_S(box,S):
    AAr._n=[0]
    try: F=cons_full(*[AAr.var((lo+hi)/2,(hi-lo)/2) for (lo,hi) in box])
    except (ValueError,ZeroDivisionError): return False
    for k in S:
        lo,hi=F[k].iv()
        if not (lo<=0<=hi): return True
    return False
def hw(x): lo,hi=x.iv(); return (hi-lo)/2
def krawczyk_S(center,r,S):
    AAr._n=[0]
    try: Fd=cons_full(*[DualR.var(k,center[k],r) for k in range(5)])
    except (ValueError,ZeroDivisionError): return 'split'
    Jm=np.array([[Fd[S[i]].grad[j].c for j in range(5)] for i in range(5)])
    if not np.all(np.isfinite(Jm)): return 'split'
    Jr=np.array([[hw(Fd[S[i]].grad[j]) for j in range(5)] for i in range(5)])
    try: Y=np.linalg.inv(Jm)
    except np.linalg.LinAlgError: return 'split'
    Fm=Fvec(center,S); M=np.eye(5)-Y@Jm; Mr=np.abs(Y)@Jr
    Kc=-(Y@Fm); Kh=(np.abs(M)+Mr)@np.full(5,r)
    lo=np.array(center)+Kc-Kh; hi=np.array(center)+Kc+Kh
    Xl=np.array(center)-r; Xh=np.array(center)+r
    if np.all(hi<Xh) and np.all(lo>Xl): return 'unique'
    if np.any(hi<Xl) or np.any(lo>Xh): return 'empty'
    return 'split'

def enum(S,tlim=120,max_depth=200,r_cert=3e-3,max_boxes=3000000):
    t0=time.time(); stack=[(list(BOX),0)]; proc=0; cert=[]; dom=0; unres=[]; maxd=0; maxq=1
    while stack and proc<max_boxes and time.time()-t0<tlim:
        maxq=max(maxq,len(stack)); box,dep=stack.pop(); proc+=1; maxd=max(maxd,dep)
        if D.domain_excluded(box): dom+=1; continue
        if excluded_S(box,S): continue
        center=[(lo+hi)/2 for (lo,hi) in box]; rad=max((hi-lo)/2 for (lo,hi) in box)
        if rad<=r_cert:
            v=krawczyk_S(center,rad,S)
            if v=='unique':
                if not any(max(abs(center[i]-q[i]) for i in range(5))<2*r_cert for q in cert): cert.append(center)
                continue
            if v=='empty': continue
        if dep>=max_depth: unres.append(center); continue
        w=[hi-lo for (lo,hi) in box]; k=int(np.argmax(w)); lo,hi=box[k]; mid=(lo+hi)/2
        L=list(box); L[k]=(lo,mid); R=list(box); R[k]=(mid,hi); stack+=[(L,dep+1),(R,dep+1)]
    return dict(boxes=proc,cert=cert,dom=dom,unres=unres,maxd=maxd,maxq=maxq,
               secs=round(time.time()-t0,1),complete=(len(stack)==0))

def classify(unres):
    if not unres: return {}
    cnt={}
    for ctr in unres:
        b,c,d,e,g=ctr
        try:
            s=eng.chain(b,c,d,e,g)
            v8,v9,v12,x10,x13,x18,x19=s['v8'],s['v9'],s['v12'],s['x10'],s['x13'],s['x18'],s['x19']
            Q20=(c+d+v9-v12)/(d+g+v8)*(x10/x13); Q21=(b+c+d+v8)/(c+d+e+v9)*(x19/x18)
            cand={'x11a:v9+c+d-v12':abs(v9+c+d-v12),'U20:Q20+1':abs(Q20+1),'U21:Q21+1':abs(Q21+1)}
            who=min(cand,key=cand.get); near=cand[who]
            key=who if near<5e-3 else 'other(not-a-known-seam)'
        except Exception: key='chain_error'
        cnt[key]=cnt.get(key,0)+1
    return cnt

PANEL={
 1:[(1,2,3,4,8),(1,2,4,5,10),(1,2,3,10,15)],
 2:[(1,2,11,12,17),(1,2,6,10,19),(1,2,3,4,6),(1,2,8,9,16)],
 3:[(1,2,3,4,13),(1,2,6,14,19),(1,2,3,4,14),(1,2,13,14,15)],
}
obj=int(sys.argv[1]) if len(sys.argv)>1 else 1
print(f"=== Panel Objective {obj} on B_plane ===")
rows=[]
for S in PANEL[obj]:
    r=enum(list(S))
    raoroot=TAB.get(S)
    rec=""
    for ctr in r['cert']:
        if raoroot and max(abs(ctr[i]-raoroot[i]) for i in range(5))<0.01: rec=" Rao-recovered"
    seam=classify(r['unres'])
    print(f"  {S}: complete={r['complete']} boxes={r['boxes']} dom_excl={r['dom']} "
          f"cert={len(r['cert'])}{rec} unresolved={len(r['unres'])} "
          f"max_depth={r['maxd']} peak_q={r['maxq']} secs={r['secs']}")
    if seam: print(f"      unresolved localization: {seam}")
    rows.append([obj,S,r['complete'],r['boxes'],r['dom'],len(r['cert']),rec.strip(),
                 len(r['unres']),r['maxd'],r['maxq'],r['secs'],seam])
# append to CSV
os.makedirs('panel_B', exist_ok=True)
new=not os.path.exists('panel_B/results.csv')
with open('panel_B/results.csv','a',newline='') as f:
    w=csv.writer(f)
    if new: w.writerow(['objective','subset','complete','boxes','dom_excl','cert','recovered','unresolved','max_depth','peak_q','secs','seam_localization'])
    for row in rows: w.writerow(row)
