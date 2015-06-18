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
add_internal_parts=True

test = False
single = True

TPANEL_MID = 5
BASE_BACK = 4
BASE_END = 3
BASE_FRONT_TOP = 7
BASE_MID = 8
FRONT_KBD_TRAY = 12
PCB1 = 14
PCB1_SUPPORT = 17
BATTERY_SUPPORT1 = 18
COMPARTMENT_LID = 19

if not test:
    lcd_l = 3598.0
    lcd_w = 2100.0
    lcd_la = lcd_l-98.0
    lcd_wa = lcd_w-129.9
    lcd_d = 50
    lcd_cable_depth = 1000
    kbd_d = 60
    kbd_l = 3390.0
    kbd_w = 1170.0

    tpanel_w = 950.0
    tpanel_wb = 50.0
    tpanel_b_w = tpanel_w + tpanel_wb * 2
    tpanel_l = 670.0
    tpanel_l_b = tpanel_l + 150 + 132
    tpanel_h = 40

    lcd_indent = 61

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

    kbd_d = 60
    kbd_l = lcd_l-180
    kbd_w = 600

    tpanel_w = 250
    tpanel_wb = 50.0
    tpanel_b_w = tpanel_w + tpanel_wb * 2
    tpanel_l = 200
    tpanel_l_b = tpanel_l + 150
    tpanel_h = 40

    lcd_indent = 61

total_width = lcd_l  + 40

lcd_ht = 10.0
lcd_doff = 5
scl = 0.1
hthick = 12 # horizontal pieces not as thick
pcbthick = 12
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

# XXX should really be calculated from lcd width, scrn width etc.
base_end_ht = 100

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

centre_ht = 30.0
base_centre_ht = 140.0

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

def chamfered_backbox_screwholes(scl, sht, r1=22):
    # chamfered screw holes in top of lid
    c = union()
    c.add(cylinder(r=topscrewrad*1.2*scl, r1=r1*scl,
                    h=12*scl,
                    segments=50, center=True))
    d = cylinder(r=topscrewrad*scl,
                    h=(bwid+2.5+sht)*scl,
                    segments=50, center=True)
    d = translate(v=[0, 0, +(bwid+0.2+sht/2)*0.5*scl]).add(d)
    c.add(d)
    d = cylinder(r=(r1+1)*scl,
                    h=(bwid+2.5+sht)*scl,
                    segments=50, center=True)
    d = translate(v=[0, 0, (-5.8-(bwid+2.5+sht)/2)*scl]).add(d)
    c.add(d)
    c = rotate([180, 0, 0]).add(c)
    return c

def case_bolthole(scl, end):
    bht = (-lcd_d+150+boxtopoffs-boxheight)
    if end == 0:
        return translate([(120)*scl, 0*scl, bht*scl])
    elif end == 1:
        return translate([(-10+lcd_w+11)*scl, 0*scl, bht*scl])
    elif end == 2:
        return translate([(lcd_w+lcd_inset_bot-100)*scl, 0*scl,
                            bht*scl])
    elif end == 3:
        return translate([(-20+lcd_w/2.0+30)*scl, 0*scl, bht*scl])

def lid_bolthole(scl, end=True):
    if end:
        return translate([(-lcd_inset_top+89)*scl, 0*scl, (7+lcd_doff)*scl])
    else:
        return translate([(168+lcd_w)*scl, 0*scl, (7+lcd_doff)*scl])

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

def screen_box(scl, ht, end=True, hingewall=False, back=False, front=False):
    u = union()

    ld = lcd_d+hthick+5.4+9

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
    elif not front:
        walls[B] = -1
        curverads.update({ R|T: (ld-hthick, 0) })
    if back:
        slen = lcd_inset_bot - 30
        offs = boxlength - slen
    elif front:
        slen = 90
        offs = 0
    else:
        slen = boxlength
        offs = 0
    b = hollowbox(scl, slen, ht, ld, walls,
                    curverads=curverads, scalecurve=scalecurve)
    b = translate(v=[offs*scl, 0, -(lcd_d-21)*scl]).add(b)
    u += b

    if hingewall:
        w1 = lcd_w+lcd_inset_top+40
        c = cube([(hthick)*scl, (ht)*scl, (ld)*scl])
        c = translate(v=[(w1)*scl, 0, -30*scl]).add(c)
        u += c

    return u

def base_end(scl, ht, kbd_numpad_indent):
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
    walls[B] = -1 # hthick
    b = hollowbox(scl, w, ht, boxheight, walls, curverads=curverads,
                                                scalecurve=scalecurve)
    b = translate(v=[0, 0, (55)*scl]).add(b)
    u += b

    # add top strut, along entire length of base_end.
    c = union()
    b = cube([lcd_w*scl, (ht-20)*scl, 35*scl])
    b = translate(v=[(120)*scl, (0)*scl, (55)*scl]).add(b)
    c += b
    d = cube([52*scl, (ht)*scl, 37*scl])
    b = translate(v=[(lcd_w-72)*scl, (-1)*scl, (54)*scl]).add(d)
    c -= b

    u += c

    # add keyboard left support
    b = hollowbox(scl, lcd_w-tpanel_l_b-103+kbd_numpad_indent, ht+20, 35,
                {T:35, L:-1, R:-1, F:20+hthick, D:-1, B:-1},
                curverads={ T|F: (hthick, 0)})
    b = translate(v=[(lcd_w-kbd_w+23-kbd_numpad_indent)*scl, (0)*scl,
                    (55)*scl]).add(b)
    u += b

    rad=35.0 + 15
    # add hinge
    c = cylinder(r=rad*scl, h=(ht)*scl, segments=50)
    c = rotate([0, 90, 90]).add(c)
    c = translate(v=[0*scl,0*scl,0]).add(c)
    t = hinge_translate(scl).add(c)
    u += t

    c = touch_arc(0, (ht+1), (boxheight-40-hthick),
                        25, scl,
                  angle=0)
    c = rotate([90, 0, 0]).add(c)
    c = rotate([0, 180, 0]).add(c)
    c = resize([(150-hthick)*scl, 0, 0], False).add(c)
    c = translate(v=[(lcd_w+66)*scl, (hthick)*scl, (boxheight-25)*scl]).add(c)
    u -= c

    # block up hole
    c = cube([(ht)*scl, (50)*scl, (85)*scl])
    c = rotate([0, 0, 90]).add(c)
    c = rotate([0, -90, 0]).add(c)
    c = translate(v=[-(rad-12)*scl,0*scl,10*scl]).add(c)
    t = hinge_translate(scl).add(c)
    u += t

    # add bits for screws through to base front
    c = base_end_bit(scl, ht, fwd=True)
    c = translate(v=[(20)*scl,(0)*scl,(56+hthick)*scl]).add(c)
    u += c

    # add bit for hinge part to rest against when over 120 degrees
    # XXX: this might not be necessary when the spring is in place
    # have to see... also it could complicate the injection mold.
    c = shearedcube([(20)*scl, (12)*scl, (20)*scl],
                shear=[0*scl, 15*scl, 0*scl],
                innershear=[0*scl, 0*scl, 0*scl])
    c = rotate([0, 0, 180]).add(c)
    c = translate(v=[(20)*scl,(10)*scl,(0)*scl]).add(c)
    c = translate(v=[(-10)*scl,(ht-10)*scl,(28)*scl]).add(c)
    t = hinge_translate(scl).add(c)
    u += t

    # hollow hinge out
    c = cylinder(r=(rad-10)*scl, h=(ht)*scl, segments=50)
    c = rotate([0, 90, 90]).add(c)
    c = translate(v=[0*scl,hthick*scl,0*scl]).add(c)
    t = hinge_translate(scl).add(c)
    u -= t

    # add bits for screws through to base back
    v = union()
    c = cube([(60)*scl, (ht)*scl, (40)*scl])
    v.add(c)
    c = cylinder(r=40*scl, h=50*scl, segments=6, center=True)
    c = rotate([0, 0, 90]).add(c)
    c = rotate([90, 0, 0]).add(c)
    #c = rotate([0, -20, 0]).add(c)
    c = translate(v=[35*scl, (25)*scl, (35)*scl]).add(c)
    v.add(c)
    c = translate(v=[(boxlength-back_top_width-5)*scl,
                      (0)*scl, (56+hthick)*scl]).add(v)
    u += c

    # add support for keyboard corner
    h = holed_support(scl, ht-hthick-1)
    t = translate(v=[(w-300)*scl, 0, (62)*scl]).add(h)
    u += t
    
    # front keyboard tray indentation support, surrounds microsd
    c = cube([(25)*scl, (60)*scl, (boxheight-2)*scl])
    t = translate(v=[(tpanel_l_b-27)*scl, 0, (55+1)*scl]).add(c)
    u += t
    t = translate(v=[(tpanel_l_b+735)*scl, 0, (55+1)*scl]).add(c)
    u += t
    t = translate(v=[(360)*scl, 0, (55+1)*scl]).add(c)
    u += t
    # between usb ports
    t = translate(v=[(730)*scl, 0, (55+1)*scl]).add(c)
    u += t
    
    # end pcb marker, also supports bamboo panels top and bottom
    c = cube([(30)*scl, (60)*scl, (boxheight-2)*scl])
    t = translate(v=[(540)*scl, 0, (55+1)*scl]).add(c)
    u += t
    c = cube([(30)*scl, (ht+20)*scl, (30)*scl])
    t = translate(v=[(540)*scl, 0, (55+21)*scl]).add(c)
    u += t
    t = translate(v=[(tpanel_l_b-56)*scl, 0, (55+21)*scl]).add(c)
    u += t
    
    # add bits for case bolthole at front
    c = cube([(90)*scl, (ht)*scl, (70)*scl])
    c = translate(v=[(60)*scl,
                      (0)*scl, (52+hthick)*scl]).add(c)
    u += c

    # annoying bug in hollowbox, bridge across curve and straight
    c = cube([(1)*scl, (ht)*scl, (hthick)*scl])
    c = translate(v=[(149.5)*scl,
                      (0)*scl, (boxheight+55-hthick)*scl]).add(c)
    u += c

    # screw holes in box
    t = box_screwholes(scl, hthick, holes=[0, 2])
    t = translate(v=[0, 0, boxheight*scl]).add(t)
    u -= t

    s = chamfered_backbox_screwholes(scl, 20, 25)
    s = rotate([90, 0, 0]).add(s)
    s = translate(v=[0, 30*scl, boxheight*scl]).add(s)
    for hole in [0,2]:
        t = case_bolthole(scl, hole).add(s)
        u -= t

    # add screw hole for front
    c = cube([40*scl, ht*scl, boxheight*scl])
    t = translate(v=[(181)*scl, 0, (55)*scl]).add(c)
    u += t
    v = front_tray_corner(scl, 200)
    v = translate([0, scl*(ht-hthick), 0]).add(v)
    u += v

    if pin_parts_3d:
        c = union()
        h = pin(B0, scl)
        h = translate([(0)*scl, (0)*scl, 45*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(75)*scl, (0)*scl, 45*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(150)*scl, (0)*scl, 45*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(120)*scl, (0)*scl, 195*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(45)*scl, (0)*scl, 195*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(0)*scl, (0)*scl, 120*scl]).add(h)
        c += h

        h = pin(B0, scl)
        h = translate([(w-120)*scl, (0)*scl, 40*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(w)*scl, (0)*scl, 50*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(w)*scl, (0)*scl, 125*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(w-120)*scl, (0)*scl, 185*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(w-45)*scl, (0)*scl, 185*scl]).add(h)
        c += h

        c = translate([(0)*scl, (3)*scl, 0*scl]).add(c)
        
        u += c

    return u
    
def holed_support(scl, ht, sht=50, dep=60, inverse=False):
    u = union()
    if not inverse:
        # add bits for screws through to base back
        c = cube([(70)*scl, (ht)*scl, (dep)*scl])
        u += c

    d = cylinder(r=topscrewrad*1.2*scl, r1=33*scl,
                    h=21*scl,
                    segments=50, center=True)
    d = rotate([90, 0, 0]).add(d)
    d = translate(v=[70/2*scl, (ht-19/2+0.5)*scl, (55/2+5)*scl]).add(d)
    if inverse:
        u += d
    else:
        u -= d

    d = cylinder(r=topscrewrad*scl,
                    h=(sht)*scl,
                    segments=50, center=True)
    d = rotate([-90, 0, 0]).add(d)
    d = translate(v=[70/2*scl, (ht-sht/2+0.5)*scl, (55/2+5)*scl]).add(d)
    if inverse:
        u += d
    else:
        u -= d

    return u

def base_end_bit(scl, ht, fwd=False, below=False):
    u = union()
    # add bits for screws through to base back
    c = cube([(115)*scl, (18+ht)*scl, (60)*scl])
    c = translate(v=[15*scl,(0)*scl,(5)*scl]).add(c)
    u += c
    c = cube([(60)*scl, (ht)*scl, (35)*scl])
    c = translate(v=[-15*scl,(0)*scl,(-2)*scl]).add(c)
    if below:
        c = translate(v=[0*scl,(0)*scl,(50)*scl]).add(c)
    u += c

    # chamfered screw-hole through to joiner
    s = chamfered_backbox_screwholes(scl, 20)
    s = rotate([0, -90, 0]).add(s)
    if fwd:
        s = rotate([0, 0, 180]).add(s)
        s = translate(v=[(25)*scl, (0)*scl, (0)*scl]).add(s)
    b = translate(v=[(8)*scl, (ht+25)*scl, (25)*scl]).add(s)
    #u -= b

    return u

def base_front_arc(scl, ht):
    c = touch_arc(0, ht, (boxheight-40-hthick),
                        25, scl,
                  angle=0)
    c = rotate([90, 0, 0]).add(c)
    c = rotate([0, 180, 0]).add(c)
    c = rotate([0, 0, 180]).add(c)
    c = resize([(151-hthick)*scl, 0, 0], False).add(c)
    return c

def base_front_fillin(scl, ht):
    u = union()
    c = cube([80*scl, ht*scl, (boxheight-hthick+2)*scl])
    c = translate(v=[(100)*scl, (0)*scl, (1)*scl]).add(c)
    u += c

    c = cube([(front_top_width-hthick)*scl, ht*scl, (42)*scl])
    c = translate(v=[(hthick)*scl, (0)*scl, (1)*scl]).add(c)
    u += c
    return u

def base_mid_cutout(u, scl, ht, offs):
    c = cube([50*scl, (hthick*3+4)*scl, (boxheight-hthick*2)*scl])
    c = translate(v=[(tpanel_l_b-50)*scl, (offs+ht/2-(hthick*3+4)/2)*scl,
                (hthick)*scl]).add(c)
    u += c
    c = cube([90*scl, (hthick+4)*scl, (boxheight)*scl])
    c = translate(v=[(tpanel_l_b-60)*scl, (offs+ht/2-(hthick+4.)/2)*scl,
                (58)*scl]).add(c)
    u -= c
    c = cube([90*scl, (hthick+4)*scl, (boxheight)*scl])
    c = translate(v=[(tpanel_l_b)*scl, (offs+ht/2-(hthick+4.)/2)*scl,
                (28)*scl]).add(c)
    u -= c
    return u

def battery_support1(scl, ht, tpanel_offset):
    u = union()
    kbd_inset = 38.0
    sdep = (boxheight-hthick-pcbthick-kbd_inset-3)
    holder_ht = 80.0

    tpanel_box_l = 150
    # main strut going from back base to tpanel
    c = cube([(boxlength - tpanel_l_b - 170+30+18)*scl,
                    ht*scl, (boxheight-hthick-kbd_inset)*scl])
    c = translate(v=[(tpanel_l_b-30)*scl, (holder_ht-ht)*scl,
                    (kbd_inset)*scl]).add(c)
    u += c

    # screw holder, done in 2 parts so that it's easier to calculate heights
    # first part joins others together
    c = cube([(70)*scl, holder_ht*scl, (boxheight-hthick-kbd_inset)*scl])
    c = translate(v=[(tpanel_l_b-30)*scl, (0)*scl,
                (kbd_inset)*scl]).add(c)
    #u += c
    # second part is flush with kbd holder
    c = cube([(tpanel_box_l)*scl, holder_ht*scl, (sdep+15)*scl])
    c = translate(v=[(tpanel_l_b-tpanel_box_l)*scl, (0)*scl,
                (22)*scl]).add(c)
    u += c
    # third part goes down to bamboo panel
    c = cube([(tpanel_box_l)*scl, holder_ht*scl, 20*scl])
    c = translate(v=[(tpanel_l_b-tpanel_box_l)*scl, (0)*scl,
                (boxheight-20-hthick)*scl]).add(c)
    u += c
    # finally a cut-out for the kbd tray slot
    c = cube([(104)*scl, 70*scl, (20)*scl])
    c = translate(v=[(19+tpanel_l_b-tpanel_box_l)*scl, (11)*scl,
                (21)*scl]).add(c)
    u -= c

    # screw holes in top for touchpanel
    d = cylinder(r=topscrewrad*scl,
                    h=(55)*scl,
                    segments=50, center=True)
    t = translate(v=[(tpanel_l_b-75)*scl, (40)*scl, (50)*scl]).add(d)
    u -= t

    v = union()
    u = translate(v=[0*scl, 0, (55)*scl]).add(u)
    v.add(u)
    return v
    
def pcb1_support(scl, ht, tpanel_offset):
    u = union()
    kbd_inset = 38.0
    sdep = (boxheight-hthick-pcbthick-kbd_inset-3)
    holder_ht = 80.0

    tpanel_box_l = 150
    # main strut going from back base to tpanel
    c = cube([(boxlength - tpanel_l_b - 170+30+18)*scl,
                    ht*scl, (boxheight-hthick-kbd_inset)*scl])
    c = translate(v=[(tpanel_l_b-30)*scl, (holder_ht-ht)*scl,
                    (kbd_inset)*scl]).add(c)
    u += c
    # secondary strut with pcb edge lock
    c = cube([(boxlength - tpanel_l_b - 170+tpanel_box_l)*scl,
                    (holder_ht)*scl, (sdep-40)*scl])
    c = translate(v=[(tpanel_l_b-tpanel_box_l)*scl, (0)*scl,
                    (kbd_inset+40)*scl]).add(c)
    u += c

    # screw holder, done in 3 parts so that it's easier to calculate heights
    # first part is flush with main strut
    c = cube([(tpanel_box_l)*scl, holder_ht*scl, sdep*scl])
    c = translate(v=[(tpanel_l_b-tpanel_box_l)*scl, (0)*scl,
                (kbd_inset)*scl]).add(c)
    u += c
    # second part goes up to underside of tpanel
    c = cube([(tpanel_box_l)*scl, holder_ht*scl, 10*scl])
    c = translate(v=[(tpanel_l_b-tpanel_box_l)*scl, (0)*scl,
                (tpanel_h+1)*scl]).add(c)
    u += c
    # third part goes down to bamboo panel
    c = cube([(tpanel_box_l)*scl, holder_ht*scl, 20*scl])
    c = translate(v=[(tpanel_l_b-tpanel_box_l)*scl, (0)*scl,
                (boxheight-20-hthick)*scl]).add(c)
    u += c

    # screw holes in top for touchpanel
    d = cylinder(r=topscrewrad*scl,
                    h=(55)*scl,
                    segments=50, center=True)
    t = translate(v=[(tpanel_l_b-75)*scl, (40)*scl, (50)*scl]).add(d)
    u -= t

    # cut-out for front kbd tray
    w = tpanel_b_w 
    b = cube([(84)*scl, (63)*scl, (27)*scl])
    b = translate(v=[(w-200)*scl, (-1)*scl, (68)*scl]).add(b)
    u -= b
    b = cube([(40)*scl, (63)*scl, (37)*scl])
    b = translate(v=[(w-193)*scl, (-1)*scl, (48)*scl]).add(b)
    u -= b

    v = union()
    u = translate(v=[0*scl, 0, (55)*scl]).add(u)
    v.add(u)
    return v
    
def tpanel_mid(scl, ht, ht_offset):
    """
    TODO:
    * put screwhole down into base_mid
    * remove some stuff on the back underside (near kbd)
    """
    u = union()

    walls = {T:40, L:hthick, R:20, F:20, D:-1, B:20}
    curverads={
                L|T: (hthick, 0),
                R|T: (hthick, 0),
                }
    # hthick is thickness of bamboo laminate
    b = hollowbox(scl, tpanel_l_b, ht, boxheight-hthick, walls,
            curverads=curverads)
    u += b

    # front cut-out matching base_front_top
    c = cube([tpanel_l*scl, tpanel_w*scl, (42)*scl])
    c = translate(v=[(100)*scl, ((ht-tpanel_w)/2)*scl, (-1)*scl]).add(c)
    u -= c

    # keyboard tray indent
    b = kbd_tray_indent(scl)
    t = translate(v=[(tpanel_l_b-19)*scl, (ht-282)*scl, (16)*scl]).add(b)
    u -= t

    # inner cut-out for actual touchpanel
    # XXX TODO: add curved edges (use a hollowbox as the cutout)
    c = cube([181*scl, (ht+2)*scl, (150)*scl])
    c = translate(v=[(-1)*scl, (-1)*scl, (40)*scl]).add(c)
    u -= c

    # lengthways support (keeps tpanel from bending)
    c = shearedcube([33*scl, ht*scl, (40)*scl],
                shear=[0*scl, 0*scl, 0],
                innershear=[15*scl, 0*scl, 0])
    c = translate(v=[(63)*scl, 0*scl, (38)*scl]).add(c)
    u += c

    # cutout for underside of panel (reduce plastic usage)
    c = cube([tpanel_l_b*scl, (ht+2)*scl, (150)*scl])
    c = translate(v=[(250)*scl, (-1)*scl, (60)*scl]).add(c)
    u -= c

    # wings for screw-holes to fit with front base
    d = shearedcube([(60)*scl, (40)*scl, (86)*scl],
            shear=[0*scl, 0*scl, 0],
            innershear=[-32*scl, 0*scl, 0])
    d = rotate([0, -90, 0]).add(d)
    d = rotate([0, 0, -90]).add(d)
    c = translate(v=[(181)*scl, (-85)*scl, (48)*scl]).add(d)
    u += c
    d = rotate([0, 0, 180]).add(d)
    c = translate(v=[(181+40)*scl, (ht+85)*scl, (48)*scl]).add(d)
    u += c

    # cut-out to match pcb1_support
    w = tpanel_b_w 
    l = 0
    c = cube([(160)*scl, (90)*scl, (20)*scl])
    b = translate(v=[(w-260)*scl, (0)*scl, (tpanel_h-3)*scl]).add(c)
    u += b
    b = translate(v=[(w-260)*scl, (ht-90)*scl, (tpanel_h-3)*scl]).add(c)
    u += b
    c = cube([(160)*scl, (82)*scl, (93)*scl])
    b = translate(v=[(w-250)*scl, (-1)*scl, (tpanel_h-3)*scl]).add(c)
    u -= b
    b = translate(v=[(w-250)*scl, (ht-82+1)*scl, (tpanel_h-3)*scl]).add(c)
    u -= b

    # cut-out to match right kbd tray
    c = cube([(104)*scl, (82)*scl, (93)*scl])
    b = translate(v=[(w-229)*scl, (ht-82+1)*scl, (20)*scl]).add(c)
    u -= b

    # matches screw-hole in front base
    u = indented_screwhole(scl, u, (182), -40, 75, -90)
    u = indented_screwhole(scl, u, (182), ht+40, 75, -90)

    # screw-holes into front base
    s = chamfered_backbox_screwholes(scl, 50)
    s = rotate([-180, 0, 0]).add(s)
    b = translate(v=[(40)*scl, (ht-40)*scl, (+20)*scl]).add(s)
    u -= b
    b = translate(v=[(40)*scl, (40)*scl, (+20)*scl]).add(s)
    u -= b
    b = translate(v=[(40)*scl, (ht/2-50-ht_offset)*scl, (+20)*scl]).add(s)
    u -= b
    b = translate(v=[(40)*scl, (ht/2+50-ht_offset)*scl, (+20)*scl]).add(s)
    u -= b
    # and into pcb1_support
    b = translate(v=[(tpanel_l_b-75)*scl, (40)*scl, (+20)*scl]).add(s)
    u -= b
    b = translate(v=[(tpanel_l_b-75)*scl, (ht-40)*scl, (+11)*scl]).add(s)
    u -= b
    # and into base_mid
    b = translate(v=[(tpanel_l_b-75)*scl, (ht/2-ht_offset)*scl,
                     (+20)*scl]).add(s)
    u -= b

    # half-way point support for top front bamboo panel
    c = cube([(100)*scl, (90)*scl, (boxheight-hthick*2)*scl])
    b = translate(v=[(w)/2*scl, (-8)*scl, (hthick)*scl]).add(c)
    u += b
    b = translate(v=[(w)/2*scl, (ht+8-90)*scl, (hthick)*scl]).add(c)
    u += b
    
    if pin_parts_3d:
        c = union()
        h = pin(B0, scl)
        h = translate([(0)*scl, (0)*scl, 0*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(0)*scl, (0)*scl, -ht*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(tpanel_l_b)*scl, (0)*scl, -ht*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(tpanel_l_b)*scl, (0)*scl, 0*scl]).add(h)
        c += h

        c = rotate([90, 0, 0]).add(c)
        c = translate([(0)*scl, (0)*scl, 3*scl]).add(c)

        h = cube([6*scl, 55*scl, 50*scl])
        h = translate([(197)*scl, (ht+30)*scl, 0*scl]).add(h)
        c += h
        h = cube([6*scl, 55*scl, 50*scl])
        h = translate([(197)*scl, (-85)*scl, 0*scl]).add(h)
        c += h

        u += c

    v = union()
    u = translate(v=[0*scl, 0, (55)*scl]).add(u)
    v.add(u)
    return u

def base_front_top(scl, ht, ht_offset):
    u = union()

    tpanel_ht = ht+ht_offset
    walls = {T:hthick, L:hthick, R:-1, F:80, D:hthick, B:105}
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
    c = cube([(120)*scl, (22)*scl, (64)*scl])
    c = shearedcube([135*scl, (64)*scl, (22)*scl],
                shear=[0*scl, 0*scl, 0],
                innershear=[15*scl, 0*scl, 0])
    c = rotate([0, -90, 0]).add(c)
    c = rotate([90, 0, 0]).add(c)
    c = rotate([0, 0, -90]).add(c)
    c = translate(v=[(32+135)*scl,(-1)*scl,(16)*scl]).add(c)
    u -= c

    # tpanel cutout
    c = shearedcube([60*scl, (tpanel_b_w+3)*scl, (43)*scl],
                shear=[0*scl, 0*scl, 0],
                innershear=[15*scl, 0*scl, 0])
    c = translate(v=[(60)*scl, (tpanel_ht-(tpanel_b_w/2))*scl,
                                (38)*scl]).add(c)
    u -= c
    c = shearedcube([32*scl, (tpanel_b_w+3)*scl, (43)*scl],
                shear=[0*scl, 0*scl, 0],
                innershear=[8*scl, 0*scl, 0])
    c = rotate([0, 0, 180]).add(c)
    c = translate(v=[(148)*scl, (tpanel_ht+(tpanel_b_w/2+3))*scl,
                        (38)*scl]).add(c)
    u -= c

    # put in series of cutouts
    fthick = 8
    offs = 110-hthick+fthick
    if test:
        num_steps = 4.0
    else:
        if ht_offset > 0:
            num_steps = 22.0
        else:
            num_steps = 17.0
    step = (tpanel_ht-tpanel_b_w/2-100-offs) / num_steps
    while offs < (tpanel_ht-step-tpanel_b_w/2-55):
        # add fill-ins
        c = base_front_fillin(scl, fthick)
        c = translate(v=[(0)*scl, (offs-fthick)*scl, (0)*scl]).add(c)
        u += c

        # remove curve arc
        c = base_front_arc(scl, step-fthick)
        c = translate(v=[(151)*scl, (offs+step-fthick)*scl, (39.5)*scl]).add(c)
        u -= c

        offs += step
        
    # remove bit more from base
    c = base_front_arc(scl, tpanel_b_w/2-65)
    c = translate(v=[(151)*scl, (tpanel_ht-80)*scl, (39.5)*scl]).add(c)
    #u -= c

    # add fillin for touchpanel
    c = base_front_fillin(scl, 95)
    c = translate(v=[(0)*scl, (tpanel_ht-tpanel_b_w/2-95)*scl, (0)*scl]).add(c)
    u += c

    # and support wall
    c = cube([30*scl, (tpanel_b_w/2-ht_offset+25)*scl, (boxheight-50)*scl])
    c = translate(v=[(150)*scl, (tpanel_ht-tpanel_b_w/2-85)*scl,
                        (40)*scl]).add(c)
    u += c

    # screw holes in box
    t = box_screwholes(scl, hthick, holes=[0], h=120)
    t = translate(v=[0, 0, (boxheight-55)*scl]).add(t)
    u -= t

    # add hexagonal bolt hole support for a nut to sit in
    c = cube([100*scl, 20*scl, 46*scl], center=True)
    c = translate(v=[(50)*scl, (85)*scl, (boxheight-55)*scl]).add(c)
    t = case_bolthole(scl, 0).add(c)
    u -= t
    c = cylinder(r=27.0*scl, h=20*scl, center=True, segments=6)
    c = rotate([0, 90, 90]).add(c)
    c = rotate([0, 30, 0]).add(c)
    t = case_bolthole(scl, 0).add(c)
    t = translate(v=[(0)*scl, (85)*scl, (boxheight-55)*scl]).add(t)
    u -= t

    # screw holes in top for touchpanel
    d = cylinder(r=topscrewrad*scl,
                    h=(55)*scl,
                    segments=50, center=True)
    t = translate(v=[(40)*scl, (ht-50)*scl, (50)*scl]).add(d)
    u -= t
    t = translate(v=[(40)*scl, (tpanel_ht-tpanel_b_w/2+40)*scl, 
                        (50)*scl]).add(d)
    u -= t
    t = rotate([0, 90, 0]).add(d)
    t = translate(v=[(160)*scl, (ht-base_centre_ht/2-30)*scl, 
                        (73)*scl]).add(t)
    u -= t

    # remove bit for touchpanel
    c = cube([(tpanel_b_w+1-50)*scl, (tpanel_l+2-ht_offset)*scl, 
                        (tpanel_h+1)*scl])
    c = translate(v=[(-1)*scl, (tpanel_ht-tpanel_b_w/2-1)*scl, 
                        (-1)*scl]).add(c)
    u -= c

    # lower screw hole for keyboard corner joiner
    t = holed_support(scl, 50, inverse=True)
    t = rotate([0, 0, -90]).add(t)
    b = translate(v=[(130)*scl, (73)*scl, (35)*scl]).add(t)
    u -= b
    # and one for tpanel_mid
    b = translate(v=[(130)*scl, ((tpanel_ht-tpanel_b_w/2-5))*scl, (44)*scl]).add(t)
    u -= b

    if True:
        offs = base_centre_ht / 2.0
        # dovetail cuts to fit base_mid
        # XXX height is magic constant
        b = shearedcube([(40)*scl, (20)*scl, (33)*scl],
                shear=[0*scl, 0*scl, 0],
                innershear=[10*scl, 0*scl, 0])
        b = rotate([0, -90, 0]).add(b)
        c = translate(v=[(181)*scl, (ht-offs-4)*scl,
                                        (48)*scl]).add(b)
        u -= c
        b = rotate([180, 0, 0]).add(b)
        b = translate(v=[(181)*scl, (ht-offs+16)*scl, (112)*scl]).add(b)
        u -= b

    if pin_parts_3d:
        c = union()
        h = pin(B0, scl)
        h = translate([(ht)*scl, (-3)*scl, 10*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(ht+75)*scl, (-3)*scl, 80*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(ht)*scl, (-3)*scl, 150*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(ht/2-38)*scl, (-3)*scl, -5*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(ht/2+38)*scl, (-3)*scl, -5*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(ht/2-38)*scl, (-3)*scl, 120*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(ht/2+38)*scl, (-3)*scl, 120*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(0)*scl, (-3)*scl, -15*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(0)*scl, (-3)*scl, 130*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(-75)*scl, (-3)*scl, 55*scl]).add(h)
        c += h
        c = rotate([0, 0, 90]).add(c)
        c = translate([(front_top_width-6)*scl, (0)*scl, 0*scl]).add(c)
        
        u += c

    v = union()
    u = translate(v=[0*scl, 0, (55)*scl]).add(u)
    v.add(u)
    return v
    
def base_back_bot(scl, ht, scrn_hinge_ht, toffs):
    u = union()
    w = boxlength-back_top_width

    walls = {T:hthick, L:-1, R:hthick, F:97+hthick+base_centre_ht/2,
                                        D:hthick, B:70}
    curverads={
                R|D: (boxheight-40, 0),
                R|T: (40, 0),
                }
    scalecurve = {
                R|D: [0, 150]
            }
    b = hollowbox(scl, back_top_width, ht+base_centre_ht/2, boxheight,
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

    # put in series of cutouts
    fthick = 8
    offs = 80-hthick+fthick
    step = (ht-100-offs) / (4.0 if test else 15.0)
    while offs < (ht-step-10):
        # add fill-ins
        c = cube([80*scl, fthick*scl, (boxheight-hthick+2)*scl])
        c = translate(v=[(w-58)*scl, (offs-fthick)*scl, (1)*scl]).add(c)
        u += c

        c = cube([135*scl, fthick*scl, (42)*scl])
        c = translate(v=[(w-58)*scl, (offs-fthick)*scl, (1)*scl]).add(c)
        u += c

        c = touch_arc(0, (step-fthick), 40-hthick,
                            25, scl,
                      angle=0)
        c = rotate([90, 0, 0]).add(c)
        c = rotate([0, -90, 0]).add(c)
        # XXX resize needed to do something odd with openscad (fixes a bug)
        c = resize([(40-hthick)*scl, 0, 0], False).add(c)
        c = translate(v=[(boxlength-41)*scl, (offs)*scl, (40)*scl]).add(c)
        u -= c

        # cutout lower and upper arcs
        c = touch_arc(0, (step-fthick), 40-hthick,
                            25, scl,
                      angle=0)
        c = rotate([90, 0, 0]).add(c)
        c = rotate([0, -90, 0]).add(c)
        # XXX resize needed to do something odd with openscad (fixes a bug)
        c = resize([(40-hthick)*scl, 0, 0], False).add(c)
        c = translate(v=[(boxlength-41)*scl, (offs)*scl, (40)*scl]).add(c)
        u -= c

        c = touch_arc(0, (step-fthick), (boxheight-40-hthick),
                            25, scl,
                      angle=0)
        c = rotate([90, 0, 0]).add(c)
        c = rotate([0, 180, 0]).add(c)
        c = resize([(150-hthick)*scl, 0, 0], False).add(c)
        c = translate(v=[(lcd_w+69)*scl, (offs)*scl, (39.5)*scl]).add(c)
        u -= c

        offs += step
        
    # ok these are for the pcb1_support and battery_support1
    # they extend all the way to the back (for injection molding)
    offs = ht + toffs - tpanel_l_b/2 +10
    if toffs < 0:
        offs += 50
    b = union()
    c = touch_arc(0, (50), (boxheight-40-hthick),
                        25, scl, angle=0)
    c = rotate([90, 0, 0]).add(c)
    c = rotate([0, 180, 0]).add(c)
    c = resize([(150-hthick)*scl, 0, 0], False).add(c)
    b += c
    c = cube([60*scl, 50*scl, (boxheight-30)*scl])
    c = translate(v=[-20*scl, (0)*scl, (-15)*scl]).add(c)
    b += c
    c = cube([168*scl, 50*scl, (16)*scl])
    c = translate(v=[-20*scl, (0)*scl, (-15)*scl]).add(c)
    b += c
    b = translate(v=[(lcd_w+69)*scl, (offs)*scl, (39.5)*scl]).add(b)

    u += b

    # ... cutout for the actual support, the rest was housing for the cutout
    c = cube([30*scl, 37*scl, (boxheight-47)*scl])
    c = translate(v=[-22*scl, (7)*scl, (-3)*scl]).add(c)
    c = translate(v=[(lcd_w+69)*scl, (offs)*scl, (39.5)*scl]).add(c)
    u -= c

    # add support for keyboard corner
    t = holed_support(scl, 50)
    t = rotate([0, 0, 90]).add(t)
    t = translate(v=[(w-8)*scl, (197)*scl, (5)*scl]).add(t)
    u += t
    
    # lower screw hole for keyboard corner joiner
    t = holed_support(scl, 50, inverse=True)
    t = rotate([0, 0, 90]).add(t)
    b = translate(v=[(w-8)*scl, (10)*scl, (35)*scl]).add(t)
    u -= b

    # slot to fit a nut into
    c = cube([70*scl, 50*scl, 80*scl], center=True)
    c = translate(v=[(lcd_w+85)*scl, (100)*scl, (45)*scl]).add(c)
    u += c
    c = cube([100*scl, 20*scl, 46*scl], center=True)
    c = translate(v=[(-50)*scl, (85)*scl, (boxheight-55)*scl]).add(c)
    t = case_bolthole(scl, 2).add(c)
    u -= t
    c = cylinder(r=27.0*scl, h=20*scl, center=True, segments=6)
    c = rotate([0, 90, 90]).add(c)
    c = rotate([0, 30, 0]).add(c)
    t = case_bolthole(scl, 2).add(c)
    t = translate(v=[(0)*scl, (85)*scl, (boxheight-55)*scl]).add(t)
    u -= t

    # screw holes in box
    t = box_screwholes(scl, hthick, holes=[2], h=120)
    t = translate(v=[0, 0, (boxheight-55)*scl]).add(t)
    u -= t

    # fit base_mid
    b = cube([(188)*scl, (62)*scl, (42)*scl])
    b = translate(v=[(w-61)*scl, (ht-61)*scl, (boxheight-41)*scl]).add(b)
    u -= b
    b = cube([(188)*scl, (base_centre_ht/2+62)*scl, (boxheight+50)*scl])
    b = translate(v=[(w-61+77)*scl, (ht-61)*scl, (40)*scl]).add(b)
    u -= b
    b = cube([(188)*scl, (base_centre_ht/2+62)*scl, (boxheight)*scl])
    b = translate(v=[(w-61)*scl, (ht)*scl, (40)*scl]).add(b)
    u -= b

    # screw-holes into base_mid
    s = chamfered_backbox_screwholes(scl, 50)
    s = rotate([-180, 0, 0]).add(s)
    b = translate(v=[(w+55)*scl, (ht+30)*scl, (20)*scl]).add(s)
    u -= b
    b = translate(v=[(w-20)*scl, (ht-30)*scl, (45)*scl]).add(s)
    u -= b

    # add lock-in to base_mid
    c = shearedcube([(20)*scl, (35)*scl, (16)*scl],
                shear=[0, 10*scl, 0, 0],
                innershear=[0*scl, 0, 0])
    c = rotate([0, 0, 90]).add(c)
    c = rotate([90, 0, 0]).add(c)
    c = translate(v=[(w+79)*scl,(ht-46)*scl,(52)*scl]).add(c)
    u += c

    if pin_parts_3d:
        c = union()
        h = pin(B0, scl)
        h = translate([(ht+25)*scl, (-3)*scl, -25*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(ht+25)*scl, (-3)*scl, 65*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(ht-30)*scl, (-3)*scl, 140*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(ht/2-38)*scl, (-3)*scl, -5*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(ht/2+38)*scl, (-3)*scl, -5*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(ht/2-38)*scl, (-3)*scl, 120*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(ht/2+38)*scl, (-3)*scl, 120*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(-30)*scl, (-3)*scl, 62*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(0)*scl, (-3)*scl, 140*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(0)*scl, (-3)*scl, -16*scl]).add(h)
        c += h
        c = rotate([0, 0, 90]).add(c)
        c = translate([(w-58)*scl, (0)*scl, 0*scl]).add(c)
        
        u += c

    v = union()
    u = translate(v=[0*scl, 0, (55)*scl]).add(u)
    v.add(u)
    return v
    
def front_mid_joiner(scl, ht):
    u = union()
    w = boxlength

    b = cube([(62)*scl, (ht)*scl, 32*scl], center=True)
    u += b

    b = cylinder(r=screwrad*1.2/2*scl, h=(50)*scl, center=True, segments=50)
    c = translate(v=[4*scl, -50*scl,0]).add(b)
    u -= c
    c = translate(v=[4*scl, 50*scl,0]).add(b)
    u -= c

    v = union()
    u = translate(v=[(131)*scl, (ht/2*scl), (136)*scl]).add(u)
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
    b = hollowbox(scl, 54, ht, boxheight-46,
                    walls, curverads=curverads, scalecurve=scalecurve)
    b = translate(v=[(-52/2)*scl, (-ht/2)*scl, -(boxheight-46)/2*scl]).add(b)
    u += b

    b = cube([(90)*scl, (45)*scl, 45*scl], center=True)
    u -= b

    b = cylinder(r=screwrad*1.2/2*scl, h=(50)*scl, center=True, segments=50)
    b = rotate([0, 90, 0]).add(b)
    c = translate(v=[4*scl, -50*scl,0]).add(b)
    u -= c
    c = translate(v=[4*scl, 50*scl,0]).add(b)
    u -= c

    u = rotate([0, 0, 180]).add(u)

    v = union()
    u = translate(v=[(boxlength-150+56)*scl, (ht*scl), (72)*scl]).add(u)
    u = translate(v=[(-26)*scl, -(ht/2)*scl, (boxheight-44)/2*scl]).add(u)
    v.add(u)
    return v
    
def base_mid(scl, ht):
    u = union()
    w = boxlength-150

    walls = {T:-1, L:-1, R:hthick, F:hthick, D:8, B:hthick}
    curverads={
                R|D: (boxheight-40, 0),
                }
    scalecurve = {
                R|D: [0, 150],
            }
    b = hollowbox(scl, w, ht, boxheight-40,
                    walls, curverads=curverads, scalecurve=scalecurve)
    b = translate(v=[(150)*scl, 0*scl, 40*scl]).add(b)
    u += b

    # couple of wings on the side for back base to screw into
    walls[F] = 60
    walls[B] = 60
    b = hollowbox(scl, 170, ht+120, boxheight-40,
                    walls, curverads=curverads, scalecurve=scalecurve)
    b = translate(v=[(w-20)*scl, -60*scl, 40*scl]).add(b)
    u += b

    # end wall for tpanel_mid to lock into
    v = union()
    # wings for screw-holes to fit with front base
    d = shearedcube([(50)*scl, (40)*scl, (76)*scl],
            shear=[0*scl, 0*scl, 0],
            innershear=[-25*scl, 0*scl, 0])
    d = rotate([0, 90, 0]).add(d)
    d = rotate([0, 0, 90]).add(d)
    c = translate(v=[(180+40)*scl, (-75)*scl, (90)*scl]).add(d)
    v += c
    d = rotate([0, 0, 180]).add(d)
    c = translate(v=[(180)*scl, (ht+75)*scl, (90)*scl]).add(d)
    v += c
    d = cube([40*scl, (base_centre_ht)*scl, (boxheight-42)*scl])
    c = translate(v=[(tpanel_l_b)*scl, (0)*scl, (40)*scl]).add(d)
    v += c
    c = translate(v=[(180)*scl, (0)*scl, (40)*scl]).add(d)
    v += c
    u += v

    # chamfered screw hole through to base_front
    s = chamfered_backbox_screwholes(scl, 50)
    s = rotate([0, 90, 0]).add(s)
    t = translate(v=[(200)*scl, (-30)*scl, (73)*scl]).add(s)
    u -= t
    t = translate(v=[(200)*scl, (base_centre_ht+30)*scl, (73)*scl]).add(s)
    u -= t

    # hole for back screw-support to poke through
    # XXX height is magic constant
    b = cube([(86)*scl, (61)*scl, (41)*scl])
    b = translate(v=[(w-31)*scl, -(61)*scl, (39)*scl]).add(b)
    u -= b
    b = translate(v=[(0)*scl, (ht+61)*scl, (0)*scl]).add(b)
    u -= b

    # dovetail cuts to fit into front base
    # XXX height is magic constant
    b = shearedcube([(50)*scl, (ht+2)*scl, (31)*scl],
            shear=[0*scl, 0*scl, 0],
            innershear=[10*scl, 0*scl, 0])
    b = rotate([0, 90, 0]).add(b)
    b = translate(v=[(149)*scl, -1*scl, (65)*scl]).add(b)
    u -= b
    b = rotate([180, 0, 0]).add(b)
    b = translate(v=[(0)*scl, (ht)*scl, (160)*scl]).add(b)
    u -= b

    # locking cut-out for back_box_base
    c = cube([(50)*scl, (20)*scl, 25*scl])
    b = translate(v=[(w+70)*scl, -61*scl, (50)*scl]).add(c)
    u -= b
    b = translate(v=[(w+70)*scl, (ht+41)*scl, (50)*scl]).add(c)
    u -= b

    # diagonal cross-walls for internal stiffness
    fthick = 6
    offs = 210#tpanel_l_b+40
    step = (w-160-offs) / (8.0 if test else 28.0)
    steps = []
    while offs < (w-step):
        steps.append((offs, boxheight-39-2))
        offs += step

    #steps.append((210, boxheight-39-2))
    #steps.append((280, boxheight-59-2))

    for (offs, ch) in steps:
        hoff = (boxheight-39-2) - ch
        d = cube([fthick*scl, 150*scl, ch*scl])
        c = rotate([0, 0, -30]).add(d)
        c = translate(v=[(offs)*scl, (hthick/2)*scl, (40+hoff)*scl]).add(c)
        u += c
        c = rotate([0, 0, 30]).add(d)
        c = translate(v=[(offs+75)*scl, (hthick/2)*scl, (40+hoff)*scl]).add(c)
        u += c

    # fill in end for diagonals to mesh to
    c = cube([(40)*scl, (ht)*scl, (boxheight-39-hthick)*scl])
    c = translate(v=[(w-20)*scl, (0)*scl, (40)*scl]).add(c)
    u += c
    
    # cutout for tpanel_mid to drop into
    c = cube([34*scl, (base_centre_ht+4)*scl, (60)*scl])
    c = translate(v=[(tpanel_l_b-32)*scl, (ht/2-(base_centre_ht+4.)/2)*scl,
                (0)*scl]).add(c)
    u -= c

    # fillin for tpanel_mid screwhole
    c = cube([(50)*scl, (ht)*scl, (boxheight-42)*scl])
    c = translate(v=[(tpanel_l_b-100)*scl, (0)*scl, (40)*scl]).add(c)
    u += c
    
    # screw holes in top for back_box_base
    d = cylinder(r=topscrewrad*scl,
                    h=(65)*scl,
                    segments=50, center=True)
    t = translate(v=[(w+93)*scl, (30)*scl, (50)*scl]).add(d)
    u -= t
    t = translate(v=[(w+93)*scl, (ht-30)*scl, (50)*scl]).add(d)
    u -= t
    t = translate(v=[(w+18)*scl, (-30)*scl, (boxheight-40)*scl]).add(d)
    u -= t
    t = translate(v=[(w+18)*scl, (ht+30)*scl, (boxheight-40)*scl]).add(d)
    u -= t
    # and for tpanel_mid
    t = translate(v=[(tpanel_l_b-75)*scl, (ht/2)*scl, (60)*scl]).add(d)
    u -= t

    if pin_parts_3d:
        c = union()
        h = pin(B0, scl)
        h = translate([(265)*scl, (0)*scl, 10*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(185)*scl, (0)*scl, -(ht+10)*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(160)*scl, (0)*scl, -ht/2*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(185)*scl, (0)*scl, 10*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(265)*scl, (0)*scl, -(ht+10)*scl]).add(h)
        c += h

        h = pin(B0, scl)
        h = translate([(w-50)*scl, (0)*scl, -(ht+15)*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(w-50)*scl, (0)*scl, (15)*scl]).add(h)
        c += h

        h = pin(B0, scl)
        h = translate([(w+177)*scl, (0)*scl, -(ht+45)*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(w+177)*scl, (0)*scl, (45)*scl]).add(h)
        c += h

        h = pin(B0, scl)
        h = translate([(tpanel_l_b+65)*scl, (0)*scl, 32*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(tpanel_l_b+65)*scl, (0)*scl, -(ht+32)*scl]).add(h)
        c += h
        
        c = rotate([90, 0, 0]).add(c)
        c = translate([(0)*scl, (0)*scl, (boxheight-3)*scl]).add(c)

        h = cube([6*scl, 56*scl, 25*scl])
        h = translate([(180)*scl, (ht-1)*scl, 95*scl]).add(h)
        c += h
        h = translate([(34)*scl, (0)*scl, 0*scl]).add(h)
        c += h
        h = cube([6*scl, 56*scl, 25*scl])
        h = translate([(180+0)*scl, (-55)*scl, 95*scl]).add(h)
        c += h
        h = translate([(34)*scl, (0)*scl, 0*scl]).add(h)
        c += h

        step = (ht+120-6) / 7.0
        offs = -60
        while offs < ht+60:
            h = cube([145*scl, 7*scl, (boxheight-40)*scl])
            h = translate([w*scl, (offs)*scl, 40*scl]).add(h)
            c += h
            offs += step

        h = cube([91*scl, (ht+124)*scl, 95*scl])
        h = translate([(w-1)*scl, (-61)*scl, 0*scl]).add(h)
        c -= h
        h = cube([20*scl, (ht+120)*scl, 6*scl])
        h = translate([(w+125)*scl, (-60)*scl, (boxheight-6)*scl]).add(h)
        c += h
        
        u += c

    v = union()
    u = translate(v=[0*scl, 0, (55)*scl]).add(u)
    v.add(u)
    return v
    
def screen_mid(scl, ht):
    u = union()
    b = screen_box(scl, ht, end=False)
    u += b

    # cutouts for connectors
    d = cube([(28)*scl, (ht+4)*scl, (35)*scl])
    c = translate(v=[18*scl, (-2)*scl, (5)*scl]).add(d)
    u -= c
    c = translate(v=[(lcd_w+160)*scl, (-2)*scl, (-5)*scl]).add(d)
    u -= c
    d = cube([(25)*scl, (ht+2)*scl, (40)*scl])
    c = translate(v=[(lcd_w+75)*scl, (-1)*scl, (-8)*scl]).add(d)
    u -= c
    c = translate(v=[55*scl, (-1)*scl, (-8)*scl]).add(d)
    u -= c

    if pin_parts_3d:
        c = union()
        h = pin(B0, scl)
        h = translate([(boxlength-62)*scl, (3)*scl, -60*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(boxlength+15)*scl, (3)*scl, 3*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(boxlength-18)*scl, (3)*scl, 80*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(boxlength-95)*scl, (3)*scl, 80*scl]).add(h)
        c += h

        h = pin(B0, scl)
        h = translate([(47)*scl, (3)*scl, -60*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(-30)*scl, (3)*scl, 8*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(30)*scl, (3)*scl, 85*scl]).add(h)
        c += h

        h = pin(B0, scl)
        h = translate([(boxlength/2)*scl, (3)*scl, -45*scl]).add(h)
        c += h

        u += c

    return u

def screen_end(scl, ht, lcd_end_ht):
    u = union()
    b = screen_box(scl, ht, end=True)
    u += b

    c = cylinder(r=28.5*scl, h=(20)*scl, center=True, segments=6)
    c = rotate([0, 90, 90]).add(c)
    c = translate(v=[0, ht*scl,0]).add(c)
    t = lid_bolthole(scl, end=True).add(c)
    u += t

    # bolt-hole
    for end in [True, False]:
        c = cylinder(r=lcdscrewrad*scl, h=(ht+81)*scl, center=True, segments=50)
        c = rotate([0, 90, 90]).add(c)
        t = lid_bolthole(scl, end=end).add(c)
        u -= t

    b = screen_edge_complete(scl, lcd_end_ht)
    b = translate(v=[0, ht*scl,0]).add(b)
    u += b

    # lock-in to screen_hinge part
    d = cube([45*scl, 20*scl, 37*scl])
    c = translate(v=[(lcd_w+79)*scl, (ht+lcd_end_ht-10)*scl,
                (hthick-3.6-16)*scl]).add(d)
    u += c

    rad=54.0
    # remove hinge
    c = cylinder(r=rad*scl, h=(ht+lcd_end_ht+2)*scl, segments=50)
    c = rotate([0, 90, 90]).add(c)
    c = translate(v=[0*scl,-1*scl,0]).add(c)
    t = hinge_translate(scl).add(c)
    u -= t

    if pin_parts_3d:
        c = union()
        h = pin(B0, scl)
        h = translate([(boxlength-62)*scl, (3)*scl, -45*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(boxlength+15)*scl, (3)*scl, 3*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(boxlength-18)*scl, (3)*scl, 80*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(boxlength-95)*scl, (3)*scl, 80*scl]).add(h)
        c += h

        h = pin(B0, scl)
        h = translate([(62)*scl, (3)*scl, -45*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(-15)*scl, (3)*scl, 3*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(62)*scl, (3)*scl, 80*scl]).add(h)
        c += h

        h = pin(B0, scl)
        h = translate([(boxlength/2)*scl, (3)*scl, 80*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(boxlength/2)*scl, (3)*scl, -45*scl]).add(h)
        c += h

        u += c

    return u


def screen_edge_complete(scl, ht):
    u = union()
    b = screen_box(scl, ht, back=True, end=False)
    u += b

    # bolt-hole
    c = cylinder(r=lcdscrewrad*scl, h=(ht+81)*scl, center=True, segments=50)
    c = rotate([0, 90, 90]).add(c)
    t = lid_bolthole(scl, end=False).add(c)
    u -= t

    return u

def screen_front_edge(scl, ht):
    # main box
    b = screen_box(scl, ht, end=False, front=True)

    # ok, remove just a tiny bit from the lcd edge, for two reasons:
    # (1) so that 3d printing works (too much overhang)
    # (2) so that the centre (wooden) laminate has something to hook onto
    d = shearedcube([(24)*scl, (ht+2)*scl, (31)*scl],
            shear=[0*scl, 0*scl, 0],
            innershear=[-23*scl, 0*scl, 0])
    c = translate(v=[98*scl, (-1)*scl, (-38)*scl]).add(d)
    b -= c

    # remove interior
    c = touch_arc(0, ht-155, 45,
                        25, scl,
                  angle=0)
    c = rotate([-90, 0, 0]).add(c)
    c = rotate([0, -90, 0]).add(c)
    c = resize([(60)*scl, 0, 0], False).add(c)
    c = translate(v=[(76)*scl, (ht-65)*scl, (lcd_d-15)*scl]).add(c)
    b -= c

    fthick = 6
    offs = 70-hthick+fthick
    step = (ht-160-offs) / (8.0 if test else 16.0)
    while offs < (ht-step):
        c = touch_arc(0, fthick, 45,
                            25, scl,
                      angle=0)
        c = rotate([-90, 0, 0]).add(c)
        c = rotate([0, -90, 0]).add(c)
        c = resize([(60)*scl, 0, 0], False).add(c)
        c = translate(v=[(76)*scl, (offs+step-fthick)*scl, (lcd_d-15)*scl]).add(c)
        b += c

        offs += step
        
    c = cylinder(r=29.5*scl, h=(24)*scl, center=True, segments=6)
    c = rotate([0, 90, 90]).add(c)
    c = translate(v=[0, 3*scl,0]).add(c)
    t = lid_bolthole(scl, end=True).add(c)
    b -= t

    # bolt-hole
    c = cylinder(r=lcdscrewrad*scl, h=(140)*scl, center=True, segments=50)
    c = rotate([0, 90, 90]).add(c)
    t = lid_bolthole(scl, end=True).add(c)
    b -= t

    # slot to fit a nut into
    c = cube([100*scl, 20*scl, 46*scl], center=True)
    c = translate(v=[(45)*scl, (60)*scl, (0)*scl]).add(c)
    t = lid_bolthole(scl, end=True).add(c)
    b -= t
    c = cylinder(r=27.0*scl, h=20*scl, center=True, segments=6)
    c = rotate([0, 90, 90]).add(c)
    c = rotate([0, 30, 0]).add(c)
    t = lid_bolthole(scl, end=True).add(c)
    t = translate(v=[(0)*scl, (60)*scl, (0)*scl]).add(t)
    b -= t

    # matching screen mid (front)
    d = shearedcube([(24)*scl, (centre_ht/2+2)*scl, (31)*scl],
            shear=[0, -12*scl, 0],
            innershear=[0, 0*scl, 0])
    c = translate(v=[20*scl, (ht-1)*scl, (7)*scl]).add(d)
    b += c

    # cutout for locking part
    d = cube([(25)*scl, (55)*scl, (40)*scl])
    c = translate(v=[55*scl, (ht-50)*scl, (-8)*scl]).add(d)
    b -= c
    d = cube([(55)*scl, (30)*scl, (40)*scl])
    c = translate(v=[30*scl, (ht-50)*scl, (-8)*scl]).add(d)
    b -= c

    if pin_parts_3d:
        c = union()
        h = cube([25*scl, 6*scl, 55*scl])
        h = translate([(50)*scl, (ht-6)*scl, -12*scl]).add(h)
        c += h
        h = cube([25*scl, 6*scl, 55*scl])
        h = translate([(50)*scl, (ht-37)*scl, -12*scl]).add(h)
        c += h

        h = cube([7*scl, 25*scl, 65*scl])
        h = translate([(45)*scl, (-24)*scl, -18*scl]).add(h)
        c += h
        h = cube([7*scl, 25*scl, 52*scl])
        h = translate([(67)*scl, (-24)*scl, -5*scl]).add(h)
        c += h
        h = cube([7*scl, 25*scl, 52*scl])
        h = translate([(22)*scl, (-24)*scl, -5*scl]).add(h)
        c += h

        b += c

    return b

def screen_back_edge(scl, ht):
    b = screen_box(scl, ht, end=False, back=True)
    # ok, remove just a tiny bit from the lcd edge, for two reasons:
    # (1) so that 3d printing works (too much overhang)
    # (2) so that the centre (wooden) laminate has something to hook onto
    d = shearedcube([(24)*scl, (ht+2)*scl, (31)*scl],
            shear=[0*scl, 0*scl, 0],
            innershear=[-43*scl, 0*scl, 0])
    d = rotate([0, 0, 180]).add(d)
    c = translate(v=[(lcd_w+54)*scl, (ht+10)*scl, (-37)*scl]).add(d)
    b -= c

    # TODO: this is going to need some underside supports
    # TODO: length of the cable run doesn't have to be this long
    fthick = 8
    offs = 80-hthick+fthick
    step = (ht-160-offs) / (8.0 if test else 20.0)
    while offs < (ht-step-55):
        c = touch_arc(0, step-fthick, 50,
                            25, scl,
                      angle=0)
        c = rotate([90, 0, 0]).add(c)
        c = rotate([0, -90, 0]).add(c)
        c = resize([(70)*scl, 0, 0], False).add(c)
        c = translate(v=[(lcd_w+140)*scl, (offs)*scl, (lcd_d-15)*scl]).add(c)
        b -= c
        c = cube([100*scl, (step-fthick)*scl, 50*scl])
        c = translate(v=[(lcd_w+41)*scl, (offs)*scl, (lcd_d-15-50)*scl]).add(c)
        b -= c
        offs += step
    c = hollowbox(scl, 100, (ht-80), 50,
                {T:50, L:40, R:30, F:1, D:18, B:1},
                curverads={ T|R: (35, 0)})
    c = translate(v=[(lcd_w+20)*scl, (-1)*scl, (lcd_d-15-46)*scl]).add(c)
    b -= c

    # bolt-hole
    c = cylinder(r=lcdscrewrad*scl, h=(100)*scl, center=True, segments=50)
    c = rotate([0, 90, 90]).add(c)
    t = lid_bolthole(scl, end=False).add(c)
    b -= t

    # slot to fit a nut into
    c = cube([100*scl, 20*scl, 46*scl], center=True)
    c = translate(v=[(-45)*scl, (40)*scl, (0)*scl]).add(c)
    t = lid_bolthole(scl, end=False).add(c)
    b -= t
    c = cylinder(r=27.0*scl, h=20*scl, center=True, segments=6)
    c = rotate([0, 90, 90]).add(c)
    c = rotate([0, 30, 0]).add(c)
    t = lid_bolthole(scl, end=False).add(c)
    t = translate(v=[(0)*scl, (40)*scl, (0)*scl]).add(t)
    b -= t

    # matching screen mid (back)
    d = shearedcube([(26)*scl, ((centre_ht/2+2))*scl, (31)*scl],
            shear=[0, -12*scl, 0],
            innershear=[0, 0*scl, 0])
    c = translate(v=[(lcd_w+161)*scl, (ht-1)*scl, (-3)*scl]).add(d)
    b += c

    # cutout for locking part
    d = cube([(25)*scl, (55)*scl, (40)*scl])
    c = translate(v=[(lcd_w+75)*scl, (ht-50)*scl, (-8)*scl]).add(d)
    b -= c
    d = cube([(45)*scl, (30)*scl, (40)*scl])
    c = translate(v=[(lcd_w+75)*scl, (ht-50)*scl, (-8)*scl]).add(d)
    b -= c

    # lock-in to screen_hinge part
    d = shearedcube([30*scl, 15*scl, 9*scl],
            shear=[0,-9*scl,0],
            innershear=[0,0*scl,0])
    c = rotate([0, 0, 180]).add(d)
    c = translate(v=[(30)*scl, (10)*scl, (0)*scl]).add(c)
    c = translate(v=[(lcd_w+90)*scl, (-6)*scl, (lcd_d-hthick-9.6)*scl]).add(c)
    b += c
    c = rotate([0, 0, 180]).add(d)
    c = translate(v=[(30)*scl, (10)*scl, (-6)*scl]).add(c)
    c = translate(v=[(lcd_w+80)*scl, (-6)*scl, (-12)*scl]).add(c)
    b += c
    d = cube([30*scl, 8*scl, 15*scl])
    c = translate(v=[(lcd_w+90)*scl, (0)*scl, (lcd_d-hthick-9.6)*scl]).add(d)
    b += c

    if pin_parts_3d:
        c = union()
        h = cube([25*scl, 6*scl, 60*scl])
        h = translate([(lcd_w+80)*scl, (0)*scl, -18*scl]).add(h)
        c += h
        h = cube([25*scl, 6*scl, 60*scl])
        h = translate([(lcd_w+80)*scl, (50)*scl, -18*scl]).add(h)
        c += h
        h = cube([25*scl, 6*scl, 60*scl])
        h = translate([(lcd_w+80)*scl, (ht/2-20)*scl, -18*scl]).add(h)
        c += h
        h = cube([25*scl, 6*scl, 60*scl])
        h = translate([(lcd_w+80)*scl, (ht/4-10)*scl, -18*scl]).add(h)
        c += h
        h = cube([25*scl, 6*scl, 60*scl])
        h = translate([(lcd_w+80)*scl, (420)*scl, -18*scl]).add(h)
        c += h
        h = cube([25*scl, 6*scl, 60*scl])
        h = translate([(lcd_w+80)*scl, (ht-6)*scl, -18*scl]).add(h)
        c += h

        b += c

    return b

def screen_hinge(scl, ht):
    u = union()
    b = screen_box(scl, ht, end=False, back=True, hingewall=False)
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
    c = cylinder(r=(rad-12)*scl, h=(ht+51)*scl, segments=50)
    c = rotate([0, 90, 90]).add(c)
    c = translate(v=[0*scl,-40*scl,0*scl]).add(c)
    t = hinge_translate(scl).add(c)
    u -= t

    # bolt-hole
    c = cylinder(r=lcdscrewrad*scl, h=(ht+81)*scl, center=True, segments=50)
    c = rotate([0, 90, 90]).add(c)
    t = lid_bolthole(scl, end=False).add(c)
    u -= t

    c = shearedcube([(rad*2-32)*scl, (ht*2)*scl, (30+hinge_offs)*scl],
                shear=[70*scl, 0, 0],
                innershear=[46*scl, 0, 0])
    c = rotate([0, 0, 180]).add(c)
    c = rotate([180, 0, 0]).add(c)
    c = translate(v=[(w-rad+8)*scl,-(ht+hthick)*scl,
                     (30+hinge_offs)*scl]).add(c)
    u -= c

    c = cube([(80)*scl, (ht+2)*scl, (lcd_d-hthick)*scl])
    c = translate(v=[(w-155)*scl,-(1)*scl,
                     (-8)*scl]).add(c)
    u -= c

    # lock-in cutout to screen_hinge part
    d = shearedcube([42*scl, 13*scl, 11*scl],
            shear=[0,-11*scl,0],
            innershear=[0,0*scl,0])
    c = rotate([0, 0, 180]).add(d)
    c = translate(v=[(32)*scl, (11)*scl, (0)*scl]).add(c)
    c = translate(v=[(lcd_w+89)*scl, (ht-10)*scl,
                    (lcd_d-hthick-8.6)*scl]).add(c)
    u -= c
    d = shearedcube([42*scl, 14*scl, 11*scl],
            shear=[0,11*scl,0],
            innershear=[0,0*scl,0])
    c = rotate([0, 0, 180]).add(d)
    c = translate(v=[(32)*scl, (12)*scl, (-6)*scl]).add(c)
    c = translate(v=[(lcd_w+79)*scl, (ht-10)*scl, (-12)*scl]).add(c)
    u -= c

    if pin_parts_3d:
        c = union()
        h = pin(B0, scl)
        h = translate([(boxlength-70)*scl, (ht-3)*scl, -55*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(boxlength+7)*scl, (ht-3)*scl, 0*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(boxlength-90)*scl, (ht-3)*scl, 140*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(boxlength-131)*scl, (ht-3)*scl, 90*scl]).add(h)
        c += h
        u += c

    return u
    
def indented_screwhole(scl, u, x, y, z, rot=0, depth=16):
    d = cylinder(r=topscrewrad*1.2*scl, r1=28*scl,
                    h=17*scl,
                    segments=50, center=True)
    d = rotate([90, 0, 0]).add(d)
    s = translate(v=[(0)*scl, (-9)*scl, (0)*scl]).add(d)
    s = rotate([0, 0, rot]).add(s)
    s = translate(v=[(x)*scl, (y)*scl, (z)*scl]).add(s)
    u += s
    s = chamfered_backbox_screwholes(scl, depth)
    s = translate(v=[(0)*scl, (0)*scl, (3)*scl]).add(s)
    s = rotate([90, 0, 0]).add(s)
    s = rotate([0, 0, 180]).add(s)
    s = rotate([0, 0, rot]).add(s)
    s = translate(v=[(x)*scl, (y)*scl, (z)*scl]).add(s)
    u -= s
    return u

def kbd_tray_indent(scl):
    return cube([(30)*scl, (95)*scl, (24.1)*scl])

def front_kbd_tray(scl, ht, woffs, hoffs):
    """
    TODO: L-piece, move micro-sd, have it go right into the corner
    TODO: cut-out to slot into base_end (at top)
    """

    u = union()
    w = lcd_w-kbd_w-158
    l = ht-tpanel_b_w/2+hthick
    if woffs < 0:
        h = 40
    else:
        h = boxheight - hthick - pcbthick - 2

    b = hollowbox(scl, 25, l, h,
                {T:-1, L:-1, R:25, F:hthick, D:-1, B:hthick*2},
                curverads={ T|R: (hthick, 0)})
    b = translate(v=[(w-25+woffs)*scl, 0*scl, (0)*scl]).add(b)
    u += b

    if woffs < 0:
        b = hollowbox(scl, 25-woffs, hoffs+8, h,
                    {T:hthick, L:-woffs-26, R:25, F:hthick, D:-1, B:hthick*2},
                    curverads={ T|R: (hthick, 0), T|B: (hthick, 0)})
        b = translate(v=[(w-25+woffs)*scl, (l-8-hoffs)*scl, (0)*scl]).add(b)
        u += b
    
    # extra bit for kbd corner support
    b = hollowbox(scl, hthick, 20+hthick, h,
                {T:-1, L:-1, R:-1, F:20+hthick, D:-1, B:-1},
                curverads={ T|F: (hthick, 0)})
    b = translate(v=[(w-hthick+woffs)*scl, (0)*scl, (0)*scl]).add(b)
    u += b
    b = cube([(hthick+22)*scl, (hthick+1)*scl, (hthick+1)*scl])
    b = translate(v=[(w-hthick-21+woffs)*scl, -1*scl, (-1)*scl]).add(b)
    u -= b

    # floor L-piece, stabilise and allow sticking to PCB
    b = cube([(26)*scl, (l)*scl, (hthick)*scl])
    b = translate(v=[(w-1+woffs)*scl, 0*scl, (h-hthick)*scl]).add(b)
    if woffs < 0:
        b = translate(v=[(-49)*scl, 0*scl, (0)*scl]).add(b)
    u += b

    if woffs < 0:
        cutht = hthick+1
    else:
        cutht = 21
    # cutouts for bamboo panel
    b = cube([(25)*scl, (2+l)*scl, cutht*scl])
    b = translate(v=[(w-25-hthick+woffs)*scl, (hthick)*scl, (-1)*scl]).add(b)
    u -= b

    # screw holes in top for touchpanel
    d = cylinder(r=topscrewrad*scl,
                    h=(55)*scl,
                    segments=50, center=True)

    # keyboard tray indents
    b = kbd_tray_indent(scl)
    if woffs >= 0:
        t = translate(v=[(w-19)*scl, (l-132)*scl, (16)*scl]).add(b)
        u -= t
        t = translate(v=[(w-19)*scl, (134)*scl, (16)*scl]).add(b)
        u -= t
    else:
        t = translate(v=[(w-19+woffs)*scl, (l-312-hoffs)*scl, (16)*scl]).add(b)
        u -= t
        t = translate(v=[(w-19+woffs)*scl, (148)*scl, (16)*scl]).add(b)
        u -= t

    if woffs >= 0:
        # lock-in to tpanel
        b = cube([(95)*scl, (30)*scl, (h-40)*scl])
        b = translate(v=[(w-70)*scl, (l-30)*scl, (40)*scl]).add(b)
        u += b
        b = cube([(80)*scl, (110)*scl, (h-70)*scl])
        b = translate(v=[(w-100)*scl, (l-50)*scl, (70)*scl]).add(b)
        u += b
        b = cube([(36)*scl, (90)*scl, (40)*scl])
        b = translate(v=[(w-93)*scl, (l-30)*scl, (50)*scl]).add(b)
        u += b

        t = translate(v=[(w-75)*scl, (l+40)*scl, (50)*scl]).add(d)
        u -= t
    else:
        b = cube([(100)*scl, (68)*scl, (18)*scl])
        b = translate(v=[(w-129)*scl, (l-1)*scl, (22)*scl]).add(b)
        u += b

        t = translate(v=[(w-75)*scl, (l+40)*scl, (19)*scl]).add(d)
        u -= t

    if pin_parts_3d:
        c = union()
        h = pin(B0, scl)
        h = translate([(0)*scl, (-3)*scl, 25*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(w)*scl, (-3)*scl, 25*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(w+200)*scl, (-3)*scl, 25*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(w+200)*scl, (-3)*scl, -50*scl]).add(h)
        c += h

        h = pin(B0, scl)
        h = translate([w*scl, (-3)*scl, -l*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([45*scl, (-3)*scl, (-l-32)*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([45*scl, (-3)*scl, (45-l)*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([-32*scl, (-3)*scl, (65-l)*scl]).add(h)
        c += h
        c = rotate([90, 0, 0]).add(c)
        c = translate([0*scl, (0)*scl, (boxheight-hthick)*scl]).add(c)
        
        u += c

    
    v = union()
    u = translate(v=[(180)*scl, 0, (55)*scl]).add(u)
    v.add(u)
    return v

def front_tray_corner(scl, ht):
    """
    this part basically locks into place (relies on surrounding parts)
    rather than acts as structural support, with the exception of
    the base_end and front_base screws, which help stabilise both
    those two parts.

    the bamboo panels basically rest on this part, internally.
    """

    u = union()
    w = lcd_w-kbd_w-158
    l = ht

    b = cube([40*scl, 85*scl, (boxheight-hthick-21)*scl])
    b = translate(v=[(1)*scl, 0*scl, (21)*scl]).add(b)
    u += b

    # screwhole into front base
    u = indented_screwhole(scl, u, 1, 50, 67, -90, 40)

    v = union()
    u = translate(v=[(180)*scl, 0, (55)*scl]).add(u)
    v.add(u)
    return v

def back_kbd_corner(scl, ht):

    u = union()
    w = boxlength-back_top_width

    b = hollowbox(scl, 150, 20+hthick, boxheight-hthick,
                {T:-1, L:-1, R:-1, F:20+hthick, D:-1, B:-1},
                curverads={ T|F: (hthick, 0)})
    b = translate(v=[(w-150)*scl, -hthick*scl, (0)*scl]).add(b)
    u += b

    b = hollowbox(scl, 20, ht, boxheight-hthick,
                {T:-1, L:20, R:-1, F:-1, D:-1, B:-1},
                curverads={ T|L: (hthick, 0)})
    b = translate(v=[(w-20)*scl, 0*scl, (0)*scl]).add(b)
    u += b
    b = cube([(200+50)*scl, (hthick+1)*scl, (hthick+1)*scl])
    b = translate(v=[(w-201)*scl, (-hthick-1)*scl, (-1)*scl]).add(b)
    u -= b

    u = indented_screwhole(scl, u, (w-98), -hthick+6, 39)
    u = indented_screwhole(scl, u, (w-1), 232, 37, 90)

    u = indented_screwhole(scl, u, (w-1), 45, 67, 90)

    if pin_parts_3d:
        c = union()
        h = pin(B0, scl)
        h = translate([(ht-38)*scl, (-3)*scl, 33*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(ht+33)*scl, (-3)*scl, -43*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(ht+33)*scl, (-3)*scl, -127*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(82)*scl, (-3)*scl, 33*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(0)*scl, (-3)*scl, 33*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(0)*scl, (-3)*scl, -43*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(ht-45)*scl, (-3)*scl, -210*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(ht+33)*scl, (-3)*scl, -210*scl]).add(h)
        c += h
        c = rotate([90, 0, 0]).add(c)
        c = translate([(w-200)*scl, (0)*scl, (boxheight-hthick)*scl]).add(c)
        
        u += c

    v = union()
    u = translate(v=[0, 0, (55)*scl]).add(u)
    v.add(u)
    return v

def compartment_lid(scl, ht, tpanel_offset, kbd_offs):

    u = union()

    # main panel, create staggered part for bamboo panel fill-in
    b = cube([(tpanel_l_b-180-hthick-2)*scl, (ht-2)*scl, (20)*scl])
    b = translate(v=[1*scl, 1*scl, (0)*scl]).add(b)
    u += b
    b = cube([(tpanel_l_b-180-hthick-30-kbd_offs)*scl, (ht-60)*scl, (13)*scl])
    b = translate(v=[30*scl, 30*scl, (-1)*scl]).add(b)
    u -= b
    b = cube([(tpanel_l_b-180-hthick-50-kbd_offs)*scl, (ht-80)*scl, (22)*scl])
    b = translate(v=[40*scl, 40*scl, (-1)*scl]).add(b)
    u -= b

    # cut out corner for tpanel_mid joiner
    b = cube([50*scl, 12*scl, (12)*scl])
    b = translate(v=[-1*scl, (ht-11)*scl, (15)*scl]).add(b)
    u -= b

    v = union()
    u = translate(v=[180*scl, 0, (55)*scl]).add(u)
    v.add(u)

    return v


def pcb1(scl):

    t = union()

    # PCB
    pcb = union()
    b = cube([1610*scl, 1200*scl, (12)*scl])
    b = translate([(40)*scl, 0*scl, 0*scl]).add(b)
    pcb += b
    b = cube([901*scl, 1100*scl, (30)*scl])
    b = translate([(1580)*scl, 440*scl, -10*scl]).add(b)
    pcb -= b
    b = cube([581*scl, 1200*scl, (30)*scl])
    b = translate([(-1)*scl, 245*scl, -10*scl]).add(b)
    pcb -= b
    # extra small cutout to fit pcb1_support at corner
    b = cube([40*scl, 90*scl, (30)*scl])
    b = translate([(570)*scl, (1200-55)*scl, -10*scl]).add(b)
    pcb -= b

    r = translate([(30)*scl, 15*scl, 0]).add(pcb)
    t.add(r)

    s = union()
    b = cube([700*scl, 986*scl, (58)*scl])
    s += b
    b = cube([540*scl, 861*scl, (60)*scl])
    b = translate([(110)*scl, -1*scl,
                (-1)*scl]).add(b)
    s -= b

    cpu_offs = 660
    r = translate([(cpu_offs)*scl, 0*scl,
                (-58)*scl]).add(s)
    t.add(r)

    # EOMA68 CPU Card 
    card = import_stl(filename = "eoma68.stl")
    r = rotate([90,180,180]).add(card)
    r = translate([(600+cpu_offs)*scl, 0*scl,
                (-19)*scl]).add(r)
    t.add(r)

    if False:
        # XXX DC Jack to move onto pcb2, on other side, with PMIC and charger
        # DC Jack
        j = cube([80*scl, 93*scl, (52)*scl])
        r = translate([(870)*scl, 0*scl,
                    (-52)*scl]).add(j)
        t.add(r)

    # Micro SD
    j = cube([160.7*scl, 151.1*scl, (18)*scl])
    r = translate([(1400)*scl, 0*scl,
                (-18)*scl]).add(j)
    t.add(r)

    # LVDS IC
    j = cube([141*scl, 83*scl, (12)*scl])
    r = translate([(1400)*scl, 700*scl,
                (-12)*scl]).add(j)
    t.add(r)

    # Headphone jack
    j = cube([60*scl, 93*scl, (52)*scl])
    r = translate([(1590)*scl, 0*scl,
                (-52)*scl]).add(j)
    t.add(r)

    # USB x 2
    u = cube([132*scl, 137*scl, (61.5)*scl])
    r = translate([(115)*scl, 130*scl, (-61.5)*scl]).add(u)
    t.add(r)
    r = translate([(260)*scl, 0*scl, (-61.5)*scl]).add(u)
    t.add(r)
    r = translate([(405)*scl, 130*scl, (-61.5)*scl]).add(u)
    t.add(r)

    v = union()
    t = translate([(320)*scl, 0*scl, (150)*scl]).add(t)
    v.add(t)
    return t

def screen_adjust(b, scl, angle):

    u = union()
    p = lcd_panel(scl, offs=3)
    p = translate(v=[155.5*scl,61*scl,(lcd_ht)*scl]).add(p)
    u += p

    p = lcd_view_area(scl, offs=3)
    p = translate(v=[155.5*scl,61*scl,(lcd_doff+lcd_ht)*scl]).add(p)
    u += p

    b -= u

    return hinge_rotate(scl, b, angle)

def mirror_part(se, scl, offs):
    if False:
        return union()
    m = mirror([0, 0, 1]).add(se)
    m = rotate([0, 0, 180]).add(m)
    return translate(v=[0, offs*scl,0]).add(m)

def create_laptop(t, scl, part, angle):
    b = union()

    lid_adjust_ht = 0
    base_adjust_ht = 0
    scrn_end_ht = 30
    scrn_hinge_ht = 60

    if part == 0:
        se = screen_end(scl, scrn_end_ht, lcd_end_ht)
        m = translate(v=[0, 0*scl,0]).add(se)
        b.add(m)
        m = mirror_part(se, scl, total_width)
        b.add(m)

        b = screen_adjust(b, scl, angle)

    lid_adjust_ht += scrn_end_ht
    lid_adjust_ht += lcd_end_ht

    tpanel_offset = -190
    kbd_numpad_indent = 79

    if part == 2:
        se = screen_hinge(scl, scrn_hinge_ht)
        m = translate(v=[0, lid_adjust_ht*scl,0]).add(se)
        b.add(m)
        m = mirror_part(se, scl, total_width-lid_adjust_ht)
        b.add(m)

        b = screen_adjust(b, scl, angle)

    lid_adjust_ht += scrn_hinge_ht

    if part == BASE_END:
        se = base_end(scl, base_end_ht, 0)
        m = translate(v=[0, 0*scl,0]).add(se)
        b.add(m)
        se = base_end(scl, base_end_ht, kbd_numpad_indent)
        m = mirror_part(se, scl, total_width)
        b.add(m)

    base_adjust_ht = base_end_ht
    base_adjust_ht += scrn_hinge_ht

    base_back_ht = (total_width - base_centre_ht) / 2 - base_adjust_ht
    base_front_ht = total_width / 2 - base_adjust_ht

    if part == PCB1:
        se = pcb1(scl)
        b.add(se)

    if part == BASE_BACK:
        # NOTE: ... here's the other bit
        se = base_back_bot(scl, base_back_ht+scrn_hinge_ht, scrn_hinge_ht+2,
                                tpanel_offset)
        m = translate(v=[0, (base_adjust_ht-scrn_hinge_ht)*scl,0]).add(se)
        b.add(m)
        se = base_back_bot(scl, base_back_ht+scrn_hinge_ht, scrn_hinge_ht+2,
                                -tpanel_offset)
        m = mirror_part(se, scl, total_width-base_adjust_ht+scrn_hinge_ht)
        b.add(m)

    if part == 9:
        se = back_kbd_corner(scl, 275)
        m = translate(v=[0, (base_adjust_ht-scrn_hinge_ht)*scl,0]).add(se)
        b.add(m)

    adj = scrn_end_ht
    if part == 10:
        se = screen_front_edge(scl, (total_width-centre_ht)/2-adj)
        m = translate(v=[0, (adj)*scl,0]).add(se)
        b.add(m)
        m = mirror_part(se, scl, total_width-adj)
        b.add(m)
        b = screen_adjust(b, scl, angle)

    adj = scrn_end_ht+lcd_end_ht+scrn_hinge_ht
    if part == 6:
        se = screen_back_edge(scl, (total_width-centre_ht)/2-adj)
        m = translate(v=[0, (adj)*scl,0]).add(se)
        b.add(m)
        m = mirror_part(se, scl, total_width-adj)
        b.add(m)
        b = screen_adjust(b, scl, angle)

    compartment_ht = base_adjust_ht-scrn_hinge_ht

    if part == BASE_FRONT_TOP:
        se = base_front_top(scl, base_front_ht+scrn_hinge_ht, tpanel_offset)
        m = translate(v=[0, (compartment_ht*scl),0]).add(se)
        b.add(m)
        se = base_front_top(scl, base_front_ht+scrn_hinge_ht, -tpanel_offset)
        m = mirror_part(se, scl, total_width-compartment_ht)
        b.add(m)

    if part == FRONT_KBD_TRAY:
        se = front_kbd_tray(scl, base_front_ht+scrn_hinge_ht+tpanel_offset,
                                 0, 0)
        m = translate(v=[0, (base_adjust_ht-scrn_hinge_ht-hthick)*scl,
                         0]).add(se)
        b.add(m)
        se = front_kbd_tray(scl, base_front_ht+scrn_hinge_ht-tpanel_offset,
                                    -kbd_numpad_indent, -tpanel_offset)
        m = mirror_part(se, scl,
                            total_width-base_adjust_ht+scrn_hinge_ht+hthick)
        b.add(m)

    base_adjust_ht += base_back_ht

    if part == BASE_MID:
        se = base_mid(scl, base_centre_ht)
        m = translate(v=[0, (base_adjust_ht)*scl,0]).add(se)
        b.add(m)

    if part == 11:
        se = screen_mid(scl, centre_ht)
        m = translate(v=[0, (total_width/2-centre_ht/2)*scl,0]).add(se)
        b.add(m)
        b = screen_adjust(b, scl, angle)

    base_joiner_ht = 150

    tpanel_ht = (base_adjust_ht + tpanel_offset + base_centre_ht/2 -
                            (tpanel_b_w)/2)
    if part == TPANEL_MID:
        se = tpanel_mid(scl, tpanel_b_w, tpanel_offset)
        m = translate(v=[0, tpanel_ht*scl, 0]).add(se)
        b.add(m)

    pcb1_support_ht = 30

    if part == COMPARTMENT_LID:
        se = compartment_lid(scl, tpanel_ht-compartment_ht, tpanel_offset,
                             kbd_numpad_indent)
        m = translate(v=[0, (compartment_ht*scl),0]).add(se)
        b.add(m)

    if part == BATTERY_SUPPORT1:
        se = battery_support1(scl, pcb1_support_ht, tpanel_offset)
        m = translate(v=[0,
                         (tpanel_ht+tpanel_b_w-80)*scl,
                         0]).add(se)
        b.add(m)

    if part == PCB1_SUPPORT:
        se = pcb1_support(scl, pcb1_support_ht, tpanel_offset)
        m = translate(v=[0,
                         (tpanel_ht)*scl,
                         0]).add(se)
        b.add(m)

    t.add(b)

def usb_wifi(scl):
    u = union()
    b = cube([250*scl, 670*scl, (70.0)*scl])
    b  = translate(v=[0, 200*scl, (0)*scl]).add(b)
    u.add(b)
    b = cube([125*scl, 200*scl, (45.0)*scl])
    b  = translate(v=[(125/2.)*scl, 0, (12.5)*scl]).add(b)
    u.add(b)

    return u

def kbd_part(scl):
    
    u = union()

    # make the keyboard look vaguely like the real thing, keys indented
    # (represented as a single block), tray 2mm high then small cut-outs
    # at various points

    b = cube([kbd_w*scl, kbd_l*scl, (20.0)*scl])
    b  = translate(v=[0, 0, ((-20))*scl]).add(b)
    u.add(b)
    b = cube([(kbd_w-20)*scl, (kbd_l-20)*scl, (kbd_d)*scl])
    b  = translate(v=[0, 0, (-kbd_d)*scl]).add(b)
    u.add(b)
    b = cube([(90)*scl, (1140)*scl, (kbd_d)*scl])
    b  = translate(v=[(-70)*scl, (kbd_l-1150)*scl,
                       (-kbd_d)*scl]).add(b)
    u.add(b)
    b = cube([(80)*scl, (1160)*scl, (20.0)*scl])
    b  = translate(v=[(-80)*scl, (kbd_l-1160)*scl,
                       ((-20))*scl]).add(b)
    u.add(b)

    # add series of small tabs at front
    b = cube([(21)*scl, (90)*scl, (20.0)*scl])
    b  = translate(v=[(-20)*scl, (100)*scl, (-20)*scl]).add(b)
    u.add(b)
    b = translate(v=[(0)*scl, (750)*scl, (0)*scl]).add(b)
    u.add(b)
    b = translate(v=[(0)*scl, (900)*scl, (0)*scl]).add(b)
    u.add(b)
    b = translate(v=[(-80)*scl, (690)*scl, (0)*scl]).add(b)
    u.add(b)
    b = translate(v=[(0)*scl, (745)*scl, (0)*scl]).add(b)
    u.add(b)

    # add series of cutouts at back
    b = cube([(20)*scl, (100)*scl, (20.0)*scl])
    b  = translate(v=[(kbd_w-19)*scl, (130)*scl, (-24)*scl]).add(b)
    u -= b
    b = translate(v=[(0)*scl, (900)*scl, (0)*scl]).add(b)
    u -= b
    b = translate(v=[(0)*scl, (1370)*scl, (0)*scl]).add(b)
    u -= b
    b = translate(v=[(0)*scl, (675)*scl, (0)*scl]).add(b)
    u -= b

    v = union()
    u = translate(v=[-kbd_w/2*scl, -kbd_l/2*scl, kbd_d/2*scl]).add(u)
    v.add(u)
    return v

if __name__ == '__main__':

    animate = False
    max_open = 130
    if animate:
        rpt = 3
        angles = [0, max_open*0.25, max_open*0.5, max_open*0.75, max_open]
    else:
        rpt = 1
        angles = [120]

    for i in range(rpt):
        for angle in angles:
            u = union()
            for i in [
                        #BASE_END,
                        #BASE_FRONT_TOP,
                        FRONT_KBD_TRAY,
                        #PCB1,
                        TPANEL_MID,
                        #BASE_MID,
                        #BASE_BACK,
                        #PCB1_SUPPORT,
                        #BATTERY_SUPPORT1,
                        COMPARTMENT_LID,
                    ]:
                t = union()
                create_laptop(t, scl, part=i, angle=angle)
                r = union().add(t)
                if i == 14: # pcb1
                    c = [0.8, 0.3, 0.8, 0.5]
                else:
                    c = [0.3, 0.5, 0.8, 0.5]
                c = color(c)
                c.add(r)
                u.add(c)

            if add_internal_parts:

                # USB WIFI dongle
                wifi = usb_wifi(scl)
                r = translate([(665)*scl, 150*scl,
                                (85)*scl]).add(wifi)
                c = [0.2, 0.8, 0.8, 0.2]
                r = union().add(r)
                c = color(c)
                c.add(r)
                u.add(c)

                # Keyboard
                kbd = kbd_part(scl)
                r = translate([(lcd_w-kbd_w/2+25)*scl, total_width/2*scl,
                                (62)*scl]).add(kbd)
                c = [0.3, 0.8, 0.5, 0.2]
                r = union().add(r)
                c = color(c)
                c.add(r)
                u.add(c)

                # LCD Panel
                b = union()
                p = lcd_panel(scl, offs=3)
                p = translate(v=[155.5*scl, lcd_indent*scl,(lcd_ht)*scl]).add(p)
                b += p

                r = hinge_rotate(scl, b, angle)
                c = [0.8, 0.8, 0.2, 0.2]
                c = color(c)
                c.add(r)
                u.add(c)

                # Battery
                b = union()
                p = cube([1620*scl, 1360*scl, 65*scl])
                p = translate(v=[500.0*scl, (lcd_l-1360-70)*scl,(97)*scl]).add(p)
                b += p
                r = b

                c = [0.8, 0.2, 0.2, 0.2]
                c = color(c)
                c.add(r)
                u.add(c)


            scad_render_to_file(u, "laptop_prog2.scad")
            f = open("laptop_model2.scad", "w")
            f.write("""include<laptop_prog2.scad>;
            """)
            f.close()
            if i != rpt:
                time.sleep(2)
