import sys,time;
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from aar import AAr, DualR
from plane_chain import cons_full, Fvec
S5=[1,2,3,4,8]
BOXB=[(1e-6,0.788471),(1e-6,0.636399),(1e-6,0.635884),(1e-6,0.679513),(1e-6,0.687977)]
RMAX=2.0

def chain_dom(b,c,d,e,g):
    # everything UPSTREAM of x11a (no x11a recip) -> safe on the v9+c+d-v12 seam
    o=1.0
    x1=(o-c*c).sqrt(); x2=(o-d*d).sqrt(); x3=(o-c)/(o+d)*x2; x4=(o-d)/(o+c)*x1
    x5=b/(b+c+d)*x4; x6=e/(c+d+e)*x3
    Q7=(d+g)/(c+d)*(x5/x6); U7=(d+g)/(Q7+o); x7=U7/(c+d)*x5
    Q8=(d+g)/(o+c)*(x1/x6); U8=(o+g)/(Q8+o); x8=U8/(o+c)*x1; v8=o-U8-d
    x16=(d+e+g)/(d+g)*x6; x11=(d+g)/(c+d)*x5; x17=(b+c+d)/(c+d)*x5
    Q9=(c+d)/(o+d)*(x2/x5); U9=(o+d)/(Q9+o); x9=U9/(o+d)*x2; v9=o-U9-c
    x10=(b+c-g)/(b+c+d)*x4; x18=(b+c+d+v8)/(b+c+d)*x4
    S12=d+g+v8; Q12=S12/(d+g)*(x6/x10); U12=S12/(Q12+o); x12=U12/(d+g)*x6; v12=d+g-U12
    x14=(U7+v8)/(d+g+v8)*x10
    x13=(e+v12)/(c+d+e)*x3; x19=(c+d+e+v9)/(c+d+e)*x3
    xs={'x1':x1,'x2':x2,'x3':x3,'x4':x4,'x5':x5,'x6':x6,'x7':x7,'x8':x8,'x9':x9,
        'x10':x10,'x11':x11,'x12':x12,'x13':x13,'x14':x14,'x16':x16,'x17':x17,'x18':x18,'x19':x19}
    pos={'v8':v8,'v9':v9,'v12':v12,'b+c-g':b+c-g}
    num11a=v9+c-g; den11a=v9+c+d-v12
    return xs,pos,num11a,den11a,x13

def absminmax(x):
    lo,hi=x.iv(); amin=0.0 if lo<=0<=hi else min(abs(lo),abs(hi)); amax=max(abs(lo),abs(hi))
    return amin,amax

def domain_excluded(box):
    AAr._n=[0]; B=[AAr.var((lo+hi)/2,(hi-lo)/2) for (lo,hi) in box]; b,c,d,e,g=B; o=1.0
    if (o-c*c).iv()[1]<=0 or (o-d*d).iv()[1]<=0: return True
    try: xs,pos,num,den,x13=chain_dom(*B)
    except (ValueError,ZeroDivisionError): return False
    for q in pos.values():
        if q.iv()[1]<=0: return True
    for x in xs.values():
        lo,hi=x.iv()
        if lo>RMAX or hi<-RMAX: return True
    # x11a range, division-free: |x11a|=|num*x13|/|den| > RMAX everywhere -> exclude
    pmin,_=absminmax(num*x13); _,qmax=absminmax(den)
    if pmin > RMAX*qmax: return True
    return False

def excluded(box):
    AAr._n=[0]
    try: F=cons_full(*[AAr.var((lo+hi)/2,(hi-lo)/2) for (lo,hi) in box])
    except (ValueError,ZeroDivisionError): return False
    for k in S5:
        lo,hi=F[k].iv()
        if not (lo<=0<=hi): return True
    return False
def hw(x): lo,hi=x.iv(); return (hi-lo)/2
def krawczyk(center,r):
    AAr._n=[0]
    try: Fd=cons_full(*[DualR.var(k,center[k],r) for k in range(5)])
    except (ValueError,ZeroDivisionError): return 'split'
    Jm=np.array([[Fd[S5[i]].grad[j].c for j in range(5)] for i in range(5)])
    if not np.all(np.isfinite(Jm)): return 'split'
    Jr=np.array([[hw(Fd[S5[i]].grad[j]) for j in range(5)] for i in range(5)])
    try: Y=np.linalg.inv(Jm)
    except np.linalg.LinAlgError: return 'split'
    Fm=Fvec(center,S5); M=np.eye(5)-Y@Jm; Mr=np.abs(Y)@Jr
    Kc=-(Y@Fm); Kh=(np.abs(M)+Mr)@np.full(5,r)
    lo=np.array(center)+Kc-Kh; hi=np.array(center)+Kc+Kh
    Xl=np.array(center)-r; Xh=np.array(center)+r
    if np.all(hi<Xh) and np.all(lo>Xl): return 'unique'
    if np.any(hi<Xl) or np.any(lo>Xh): return 'empty'
    return 'split'

def enum(tlim=285,max_depth=200,r_cert=3e-3,max_boxes=3000000):
    t0=time.time(); stack=[(list(BOXB),0)]; proc=0; cert=[]; dom=0; unres=0; maxd=0; maxq=1
    while stack and proc<max_boxes and time.time()-t0<tlim:
        maxq=max(maxq,len(stack)); box,dep=stack.pop(); proc+=1; maxd=max(maxd,dep)
        if domain_excluded(box): dom+=1; continue
        if excluded(box): continue
        center=[(lo+hi)/2 for (lo,hi) in box]; rad=max((hi-lo)/2 for (lo,hi) in box)
        if rad<=r_cert:
            v=krawczyk(center,rad)
            if v=='unique':
                if not any(max(abs(center[i]-q[i]) for i in range(5))<2*r_cert for q in cert): cert.append(center)
                continue
            if v=='empty': continue
        if dep>=max_depth: unres+=1; continue
        w=[hi-lo for (lo,hi) in box]; k=int(np.argmax(w)); lo,hi=box[k]; mid=(lo+hi)/2
        L=list(box); L[k]=(lo,mid); R=list(box); R[k]=(mid,hi); stack+=[(L,dep+1),(R,dep+1)]
    return dict(boxes=proc,cert=cert,dom=dom,unres=unres,maxd=maxd,maxq=maxq,
               secs=round(time.time()-t0,1),complete=(len(stack)==0))

def _run():
    print("{1,2,3,4,8} on box B, domain_v3 (division-free x11a range):")
    r=enum()
    print(f"  boxes={r['boxes']} domain_excl={r['dom']} cert={len(r['cert'])} unresolved={r['unres']} "
          f"peak_q={r['maxq']} max_depth={r['maxd']} secs={r['secs']} complete={r['complete']}")
    rao=[0.463752,0.223255,0.288990,0.488181,0.106157]
    for c in r['cert']:
        tag=" <-Rao" if max(abs(c[i]-rao[i]) for i in range(5))<0.01 else ""
        print(f"    cert {[round(x,4) for x in c]}{tag}")

if __name__=="__main__":
    _run()
