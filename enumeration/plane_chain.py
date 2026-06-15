"""
plane_chain.py — the Rao (1998) plane constraint system F1..F20 in arithmetic-
generic form (works for float, rigorous AA, or AA-dual), plus the engine vector.

Single source of the confirmatory constraint chain. Identical to the port
validated in the validation panel and Gate M (brackets the v0.1.0 engine on all
20 constraints; F2 via the validated w-form). cons_full takes any number type
supporting +,-,*,/ and a .sqrt() method.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, '.')
import numpy as np
import sriyantra_plane as SP

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

def Fvec(p, S):
    F=SP.constraints(*p); return np.array([F[k] for k in S])
