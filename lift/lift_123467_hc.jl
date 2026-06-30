using HomotopyContinuation
@var s_b c_b s_c c_c s_d c_d s_e c_e s_g c_g s_h c_h S_x1 C_x1 S_x2 C_x2 S_x3 C_x3 S_x4 C_x4 S_x5 C_x5 S_x6 C_x6 S_U7 C_U7 S_x7 C_x7 S_U8 C_U8 S_U9 C_U9 S_x10 C_x10 S_U12 C_U12 S_x13 C_x13 S_x18 C_x18 S_x19 C_x19 S_x11 C_x11 S_x11a C_x11a S_t C_t S_rT C_rT
F = System([
    c_b^2 + s_b^2 - 1,   # pyth_b
    c_c^2 + s_c^2 - 1,   # pyth_c
    c_d^2 + s_d^2 - 1,   # pyth_d
    c_e^2 + s_e^2 - 1,   # pyth_e
    c_g^2 + s_g^2 - 1,   # pyth_g
    c_h^2 + s_h^2 - 1,   # pyth_h
    C_x1^2 + S_x1^2 - 1,   # pyth_x1
    C_x1*c_c - s_h,   # def_x1
    C_x2^2 + S_x2^2 - 1,   # pyth_x2
    C_x2*c_d - s_h,   # def_x2
    C_x3^2 + S_x3^2 - 1,   # pyth_x3
    C_x2*S_x3*c_d*c_h + C_x2*S_x3*s_d*s_h - C_x3*S_x2*c_c*c_h + C_x3*S_x2*s_c*s_h,   # def_x3
    C_x4^2 + S_x4^2 - 1,   # pyth_x4
    C_x1*S_x4*c_c*c_h + C_x1*S_x4*s_c*s_h - C_x4*S_x1*c_d*c_h + C_x4*S_x1*s_d*s_h,   # def_x4
    C_x5^2 + S_x5^2 - 1,   # pyth_x5
    C_x4*S_x5*c_b*c_c*s_d + C_x4*S_x5*c_b*c_d*s_c + C_x4*S_x5*c_c*c_d*s_b - C_x4*S_x5*s_b*s_c*s_d - C_x5*S_x4*s_b,   # def_x5
    C_x6^2 + S_x6^2 - 1,   # pyth_x6
    C_x3*S_x6*c_c*c_d*s_e + C_x3*S_x6*c_c*c_e*s_d + C_x3*S_x6*c_d*c_e*s_c - C_x3*S_x6*s_c*s_d*s_e - C_x6*S_x3*s_e,   # def_x6
    C_U7^2 + S_U7^2 - 1,   # pyth_U7
    -C_U7*C_x5*S_x6*c_c*c_d*s_d*s_g - C_U7*C_x5*S_x6*c_c*c_g*s_d^2 - C_U7*C_x5*S_x6*c_d^2*s_c*s_g - C_U7*C_x5*S_x6*c_d*c_g*s_c*s_d + C_x5*S_U7*S_x6*c_c*c_d*c_g*s_d - C_x5*S_U7*S_x6*c_c*s_d^2*s_g + C_x5*S_U7*S_x6*c_d^2*c_g*s_c - C_x5*S_U7*S_x6*c_d*s_c*s_d*s_g + C_x6*S_U7*S_x5*c_d*s_g + C_x6*S_U7*S_x5*c_g*s_d,   # def_U7
    C_x7^2 + S_x7^2 - 1,   # pyth_x7
    C_x5*S_x7*c_c*s_d + C_x5*S_x7*c_d*s_c - C_x7*S_U7*S_x5,   # def_x7
    C_U8^2 + S_U8^2 - 1,   # pyth_U8
    -C_U8*C_x1*S_x6*c_c*c_g*c_h^2 - C_U8*C_x1*S_x6*c_c*c_h*s_g*s_h - C_U8*C_x1*S_x6*c_g*c_h*s_c*s_h - C_U8*C_x1*S_x6*s_c*s_g*s_h^2 + C_x1*S_U8*S_x6*c_c*c_g*c_h*s_h - C_x1*S_U8*S_x6*c_c*c_h^2*s_g + C_x1*S_U8*S_x6*c_g*s_c*s_h^2 - C_x1*S_U8*S_x6*c_h*s_c*s_g*s_h + C_x6*S_U8*S_x1*c_d*s_g + C_x6*S_U8*S_x1*c_g*s_d,   # def_U8
    C_U9^2 + S_U9^2 - 1,   # pyth_U9
    -C_U9*C_x2*S_x5*c_d^2*c_h^2 - 2*C_U9*C_x2*S_x5*c_d*c_h*s_d*s_h - C_U9*C_x2*S_x5*s_d^2*s_h^2 + C_x2*S_U9*S_x5*c_d^2*c_h*s_h - C_x2*S_U9*S_x5*c_d*c_h^2*s_d + C_x2*S_U9*S_x5*c_d*s_d*s_h^2 - C_x2*S_U9*S_x5*c_h*s_d^2*s_h + C_x5*S_U9*S_x2*c_c*s_d + C_x5*S_U9*S_x2*c_d*s_c,   # def_U9
    C_x10^2 + S_x10^2 - 1,   # pyth_x10
    C_x10*S_x4*c_b*c_c*s_g - C_x10*S_x4*c_b*c_g*s_c - C_x10*S_x4*c_c*c_g*s_b - C_x10*S_x4*s_b*s_c*s_g + C_x4*S_x10*c_b*c_c*s_d + C_x4*S_x10*c_b*c_d*s_c + C_x4*S_x10*c_c*c_d*s_b - C_x4*S_x10*s_b*s_c*s_d,   # def_x10
    C_U12^2 + S_U12^2 - 1,   # pyth_U12
    -C_U12*C_U8*C_x6*S_x10*c_d^3*c_g*c_h*s_g - C_U12*C_U8*C_x6*S_x10*c_d^3*s_g^2*s_h - C_U12*C_U8*C_x6*S_x10*c_d^2*c_g^2*c_h*s_d - C_U12*C_U8*C_x6*S_x10*c_d^2*c_g*s_d*s_g*s_h - C_U12*C_U8*C_x6*S_x10*c_d*c_g*c_h*s_d^2*s_g - C_U12*C_U8*C_x6*S_x10*c_d*s_d^2*s_g^2*s_h - C_U12*C_U8*C_x6*S_x10*c_g^2*c_h*s_d^3 - C_U12*C_U8*C_x6*S_x10*c_g*s_d^3*s_g*s_h + C_U12*C_x6*S_U8*S_x10*c_d^3*c_g*s_g*s_h - C_U12*C_x6*S_U8*S_x10*c_d^3*c_h*s_g^2 + C_U12*C_x6*S_U8*S_x10*c_d^2*c_g^2*s_d*s_h - C_U12*C_x6*S_U8*S_x10*c_d^2*c_g*c_h*s_d*s_g + C_U12*C_x6*S_U8*S_x10*c_d*c_g*s_d^2*s_g*s_h - C_U12*C_x6*S_U8*S_x10*c_d*c_h*s_d^2*s_g^2 + C_U12*C_x6*S_U8*S_x10*c_g^2*s_d^3*s_h - C_U12*C_x6*S_U8*S_x10*c_g*c_h*s_d^3*s_g + C_U8*C_x10*S_U12*S_x6*c_d^2*c_g*c_h + C_U8*C_x10*S_U12*S_x6*c_d^2*s_g*s_h + C_U8*C_x10*S_U12*S_x6*c_g*c_h*s_d^2 + C_U8*C_x10*S_U12*S_x6*s_d^2*s_g*s_h + C_U8*C_x6*S_U12*S_x10*c_d^3*c_g*s_g*s_h - C_U8*C_x6*S_U12*S_x10*c_d^3*c_h*s_g^2 + C_U8*C_x6*S_U12*S_x10*c_d^2*c_g^2*s_d*s_h - C_U8*C_x6*S_U12*S_x10*c_d^2*c_g*c_h*s_d*s_g + C_U8*C_x6*S_U12*S_x10*c_d*c_g*s_d^2*s_g*s_h - C_U8*C_x6*S_U12*S_x10*c_d*c_h*s_d^2*s_g^2 + C_U8*C_x6*S_U12*S_x10*c_g^2*s_d^3*s_h - C_U8*C_x6*S_U12*S_x10*c_g*c_h*s_d^3*s_g - C_x10*S_U12*S_U8*S_x6*c_d^2*c_g*s_h + C_x10*S_U12*S_U8*S_x6*c_d^2*c_h*s_g - C_x10*S_U12*S_U8*S_x6*c_g*s_d^2*s_h + C_x10*S_U12*S_U8*S_x6*c_h*s_d^2*s_g + C_x6*S_U12*S_U8*S_x10*c_d^3*c_g*c_h*s_g + C_x6*S_U12*S_U8*S_x10*c_d^3*s_g^2*s_h + C_x6*S_U12*S_U8*S_x10*c_d^2*c_g^2*c_h*s_d + C_x6*S_U12*S_U8*S_x10*c_d^2*c_g*s_d*s_g*s_h + C_x6*S_U12*S_U8*S_x10*c_d*c_g*c_h*s_d^2*s_g + C_x6*S_U12*S_U8*S_x10*c_d*s_d^2*s_g^2*s_h + C_x6*S_U12*S_U8*S_x10*c_g^2*c_h*s_d^3 + C_x6*S_U12*S_U8*S_x10*c_g*s_d^3*s_g*s_h,   # def_U12
    C_x13^2 + S_x13^2 - 1,   # pyth_x13
    -C_U12*C_x13*S_x3*c_d*c_e*s_g - C_U12*C_x13*S_x3*c_d*c_g*s_e - C_U12*C_x13*S_x3*c_e*c_g*s_d + C_U12*C_x13*S_x3*s_d*s_e*s_g + C_x13*S_U12*S_x3*c_d*c_e*c_g - C_x13*S_U12*S_x3*c_d*s_e*s_g - C_x13*S_U12*S_x3*c_e*s_d*s_g - C_x13*S_U12*S_x3*c_g*s_d*s_e + C_x3*S_x13*c_c*c_d*s_e + C_x3*S_x13*c_c*c_e*s_d + C_x3*S_x13*c_d*c_e*s_c - C_x3*S_x13*s_c*s_d*s_e,   # def_x13
    C_x18^2 + S_x18^2 - 1,   # pyth_x18
    -C_U8*C_x18*S_x4*c_b*c_c*c_d^2*c_h - C_U8*C_x18*S_x4*c_b*c_c*c_h*s_d^2 - C_U8*C_x18*S_x4*c_b*c_d^2*s_c*s_h - C_U8*C_x18*S_x4*c_b*s_c*s_d^2*s_h - C_U8*C_x18*S_x4*c_c*c_d^2*s_b*s_h - C_U8*C_x18*S_x4*c_c*s_b*s_d^2*s_h + C_U8*C_x18*S_x4*c_d^2*c_h*s_b*s_c + C_U8*C_x18*S_x4*c_h*s_b*s_c*s_d^2 + C_x18*S_U8*S_x4*c_b*c_c*c_d^2*s_h + C_x18*S_U8*S_x4*c_b*c_c*s_d^2*s_h - C_x18*S_U8*S_x4*c_b*c_d^2*c_h*s_c - C_x18*S_U8*S_x4*c_b*c_h*s_c*s_d^2 - C_x18*S_U8*S_x4*c_c*c_d^2*c_h*s_b - C_x18*S_U8*S_x4*c_c*c_h*s_b*s_d^2 - C_x18*S_U8*S_x4*c_d^2*s_b*s_c*s_h - C_x18*S_U8*S_x4*s_b*s_c*s_d^2*s_h + C_x4*S_x18*c_b*c_c*s_d + C_x4*S_x18*c_b*c_d*s_c + C_x4*S_x18*c_c*c_d*s_b - C_x4*S_x18*s_b*s_c*s_d,   # def_x18
    C_x19^2 + S_x19^2 - 1,   # pyth_x19
    -C_U9*C_x19*S_x3*c_c^2*c_d*c_e*c_h - C_U9*C_x19*S_x3*c_c^2*c_d*s_e*s_h - C_U9*C_x19*S_x3*c_c^2*c_e*s_d*s_h + C_U9*C_x19*S_x3*c_c^2*c_h*s_d*s_e - C_U9*C_x19*S_x3*c_d*c_e*c_h*s_c^2 - C_U9*C_x19*S_x3*c_d*s_c^2*s_e*s_h - C_U9*C_x19*S_x3*c_e*s_c^2*s_d*s_h + C_U9*C_x19*S_x3*c_h*s_c^2*s_d*s_e + C_x19*S_U9*S_x3*c_c^2*c_d*c_e*s_h - C_x19*S_U9*S_x3*c_c^2*c_d*c_h*s_e - C_x19*S_U9*S_x3*c_c^2*c_e*c_h*s_d - C_x19*S_U9*S_x3*c_c^2*s_d*s_e*s_h + C_x19*S_U9*S_x3*c_d*c_e*s_c^2*s_h - C_x19*S_U9*S_x3*c_d*c_h*s_c^2*s_e - C_x19*S_U9*S_x3*c_e*c_h*s_c^2*s_d - C_x19*S_U9*S_x3*s_c^2*s_d*s_e*s_h + C_x3*S_x19*c_c*c_d*s_e + C_x3*S_x19*c_c*c_e*s_d + C_x3*S_x19*c_d*c_e*s_c - C_x3*S_x19*s_c*s_d*s_e,   # def_x19
    C_x11^2 + S_x11^2 - 1,   # pyth_x11
    -C_x11*S_x5*c_d*s_g - C_x11*S_x5*c_g*s_d + C_x5*S_x11*c_c*s_d + C_x5*S_x11*c_d*s_c,   # def_x11
    C_x11a^2 + S_x11a^2 - 1,   # pyth_x11a
    C_U12*C_U9*C_x13*S_x11a*c_c^2*c_d^2*c_g*c_h - C_U12*C_U9*C_x13*S_x11a*c_c^2*c_d^2*s_g*s_h + C_U12*C_U9*C_x13*S_x11a*c_c^2*c_g*c_h*s_d^2 - C_U12*C_U9*C_x13*S_x11a*c_c^2*s_d^2*s_g*s_h + C_U12*C_U9*C_x13*S_x11a*c_d^2*c_g*c_h*s_c^2 - C_U12*C_U9*C_x13*S_x11a*c_d^2*s_c^2*s_g*s_h + C_U12*C_U9*C_x13*S_x11a*c_g*c_h*s_c^2*s_d^2 - C_U12*C_U9*C_x13*S_x11a*s_c^2*s_d^2*s_g*s_h - C_U12*C_x13*S_U9*S_x11a*c_c^2*c_d^2*c_g*s_h - C_U12*C_x13*S_U9*S_x11a*c_c^2*c_d^2*c_h*s_g - C_U12*C_x13*S_U9*S_x11a*c_c^2*c_g*s_d^2*s_h - C_U12*C_x13*S_U9*S_x11a*c_c^2*c_h*s_d^2*s_g - C_U12*C_x13*S_U9*S_x11a*c_d^2*c_g*s_c^2*s_h - C_U12*C_x13*S_U9*S_x11a*c_d^2*c_h*s_c^2*s_g - C_U12*C_x13*S_U9*S_x11a*c_g*s_c^2*s_d^2*s_h - C_U12*C_x13*S_U9*S_x11a*c_h*s_c^2*s_d^2*s_g - C_U9*C_x11a*S_x13*c_c^2*c_g*c_h + C_U9*C_x11a*S_x13*c_c^2*s_g*s_h - C_U9*C_x11a*S_x13*c_g*c_h*s_c^2 + C_U9*C_x11a*S_x13*s_c^2*s_g*s_h + C_U9*C_x13*S_U12*S_x11a*c_c^2*c_d^2*c_g*s_h + C_U9*C_x13*S_U12*S_x11a*c_c^2*c_d^2*c_h*s_g + C_U9*C_x13*S_U12*S_x11a*c_c^2*c_g*s_d^2*s_h + C_U9*C_x13*S_U12*S_x11a*c_c^2*c_h*s_d^2*s_g + C_U9*C_x13*S_U12*S_x11a*c_d^2*c_g*s_c^2*s_h + C_U9*C_x13*S_U12*S_x11a*c_d^2*c_h*s_c^2*s_g + C_U9*C_x13*S_U12*S_x11a*c_g*s_c^2*s_d^2*s_h + C_U9*C_x13*S_U12*S_x11a*c_h*s_c^2*s_d^2*s_g + C_x11a*S_U9*S_x13*c_c^2*c_g*s_h + C_x11a*S_U9*S_x13*c_c^2*c_h*s_g + C_x11a*S_U9*S_x13*c_g*s_c^2*s_h + C_x11a*S_U9*S_x13*c_h*s_c^2*s_g + C_x13*S_U12*S_U9*S_x11a*c_c^2*c_d^2*c_g*c_h - C_x13*S_U12*S_U9*S_x11a*c_c^2*c_d^2*s_g*s_h + C_x13*S_U12*S_U9*S_x11a*c_c^2*c_g*c_h*s_d^2 - C_x13*S_U12*S_U9*S_x11a*c_c^2*s_d^2*s_g*s_h + C_x13*S_U12*S_U9*S_x11a*c_d^2*c_g*c_h*s_c^2 - C_x13*S_U12*S_U9*S_x11a*c_d^2*s_c^2*s_g*s_h + C_x13*S_U12*S_U9*S_x11a*c_g*c_h*s_c^2*s_d^2 - C_x13*S_U12*S_U9*S_x11a*s_c^2*s_d^2*s_g*s_h,   # def_x11a
    C_t^2 + S_t^2 - 1,   # pyth_t
    -C_U7*C_t*c_d*s_g - C_U7*C_t*c_g*s_d + C_U7*S_t*S_x7*c_d*c_g - C_U7*S_t*S_x7*s_d*s_g + C_t*S_U7*c_d*c_g - C_t*S_U7*s_d*s_g + S_U7*S_t*S_x7*c_d*s_g + S_U7*S_t*S_x7*c_g*s_d,   # def_t
    C_rT^2 + S_rT^2 - 1,   # pyth_rT
    -C_rT*S_t*S_x7 + C_t*S_rT + S_rT,   # def_rT
    -C_x11*S_x11a + C_x11a*S_x11,   # F1
    C_U7*C_rT*s_d - C_U7*S_rT*c_d - C_rT*S_U7*c_d - S_U7*S_rT*s_d,   # F2
    C_U8*C_x10*c_g*s_h - C_U8*C_x10*c_h*s_g - 2*C_x10^2 + C_x10*S_U8*c_g*c_h + C_x10*S_U8*s_g*s_h + 1,   # F3
    C_U12*C_U9*C_x13*c_c^2*c_d^2*c_g*s_h + C_U12*C_U9*C_x13*c_c^2*c_d^2*c_h*s_g + C_U12*C_U9*C_x13*c_c^2*c_g*s_d^2*s_h + C_U12*C_U9*C_x13*c_c^2*c_h*s_d^2*s_g + C_U12*C_U9*C_x13*c_d^2*c_g*s_c^2*s_h + C_U12*C_U9*C_x13*c_d^2*c_h*s_c^2*s_g + C_U12*C_U9*C_x13*c_g*s_c^2*s_d^2*s_h + C_U12*C_U9*C_x13*c_h*s_c^2*s_d^2*s_g + C_U12*C_x13*S_U9*c_c^2*c_d^2*c_g*c_h - C_U12*C_x13*S_U9*c_c^2*c_d^2*s_g*s_h + C_U12*C_x13*S_U9*c_c^2*c_g*c_h*s_d^2 - C_U12*C_x13*S_U9*c_c^2*s_d^2*s_g*s_h + C_U12*C_x13*S_U9*c_d^2*c_g*c_h*s_c^2 - C_U12*C_x13*S_U9*c_d^2*s_c^2*s_g*s_h + C_U12*C_x13*S_U9*c_g*c_h*s_c^2*s_d^2 - C_U12*C_x13*S_U9*s_c^2*s_d^2*s_g*s_h - C_U9*C_x13*S_U12*c_c^2*c_d^2*c_g*c_h + C_U9*C_x13*S_U12*c_c^2*c_d^2*s_g*s_h - C_U9*C_x13*S_U12*c_c^2*c_g*c_h*s_d^2 + C_U9*C_x13*S_U12*c_c^2*s_d^2*s_g*s_h - C_U9*C_x13*S_U12*c_d^2*c_g*c_h*s_c^2 + C_U9*C_x13*S_U12*c_d^2*s_c^2*s_g*s_h - C_U9*C_x13*S_U12*c_g*c_h*s_c^2*s_d^2 + C_U9*C_x13*S_U12*s_c^2*s_d^2*s_g*s_h - 2*C_x13^2 + C_x13*S_U12*S_U9*c_c^2*c_d^2*c_g*s_h + C_x13*S_U12*S_U9*c_c^2*c_d^2*c_h*s_g + C_x13*S_U12*S_U9*c_c^2*c_g*s_d^2*s_h + C_x13*S_U12*S_U9*c_c^2*c_h*s_d^2*s_g + C_x13*S_U12*S_U9*c_d^2*c_g*s_c^2*s_h + C_x13*S_U12*S_U9*c_d^2*c_h*s_c^2*s_g + C_x13*S_U12*S_U9*c_g*s_c^2*s_d^2*s_h + C_x13*S_U12*S_U9*c_h*s_c^2*s_d^2*s_g + 1,   # F4
    C_U7*C_x7*c_d*c_g - C_U7*C_x7*s_d*s_g - 2*C_x7^2 + C_x7*S_U7*c_d*s_g + C_x7*S_U7*c_g*s_d + 1,   # F6
    -C_x18*S_x19 + C_x19*S_x18,   # F7
])

# Exact mixed volume (decisive path count for polyhedral homotopy):
mv = mixed_volume(F)
println("mixed_volume = ", mv)
println("n_vars = ", nvariables(F), "  n_eqs = ", length(expressions(F)))
