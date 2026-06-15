"""
Route-3 VALIDATION PANEL. Before scaling or amending: does the AA-exclusion +
AA-Krawczyk pipeline behave sensibly across representative subset CLASSES, not
just {1,2,3,4,8}? Full engine chain ported to affine arithmetic once (all of
F1..F20; F2 via the validated w-form), so any 5-subset is selectable.

Panel:
  {1,2,3,4,8}   Rao A  (reproduce, reference 0.463752,0.223255,0.288990,0.488181,0.106157)
  {1,2,4,5,10}  Rao B  (reproduce, reference 0.438237,0.218371,0.269490,0.440182,0.096716)
  {1,2,8,9,16}  degenerate (rank-deficient: F8-F9+F16==0)  -> must NOT falsely certify
  {1,2,11,12,17} coordinate-grounded-heavy (stress F11,F12,F17)
  {1,2,6,10,19} random well-posed (generality)
  {1,2,3,4,6}   algebraically dense (three -(.)^2/2+1.5(.)^2 constraints)
"""
import os, sys, math, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, '.')
import sriyantra_plane as SP
import numpy as np
from route3_enum import AA, Dual          # guarded import (classes only)

# ---------- full plane chain + all constraints, generic in AA/Dual ----------
def cons_full(b,c,d,e,g):
    o=1.0; H=1.5
    x1=(o-c*c).sqrt(); x2=(o-d*d).sqrt()
    x3=(o-c)/(o+d)*x2;  x4=(o-d)/(o+c)*x1
    x5=b/(b+c+d)*x4;    x6=e/(c+d+e)*x3
    Q7=(d+g)/(c+d)*(x5/x6); U7=(d+g)/(Q7+o); V7=(d+g)-U7
    x7=U7/(c+d)*x5; w=(x7*x7+V7*V7).sqrt(); rT=x7*(w-x7)/V7
    Q8=(d+g)/(o+c)*(x1/x6); U8=(o+g)/(Q8+o); V8=(o+g)-U8
    x8=U8/(o+c)*x1; v8=o-U8-d
    x16=(d+e+g)/(d+g)*x6; x11=(d+g)/(c+d)*x5; x17=(b+c+d)/(c+d)*x5
    Q9=(c+d)/(o+d)*(x2/x5); U9=(o+d)/(Q9+o); V9=(o+d)-U9
    x9=U9/(o+d)*x2; v9=o-U9-c
    x10=(b+c-g)/(b+c+d)*x4; x18=(b+c+d+v8)/(b+c+d)*x4
    S12=d+g+v8; Q12=S12/(d+g)*(x6/x10); U12=S12/(Q12+o)
    x12=U12/(d+g)*x6; v12=d+g-U12
    x14=(U7+v8)/(d+g+v8)*x10
    x13=(e+v12)/(c+d+e)*x3; x19=(c+d+e+v9)/(c+d+e)*x3
    x11a=(v9+c-g)/(v9+c+d-v12)*x13
    r16=((d+e)*(d+e)+x16*x16).sqrt(); r17=((b+c)*(b+c)+x17*x17).sqrt()
    r18=((d+v8)*(d+v8)+x18*x18).sqrt(); r19=((c+v9)*(c+v9)+x19*x19).sqrt()
    Q20=(c+d+v9-v12)/(d+g+v8)*(x10/x13); U20=(c+d+v8+v9)/(Q20+o)
    Q21=(b+c+d+v8)/(c+d+e+v9)*(x19/x18); U21=(b+c+d+e)/(Q21+o)
    F={}
    F[1]=x11-x11a; F[2]=d-U7-rT
    F[3]=H*x10*x10-0.5*V8*V8
    F[4]=H*x13*x13-0.5*(c+d+v9-v12)*(c+d+v9-v12)
    F[5]=x10-x13
    F[6]=H*x7*x7-0.5*V7*V7
    F[7]=x18-x19; F[8]=o-r16; F[9]=o-r17
    F[10]=b+c-d-2.0*g-v8
    F[11]=c+d+v9-2.0*v12-e
    F[12]=x16-x17
    F[13]=U7-(U20-v8+v12)/2.0
    F[14]=v12-(U21-e)/2.0
    F[15]=g+(d+e-c-U21)/2.0
    F[16]=r16-r17; F[17]=r18-r19; F[18]=r16-r18; F[19]=r17-r19
    F[20]=c-d
    return F

def Fvec(p, S): F=SP.constraints(*p); return np.array([F[k] for k in S])

# ---------- validation: AA cons_full must bracket the engine on ALL F1..F20 ----------
def validate_port():
    pt=(0.463752,0.223255,0.288990,0.488181,0.106157); h=1e-9
    AA._n=[0]; F=cons_full(*[AA.var(v,h) for v in pt]); E=SP.constraints(*pt)
    worst=0.0; ok=True
    for k in range(1,21):
        lo,hi=F[k].iv(); br=lo<=E[k]<=hi; ok&=br; worst=max(worst,(hi-lo)/2)
    print(f"AA port validation over F1..F20 at Rao A: all bracket engine = {ok}  "
          f"(max half-width {worst:.1e})")
    return ok

# ---------- generalized exclusion / Krawczyk / enumerate ----------
def excluded(box, S):
    AA._n=[0]
    try: F=cons_full(*[AA.var((lo+hi)/2,(hi-lo)/2) for (lo,hi) in box])
    except (ValueError,ZeroDivisionError): return False
    for k in S:
        lo,hi=F[k].iv()
        if not (lo<=0<=hi): return True
    return False

def krawczyk(center, r, S):
    AA._n=[0]
    try: Fd=cons_full(*[Dual.var(k,center[k],r) for k in range(5)])
    except (ValueError,ZeroDivisionError): return 'split'
    Jmid=np.array([[Fd[S[i]].grad[j].c    for j in range(5)] for i in range(5)])
    Jrad=np.array([[Fd[S[i]].grad[j].rad() for j in range(5)] for i in range(5)])
    if not np.all(np.isfinite(Jmid)): return 'split'
    try: Y=np.linalg.inv(Jmid)
    except np.linalg.LinAlgError: return 'split'
    Fm=Fvec(center,S)
    Mmid=np.eye(5)-Y@Jmid; Mrad=np.abs(Y)@Jrad
    Kc=-(Y@Fm); Khw=(np.abs(Mmid)+Mrad)@np.full(5,r)
    lo=np.array(center)+Kc-Khw; hi=np.array(center)+Kc+Khw
    Xlo=np.array(center)-r; Xhi=np.array(center)+r
    if np.all(hi<Xhi) and np.all(lo>Xlo): return 'unique'
    if np.any(hi<Xlo) or np.any(lo>Xhi): return 'empty'
    return 'split'

def enum_subset(S, box0, r_cert=3e-3, max_boxes=200000, tlim=55):
    t0=time.time(); stack=[list(box0)]; cert=[]; proc=0; maxq=1
    while stack and proc<max_boxes and time.time()-t0<tlim:
        maxq=max(maxq,len(stack)); box=stack.pop(); proc+=1
        if excluded(box,S): continue
        center=[(lo+hi)/2 for (lo,hi) in box]; rad=max((hi-lo)/2 for (lo,hi) in box)
        if rad<=r_cert:
            v=krawczyk(center,rad,S)
            if v=='unique':
                if not any(max(abs(center[i]-q[i]) for i in range(5))<2*r_cert for q in cert):
                    cert.append(center)
                continue
            if v=='empty': continue
        w=[hi-lo for (lo,hi) in box]; k=int(np.argmax(w)); lo,hi=box[k]; mid=(lo+hi)/2
        L=list(box); L[k]=(lo,mid); R=list(box); R[k]=(mid,hi); stack+=[L,R]
    return dict(cert=cert,proc=proc,maxq=maxq,secs=time.time()-t0,done=(len(stack)==0))

BOX=[(0.20,0.80),(0.10,0.45),(0.15,0.45),(0.25,0.75),(0.03,0.25)]
REF={(1,2,3,4,8):(0.463752,0.223255,0.288990,0.488181,0.106157),
     (1,2,4,5,10):(0.438237,0.218371,0.269490,0.440182,0.096716),
     (1,2,6,14,19):(0.468710,0.257071,0.308200,0.480582,0.121790),
     (1,2,3,10,15):(0.456449,0.236967,0.282560,0.456267,0.104822)}

PANEL=[("Rao A",       (1,2,3,4,8)),
       ("Rao B",       (1,2,4,5,10)),
       ("degenerate",  (1,2,8,9,16)),
       ("coord-heavy", (1,2,11,12,17)),
       ("random",      (1,2,6,10,19)),
       ("dense",       (1,2,3,4,6)),
       ("grounded-F14",(1,2,6,14,19)),
       ("grounded-F15",(1,2,3,10,15))]

CATEGORY={"Rao A":"published-reference","Rao B":"published-reference",
          "grounded-F14":"published-reference (grounded F14)",
          "grounded-F15":"published-reference (grounded F15)",
          "random":"feasible non-reference","coord-heavy":"infeasible (stress F11/F12/F17)",
          "dense":"infeasible (algebraically dense)","degenerate":"rank-deficient (F8-F9+F16=0)"}
BUDGET={"degenerate":(40000,60)}     # rank-deficient: cap (never completes); others run to completion

import csv, json
HERE=os.path.dirname(os.path.abspath(__file__))
OUT=os.path.join(HERE,"validation_panel"); LOGS=os.path.join(OUT,"logs")
os.makedirs(LOGS, exist_ok=True)
CSVP=os.path.join(OUT,"panel_results.csv")
COLS=["label","subset","category","done","roots_certified","boxes_processed",
      "max_queue","runtime_s","ref_delta","certified_root"]

if __name__=="__main__":
    idx=[int(x) for x in sys.argv[1:]] or list(range(len(PANEL)))
    if not validate_port(): print("PORT INVALID — abort."); raise SystemExit
    new=not os.path.exists(CSVP)
    fcsv=open(CSVP,"a",newline=""); wr=csv.writer(fcsv)
    if new: wr.writerow(COLS)
    print(f"\n{'label':12s} {'subset':16s} {'cert':>4s} {'boxes':>7s} {'queue':>5s} "
          f"{'secs':>6s} {'done':>5s}  note")
    for ii,(label,S) in enumerate(PANEL):
        if ii not in idx: continue
        mb,tl=BUDGET.get(label,(700000,255))
        r=enum_subset(list(S), BOX, max_boxes=mb, tlim=tl)
        note=""; refd=""
        if S in REF and r['cert']:
            d=min(max(abs(c[i]-REF[S][i]) for i in range(5)) for c in r['cert'])
            refd=f"{d:.2e}"
            note=f"matches ref (Δ={d:.1e})" if d<0.01 else f"MISMATCH ref (Δ={d:.1e})"
        elif label=="degenerate":
            note="no false certification" if len(r['cert'])==0 else "!! certified (unexpected)"
        elif r['cert']:
            res=max(np.max(np.abs(Fvec(c,S))) for c in r['cert'])
            note=f"engine |F|max≤{res:.0e} at center"
        root=";".join("("+",".join(f"{v:.5f}" for v in c)+")" for c in r['cert'])
        wr.writerow([label,str(S),CATEGORY[label],r['done'],len(r['cert']),
                     r['proc'],r['maxq'],f"{r['secs']:.1f}",refd,root]); fcsv.flush()
        with open(os.path.join(LOGS,f"{label.replace(' ','_')}.log"),"w") as lg:
            lg.write(f"subset {S}  category={CATEGORY[label]}\n"
                     f"box={BOX}\nbudget=(max_boxes={mb},tlim={tl})  r_cert=3e-3\n"
                     f"done={r['done']}  roots_certified={len(r['cert'])}  "
                     f"boxes={r['proc']}  max_queue={r['maxq']}  runtime={r['secs']:.1f}s\n"
                     f"ref={REF.get(S)}  ref_delta={refd}\n"
                     f"certified_roots={r['cert']}\nnote={note}\n")
        print(f"{label:12s} {str(S):16s} {len(r['cert']):>4d} {r['proc']:>7d} "
              f"{r['maxq']:>5d} {r['secs']:>6.1f} {str(r['done']):>5s}  {note}")
        for c in r['cert']:
            print(f"             -> ({', '.join(f'{v:.4f}' for v in c)})")
    fcsv.close()

