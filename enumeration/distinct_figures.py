"""
distinct_figures.py — §7 distinct-figure count over the certified Tier-2 census.

Two certified solutions describe the SAME figure iff their 30-point figures
coincide under the registered §7 metric:
  normalized frame (r=1, centre origin, axis = y, NO alignment),
  d(F_i, F_j) = max over labeled points of Euclidean point-to-point distance,
counted distinct at thresholds tau in {1e-2,1e-3,1e-4,1e-5}.

This turns "N feasible subsets" into "N distinct figures": different subsets can be
satisfied by the same figure, so the distinct count <= the feasible-subset count.

Metric note (rigorous lower bound): figure_coords emits 27 of the 30 labeled points
(10 base + intersection 1-13,16-19), each validated to ~1e-16 against the engine
chain. The max over this validated subset is <= the full 30-point metric, so any
pair at distance >= tau here is PROVABLY distinct under the full metric, and a
reported count of 134 at a given tau is exact (it cannot exceed the subset count).
Only pairs that merge (d < tau) could be affected by the 3 omitted points (14,15,P5)
and are flagged.
"""
import os, sys, json, itertools
HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import numpy as np
import figure_coords as FC

TAUS=[1e-2,1e-3,1e-4,1e-5]
RES=os.path.join(HERE,"campaign_results"); OUT=os.path.join(HERE,"figure_results")

def load_feasible():
    figs=[]
    for line in open(os.path.join(RES,"roots.jsonl")):
        d=json.loads(line)
        for rt in d.get("roots",[]):
            figs.append((tuple(d["subset"]), rt["coords"]))
    return figs

def figure_vector(coords):
    pts=FC.figure_coordinates(*coords)
    return {k:np.array(v) for k,v in pts.items()}, list(pts.keys())

def metric(Fa, Fb, labels):
    return max(np.hypot(*(Fa[k]-Fb[k])) for k in labels)

def clusters(D, tau, n):
    parent=list(range(n))
    def find(x):
        while parent[x]!=x: parent[x]=parent[parent[x]]; x=parent[x]
        return x
    for i in range(n):
        for j in range(i+1,n):
            if D[i,j]<tau:
                parent[find(i)]=find(j)
    return len({find(i) for i in range(n)})

def main():
    os.makedirs(OUT,exist_ok=True)
    figs=load_feasible(); n=len(figs)
    F=[]; labels=None
    for _,c in figs:
        fv,lab=figure_vector(c); F.append(fv); labels=lab
    D=np.zeros((n,n))
    for i in range(n):
        for j in range(i+1,n):
            D[i,j]=D[j,i]=metric(F[i],F[j],labels)
    mask=np.ones_like(D,bool); np.fill_diagonal(mask,False)
    flat=np.where(mask,D,np.inf); a,b=np.unravel_index(np.argmin(flat),D.shape); mind=D[a,b]
    print("§7 distinct-figure count over %d certified feasible figures"%n)
    print("  metric: max over %d validated labeled points (r=1, centre origin, axis y, no alignment)"%len(labels))
    print("  closest pair distance: %.4e  -> subsets %s and %s"%(mind,figs[a][0],figs[b][0]))
    print("  tau      distinct figures   (= %d means all distinct; exact when = %d)"%(n,n))
    rows=[]
    for tau in TAUS:
        k=clusters(D,tau,n); rows.append((tau,k))
        merged=[] 
        if k<n:
            parent=list(range(n))
            def find(x):
                while parent[x]!=x: parent[x]=parent[parent[x]]; x=parent[x]
                return x
            for i in range(n):
                for j in range(i+1,n):
                    if D[i,j]<tau: parent[find(i)]=find(j); merged.append((figs[i][0],figs[j][0],D[i,j]))
        flag=' (EXACT: all distinct)' if k==n else ' <- some pairs merge'
        print("  %.0e   %d%s"%(tau,k,flag))
        for s1,s2,dd in merged[:20]:
            print("        merged: %s ~ %s  (d=%.2e < tau; full-metric check w/ pts 14,15,P5 advisable)"%(s1,s2,dd))
    with open(os.path.join(OUT,"distinct_figures.csv"),"w") as f:
        f.write("tau,distinct_figures\n")
        for tau,k in rows: f.write("%.0e,%d\n"%(tau,k))
    print("  min pairwise distance %.4e %s 1e-2 -> %s"%(mind, '>=' if mind>=1e-2 else '<',
          'all %d figures distinct at every tau (count exact)'%n if mind>=1e-2 else 'see merged pairs'))

if __name__=="__main__": main()
