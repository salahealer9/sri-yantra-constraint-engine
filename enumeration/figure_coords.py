"""
figure_coords.py — §7 figure constructor: the labeled (x,y) points of the plane
Sri Yantra in the registered normalized frame (axis = y-axis, centre = origin,
circumradius r = 1, NO alignment step). Pure straight-line intersection, the same
independent construction validated in geo_check.py against the trig chain.

Returns an ordered dict of labeled points. Base points P0..P10 lie on the axis;
intersection points 1..19 are the figure vertices. Each off-axis point's
x-coordinate is cross-checked against the chain's x_i by validate_against_chain().
"""
import math
import numpy as np
import sriyantra_plane as SP

def iy(P, Q, y):
    (x1,y1),(x2,y2) = P,Q; t=(y-y1)/(y2-y1); return (x1+t*(x2-x1), y)
def ii(P, Q, R, S):
    (x1,y1),(x2,y2)=P,Q; (x3,y3),(x4,y4)=R,S
    den=(x1-x2)*(y3-y4)-(y1-y2)*(x3-x4)
    px=((x1*y2-y1*x2)*(x3-x4)-(x1-x2)*(x3*y4-y3*x4))/den
    py=((x1*y2-y1*x2)*(y3-y4)-(y1-y2)*(x3*y4-y3*x4))/den
    return (px,py)

def figure_coordinates(b,c,d,e,g,r=1.0):
    # --- base points on the axis (x=0) ---
    Pc=(0.0,0.0); P0=(0.0,-r); P1=(0.0,-(b+c)); P3=(0.0,-c); P4=(0.0,-g)
    P7=(0.0,d); P9=(0.0,d+e); P10=(0.0,r)
    # --- the primary intersection points (geo_check construction) ---
    p1=(math.sqrt(r*r-c*c), -c)          # baseline(P3) ∩ circle
    p2=(math.sqrt(r*r-d*d),  d)          # baseline(P7) ∩ circle
    p3=iy(P0,p2,-c)                      # transversal P0-2 at height -c
    p4=iy(P10,p1,d)                      # transversal P10-1 at height  d
    p5=iy(P1,p4,-c)                      # transversal P1-4 at height -c
    p6=iy(P9,p3,d)                       # transversal P9-3 at height  d
    p8=ii(P4,p6,P10,p1)                  # P4-6 ∩ P10-1
    p9=ii(P7,p5,P0,p2)                   # P7-5 ∩ P0-2
    yP8=p8[1]; yP2=p9[1]
    P8=(0.0,yP8); P2=(0.0,yP2)
    p10=iy(P1,p4,-g)                     # transversal P1-4 at height -g
    p12=ii(P4,p6,P8,p10)                 # P4-6 ∩ P8-10
    yP6=p12[1]; P6=(0.0,yP6)
    p7 =ii(P4,p6,P7,p5)                 # point 7  : T(P4-6) ∩ T(P7-5)
    p11=iy(P7,p5,-g)                     # point 11 : T(P7-5) at baseline P4 (height -g)
    p13=iy(P9,p3,yP6)                    # point 13 : T(P9-3) at baseline P6
    p16=iy(P4,p6,d+e)                    # baseline(P9) ∩ transversal P4-6
    p17=iy(P7,p5,-(b+c))                 # baseline(P1) ∩ transversal P7-5
    p18=iy(P1,p4,yP8)                    # baseline(P8) ∩ transversal P1-4
    p19=iy(P9,p3,yP2)                    # baseline(P2) ∩ transversal P9-3
    pts = {
        'P0':P0,'P1':P1,'P2':P2,'P3':P3,'P4':P4,'P6':P6,'P7':P7,'P8':P8,'P9':P9,'P10':P10,
        '1':p1,'2':p2,'3':p3,'4':p4,'5':p5,'6':p6,'7':p7,'8':p8,'9':p9,'10':p10,
        '11':p11,'12':p12,'13':p13,'16':p16,'17':p17,'18':p18,'19':p19,
    }
    return pts

# x_i in the chain for cross-checking constructed points (point label -> chain key)
_CHAIN_X = {'1':'x1','2':'x2','3':'x3','4':'x4','5':'x5','6':'x6','7':'x7','8':'x8',
            '9':'x9','10':'x10','11':'x11','12':'x12','13':'x13','16':'x16','17':'x17',
            '18':'x18','19':'x19'}

def validate_against_chain(b,c,d,e,g):
    pts=figure_coordinates(b,c,d,e,g); s=SP.chain(b,c,d,e,g)
    out={}
    for lbl,xkey in _CHAIN_X.items():
        out[lbl]=abs(abs(pts[lbl][0]) - abs(s[xkey]))
    return out
