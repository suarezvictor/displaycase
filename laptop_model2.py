# Copyright (C) 2014, 2015 Luke Kenneth Casson Leighton <lkcl@lkcl.net>
# License: GPLv3+

import time
import itertools
from pyopenscad import *
from polysurface import spline_double_divide, Offset, SurfaceFromCurves
from copy import deepcopy
from pyscadutil import B0, B45, pin, shearedcube, hollowbox, touch_arc
from pyscadutil import L, R, T, D, F, B

pin_parts_3d=True

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
lcd_inset_bot = 180
lcd_gap = 3
lcd_hinge_inner_rad=70
lcd_hinge_inside_rad=70
lcd_ext_rot_angle=250
lcd_outer_rad = lcd_hinge_inner_rad+bwid
lcd_end_ht = 50 
lcd_end_offs = 20

lcdscrewrad = 29 / 2.0 # XXX: 2mm diameter thread, why 0.9mm extra????
screwrad = 32 / 2.0 # XXX: 2mm thread diameter, needs 1.2mm extra!!!
topscrewrad = 20 / 2.0 # supposed to be 3mm screw holes but 3d baaad....
boxheight = 100
backboxheight = boxheight+bwid*2-10
boxtopoffs = 2
boxinset = 55
hinge_depth = 70
hole_depth = hinge_depth
boxlength = lcd_w + lcd_inset_top + lcd_inset_bot 
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

hinge_offs = 70

def hinge_translate(scl):
    return translate(v=[+(+lcd_inset_bot+lcd_w-25)*scl,
                       0,
                        (78-lcd_d+hinge_offs)*scl])

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

def screen_box(scl, ht, end=True, hingewall=False):
    u = union()

    ld = lcd_d+hthick*2+lcd_gap*2

    walls = {T:hthick, L:80, R:hthick, F:-1, D:20}
    curverads={
                L|T: (65, 0),
                L|D: (hthick, 0),
                
                }
    if end:
        walls[B] = hthick
        curverads.update({ R|T: (65, 0),R|D: (hthick, 0),})
    else:
        walls[B] = -1
        #curverads.update({ R|T: (hthick, 65-hthick) })
        curverads.update({ R|T: (65, 0) })
    b = hollowbox(scl, boxlength, ht, ld, walls, curverads=curverads)
    b = translate(v=[0, 0, -(lcd_d-20)*scl]).add(b)
    u += b

    if hingewall:
        w1 = lcd_w+lcd_inset_top+40
        c = cube([(hthick)*scl, (ht)*scl, (ld)*scl])
        c = translate(v=[(w1)*scl, 0, -30*scl]).add(c)
        u += c

    return u

def base_end(scl, ht):
    u = union()
    w = boxlength-3

    topcurve = 30
    walls = {T:hthick, L:hthick, R:hthick, F:-1, D:-1}
    curverads={
                L|T: (hthick, 0),
                L|D: (boxheight-hthick, 0),
                R|T: (40, 0),
                R|D: (boxheight-40, 0),
                }
    walls[B] = hthick
    b = hollowbox(scl, w, ht, boxheight, walls, curverads=curverads)
    b = translate(v=[0, 0, (55)*scl]).add(b)
    u += b

    rad=35.0 + 12
    # add hinge
    c = cylinder(r=rad*scl, h=(ht)*scl, segments=50)
    c = rotate([0, 90, 90]).add(c)
    c = translate(v=[0*scl,0*scl,0]).add(c)
    t = hinge_translate(scl).add(c)
    u += t

    # hollow hinge out
    c = cylinder(r=(rad-10)*scl, h=(ht)*scl, segments=50)
    c = rotate([0, 90, 90]).add(c)
    c = translate(v=[0*scl,hthick*scl,0*scl]).add(c)
    t = hinge_translate(scl).add(c)
    u -= t

    # cable access
    c = cube([(ht)*scl, (rad+1)*scl, (rad+hthick)*scl])
    c = rotate([0, 0, 90]).add(c)
    c = translate(v=[0*scl,hthick*scl,-hthick*scl]).add(c)
    t = hinge_translate(scl).add(c)
    u -= t

    return u
    
def screen_end(scl, ht):
    return screen_box(scl, ht, end=True)

def screen_edge_complete(scl, ht):
    return screen_box(scl, ht, end=False)

def screen_hinge(scl, ht):
    u = union()
    b = screen_box(scl, ht, end=False, hingewall=False)
    u += b

    rad=35.0
    # add hinge
    c = cylinder(r=rad*scl, h=(ht+20)*scl, segments=50)
    c = rotate([0, 90, 90]).add(c)
    c = translate(v=[0*scl,-20*scl,0]).add(c)
    t = hinge_translate(scl).add(c)
    u += t

    w = lcd_w+lcd_inset_top+lcd_inset_bot
    c = shearedcube([(rad*2)*scl, ht*scl, (hinge_offs)*scl],
                shear=[50*scl, 0, 0],
                innershear=[-15*scl, 0, 0])
    c = rotate([0, 0, 180]).add(c)
    c = rotate([180, 0, 0]).add(c)
    c = translate(v=[(w-15)*scl,0*scl,(30+hinge_offs)*scl]).add(c)
    u += c

    # hollow hinge out
    c = cylinder(r=(rad-10)*scl, h=(ht+51)*scl, segments=50)
    c = rotate([0, 90, 90]).add(c)
    c = translate(v=[0*scl,-40*scl,0*scl]).add(c)
    t = hinge_translate(scl).add(c)
    u -= t

    c = shearedcube([(rad*2-25)*scl, (ht*2)*scl, (2+hinge_offs)*scl],
                shear=[55*scl, 0, 0],
                innershear=[35*scl, 0, 0])
    c = rotate([0, 0, 180]).add(c)
    c = rotate([180, 0, 0]).add(c)
    c = translate(v=[(w-rad+10)*scl,-(ht+hthick)*scl,(30+hinge_offs)*scl]).add(c)
    u -= c

    if pin_parts_3d:
        c = union()
        h = pin(B0, scl)
        h = translate([(boxlength-80)*scl, (ht-3)*scl, -25*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(boxlength-3)*scl, (ht-3)*scl, 0*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(boxlength-90)*scl, (ht-3)*scl, 140*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(boxlength-131)*scl, (ht-3)*scl, 80*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(0)*scl, (ht-3)*scl, -20*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(51)*scl, (ht-3)*scl, 60*scl]).add(h)
        c += h
        u += c

    return u
    

def screen_adjust(b, scl, angle):
    u = union()
    p = lcd_panel(scl, offs=3)
    p = translate(v=[155.5*scl,61*scl,0]).add(p)
    u += p

    p = lcd_view_area(scl, offs=3)
    p = translate(v=[155.5*scl,61*scl,lcd_doff*scl]).add(p)
    u += p

    b -= u

    return hinge_rotate(scl, b, angle)


def create_laptop(t, scl, mirror, colour, part, angle):

    #if part != 0 and part != 1:
    #    return
    if part != 2:
        return

    c = color(colour)
    c.add(t)

    b = union()

    lid_adjust_ht = 0
    base_adjust_ht = 0
    scrn_end_ht = 30
    scrn_hinge_ht = 60

    if part == 0:
        se = screen_end(scl, scrn_end_ht)
        m = translate(v=[0, 0*scl,0]).add(se)
        b.add(m)

        b = screen_adjust(b, scl, angle)

    lid_adjust_ht += scrn_end_ht

    if part == 1:
        se = screen_edge_complete(scl, lcd_end_ht)
        m = translate(v=[0, 0*scl,0]).add(se)
        b.add(m)

        b = translate(v=[0, lid_adjust_ht*scl,0]).add(b)
        b = screen_adjust(b, scl, angle)

    lid_adjust_ht += lcd_end_ht

    if part == 2:
        se = screen_hinge(scl, scrn_hinge_ht)
        m = translate(v=[0, 0*scl,0]).add(se)
        b.add(m)

        b = translate(v=[0, lid_adjust_ht*scl,0]).add(b)
        b = screen_adjust(b, scl, angle)

    lid_adjust_ht += scrn_hinge_ht

    if part == 3:
        se = base_end(scl, scrn_end_ht+lcd_end_ht)
        m = translate(v=[0, 0*scl,0]).add(se)
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
        angles = [00]

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
                r = rotate([90,180,180]).add(card)
                r = translate([(lcd_w-250)*scl, 0*scl, 110*scl]).add(r)
                t.add(r)
                pcb = cube([800*scl, 1000*scl, (12)*scl], center=True)
                r = translate([(lcd_w-400)*scl, 520*scl, 134*scl]).add(pcb)
                t.add(r)

            scad_render_to_file(t, "laptop_prog2.scad")
            f = open("laptop_model2.scad", "w")
            f.write("""include<laptop_prog2.scad>;
            """)
            f.close()
            if i != rpt:
                time.sleep(2)
