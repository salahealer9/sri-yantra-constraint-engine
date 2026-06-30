"""
true_reduced_support_123467.py — Route B2: attempt COEFFICIENT-EXACT node elimination to obtain
the reduced support of each constraint over the 6 base atoms, with a hard explosion guard.

Status ladder (per pre-commit):
  exact_coefficients   -- elimination completed; reduced polynomial + TRUE support obtained
  conservative_support -- elimination guarded/aborted; only a support over-approximation available
  failed               -- elimination exploded past the guard (no usable reduced support)

Method: each node N has def_N (linear in S_N,C_N: den*S_N - C_N*num = 0) and circle S_N^2+C_N^2=1.
Eliminate (S_N,C_N) from a constraint by sequential resultants in reverse dependency order:
  1) res(P, def_N, S_N)               -- removes S_N (def_N linear in S_N)
  2) circ' = C_N^2*(num^2+den^2)-den^2 (circle after S_N=num*C_N/den, cleared)
     res(P1, circ', C_N)              -- removes C_N
Guard: abort a constraint if any intermediate exceeds DEG_CAP total degree or TERM_CAP terms.
The OUTCOME (reduces vs explodes, and at which node) is itself the finding -- it tells us whether
the reduced 6-base geometry is itself high-degree, or whether the lift was paying branch slack.

NO infeasibility claim.
"""
import sys, os, math, json, time, signal
_here = os.path.dirname(os.path.abspath(__file__))
_root = _here
while _root != os.path.dirname(_root):
    if os.path.exists(os.path.join(_root, "sriyantra.py")):
        break
    _root = os.path.dirname(_root)
for _p in (_here, _root, os.path.join(_root, "enumeration")):
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)
import sympy as sp
import polynomialize_probe_123467 as P

DEG_CAP=120        # abort if an intermediate poly exceeds this total degree
TERM_CAP=200000    # or this many terms
STEP_TIMEOUT=45    # seconds per resultant step

class Timeout(Exception): pass
def _alarm(s,f): raise Timeout()

def guarded_resultant(P1, P2, var, label):
    signal.signal(signal.SIGALRM,_alarm); signal.alarm(STEP_TIMEOUT)
    try:
        R=sp.resultant(P1,P2,var)
        R=sp.expand(R)
    finally:
        signal.alarm(0)
    R=sp.factor_terms(R)
    return R

def size(expr):
    expr=sp.expand(expr)
    terms=expr.as_ordered_terms() if expr.is_Add else [expr]
    try: deg=sp.Poly(expr, *expr.free_symbols).total_degree() if expr.free_symbols else 0
    except Exception: deg=-1
    return deg, len(terms)

def eliminate_constraint(L, con_tag):
    """Try to reduce one constraint to base atoms. Returns (status, info)."""
    defeq={t[4:]:eq for t,eq in zip(L.eq_tags,L.eqs) if t.startswith('def_')}
    order=[t[4:] for t in L.eq_tags if t.startswith('def_')]
    pos={n:i for i,n in enumerate(order)}
    def node_atoms(expr):
        return {n.name[2:] for n in expr.free_symbols if n.name.startswith('S_') or n.name.startswith('C_')}
    # transitive cone
    deps={n:node_atoms(defeq[n]) for n in order}
    def closure(ns):
        seen=set(); st=list(ns)
        while st:
            x=st.pop()
            if x in seen: continue
            seen.add(x); st+=list(deps.get(x,[]))
        return seen
    P0=[e for t,e in zip(L.eq_tags,L.eqs) if t==con_tag][0]
    cone=closure(node_atoms(P0))
    elim_order=sorted(cone, key=lambda n:-pos[n])   # deepest (latest) first
    cur=sp.expand(P0)
    trace=[]
    t0=time.time()
    for nm in elim_order:
        S=sp.Symbol('S_'+nm); C=sp.Symbol('C_'+nm)
        eq=defeq[nm]
        den=eq.coeff(S,1); num=-eq.coeff(C,1)
        try:
            if den!=0:   # atan node
                # remove S_N via def (linear in S)
                P1=guarded_resultant(cur, eq, S, nm+':S')
                circp=sp.expand(C**2*(num**2+den**2) - den**2)
                cur=guarded_resultant(P1, circp, C, nm+':C')
            else:        # acos node: eq = coeffC*C + rest -> C = -rest/coeffC ; sub + circle
                coeffC=eq.coeff(C,1); rest=sp.expand(eq-coeffC*C)
                # C determined linearly; also need S via circle: S^2 = 1 - C^2
                P1=guarded_resultant(cur, eq, C, nm+':C')
                # S still possibly present: eliminate via circle with C substituted already gone
                if S in P1.free_symbols:
                    circS=sp.expand(S**2 + (rest/coeffC)**2 - 1)  # may be rational; clear
                    circS=sp.expand(sp.together(circS).as_numer_denom()[0])
                    P1=guarded_resultant(P1, circS, S, nm+':Sacos')
                cur=P1
        except Timeout:
            return 'failed', dict(constraint=con_tag, aborted_at=nm, reason='timeout',
                                  elapsed=time.time()-t0, trace=trace)
        cur=sp.expand(cur)
        deg,nt=size(cur); trace.append((nm,deg,nt))
        if deg>DEG_CAP or nt>TERM_CAP:
            return 'failed', dict(constraint=con_tag, aborted_at=nm, reason='cap',
                                  degree=deg, terms=nt, elapsed=time.time()-t0, trace=trace)
        if cur==0:
            return 'failed', dict(constraint=con_tag, aborted_at=nm, reason='vanished(resultant degenerate)',
                                  trace=trace)
    # fully reduced to base atoms
    base_syms=[v for v in cur.free_symbols if v.name.startswith('s_') or v.name.startswith('c_')]
    deg,nt=size(cur)
    return 'exact_coefficients', dict(constraint=con_tag, reduced_degree=deg, reduced_terms=nt,
                                      base_vars=sorted(s.name for s in base_syms),
                                      elapsed=time.time()-t0, trace=trace)

if __name__=='__main__':
    L=P.build_lift()
    # smallest cone first: F3 (7), F6 (8), then deeper
    targets=['F3','F6','F2','F7','F4','F1']
    print("=== Route B2: coefficient-exact elimination attempt (guarded) ===")
    print("guards: DEG_CAP=%d TERM_CAP=%d STEP_TIMEOUT=%ds\n"%(DEG_CAP,TERM_CAP,STEP_TIMEOUT))
    results={}
    for tag in targets:
        print("--- %s ---"%tag, flush=True)
        st,info=eliminate_constraint(L, tag)
        results[tag]=dict(status=st, **{k:v for k,v in info.items() if k!='trace'})
        if st=='exact_coefficients':
            print("  REDUCED exact: degree=%d terms=%d over %s (%.1fs)"%(
                info['reduced_degree'],info['reduced_terms'],info['base_vars'],info['elapsed']))
        else:
            tr=info.get('trace',[])
            last=tr[-1] if tr else None
            print("  %s at %s (reason=%s); last step %s (%.1fs)"%(
                st.upper(), info.get('aborted_at'), info.get('reason'), last, info.get('elapsed',0)))
        # stop early if even the smallest explodes -- the finding is established
        if tag in ('F3','F6') and st=='failed':
            print("\n  -> smallest cone already fails coefficient-exact elimination; deeper cones worse.")
            break
    json.dump(results, open('docs/true_reduced_support_123467.json','w'),indent=2)
    print("\nsummary -> true_reduced_support_123467.json")
