# Copyright (C) 2014, 2015 Luke Kenneth Casson Leighton <lkcl@lkcl.net>
# License: GPLv3+

import time
import itertools
from pyopenscad import *
from polysurface import spline_double_divide, Offset, SurfaceFromCurves
from copy import deepcopy
from pyscadutil import B0, B45, pin, shearedcube, hollowbox, touch_arc
from pyscadutil import L, R, T, D, F, B

pin_parts_3d=False

test = True
single = True


if not test:
    lcd_l = 3598.0
    lcd_w = 2100.0
    lcd_la = lcd_l-98.0
    lcd_wa = lcd_w-129.9
    lcd_d = 50
else:
    # HSD070PWW1
    lcd_l = 1612
    lcd_w = 1055
    # HSD101PWW1
    #lcd_l = 2294.6
    #lcd_w = 1492.0
    lcd_la = lcd_l-104.8+40
    lcd_wa = lcd_w-113.0+40
    lcd_d = 50

lcd_doff = 5
scl = 0.1
hthick = 12 # horizontal pieces not as thick
bwid = 17 # 24
lcd_inset_top = 25
lcd_inset_bot = 200
lcd_gap = 3
lcd_hinge_inner_rad=70
lcd_hinge_inside_rad=70
lcd_ext_rot_angle=250
lcd_outer_rad = lcd_hinge_inner_rad+bwid
lcd_end_ht = 20 # 40
lcd_end_offs = 20

lcdscrewrad = 29 / 2.0 # XXX: 2mm diameter thread, why 0.9mm extra????
screwrad = 32 / 2.0 # XXX: 2mm thread diameter, needs 1.2mm extra!!!
topscrewrad = 20 / 2.0 # supposed to be 3mm screw holes but 3d baaad....
boxheight = 140
backboxheight = boxheight+bwid*2-10
boxtopoffs = 2
boxinset = 55
hinge_depth = 70
hole_depth = hinge_depth
boxlength = lcd_w + lcd_inset_top + lcd_inset_bot + lcd_d-20
lidfront_offs = 10
lcd_front_indent = 108

bdep = 325
fdep = 300
ethdep = 160
bdepoffs = 15
csw = 55.0 # centre support width (for screws to go into)

bbcutout_dep = bdep-50
bbcutout_wid = 130

paneldepth = 190
pdept =  130

def hinge_translate(scl):
    return translate(v=[+(+lcd_inset_bot+lcd_w+63-lcd_gap)*scl,
                       0,
                        (30-lcd_d+lcd_hinge_inner_rad)*scl])

def hinge_rotate(scl, o, angle):
    u = union()
    t = hinge_translate(-scl).add(o)
    t = rotate([0, -angle, 0]).add(t)
    t = hinge_translate(scl).add(t)
    return t

hinge_x = -20
hinge_y = -20

def ethernet(scl):
    # ethernet, amphenol RJCSE-538X-01
    eth = cube([157.5*scl, 165.5*scl, (134.8+13.0)*scl])
    return translate(v=[(lcd_w+190)*scl,130*scl,(4+23)*scl]).add(eth)

def lcd_panel(scl, offs=0):

    w = lcd_w
    h = lcd_l
    d = lcd_d

    a = union()

    r = union()
    c = cube(size=[(w+offs*2)*scl,(h+offs*2)*scl,(d+offs*2)*scl])
    c = rotate([00, 0, 0 ]).add(c)
    r.add(c)
    t = translate(v=[(-93-offs)*scl, (-40-offs)*scl, (lcd_doff+29.5-d-offs)*scl])
    t.add(r)
    a.add(t)

    return a

def lcd_view_area(scl, offs=0):

    shear = 0
    innershear = 0
    w = lcd_wa
    h = lcd_la
    d = lcd_d

    wo = (lcd_w - lcd_wa) / 2
    do = (lcd_l - lcd_la) / 2

    a = union()

    r = union()
    c = cube(size=[(w+offs*2)*scl,(h+offs*2)*scl,(d+offs*2)*scl])
    c = rotate([00, 0, 0 ]).add(c)
    r.add(c)
    t = translate(v=[(-93-offs+wo)*scl, (-40-offs+do)*scl, (32.5-offs)*scl])
    t.add(r)
    a.add(t)

    return a

def case_bolthole(scl, end):
    bht = lcd_hinge_inner_rad+boxtopoffs-20-lcd_d
    if end == 0:
        return translate([(29.0+140-lcd_d-lcd_inset_top+6)*scl, 0*scl, bht*scl])
    elif end == 1:
        return translate([(-10+lcd_w+11)*scl, 0*scl, bht*scl])
    elif end == 2:
        return translate([(lcd_w+lcd_inset_bot-95)*scl, 0*scl,
                            (-lcd_d+135+boxtopoffs-boxheight)*scl])
    elif end == 3:
        return translate([(-20+lcd_w/2.0+30)*scl, 0*scl, bht*scl])

def lid_bolthole(scl, end=True):
    if end:
        return translate([(-lcd_inset_top+58)*scl, 0*scl, (16+lcd_doff)*scl])
    else:
        return translate([(100+lcd_w)*scl, 0*scl, (16+lcd_doff)*scl])

def screen_mid3(scl, ht, hole_ht, nohinge=True, endpart=True):
    """
        TODO:
        * middle join part not quite right (too low, too long)
    """

    w = lcd_w+lcd_inset_top+lcd_inset_bot-200
    iro = 0
    shear = 0
    innershear = 0
    edge_inset = bwid
    a = union()

    # top edge
    toplen = w+lcd_gap*2-180
    toplenoffs = (-lcd_inset_top+w+75)
    r = union()
    c = shearedcube(size=[(bwid+iro)*scl,toplen*scl,ht*scl],
                shear=[-shear*scl, 0, 0],
                innershear=[-innershear*scl, 0, 0])
    c = rotate([0, 90, 90]).add(c)
    r.add(c)
    t = translate(v=[toplenoffs*scl, (16.5-ht)*scl, (30-lcd_d)*scl])
    t.add(r)
    a.add(t)

    a = translate(v=[0, (ht-edge_inset)*scl, 0]).add(a)
    a += screen_mid2(scl, ht, hole_ht)
    a += screen_mid1(scl, ht, hole_ht, nohinge=True, endpart=True)
    return a

def screen_mid2(scl, ht, hole_ht, endpart=True,
                removemiddle=True, cableduct=False):

    shear = 0
    innershear = 0
    w = lcd_w+lcd_inset_top+lcd_inset_bot
    edge_inset = bwid
    iro = 0

    rad = 15

    a = union()

    toplen = 180 if test else 250
    toplenoffs = (w-lcd_inset_top)

    # top and bottom edge
    a += screen_frontedge(scl, ht, 80, toplenoffs,
                               curvefront=False, curvetopback=True,
                               indent=[0], outdent=[0])

    # add hinge-end filler over top of screwhole
    a.add(lcd_hinge_filler(scl, ht, cableduct))

    a.add(lid_bottom_boltholder(scl, lcd_gap, ht, iro))

    if removemiddle:
        # top edge
        r = union()
        c = shearedcube(size=[(bwid*3+iro)*scl,
                            (w-toplen-lcd_inset_top-lcd_inset_bot-80)*scl,
                            (ht+2)*scl],
                    shear=[-shear*scl, 0, 0],
                    innershear=[-innershear*scl, 0, 0])
        c = rotate([0, 90, 90]).add(c)
        r.add(c)
        t = translate(v=[(w-lcd_inset_bot-lcd_inset_top-80)*scl,
                        (16.5-ht-1)*scl, (lcd_doff-bwid)*scl])
        t.add(r)
        a -= t
    # screw holes through lid
    a -= lid_screwholes(scl, edge_inset)

    if pin_parts_3d:
        c = union()
        h = pin(B0)
        h = translate([(w-348)*scl, (13.5)*scl, -5*scl]).add(h)
        c += h
        c = translate([0, (-ht+6)*scl, 0*scl]).add(c)
        a += c

    a = translate(v=[0, (ht-edge_inset)*scl, 0]).add(a)
    return a

def lid_bottom_boltholder(scl, lcd_gap, ht, iro, extra=0):
    shear = 0
    innershear = 0

    a = union()

    # bottom edge bolt holder
    r = union()
    c = cylinder(r=24*scl, h=ht*scl, segments=50)
    c = rotate([0, 90, 90]).add(c)
    r.add(c)
    t = translate(v=[(0)*scl, (16.5-ht)*scl, (0)*scl]).add(r)
    t = lid_bolthole(scl, end=False).add(t)
    a.add(t)
    r = union()
    c = shearedcube(size=[(bwid+5+iro)*scl,(60+extra+lcd_gap*2)*scl,ht*scl],
                shear=[-shear*scl, 0, 0],
                innershear=[-innershear*scl, 0, 0])
    c = rotate([0, 90, 90]).add(c)
    r.add(c)
    t = translate(v=[(40+extra)*scl, (16.5-ht)*scl, (25)*scl]).add(r)
    t = lid_bolthole(scl, end=False).add(t)
    a.add(t)

    return a

def screen_frontedge(scl, ht, extralen, toplenoffs,
                            curvefront=True, curvetopback=False,
                            edge=False,
                            frontonly=False,
                            indent=None,
                            indent2=None,
                            outdent=None):
    shear = 0
    innershear = 0
    edge_inset = bwid
    iro = 0

    rad = 15
    rad2 = 2
    a = union()
    if indent2 is None:
        indent2 = []
    if indent is None:
        indent = []
    if outdent is None:
        outdent = []

    if curvetopback or frontonly:
        to = toplenoffs-40
    else:
        to = toplenoffs

    curverads={}
    if not frontonly:
       curverads[D|R] = (bwid+lcd_gap+2, bwid*2-2)
    if edge:
        curverads[B|T] = (bwid, 0)
    if curvefront:
        curverads[L|T] = (lcd_d+bwid+5, 0)
        curverads[L|D] = (hthick, 0)
        offs = 0
    else:
        to -= lcd_w
        offs = lcd_w
    if curvetopback and not frontonly:
        curverads[T|R] = (bwid+5, 0)
    ld = lcd_d+18+hthick+lcd_gap*2
    c = union()
    b = hollowbox(scl, to+15+extralen, ht, ld,
                    {T:bwid, B: -1,
                    L:80, R:22, F:-1, D:hthick},
                    curverads=curverads)
    c.add(b)
    for ind in indent:
        # remove a matching part to clip
        o = shearedcube(size=[62*scl,
                        25*scl,(bwid+2)*scl],
                    shear=[0, 0*scl, 0],
                    innershear=[0, -20*scl, 0])
        #o = rotate([0, 0, 180]).add(o)
        t = translate(v=[(60+ind)*scl, (-11)*scl,
                        (-1)*scl])
        t.add(o)
        c -= t
        o = shearedcube(size=[63*scl,
                        25*scl,(bwid+3)*scl],
                    shear=[0, 0*scl, 0],
                    innershear=[0, -20*scl, 0])
        o = rotate([0, 180, 0]).add(o)
        t = translate(v=[(62+ind)*scl, (-11)*scl,
                        (bwid+2)*scl])
        t.add(o)
        c -= t

    for out in outdent:
        # add a tiny clip which locks into the next part
        o = shearedcube(size=[55*scl,
                        25*scl,(bwid)*scl],
                    shear=[0, 0*scl, 0],
                    innershear=[0, -17*scl, 0])
        #o = rotate([0, 0, 180]).add(o)
        t = translate(v=[(64+out)*scl, (ht-14)*scl,
                        (0)*scl])
        t.add(o)
        c += t
        o = shearedcube(size=[57*scl,
                        25*scl,(bwid)*scl],
                    shear=[0, 0*scl, 0],
                    innershear=[0, -17*scl, 0])
        o = rotate([0, 180, 0]).add(o)
        t = translate(v=[(57+out)*scl, (ht-14)*scl,
                        (bwid)*scl])
        t.add(o)
        c += t

    for ind in indent2:
        # remove a matching part to clip, for screen_mid3
        o = shearedcube(size=[62*scl,
                        25*scl,(bwid+2)*scl],
                    shear=[0, 0*scl, 0],
                    innershear=[0, -20*scl, 0])
        o = rotate([0, 0, 180]).add(o)
        t = translate(v=[(122+ind)*scl, (ht+11)*scl,
                        (-1)*scl])
        t.add(o)
        c -= t
        o = shearedcube(size=[63*scl,
                        25*scl,(bwid+3)*scl],
                    shear=[0, 0*scl, 0],
                    innershear=[0, -20*scl, 0])
        o = rotate([0, 0, 180]).add(o)
        o = rotate([0, 180, 0]).add(o)
        t = translate(v=[(-1+ind)*scl, (ht+11)*scl,
                        (bwid+2)*scl])
        t.add(o)
        c -= t

    c = translate(v=[(offs-extralen)*scl, (16.5-ht)*scl,
                    (lcd_doff+12-lcd_d-lcd_gap)*scl]).add(c)
    a.add(c)

    return a

def lcd_hinge_filler(scl, ht, cableduct):
    fillerht = (lcd_d+10+lcd_gap*2)
    if cableduct:
        fillerht -= 20

    r = union()
    c = cube(size=[fillerht*scl,(lcd_gap*2+bwid+5)*scl,ht*scl])
    c = rotate([0, 90, 90]).add(c)
    r.add(c)
    t = translate(v=[(+lcd_inset_bot+lcd_w-110)*scl,
                        (16.5-ht)*scl, (lcd_doff+37+lcd_gap)*scl])
    t.add(r)

    return t

def screen_mid1(scl, ht, hole_ht, nohinge=False, endpart=False,
                        halfhollow=False, fillinner=False,
                        indent=None, outdent=None,
                        cableduct=False, extra=None):
    """
        TODO: 
        * thin down edge from bwid to hthick at hinge end for cable duct
    """

    shear = 0
    innershear = 0
    w = lcd_w+lcd_inset_top+lcd_inset_bot
    edge_inset = bwid
    iro = 0

    rad = 15

    a = union()

    if endpart:
        toplen = 140 if test else 200
        toplenoffs = (toplen-131+165)+40

    else:
        toplen = w+lcd_gap*2
        toplenoffs = (-lcd_inset_top+w+65)+30
    extralen = 0
    if nohinge and not endpart:
        extralen = 80

    # top and bottom edge
    a += screen_frontedge(scl, ht, extralen, toplenoffs,
                curvefront=not fillinner,
                curvetopback=not (nohinge and endpart),
                indent=indent, outdent=outdent)

    if not endpart:
        if extra is None:
            extra = 30 if fillinner else 0
    if extra is not None:
        a.add(lid_bottom_boltholder(scl, lcd_gap, ht, iro, extra=extra))

    if endpart:
        # middle filler
        r = union()
        c = shearedcube(size=[(lcd_d+lcd_gap*2)*scl,toplen*scl,ht*scl],
                    shear=[-shear*scl, 0, 0],
                    innershear=[-innershear*scl, 0, 0])
        c = rotate([0, 90, 90]).add(c)
        r.add(c)
        t = translate(v=[toplenoffs*scl, (16.5-ht)*scl,
                    (lcd_doff+30+lcd_gap)*scl])
        t.add(r)
        a.add(t)

    if fillinner:
        # add hinge-end filler over top of screwhole
        c = shearedcube(size=[70*scl,
                        bwid*scl,(lcd_d+10+lcd_gap*2)*scl],
                    shear=[-shear*scl, 0, 0],
                    innershear=[-innershear*scl, 0, 0])
        t = translate(v=[(+lcd_inset_bot+lcd_w-34)*scl, (-0.5)*scl,
                        (lcd_doff-26)*scl])
        t.add(c)
        a.add(t)

    if halfhollow:
        # add a tiny clip which locks into the screen end part
        c = shearedcube(size=[32*scl,
                        40*scl,(15)*scl],
                    shear=[0, -10*scl, ],
                    innershear=[0,0,0])
        c = rotate([180, 0, 0]).add(c)
        t = translate(v=[(+lcd_inset_bot+lcd_w-59)*scl, (30)*scl,
                        (lcd_doff+32)*scl])
        t.add(c)
        a.add(t)

    if not endpart:
        # add hinge-end filler over top of screwhole
        a.add(lcd_hinge_filler(scl, ht, cableduct))

        # bottom end curve (1st)
        r = touch_arc(lcd_hinge_inner_rad, ht, bwid, 30, scl)
        r = rotate([180, 90, 90]).add(r)
        r = rotate([0, -30, 0]).add(r)
        r = rotate([0, lcd_ext_rot_angle+20, 0]).add(r)
        t = translate(v=[+(-lcd_inset_top+w+63-lcd_gap)*scl, (-ht+24-7.5)*scl,
                        (30-lcd_d+lcd_hinge_inner_rad)*scl]).add(r)
        a.add(t)

        # bottom end curve, overlap with 1st
        r = touch_arc(lcd_hinge_inner_rad, ht, bwid, 30, scl)
        r = rotate([180, 90, 90]).add(r)
        r = rotate([0, 10, 0]).add(r)
        r = rotate([0, lcd_ext_rot_angle+5, 0]).add(r)
        t = translate(v=[+(-lcd_inset_top+w+63-lcd_gap)*scl, (-ht+24-7.5)*scl,
                        (30-lcd_d+lcd_hinge_inner_rad)*scl]).add(r)
        a.add(t)

    if not nohinge:
        # outer surround
        r = cylinder(r=(lcd_hinge_inner_rad+bwid)*scl, h=(hole_ht)*scl,
                     segments=50, center=True)
        r = rotate([180, 90, 90]).add(r)
        t = translate(v=[+(-lcd_inset_top+w+63-lcd_gap)*scl,
                         (-ht+hole_ht/2+16.5)*scl,
                         (30-lcd_d+lcd_hinge_inner_rad)*scl]).add(r)
        a += t

        # hole for cable
        r = touch_arc(lcd_hinge_inner_rad+5, hinge_depth+ht, bwid,
                        lcd_hinge_inner_rad, scl,
                      angle=64)
        r = rotate([180, 90, 90]).add(r)
        r = rotate([0, lcd_ext_rot_angle+3, 0]).add(r)
        t = hinge_translate(scl).add(r)
        t = translate(v=[0, -(hole_ht+ht/2-7.5)*scl, 0]).add(t)
        a -= t
        r = cube([70*scl, (hinge_depth+ht)*scl, 50*scl])
        t = hinge_translate(scl).add(r)
        t = translate(v=[-lcd_hinge_inner_rad*scl, -(hole_ht+ht/2-7.5)*scl, (-lcd_hinge_inner_rad+1)*scl]).add(t)
        a -= t

    if halfhollow:
        hrad = lcd_hinge_inside_rad-8
    else:
        hrad = lcd_hinge_inside_rad
    # hinge hole
    r = union()
    r = cylinder(r=hrad*scl,
                        h=(ht+90+0.3)*scl, segments=50, center=True)
    r = rotate([180, 90, 90]).add(r)
    t = hinge_translate(scl).add(r)
    t = translate(v=[0, (-ht/2+28.5)*scl, 0]).add(t)
    a -= t
    if halfhollow:
        # hinge hole inset against base hinge part, only we have
        # to take a tiny bit out of it for the cable
        r = union()
        r = cylinder(r=lcd_hinge_inside_rad*scl,
                            h=(ht)*scl, segments=50, center=True)
        r = rotate([180, 90, 90]).add(r)
        t = hinge_translate(scl).add(r)
        t = translate(v=[0, (-ht/2+65)*scl, 0]).add(t)
        a -= t

    # screw holes through lid
    a -= lid_screwholes(scl, edge_inset)

    a = translate(v=[0, (ht-edge_inset)*scl, 0]).add(a)
    return a

def friction_hinge_inner(scl, ht):

    a = union()
    hht = 40

    # outer disc
    r = union()
    c = cylinder(r=47*scl,
                        h=(hht)*scl, segments=50, center=True)
    c = rotate([180, 90, 90]).add(c)
    r.add(c)
    # cutout to match with inset in the wall, stops the friction hinge turning
    for ang in [0, 180]:
        c = touch_arc(lcd_hinge_inner_rad-20, 60, bwid,
                            13, scl,
                      angle=58)
        c = rotate([180, 90, 90]).add(c)
        c = rotate([0, lcd_ext_rot_angle+221+ang, 0]).add(c)
        c = translate(v=[0, (-55)*scl, 0]).add(c)
        r -= c
    # cutout for the cable
    c = touch_arc(lcd_hinge_inner_rad-20, 60, bwid,
                        25, scl,
                  angle=0)
    c = rotate([0, 90, 90]).add(c)
    c = rotate([0, lcd_ext_rot_angle+223+210, 0]).add(c)
    c = translate(v=[0, (24)*scl, 0]).add(c)
    r -= c
    c = touch_arc(lcd_hinge_inner_rad-20, 60, bwid,
                        25, scl,
                  angle=0)
    c = rotate([0, 90, 90]).add(c)
    c = rotate([0, lcd_ext_rot_angle+223+205, 0]).add(c)
    c = translate(v=[0, (26)*scl, 0]).add(c)
    r -= c
    t = hinge_translate(scl).add(r)
    t = translate(v=[0, (-ht/2+27.5-bwid)*scl, 0]).add(t)
    a += t

    # hinge hole
    r = union()
    r = cylinder(r=(screwrad-3)*scl, h=(ht*5+0.3)*scl, segments=50, center=True)
    r = rotate([180, 90, 90]).add(r)
    t = hinge_translate(scl).add(r)
    t = translate(v=[0, (-ht/2+16.5)*scl, 0]).add(t)
    a -= t

    return a

def box_screwholes(scl, edge_inset, holes=None, h=lcd_l*2+100):
    u = union()

    if holes is None:
        holes = range(3 if test else 4)
    for i in holes:
        t = case_bolthole(scl, i)
        r = cylinder(r=screwrad*scl, h=h*scl, segments=50, center=True)
        r = rotate([90, 0, 0]).add(r)
        r = translate(v=[0, h*0.25*scl, 0]).add(r)
        t.add(r)
        u += t

    return u

def lid_screwholes(scl, edge_inset):
    u = union()

    t = lid_bolthole(scl)
    r = cylinder(r=lcdscrewrad*scl, h=(lcd_l*2+100)*scl, segments=50, center=True)
    r = rotate([90, 0, 0]).add(r)
    r = translate(v=[0, (lcd_l/2+50-edge_inset)*scl, 0]).add(r)
    t.add(r)
    u += t

    t = lid_bolthole(scl, False)
    r = cylinder(r=lcdscrewrad*scl, h=(lcd_l*2+100)*scl, segments=50, center=True)
    r = rotate([90, 0, 0]).add(r)
    r = translate(v=[0, (lcd_l/2+50-edge_inset)*scl, 0]).add(r)
    t.add(r)
    u += t

    return u

def screen_end(scl, ht=60):
    """
    TODO:
    * 
    """

    shear = 0
    innershear = 0
    w = lcd_w+lcd_inset_top+lcd_inset_bot
    edge_inset = bwid
    iro = 0

    rad = 15

    a = union()

    toplen = w+lcd_gap*2
    toplenoffs = (-lcd_inset_top+w+95)
    a += screen_frontedge(scl, ht, 0, toplenoffs, curvetopback=True,
                          frontonly=True)

    # middle filler
    r = union()
    c = shearedcube(size=[(lcd_d+lcd_gap*4)*scl,(w+lcd_gap*2)*scl,
                    (lcd_end_offs+ht)*scl],
                shear=[-shear*scl, 0, 0],
                innershear=[-innershear*scl, 0, 0])
    c = rotate([0, 90, 90]).add(c)
    r.add(c)
    t = translate(v=[(-lcd_inset_top+w+65)*scl, (16.5-ht)*scl,
                        (lcd_doff+30+lcd_gap*2)*scl])
    t.add(r)
    a += t

    # hinge hole
    r = union()
    r = cylinder(r=(lcd_hinge_inside_rad)*scl,
                        h=(20)*scl, segments=50, center=True)
    r = rotate([180, 90, 90]).add(r)
    t = hinge_translate(scl).add(r)
    t = translate(v=[0, (28.5)*scl, 0]).add(t)
    a -= t

    # hinge
    r = union()
    r = cylinder(r=(lcd_outer_rad)*scl, h=(ht+0.1)*scl,
                        segments=50, center=True)
    r = rotate([180, 90, 90]).add(r)
    t = hinge_translate(scl).add(r)
    t = translate(v=[0, (-ht/2+16.5)*scl, 0]).add(t)
    a += t

    # inner hexagon for nut
    c = cylinder(r=25.5*scl, # XXX: M2 nuts are 4mm hex diameter!
                        h=(bwid+30)*scl, segments=6, center=True)
    c = rotate([180, 90, 90]).add(c)
    c = hinge_translate(scl).add(c)
    a -= c
    c = cylinder(r=40*scl,
                        h=(25)*scl, segments=50, center=True)
    c = rotate([180, 90, 90]).add(c)
    c = translate(v=[0, (12)*scl, 0]).add(c)
    t = hinge_translate(scl).add(c)
    t = translate(v=[0, (-ht/2+25.5)*scl, 0]).add(t)
    a += t

    # hinge hole
    r = union()
    r = cylinder(r=screwrad*scl, h=(ht*5+0.3)*scl, segments=50, center=True)
    r = rotate([180, 90, 90]).add(r)
    t = hinge_translate(scl).add(r)
    t = translate(v=[0, (-ht/2+16.5)*scl, 0]).add(t)
    a -= t

    #a = translate(v=[0, (-lcd_end_offs)*scl, 0]).add(a)
    #return a

    r = union()
    r = cylinder(r=60*scl, h=(ht+50)*scl, segments=6, center=True)
    r = rotate([180, 90, 90]).add(r)
    t = hinge_translate(scl).add(r)
    t = translate(v=[0, (-ht/2+16.5-20)*scl, 0]).add(t)
    #a += t

    # hinge hole
    r = union()
    r = cylinder(r=45*scl, h=(ht+50)*scl, segments=6, center=True)
    r = rotate([180, 90, 90]).add(r)
    t = hinge_translate(scl).add(r)
    t = translate(v=[0, (-ht/2+16.5)*scl, 0]).add(t)
    #a -= t

    # clear out area containing lcd panel
    a = translate(v=[0, (ht-edge_inset)*scl, 0]).add(a)
    p = lcd_panel(scl, offs=3)
    p = translate(v=[155.5*scl,61*scl,0]).add(p)
    a -= p

    # add screen middle part
    a = translate(v=[0, (-lcd_end_ht)*scl,0]).add(a)
    a += screen_mid1(scl, hinge_depth+lcd_end_offs,
                          hole_depth+lcd_end_offs, halfhollow=True,
                          outdent=[lcd_w-82, lcd_front_indent],
                          cableduct=False, extra=40.0)

    # clear out end edge for a nut
    b = cube([50*2*scl, (55)*scl, (lcd_d+28)*scl])
    b = translate([-50*scl, (-0.5)*scl, -lcd_d*scl]).add(b)
    t = lid_bolthole(scl, False)
    t.add(b)
    a += t
    b = cube([30*2*scl, (ht+hinge_depth-12)*scl, (lcd_d+28)*scl])
    b = translate([-30*scl, -70*scl, -(lcd_d-20)*scl]).add(b)
    t = lid_bolthole(scl, False)
    t.add(b)
    a -= t
    if True: # XXX: hmmm... not sure if to do square or cylinder cutout
        b = cube([35*2*scl, (ht+hinge_depth-12)*scl, (lcd_d+23)*scl])
        b = translate([-35*scl, -70*scl, -(lcd_d-20)*scl]).add(b)
    else:
        b = cylinder(r=28*scl, h=(ht+hinge_depth-12)*scl, 
                        segments=50, center=True)
        b = rotate([0, 90, 90]).add(b)
        b = translate([0*scl, -30*scl, 0*scl]).add(b)
    t = lid_bolthole(scl)
    t.add(b)
    a -= t

    # *sigh* have to add some external edge support
    b = cube([55*scl, (30)*scl, (15)*scl])
    b = translate([-30*scl, -20*scl, 25*scl]).add(b)
    t = lid_bolthole(scl)
    t.add(b)
    a += t
    b = cube([15*scl, (30)*scl, (30)*scl])
    b = translate([-40*scl, -20*scl, -15*scl]).add(b)
    t = lid_bolthole(scl)
    t.add(b)
    a += t

    if pin_parts_3d:
        c = union()
        h = pin(B0)
        h = translate([40*scl, (16.5-ht)*scl, -55*scl]).add(h)
        c += h
        h = pin(B0)
        h = translate([(boxlength+20)*scl, (16.5-ht)*scl, -25*scl]).add(h)
        c += h
        h = pin(B0)
        h = translate([(boxlength-70)*scl, (16.5-ht)*scl, 70*scl]).add(h)
        c += h
        h = pin(B0)
        h = translate([(boxlength+80)*scl, (16.5-ht)*scl, 20*scl]).add(h)
        c += h
        h = pin(B0)
        h = translate([(boxlength-20)*scl, (16.5-ht)*scl, 125*scl]).add(h)
        c += h
        h = pin(B0)
        h = translate([(boxlength-145)*scl, (16.5-ht)*scl, 70*scl]).add(h)
        c += h
        h = pin(B0)
        h = translate([(50)*scl, (16.5-ht)*scl, 45*scl]).add(h)
        c += h
        h = pin(B0)
        h = translate([(-25)*scl, (16.5-ht)*scl, 22*scl]).add(h)
        c += h
        c = translate([0*scl, (-14)*scl, 0*scl]).add(c)
        a += c

    # screw holes through lid
    a -= lid_screwholes(scl, edge_inset)

    # more support
    b = cylinder(r=13*scl, h=28*scl, 
                    segments=50, center=True)
    b = rotate([0, 90, 90]).add(b)
    b = translate([0*scl, -6.5*scl, 0*scl]).add(b)
    t = lid_bolthole(scl)
    t.add(b)
    a += t
    t = lid_bolthole(scl, False)
    t.add(b)
    a += t

    if False: # XXX: disable. makes a bit of a mess of the hex hole
        # more support, this is for friction hinge inner
        c = cylinder(r=17*scl, 
                            h=(bwid)*scl, segments=50, center=True)
        c = rotate([180, 90, 90]).add(c)
        c = translate(v=[0, (-12)*scl,0]).add(c)
        c = hinge_translate(scl).add(c)
        a += c
        a = translate(v=[0, (-lcd_end_offs)*scl,0]).add(a)

    return a

def box_hook_cutout(scl, hinge_depth):
    a = union()
    b = cube([29.1*2*scl, 90*scl, 70*scl])
    b = translate([-29.1*scl, -10*scl, -30*scl]).add(b)
    t = case_bolthole(scl, end=0).add(b)
    t = translate(v=[(0)*scl, (-hinge_depth/2+3)*scl,
                  (boxheight)*scl]).add(t)
    a += t
    return a

def lid_end(scl, ht_offset, ht, hinge_depth, hole_depth):
    """
        TODO:
        fill in between hinge-end small stop-part and screwhole support 2
        fix curving on end T|L so that printhead is a bit happier
        create clips to lock matching base_end into place
    """
    # matches up with front_box_lid
    edge_inset = bwid
    a = union()

    border=3.0
    slot_depth = 100
    boxdepth = hinge_depth+ht+edge_inset# matches front_box_lid
    lid_depth = (boxlength-lcd_inset_bot+bwid-2)

    c = union()
    if True:
        curverads={
                   D|L:(80, 0),
                   #D|R:(bwid*2, 0),
                   T|L:(hthick, 0), # XXX: gcode chops this separate
                   #B|L:(bwid, 0), # XXX: bug in hollowbox
                   D|B:(hthick, 0),
                   T|B:(hthick, 0),
                   }
        b = hollowbox(scl, boxlength-122, boxdepth-bwid+hthick+30, boxheight,
                        {T:hthick, B: hthick,
                        L:hthick, R:-1, F:-1, D:-1},
                        curverads=curverads)
        b = translate([0, (20+bwid-hthick)*scl, 0*scl]).add(b)
        c.add(b)
        # short wall hinge-end XXX had to go, causes curving of lid
        #b = cube([(hthick)*scl, (boxdepth-bwid+30)*scl, (boxinset-20)*scl])
        #b = translate([(lid_depth-hthick)*scl, (20+bwid)*scl, 0*scl]).add(b)
        #c.add(b)

        # back hinge-end cutout XXX: inset adjust for print inaccuracy by -2
        b = cube([(90)*scl, (boxdepth+30)*scl, (boxinset+100)*scl])
        b = translate([-1*scl, (20+bwid)*scl, (boxinset-2)*scl]).add(b)
        c -= b
        # front cut-out
        b = cube([(400)*scl, (boxdepth+30)*scl, (boxinset+100)*scl])
        b = translate([(lid_depth)*scl, (bwid*2+3.0)*scl, (-1)*scl]).add(b)
        c -= b
    a.add(c)
    a = translate(v=[(30-lcd_inset_top)*scl, (-bwid)*scl,
                        (+50+boxtopoffs)*scl]).add(a)

    # insets for nuts and threaded bar
    holes = [2]
    cdep = 60
    for end in holes:
        r = union()
        dp = -3
        c = cube([36*2*scl, cdep*scl, (69)*scl], center=True)
        c = translate(v=[(-3)*scl, (cdep/2)*scl, (dp/2+1.5)*scl]).add(c)
        r.add(c)
        c = cylinder(r=27*scl, h=(200)*scl, segments=6)
        c = rotate([0, 90, 90]).add(c)
        c = rotate([0, 30, 0]).add(c)
        c = translate(v=[(0)*scl, (15)*scl, 0*scl]).add(c)
        r -= c
        t = case_bolthole(scl, end=end).add(r)
        t = translate(v=[(0)*scl, (3+bwid-1)*scl, (boxheight)*scl]).add(t)
        a += t

    # add screw-hole for lid_end to lock against
    sholes = [(165, 150), (boxlength-180, 150)]
    for end in range(3 if test else 4):
        if end == 2:
            continue
        d = cube([140*scl, 114*scl, 25*scl], center=True)
        d = rotate([90, 0, 0]).add(d)
        d = case_bolthole(scl, end=end).add(d)
        d = translate(v=[40*scl, 27*scl, 116*scl]).add(d) # XXX: magic constant
        a += d
        d = chamfered_backbox_screwholes(scl, 10)
        d = rotate([90, 0, 0]).add(d)
        d = case_bolthole(scl, end=end).add(d)
        d = translate(v=[0*scl, 22*scl, 85*scl]).add(d) # XXX: magic constant
        a -= d
    for (x,h) in sholes:
        d = chamfered_backbox_screwholes(scl, 10)
        d = rotate([90, 0, 0]).add(d)
        d = translate(v=[x*scl, 22*scl, h*scl]).add(d) # XXX: magic constant
        a -= d

    # add some structural support, algorithm matches up with
    # back_box lid_end base_mid
    sstep = 200
    sdep = sstep
    while sdep <= boxlength-sstep*2:
        h = cube([bwid*scl, 65*scl, 62*scl]) # sit just above strengthener
        h = translate(v=[sdep*scl, 10*scl, (60)*scl]).add(h)
        a += h
        h = shearedcube([25*scl, 15*scl, 20*scl],
                shear=[-10*scl, 0, 0], innershear=[0,0,0])
        h = rotate([0, 0, 90]).add(h)
        h = translate(v=[(sdep+15)*scl, bwid*scl,
                    (boxheight+50+boxtopoffs-bwid-20)*scl]).add(h)
        a += h
        sdep += sstep

    if pin_parts_3d:
        c = union()
        h = pin(B0)
        h = translate([-20*scl, (16.5-ht)*scl, 45*scl]).add(h)
        c += h
        h = pin(B0)
        h = translate([-5*scl, (16.5-ht)*scl, 200*scl]).add(h)
        c += h
        h = pin(B0)
        h = translate([(boxlength-100)*scl, (16.5-ht)*scl, 50*scl]).add(h)
        c += h
        h = pin(B0)
        h = translate([(boxlength-60)*scl, (16.5-ht)*scl, 130*scl]).add(h)
        c += h
        h = pin(B0)
        h = translate([(boxlength-100)*scl, (16.5-ht)*scl, 210*scl]).add(h)
        c += h
        c = translate([0*scl, (34.5)*scl, -5*scl]).add(c)
        a += c

    return a

def chamfered_backbox_screwholes(scl, sht):
    # chamfered screw holes in top of lid
    c = union()
    c.add(cylinder(r=topscrewrad*1.2*scl, r1=22*scl,
                    h=12*scl,
                    segments=50, center=True))
    d = cylinder(r=topscrewrad*scl,
                    h=(bwid+2.5+sht)*scl,
                    segments=50, center=True)
    d = translate(v=[0, 0, +(bwid+0.2+sht/2)*0.5*scl]).add(d)
    c.add(d)
    d = cylinder(r=22*scl,
                    h=(bwid+2.5+sht)*scl,
                    segments=50, center=True)
    d = translate(v=[0, 0, -20*scl]).add(d)
    c.add(d)
    c = rotate([180, 0, 0]).add(c)
    return c


def back_box_lidfront(scl, ht_offset, ht, extraht, boxextraht):
    """ TODO:
        * add test mode for keyboard clips, and some non-test ones
    """
    edge_inset = bwid
    bht = bwid*3-10
    blen = ht+extraht
    a = union()
    c = hollowbox(scl, bdep-ethdep+100+lidfront_offs+bwid, blen+boxextraht, bht,
                    {T:hthick, B: -1, L:bwid, R:-1, F:-1, D:-1},
                    curverads={ T|L:(bwid, 0),
                               })
    c = translate(v=[(-100-lidfront_offs-bwid)*scl,
                    0*scl, (lcd_d-15+bwid)*scl]).add(c)

    a.add(c)

    # clip on edge for keyboard
    c = shearedcube([18*scl, 80*scl, 8*scl],
                    shear=[5*scl, 0],
                    innershear=[0,0,0])
    c = rotate([0,90, 0]).add(c)
    c = translate(v=[(-100-lidfront_offs-bwid-5)*scl,
                    (150)*scl, (lcd_d+30+bwid-1)*scl]).add(c)
    a += c

    # cutout in lid which matches the base_mid screwhole cross-supports
    c = cube([(59+2)*2*scl, (extraht+56)*scl, 25*scl])
    c = translate(v=[(54)*scl,
                    (ht+extraht-45-2)*scl, (lcd_d-15+bwid-1)*scl]).add(c)
    a -= c

    # cutout at outer edge for base_end2 bits to poke through
    c = cube([159*scl, (extraht+48)*scl, 200*scl])
    c = translate(v=[(54)*scl,
                    -1*scl, (lcd_d-15+bwid-1)*scl]).add(c)

    a -= c
    for ((x,y,z), sht) in backboxsupports(blen-extraht, csw,
                                            overhanglid=boxextraht-3,
                                            underhanglid=18,
                                            frontlidonly=True):
        c = screwsupport(scl, csw, csw, sht)
        c = translate(v=[x,y,z]).add(c)
        c = translate(v=[-csw/2.0*scl, -csw/2.0*scl, 0]).add(c)
        c = translate(v=[-100*scl, extraht*scl, -10*scl]).add(c)
        a += c

    # join left and right supports together, needed because of 3dprint errs
    c = cube([54*scl, (154)*scl, 53*scl])
    c = translate(v=[(-100-lidfront_offs)*scl, 0*scl, 52*scl]).add(c)
    a += c
    c = cube([54*scl, (144)*scl, 50*scl])
    c = translate(v=[(-100-lidfront_offs)*scl, (blen+boxextraht-144)*scl,
                    52*scl]).add(c)
    a += c

    if pin_parts_3d:
        dep = bdep
        pblen = blen+boxextraht
        c = union()
        # horizontal
        h = cube([(160)*scl, 15*scl, (6)*scl])
        h = translate([(dep-130)*scl, (10)*scl, boxheight*scl]).add(h)
        c += h
        h = cube([(50)*scl, 15*scl, (6)*scl])
        h = translate([(dep-20)*scl, (pblen-130)*scl, boxheight*scl]).add(h)
        c += h
        h = cube([(40)*scl, 15*scl, (6)*scl])
        h = translate([(dep-10)*scl, (128)*scl, boxheight*scl]).add(h)
        c += h
        h = cube([140*scl, (15)*scl, (6)*scl])
        h = translate([60*scl, (pblen+40)*scl, boxheight*scl]).add(h)
        c += h
        h = cube([140*scl, (15)*scl, (6)*scl])
        h = translate([60*scl, (-50)*scl, boxheight*scl]).add(h)
        c += h

        # vertical
        h = cube([15*scl, (70)*scl, (6)*scl])
        h = translate([60*scl, -50*scl, boxheight*scl]).add(h)
        c += h
        h = cube([15*scl, (70)*scl, (6)*scl])
        h = translate([60*scl, (pblen-20)*scl, boxheight*scl]).add(h)
        c += h
        h = cube([15*scl, (pblen-130)*scl, (6)*scl])
        h = translate([(dep+15)*scl, (10)*scl, boxheight*scl]).add(h)
        c += h
        h = cube([15*scl, (pblen+100)*scl, (6)*scl])
        h = translate([(dep-140)*scl, (-50)*scl, boxheight*scl]).add(h)
        c += h

        #c = translate(v=[(-0)*scl, 0, (lcd_d-31+bwid+hthick)*scl]).add(c)
        c = translate(v=[(-135-lidfront_offs-bwid)*scl,
                        0*scl, (-boxheight+bht+11)*scl]).add(c)
        a += c

    a = translate(v=[(lcd_w+35-bdepoffs)*scl, 0, 0]).add(a)

    # supports for threads, one (end=1) needs a cutout in the base box
    # (for which it matches with back_box_base on end=1)
    dep = 40
    holes = [(1, extraht+45), (2, extraht+50),
                (2, (blen-dep)/2.0), (2, blen-dep-50)]
    for (end, offs) in holes:
        r = union()
        if end == 1:
            dp = -11
            r = lidscrewsupport(scl, dep, 105, dp)
        else:
            dp = 0
            c = cube([29*2*scl, dep*scl, (dp+29*2)*scl], center=True)
            c = translate(v=[(0)*scl, (dep/2.0)*scl, (-dp/2)*scl]).add(c)
            r.add(c)
        t = case_bolthole(scl, end=end).add(r)
        t = translate(v=[(0)*scl, (offs)*scl, (boxheight)*scl]).add(t)
        a += t

    # screw holes in box
    t = box_screwholes(scl, edge_inset, holes=[1,2])
    t = translate(v=[0, 0, boxheight*scl]).add(t)
    a -= t

    return a

def back_box_lid(scl, ht_offset, ht, extraht):
    """ TODO:
    """
    edge_inset = bwid
    bht = bwid*2+hthick-10
    blen = ht
    a = union()
    c = union()
    b = hollowbox(scl, ethdep+hthick, blen+extraht, bht,
                    {T:hthick, B: -1, L:hthick, R:-1, F:-1, D:-1},
                    curverads={ T|L:(hthick, 0),
                               T|R:(hthick, 0),
                               B|R:(bwid, 0),
                               })
    c.add(b)
    if pin_parts_3d:
        u = union()
        h = pin(B0, 1)
        h = translate([0*scl, -10*scl, 0*scl]).add(h)
        u += h
        h = pin(B0, 1)
        h = translate([(ethdep)*scl, -10*scl, 0*scl]).add(h)
        u += h
        h = pin(B0, 1)
        h = translate([(ethdep)*scl, (blen+extraht)*scl, 0*scl]).add(h)
        u += h
        h = pin(B0, 1)
        h = translate([(0)*scl, (blen+extraht)*scl, 0*scl]).add(h)
        u += h
        u = translate([0*scl, (0)*scl, 3*scl]).add(u)
        c += u

    c = translate(v=[(bdep-ethdep-hthick)*scl, 0, (lcd_d-22-hthick)*scl]).add(c)
    a += c
    # ok limitations of hollowbox we need to cut out the back right corner
    c = cube([159*scl, (bwid+1)*scl, 50*scl])
    c = translate(v=[(ethdep+bwid)*scl,
                    -0.9*scl, (lcd_d-22)*scl]).add(c)

    a -= c

    for ((x,y,z), sht) in backboxsupports(blen, csw, overhanglid=extraht-4,
                                                backlidonly=True):
        c = screwsupport(scl, csw, csw, sht)
        c = translate(v=[x,y,z]).add(c)
        c = translate(v=[-csw/2.0*scl, -csw/2.0*scl, 0]).add(c)
        c = translate(v=[-100*scl, 0*scl, -(10)*scl]).add(c)
        a += c

    a = translate(v=[(lcd_w+35-bdepoffs)*scl, 0, 0]).add(a)

    return a

def backboxsupports(blen, csw, overhanglid=0, onlyoverhang=False,
                               underhanglid=None,
                               backlidonly=False,
                               frontlidonly=False):
    l = []
    if not onlyoverhang:
        fl = [
            # these are for the keyboard lid
            ([(bdep+98-ethdep-csw/2)*scl, (blen-csw/2-48)*scl,
                                           (lcd_d-32+bwid*3)*scl],
                (backboxheight-bwid*2-hthick-17)),
            # box now has a big hole in it
            #([(csw/2-lidfront_offs-0.5)*scl,
            #    (blen*0.45-csw/2)*scl, (lcd_d-32+bwid*3)*scl],
            #    (backboxheight-bwid*2-hthick-17)),
            ([(csw/2-lidfront_offs-0.5)*scl,
                (blen-csw/2-19)*scl, (lcd_d-32+bwid*3)*scl],
                (backboxheight-bwid*2-hthick-17)),
            ([(csw/2-lidfront_offs-0.5)*scl,
                (csw/2+19)*scl, (lcd_d-32+bwid*3)*scl],
                (backboxheight-bwid*2-hthick-17)),
            ([(bdep+98-ethdep-csw/2)*scl,
                (csw/2+bwid+30)*scl, (lcd_d-32+bwid*3)*scl],
                (backboxheight-bwid*2-hthick-17)),
            ]
        bl = [
            # towards back of box
            ([(bdep+100-csw/2-bwid-4)*scl, (59+csw/2)*scl, (lcd_d-22)*scl],
                backboxheight-22.0),
            ([(bdep+100-csw/2-bwid-4)*scl, (320+csw/2)*scl, (lcd_d-22)*scl],
                backboxheight-22.0),
            ([(bdep+100-ethdep+csw/2+4)*scl, (59+csw/2)*scl, (lcd_d-22)*scl],
                backboxheight-22.5),
            ([(bdep+100-ethdep+csw/2+4)*scl, (blen-csw/2-hthick-5)*scl, (lcd_d-22)*scl],
                backboxheight-22.0),
            ([(bdep+100-csw/2-bwid-4)*scl, (blen-csw/2-hthick-5)*scl, (lcd_d-22)*scl],
                backboxheight-22.0),
        ]
        if backlidonly:
            l = bl
        elif frontlidonly:
            l = fl
        else:
            l = bl + fl
    if overhanglid:
        _blen = blen + overhanglid
        if not frontlidonly:
            l += [
            # towards back of box
            ([(bdep+100-csw/2-bwid-4)*scl, (_blen-csw/2)*scl, (lcd_d-22)*scl],
                backboxheight-22.0),
            ]
        if not backlidonly:
            l += [
            # these are for the keyboard lid
            ([(csw/2-12)*scl, (_blen-csw/2)*scl, (lcd_d-32+bwid*3)*scl],
                (backboxheight-bwid*2-hthick-17)),
        ]
    if underhanglid is not None:
        l += [
            # these are for the keyboard lid
            ([(csw/2-12)*scl, (-underhanglid-csw/2)*scl,
                                           (lcd_d-32+bwid*3)*scl],
                (backboxheight-bwid*2-hthick-17)),
        ]
    return l

def back_box_base(scl, ht_offset, ht, midpart=False, frontpart=False):
    """
    TODO:
    * use new 3d pin style (old doesn't work)
    * increase hole size for cable (widen and deepen)
    """
    edge_inset = bwid
    blen = ht
    a = union()
    curverads={ D|R:(bwid, 0),
               }
    if not midpart:
        # XXX: minor problem with this one, it covers the screwhole support
        # in the corner.
        curverads[B|R] = (bwid, 0)
    c = hollowbox(scl, ethdep, blen, backboxheight,
                    {T:-1, B: hthick, L:-25.0, R:bwid, F:hthick, D:hthick},
                    curverads=curverads)
    c = translate(v=[(bdep+100-ethdep)*scl, 0, (lcd_d-22)*scl]).add(c)
    a.add(c)
    c = hollowbox(scl, bdep+100+lidfront_offs-ethdep+1, blen, boxheight-hthick,
                    {T:-1, B: hthick, L:-25.0, R:-1, F:hthick, D:hthick})
    c = translate(v=[-lidfront_offs*scl, 0, (lcd_d-32+bwid*2+hthick)*scl]).add(c)
    a.add(c)

    # add extra bit at front (screw-holes are messed up otherwise)
    # TODO: this will become a shelf/interlock for the rest of the base
    c = cube([30*scl, blen*scl, hthick*scl])
    c = translate(v=[-(lidfront_offs+20)*scl, 0*scl,
                        (lcd_d-22-hthick+backboxheight)*scl]).add(c)
    a += c

    if not midpart:
        # cutout middle of base because there's too much plastic in the part
        c = cube([(bbcutout_dep+30)*scl, (blen-bbcutout_wid*2)*scl, 20*scl])
        c = translate(v=[-(lidfront_offs+30)*scl, bbcutout_wid*scl,
                        (boxheight+(lcd_d-34+bwid*2-hthick))*scl]).add(c)
        a -= c

    # cutout in supports, matched by join between downsupports
    # needed because 3d printing joins close downsupports anyway
    c = cube([58*scl, (blen+2)*scl, 53*scl])
    c = translate(v=[-(lidfront_offs+1)*scl, -1*scl, 50*scl]).add(c)
    a -= c

    if pin_parts_3d:
        dep = bdep+ethdep
        c = union()
        # horizontal
        h = pin(B0, 1)
        h = translate([50*scl, (-10)*scl, boxheight*scl]).add(h)
        c += h
        h = pin(B0, 1)
        h = translate([50*scl, (blen+10)*scl, boxheight*scl]).add(h)
        c += h
        h = pin(B0, 1)
        h = translate([(dep+10)*scl, (-20)*scl, boxheight*scl]).add(h)
        c += h
        h = pin(B0, 1)
        h = translate([(dep+10)*scl, (blen+10)*scl, boxheight*scl]).add(h)
        c += h

        c = translate(v=[(-75)*scl, 0, (lcd_d-30+bwid+hthick)*scl]).add(c)
        a += c

    if not midpart:
        overhanglid = 0
        boxlen = blen
        onlyoverhang = False
    else:
        overhanglid = 36 # XXX: total guess-work
        boxlen = 0
        onlyoverhang = True
    # add corner supports
    for ((x,y,z), sht) in backboxsupports(boxlen, csw, overhanglid=overhanglid,
                                            onlyoverhang=onlyoverhang):
        # add backing support for screwhole
        c = cube([63*scl, 55*scl, 25*scl], center=True)
        c = translate(v=[x,y,(backboxheight+7+bwid-15)*scl]).add(c)
        if midpart:
            c = translate(v=[0, 35*scl, 0]).add(c) # XXX: guesswork!
        a += c
        if midpart:
            c = translate(v=[0, 63*scl, 0]).add(c) # XXX: guesswork!
            a += c
        # now drill holes
        c = chamfered_backbox_screwholes(scl, 10)
        c = translate(v=[x,y,(backboxheight+hthick+0)*scl]).add(c)
        if midpart:
            c = translate(v=[0, 35*scl, 0]).add(c) # XXX: guesswork!
        a -= c
        if midpart:
            c = translate(v=[0, 63*scl, 0]).add(c) # XXX: guesswork!
            a -= c

    a = translate(v=[(lcd_w+35-100-bdepoffs)*scl, 0, 0]).add(a)

    if frontpart:
        a += front_box_base(scl, ht_offset, ht, dep=lcd_w-92, midpart=True)

    # add a structural support for bolthole (nut lock point)
    # has to be extended slightly so that the lid can sit on top of it
    hwid = 45.0 if not midpart else ht/2+1
    hoffsl = [(2, 0), (2, blen-hwid)]
    if not midpart:
        hoffsl += [(1, 0)]
    if midpart and not test:
        hoffsl += [(3, 0), (3, blen-hwid)]
    for (hole, offs) in hoffsl:
        r = union()
        doffs = 0
        dmoffs = 0
        if midpart and hole == 2:
            doffs = -80+6
            dp = 80
            dmoffs = 6
        elif hole == 2 or hole == 3:
            dp = 80
            doffs = -80+6
            dmoffs = 6
        else:
            dp = 60
            doffs = -11
        c = cube([29*2*scl, hwid*scl, (dp+29*2)*scl], center=True)
        c = translate(v=[(0)*scl, (hwid/2-3)*scl, (-dp/2-doffs)*scl]).add(c)
        r.add(c)
        if hole == 2:#and offs == 0:
            c = cube([29*2*scl, hwid*scl, (dp+29*2)*scl], center=True)
            c = translate(v=[(+26.0*2)*scl, (hwid/2-3)*scl,
                        (dp/2-dmoffs)*scl]).add(c)
            r.add(c)
        t = case_bolthole(scl, end=hole).add(r)
        t = translate(v=[(0)*scl, (offs+3)*scl, (boxheight)*scl]).add(t)
        a += t

    if not midpart:
        # cutout and inset for friction hinge bolt.
        # matches up with base_end2 hinge location
        r = union()
        r.add(cube([80*scl, 40*scl, 52*scl], center=True))
        r.add(cube([60*scl, 40*scl, 82*scl], center=True))
        t = hinge_translate(scl).add(r)
        t = translate(v=[0, (bwid/2)*scl, (-3*scl)]).add(t)
        a -= t
        h = shearedcube([(10)*scl, (43.0)*scl, (hthick*2)*scl],
                        shear=[0,-6*scl, 0],
                        innershear=[0,0*scl, 0])
        h = rotate([90, 0, 0]).add(h)
        c = hinge_translate(scl).add(h)
        c = translate(v=[(34.1)*scl, (hthick)*scl,
                         (-17)*scl]).add(c)
        a += c

    # add a holder for a nut
    if not midpart:
        r = union()
        c = cube([80*scl, 40*scl, 40*scl], center=True)
        r.add(c)
        t = case_bolthole(scl, end=1).add(r)
        t = translate(v=[0, 107*scl, (boxheight+29)*scl]).add(t)
        a -= t
        c = cylinder(r=(26)*scl, # XXX: nuts are 4mm hex diameter!
                            h=(25)*scl, segments=6, center=True)
        c = rotate([180, 90, 90]).add(c)
        c = translate(v=[0, -10*scl, -10*scl]).add(c)
        r -= c
        t = case_bolthole(scl, end=1).add(r)
        t = translate(v=[0, 107*scl, (boxheight+30)*scl]).add(t)
        a += t

    # screw holes in box
    holes = [1,2] if not midpart else [2]
    if midpart and not test:
        holes.append(3)
    t = box_screwholes(scl, edge_inset, holes=holes)
    t = translate(v=[0, 0, boxheight*scl]).add(t)
    a -= t

    if not midpart:
        # add a locking-part to base_end2 cutout
        h = shearedcube([(10)*scl, (53.1)*scl, (hthick*2)*scl],
                        shear=[0,-6*scl, 0],
                        innershear=[0,0*scl, 0])
        h = rotate([90, 0, 0]).add(h)
        h = translate(v=[(boxlength-bwid-49.8)*scl,
                            (hthick)*scl, (119.9)*scl]).add(h)
        a += h

    if not midpart:
        a -= ethernet(scl)

    return a

def tpanel_supports(blen, dep, csw):
    return [
        ([(dep-csw/2)*scl, (blen-csw/2)*scl,
                                       (lcd_d-32+bwid*3)*scl],
            (backboxheight-bwid*2-hthick+7-17)),
        ([(csw/2+124-0.5)*scl,
            (blen-csw/2)*scl, (lcd_d-32+bwid*3)*scl],
            (backboxheight-bwid*2-hthick+7-17)),
        ([(csw/2+124-0.5)*scl,
            (csw/2+2)*scl, (lcd_d-32+bwid*3)*scl],
            (backboxheight-bwid*2-hthick+7-17)),
        ([(dep-csw/2)*scl,
            (csw/2+2)*scl, (lcd_d-32+bwid*3)*scl],
            (backboxheight-bwid*2-hthick+7-17)),
        ([(paneldepth+pdept+30-csw/2)*scl,
            (blen/2)*scl, (lcd_d-32+bwid*3)*scl],
            (backboxheight-bwid*2-hthick+7-17)),
        ]

def frontboxsupports(blen, dep, csw, overhanglid=0, onlyoverhang=False,
                               underhanglid=None,
                               touchpaneltray=None):
    l = []
    if not onlyoverhang:
        l = [
            # these are for the keyboard lid
            ([(dep-csw/2)*scl, (blen-csw/2)*scl,
                                           (lcd_d-32+bwid*3)*scl],
                (backboxheight-bwid*2-hthick+7-17)),
            ([(csw/2+134-0.5)*scl,
                (blen*0.45-csw/2)*scl, (lcd_d-32+bwid*3)*scl],
                (backboxheight-bwid*2-hthick+7-17)),
            ([(csw/2+134-0.5)*scl,
                (blen-csw/2)*scl, (lcd_d-32+bwid*3)*scl],
                (backboxheight-bwid*2-hthick+7-17)),
            ([(csw/2+134-0.5)*scl,
                (csw/2+bwid+2)*scl, (lcd_d-32+bwid*3)*scl],
                (backboxheight-bwid*2-hthick+7-17)),
            ([(dep-csw/2)*scl,
                (csw/2+bwid+2)*scl, (lcd_d-32+bwid*3)*scl],
                (backboxheight-bwid*2-hthick+7-17)),
            ]
    if overhanglid:
        _blen = blen + overhanglid
        l += [
            # these go into base_end2
            ([(csw/2-12)*scl, (_blen-csw/2)*scl, (lcd_d-32+bwid*3)*scl],
                (backboxheight-bwid*2-hthick-17)),
        ]
    if touchpaneltray is not None:
        _blen = blen + touchpaneltray
        l += [
            # these go into base_end2
            ([(csw/2+124-0.5)*scl, (_blen-csw/2)*scl, (lcd_d-32+bwid*3)*scl],
                (backboxheight-bwid*2-hthick-17)),
            ([(dep-csw/2)*scl, (_blen-csw/2)*scl, (lcd_d-32+bwid*3)*scl],
                (backboxheight-bwid*2-hthick-17)),
        ]
    if underhanglid is not None:
        l += [
            # these are for the keyboard lid
            ([(csw/2+134-0.5)*scl, (-underhanglid-csw/2)*scl,
                                           (lcd_d-32+bwid*3)*scl],
                (backboxheight-bwid*2-hthick+7-17)),
            ([(dep-csw/2-0.5)*scl, (-underhanglid-csw/2)*scl,
                                           (lcd_d-32+bwid*3)*scl],
                (backboxheight-bwid*2-hthick+7-17)),
        ]
    return l

def front_box_lid(scl, ht_offset, ht, extraht=0, tpanel=False):
    """
    TODO:
    """
    # matches up with lid_end
    edge_inset = bwid
    bht = boxheight-86 # XXX: magic number...
    flen = ht+extraht
    plen = 200
    plent = (flen - plen) / 2
    pht = bht
    pborder = 18
    boxextraht = 0
    a = union()
    thick = {T:hthick, B: 40, L:hthick, R:25, F:40, D:-1}
    curverads={ T|L:(hthick, 0) }
    c = hollowbox(scl, fdep, flen, bht,
                    thick, curverads)
    if pin_parts_3d:
        u = union()
        h = pin(B0, 1)
        h = translate([-10*scl, -10*scl, 0*scl]).add(h)
        u += h
        h = pin(B0, 1)
        h = translate([(fdep+10)*scl, -10*scl, 0*scl]).add(h)
        u += h
        h = pin(B0, 1)
        h = translate([(fdep+10)*scl, (flen+10)*scl, 0*scl]).add(h)
        u += h
        h = pin(B0, 1)
        h = translate([(-10)*scl, (flen+10)*scl, 0*scl]).add(h)
        u += h
        h = pin(B0, 1)
        h = translate([(fdep+30)*scl, (flen)/2*scl, 0*scl]).add(h)
        u += h
        h = pin(B0, 1)
        h = translate([(fdep+30)*scl, (plent)*scl, 0*scl]).add(h)
        u += h
        h = pin(B0, 1)
        h = translate([(fdep+30)*scl, (plent+plen)*scl, 0*scl]).add(h)
        u += h
        u = translate([0*scl, (0)*scl, 3*scl]).add(u)
        c += u

    c = translate([5*scl, 0, (+50+boxtopoffs)*scl]).add(c)
    a.add(c)

    if not tpanel:
        supports = frontboxsupports(flen-extraht, fdep, csw,
                                            overhanglid=boxextraht,
                                            underhanglid=18)
    else:
        supports = tpanel_supports(flen-extraht, fdep, csw)

    for ((x,y,z), sht) in supports:
        c = screwsupport(scl, csw, csw, sht)
        c = translate(v=[x,y,z]).add(c)
        c = translate(v=[-csw/2.0*scl, -csw/2.0*scl, 0]).add(c)
        c = translate(v=[5*scl, extraht*scl, -17*scl]).add(c)
        a += c

    if not tpanel:
        # bridge between supports, stops front box from moving about
        # XXX: magic constants
        c = cube([30*scl, (extraht+56)*scl, 44*scl])
        c = translate(v=[(fdep-25)*scl,
                        (extraht-65-1)*scl, (60)*scl]).add(c)
        a += c

    # supports for threads, one (end=1) needs a cutout in the base box
    dep = 20
    if tpanel:
        holes = [(0, 71), (0, flen-dep-71), (0, (flen-dep)/2)]
    else:
        holes = [(0, extraht+50),
                    (0, (flen-dep)/2.0), (0, flen-dep)]
    for (end, offs) in holes:
        r = lidscrewsupport(scl, dep, 105, -13)
        t = case_bolthole(scl, end=end).add(r)
        t = translate(v=[(0)*scl, (offs)*scl, (boxheight)*scl]).add(t)
        a += t

    if tpanel:
        c = cube([(paneldepth+1)*scl, plen*scl, (pht+1)*scl])
        t = translate([(5+pdept)*scl, plent*scl, (+50+boxtopoffs-1)*scl]).add(c)
        a -= t

        thick = {T:-1, B: hthick, L:hthick, R:hthick+15, F:hthick, D:hthick}
        c = hollowbox(scl, paneldepth+15, plen, pht,
                        thick)
        t = translate([(5+pdept)*scl, plent*scl, (+50+boxtopoffs)*scl]).add(c)
        a += t

        c = cube([(paneldepth+1-pborder*2)*scl,
                    (plen-pborder*2)*scl, (pht+2)*scl])
        t = translate([((5+pdept)+pborder)*scl, (plent+pborder)*scl,
                            (+50+boxtopoffs-1)*scl]).add(c)
        a -= t

    # screw holes in box
    t = box_screwholes(scl, edge_inset, holes=[0])
    t = translate(v=[0, 0, boxheight*scl]).add(t)
    a -= t

    return a

def lidscrewsupport(scl, hdep, ht, dp, offs=0, wid=29):
    r = union()
    c = cube([(wid+offs)*2*scl, hdep*scl, (ht)*scl], center=True)
    c = translate(v=[(0)*scl, (hdep/2.0)*scl, (+ht/2-10)*scl]).add(c)
    r.add(c)
    c = shearedcube([(wid+offs)*2*scl, hdep*scl, (17)*scl],
            shear=[-15*scl,0,0], innershear=[15*scl, 0, 0], center=True)
    c = translate(v=[(0)*scl, (hdep/2.0)*scl, (ht-3)*scl]).add(c)
    r.add(c)
    r = translate(v=[(0)*scl, 0, (dp-ht/2-13)*scl]).add(r)
    return r

def front_box_base(scl, ht_offset, ht, lid_ht=0, extraht=0, dep=None,
                midpart=False):
    """
    TODO:
    * use new 3d pin style 
    """
    if dep is None:
        dep = fdep
    edge_inset = bwid
    bht = boxheight-boxinset
    blen = ht
    flen = lid_ht+extraht
    a = union()
    c = hollowbox(scl, dep, blen, bht,
                    {T:-1, B: hthick, R:-25.0, L:hthick, F:hthick, D:hthick},
                    curverads={ D|L:(80, 0),
                               })
    c = translate(v=[(5)*scl, 0, (lcd_d-32+bwid*2+boxinset)*scl]).add(c)
    a.add(c)

    # remove front part for touchpanel
    c = cube([500*scl, (blen+2)*scl, (bwid+2)*scl])
    c = translate(v=[(73)*scl, (-1)*scl,
                (lcd_d-34+boxinset+bwid+hthick)*scl]).add(c)
    a -= c


    # add a structural support for bolthole (nut lock point)
    hwid = 34
    hoffsl = [(0, 1), (0, blen-hwid)]
    if not midpart:
        hoffsl += [(0, (blen-hwid)/2)]
    for (hole, offs) in hoffsl:
        r = union()
        doffs = -5
        dp = 0
        c = cube([40*2*scl, hwid*scl, (dp+34*2)*scl], center=True)
        c = translate(v=[(0)*scl, (hwid/2-3)*scl, (-dp/2-doffs)*scl]).add(c)
        r.add(c)
        t = case_bolthole(scl, end=hole).add(r)
        t = translate(v=[(0)*scl, (offs+3)*scl, (boxheight)*scl]).add(t)
        a += t

    if not midpart:
        # XXX: magic constant for length and touchpaneltray arg
        for ((x,y,z), sht) in frontboxsupports(blen-125, fdep, csw, 0,
                                                touchpaneltray=57):
            # add backing support for screwhole
            c = cube([63*scl, 70*scl, 25*scl], center=True)
            c = translate(v=[x+5*scl,y,(backboxheight+7+bwid-15)*scl]).add(c)
            a += c
            c = chamfered_backbox_screwholes(scl, 10)
            c = translate(v=[x+5*scl,y,(backboxheight+hthick)*scl]).add(c)
            a -= c

    # screwhole for touchpanel
    if midpart:
        # add backing support for screwhole
        c = cube([63*scl, 70*scl, 25*scl], center=True)
        c = translate(v=[(7+paneldepth+pdept)*scl,
                            ht/2*scl,(backboxheight+7+bwid-15)*scl]).add(c)
        a += c
        c = chamfered_backbox_screwholes(scl, 10)
        c = translate(v=[(7+paneldepth+pdept)*scl, ht/2*scl,
                            (backboxheight+hthick)*scl]).add(c)
        a -= c


    # cut-outs so that the lid's thread-support goes through
    hdep = 30
    cdep = 20
    if midpart:
        holes = [(0, (flen-cdep)/2.0+74)] # XXX: 74=magic constant
        hdep = 40
        cdep = 20
    else:
        holes = [(0, extraht+50),
                    (0, (flen-cdep)/2.0), (0, flen-cdep),
                    (0, blen+20) # XXX: magic number, for touchpanel tray
                ]
    for (end, offs) in holes:
        r = lidscrewsupport(scl, hdep, 70, 3, wid=35)
        t = case_bolthole(scl, end=end).add(r)
        t = translate(v=[(0)*scl, (offs-extraht-(hdep-cdep)/2)*scl,
                (boxheight)*scl]).add(t)
        a -= t


    # screw holes in box
    t = box_screwholes(scl, edge_inset, holes=[0])
    t = translate(v=[0, 0, boxheight*scl]).add(t)
    a -= t

    if pin_parts_3d:
        c = union()
        # horizontal
        h = cube([(105)*scl, 15*scl, (6)*scl])
        h = translate([30*scl, -30*scl, boxheight*scl]).add(h)
        c += h
        h = cube([(65)*scl, 15*scl, (6)*scl])
        h = translate([(dep-15)*scl, -30*scl, boxheight*scl]).add(h)
        c += h
        h = cube([(105)*scl, 15*scl, (6)*scl])
        h = translate([30*scl, (20+blen)*scl, boxheight*scl]).add(h)
        c += h
        h = cube([(65)*scl, 15*scl, (6)*scl])
        h = translate([(dep-15)*scl, (30+blen)*scl, boxheight*scl]).add(h)
        c += h
        h = cube([(dep)*scl, 15*scl, (6)*scl])
        h = translate([30*scl, (10)*scl, boxheight*scl]).add(h)
        c += h
        h = cube([(dep)*scl, 15*scl, (6)*scl])
        h = translate([30*scl, (blen-20)*scl, boxheight*scl]).add(h)
        c += h

        # vertical
        h = cube([15*scl, (blen+60)*scl, (6)*scl])
        h = translate([30*scl, -30*scl, boxheight*scl]).add(h)
        c += h
        h = cube([15*scl, (blen+60)*scl, (6)*scl])
        h = translate([120*scl, -30*scl, boxheight*scl]).add(h)
        c += h
        h = cube([15*scl, (60)*scl, (6)*scl])
        h = translate([80*scl, -30*scl, boxheight*scl]).add(h)
        c += h
        h = cube([15*scl, (60)*scl, (6)*scl])
        h = translate([80*scl, (blen-30)*scl, boxheight*scl]).add(h)
        c += h
        h = cube([12*scl, (blen+75)*scl, (6)*scl])
        h = translate([(dep-22)*scl, -30*scl, boxheight*scl]).add(h)
        c += h
        h = cube([15*scl, (blen+75)*scl, (6)*scl])
        h = translate([(dep+45)*scl, (-30)*scl, boxheight*scl]).add(h)
        c += h
        if not test:
            h = cube([15*scl, (blen+60)*scl, (6)*scl])
            h = translate([(dep/2)*scl, (-28)*scl, boxheight*scl]).add(h)
            c += h

        c = translate(v=[(5)*scl, 0, (lcd_d-33+bwid+hthick)*scl]).add(c)
        a += c

    return a

def base_mid(scl, ht_offset, ht, hinge_depth, hole_depth, mid=False):
    edge_inset = bwid
    a = union()
    a += back_box_base(scl, ht_offset, ht, midpart=True, frontpart=True)

    # add some structural support, algorithm matches up with
    # back_box lid_end
    sstep = 134
    sdep = sstep
    while sdep <= boxlength-sstep*3:
        h = cube([8*scl, ht*scl, 50*scl])
        h = translate(v=[sdep*scl, 0*scl, (boxheight)*scl]).add(h)
        a.add(h)
        sdep += sstep

    return a

def screwsupport(scl, w, d, h):
    sht = 80 # screw hole height: 8mm screws
    u = union()
    u.add(cube([w*scl, d*scl, h*scl]))
    sh = cylinder(r=topscrewrad*scl, h=sht*scl, center=True, segments=50)
    sh = translate(v=[w/2.0*scl, d/2.0*scl, +(h-sht/2+0.5)*scl]).add(sh)
    u -= sh
    return u

def base_end2(scl, ht_offset, ht, hinge_depth, hole_depth, mid=False):
    """
        TODO:
        * hole for friction hinge bolt too large a diameter.  reduce.
    """
    edge_inset = bwid
    a = union()

    border=3.0 # move cylinders inwards so that lid cylinders fit around them
    slot_depth = 100
    extradepth = 0
    boxdepth = hinge_depth+ht

    if mid:
        extradepth = 140
    else:
        # inner tube
        r = union()
        r = cylinder(r=(lcd_hinge_inside_rad-border)*scl, h=(boxdepth)*scl,
                     segments=50, center=True)
        r = rotate([180, 90, 90]).add(r)
        t = hinge_translate(scl).add(r)
        t = translate(v=[0, (-27-bwid+boxdepth/2)*scl, 0]).add(t)
        a.add(t)

    # base hinge box
    box = base_box(scl, boxdepth, hole_depth, ht, extralen=extradepth,
                   hollow=True, inner=True)

    a += box

    # add corner supports
    # XXX: locations are all a bit bogus (magic numbers)
    for ((x,y,z), sht) in backboxsupports(0, csw, underhanglid=-18,
                                            onlyoverhang=True):
        c = cube([75*scl, 68*scl, 25*scl], center=True)
        c = translate(v=[x,y,(boxdepth+92+bwid-16)*scl]).add(c)
        c = translate(v=[(lcd_w-80)*scl, 0, 0]).add(c)
        a += c
        c = chamfered_backbox_screwholes(scl, 10)
        c = translate(v=[x,y,(boxdepth+92+hthick-7)*scl]).add(c)
        c = translate(v=[(lcd_w-80)*scl, 0, 0]).add(c)
        a -= c

    for ((x,y,z), sht) in frontboxsupports(0, fdep, csw,
                                            onlyoverhang=True,
                                            underhanglid=-18): # XXX: magic
        c = cube([75*scl, 68*scl, 25*scl], center=True)
        c = translate(v=[x+5*scl,y,(backboxheight+hthick-3)*scl]).add(c)
        a += c
        c = chamfered_backbox_screwholes(scl, 10)
        c = translate(v=[x+5*scl,y,(backboxheight+hthick)*scl]).add(c)
        a -= c

    # hollow out the inner tube
    ho = hollow_out_basebox(scl, border, boxdepth)
    t = translate(v=[0, (-60.5)*scl, 0]).add(ho)
    a -= t

    holes = [0, 1, 2] if test else [0, 1, 2, 3]
    # screw support at both ends
    for end in holes:
        r = union()
        cht = 32*2 if end == 2 else 74
        doff = 0 if end == 2 else -7
        c = cube([29*2*scl, boxdepth*scl, cht*scl], center=True)
        r.add(c)
        t = case_bolthole(scl, end=end).add(r)
        t = translate(v=[(0)*scl, (-(0)/2-3.5)*scl,
                        (boxheight-doff)*scl]).add(t)
        a += t

    # screw holes in box
    t = box_screwholes(scl, edge_inset, holes=holes)
    t = translate(v=[0, 0, boxheight*scl]).add(t)
    a -= t

    if not mid:
        # this screwhole is only part-way through
        t = box_screwholes(scl, edge_inset, holes=[1], h=60)
        t = translate(v=[0, -69.0*scl, boxheight*scl]).add(t)
        a -= t

        # cutout for cable
        h = cylinder(r=33*scl, h=30*scl, segments=50, center=True)
        h = rotate([180, 90, 90]).add(h)
        h = hinge_translate(scl).add(h)
        h = translate(v=[(0)*scl,
                            (25)*scl, (0)*scl]).add(h)
        a -= h

        # arc cutout for cable
        r = union()
        cable_slot_depth = 70
        c = touch_arc(lcd_hinge_inner_rad-37, 20, bwid,
                            30, scl,
                      angle=0)
        c = rotate([180, 90, 90]).add(c)
        c = rotate([0, -29, 0]).add(c)
        r += c
        c = rotate([0, 29, 0]).add(c)
        r += c
        t = hinge_translate(scl).add(r)
        t = translate(v=[0, (hinge_depth-ht+cable_slot_depth/2-10)*scl,
                         0]).add(t)
        a -=t

        # cutout in other side for slot
        h = cube([(30)*scl, (boxdepth)*scl,
                   (50)*scl])
        h = translate(v=[(boxlength-bwid-125+60)*scl,
                            (-32-0.2)*scl, (120)*scl]).add(h)
        a -= h

        # fill-in just above front box lid, in between two screwholes
        # XXX: magic numbers here... *sigh*
        h = cube([(100)*scl, (bwid)*scl,
                   (55)*scl])
        h = translate(v=[(boxlength-bwid-260)*scl,
                            (bwid+2.5)*scl, (53+hthick)*scl]).add(h)
        a += h

    # hinge hole, for friction hinge to poke through and support back box
    r = union()
    r = cube([88*scl, 40*scl, 40*scl], center=True)
    t = hinge_translate(scl).add(r)
    t = translate(v=[0, (-ht/2+48.5)*scl, (3*scl)]).add(t)
    a -= t

    a = translate(v=[0, (ht-edge_inset+ht_offset)*scl, 0]).add(a)

    return a

def hollow_out_edge(scl, hole_depth, ht, border):
    r = union()
    r = cylinder(r=(lcd_outer_rad+border)*scl, h=(hole_depth+ht*1+10.0)*scl,
                        segments=50, center=True)
    r = rotate([180, 90, 90]).add(r)
    t = hinge_translate(scl).add(r)
    t = translate(v=[0, (hole_depth-ht*2-hole_depth/2+16.5)*scl, 0]).add(t)
    return t

def hollow_out_basebox(scl, border, hinge_depth):
    r = union()
    r = cylinder(r=(lcd_hinge_inside_rad-bwid-border)*scl,
                        h=(hinge_depth+0.4)*scl, segments=50, center=True)
    r = rotate([180, 90, 90]).add(r)
    t = hinge_translate(scl).add(r)
    t = translate(v=[0, (hinge_depth-hinge_depth/2+16.5-10)*scl, 0]).add(t)
    return t

def base_end(scl, ht_offset, ht, hinge_depth, hole_depth, innerpart=False):
    """
        TODO:
        fill in between lid screwhole gap 1 and 2
        increase size of insets a bit to fit with the lid
    """
    edge_inset = bwid
    a = union()

    border=3.0 # move cylinders inwards so that lid cylinders fit around them
    slot_depth = 100

    # inner tube
    r = union()
    r = cylinder(r=(lcd_hinge_inside_rad-border)*scl, h=(hinge_depth-10)*scl,
                        segments=50, center=True)
    r = rotate([180, 90, 90]).add(r)
    t = hinge_translate(scl).add(r)
    t = translate(v=[0, (hinge_depth-hinge_depth/2+6.5-5)*scl, 0]).add(t)
    a.add(t)

    # base hinge box
    boxdepth = hinge_depth+ht+lcd_end_offs+10
    box = base_box(scl, boxdepth+hthick, hole_depth, ht,
                            hollow=True, endpart=True)
    box = translate(v=[0, -(hthick+lcd_end_offs+10)*scl, 0]).add(box)

    # add big strengthening bar, help reduce torquing
    h = cube([(boxlength-96)*scl, 60*scl, 60*scl])
    h = translate(v=[50*scl, 0*scl, (124)*scl]).add(h)
    a.add(h)
    # XXX: blegh!  must be a better way to do this...
    # fill in end part near hinge (might as well)
    h = cube([(159)*scl, (60+hthick+30)*scl, 57*scl])
    h = translate(v=[(boxlength-205)*scl, (-43.5-hthick-30)*scl,
                        (124)*scl]).add(h)
    a.add(h)
    h = cube([(90)*scl, (60+hthick+30)*scl, 60*scl])
    h = translate(v=[(105)*scl, (-43.5-hthick-30)*scl,
                        (124)*scl]).add(h)
    a.add(h)
    h = cube([(40)*scl, (hole_depth+ht+hthick+30)*scl, 60*scl])
    h = rotate([0, 30, 0]).add(h) # hilarious....
    h = translate(v=[(boxlength-120)*scl, (-43.5-hthick-30)*scl, 95*scl]).add(h)
    a.add(h)

    # add curved inner wall
    u = intersection()
    r = union()
    r = cylinder(r=(lcd_outer_rad+20)*scl, h=(hole_depth+ht*2+30+bwid+0.1)*scl,
                        segments=50, center=True)
    r = rotate([180, 90, 90]).add(r)
    t = hinge_translate(scl).add(r)
    t = translate(v=[0, (hole_depth-ht*2-hole_depth/2+16.5)*scl, 0]).add(t)
    b = base_box(scl, boxdepth+hthick, hole_depth, ht, hollow=False)
    b = translate(v=[0, -(hthick+30)*scl, 0]).add(b)
    u.add(b)
    u.add(t)

    box += u

    # add 2nd covering curved inner wall
    u = intersection()
    r = union()
    r = cylinder(r=(lcd_outer_rad)*scl, h=(20+0.1)*scl,
                        segments=50, center=True)
    r = rotate([180, 90, 90]).add(r)
    t = hinge_translate(scl).add(r)
    t = translate(v=[0, (hole_depth-15)*scl, 0]).add(t)
    b = base_box(scl, boxdepth, hole_depth, ht, hollow=False)
    u.add(b)
    u.add(t)

    box += u

    # hollow out base box at edge
    box -= hollow_out_edge(scl, hole_depth, ht, border)

    a += box

    # hollow out tube including base box
    a -= hollow_out_basebox(scl, border, hinge_depth)

    soffset = -30

    # screw support at both ends.  also have self-tap screw-holes above
    # bolts
    bhwid = 29.1+6
    bhdep = ht + hinge_depth +hthick+30
    for end in range(3 if test else 4):
        if end == 2:
            bht = bhwid*2+5
        else:
            bht = 90
        if end == 2:
            b = cube([(bhwid*2+15)*scl, bhdep*scl, (bhwid+40)*scl])
            b = translate([(-bhwid+5)*scl, (18.5-hthick)*scl, 0*scl]).add(b)
        else:
            b = cube([(bhwid*2+bwid*2)*scl, (bhdep)*scl, (130-hthick)*scl])
            b = translate([(-bhwid-bwid)*scl, (18.5-hthick)*scl,
                            -(bhwid+37-hthick)*scl]).add(b)
        t = case_bolthole(scl, end=end).add(b)
        t = translate(v=[(0)*scl, (-hinge_depth/2+3+soffset-30)*scl,
                    (boxheight-bwid)*scl]).add(t)
        a += t

        b = cube([bhwid*2*scl, 70*scl, bht*scl])
        if end == 2:
            b = translate([-bhwid*scl, 10*scl, -(bhwid+3)*scl]).add(b)
        else:
            b = translate([-bhwid*scl, 10*scl, -(bhwid+2)*scl]).add(b)
        t = case_bolthole(scl, end=end).add(b)
        t = translate(v=[(0)*scl, (-hinge_depth/2+3+soffset-30)*scl,
                    (boxheight)*scl]).add(t)
        a -= t

        r = union()
        c = cube([29*2*scl, 48*scl, bhwid*1.7*scl])
        r += translate([-29*scl, 80*scl, -28*scl]).add(c)
        t = case_bolthole(scl, end=end).add(r)
        t = translate(v=[(0)*scl, (-hinge_depth/2+3+soffset)*scl,
                        (boxheight)*scl]).add(t)
        a += t

    for end in range(3 if test else 4):
        if end == 2:
            bht = bhwid*2+5
        else:
            bht = 90

        if end != 2:
            # add screw-hole for lid_end to lock against
            d = cube([149*scl, 118*scl, 26*scl], center=True)
            d = rotate([90, 0, 0]).add(d)
            d = case_bolthole(scl, end=end).add(d)
            d = translate(v=[40*scl, -64*scl, 116*scl]).add(d) # XXX: magic constant
            a -= d
            v = union()
            d = cylinder(r=topscrewrad*scl,
                            h=(80)*scl,
                            segments=50, center=True)
            v.add(d)
            v = rotate([90, 0, 0]).add(v)
            d = translate(v=[0, -34*scl, (85)*scl]).add(v) # XXX: magic constant
            d = case_bolthole(scl, end=end).add(d)
            a -= d

    for (x,h) in [(165, 150), (boxlength-179, 150)]:
        # add screw-hole for lid_end to lock against
        v = union()
        d = cylinder(r=topscrewrad*scl,
                        h=(80)*scl,
                        segments=50, center=True)
        v.add(d)
        v = rotate([90, 0, 0]).add(v)
        d = translate(v=[x*scl, -34*scl, h*scl]).add(v) # XXX: magic constant
        a -= d

    # screw holes in box
    t = box_screwholes(scl, edge_inset)
    t = translate(v=[0, 0, boxheight*scl]).add(t)
    a -= t

    # additional support for friction hinge
    r = union()
    cable_slot_depth = 25
    for ang in [0, 180]:
        c = touch_arc(lcd_hinge_inner_rad-20, cable_slot_depth, bwid,
                            10, scl,
                      angle=65)
        c = rotate([180, 90, 90]).add(c)
        c = rotate([0, lcd_ext_rot_angle+168+ang, 0]).add(c)
        r += c
    t = hinge_translate(scl).add(r)
    t = translate(v=[0, (hinge_depth-ht-cable_slot_depth/2+23)*scl,
                     0]).add(t)
    a +=t

    b = cube([(boxlength)*scl, (3+bwid)*scl, (boxheight+20)*scl])
    b = translate(v=[(-115*scl), (-boxdepth+bwid*2+14.5)*scl, 40*scl]).add(b)
    a -= b

    a = translate(v=[0, (ht-edge_inset+ht_offset+20)*scl, 0]).add(a)

    return a

def base_box(scl, boxdepth, hole_depth, ht, extralen=0,
                hollow=True, inner=False, endpart=False):
    blen = boxlength+extralen
    # base hinge box
    c = union()
    nonhollowb = cube([blen*scl, (boxdepth)*scl, boxheight*scl])
    nonhollowb = translate([0, 20*scl, 0*scl]).add(nonhollowb)
    if not hollow:
        c.add(nonhollowb)
    if hollow:
        curverads={
                   D|L:(80, 0),
                   D|R:(bwid*2, 0),
                   }
        if endpart:
           curverads[T|B] = (bwid, 0) # XXX: hmm, gets covered up...
           curverads[D|B] = (hthick, 0)
        b = hollowbox(scl, blen, boxdepth, boxheight,
                        {T:-1, B: -1,
                        L:bwid, R:bwid*3, F:hthick, D:hthick},
                        curverads=curverads)
        b = translate([0, 20*scl, 0*scl]).add(b)
        c.add(b)
        if inner:
            hoffs=bwid*2
            bl = blen-bwid*2
        else:
            hoffs = -0.3
            bl = blen-lcd_outer_rad-80-bwid*2
        # cut out top front part of box (for base lid, keyboard etc.)
        h = cube([(boxlength-lcd_outer_rad-80-bwid+0.3)*scl,
                   (boxdepth+bwid+0.3)*scl,
                   (boxinset+0.3)*scl])
        h = translate(v=[(-0.3)*scl, (bwid-0.3)*scl, -0.3*scl]).add(h)
        c -= h

        if not inner:
            h = cube([(bwid+0.5)*scl, (boxdepth)*scl,
                       (boxheight)*scl])
            h = translate(v=[(blen-lcd_outer_rad-80-bwid)*scl, 20*scl,
                              -0.0*scl]).add(h)
            c += h

        if not inner:
            # add some structural support, algorithm matches with base_mid
            sstep = 140
            sdep = sstep
            while sdep <= boxlength-sstep*(2 if test else 2):
                u = intersection()
                u.add(nonhollowb)
                r = union()
                h = cube([bwid*scl, 100*scl, 100*scl])
                h = rotate([-45, 0, 0]).add(h)
                h = translate(v=[sdep*scl, 100*scl, (boxheight-2)*scl]).add(h)
                r.add(h)
                u.add(r)
                c += u
                sdep += sstep

        if pin_parts_3d:
            p = union()
            h = pin(B0)
            h = translate([20*scl, (boxdepth+10)*scl, 30*scl]).add(h)
            p += h
            h = pin(B0)
            h = translate([170*scl, (boxdepth+10)*scl, 30*scl]).add(h)
            p += h
            h = pin(B0)
            h = translate([120*scl, (boxdepth+10)*scl, 145*scl]).add(h)
            p += h
            h = pin(B0)
            h = translate([(boxlength-200)*scl, (boxdepth+10)*scl, 10*scl]).add(h)
            p += h
            h = pin(B0)
            h = translate([(boxlength-10)*scl, (boxdepth+10)*scl, 125*scl]).add(h)
            p += h
            h = pin(B0)
            h = translate([(boxlength-50)*scl,
                    (boxdepth+10)*scl, -30*scl]).add(h)
            p += h
            h = pin(B0)
            h = translate([(boxlength+38)*scl, (boxdepth+10)*scl, 38*scl]).add(h)
            p += h
            p = translate([0, 7*scl, 0]).add(p)
            c += p

    # lid at hinge end
    b = cube([(lcd_outer_rad+100+extralen-3)*scl, (boxdepth)*scl, 20*scl])
    b = translate(v=[(boxlength-lcd_outer_rad-100+3)*scl, 20*scl, 0]).add(b)
    c += b
    if extralen == 0:
        # back piece at hinge end
        b = cube([(8)*scl, (boxdepth)*scl, 70*scl])
        b = translate(v=[(boxlength-0.3)*scl, 20*scl, 40*scl]).add(b)
        c += b
    t = hinge_translate(scl).add(c)
    box = translate(v=[-boxlength*scl, (+16.5-ht*2)*scl, boxtopoffs*scl]).add(t)
    return box

def screen_adjust(b, scl, angle):
    p = lcd_panel(scl, offs=3)
    p = translate(v=[155.5*scl,61*scl,0]).add(p)
    b -= p

    p = lcd_view_area(scl, offs=3)
    p = translate(v=[155.5*scl,61*scl,lcd_doff*scl]).add(p)
    b -= p

    return hinge_rotate(scl, b, angle)


def create_laptop(t, scl, mirror, colour, part, angle):

    #if part != 1 and part != 8 and part != 6 and part != 7:
    #if part != 3 and part != 4 and part != 0 and part != 2:
    #if part != 1 and part != 7:
    #if part > 3:
    #if part > 6:
    #    return
    #if part != 0 and part != 2 and part != 4 and part != 5 and part != 3:
    #if part != 8 and part != 6 and part != 9 and part != 1 and part != 7 and \
    #    part != -0 and part != -4 and part != 10 and part != 11 and \
    #    part != 12:
    #    return
    #if part != 1 and part != 7 and part != 6 and part != 11 and \
    #    part != 0.1 and part != 8 and part != 12:
    #if part != 12 and part != 16:#and part != 8 and part != 11:
    #if part != 8 and part != -1 and part != 6:
    #if part != 8 and part != 6:
    #if part != 4 and part != 2 and part != 0 and part != 3 and part != 5:
    #if part != 0 and part != 3 and part != 2 and part != -4 and \
        #part != 1 and part != -10 and part != -8 and part != -5 and \
        #part != -7:
    if part != 0:
    #if part != 10 and part != 11 and part != -12 and part != 8 and \
    #    part != 1 and part != -9 and part != -15 and part != -1 and \
    #    part != 0 and part != 7:
    #if part != 10 and part != -11 and part != 12 and part != 8 and \
        #part != 6 and part != 9 and part != 15 and part != -1 and \
        #part != 16 and part != -7:
    #if part != 8 and part != 15 and part != 6 and part != 11:
    #if part != -6 and part != 0.1 and part != 1 and part != 7 and part != -13 \
        #and part != 2 and part != -4 and part != -3:
        return

    c = color(colour)
    c.add(t)

    b = union()

    if part == 0:
        se = screen_end(scl, lcd_end_ht)
        m = translate(v=[0, lcd_end_ht*scl,0]).add(se)
        b.add(m)
        #ht2 += lcd_end_ht

        b = screen_adjust(b, scl, angle)

    ht = 40
    if part == 1:
        b.add(base_end(scl, lcd_end_ht, ht, hinge_depth, hole_depth))
    if part == 7:
        le = lid_end(scl, lcd_end_ht, ht, hinge_depth, hole_depth)
        le = translate(v=[0, (-30)*scl,0]).add(le)
        b.add(le)

    base_ht = 40

    if part == 14:
        h = friction_hinge_inner(scl, ht)
        h = translate(v=[0, (lcd_end_ht+ht+hinge_depth)*scl,0]).add(h)
        b.add(h)

    offs = (lcd_end_ht+ht+hinge_depth+base_ht+40)
    mid_ht = 150
    wid = lcd_l/2-offs-mid_ht/2
    if part == 8:
        print "wid, offs",  wid, offs
        e = back_box_base(scl, lcd_end_ht, wid)
        e = translate(v=[0, offs*scl,0]).add(e)
        b.add(e)

    if part == 10:
        e = back_box_lid(scl, lcd_end_ht, wid, mid_ht/2)
        e = translate(v=[0, offs*scl,0]).add(e)
        b.add(e)

    if part == 11:
        e = back_box_lidfront(scl, lcd_end_ht, wid, base_ht+40, mid_ht/2)
        e = translate(v=[0, (offs-base_ht-40)*scl,0]).add(e)
        b.add(e)

    if test:
        tpanel_wid = 400.0
    else:
        tpanel_wid = 700.0
    front_lid_ht = wid+mid_ht/2-tpanel_wid/2
    if part == 15:
        #
        e = front_box_lid(scl, lcd_end_ht, front_lid_ht, extraht=(base_ht+40))
        e = translate(v=[0, (offs-base_ht-40)*scl,0]).add(e)
        b.add(e)

    if part == 16:
        #
        e = front_box_lid(scl, lcd_end_ht, tpanel_wid, extraht=0,
                        tpanel=True)
        e = translate(v=[0, (offs+front_lid_ht)*scl,0]).add(e)
        b.add(e)

    if part == 9:
        e = front_box_base(scl, lcd_end_ht, wid,
                        front_lid_ht, extraht=(base_ht+40))
        e = translate(v=[0, offs*scl,0]).add(e)
        b.add(e)

    if part == 6:
        e = base_end2(scl, lcd_end_ht, ht, base_ht, hole_depth)
        e = translate(v=[0, (lcd_end_ht+ht+hinge_depth)*scl,0]).add(e)
        b.add(e)

    if part == 12:
        e = base_mid(scl, lcd_end_ht, mid_ht, base_ht, hole_depth)
        e = translate(v=[0, (offs+wid)*scl,0]).add(e)
        b.add(e)

    numparts = 10 if test else 30
    offs = lcd_end_ht+hinge_depth
    midht = (lcd_l/2.0-offs+bwid-50.0) / numparts

    if single:
        x = 1 if part == 2 else 2
    else:
        x = 1 if part == 2 else numparts
    for i in range(x):
        m = None
        if part == 2:
            m = screen_mid1(scl, midht, hole_depth, nohinge=True,
                                fillinner=False, endpart=False,
                                indent=[0], outdent=[0],
                                cableduct=True)
        if part == 3:
            m = screen_mid1(scl, midht, hole_depth, nohinge=True,
                            endpart=True,
                            indent=[lcd_front_indent],
                            outdent=[lcd_front_indent])
        if part == 4 and i > 0:
            cableduct = i < 5
            m = screen_mid2(scl, midht, hole_depth, cableduct = cableduct)

        if m:
            m = translate(v=[0, offs*scl,0]).add(m)
            m = screen_adjust(m, scl, angle)
            b.add(m)

        offs += midht

    if part == 5:
        m = screen_mid3(scl, 100, hole_depth)
        m = translate(v=[0, (lcd_l/2+bwid-50)*scl,0]).add(m)
        m = screen_adjust(m, scl, angle)
        b.add(m)


    c = color([0.2, 0.2, 0.2, 1.0])
    c.add(b)
    t.add(c)

if __name__ == '__main__':

    animate = False
    max_open = 130
    if animate:
        rpt = 3
        angles = [0, max_open*0.25, max_open*0.5, max_open*0.75, max_open]
    else:
        rpt = 1
        angles = [0]

    for i in range(rpt):
        for angle in angles:
            t = union()
            c = [0.3, 0.5, 0.8, 0.5]
            for i in range(17):
                create_laptop(t, scl, 1.0, c, part=i, angle=angle)
            t = color(c).add(t)

            if False: # add inner parts for reference
                p = lcd_panel(scl)
                p = translate(v=[155.5*scl,61*scl,0]).add(p)
                p = hinge_rotate(scl, p, angle)
                t.add(p)
                p = ethernet(scl)
                p  = translate(v=[0, 210*scl,0]).add(p)
                t.add(p)

            if False:
                card = import_stl(filename = "eoma68.stl")
                r = rotate([90,180,-90]).add(card)
                r = translate([(lcd_w+350)*scl, 1100*scl, 135*scl]).add(r)
                t.add(r)
                pcb = cube([800*scl, 1000*scl, (12)*scl], center=True)
                r = translate([(lcd_w-80)*scl, 760*scl, 159*scl]).add(pcb)
                t.add(r)

            scad_render_to_file(t, "laptop_prog.scad")
            f = open("laptop_model.scad", "w")
            f.write("""include<laptop_prog.scad>;
            """)
            f.close()
            if i != rpt:
                time.sleep(2)
