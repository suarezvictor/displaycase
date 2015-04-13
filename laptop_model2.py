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
add_internal_parts=False

test = True
single = True


if not test:
    lcd_l = 3598.0
    lcd_w = 2100.0
    lcd_la = lcd_l-98.0
    lcd_wa = lcd_w-129.9
    lcd_d = 50
    lcd_cable_depth = 1000
else:
    # HSD070PWW1
    lcd_l = 1612
    lcd_w = 1055
    lcd_cable_depth = 500
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
lcd_inset_top = 40
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
boxheight = 120
backboxheight = boxheight+bwid*2-10
boxtopoffs = 2
boxinset = 55
hinge_depth = 70
hole_depth = hinge_depth
boxlength = lcd_w + lcd_inset_top + lcd_inset_bot 
lidfront_offs = 10
lcd_front_indent = 108
back_top_width = 170
front_top_width = 180

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
    return translate(v=[+(+lcd_inset_bot+lcd_w-50+lcd_inset_top)*scl,
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
    t = translate(v=[(-78-offs)*scl, (-40-offs)*scl, (lcd_doff+29.5-d-offs)*scl])
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

def screen_box(scl, ht, end=True, hingewall=False, back=False):
    u = union()

    ld = lcd_d+hthick+5.4

    walls = {T:hthick, L:80, R:hthick, F:-1, D:115}
    curverads={
                }
    scalecurve = {
                L|T: [0, 80],
                R|T: [0, 80]
            }
    if not back:
        curverads[L|T] = (ld-hthick, 0)
        curverads[L|D] = (hthick, 0)
    if end:
        walls[B] = hthick
        curverads.update({ R|T: (ld-hthick, 0),R|D: (hthick, 0),})
    else:
        walls[B] = -1
        curverads.update({ R|T: (ld-hthick, 0) })
    if back:
        slen = lcd_inset_bot - 30
        offs = boxlength - slen
    else:
        slen = boxlength
        offs = 0
    b = hollowbox(scl, slen, ht, ld, walls,
                    curverads=curverads, scalecurve=scalecurve)
    b = translate(v=[offs*scl, 0, -(lcd_d-30)*scl]).add(b)
    u += b

    if hingewall:
        w1 = lcd_w+lcd_inset_top+40
        c = cube([(hthick)*scl, (ht)*scl, (ld)*scl])
        c = translate(v=[(w1)*scl, 0, -30*scl]).add(c)
        u += c

    return u

def base_end_hinge(scl, ht):
    u = union()
    w = boxlength-112

    topcurve = 30
    walls = {T:hthick, L:hthick, R:-1, F:-1, D:-1, B: -1}
    curverads={
                L|T: (hthick, 0),
                R|T: (hthick, 0),
                }
    b = hollowbox(scl, back_top_width-112, ht, boxheight, walls,
                  curverads=curverads)
    b = translate(v=[(boxlength-back_top_width)*scl, 0, (55)*scl]).add(b)
    u += b

    c = shearedcube([(45.5)*scl, ht*scl, (boxheight-5)*scl],
                shear=[68*scl, 0, 0],
                innershear=[0*scl, 0, 0])
    c = rotate([0, 0, 180]).add(c)
    c = rotate([180, 0, 0]).add(c)
    c = rotate([0, 180, 0]).add(c)
    c = translate(v=[(w-48)*scl,0*scl,(hinge_offs-10)*scl]).add(c)
    u += c

    rad=35.0 + 12
    # add hinge
    c = cube([rad*scl, (ht+2)*scl, boxheight*2*scl])
    c = translate(v=[(w+25)*scl,-1*scl,(boxheight/2)*scl]).add(c)
    u -= c

    return u
    
def base_end(scl, ht):
    u = union()
    w = boxlength-3

    topcurve = 30
    walls = {T:hthick, L:hthick, R:hthick, F:-1, D:hthick}
    curverads={
                L|T: (hthick, 0),
                L|D: (boxheight-40, 0),
                R|T: (40, 0),
                R|D: (boxheight-40, 0),
                }
    scalecurve = {
                L|D: [0, 150],
                R|D: [0, 150]
            }
    walls[B] = hthick
    b = hollowbox(scl, w, ht, boxheight, walls, curverads=curverads,
                                                scalecurve=scalecurve)
    b = translate(v=[0, 0, (55)*scl]).add(b)
    u += b

    rad=35.0 + 12
    # add hinge
    c = cylinder(r=rad*scl, h=(ht)*scl, segments=50)
    c = rotate([0, 90, 90]).add(c)
    c = translate(v=[0*scl,0*scl,0]).add(c)
    t = hinge_translate(scl).add(c)
    u += t

    # block up hole
    c = cube([(ht)*scl, (rad-10)*scl, (28)*scl])
    c = rotate([0, 0, 90]).add(c)
    c = rotate([0, -90, 0]).add(c)
    c = translate(v=[-(rad-12)*scl,0*scl,0*scl]).add(c)
    t = hinge_translate(scl).add(c)
    u += t

    # add bits for screws through to base front
    c = cube([(50)*scl, (50+ht)*scl, (50)*scl])
    #c = rotate([0, 0, 90]).add(c)
    #c = rotate([0, -90, 0]).add(c)
    c = translate(v=[(150)*scl,(0)*scl,(boxheight-hthick+4)*scl]).add(c)
    u += c

    # add bits for screws through to base front
    c = cube([(50)*scl, (50+ht)*scl, (50)*scl])
    #c = rotate([0, 0, 90]).add(c)
    #c = rotate([0, -90, 0]).add(c)
    c = translate(v=[(50)*scl,(0)*scl,(56+hthick)*scl]).add(c)
    u += c

    # hollow hinge out
    c = cylinder(r=(rad-10)*scl, h=(ht)*scl, segments=50)
    c = rotate([0, 90, 90]).add(c)
    c = translate(v=[0*scl,hthick*scl,0*scl]).add(c)
    t = hinge_translate(scl).add(c)
    u -= t

    # cable access
    c = cube([(ht)*scl, (rad+80)*scl, (rad+hthick)*scl])
    c = rotate([0, 0, 90]).add(c)
    c = translate(v=[0*scl,hthick*scl,-hthick*scl]).add(c)
    t = hinge_translate(scl).add(c)
    u -= t

    # add bits for screws through to base back
    c = cube([(40)*scl, (50+ht)*scl, (50)*scl])
    c = translate(v=[(boxlength-back_top_width)*scl,(0)*scl,(56+hthick)*scl]).add(c)
    u += c
    c = cube([(50)*scl, (ht)*scl, (5)*scl])
    c = translate(v=[(boxlength-back_top_width)*scl,(0)*scl,(54+hthick)*scl]).add(c)
    u += c

    if False:
        # add screwhole
        r = cylinder(r=lcdscrewrad*scl, h=(ht+hthick+2)*scl, segments=50)
        c = rotate([90, 0, 0]).add(r)
        c = translate(v=[(boxlength-back_top_width+25)*scl,(ht+hthick+1)*scl,(65+30)*scl]).add(c)
        u -= c

    c = cube([(ht)*scl, (104)*scl, (30)*scl])
    c = rotate([0, 0, 90]).add(c)
    c = rotate([0, 10, 0]).add(c)
    c = translate(v=[-6*scl,hthick*scl,17*scl]).add(c)
    t = hinge_translate(scl).add(c)
    u -= t

    return u
    
def base_front_bottom(scl, ht):
    u = union()

    woffs = (boxheight-hthick)
    walls = {T:-1, L:-1, R:-1, F:hthick, D:hthick, B:hthick}
    curverads={
                #L|T: (hthick, 0),
                #L|D: (boxheight-hthick, 0),
                }
    b = hollowbox(scl, front_top_width-(woffs), ht, boxheight-40, walls, curverads=curverads)
    b = translate(v=[woffs*scl, 0, (95)*scl]).add(b)
    u += b

    return u
    
def base_front_top(scl, ht):
    u = union()

    walls = {T:hthick, L:hthick, R:-1, F:-1, D:hthick, B:hthick}
    curverads={
                L|T: (hthick, 0),
                L|D: (boxheight-40, 0),
                }
    scalecurve = {
                L|D: [0, 150],
                R|D: [0, 150]
            }
    b = hollowbox(scl, front_top_width, ht, boxheight, walls,
            curverads=curverads, scalecurve=scalecurve)
    b = translate(v=[0*scl, 0, 0]).add(b)
    u += b

    # add bits for screws through to base front
    c = cube([(52)*scl, (53)*scl, (52)*scl])
    #c = rotate([0, 0, 90]).add(c)
    #c = rotate([0, -90, 0]).add(c)
    c = translate(v=[(149)*scl,(-1)*scl,(boxheight-hthick-52)*scl]).add(c)
    u -= c

    # add bits for screws through to base front
    c = cube([(52)*scl, (53)*scl, (52)*scl])
    #c = rotate([0, 0, 90]).add(c)
    #c = rotate([0, -90, 0]).add(c)
    c = translate(v=[(49)*scl,(-1)*scl,(hthick)*scl]).add(c)
    u -= c

    v = union()
    u = translate(v=[0*scl, 0, (55)*scl]).add(u)
    v.add(u)
    return v
    
def base_back_bot(scl, ht, scrn_hinge_ht):
    u = union()
    w = boxlength-back_top_width

    walls = {T:hthick, L:-1, R:hthick, F:60+hthick, D:hthick, B:70}
    curverads={
                R|D: (boxheight-40, 0),
                R|T: (40, 0),
                }
    scalecurve = {
                R|D: [0, 150]
            }
    b = hollowbox(scl, back_top_width, ht, boxheight,
                    walls, curverads=curverads, scalecurve=scalecurve)
    b = translate(v=[w*scl, 0, 0]).add(b)
    u += b

    # fill in around hinge before cut-out

    c = cube([120*scl, (scrn_hinge_ht+2)*scl, 40*scl])
    c = translate(v=[(w+20)*scl,hthick*scl,(5)*scl]).add(c)
    u += c

    rad=35.0 + 12
    # add hinge
    w = boxlength-112
    c = cube([rad*3*scl, (scrn_hinge_ht+2)*scl, boxheight*1.1*scl])
    c = translate(v=[(w+25)*scl,-1*scl,(0)*scl]).add(c)
    u -= c

    c = shearedcube([(100*2)*scl, (scrn_hinge_ht+2)*scl, (hinge_offs)*scl],
                shear=[50*scl, 0, 0],
                innershear=[-15*scl, 0, 0])
    c = rotate([180, 0, 0]).add(c)
    c = rotate([0, 0, 180]).add(c)
    #c = rotate([180, 0, 0]).add(c)
    c = translate(v=[(w+225)*scl,-1*scl,(-25+hinge_offs)*scl]).add(c)
    u -= c

    # add bits for screws through to base back
    c = cube([(42)*scl, (53)*scl, (52)*scl])
    #c = rotate([0, 0, 90]).add(c)
    #c = rotate([0, -90, 0]).add(c)
    c = translate(v=[(boxlength-back_top_width-1)*scl,(-1)*scl,
                    (hthick)*scl]).add(c)
    u -= c

    # put in series of cutouts
    offs = 80
    step = (ht-60-offs) / 5 if test else 10
    while offs < (ht-step):
        # add fill-ins
        c = cube([80*scl, hthick*scl, (boxheight-hthick+2)*scl])
        c = translate(v=[(w-58)*scl, (offs-hthick)*scl, (1)*scl]).add(c)
        u += c

        c = cube([135*scl, hthick*scl, (42)*scl])
        c = translate(v=[(w-58)*scl, (offs-hthick)*scl, (1)*scl]).add(c)
        u += c

        c = touch_arc(0, (step-hthick), 40-hthick,
                            25, scl,
                      angle=0)
        c = rotate([90, 0, 0]).add(c)
        c = rotate([0, -90, 0]).add(c)
        # XXX resize needed to do something odd with openscad (fixes a bug)
        c = resize([(40-hthick)*scl, 0, 0], False).add(c)
        c = translate(v=[(boxlength-41)*scl, (offs)*scl, (40)*scl]).add(c)
        u -= c

        # cutout lower and upper arcs
        c = touch_arc(0, (step-hthick), 40-hthick,
                            25, scl,
                      angle=0)
        c = rotate([90, 0, 0]).add(c)
        c = rotate([0, -90, 0]).add(c)
        # XXX resize needed to do something odd with openscad (fixes a bug)
        c = resize([(40-hthick)*scl, 0, 0], False).add(c)
        c = translate(v=[(boxlength-41)*scl, (offs)*scl, (40)*scl]).add(c)
        u -= c

        c = touch_arc(0, (step-hthick), (boxheight-40-hthick),
                            25, scl,
                      angle=0)
        c = rotate([90, 0, 0]).add(c)
        c = rotate([0, 180, 0]).add(c)
        c = resize([(150-hthick)*scl, 0, 0], False).add(c)
        c = translate(v=[(lcd_w+69)*scl, (offs)*scl, (39.5)*scl]).add(c)
        u -= c

        offs += step
        
    # hole for back screw-support to poke through
    # XXX height is magic constant
    b = cube([(63)*scl, (62)*scl, (boxheight-38)*scl])
    b = translate(v=[(w-39)*scl, (ht-61)*scl, (14)*scl]).add(b)
    u -= b

    v = union()
    u = translate(v=[0*scl, 0, (55)*scl]).add(u)
    v.add(u)
    return v
    
def base_back_joiner(scl, ht):
    u = union()
    w = boxlength

    walls = {T:-1, L:60, R:-1, F:50, D:-1, B:50}
    curverads={
                B|L: (10, 0),
                F|L: (10, 0),
                }
    scalecurve = {
            }
    b = hollowbox(scl, 60, ht, boxheight-40,
                    walls, curverads=curverads, scalecurve=scalecurve)
    u += b

    b = cube([(90)*scl, (45)*scl, 55*scl], center=True)
    b = translate(v=[(25)*scl, (ht/2)*scl, (boxheight-40)/2*scl]).add(b)
    u -= b

    u = rotate([0, 0, 180]).add(u)

    v = union()
    u = translate(v=[(boxlength-150+60)*scl, (ht*scl), (70)*scl]).add(u)
    v.add(u)
    return v
    
def base_mid(scl, ht):
    u = union()
    w = boxlength

    walls = {T:-1, L:-1, R:hthick, F:hthick, D:hthick, B:hthick}
    curverads={
                T|R: (40, 0),
                R|D: (boxheight-40, 0),
                L|D: (boxheight-40, 0),
                }
    scalecurve = {
                R|D: [0, 150],
                L|D: [0, 150],
            }
    b = hollowbox(scl, w, ht, boxheight,
                    walls, curverads=curverads, scalecurve=scalecurve)
    u += b

    # top cutout makes shelf support for keyboard
    b = cube([(w-169)*scl, (ht+2)*scl, 41*scl])
    b = translate(v=[(-1)*scl, -1*scl, (-1)*scl]).add(b)
    u -= b

    # hole for back screw-support to poke through
    # XXX height is magic constant
    b = cube([(62)*scl, (ht+2)*scl, (boxheight-38)*scl])
    b = translate(v=[(w-151)*scl, -1*scl, (14)*scl]).add(b)
    u -= b

    v = union()
    u = translate(v=[0*scl, 0, (55)*scl]).add(u)
    v.add(u)
    return v
    
def screen_end(scl, ht):
    return screen_box(scl, ht, end=True)

def screen_edge_complete(scl, ht):
    return screen_box(scl, ht, end=False)

def screen_back_edge(scl, ht):
    b = screen_box(scl, ht, end=False, back=True)
    # TODO: this is going to need some underside supports
    # TODO: length of the cable run doesn't have to be this long
    c = touch_arc(0, lcd_cable_depth, 45,
                        25, scl,
                  angle=0)
    c = rotate([90, 0, 0]).add(c)
    c = rotate([0, -90, 0]).add(c)
    c = translate(v=[(lcd_w+70)*scl, (-1)*scl, (lcd_d-15)*scl]).add(c)
    b -= c

    return b

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
    c = translate(v=[(w-rad+10)*scl,-(ht+hthick)*scl,
                     (30+hinge_offs)*scl]).add(c)
    u -= c

    c = cube([(80)*scl, (ht+2)*scl, (lcd_d-hthick)*scl])
    c = translate(v=[(w-155)*scl,-(1)*scl,
                     (-8)*scl]).add(c)
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

    lcd_ht = 10.0
    u = union()
    p = lcd_panel(scl, offs=3)
    p = translate(v=[155.5*scl,61*scl,(lcd_ht)*scl]).add(p)
    u += p

    p = lcd_view_area(scl, offs=3)
    p = translate(v=[155.5*scl,61*scl,(lcd_doff+lcd_ht)*scl]).add(p)
    u += p

    b -= u

    if add_internal_parts:
        p = lcd_panel(scl, offs=3)
        p = translate(v=[155.5*scl,61*scl,(lcd_ht)*scl]).add(p)
        b += p

    return hinge_rotate(scl, b, angle)


def create_laptop(t, scl, mirror, colour, part, angle):

    #if part != 7 and part != 3 and part != 4 and part != -2:
    #    return
    #if part != 2 and part != 5:
        #return
    if part != 4 and part != 8 and part != 5:
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

    base_adjust_ht = scrn_end_ht+lcd_end_ht
    base_adjust_ht += scrn_hinge_ht

    centre_ht = hthick*2
    base_back_ht = (lcd_l + hthick*2 - centre_ht) / 2 - base_adjust_ht

    #if part == 5:
    #    se = base_back_top(scl, base_back_ht+scrn_hinge_ht+centre_ht/2,
    #                            scrn_hinge_ht)
    #    m = translate(v=[0, (base_adjust_ht-scrn_hinge_ht)*scl,0]).add(se)
    #    b.add(m)

    if part == 4:
        # NOTE: ... here's the other bit
        se = base_back_bot(scl, base_back_ht+scrn_hinge_ht, scrn_hinge_ht)
        m = translate(v=[0, (base_adjust_ht-scrn_hinge_ht)*scl,0]).add(se)
        b.add(m)

    adj = scrn_end_ht+lcd_end_ht+scrn_hinge_ht
    if part == 6:
        se = screen_back_edge(scl, (lcd_l-centre_ht)/2-adj+hthick)
        m = translate(v=[0, (adj)*scl,0]).add(se)
        b.add(m)
        b = screen_adjust(b, scl, angle)

    if part == 7:
        se = base_front_top(scl, base_back_ht+scrn_hinge_ht)
        m = translate(v=[0, (base_adjust_ht-scrn_hinge_ht)*scl,0]).add(se)
        b.add(m)

    base_adjust_ht += base_back_ht

    if part == 8:
        se = base_mid(scl, centre_ht)
        m = translate(v=[0, (base_adjust_ht)*scl,0]).add(se)
        b.add(m)

    base_joiner_ht = 150

    if part == 5:
        se = base_back_joiner(scl, base_joiner_ht)
        m = translate(v=[0,
                        (base_adjust_ht + centre_ht/2 - base_joiner_ht/2)*scl,
                         0]).add(se)
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

            if add_internal_parts:
                card = import_stl(filename = "eoma68.stl")
                drop_ht=20.0
                r = rotate([90,180,180]).add(card)
                r = translate([(lcd_w-250)*scl, 0*scl, (drop_ht+110)*scl]).add(r)
                t.add(r)
                kbd = cube([600*scl, (lcd_l-100)*scl, (60)*scl], center=True)
                r = translate([(lcd_w-300)*scl, lcd_l/2*scl, (drop_ht+47)*scl]).add(kbd)
                t.add(r)
                pcb = cube([800*scl, 1000*scl, (12)*scl], center=True)
                r = translate([(lcd_w-400)*scl, 520*scl, (drop_ht+134)*scl]).add(pcb)
                t.add(r)

            scad_render_to_file(t, "laptop_prog2.scad")
            f = open("laptop_model2.scad", "w")
            f.write("""include<laptop_prog2.scad>;
            """)
            f.close()
            if i != rpt:
                time.sleep(2)
