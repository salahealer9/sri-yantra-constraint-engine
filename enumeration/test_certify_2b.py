"""Five-case (plus disjoint + genuinely-complex) battery proving the certify_2b contract."""
import math
import certify_2b as C
ROOT=[0.6246238466927992,0.7044304165359816,0.7482768099360514,
      0.6307397242292889,0.3136386632298885,22.64768569612002*math.pi/180]

def run():
    R={}
    s,ev=C.certify_2b_candidate(C.S6, ROOT); R['1_known_root']=(s,'CERTIFIED_UNIQUE_GEOMETRIC')
    s,_=C.certify_2b_candidate(C.S6, [0.50,0.55,0.90,0.45,0.50,0.30]); R['2_offroot_far']=(s,'NOT_CERTIFIED')
    s,_=C.certify_2b_candidate(C.S6, [0.5,1.40,0.70,0.55,0.30,0.40]); R['3_out_of_domain']=(s,'DOMAIN_INVALID')
    s,_=C.certify_2b_candidate(C.S6, [complex(ROOT[i],(1e-7 if i==0 else 0.0)) for i in range(6)]); R['4_complex_near_real']=(s,'CERTIFIED_UNIQUE_GEOMETRIC')
    s,_=C.certify_2b_candidate(C.S6, [complex(0.5,0.3),complex(0.55,0.3),complex(0.9,0.3),complex(0.45,0.3),complex(0.5,0.3),complex(0.3,0.3)]); R['4b_complex_far']=(s,'NOT_CERTIFIED')
    _,ev1=C.certify_2b_candidate(C.S6, ROOT)
    _,ev2=C.certify_2b_candidate(C.S6, [ROOT[i]+(1e-5 if i==0 else 0.0) for i in range(6)])
    cnt,_,_=C.collapse_certified([ev1,ev2]); R['5_overlap_collapse']=(cnt,1)
    cnt2,_,_=C.collapse_certified([ev1, dict(status='CERTIFIED_UNIQUE_GEOMETRIC', box_bounds=[(10,10.001)]*6)])
    R['5b_disjoint_count']=(cnt2,2)
    return R

if __name__=='__main__':
    print('certify_2b contract battery (engine_hash=%s)'%C.ENGINE_HASH)
    R=run(); ok=True
    for k,(got,exp) in R.items():
        p=(got==exp); ok=ok and p
        print('  %-22s got=%-28s expect=%-28s %s'%(k,got,exp,'PASS' if p else 'FAIL'))
    print('ALL PASS:', ok)
