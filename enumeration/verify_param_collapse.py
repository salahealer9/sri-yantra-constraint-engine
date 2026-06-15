"""
verify_param_collapse.py — parameter-space verification of the §7 distinct count.

Independent of the 27-point figure metric: two certified solutions are the SAME
figure iff their parameter vectors (b,c,d,e,g) coincide (params -> figure is
bijective). This clusters the 134 certified roots by L-infinity parameter distance,
reports every identical class with its exact internal spread, and states the exact
distinct-figure count. Removes any dependence on figure_coords.
"""
import os, sys, json, itertools
HERE=os.path.dirname(os.path.abspath(__file__))
import numpy as np
RES=os.path.join(HERE,"campaign_results")
IDENT=1e-9                      # below this, parameter vectors are "identical"
TAUS=[1e-2,1e-3,1e-4,1e-5]

def load():
    out=[]
    for L in open(os.path.join(RES,"roots.jsonl")):
        d=json.loads(L)
        for rt in d.get("roots",[]):
            out.append((tuple(d["subset"]), np.array(rt["coords"])))
    return out

def cluster(P, tau, n):
    parent=list(range(n))
    def find(x):
        while parent[x]!=x: parent[x]=parent[parent[x]]; x=parent[x]
        return x
    for i in range(n):
        for j in range(i+1,n):
            if np.max(np.abs(P[i]-P[j]))<tau: parent[find(i)]=find(j)
    comp={}
    for i in range(n): comp.setdefault(find(i),[]).append(i)
    return list(comp.values())

def main():
    figs=load(); n=len(figs); P=[p for _,p in figs]
    print("Parameter-space verification over %d certified feasible roots"%n)
    print("  metric: L-inf parameter distance  max|Δ(b,c,d,e,g)|   (figure-construction-independent)\n")
    # exact distinct count: merge only parameter-identical roots
    classes=cluster(P,IDENT,n)
    identical=[c for c in classes if len(c)>1]
    print("  IDENTICAL-parameter classes (max|Δparam| < %.0e):"%IDENT)
    for c in sorted(identical, key=lambda c:-len(c)):
        spread=max(np.max(np.abs(P[i]-P[j])) for i,j in itertools.combinations(c,2))
        subs=[figs[i][0] for i in c]
        print("    %d subsets, max|Δparam| = %.2e :"%(len(c),spread))
        for s in subs: print("        %s"%(s,))
    print("\n  EXACT distinct-figure count (parameter-identical collapses only): %d"%len(classes))
    print("    = %d singleton figures + %d over-determined classes"%(
          sum(1 for c in classes if len(c)==1), len(identical)))
    print("    reduction from %d feasible subsets: %d  (= sum of class_size-1)\n"%(n, n-len(classes)))
    # parameter-space tau sweep, to compare with the figure-metric sweep
    print("  parameter-space tau sweep (for comparison with the §7 figure sweep):")
    for tau in TAUS:
        print("    tau %.0e -> %d clusters"%(tau, len(cluster(P,tau,n))))

if __name__=="__main__": main()
