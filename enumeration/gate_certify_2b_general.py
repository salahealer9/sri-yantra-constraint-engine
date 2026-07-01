"""Strict gate for certify_2b_general vs the S6 reference certify_2b."""
import sys, os
_here = os.path.dirname(os.path.abspath(__file__))
_root = _here
while _root != os.path.dirname(_root):
    if os.path.exists(os.path.join(_root, "sriyantra.py")):
        break
    _root = os.path.dirname(_root)
for _p in (_here, _root, os.path.join(_root, "enumeration")):
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)
import certify_2b as REF          # S6-only reference
import certify_2b_general as GEN  # generalized

BENCH=[1,2,3,4,6,7]
ROOT=[0.6246238466927992,0.7044304165359816,0.7482768099360514,0.6307397242292889,0.3136386632298885,0.39527668335411803]

def cond_of(ev):
    k=ev.get('krawczyk')
    if isinstance(k,(list,tuple)) and len(k)==2 and isinstance(k[1],str):
        import re; m=re.search(r'cond\(J\)=([0-9.eE+-]+)', k[1])
        return float(m.group(1)) if m else None
    return None

passed=[]; failed=[]
def check(name, ok, detail=''):
    (passed if ok else failed).append(name)
    print(('  PASS ' if ok else '  FAIL ')+name+('  '+detail if detail else ''))

print("=== GATE: certify_2b_general ===\n")

# 1. benchmark still certifies (general)
sg, eg = GEN.certify_2b_candidate(BENCH, ROOT)
check("1. benchmark certifies (general)", sg=='CERTIFIED_UNIQUE_GEOMETRIC', f'status={sg}')

# reference on benchmark
sr, er = REF.certify_2b_candidate(BENCH, ROOT)

# 2. benchmark evidence MATHEMATICALLY identical (class/root-tol/radius/residual-scale/cond-scale/engine/guard)
import math
same_class = sg==sr
root_close = er['real_projected_center'] and eg['real_projected_center'] and \
             max(abs(a-b) for a,b in zip(eg['real_projected_center'],er['real_projected_center']))<1e-10
same_radius = eg['radius_used']==er['radius_used']
resid_scale = (er['residual_norm'] and eg['residual_norm'] and
               abs(math.log10(eg['residual_norm'])-math.log10(er['residual_norm']))<1.0) or \
              (eg['residual_norm']<1e-12 and er['residual_norm']<1e-12)
cg,cr=cond_of(eg),cond_of(er)
cond_scale = cg and cr and abs(math.log10(cg)-math.log10(cr))<0.5
same_engine = eg['engine_hash']==er['engine_hash']
same_guard = eg['full_chain_guard_result']==er['full_chain_guard_result']
check("2. benchmark evidence math-identical", all([same_class,root_close,same_radius,resid_scale,cond_scale,same_engine,same_guard]),
      f'class={same_class} root={root_close} r={same_radius} resid={resid_scale} cond={cond_scale} eng={same_engine} guard={same_guard}')
print(f'       ref: r={er["radius_used"]} resid={er["residual_norm"]:.2e} cond={cr} | gen: r={eg["radius_used"]} resid={eg["residual_norm"]:.2e} cond={cg}')

# 3. non-benchmark subset no longer TECH_FAIL merely for being non-benchmark
#    (use a nearby well-posed subset; supply the benchmark root as a generic candidate -- we only
#     require it does NOT TECH_FAIL for the wiring reason; NOT_CERTIFIED/DOMAIN_INVALID are fine)
for nb in [[1,2,3,4,5,6],[1,2,3,4,6,8],[1,2,5,6,7,8]]:
    s,e = GEN.certify_2b_candidate(nb, ROOT)
    wired_reason = (s=='TECH_FAIL' and 'wired' in str(e.get('note','')))
    check(f"3. non-benchmark {nb} not TECH_FAIL-for-wiring", not wired_reason, f'status={s} note={e.get("note","")[:40]}')

# 4. invalid candidate -> DOMAIN_INVALID (out-of-domain point)
s,e = GEN.certify_2b_candidate(BENCH, [1.4,1.4,1.4,1.4,1.4,1.4])
check("4. invalid candidate -> DOMAIN_INVALID/NOT_CERTIFIED", s in ('DOMAIN_INVALID','NOT_CERTIFIED'), f'status={s}')

# 5. off-root candidate -> NOT_CERTIFIED (displacement cap rejects)
off=[ROOT[0]+0.05, ROOT[1]-0.05, ROOT[2]+0.05, ROOT[3], ROOT[4], ROOT[5]]
s,e = GEN.certify_2b_candidate(BENCH, off)
check("5. off-root -> NOT_CERTIFIED", s=='NOT_CERTIFIED', f'status={s} disp={e.get("polish_displacement")}')

# 6. displacement cap active (no global Newton wander): a far point must be rejected by cap
far=[ROOT[0]+0.15, ROOT[1]-0.15, ROOT[2]+0.1, ROOT[3]+0.1, ROOT[4], ROOT[5]]
s,e = GEN.certify_2b_candidate(BENCH, far)
capped = (s=='NOT_CERTIFIED')
check("6. displacement cap active (far pt rejected)", capped, f'status={s} disp={e.get("polish_displacement")}')

print(f"\n=== {len(passed)}/{len(passed)+len(failed)} PASSED ===")
sys.exit(0 if not failed else 1)
