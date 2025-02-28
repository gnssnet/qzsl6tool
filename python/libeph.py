#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# libeph.py: library for RTCM ephemeride message processing
# A part of QZS L6 Tool, https://github.com/yoronneko/qzsl6tool
#
# Copyright (c) 2022-2024 Satoshi Takahashi
#
# Released under BSD 2-clause license.
#
# References:
# [1] Radio Technical Commission for Maritime Services (RTCM),
#     Differential GNSS (Global Navigation Satellite Systems) Services
#     - Version 3, RTCM Standard 10403.3, Apr. 24 2020.
# [2] Cabinet Office, Government of Japan, Quasi-Zenith Satellite System
#     Interface Specification Satellite Positioning, Navigation and Timing
#     Service, IS-QZSS-PNT-005, Oct. 2022.

# format definitions
FMT_IODC = '<4d'  # format string for issue of data clock
FMT_IODE = '<4d'  # format string for issue of data ephemeris

# constants
PI = 3.1415926535898            # Ratio of a circle's circumference
MU = 3.986004418  * (10**14)    # Geocentric gravitational constant [m^3/s^2]
OE = 7.2921151467 * (10**(-5))  # Mean angular velocity of the Earth [rad/s]
C  = 299792458                  # Speed of light [m/s]

class EphRaw:
    ''' raw ephemeris data '''
    svid  = 0  # satellite id, DF009
    wn    = 0  # week number, DF076
    sva   = 0  # space vehicle accuracy, DF077
    gpsc  = 0  # GPS code L2, DF078
    idot  = 0  # rate of change of inclination angle, DF079
    iode  = 0  # IODE, DF079
    toc   = 0  # t_oc, DF081
    af2   = 0  # SV clock drift rate correction coefficient, DF082
    af1   = 0  # SV clock drift correction coefficient, DF083
    af0   = 0  # SV clock bias correction coefficient, DF084
    iodc  = 0  # IODC, DF805
    crs   = 0  # sin harmonic correction term to the orbit radius, DF086
    dn    = 0  # mean motion difference from computed value, DF087
    m0    = 0  # mean anomaly at reference time, DF088
    cuc   = 0  # cos harmonic correction term to the argument of latitude, DF089
    e     = 0  # eccentricity, DF090
    cus   = 0  # sin harmonic correction term to the argument of latitude, DF091
    a12   = 0  # square root of the semi-major axis, DF092
    toe   = 0  # t_oe, DF093
    cic   = 0  # cos harmonic correction term to the angle of inclination, DF094
    omg0  = 0  # longitude of ascending node of orbital plane, DF095
    cis   = 0  # sin harmonic correction term to the angle of inclination, DF096
    i0    = 0  # inclination angle at reference time, DF097
    crc   = 0  # cos harmonic correction term to the orbit radius, DF098
    omg   = 0  # argument of perigee, DF099
    omgd  = 0  # rate of change of right ascension, DF100
    tgd   = 0  # t_GD, DF101
    svh   = 0  # SV health, DF102
    l2p   = 0  # P flag, DF103
    fi    = 0  # fit interval, DF137
# GLO
    fcn   = 0  # freq ch, DF040
    iodn  = 0  # IODnav, DF209
    sisa  = 0  # SIS Accuracy, DF291
    t0e   = 0  # ephemeris reference time
    t0c   = 0  # clock correction data reference TOW
    be5a  = 0  # E1-E5a broadcast group delay
    be5b  = 0  # E1-E5b broadcast group delay
    ai0   = 0  # effective ionisation level 1st order parameter
    ai1   = 0  # effective ionisation level 2nd order parameter
    a0    = 0  # constant term of polynomial
    a1    = 0  # 1st order term of polynomial
    dtls  = 0  # leap Second count before leap second adjustment
    t0t   = 0  # UTC data reference TOW
    wn0t  = 0  # UTC data reference week number
    wnlsf = 0  # week number of leap second adjustment
    dn    = 0  # day number at the end of which a leap second adjustment becomes effective
    dtlsf = 0  # leap second count after leap second adjustment
    a0g   = 0  # constant term of the polynomial describing the offset
    a1g   = 0  # rate of change of the offset
    t0g   = 0  # reference time for GGTO data
    wn0g  = 0  # week number of GGTO reference

class EphData:
    ''' ephemeris data '''
    def __init__(self, satsys, r=EphRaw()):
        '''
        returns decoded ephemeris data
        '''
        self.svid  = r.svid.u                # satellite id
        self.m0    = r.m0.i   * 2**(-31)*PI  # mean anomaly at reference time
        self.e     = r.e.u    * 2**(-33)     # eccentricity
        self.a12   = r.a12.u  * 2**(-19)     # square root of the semi-major axis
        self.t0e   = r.t0e.u  * 60           # ephemeris reference time
        self.omg0  = r.omg0.i * 2**(-31)*PI  # longitude of ascending node of orbital plane
        self.i0    = r.i0.i   * 2**(-31)*PI  # inclination angle at reference time
        self.omg   = r.omg.i  * 2**(-31)*PI  # argument of perigee
        self.idot  = r.idot.i * 2**(-43)*PI  # rate of change of inclination angle
        self.dn    = r.dn.i   * 2**(-43)*PI  # mean motion difference from computed value
        self.omgd  = r.omgd.i * 2**(-43)*PI  # rate of change of right ascension
        self.cuc   = r.cuc.i  * 2**(-29)     # cos harmonic correction term to the argument of latitude
        self.cus   = r.cus.i  * 2**(-29)     # sin harmonic correction term to the argument of latitude
        self.crc   = r.crc.i  * 2**(-5)      # cos harmonic correction term to the orbit radius
        self.crs   = r.crs.i  * 2**(-5)      # sin harmonic correction term to the orbit radius
        self.cic   = r.cic.i  * 2**(-29)     # cos harmonic correction term to the angle of inclination
        self.cis   = r.cis.i  * 2**(-29)     # sin harmonic correction term to the angle of inclination
        self.t0c   = r.t0c.u  * 60           # clock correction data reference TOW
        self.af0   = r.af0.i  * 2**(-34)     # SV clock bias correction coefficient
        self.af1   = r.af1.i  * 2**(-46)     # SV clock drift correction coefficient
        self.af2   = r.af2.i  * 2**(-59)     # SV clock drift rate correction coefficient
        self.be5a  = r.be5a.i * 2**(-32)     # E1-E5a broadcast group delay
        self.be5b  = r.be5b.i * 2**(-32)     # E1-E5b broadcast group delay
        self.ai0   = r.ai0.u  * 2**(-2)      # effective ionisation level 1st order parameter
        self.ai1   = r.ai1.i  * 2**(-8)      # effective ionisation level 2nd order parameter
        self.a0    = r.a0.i   * 2**(-30)     # constant term of polynomial
        self.a1    = r.a1.i   * 2**(-50)     # 1st order term of polynomial
        self.dtls  = r.dtls.i                # leap Second count before leap second adjustment
        self.t0t   = r.t0t.u                 # UTC data reference TOW
        self.wn0t  = r.wn0t.u                # UTC data reference week number
        self.wnlsf = r.wnlsf.u               # week number of leap second adjustment
        self.dn    = r.dn.u                  # day number at the end of which a leap second adjustment becomes effective
        self.dtlsf = r.dtlsf.i               # leap second count after leap second adjustment
        self.a0g   = r.a0g.i  * 2**(-35)     # constant term of the polynomial describing the offset
        self.a1g   = r.a1g.i  * 2**(-51)     # rate of change of the offset
        self.t0g   = r.t0g.u  * 3600         # reference time for GGTO data
        self.wn0g  = r.wn0g.u                # week number of GGTO reference

class Eph:
    ''' Ephemeris class '''
    def __init__(self, trace):
        self.trace = trace

    def decode_ephemerides(self, payload, satsys, mtype):
        ''' returns decoded ephemeris data '''
        r = EphRaw()
        msg = ''
        if satsys == 'G':  # GPS ephemerides
            r.svid = payload.read( 6).u  # satellite id, DF009
            r.wn   = payload.read(10).u  # week number, DF076
            r.sva  = payload.read( 4).u  # SV accuracy DF077
            r.gpsc = payload.read( 2)    # GPS code L2, DF078
            r.idot = payload.read(14).i  # IDOT, DF079
            r.iode = payload.read( 8).u  # IODE, DF071
            r.toc  = payload.read(16).u  # t_oc, DF081
            r.af2  = payload.read( 8).i  # a_f2, DF082
            r.af1  = payload.read(16).i  # a_f1, DF083
            r.af0  = payload.read(22).i  # a_f0, DF084
            r.iodc = payload.read(10).u  # IODC, DF085
            r.crs  = payload.read(16).i  # C_rs, DF086
            r.dn   = payload.read(16).i  # d_n,  DF087
            r.m0   = payload.read(32).i  # M_0,  DF088
            r.cuc  = payload.read(16).i  # C_uc, DF089
            r.e    = payload.read(32).u  # e,    DF090
            r.cus  = payload.read(16).i  # C_us, DF091
            r.a12  = payload.read(32).u  # a12,  DF092
            r.toe  = payload.read(16).u  # t_oe, DF093
            r.cic  = payload.read(16).i  # C_ic, DF094
            r.omg0 = payload.read(32).i  # Omg0, DF095
            r.cis  = payload.read(16).i  # C_is, DF096
            r.i0   = payload.read(32).i  # i_0,  DF097
            r.crc  = payload.read(16).i  # C_rc, DF098
            r.omg  = payload.read(32).i  # omg,  DF099
            r.omgd = payload.read(24).i  # Omg-dot, DF100
            r.tgd  = payload.read( 8).i  # t_GD, DF101
            r.svh  = payload.read( 6).u  # SV health, DF102
            r.l2p  = payload.read( 1).u  # P flag, DF103
            r.fi   = payload.read( 1).u  # fit interval, DF137
            msg += f'G{r.svid:02d} WN={r.wn} IODE={r.iode:{FMT_IODE}} IODC={r.iodc:{FMT_IODC}}'
            if   r.gpsc == '0b01': msg += ' L2P'
            elif r.gpsc == '0b10': msg += ' L2C/A'
            elif r.gpsc == '0b11': msg += ' L2C'
            else: msg += f'unknown L2 code: {r.gpsc}'
            if r.svh:
                msg += self.trace.msg(0, f' unhealthy({r.svh:02x})', fg='red')
        elif satsys == 'R':  # GLONASS ephemerides
            r.svid  = payload.read( 6).u  # satellite id, DF038
            r.fcn   = payload.read( 5).u  # freq ch, DF040
            r.svh   = payload.read( 1).u  # alm health DF104
            r.aha   = payload.read( 1).u  # alm health avail, DF105
            r.p1    = payload.read( 2).u  # P1, DF106
            r.tk    = payload.read(12)  # t_k, DF107
            r.bn    = payload.read( 1).u  # B_n word MSB, DF108
            r.p2    = payload.read( 1).u  # P2, DF109
            r.tb    = payload.read( 7).u  # t_b, DF110
            _sgn    = payload.read( 1).u  # x_n dot, DF111
            r.xnd   = payload.read(23).u
            if _sgn: r.xnd = -r.xnd
            _sgn    = payload.read( 1).u  # x_n, DF112
            r.xn    = payload.read(26).u
            if _sgn: r.xn = -r.xn
            _sgn    = payload.read( 1).u  # x_n dot^2, DF113
            r.xndd  = payload.read( 4).u
            if _sgn: r.xndd = -r.xndd
            _sgn    = payload.read( 1).u  # y_n dot, DF114
            r.ynd   = payload.read(23).u
            if _sgn: r.ynd = -r.ynd
            _sgn    = payload.read( 1).u  # y_n, DF115
            r.yn    = payload.read(26).u
            if _sgn: r.yn = -r.yn
            _sgn    = payload.read( 1).u  # y_n dot^2, DF116
            r.yndd  = payload.read( 4).u
            if _sgn: r.yndd = -r.yndd
            _sgn    = payload.read( 1).u  # z_n dot, DF117
            r.znd   = payload.read(23).u
            if _sgn: r.znd = -r.znd
            _sgn    = payload.read( 1).u  # z_n, DF118
            r.zn    = payload.read(26).u
            if _sgn: r.zn = -r.zn
            _sgn    = payload.read( 1).u  # z_n dot^2, DF119
            r.zndd  = payload.read( 4).u
            if _sgn: r.zndd = -r.zndd
            r.p3    = payload.read( 1).u  # P3, DF120
            _sgn    = payload.read( 1).u  # gamma_n, DF121
            r.gmn   = payload.read(10).u
            if _sgn: r.gmn = -r.gmn
            r.p     = payload.read( 2)  # P, DF122
            r.in3   = payload.read( 1).u  # I_n, DF123
            _sgn    = payload.read( 1).u  # tau_n, DF124
            r.taun  = payload.read(21).u
            if _sgn: r.taun = -r.taun
            _sgn    = payload.read( 1).u  # d_tau_n, DF125
            r.dtaun = payload.read( 4).u
            if _sgn: r.dtaun = -r.dtaun
            r.en    = payload.read( 5).u  # E_n, DF126
            r.p4    = payload.read( 1).u  # P4, DF127
            r.ft    = payload.read( 4).u  # F_t, DF128
            r.nt    = payload.read(11).u  # N_t, DF129
            r.m     = payload.read( 2)  # M, DF130
            r.add   = payload.read( 1).u  # addition, DF131
            r.na    = payload.read(11).u  # N^A, DF132
            _sgn    = payload.read( 1).u  # tau_c, DF133
            r.tauc  = payload.read(31).u
            if _sgn: r.tauc = -r.tauc
            r.n4    = payload.read( 5).u  # N_4, DF134
            _sgn    = payload.read( 1).u  # tau_GPS, DF135
            r.tgps  = payload.read(21).u
            if _sgn: r.tgps = -r.tgps
            r.in5   = payload.read( 1).u  # I_n, DF136
            payload.pos +=  7              # reserved
            msg += f'R{r.svid:02d} f={r.fcn:02d} tk={r.tk[7:12].u:02d}:{r.tk[1:7].u:02d}:{r.tk[0:2].u*15:02d} tb={r.tb*15}min'
            if r.svh:
                msg += self.trace.msg(0, ' unhealthy', fg='red')
        elif satsys == 'E':  # Galileo ephemerides
            r.svid  = payload.read( 6).u  # satellite id, DF252
            r.wn    = payload.read(12).u  # week number, DF289
            r.iodn  = payload.read(10).u  # IODnav, DF290
            r.sisa  = payload.read( 8).u  # SIS Accuracy, DF291
            r.idot  = payload.read(14).i  # IDOT, DF292
            r.toc   = payload.read(14).u  # t_oc, DF293
            r.af2   = payload.read( 6).i  # a_f2, DF294
            r.af1   = payload.read(21).i  # a_f1, DF295
            r.af0   = payload.read(31).i  # a_f0, DF296
            r.crs   = payload.read(16).i  # C_rs, DF297
            r.dn    = payload.read(16).i  # delta n, DF298
            r.m0    = payload.read(32).i  # M_0, DF299
            r.cuc   = payload.read(16).i  # C_uc, DF300
            r.e     = payload.read(32).u  # e, DF301
            r.cus   = payload.read(16).i  # C_us, DF302
            r.a12   = payload.read(32).u  # sqrt_a, DF303
            r.toe   = payload.read(14).u  # t_oe, DF304
            r.cic   = payload.read(16).i  # C_ic, DF305
            r.omg0  = payload.read(32).i  # Omega_0, DF306
            r.cis   = payload.read(16).i  # C_is, DF307
            r.i0    = payload.read(32).i  # i_0, DF308
            r.crc   = payload.read(16).i  # C_rc, DF309
            r.omg   = payload.read(32).i  # omega, DF310
            r.omgd0 = payload.read(24).i  # Omega-dot0, DF311
            r.be5a  = payload.read(10).i  # BGD_E5aE1, DF312
            if   mtype == 'F/NAV':
                r.osh = payload.read(2).u  # open signal health DF314
                r.osv = payload.read(1).u  # open signal valid DF315
                payload.pos += 7            # reserved, DF001
            elif mtype == 'I/NAV':
                r.be5b = payload.read(10).i  # BGD_E5bE1 DF313
                r.e5h  = payload.read( 2).u  # E5b signal health, DF316
                r.e5v  = payload.read( 1).u  # E5b data validity, DF317
                r.e1h  = payload.read( 2).u  # E1b signal health, DF287
                r.e1v  = payload.read( 1).u  # E1b data validity, DF288
                payload.pos += 2              # reserved, DF001
            else:
                raise Exception(f'unknown Galileo nav message: {mtype}')
            msg += f'E{r.svid:02d} WN={r.wn} IODnav={r.iodn}'
            if   mtype == 'F/NAV':
                if r.osh:
                    msg += self.trace.msg(0, f' unhealthy OS ({r.osh})', fg='red')
                if r.osv:
                    msg += self.trace.msg(0, ' invalid OS', fg='red')
            elif mtype == 'I/NAV':
                if r.e5h:
                    msg += self.trace.msg(0, f' unhealthy E5b ({r.e5h})', fg='red')
                if r.e5v:
                    msg += self.trace.msg(0, ' invalid E5b', fg='red')
                if r.e1h:
                    msg += self.trace.msg(0, f' unhealthy E1b ({r.e1h})', fg='red')
                if r.e1v:
                    msg += self.trace.msg(0, ' invalid E1b', fg='red')
            else:
                raise Exception(f'unknown Galileo nav message: {mtype}')
        elif satsys == 'J':  # QZSS ephemerides
            r.svid = payload.read( 4).u  # satellite id, DF429
            r.toc  = payload.read(16).u  # t_oc, DF430
            r.af2  = payload.read( 8).i  # a_f2, DF431
            r.af1  = payload.read(16).i  # a_f1, DF432
            r.af0  = payload.read(22).i  # a_f0, DF433
            r.iode = payload.read( 8).u  # IODE, DF434
            r.crs  = payload.read(16).i  # C_rs, DF435
            r.dn0  = payload.read(16).i  # delta n_0, DF436
            r.m0   = payload.read(32).i  # M_0, DF437
            r.cuc  = payload.read(16).i  # C_uc, DF438
            r.e    = payload.read(32).u  # e, DF439
            r.cus  = payload.read(16).i  # C_uc, DF440
            r.a12  = payload.read(32).u  # sqrt_A, DF441
            r.toe  = payload.read(16).u  # t_oe, DF442
            r.cic  = payload.read(16).i  # C_ic, DF443
            r.omg0 = payload.read(32).i  # Omg_0, DF444
            r.cis  = payload.read(16).i  # C_is, DF445
            r.i0   = payload.read(32).i  # i_0, DF446
            r.crc  = payload.read(16).i  # C_rc, DF447
            r.omgn = payload.read(32).i  # omg_n, DF448
            r.omgd = payload.read(24).i  # Omg dot, DF449
            r.i0d  = payload.read(14).i  # i0 dot, DF450
            r.l2   = payload.read( 2).u  # L2 code, DF451
            r.wn   = payload.read(10).u  # week number, DF452
            r.ura  = payload.read( 4).u  # URA, DF453
            r.svh  = payload.read( 6)  # SVH, DF454
            r.tgd  = payload.read( 8).i  # T_GD, DF455
            r.iodc = payload.read(10).u  # IODC, DF456
            r.fi   = payload.read( 1).u  # fit interval, DF457
            msg += f'J{r.svid:02d} WN={r.wn} IODE={r.iode:{FMT_IODE}} IODC={r.iodc:{FMT_IODC}}'
            if (r.svh[0:1]+r.svh[2:5]).u:  # determination of QZSS health including L1C/B is complex, ref.[2], p.47, 4.1.2.3(4)
                unhealthy = ''
                if r.svh[1]: unhealthy += ' L1C/A'
                if r.svh[2]: unhealthy += ' L2C'
                if r.svh[3]: unhealthy += ' L5'
                if r.svh[4]: unhealthy += ' L1C'
                if r.svh[5]: unhealthy += ' L1C/B'
                msg += self.trace.msg(0, f' unhealthy ({unhealthy[1:]})', fg='red')
            elif not r.svh[0]:                # L1 signal is healthy
                if r.svh[1]: msg += ' L1C/B'  # transmitting L1C/B
                if r.svh[5]: msg += ' L1C/A'  # transmitting L1C/A
        elif satsys == 'C':  # BeiDou ephemerides
            r.svid = payload.read( 6).u  # satellite id, DF488
            r.wn   = payload.read(13).u  # week number, DF489
            r.urai = payload.read( 4).u  # URA, DF490
            r.idot = payload.read(14).i  # IDOT, DF491
            r.aode = payload.read( 5).u  # AODE, DF492
            r.toc  = payload.read(17).u  # t_oc, DF493
            r.a2   = payload.read(11).i  # a_2, DF494
            r.a1   = payload.read(22).i  # a_1, DF495
            r.a0   = payload.read(24).i  # a_0, DF496
            r.aodc = payload.read( 5).u  # AODC, DF497
            r.crs  = payload.read(18).i  # C_rs, DF498
            r.dn   = payload.read(16).i  # delta n, DF499
            r.m0   = payload.read(32).i  # M_0, DF500
            r.cuc  = payload.read(18).i  # C_uc, DF501
            r.e    = payload.read(32).u  # e, DF502
            r.cus  = payload.read(18).i  # C_us, DF503
            r.a12  = payload.read(32).u  # sqrt_a, DF504
            r.toe  = payload.read(17).u  # t_oe, DF505
            r.cic  = payload.read(18).u  # C_ic, DF506
            r.omg0 = payload.read(32).i  # Omg_0, DF507
            r.cis  = payload.read(18).i  # C_is, DF508
            r.i0   = payload.read(32).i  # i_0, DF509
            r.crc  = payload.read(18).i  # C_rc, DF510
            r.omg  = payload.read(32).i  # omg, DF511
            r.omgd = payload.read(24).i  # Omg dot, DF512
            r.tgd1 = payload.read(10).i  # T_GD1, DF513
            r.tgd2 = payload.read(10).i  # T_GD2, DF514
            r.svh  = payload.read( 1).u  # SVH, DF515
            msg +=f'C{r.svid:02d} WN={r.wn} AODE={r.aode}'
            if r.svh:
                msg += self.trace.msg(0, ' unhealthy', fg='red')
        elif satsys == 'I':  # NavIC ephemerides
            r.svid  = payload.read( 6).u  # satellite id, DF516
            r.wn    = payload.read(10).u  # week number, DF517
            r.af0   = payload.read(22).i  # a_f0, DF518
            r.af1   = payload.read(16).i  # a_f1, DF519
            r.af2   = payload.read( 8).i  # a_f2, DF520
            r.ura   = payload.read( 4).u  # URA, DF521
            r.toc   = payload.read(16).u  # t_oc, DF522
            r.tgd   = payload.read( 8).i  # t_GD, DF523
            r.dn    = payload.read(22).i  # delta n, DF524
            r.iodec = payload.read( 8).u  # IODEC, DF525
            payload.pos += 10              # reserved, DF526
            r.hl5   = payload.read( 1).u  # L5_flag, DF527
            r.hs    = payload.read( 1).u  # S_flag, DF528
            r.cuc   = payload.read(15).i  # C_uc, DF529
            r.cus   = payload.read(15).i  # C_us, DF530
            r.cic   = payload.read(15).i  # C_ic, DF531
            r.cis   = payload.read(15).i  # C_is, DF532
            r.crc   = payload.read(15).i  # C_rc, DF533
            r.crs   = payload.read(15).i  # C_rs, DF534
            r.idot  = payload.read(14).i  # IDOT, DF535
            r.m0    = payload.read(32).i  # M_0, DF536
            r.toe   = payload.read(16).u  # t_oe, DF537
            r.e     = payload.read(32).u  # e, DF538
            r.a12   = payload.read(32).u  # sqrt_A, DF539
            r.omg0  = payload.read(32).i  # Omg0, DF540
            r.omg   = payload.read(32).i  # omg, DF541
            r.omgd  = payload.read(22).i  # Omg dot, DF542
            r.i0    = payload.read(32).i  # i0, DF543
            payload.pos += 2               # spare, DF544
            payload.pos += 2               # spare, DF545
            msg += f'I{r.svid:02d} WN={r.wn} IODEC={r.iodec:{FMT_IODE}}'
            if r.hl5 or r.hs:
                msg += self.trace.msg(0, f" unhealthy{' L5' if r.hl5 else ''}{' S' if r.hs else ''}", fg='red')
        else:
            raise Exception(f'unknown satsys({satsys})')
        return msg

class Alm:
    ''' Almanac class '''
    pass

# EOF
