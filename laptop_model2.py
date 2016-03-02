# Copyright (C) 2014, 2015 Luke Kenneth Casson Leighton <lkcl@lkcl.net>
# License: GPLv3+

""" TODO:
    * sort out gaps between base end, base hinge end, and screen edge
    * parameterise plastic join-point gaps/sizes so it can be varied
    * allow [flat] cable access through to screen connector
"""

import time
import itertools
from pyopenscad import *
from polysurface import spline_double_divide, Offset, SurfaceFromCurves
from copy import deepcopy
from pyscadutil import B0, B45, pin
from pyscadutil import curvebox, shearedcube, hollowbox, touch_arc
from pyscadutil import L, R, T, D, F, B

pin_parts_3d=False
orientate=True
LEFTPART = 1
RIGHTPART = 2
mirroring = LEFTPART #LEFTPART| RIGHTPART #RIGHTPART 

BATTERY = 0x1
KEYBOARD = 0x2
USB_WIFI = 0x4
LCD_PANEL = 0x8
add_internal_parts = 0 # BATTERY 

test = False
single = True
cutdown = False
revision_1_pcb = True

SCREEN_END = 0
SCREEN_HINGE = 2
SCREEN_FRONT_EDGE = 10
SCREEN_BACK_EDGE = 6
TPANEL_MID = 5
BASE_BACK = 4
BASE_END = 3
BASE_FRONT_TOP = 7
BASE_MID = 8
SCREEN_MID = 9
FRONT_KBD_TRAY = 12
PCB1 = 14
PCB1_SUPPORT = 17
BATTERY_SUPPORT1 = 18
COMPARTMENT_LID = 19
PCB2 = 20
BACK_KBD_RUNNER = 21
FRICTION_HINGE1 = 22
FRICTION_HINGE2 = 23
BASE_BACK_HINGE = 26
CABLE_PROTECTOR = 27
BASE_PANEL = 28
BASE_PANEL_BACK_CLIPS = 29
BASE_PANEL_FRONT_CLIPS = 30
PCB3 = 31
PCB3_SUPPORT = 32
COMPARTMENT_LOCKIN = 33
COMPARTMENT_LOCKIN_CAPTURE = 34

if not test:
    lcd_l = 3598.0
    lcd_w = 2100.0
    # dimensions from datasheet.  reality-adjustment is needed..
    lcd_la = lcd_l-98.0
    lcd_wa = lcd_w-129.9
    lcd_la -= 25
    #lcd_wa -= 20
    lcd_d = 50
    lcd_cable_depth = 1000
    kbd_d = 60
    kbd_l = 3390.0
    kbd_w = 1170.0-79.0

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

hinge_indent_ht = 20.0
lcd_ht = 10.0
lcd_doff = 5
scl = 0.1
hthick = 12 # horizontal pieces not as thick
pcbthick = 16
bwid = 17 # 24
lcd_inset_top = 40
lcd_inset_bot = 180
lcd_gap = 3
lid_offset = 16
lcd_hinge_inner_rad=70
lcd_hinge_inside_rad=70
lcd_ext_rot_angle=250
lcd_outer_rad = lcd_hinge_inner_rad+bwid
lcd_end_ht = 72
lcd_end_offs = 20
pcb3_lock_offs = 839+15
kbd_numpad_indent = 79
lcd_panel_offs = -10

# XXX should really be calculated from lcd width, scrn width etc.
base_end_ht = 110

lcdscrewrad = 30 / 2.0 # XXX: 2.5mm diameter thread, why 0.9mm extra????
screwrad = 28 / 2.0 # XXX: 2mm thread diameter, needs 0.7mm extra!!!
topscrewrad = 20 / 2.0 # supposed to be 3mm screw holes but 3d baaad....
boxheight = 124
backboxheight = boxheight+bwid*2-10
boxtopoffs = 2
boxinset = 55
hinge_depth = 70
hole_depth = hinge_depth
boxlength = lcd_w + lcd_inset_top + lcd_inset_bot
lidfront_offs = 10
lcd_front_indent = 108
back_top_width = 170+79
front_top_width = 180

scrn_centre_ht = 90.0 # XXX +10!
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

def pin_t(ht=244, mirror=True, pht=140, dep=30, half=False):
    d = union()
    h = pin(B0, scl, fill=True)
    h = translate([0, (-3)*scl, -35*scl]).add(h)
    d += h
    if mirror:
        h = translate([0, 0, ht*scl]).add(h)
        d += h
    d += translate([70*scl, 0, 0*scl]).add(d)
    if not half:
        d += translate([0, 0, -50*scl]).add(d)
    d = translate([-35*scl, 0, 0*scl]).add(d)
    h = cube([6*scl, dep*scl, pht*scl])
    h = translate([0*scl, -dep*scl, -(pht-10)*scl]).add(h)
    d += h
    if mirror:
        h = translate([0*scl, 0*scl, ht*scl]).add(h)
        d += h
    return d

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

def lcd_panel(scl, offs=0):

    w = lcd_w
    h = lcd_l
    d = lcd_d

    a = union()

    r = union()
    c = cube(size=[(w+offs*2)*scl,(h+offs*2)*scl,(d+offs*2)*scl])
    r.add(c)
    c = cube(size=[(70)*scl,(250)*scl,(10)*scl])
    t = translate(v=[(w-300)*scl, (h-1080)*scl, (lcd_doff+29.5-d-offs+10)*scl])
    t.add(c)
    r.add(t)
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
    t = translate(v=[(-78-offs+wo)*scl, (-40-offs+do)*scl, (32.5-offs)*scl])
    t.add(r)
    a.add(t)

    return a

def chamfered_backbox_screwholes(scl, sht, r1=22, ri=topscrewrad,
                                 nochamfer=False):
    # chamfered screw holes in top of lid
    c = union()
    if not nochamfer:
        r = topscrewrad*1.2*scl
        r_1 = r1*scl
        c.add(cylinder(r=r, r1=r_1,
                        h=12*scl,
                        segments=50, center=True))
    d = cylinder(r=ri*scl,
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
        return translate([(100)*scl, 0*scl, bht*scl])
    elif end == 1:
        return translate([(-10+lcd_w+11)*scl, 0*scl, bht*scl])
    elif end == 2:
        return translate([(lcd_w+lcd_inset_bot-100)*scl, 0*scl,
                            (bht-5)*scl])
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

def box_screwholes(scl, edge_inset, holes=None, h=lcd_l*2+100,
                        rad=screwrad):
    u = union()

    if holes is None:
        holes = range(3 if test else 4)
    for i in holes:
        t = case_bolthole(scl, i)
        r = cylinder(r=rad*scl, h=h*scl, segments=50, center=True)
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

    lth = 15
    ld = lcd_d+lth+5.4+9+8
    rh = ht
    roff = 0

    walls = {T:lth, L:80, R:hthick, F:-1, D:115}
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
        walls[B] = 20
        curverads.update({ R|T: (ld-hthick, 0),R|D: (hthick, 0),})
        rh = ht + 10
        roff = -20
    elif not front:
        walls[B] = -1
        curverads.update({ R|T: (ld-hthick, 0) })
    if back:
        slen = lcd_inset_bot + 40
        offs = boxlength - slen
    elif front:
        slen = 140
        offs = 0
    else:
        slen = boxlength
        offs = 0
    print "screen box ht", rh, slen, ld
    b = hollowbox(scl, slen, rh, ld, walls,
                    curverads=curverads, scalecurve=scalecurve)
    b = translate(v=[offs*scl, 0, -(lcd_d-18)*scl]).add(b)
    u += b

    if hingewall:
        w1 = lcd_w+lcd_inset_top+40
        c = cube([(hthick)*scl, (ht)*scl, (ld)*scl])
        c = translate(v=[(w1)*scl, 0, -30*scl]).add(c)
        u += c

    u = translate(v=[(0)*scl, roff*scl, 0]).add(u)

    if back:
        # take a bit out for the bamboo panel
        d = shearedcube([(70)*scl, (ht+4)*scl, (32)*scl],
                shear=[0*scl, 0*scl, 0],
                innershear=[0*scl, 0*scl, 0])
        d = rotate([0, 0, 180]).add(d)
        c = translate(v=[(lcd_w+50+lcd_panel_offs)*scl, (ht+1)*scl, (-37)*scl]).add(d)
        u -= c

        # remove runner along bottom of base, for lower panel
        # these are along the back wings
        c = shearedcube([14*scl, (ht+2)*scl, (14)*scl],
                    shear=[14*scl, 0*scl, 0],
                    innershear=[0*scl, 0*scl, 0])
        #c = rotate([0, 0, -90]).add(c)
        t = translate(v=[(lcd_w+36+lcd_panel_offs)*scl, (-1)*scl,
                                    (-27)*scl]).add(c)
        u -= t

    if front:
        # ok, remove just a tiny bit from the lcd edge, for two reasons:
        # (1) so that 3d printing works (too much overhang)
        # (2) so that the centre (wooden) laminate has something to hook onto
        d = shearedcube([(54)*scl, (ht+4)*scl, (32.6)*scl],
                shear=[0*scl, 0*scl, 0],
                innershear=[0*scl, 0*scl, 0])
        c = translate(v=[(98+lcd_panel_offs)*scl, (-1)*scl, (-38)*scl]).add(d)
        u -= c

        # remove runner along top screen edge
        c = shearedcube([14*scl, (lcd_w)*scl, (14)*scl],
                    shear=[14*scl, 0*scl, 0],
                    innershear=[0*scl, 0*scl, 0])
        c = rotate([0, 0, 180]).add(c)
        t = translate(v=[(98+14+lcd_panel_offs)*scl, (ht+1)*scl,
                                    (-27)*scl]).add(c)
        u -= t

    return u


def base_end(scl, ht, kbd_numpad_indent):
    """ TODO:
        * add back_kbd_runner nibs that stop it moving about, left and right
        * RIGHTPART: sort out PCB3 supports, power and switch holes
    """
    u = union()
    w = boxlength-3
    kbd_ht = ht+20

    print "BASE_END height", ht, kbd_ht

    topcurve = 30
    walls = {T:25, L:hthick, R:hthick, F:-1, D:hthick}
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
    u += b

    if kbd_numpad_indent == 0:
        # add top strut, along entire length of base_end.
        c = union()
        b = cube([lcd_w*scl, (ht)*scl, 33*scl])
        b = translate(v=[(120)*scl, (0)*scl, (0)*scl]).add(b)
        c += b
        d = cube([52*scl, (ht)*scl, 37*scl])
        b = translate(v=[(lcd_w-72)*scl, (-1)*scl, (-1)*scl]).add(d)
        u += c

    if revision_1_pcb:
        usb_pos = 562
    else:
        usb_pos = 512

    if not test:
        if kbd_numpad_indent == 0:
            # add PCB traps that keep it down
            c = shearedcube([(boxheight-49)*scl, (15)*scl, 81*scl],
                        shear=[5*scl, 0, 0],
                        innershear=[0*scl, 0, 0])
            c = rotate([180, -90, -90]).add(c)
            u += translate(v=[(lcd_w-75)*scl, (82)*scl,
                    (boxheight-110)*scl]).add(c)
            u += translate(v=[(lcd_w-400)*scl, (82)*scl,
                    (boxheight-110)*scl]).add(c)
            u += translate(v=[(usb_pos-160)*scl, (82)*scl,
                    (boxheight-110)*scl]).add(c)

    if not test:
        if kbd_numpad_indent == 0:
            # remove holes for connectors

            # Headphones
            c = cylinder(r=33*scl, h=(40)*scl, center=True, segments=50)
            c = rotate([0, 90, 90]).add(c)
            c = translate(v=[(lcd_w-340)*scl, (-1)*scl, (75)*scl]).add(c)
            u -= c
            # MicroSD
            c = cube([169*scl, 60*scl, 36*scl])
            c = translate(v=[(lcd_w-272)*scl, (-1)*scl, (66)*scl]).add(c)
            u -= c
            # EOMA68
            c = cube([550*scl, 68*scl, 69*scl])
            c = translate(v=[(1085)*scl, (-1)*scl, (33)*scl]).add(c)
            u -= c
            # EOMA68 eject
            c = cube([77*scl, 60*scl, 61*scl])
            c = translate(v=[(973)*scl, (-1)*scl, (41)*scl]).add(c)
            u -= c
            # USB2
            c = cube([160*scl, 180*scl, 86*scl])
            c = translate(v=[(usb_pos)*scl, (-1)*scl, (16)*scl]).add(c)
            u -= c

            # add bottom strut, along EOMA68 and USB
            b = cube([765*scl, (ht+2)*scl, 15*scl])
            b = translate(v=[(925)*scl, (0)*scl,
                    (boxheight-hthick-10)*scl]).add(b)
            u += b

            # and along USB
            b = cube([219*scl, (50)*scl, 20*scl])
            b = translate(v=[(usb_pos-30)*scl, (0)*scl,
                    (boxheight-hthick-18+5)*scl]).add(b)
            u += b

        else:
            # Power Jack
            c = cube([60*scl, 60*scl, 60*scl])
            c = translate(v=[(280)*scl, (-1)*scl, (16)*scl]).add(c)
            u -= c

            # Reset switch
            c = cylinder(r=30*scl, h=(40)*scl, center=True, segments=50)
            c = rotate([0, 90, 90]).add(c)
            c = translate(v=[(430)*scl, (-1)*scl, (66)*scl]).add(c)
            u -= c

    # add keyboard left support
    w1 = -2 
    if kbd_numpad_indent != 0:
        w1 = kbd_numpad_indent - 5
    b = hollowbox(scl, lcd_w-tpanel_l_b-
                        (back_top_width-140-79)-2+w1, kbd_ht, 33,
                {T:33, L:-1, R:-1, F:20+hthick, D:-1, B:-1},
                curverads={ T|F: (hthick, 0)})
    b = translate(v=[(lcd_w-kbd_w+23-w1-79)*scl, (0)*scl,
                    (0)*scl]).add(b)
    u += b

    # back keyboard support
    b = hollowbox(scl, 12, ht+20, 33,
                {T:-1, L:12, R:-1, F:-1, D:-1, B:-1},
                curverads={ T|L: (hthick, 0)})
    b = translate(v=[(boxlength-back_top_width-15)*scl,
                     0*scl, (0)*scl]).add(b)
    u += b

    rad=35.0 + 15
    # add hinge
    c = cylinder(r=rad*scl, h=(ht)*scl, segments=50)
    c = rotate([0, 90, 90]).add(c)
    c = translate(v=[0*scl,0*scl,-55*scl]).add(c)
    t = hinge_translate(scl).add(c)
    u += t

    # block up hole
    c = cube([(ht)*scl, (50)*scl, (85)*scl])
    c = rotate([0, 0, 90]).add(c)
    c = rotate([0, -90, 0]).add(c)
    c = translate(v=[-(rad-12)*scl,0*scl,(10-55)*scl]).add(c)
    t = hinge_translate(scl).add(c)
    u += t

    c = base_end_bit(scl, ht, fwd=True)
    c = translate(v=[(20)*scl,(0)*scl,(1+hthick)*scl]).add(c)
    u += c

    # add bits for screws through to base front
    c = touch_arc(0, (ht+1), (boxheight-44-hthick),
                        25, scl,
                  angle=0)
    c = rotate([90, 0, 0]).add(c)
    c = rotate([0, 180, 0]).add(c)
    c = resize([(150-hthick-4)*scl, 0, 0], False).add(c)
    c = translate(v=[(lcd_w+66)*scl, (hthick)*scl, (boxheight-80)*scl]).add(c)
    u -= c

    # add base_back lock-ins
    d = union()
    c = shearedcube([(21)*scl, (34)*scl, 61*scl],
                shear=[50*scl, 0, 0],
                innershear=[0*scl, 0, 0])
    c = rotate([90, 0, 0]).add(c)
    d += c
    c = cube([(60)*scl, (40)*scl, 40*scl])
    c = translate(v=[(-1)*scl,(-30)*scl,
                        (-1)*scl]).add(c)
    d -= c
    d = translate(v=[(w-back_top_width+20)*scl,(ht+57)*scl,
                        (hthick+2)*scl]).add(d)
    u += d

    d = union()
    c = shearedcube([(108)*scl, (25)*scl, 91*scl],
                shear=[70*scl, 0, 0],
                innershear=[0*scl, 0, 0])
    c = rotate([90, 0, 0]).add(c)
    c = translate(v=[(w-back_top_width+20)*scl,(ht+10)*scl,
                        (hthick+11)*scl]).add(c)
    d += c
    c = cube([(50)*scl, (150)*scl, 50*scl])
    c = translate(v=[(w-back_top_width+145)*scl,(0)*scl,
                        (hthick+2)*scl]).add(c)
    d -= c
    u += d

    # hollow hinge out
    c = cylinder(r=(rad-12)*scl, h=(ht)*scl, segments=50)
    c = rotate([0, 90, 90]).add(c)
    c = translate(v=[0*scl,hthick*scl,-55*scl]).add(c)
    t = hinge_translate(scl).add(c)
    u -= t

    # add bits for screws through to base back
    v = union()
    c = cube([(60)*scl, (ht)*scl, (40)*scl])
    v += c
    c = cube([(130)*scl, (50)*scl, (95)*scl])
    c = translate(v=[-57*scl, (0)*scl, (5)*scl]).add(c)
    v += c
    c = cube([(130)*scl, (50)*scl, (95)*scl])
    c = rotate([0, 0, -35]).add(c)
    c = translate(v=[10*scl, (70)*scl, (45)*scl]).add(c)
    v -= c
    c = translate(v=[(boxlength-170-5)*scl,
                      (0)*scl, (1+hthick)*scl]).add(v)
    u += c

    # front keyboard tray indentation support, surrounds microsd
    c = cube([(29)*scl, (40)*scl, (boxheight-2)*scl])
    if kbd_numpad_indent == 0:
        t = translate(v=[(tpanel_l_b-27)*scl, 0, (1)*scl]).add(c)
        u += t
        t = translate(v=[(310)*scl, 0, (1)*scl]).add(c)
        u += t
        # between usb ports
        t = translate(v=[(usb_pos+160)*scl, 0, (1)*scl]).add(c)
        u += t
        # at end of PCB
        t = translate(v=[(boxlength-back_top_width-31)*scl, 0,
                (1)*scl]).add(c)
        u += t

        # end pcb marker, also supports bamboo panels top and bottom
        t = translate(v=[(usb_pos-30)*scl, 0, (1)*scl]).add(c)
        u += t

        # support either side of EOMA68 cpu card
        d = cube([(35)*scl, (60)*scl, (boxheight-2)*scl])
        t = translate(v=[(tpanel_l_b+98)*scl, 0, (1)*scl]).add(d)
        u += t
        t = translate(v=[(tpanel_l_b+683)*scl, 0, (1)*scl]).add(d)
        u += t
    else:
        # next to PCB3
        t = translate(v=[(650)*scl, 0, (1)*scl]).add(c)
        u += t
        # roughly along the keyboard edge
        t = translate(v=[(tpanel_l_b-95)*scl, 0, (1)*scl]).add(c)
        u += t
        t = translate(v=[(tpanel_l_b+300)*scl, 0, (1)*scl]).add(c)
        u += t
        t = translate(v=[(tpanel_l_b+700)*scl, 0, (1)*scl]).add(c)
        u += t
        # at end of PCB
        t = translate(v=[(boxlength-back_top_width-50)*scl, 0,
                (1)*scl]).add(c)
        u += t

    if kbd_numpad_indent == 0:
        c = cube([(30)*scl, (ht+20)*scl, (54)*scl])
        t = translate(v=[(usb_pos-31)*scl, 0, (17)*scl]).add(c)
        u += t
        t = translate(v=[(tpanel_l_b-79)*scl, 0, (17)*scl]).add(c)
        u += t
        c = cube([(18)*scl, (ht+20)*scl, (50)*scl])
        t = translate(v=[(tpanel_l_b-56+59)*scl, 0, (21)*scl]).add(c)
        u += t
    else:
        c = cube([(105)*scl, (ht+10)*scl, (18)*scl])
        t = translate(v=[(tpanel_l_b-79-kbd_numpad_indent)*scl, 0,
                            (44)*scl]).add(c)
        u += t
        c = cube([(20)*scl, (ht+10)*scl, (44)*scl])
        t = translate(v=[(tpanel_l_b-79-kbd_numpad_indent)*scl, 0,
                            (12)*scl]).add(c)
        u += t
        t = translate(v=[(tpanel_l_b+1-kbd_numpad_indent+5)*scl, 0,
                            (12)*scl]).add(c)
        u += t

    # add bits for case bolthole at front
    c = cube([(90)*scl, (ht)*scl, (70)*scl])
    c = translate(v=[(60)*scl,
                      (0)*scl, (hthick-3)*scl]).add(c)
    u += c

    # annoying bug in hollowbox, bridge across curve and straight
    c = cube([(1)*scl, (ht)*scl, (hthick)*scl])
    c = translate(v=[(149.5)*scl,
                      (0)*scl, (boxheight-hthick)*scl]).add(c)
    u += c

    # screw holes in box
    t = box_screwholes(scl, hthick, holes=[0, 2], rad=35./2)
    t = translate(v=[0, 0, (boxheight-55)*scl]).add(t)
    u -= t

    s = chamfered_backbox_screwholes(scl, 20, 28)
    s = rotate([90, 0, 0]).add(s)
    s = translate(v=[0, 10*scl, (boxheight-55)*scl]).add(s)
    for hole in [0,2]:
        t = case_bolthole(scl, hole).add(s)
        u -= t

    # add screw hole for front
    c = cube([53*scl, ht*scl, boxheight*scl])
    t = translate(v=[(149)*scl, 0, (0)*scl]).add(c)
    u += t
    v = front_tray_corner(scl, 195)
    v = translate([0, scl*(ht-hthick-5), (-4-55)*scl]).add(v)
    u += v
    # remove extra weight from front tray
    c = shearedcube([(boxheight-66)*scl, (ht+60)*scl, (25)*scl],
            shear=[8*scl, 0*scl, 0],
            innershear=[-8*scl, 0*scl, 0])
    c = rotate([0, 90, 0]).add(c)
    v = translate([(front_top_width-19)*scl, scl*(hthick), (91)*scl]).add(c)
    u -= v
    c = cube([70*scl, (ht+60)*scl, (boxheight-50)*scl])
    v = translate([(front_top_width+5.9)*scl, scl*(hthick), (25)*scl]).add(c)
    u -= v

    # remove runner for panel
    c = shearedcube([20*scl, (boxlength-180-150-5)*scl, (13)*scl],
                shear=[0*scl, 0*scl, 0],
                innershear=[11*scl, 0*scl, 0])
    c = rotate([0, 0, 90]).add(c)
    c = translate(v=[(boxlength-180+8+8)*scl, (ht-9)*scl,
                                (boxheight-hthick-4)*scl]).add(c)
    u -= c

    # add interlock down behind base_back_bot
    b = union()
    c = cube([40*scl, (ht-10)*scl, (hthick+6)*scl])
    b += c
    c = cube([40*scl, (21)*scl, (hthick)*scl])
    c = translate(v=[0*scl, (ht-11)*scl, 0*scl]).add(c)
    b += c
    t = translate(v=[(boxlength-back_top_width-42)*scl, (0)*scl,
                    (boxheight-hthick*2-4)*scl]).add(b)
    u += t
    t = translate(v=[(220)*scl, (0)*scl,
                    (boxheight-hthick*2-4)*scl]).add(b)
    u += t

    if kbd_numpad_indent != 0:
        b = union()
        c = cube([48*scl, (ht+10)*scl, (hthick+2)*scl])
        b += c
        c = cube([48*scl, (ht-10)*scl, (hthick+7)*scl])
        b += c
        for l in [(boxlength-back_top_width-200),
                 (boxlength*0.45), (boxlength*0.64), 530, 794]:
            t = translate(v=[l*scl, (0)*scl,
                            (boxheight-hthick*2-6)*scl]).add(b)
            u += t

    # inset for base_front
    c = cube([(118)*scl, (40)*scl, (63)*scl])
    c = translate(v=[14*scl,(ht-25)*scl,(4)*scl]).add(c)
    c = translate(v=[(20)*scl,(0)*scl,(1+hthick)*scl]).add(c)
    u -= c

    if kbd_numpad_indent != 0:
        doffs = 75
        wd = 100
    else:
        doffs = boxheight-12
        wd = 100
    # top screwhole into front kbd tray
    s = cube([wd*scl, (ht-8)*scl, boxheight*scl])
    s = translate(v=[(tpanel_l_b-29-kbd_numpad_indent-50)*scl,
                    (0)*scl, (0)*scl]).add(s)
    u += s
    s = chamfered_backbox_screwholes(scl, 60, 25)
    #s = rotate([180, 0, 0]).add(s)
    s = translate(v=[(tpanel_l_b-29-kbd_numpad_indent)*scl,
                    (ht-40)*scl, (doffs)*scl]).add(s)
    u -= s

    if kbd_numpad_indent != 0:
        c = cube([(65)*scl, (ht+20)*scl, (34)*scl])
        t = translate(v=[(tpanel_l_b-59-kbd_numpad_indent)*scl, 27*scl,
                            (11)*scl]).add(c)
        u -= t
    else:
        c = cube([(60)*scl, (ht+20)*scl, (36)*scl])
        t = translate(v=[(tpanel_l_b-59-kbd_numpad_indent)*scl, 30*scl,
                            (boxheight-pcbthick-47)*scl]).add(c)
        u -= t

    if kbd_numpad_indent != 0:
        # add an underside support
        c = cube([(tpanel_l_b-190-150)*scl, 11*scl, (14)*scl])
        c = translate(v=[(202)*scl, (ht-1)*scl,
                                    (12)*scl]).add(c)
        u += c

        # remove runner for top panel
        c = shearedcube([22*scl, (tpanel_l_b-180-114)*scl, (11)*scl],
                    shear=[0*scl, 0*scl, 0],
                    innershear=[-11*scl, 0*scl, 0])
        c = rotate([0, 0, 90]).add(c)
        c = translate(v=[(tpanel_l_b+8-100)*scl, (ht)*scl,
                                    (4)*scl]).add(c)
        u -= c

    if kbd_numpad_indent == 0:
        # remove runner for compartment lid
        c = shearedcube([20*scl, (tpanel_l_b-280)*scl, (13)*scl],
                    shear=[0*scl, 0*scl, 0],
                    innershear=[-13*scl, 0*scl, 0])
        c = rotate([0, 0, 90]).add(c)
        c = translate(v=[(tpanel_l_b-50)*scl, (ht+1)*scl,
                                    (4)*scl]).add(c)
        u -= c

    clasp = False
    if clasp:
        # add spring-loaded clasp
        c = cube([(150)*scl, (ht)*scl, (boxheight)*scl])
        t = translate(v=[150*scl, 0*scl, (0)*scl]).add(c)
        u += t
        c = cube([(120)*scl, (ht-20+1)*scl, (boxheight-30+1)*scl])
        t = translate(v=[145*scl, -1*scl, (-1+15)*scl]).add(c)
        u -= t
        c = cube([(120)*scl, (28+1)*scl, (30)*scl])
        t = translate(v=[145*scl, -1*scl, (-1)*scl]).add(c)
        u -= t
        c = cube([(160)*scl, (55)*scl, (30)*scl])
        c = translate(v=[130*scl,15*scl, (53)*scl]).add(c)
        u -= c
        # add middle-bit back in
        c = cube([(26)*scl, (40)*scl, (boxheight)*scl])
        t = translate(v=[180*scl, (base_end_ht-47)*scl, (0)*scl]).add(c)
        u += t

    if pin_parts_3d:
        c = union()
        h = pin(B0, scl)
        h = translate([(0)*scl, (0)*scl, 45*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(60)*scl, (0)*scl, 45*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(180)*scl, (0)*scl, 45*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(120)*scl, (0)*scl, 45*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(255)*scl, (0)*scl, 45*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(255)*scl, (0)*scl, 205*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(120)*scl, (0)*scl, 205*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(180)*scl, (0)*scl, 205*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(45)*scl, (0)*scl, 195*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(0)*scl, (0)*scl, 120*scl]).add(h)
        c += h

        h = pin_t(250, dep=20)
        h = rotate([180, 0, 0]).add(h)
        h = translate([(tpanel_l_b-30)*scl, (1.2)*scl, 182*scl]).add(h)
        c += h

        c += translate([(-450)*scl, (0)*scl, 0*scl]).add(h)
        c += translate([(-820)*scl, (0)*scl, 0*scl]).add(h)
        c += translate([(350)*scl, (0)*scl, 0*scl]).add(h)
        c += translate([(700)*scl, (0)*scl, 0*scl]).add(h)
        c += translate([(1000)*scl, (0)*scl, 0*scl]).add(h)
        c += translate([(1280)*scl, (0)*scl, 0*scl]).add(h)

        h = pin(B0, scl)
        h = translate([(w-120)*scl, (0)*scl, 40*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(w-60)*scl, (0)*scl, 40*scl]).add(h)
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

        h = cube([150*scl, 60*scl, 7*scl])
        h = translate([(130)*scl, (1.2)*scl, 55*scl]).add(h)
        c += h

        h = cube([w*scl, 1.2*scl, (boxheight+20)*scl*1.1])
        h = translate([(0)*scl, (1.2)*scl, 40*scl]).add(h)
        c += h

        c = translate([(0)*scl, (-1.2)*scl, 0*scl]).add(c)

        u += c

    if cutdown:
        # cut down
        #c = cube([(tpanel_l_b-20)*scl, (ht+100)*scl, 400*scl])
        #c = translate([(-79-kbd_numpad_indent)*scl, -20*scl, -50*scl]).add(c)
        #u -= c
        #c = cube([(boxlength+300)*scl, (ht+100)*scl, 400*scl])
        #c = translate([(tpanel_l_b+30-kbd_numpad_indent)*scl, -20*scl, -50*scl]).add(c)
        #u -= c

        #c = cube([(boxlength+300)*scl, (ht+100)*scl, 400*scl])
        #c = translate([(-600)*scl, -20*scl, -50*scl]).add(c)
        #u -= c
        c = cube([(boxlength+300)*scl, (ht+100)*scl, 400*scl])
        c = translate([(300)*scl, -20*scl, -50*scl]).add(c)
        u -= c
        #c = cube([(300)*scl, (ht+100)*scl, 400*scl])
        #c = translate([(-175)*scl, -20*scl, -50*scl]).add(c)
        #u -= c

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
    c = cube([(115)*scl, (ht)*scl, (60)*scl])
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
    c = cube([(boxlength - tpanel_l_b - back_top_width+30+18)*scl,
                    ht*scl, (boxheight-hthick-kbd_inset-3)*scl])
    c = translate(v=[(tpanel_l_b-30)*scl, (holder_ht-ht)*scl,
                    (kbd_inset)*scl]).add(c)
    u += c

    # cut-out for back kbd runner
    c = cube([(46)*scl, (150)*scl, (18)*scl])
    c = translate(v=[(boxlength-back_top_width-25)*scl,
                (-40)*scl, (36)*scl]).add(c)
    u -= c

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
                (boxheight-20-hthick-3)*scl]).add(c)
    u += c
    # finally a cut-out for the kbd tray slot
    c = cube([(104)*scl, 70*scl, (20)*scl])
    c = translate(v=[(19+tpanel_l_b-tpanel_box_l)*scl, (11)*scl,
                (21)*scl]).add(c)
    u -= c

    # small cut-out to match tpanel
    c = cube([(22)*scl, 90*scl, (20)*scl])
    c = translate(v=[(tpanel_l_b-tpanel_box_l-1)*scl, (-1)*scl,
                (21)*scl]).add(c)
    u -= c
    c = cube([(32)*scl, 90*scl, (20)*scl])
    c = translate(v=[(tpanel_l_b-tpanel_box_l+121)*scl, (-1)*scl,
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

def pcb3_support(scl, ht):
    u = union()
    w = tpanel_l_b - front_top_width - kbd_numpad_indent - 53

    # main strut
    u += cube([(w)*scl, ht*scl, (25)*scl])

    # top pcb3 slot support, also strengthens strut
    c = cube([(w-35)*scl, 21*scl, (8)*scl])
    u += translate([12*scl, (ht-1)*scl, 0]).add(c)

    # stabiliser in front base slot
    u += cube([(30)*scl, ht*scl, (39)*scl])

    # underside of slot for pcb3
    v = union()
    c = cube([(30)*scl, 21*scl, (10)*scl])
    v += translate([0*scl, (ht-1)*scl, 29*scl]).add(c)
    c = cube([(30)*scl, ht*scl, (15)*scl])
    v += translate([0*scl, 0*scl, 24*scl]).add(c)

    u += translate([25*scl, 0, 0]).add(v)
    u += translate([340*scl, 0, 0]).add(v)

    # end-stop for pcb, extends down to base panel
    c = cube([(20)*scl, (ht+20)*scl, (boxheight-30)*scl])
    u += translate([365*scl, 0*scl, 0]).add(c)
    
    # other end-stop for pcb
    c = cube([(20)*scl, 21*scl, (39)*scl])
    u += translate([12*scl, (ht-1)*scl, 0]).add(c)
    
    u = translate(v=[(front_top_width-10)*scl, (-36)*scl,
                    (55+15)*scl]).add(u)

    if pin_parts_3d:

        v = union()
        d = pin_t(0, mirror=False, dep=50, half=True, pht=80)
        d = rotate([180, 0, 0]).add(d)
        v += translate([(219)*scl, (boxheight-160)*scl, 115*scl]).add(d)
        d = pin_t(0, mirror=False, dep=50)
        d = rotate([180, 0, 0]).add(d)
        v += translate([(549)*scl, (boxheight-160)*scl, 80*scl]).add(d)
        d = rotate([0, 90, 0]).add(d)
        v += translate([(95)*scl, (boxheight-160)*scl, 109*scl]).add(d)
        d = pin_t(0, mirror=False)
        d = rotate([180, 0, 0]).add(d)
        v += translate([(170)*scl, (boxheight-160)*scl, 30*scl]).add(d)
        v += translate([(w+164)*scl, (boxheight-160)*scl, 30*scl]).add(d)
        d = rotate([0, 90, 0]).add(d)
        v += translate([(w+104)*scl, (boxheight-160)*scl, 94*scl]).add(d)

        u += v

    return u

def pcb1_support(scl, ht, tpanel_offset, pcb1_support_offset):
    u = union()
    kbd_inset = 38.0
    sdep = (boxheight-hthick-pcbthick-kbd_inset-3)
    holder_ht = pcb1_support_offset - ht
    w = (boxlength - tpanel_l_b - back_top_width)
    tpanel_box_l = 150
    # main strut going from back base to tpanel
    c = cube([(w+30+18)*scl,
                    ht*scl, (boxheight-hthick-kbd_inset-3)*scl])
    c = translate(v=[(tpanel_l_b-30)*scl, (holder_ht-ht)*scl,
                    (kbd_inset)*scl]).add(c)
    u += c
    # secondary strut with pcb edge lock
    c = cube([(w+tpanel_box_l-23)*scl,
                    (holder_ht)*scl, (sdep-40)*scl])
    c = translate(v=[(tpanel_l_b-tpanel_box_l)*scl, (0)*scl,
                    (kbd_inset+40)*scl]).add(c)
    u += c

    # cut-out for LVDS cable
    c = cube([(400)*scl, (holder_ht-ht+1)*scl, (150)*scl])
    c = translate(v=[(tpanel_l_b-tpanel_box_l+180+300)*scl, (-1)*scl,
                    (kbd_inset)*scl]).add(c)
    u -= c

    c = shearedcube([(200)*scl, (30)*scl, (50)*scl],
                shear=[0*scl, 0*scl, 0],
                innershear=[0*scl, 23*scl, 0])
    c = rotate([-90, 0, 0]).add(c)
    c = translate(v=[(tpanel_l_b-tpanel_box_l+180+400)*scl, (-1+50)*scl,
                    (kbd_inset+80)*scl]).add(c)
    u -= c

    d = union()
    c = cube([(480)*scl, (holder_ht-ht+1)*scl, (20)*scl])
    d += c
    c = cube([(40)*scl, (holder_ht-ht+1)*scl, (50)*scl])
    d += c
    d += translate([440*scl, 0, 0]).add(c)
    u += translate(v=[(tpanel_l_b-tpanel_box_l+180+300-40)*scl, (-1+30)*scl,
                    (kbd_inset)*scl]).add(d)

    # cut-out for power / signal cables and for re-routing LVDS cable back
    c = cube([(250)*scl, (holder_ht-ht+1)*scl, (24)*scl])
    c = translate(v=[(tpanel_l_b-tpanel_box_l+180+740)*scl, (30)*scl,
                    (kbd_inset-1)*scl]).add(c)
    u -= c

    # cut-out for back kbd runner
    c = cube([(46)*scl, (150)*scl, (18)*scl])
    c = translate(v=[(boxlength-back_top_width-25)*scl,
                (-40)*scl, (36)*scl]).add(c)
    u -= c

    # cut-out for PCB1 
    c = cube([(w+18-70)*scl, (holder_ht-ht+1)*scl, (150)*scl])
    c = translate(v=[(tpanel_l_b-tpanel_box_l+170)*scl, (10)*scl,
                    (boxheight-kbd_inset+7)*scl]).add(c)
    u -= c

    # screw holder, done in 3 parts so that it's easier to calculate heights
    # first part is flush with main strut
    bhht = holder_ht+110.0
    c = cube([(tpanel_box_l+20)*scl, bhht*scl, sdep*scl])
    c = translate(v=[(tpanel_l_b-tpanel_box_l)*scl, (-110)*scl,
                (kbd_inset)*scl]).add(c)
    u += c
    # second part goes up to underside of tpanel
    c = cube([(tpanel_box_l+20)*scl, bhht*scl, 10*scl])
    c = translate(v=[(tpanel_l_b-tpanel_box_l)*scl, (-110)*scl,
                (tpanel_h+1)*scl]).add(c)
    u += c
    # third part goes down to bamboo panel
    c = cube([(tpanel_box_l+20)*scl, bhht*scl, 20*scl])
    c = translate(v=[(tpanel_l_b-tpanel_box_l)*scl, (-110)*scl,
                (boxheight-20-hthick-3)*scl]).add(c)
    u += c

    # cut-out for PCB1
    c = cube([(50)*scl, (31)*scl, (150)*scl])
    c = translate(v=[(tpanel_l_b-tpanel_box_l+145)*scl, (-110-1)*scl,
                    (0)*scl]).add(c)
    u -= c

    # screw holes in top for touchpanel
    d = cylinder(r=topscrewrad*scl,
                    h=(55)*scl,
                    segments=50, center=True)
    t = translate(v=[(tpanel_l_b-75)*scl, (40-110)*scl, (50)*scl]).add(d)
    u -= t

    # cut-out for front kbd tray
    w = tpanel_b_w
    b = cube([(87)*scl, (bhht+4)*scl, (31)*scl])
    b = translate(v=[(w-202)*scl, (-1-110)*scl, (66)*scl]).add(b)
    u -= b
    b = cube([(54)*scl, (bhht+4)*scl, (40)*scl])
    b = translate(v=[(w-202)*scl, (-1-110)*scl, (47)*scl]).add(b)
    u -= b

    if pin_parts_3d:

        v = union()
        d = pin_t(190)
        v += translate([(tpanel_l_b-30)*scl, 0, 0]).add(d)
        v += translate([(-165)*scl, 0, 0]).add(d)
        d = pin_t(mirror=False, dep=20)
        v += translate([(tpanel_l_b/2-20)*scl, 0, 90*scl]).add(d)
        d = pin_t(tpanel_l_b+410)
        d = rotate([0, 90, 0]).add(d)
        d = translate([-250*scl, 0, 40*scl]).add(d)
        v += d
        #v = rotate([0, 0, 90]).add(v)
        v = translate(v=[(tpanel_b_w)*scl, (90)*scl,
                    (35)*scl]).add(v)
        c += v

        u += c

    v = union()
    u = translate(v=[0*scl, 0, (55)*scl]).add(u)
    v.add(u)

    return v

def tpanel_mid(scl, ht, ht_offset, pcb1_support_offset, base_screwholes=False):
    """
    TODO:
    * put screwhole down into base_mid
    * remove some stuff on the back underside (near kbd)
    """
    u = union()

    walls = {T:40, L:hthick, R:35, F:20, D:-1, B:20}
    curverads={
                L|T: (hthick, 0),
                R|T: (hthick, 0),
                }
    # hthick is thickness of bamboo laminate
    b = hollowbox(scl, tpanel_l_b, ht, boxheight-hthick, walls,
            curverads=curverads)
    u += b

    # front cut-out matching base_front_top
    c = cube([181*scl, (ht+2)*scl, (150)*scl])
    c = translate(v=[(-1)*scl, (-1)*scl, (40)*scl]).add(c)
    u -= c

    # back cutout to save plastic
    c = cube([130*scl, (ht-200)*scl, (150)*scl])
    c = translate(v=[(tpanel_l_b-160)*scl, (100)*scl, (15)*scl]).add(c)
    u -= c

    # add bit back in for screwhole
    c = cube([163*scl, (80)*scl, (40)*scl])
    c = translate(v=[(tpanel_l_b-180)*scl, (ht/2-ht_offset-40)*scl, (0)*scl]).add(c)
    u += c

    # remove cutout for base_mid
    c = cube([470*scl, (347)*scl, (150)*scl])
    c = translate(v=[(tpanel_l_b-80)*scl, (ht-440)*scl, (40)*scl]).add(c)
    u -= c

    # remove cutout for pcb2 
    c = cube([470*scl, (421)*scl, (150)*scl])
    c = translate(v=[(tpanel_l_b-280)*scl, (ht-834)*scl, (30)*scl]).add(c)
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

    # keyboard tray indent
    b = kbd_tray_indent(scl)
    t = translate(v=[(tpanel_l_b-19)*scl, (ht-282)*scl, (16)*scl]).add(b)
    u -= t

    offs = tpanel_l_b/2
    # half-way point support for top front bamboo panel
    c = union()
    c += cube([(110)*scl, (82)*scl, (50)*scl])
    d = cube([(110)*scl, (57)*scl, (boxheight-38)*scl])
    c += translate(v=[0, (25)*scl, 0*scl]).add(d)
    b = translate(v=[(offs-5)*scl, (-25)*scl, 0*scl]).add(c)
    u += b
    c = cube([(100)*scl, (58)*scl, (boxheight-hthick*2)*scl])
    b = translate(v=[offs*scl, (ht-50)*scl, (hthick)*scl]).add(c)
    u += b

    # inner cut-out for actual touchpanel
    # XXX TODO: add curved edges (use a hollowbox as the cutout)
    crad = 30
    inset = 7.0
    c = curvebox(scl, tpanel_l+inset, tpanel_w+inset, 13, crad)
    c = translate(v=[(100-inset/2)*scl,
                      ((ht-tpanel_w-inset)/2)*scl, (-1)*scl]).add(c)
    u -= c
    c = curvebox(scl, tpanel_l-16, tpanel_w-16, 42, 22)
    c = translate(v=[(100+8)*scl, ((ht-tpanel_w)/2+8)*scl, (9)*scl]).add(c)
    u -= c

    # wings for screw-holes to fit with front base
    d = shearedcube([(64)*scl, (40)*scl, (86)*scl],
            shear=[0*scl, 0*scl, 0],
            innershear=[-32*scl, 0*scl, 0])
    d = rotate([0, -90, 0]).add(d)
    d = rotate([0, 0, -90]).add(d)
    c = translate(v=[(181)*scl, (-85)*scl, (44)*scl]).add(d)
    u += c
    d = rotate([0, 0, 180]).add(d)
    c = translate(v=[(181+40)*scl, (ht+85)*scl, (44)*scl]).add(d)
    u += c

    # cut-out to match pcb1_support
    w = tpanel_b_w
    l = 0
    c = cube([(163)*scl, (95+pcb1_support_offset)*scl, (50)*scl])
    b = translate(v=[(w-263)*scl, (0)*scl, (tpanel_h-33)*scl]).add(c)
    u += b
    c = cube([(160)*scl, (90)*scl, (20)*scl])
    b = translate(v=[(w-260)*scl, (ht-90)*scl, (tpanel_h-3)*scl]).add(c)
    u += b
    c = cube([(160)*scl, (85+pcb1_support_offset)*scl, (95)*scl])
    b = translate(v=[(w-253)*scl, (-1)*scl, (tpanel_h-3)*scl]).add(c)
    u -= b
    c = cube([(160)*scl, (85)*scl, (93)*scl])
    b = translate(v=[(w-250)*scl, (ht-85+1)*scl, (tpanel_h-3)*scl]).add(c)
    u -= b

    # cut-out to match right kbd tray
    c = cube([(104)*scl, (82)*scl, (93)*scl])
    b = translate(v=[(w-229)*scl, (ht-82+1)*scl, (20)*scl]).add(c)
    u -= b

    # matches screw-hole in front base
    u = indented_screwhole(scl, u, (182), -40, 75, -90, base_screwholes)
    u = indented_screwhole(scl, u, (182), ht+40, 75, -90, base_screwholes)

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
    # and into #base_mid
    b = translate(v=[(tpanel_l_b-75)*scl, (ht/2-ht_offset)*scl,
                     (+20)*scl]).add(s)
    u -= b

    # cutout for circular lock
    c = union()
    d = cylinder(r=48*scl, h=(100)*scl, segments=50, center=True)
    c += translate(v=[0*scl, 0*scl, -2*scl]).add(d)
    d = cylinder(r=35*scl, h=(140)*scl, segments=50, center=True)
    c += translate(v=[0*scl, 0*scl, -40*scl]).add(d)
    b = translate(v=[(offs+50)*scl, (-5)*scl, 62*scl]).add(c)
    u -= b

    # remove runner along bottom of base, for lower panel
    # these are along the back wings
    c = shearedcube([12*scl, (tpanel_l_b-230)*scl, (12)*scl],
                shear=[12*scl, 0*scl, 0],
                innershear=[0*scl, 0*scl, 0])
    c = rotate([0, 0, -90]).add(c)
    t = translate(v=[(90)*scl, (ht+12)*scl,
                                (3)*scl]).add(c)
    u -= t

    if pin_parts_3d:

        c = curvebox(scl, tpanel_l-13, tpanel_w-13, 12, 21)
        c = translate(v=[(100+6.5)*scl, ((ht-tpanel_w)/2+6.5)*scl,
                        (0)*scl]).add(c)
        u += c
        c = curvebox(scl, tpanel_l-26, tpanel_w-26, 14, 14)
        c = translate(v=[(100+13)*scl, ((ht-tpanel_w)/2+13)*scl,
                        (-1)*scl]).add(c)
        u -= c

        c = union()
        h = pin(B0, scl)
        h = translate([(157)*scl, (0)*scl, -108*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(tpanel_l_b-240)*scl, (0)*scl, -108*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(tpanel_l_b-234)*scl, (0)*scl, (-ht)/2*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(tpanel_l_b-240)*scl, (0)*scl, (-ht+108)*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(157)*scl, (0)*scl, (-ht+108)*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(152)*scl, (0)*scl, (-ht)/2*scl]).add(h)
        c += h

        h = pin(B0, scl)
        h = translate([(0)*scl, (0)*scl, 30*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(0)*scl, (0)*scl, (-ht-30)*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(tpanel_l_b)*scl, (0)*scl, -ht*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(tpanel_l_b)*scl, (0)*scl, 0*scl]).add(h)
        c += h

        h = pin(B0, scl)
        h = translate([(197)*scl, (0)*scl, (-ht-40)*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(197)*scl, (0)*scl, (+40)*scl]).add(h)
        c += h

        c = rotate([90, 0, 0]).add(c)
        c = translate([(0)*scl, (0)*scl, -1.2*scl]).add(c)

        h = cube([6*scl, 86*scl, 50*scl])
        h = translate([(197)*scl, (ht-1)*scl, 0*scl]).add(h)
        c += h
        h = cube([6*scl, 86*scl, 50*scl])
        h = translate([(197)*scl, (-85)*scl, 0*scl]).add(h)
        c += h

        u += c

    if cutdown:
        c = cube([500*scl, (ht+200)*scl, 300*scl])
        u -= translate([-100*scl, -100*scl, -20*scl]).add(c)
        c = cube([900*scl, (ht+200)*scl, 300*scl])
        u -= translate([(offs+120)*scl, -100*scl, -1*scl]).add(c)
        c = cube([1900*scl, (ht+200)*scl, 300*scl])
        u -= translate([(-100)*scl, 200*scl, -20*scl]).add(c)

        if pin_parts_3d:
            c = union()
            h = pin(B0, scl)
            c += translate([(tpanel_l_b/2-40)*scl, (0)*scl, 25*scl]).add(h)
            c += translate([(tpanel_l_b/2-40)*scl, (0)*scl, -40*scl]).add(h)
            c += translate([(tpanel_l_b/2+40)*scl, (0)*scl, 25*scl]).add(h)
            c += translate([(tpanel_l_b/2+40)*scl, (0)*scl, -40*scl]).add(h)
            c += translate([(tpanel_l_b/2+120)*scl, (0)*scl, 25*scl]).add(h)
            c += translate([(tpanel_l_b/2+120)*scl, (0)*scl, -40*scl]).add(h)

            c = rotate([90, 0, 0]).add(c)
            c = translate([(0)*scl, (0)*scl, -1.2*scl]).add(c)
            u += c

    v = union()
    u = translate(v=[0*scl, 0, (55)*scl]).add(u)
    v.add(u)
    return u

def base_panel_front_clip(scl):

    u = union()

    e = union()
    c = cube([100*scl, (50)*scl, (15)*scl])
    e += translate(v=[(00)*scl, (0)*scl, (0)*scl]).add(c)
    c = cube([100*scl, (55)*scl, (15)*scl])
    e -= translate(v=[(-65)*scl, (-1)*scl, (8)*scl]).add(c)

    u += translate(v=[0*scl, 0*scl, (55+boxheight-15-16)*scl]).add(e)

    if pin_parts_3d:
        c = union()
        h = pin(B0, scl)
        c += translate([(0)*scl, (0)*scl, -95*scl]).add(h)
        c += translate([(70)*scl, (0)*scl, -95*scl]).add(h)

        c = rotate([90, 0, 0]).add(c)
        u += translate([(10)*scl, (-70)*scl, (boxheight+16+8.8)*scl]).add(c)

    return u

def base_panel_front_clips(scl, ht, ht_offset):
    print "BASE_PANEL_FRONT_CLIPS ht", ht

    u = union()
    boff = front_top_width - 30

    c = base_panel_front_clip(scl)
    u += translate(v=[boff*scl, 120*scl, 0*scl]).add(c)

    if False: # XXX TEST to see if clips work for base_mid... they do
        c = rotate([0, 0, -90]).add(c)
        u += translate(v=[(boff+120)*scl, (ht-50)*scl, 0*scl]).add(c)

    return u

def base_panel_back_clips(scl, ht, ht_offset):
    print "BASE_PANEL_BACK_CLIPS ht", ht

    u = union()
    boff = boxlength - back_top_width - 50

    e = union()
    c = cube([25*scl, (85)*scl, (30)*scl])
    e += translate(v=[(00)*scl, (0)*scl, (0)*scl]).add(c)

    d = union()
    d += shearedcube([(35)*scl, (62)*scl, (18)*scl],
                    shear=[0, 30*scl, 0],
                    innershear=[0, 0*scl, 0, 0])
    b = cube([(35)*scl, (92)*scl, (8.1)*scl])
    d += translate(v=[(0)*scl, (0)*scl, (17.9)*scl]).add(b)
    d = rotate([0, 0, 180]).add(d)
    e -= translate(v=[(30)*scl, (135+12)*scl, (8)*scl]).add(d)

    u += translate(v=[boff*scl, 15*scl, (55+boxheight-30-15)*scl]).add(e)

    if pin_parts_3d:
        c = union()
        h = pin(B0, scl)
        c += translate([(0)*scl, (0)*scl, -40*scl]).add(h)

        c = rotate([90, 0, 0]).add(c)
        u += translate([(boff+10)*scl, (-10)*scl, (boxheight+8.8)*scl]).add(c)
        u += translate([(boff+10)*scl, (50)*scl, (boxheight+8.8)*scl]).add(c)

    return u

def base_panel(scl, ht, ht_offset):
    print "BASE_PANEL ht", ht

    u = union()
    bl = boxlength - front_top_width - back_top_width
    c = cube([bl*scl, (ht-base_centre_ht/2)*scl, (15)*scl])
    c = translate(v=[front_top_width*scl, 0, (55+boxheight-15)*scl]).add(c)
    u += c

    return u

def base_front_top(scl, ht, ht_offset):
    print "BASE_FRONT_TOP ht", ht

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
    c = shearedcube([110*scl, (54)*scl, (21)*scl],
                shear=[-16*scl, 0*scl, 0],
                innershear=[16*scl, 0*scl, 0])
    c = rotate([0, -90, 0]).add(c)
    c = rotate([90, 0, 0]).add(c)
    c = rotate([0, 0, 90]).add(c)
    c = translate(v=[(37)*scl,(1)*scl,(21)*scl]).add(c)
    u += c

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

    # prepare series of cutouts
    fthick = 6
    offs = 110-hthick+fthick
    if test:
        num_steps = 4.0
    else:
        if ht_offset > 0:
            num_steps = 12.0
        else:
            num_steps = 8.0
    step = (tpanel_ht-tpanel_b_w/2-100-offs) / num_steps
    end = (tpanel_ht-step-tpanel_b_w/2+5)

    doffs = 66
    c = base_cutout(scl, end-offs, doffs=doffs)
    c = resize([(236-doffs)*scl, 0, (boxheight-hthick*2)*scl], False).add(c)
    c = rotate([0, 0, 180]).add(c)
    c = translate(v=[0*scl, (end)*scl, (0)*scl]).add(c)
    u -= c

    # put in series of cutouts
    while offs < end-10:
        # add fill-ins
        b = base_cutout(scl, fthick, arch=True, doffs=doffs)
        b = resize([(234-doffs)*scl, 0,
                    pow(2, 0.5)*(boxheight-hthick*2+6)*scl], False).add(b)
        b = rotate([0, 0, 180]).add(b)
        c = rotate([-43, 0, 0]).add(b)
        c = translate(v=[0*scl, (offs-fthick+step+1)*scl, (-6)*scl]).add(c)
        u += c
        offs += step
        c = rotate([43, 0, 0]).add(b)
        c = translate(v=[0*scl, (offs-fthick+25)*scl,
                (-3)*scl]).add(c)
        u += c

        offs += step

    # add runner support, has to be done before pcb/battery support
    if ht_offset > 0:
        lst = [480, 1070]
    else:
        lst = [490, 690]
    for h in lst:
        c = shearedcube([(front_top_width-80)*scl, (40)*scl, (15)*scl])
        c = translate(v=[(80)*scl, h*scl,
                                    (boxheight-hthick-13)*scl]).add(c)
        u += c
    mholderw = 139+fthick*4
    mholdero = 229

    # add a support for magnet
    d = union()
    c = shearedcube([(mholderw+40)*scl, 178*scl, 110*scl],
            shear=[-95*scl, -20*scl, 0],
            innershear=[95*scl, 0*scl, 0])
    d += rotate([0, 0, 90]).add(c)
    c = shearedcube([(mholderw+40)*scl, 180*scl, 110*scl],
            shear=[-180*scl, -20*scl, 0],
            innershear=[0*scl, -8*scl, 0])
    c = rotate([180, 0, 0]).add(c)
    d -= translate(v=[-264*scl, 180*scl, (130)*scl]).add(c)
    u += translate(v=[180*scl, (mholdero-25)*scl, (6)*scl]).add(d)

    print "magholder width", mholderw-fthick*4
    # add a hole for a magnet.  quite low down
    c = shearedcube([(65)*scl, 167*scl, 57*scl],
            shear=[-2*scl, 15*scl, 0],
            innershear=[2*scl, 8*scl, 0])
    c = rotate([0, 0, 90]).add(c)
    c = translate(v=[201*scl, (mholdero+42)*scl, (6)*scl]).add(c)
    u -= c

    if ht_offset > 0:
        boffs = pcb3_lock_offs-52
        # ok these are for the pcb3 support
        # they extend all the way to the back (for injection molding)
        c = base_cutout(scl, 54, doffs=doffs)
        c = rotate([0, 0, 180]).add(c)
        c = resize([(234-doffs)*scl, 0, (boxheight-hthick*2+2)*scl],
                    False).add(c)
        c = translate(v=[0*scl, (boffs)*scl, (-1)*scl]).add(c)
        u += c

        # ... cutout for the actual support, the rest was housing for the cutout
        c = cube([40*scl, 37*scl, (45)*scl])
        c = translate(v=[-32*scl, (9-54)*scl, (-7)*scl]).add(c)
        c = translate(v=[(180+5)*scl, (boffs)*scl, (19.5)*scl]).add(c)
        u -= c

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
    t = box_screwholes(scl, hthick, holes=[0], h=130, rad=35./2)
    t = translate(v=[0, 0, (boxheight-55)*scl]).add(t)
    u -= t

    # add hexagonal bolt hole support for a nut to sit in
    c = cube([100*scl, 40*scl, 60*scl], center=True)
    c = translate(v=[(50)*scl, (110)*scl, (boxheight-55)*scl]).add(c)
    t = case_bolthole(scl, 0).add(c)
    u -= t
    c = cylinder(r=34.0*scl, h=40*scl, center=True, segments=6)
    c = rotate([0, 90, 90]).add(c)
    c = rotate([0, 30, 0]).add(c)
    t = case_bolthole(scl, 0).add(c)
    t = translate(v=[(0)*scl, (110)*scl, (boxheight-55)*scl]).add(t)
    u -= t

    # fillin/cutout for base_mid
    cht = base_centre_ht/2+85
    c = shearedcube([50*scl, cht*scl, (45)*scl],
            shear=[0*scl, 0*scl, 0],
            innershear=[-10*scl, 0*scl, 0])
    t = translate(v=[(120)*scl, (ht-cht)*scl, (40)*scl]).add(c)
    u += t

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
    t = translate(v=[(135)*scl, (ht-base_centre_ht/2-30)*scl,
                        (80)*scl]).add(t)
    u -= t

    # remove bit for touchpanel
    c = cube([(tpanel_b_w+1-50)*scl, (tpanel_l+3-ht_offset)*scl,
                        (tpanel_h+3)*scl])
    c = translate(v=[(-1)*scl, (tpanel_ht-tpanel_b_w/2-2)*scl,
                        (-1)*scl]).add(c)
    u -= c

    # cut-in for base_end lock
    t = shearedcube([(boxheight-hthick*2-22)*scl, (60)*scl, (34.2)*scl],
            shear=[11*scl, 0*scl, 0],
            innershear=[-11*scl, 0*scl, 0])
    t = rotate([0, 90, 0]).add(t)
    b = translate(v=[(146)*scl, (-1)*scl, (55+hthick+34)*scl]).add(t)
    u -= b
    # screw hole for tpanel_mid
    t = holed_support(scl, 50, inverse=True)
    t = rotate([0, 0, -90]).add(t)
    b = translate(v=[(130)*scl, ((tpanel_ht-tpanel_b_w/2-5))*scl,
                     (44)*scl]).add(t)
    u -= b

    # dovetail cuts to fit base_mid
    # XXX height is magic constant
    doffs = 36
    offs = base_centre_ht / 2.0 + 73 - doffs
    b = shearedcube([(50)*scl, (offs+1)*scl, (33)*scl],
            shear=[0*scl, 0*scl, 0],
            innershear=[10*scl, 0*scl, 0])
    b = rotate([0, -90, 0]).add(b)
    c = translate(v=[(160)*scl, (ht-offs+1-doffs)*scl,
                                    (45)*scl]).add(b)
    u -= c
    b = rotate([180, 0, 0]).add(b)
    b = translate(v=[(160)*scl, (ht+1-doffs)*scl, (boxheight-3)*scl]).add(b)
    u -= b
    b = cube([(31)*scl, (offs)*scl, (150)*scl])
    c = translate(v=[(159)*scl, (ht-offs+1-doffs)*scl,
                                    (40)*scl]).add(b)
    u -= c
    # XXX secondary cutout
    b = cube([(31)*scl, (offs)*scl, (boxheight-44-24)*scl])
    c = translate(v=[(105)*scl, (ht-offs+1-doffs)*scl,
                                    (55)*scl]).add(b)
    u -= c

    # remove runner along top of base, for front top panel 
    if (ht_offset > 0):
        dropoffs = 3
        c = shearedcube([12*scl, (ht+2)*scl, (12)*scl],
                    shear=[0*scl, 0*scl, 0],
                    innershear=[-12*scl, 0*scl, 0])
        c = translate(v=[(180)*scl, -1*scl,
                                    (dropoffs)*scl]).add(c)
        u -= c

    if pin_parts_3d:
        c = union()
        h = pin(B0, scl)
        h = translate([(ht)*scl, (-3)*scl, 10*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(ht+75)*scl, (-3)*scl, 80*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(ht)*scl, (-3)*scl, 155*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(ht-76)*scl, (-3)*scl, 155*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(ht/2-38+100)*scl, (-3)*scl, 0*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(ht/2+138)*scl, (-3)*scl, 0*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(ht/2-38-50)*scl, (-3)*scl, 120*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(ht/2+38-50)*scl, (-3)*scl, 120*scl]).add(h)
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
        c = translate([(front_top_width-6+4.2)*scl, (0)*scl, 0*scl]).add(c)


        h = cube([40*scl, 6*scl, (boxheight-2)*scl])
        h = translate([(front_top_width-40)*scl, (0)*scl, 1*scl]).add(h)
        c += h

        h = cube([90*scl, 85*scl, (6)*scl])
        h = translate([(front_top_width-90)*scl, (ht-130)*scl, 81*scl]).add(h)
        c += h

        h = cube([30*scl, 60*scl, (6)*scl])
        h = translate([(front_top_width-30)*scl, (ht-120)*scl, (boxheight-6)*scl]).add(h)
        c += h
        h = translate([0, 0*scl, (-boxheight+48)*scl]).add(h)
        c += h

        v = union()
        d = pin_t(257)
        v += translate([(70)*scl, 0, 0]).add(d)
        v += translate([(ht*0.53)*scl, 0, 0]).add(d)
        v += translate([(ht*0.3)*scl, 0, 0]).add(d)
        d = pin_t(214)
        v += translate([(ht*0.74)*scl, 0, 0]).add(d)
        v += translate([(ht-89)*scl, 0, 0]).add(d)
        d = pin_t(ht+100, dep=35)
        d = rotate([0, 90, 0]).add(d)
        d = translate([50*scl, 0, boxheight*0.55*scl]).add(d)
        v += d
        v = rotate([0, 0, 90]).add(v)
        v = rotate([0, 180, 0]).add(v)
        v = translate(v=[(front_top_width)*scl, (0)*scl,
                    (boxheight+5)*scl]).add(v)
        c += v

        h = cube([(1.2)*scl, (ht+ht_offset-tpanel_l-70)*scl,
                            (boxheight-35)*scl])
        h = translate(v=[(180-1.2)*scl, (100)*scl,
                            (21)*scl]).add(h)
        c += h

        u += c

    # remove runner along bottom of base, for lower panel
    c = shearedcube([15*scl, (ht+2)*scl, (14)*scl],
                shear=[0*scl, 0*scl, 0],
                innershear=[14*scl, 0*scl, 0])
    c = translate(v=[(front_top_width-11)*scl, (-1-doffs)*scl,
                                (boxheight-hthick-4)*scl]).add(c)
    u -= c

    if cutdown:
        c = cube([300*scl, ht*scl, 200*scl])
        u -= translate([-1*scl, 20*scl, -1*scl]).add(c)

    v = union()
    u = translate(v=[0*scl, 0, (55)*scl]).add(u)
    v.add(u)
    return v

def base_cutout(scl, ht, loffs=0, arch=False, doffs=0):

    dep = (boxheight-hthick*2)
    u = union()
    # add fill-ins
    c = cube([(99.2-loffs-doffs)*scl, ht*scl, dep*scl])
    c = translate(v=[(-back_top_width+loffs+doffs)*scl,
                     0*scl, (hthick)*scl]).add(c)
    u += c

    c = cube([(130.2-loffs)*scl, ht*scl, (42)*scl])
    c = translate(v=[(-170+loffs)*scl, 0*scl, (hthick)*scl]).add(c)
    u += c

    # cutout lower and upper arcs
    c = touch_arc(0, ht, 40-hthick,
                        25, scl,
                  angle=0)
    c = rotate([90, 0, 0]).add(c)
    c = rotate([0, -90, 0]).add(c)
    # XXX resize needed to do something odd with openscad (fixes a bug)
    c = resize([(40-hthick+0.5)*scl, 0, 0], False).add(c)
    c = translate(v=[(-40)*scl, 0*scl, (40)*scl]).add(c)
    u += c

    c = touch_arc(0, ht, (boxheight-40-hthick+0.2),
                        25, scl,
                  angle=0)
    c = rotate([90, 0, 0]).add(c)
    c = rotate([0, 180, 0]).add(c)
    c = resize([(150-hthick)*scl, 0, 0], False).add(c)
    c = translate(v=[(-150)*scl, 0*scl, (40-0.2)*scl]).add(c)
    u += c

    if arch:
        c = cylinder(r=dep/2.0*scl, h=ht*4*scl, segments=90, center=True)
        c = resize([(dep*2.2)*scl, 0, 0], False).add(c)
        c = rotate([90, 0, 0]).add(c)
        c = translate(v=[(-160-dep+loffs+doffs)*scl, 0*scl, (dep/2+12)*scl]).add(c)
        u -= c

    return u

def base_back_hinge(scl, ht, scrn_hinge_ht, toffs):
    u = union()
    w1 = boxlength-back_top_width
    bht = ht
    friclen = ht-128

    print "BASE_BACK_HINGE ht", bht, friclen
    walls = {T:hthick, L:-1, R:hthick, F:50,
                                        D:hthick, B:ht-50}
    curverads={
                R|D: (boxheight-40, 0),
                R|T: (40, 0),
                }
    scalecurve = {
                R|D: [0, 150]
            }
    b = hollowbox(scl, back_top_width, bht-1, boxheight,
                    walls, curverads=curverads, scalecurve=scalecurve)
    b = translate(v=[w1*scl, 0, 0]).add(b)
    u += b

    # fill in around hinge before cut-out
    c = cube([120*scl, (scrn_hinge_ht+2)*scl, 40*scl])
    c = translate(v=[(w1+20)*scl,hthick*scl,(5)*scl]).add(c)
    u += c

    w = boxlength-112

    rad=35.0 + 12
    # cut down for hinge, but allow a stop at 150 degrees
    d = union()
    c = cube([rad*3*scl, (scrn_hinge_ht+2)*scl, boxheight*1.1*scl])
    d += c
    c = cube([rad*4*scl, (scrn_hinge_ht+3)*scl, boxheight*1.2*scl])
    c = rotate([0, 16, 0]).add(c)
    c = translate(v=[(-185)*scl,-1*scl,(90)*scl]).add(c)
    d -= c
    
    c = translate(v=[(w+10)*scl,-1*scl,(0)*scl]).add(d)
    u -= c

    # cut-off for screen
    c = shearedcube([(100*2)*scl, (scrn_hinge_ht+2)*scl, (hinge_offs)*scl],
                shear=[58*scl, 0, 0],
                innershear=[-15*scl, 0, 0])
    c = rotate([180, 0, 0]).add(c)
    c = rotate([0, 0, 180]).add(c)
    c = translate(v=[(w+215)*scl,-1*scl,(-25+hinge_offs)*scl]).add(c)
    u -= c

    # cable access and interlock with base_end
    c = shearedcube([(41)*scl, (boxheight-hthick*2)*scl, 61*scl],
                shear=[50*scl, 0, 0],
                innershear=[0*scl, 0, 0])
    c = rotate([90, 0, 0]).add(c)
    c = translate(v=[(w-back_top_width+110)*scl,59*scl,(hthick)*scl]).add(c)
    u -= c
    c = shearedcube([(61)*scl, (40)*scl, 61*scl],
                shear=[50*scl, 0, 0],
                innershear=[0*scl, 0, 0])
    c = rotate([90, 0, 0]).add(c)
    c = translate(v=[(w-back_top_width+140)*scl,29*scl,
                    (boxheight-hthick-45)*scl]).add(c)
    u -= c
    c = shearedcube([(61)*scl, (43)*scl, 14*scl],
                shear=[10*scl, 0, 0],
                innershear=[0*scl, 0, 0])
    c = rotate([90, 0, 0]).add(c)
    c = translate(v=[(w-back_top_width+177)*scl,13*scl,
                    (20)*scl]).add(c)
    u -= c
    c = cube([(80)*scl, (50)*scl, 63*scl])
    c = translate(v=[(w-back_top_width+112)*scl,13*scl,
                    (50)*scl]).add(c)
    u += c
    c = cube([(15)*scl, (70)*scl, 41*scl])
    c = translate(v=[(w-back_top_width+112)*scl,0*scl,
                    (hthick)*scl]).add(c)
    u += c
    c = cube([(140)*scl, (80)*scl, 12*scl])
    c = translate(v=[(w-back_top_width+112)*scl,-15*scl,
                    (boxheight-hthick-12)*scl]).add(c)
    u += c
    c = shearedcube([(10)*scl, (16)*scl, 5*scl],
                shear=[5*scl, 0, 0],
                innershear=[0*scl, 0, 0])
    c = translate(v=[(w-back_top_width+112)*scl,-16*scl,
                    (boxheight-hthick-4)*scl]).add(c)
    u -= c
    c = cube([(140)*scl, (75)*scl, 12*scl])
    c = translate(v=[(w-back_top_width+112)*scl,-10*scl,
                    (53)*scl]).add(c)
    u += c

    # lock-in slot to base_back_bot
    c = union()
    d = cube([70*scl, 35*scl, (boxheight-30)*scl], center=True)
    d = translate(v=[(70)*scl, (0)*scl, (19)*scl]).add(d)
    c += d
    d = cube([200*scl, 35*scl, 40*scl], center=True)
    d = translate(v=[(0)*scl, (0)*scl, (20)*scl]).add(d)
    c += d
    c = translate(v=[(-65)*scl, (ht-16)*scl, (boxheight-55)*scl]).add(c)
    t = case_bolthole(scl, 2).add(c)
    u -= t

    # screw holes in box
    t = box_screwholes(scl, hthick, holes=[2], h=320, rad=35./2)
    t = translate(v=[0, 0, (boxheight-55)*scl]).add(t)
    u -= t

    # remove runner along bottom of base, for lower panel
    c = shearedcube([14*scl, (ht+300)*scl, (14)*scl],
                shear=[-12*scl, 0*scl, 0],
                innershear=[0*scl, 0*scl, 0])
    c = translate(v=[(boxlength-back_top_width-5)*scl, (-21-0)*scl,
                                (boxheight-hthick-4)*scl]).add(c)
    u -= c

    rad=35.0 + 15
    # add hinge
    d = union()
    c = cylinder(r=rad*scl, h=(friclen+44)*scl, segments=50)
    c = rotate([0, 90, 90]).add(c)
    d += c
    c = cube([55*scl, (friclen+44)*scl, 93*scl])
    c = translate(v=[-60*scl,0*scl,(-35)*scl]).add(c)
    d += c
    c = cube([35*scl, (friclen+44)*scl, 100*scl])
    c = translate(v=[-60*scl,0*scl,(-35)*scl]).add(c)
    d += c
    c = translate(v=[0*scl,(scrn_hinge_ht+1)*scl,(-55)*scl]).add(d)
    t = hinge_translate(scl).add(c)
    u += t

    # hollow hinge out
    c = cylinder(r=(rad-12)*scl, h=(friclen+40)*scl, segments=50)
    c = rotate([0, 90, 90]).add(c)
    c = translate(v=[0*scl,(scrn_hinge_ht-1)*scl,-55*scl]).add(c)
    t = hinge_translate(scl).add(c)
    u -= t
    c = cylinder(r=(rad+2)*scl, h=(scrn_hinge_ht+2+40)*scl,
                    segments=50)
    c = rotate([0, 90, 90]).add(c)
    c = translate(v=[0*scl,(-1-40)*scl,-55*scl]).add(c)
    t = hinge_translate(scl).add(c)
    u -= t
    # add lock-in to base_back_hinge
    c = cylinder(r=(rad-8)*scl, r1 = (rad-12)*scl, h=(14)*scl, segments=50)
    c = rotate([0, 90, 90]).add(c)
    c = translate(v=[0*scl,(ht+scrn_hinge_ht-25.5)*scl,-55*scl]).add(c)
    t = hinge_translate(scl).add(c)
    u -= t
    # hole for bolt
    c = cylinder(r=(35./2)*scl, h=(friclen+90)*scl, segments=50)
    c = rotate([0, 90, 90]).add(c)
    c = translate(v=[0*scl,(scrn_hinge_ht-1)*scl,-55*scl]).add(c)
    t = hinge_translate(scl).add(c)
    u -= t

    # capture channel in hinge
    hd = 25
    v = union()
    c = shearedcube([24*scl, (friclen+scrn_hinge_ht+40)*scl, hd*scl], center=True,
                shear=[-3*scl, 0*scl, 0],
                innershear=[0*scl, 0*scl, 0])
    c = rotate([90, 0, 0]).add(c)
    c = translate(v=[5*scl,-40*scl,20*scl]).add(c)
    v += c
    c = shearedcube([24*scl, (friclen+scrn_hinge_ht+40)*scl, hd*scl], center=True,
                shear=[0*scl, 0*scl, 0],
                innershear=[3*scl, 0*scl, 0])
    c = rotate([90, 0, 0]).add(c)
    c = translate(v=[-5*scl,-40*scl, 20*scl]).add(c)
    v += c

    v = rotate([90, 0, 0]).add(v)
    v = rotate([0, 90, 0]).add(v)
    c = translate(v=[0*scl,((scrn_hinge_ht+friclen)/2+30)*scl,-55*scl]).add(v)
    t = hinge_translate(scl).add(c)
    u -= t

    # hollow out below screw hole
    c = shearedcube([150*scl, (ht-140)*scl, (boxheight-95)*scl],
                shear=[35*scl, 0*scl, 0],
                innershear=[0*scl, 0*scl, 0])
    c = translate(v=[(w1-1)*scl,90*scl,(70)*scl]).add(c)
    u -= c

    # hollow out above screw hole
    c = shearedcube([100*scl, (ht-140)*scl, (40)*scl],
                shear=[-35*scl, 0*scl, 0],
                innershear=[0*scl, 0*scl, 0])
    c = translate(v=[(w1-1)*scl,90*scl,(15)*scl]).add(c)
    u -= c
    
    if pin_parts_3d:
        v = union()

        d = pin_t()

        v += translate([(40)*scl, 0, 0]).add(d)
        v += translate([(120)*scl, 0, 0]).add(d)
        d = pin_t(ht=240, dep=35)
        d = rotate([0, 90, 0]).add(d)
        v += translate([130*scl, 0, (64)*scl]).add(d)

        h = pin(B0, scl, fill=True)
        v += translate([(-30)*scl, (-3)*scl, 22*scl]).add(h)
        v += translate([(-30)*scl, (-3)*scl, 97*scl]).add(h)
        v += translate([(77)*scl, (-3)*scl, 153*scl]).add(h)
        v += translate([(202)*scl, (-3)*scl, 113*scl]).add(h)
        v += translate([(77)*scl, (-3)*scl, -30*scl]).add(h)
        v += translate([(202)*scl, (-3)*scl, -30*scl]).add(h)
        v += translate([(-10)*scl, (-3)*scl, 140*scl]).add(h)
        v += translate([(-10)*scl, (-3)*scl, -16*scl]).add(h)
        v = translate([(w-58-79)*scl, (ht)*scl, 0*scl]).add(v)

        u += v


        c = cube([6*scl, 40*scl, 70*scl])
        c = translate([(w-64)*scl, (ht-40)*scl, 15*scl]).add(c)
        u += c

    v = union()
    u = translate(v=[0*scl, 0, (55)*scl]).add(u)
    v.add(u)

    if cutdown:
        # cut down
        c = cube([(boxlength-300+80)*scl, (ht+100)*scl, 400*scl])
        c = translate([(300)*scl, 212.0*scl, -50*scl]).add(c)
        v -= c
        c = cube([(boxlength-300+60)*scl, (ht+100)*scl, 400*scl])
        c = translate([(95)*scl, -150*scl, -50*scl]).add(c)
        v -= c

        if pin_parts_3d:

            c = union()

            h = pin(B0, scl)
            h = translate([(150)*scl, (0)*scl, 15*scl]).add(h)
            c += h
            h = pin(B0, scl)
            h = translate([(150)*scl, (0)*scl, 104*scl]).add(h)
            c += h
            h = pin(B0, scl)
            h = translate([(240)*scl, (0)*scl, 15*scl]).add(h)
            c += h
            h = pin(B0, scl)
            h = translate([(70)*scl, (0)*scl, 104*scl]).add(h)
            c += h
            h = pin(B0, scl)
            h = translate([(70)*scl, (0)*scl, 15*scl]).add(h)
            c += h
            h = pin(B0, scl)
            h = translate([(0)*scl, (0)*scl, 104*scl]).add(h)
            c += h
            h = pin(B0, scl)
            h = translate([(0)*scl, (0)*scl, 15*scl]).add(h)
            c += h
            h = pin(B0, scl)
            h = translate([(240)*scl, (0)*scl, 104*scl]).add(h)
            c += h
            c = rotate([0, 0, 90]).add(c)
            c = translate([(w-30)*scl, (0)*scl, 55*scl]).add(c)

            v += c

    if orientate:
        v = rotate([-90, 0, 0]).add(v)

    return v

def base_back_bot(scl, ht, scrn_hinge_ht, toffs):
    u = union()
    w = boxlength-back_top_width
    bht = ht+base_centre_ht/2

    print "BASE_BACK ht", bht

    wthick = 130
    walls = {T:hthick, L:-1, R:hthick, F:wthick-3+hthick+base_centre_ht/2,
                                        D:hthick, B:110}
    curverads={
                R|D: (boxheight-40, 0),
                R|T: (40, 0),
                }
    scalecurve = {
                R|D: [0, 150]
            }
    b = hollowbox(scl, back_top_width, bht, boxheight,
                    walls, curverads=curverads, scalecurve=scalecurve)
    b = translate(v=[w*scl, 0, 0]).add(b)
    u += b

    # fill in around hinge before cut-out
    c = cube([120*scl, (scrn_hinge_ht+2)*scl, 40*scl])
    c = translate(v=[(w+20)*scl,hthick*scl,(5)*scl]).add(c)
    u += c

    w = boxlength-112
    rad=35.0 + 12
    # cut down for hinge, but allow a stop at 150 degrees
    d = union()
    c = cube([rad*3*scl, (scrn_hinge_ht+2)*scl, boxheight*1.1*scl])
    d += c
    c = cube([rad*4*scl, (scrn_hinge_ht+3)*scl, boxheight*1.2*scl])
    c = rotate([0, 16, 0]).add(c)
    c = translate(v=[(-185)*scl,-1*scl,(90)*scl]).add(c)
    d -= c
    
    c = translate(v=[(w+10)*scl,-1*scl,(0)*scl]).add(d)
    u -= c

    # calculate pcb / battery support locations, needed to jump cutouts
    boffs = ht + toffs - tpanel_l_b/2 +8
    if toffs < 0:
        boffs += 50

    fthick = 6
    offs = scrn_hinge_ht+hthick+fthick+60
    c = base_cutout(scl, ht-wthick-offs-2)
    c = resize([(238)*scl, 0, (boxheight-hthick*2)*scl], False).add(c)
    c = translate(v=[boxlength*scl, (offs-fthick)*scl, (0)*scl]).add(c)
    u -= c

    # put in series of cutouts
    offs -= 105 
    step = (ht-wthick-offs) / (4.0 if test else 14.0)
    offs += step 
    while offs < (ht-step-90):
        # add fill-ins
        b = base_cutout(scl, fthick, arch=True)
        b = resize([(236)*scl, 0,
                    pow(2, 0.5)*(boxheight-hthick*2+10)*scl], False).add(b)
        c = rotate([43, 0, 0]).add(b)
        c = translate(v=[boxlength*scl, (offs-fthick+step+35)*scl, (-9)*scl]).add(c)
        u += c
        offs += step
        if abs(offs - boffs+step) < 90:
            if toffs < 0:
                offs += 50
            else:
                offs += 80
        c = rotate([-43, 0, 0]).add(b)
        c = translate(v=[boxlength*scl, (offs-fthick)*scl,
                (-5)*scl]).add(c)
        u += c

        offs += step

    # add runner support, has to be done before pcb/battery support
    for h in [ht*0.310, ht*0.515, ht*0.74, 62]:
        c = shearedcube([(back_top_width-80)*scl, (40)*scl, (15)*scl])
        c = translate(v=[(boxlength-back_top_width)*scl, h*scl,
                                    (boxheight-hthick-13)*scl]).add(c)
        u += c
    # ok these are for the pcb1_support and battery_support1
    # they extend all the way to the back (for injection molding)
    c = base_cutout(scl, 54)
    c = resize([(236)*scl, 0, (boxheight-hthick*2+2)*scl], False).add(c)
    c = translate(v=[boxlength*scl, (boffs)*scl, (-1)*scl]).add(c)
    u += c

    # ... cutout for the actual support, the rest was housing for the cutout
    c = cube([30*scl, 37*scl, (boxheight-47)*scl])
    c = translate(v=[-22*scl, (9)*scl, (-3)*scl]).add(c)
    c = translate(v=[(lcd_w+69-79)*scl, (boffs)*scl, (39.5)*scl]).add(c)
    u -= c

    # fits into back base hinge
    c = union()
    d = shearedcube([(50)*scl, (boxheight-35)*scl, (33)*scl], center=True,
                shear=[3*scl, 0*scl, 0],
                innershear=[-3*scl, 0*scl, 0])
    d = rotate([0, 90, 90]).add(d)
    d = rotate([0, 90, 0]).add(d)
    d = translate(v=[(64)*scl, (0)*scl, 19*scl]).add(d)
    c += d
    d = shearedcube([(30)*scl, 130*scl, (33)*scl], center=True,
                shear=[3*scl, 0*scl, 0],
                innershear=[-3*scl, 0*scl, 0])
    d = rotate([0, 90, 90]).add(d)
    d = translate(v=[(20)*scl, (0)*scl, (20)*scl]).add(d)
    c += d
    c = translate(v=[-64*scl, (-15.5)*scl, (boxheight-55)*scl]).add(c)
    c = case_bolthole(scl, 2).add(c)
    u += c

    # lock-in slot to base_back_bot
    d = cube([110*scl, 35*scl, 58*scl], center=True)
    d = translate(v=[(90)*scl, (0)*scl, (0)*scl]).add(d)
    c += d
    d = cube([200*scl, 35*scl, 40*scl], center=True)
    d = translate(v=[(0)*scl, (0)*scl, (20)*scl]).add(d)
    c += d
    c = translate(v=[(-65)*scl, (198)*scl, (boxheight-55)*scl]).add(c)
    t = case_bolthole(scl, 2).add(c)
    #u -= t

    # slot to fit a nut into
    # XXX TODO: fill this all the way back (for mold purposes)
    c = cube([(40+73)*scl, 40*scl, (boxheight-10)*scl], center=True)
    c = translate(v=[(lcd_w+85-79/2.)*scl, (68)*scl, (boxheight/2)*scl]).add(c)
    #u += c
    c = cube([200*scl, 34*scl, 62*scl], center=True)
    c = translate(v=[(-100)*scl, (67)*scl, (boxheight-55)*scl]).add(c)
    t = case_bolthole(scl, 2).add(c)
    u -= t
    c = cube([200*scl, 52*scl, 60*scl], center=True)
    c = translate(v=[(-140)*scl, (101)*scl, (boxheight-55)*scl]).add(c)
    t = case_bolthole(scl, 2).add(c)
    u -= t
    c = cylinder(r=36.0*scl, h=34*scl, center=True, segments=6)
    c = rotate([0, 90, 90]).add(c)
    c = rotate([0, 30, 0]).add(c)
    t = case_bolthole(scl, 2).add(c)
    t = translate(v=[(0)*scl, (67)*scl, (boxheight-55)*scl]).add(t)
    u -= t

    # screw holes in box
    t = box_screwholes(scl, hthick, holes=[2], h=120, rad=35./2)
    t = translate(v=[0, -10*scl, (boxheight-55)*scl]).add(t)
    u -= t

    # fit base_mid
    wd = back_top_width-109
    b = cube([(288)*scl, (123)*scl, (80)*scl])
    b = translate(v=[(w-wd+78)*scl, (ht-112)*scl, (boxheight-46)*scl]).add(b)
    u -= b
    b = cube([(288)*scl, (base_centre_ht/2+123)*scl, (boxheight+50)*scl])
    b = translate(v=[(w-61+75)*scl, (ht-112)*scl, (38)*scl]).add(b)
    u -= b
    b = cube([(288)*scl, (base_centre_ht/2+93)*scl, (boxheight)*scl])
    b = translate(v=[(w-wd)*scl, (ht-2)*scl, (38)*scl]).add(b)
    u -= b

    # screw-holes into base_mid
    s = chamfered_backbox_screwholes(scl, 50)
    s = rotate([-180, 0, 0]).add(s)
    b = translate(v=[(w-75)*scl, (ht+25)*scl, (16)*scl]).add(s)
    u -= b
    b = translate(v=[(w+50)*scl, (ht-85)*scl, (16)*scl]).add(s)
    u -= b

    rad=35.0 + 12

    # screw from friction hinge pokes through here
    c = union()
    d = cylinder(r=(18)*scl, h=(90)*scl, segments=50)
    d = translate(v=[0*scl,0*scl,-29*scl]).add(d)
    c.add(d)
    c = rotate([0, 90, 90]).add(c)
    c = translate(v=[0*scl,(scrn_hinge_ht+15)*scl,-55*scl]).add(c)
    t = hinge_translate(scl).add(c)
    u -= t

    # XXX: base panel runner is removed after pinning

    if pin_parts_3d:
        c = union()
        h = pin(B0, scl, fill=True)
        h = translate([(ht-52)*scl, (-3)*scl, -25*scl]).add(h)
        c += h
        h = translate([(-75)*scl, (0)*scl, 0*scl]).add(h)
        c += h
        h = pin(B0, scl, fill=True)
        h = translate([(ht+25)*scl, (-3)*scl, -25*scl]).add(h)
        c += h
        h = pin(B0, scl, fill=True)
        h = translate([(ht+25)*scl, (-3)*scl, 65*scl]).add(h)
        c += h
        h = pin(B0, scl, fill=True)
        h = translate([(ht+102)*scl, (-3)*scl, 85*scl]).add(h)
        c += h
        h = pin(B0, scl, fill=True)
        h = translate([(ht+102)*scl, (-3)*scl, 5*scl]).add(h)
        c += h
        h = pin(B0, scl, fill=True)
        h = translate([(ht-47)*scl, (-3)*scl, 140*scl]).add(h)
        c += h
        h = translate([(-75)*scl, (0)*scl, 0*scl]).add(h)
        c += h
        h = pin(B0, scl, fill=True)
        h = translate([(ht-47+75)*scl, (-3)*scl, 140*scl]).add(h)
        c += h

        d = pin_t()

        c += translate([(110)*scl, 0, 0]).add(d)
        c += translate([(ht*0.53)*scl, 0, 0]).add(d)
        c += translate([(ht*0.74)*scl, 0, 0]).add(d)
        c += translate([(ht*0.3)*scl, 0, 0]).add(d)
        c += translate([(ht-85)*scl, 0, 0]).add(d)

        d = pin_t(ht=ht+220)
        d = rotate([0, 90, 0]).add(d)
        c += translate([(-40)*scl, 0, 65*scl]).add(d)
        d = cube([(30)*scl, 90*scl, 6*scl])
        c += translate([(-30)*scl, -90*scl, 16.5*scl]).add(d)
        c += translate([(-30)*scl, -90*scl, 99.5*scl]).add(d)

        h = pin(B0, scl, fill=True)
        h = translate([(-30)*scl, (-3)*scl, 22*scl]).add(h)
        c += h
        h = translate([(0)*scl, (0)*scl, 75*scl]).add(h)
        c += h
        h = pin(B0, scl, fill=True)
        h = translate([(77)*scl, (-3)*scl, 153*scl]).add(h)
        c += h
        h = translate([(75)*scl, (0)*scl, 0*scl]).add(h)
        c += h
        h = pin(B0, scl, fill=True)
        h = translate([(77)*scl, (-3)*scl, -30*scl]).add(h)
        c += h
        h = translate([(75)*scl, (0)*scl, 0*scl]).add(h)
        c += h
        h = pin(B0, scl, fill=True)
        h = translate([(0)*scl, (-3)*scl, 140*scl]).add(h)
        c += h
        h = pin(B0, scl, fill=True)
        h = translate([(0)*scl, (-3)*scl, -16*scl]).add(h)
        c += h
        offs = ht + toffs - tpanel_l_b/2 +8
        if toffs > 0:
            offs -= 50
        h = cube([(offs-45)*scl, 1.8*scl, boxheight*1.5*scl])
        h = translate([(100)*scl, (-1.8)*scl, -boxheight*0.25*scl]).add(h)
        c += h
        h = cube([(ht-offs-235)*scl, 1.8*scl, boxheight*1.5*scl])
        h = translate([(offs+100)*scl, (-1.8)*scl, -boxheight*0.25*scl]).add(h)
        c += h
        c = rotate([0, 0, 90]).add(c)
        c = translate([(w-58-79)*scl, (0)*scl, 0*scl]).add(c)

        u += c

        c = cube([105*scl,36*scl,6*scl], center=True)
        c = translate(v=[-15*scl,(scrn_hinge_ht+10)*scl,-55*scl]).add(c)
        t = hinge_translate(scl).add(c)
        u += t

    # remove runner along bottom of base, for lower panel
    c = shearedcube([15*scl, (ht+2)*scl, (14)*scl],
                shear=[-12*scl, 0*scl, 0],
                innershear=[0*scl, 0*scl, 0])
    c = translate(v=[(boxlength-back_top_width-5)*scl, (-1)*scl,
                                (boxheight-hthick-5)*scl]).add(c)
    u -= c

    v = union()
    u = translate(v=[0*scl, 0, (55)*scl]).add(u)
    v.add(u)

    if cutdown:
        # cut down
        c = cube([(boxlength-300+80)*scl, (ht+300)*scl, 500*scl])
        c = translate([(300)*scl, 70.0*scl, -100*scl]).add(c)
        v -= c
        c = cube([(boxlength-300+60)*scl, (413)*scl, 500*scl])
        c = translate([(130)*scl, -250*scl, -100*scl]).add(c)
        v -= c

        if pin_parts_3d:

            c = union()

            h = pin(B0, scl)
            c += translate([(70)*scl, (0)*scl, 104*scl]).add(h)
            c += translate([(70)*scl, (0)*scl, 15*scl]).add(h)
            c += translate([(-15)*scl, (0)*scl, 104*scl]).add(h)
            c += translate([(-15)*scl, (0)*scl, 15*scl]).add(h)
            c = rotate([0, 0, 90]).add(c)
            c = translate([(w+5)*scl, (0)*scl, 55*scl]).add(c)

            v += c

    return v

def front_mid_joiner(scl, ht):
    u = union()
    w = boxlength

    b = cube([(62)*scl, (ht)*scl, 32*scl], center=True)
    u += b

    b = cylinder(r=9.6*scl, h=(50)*scl, center=True, segments=50)
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

    b = cylinder(r=9.6*scl, h=(50)*scl, center=True, segments=50)
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

def base_mid(scl, ht, base_screwholes=False):
    u = union()
    w = boxlength-150

    walls = {T:-1, L:-1, R:hthick, F:32, D:8, B:32}
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

    # fillin for tpanel_mid screwhole
    c = cube([(170)*scl, (ht)*scl, (boxheight-42)*scl])
    c = translate(v=[(tpanel_l_b-160)*scl, (0)*scl, (40)*scl]).add(c)
    u += c

    # cutout sides
    d = cube([(boxlength-180-back_top_width-82)*scl, (32)*scl, (boxheight)*scl])
    u -= translate(v=[(180+35)*scl, -10*scl, -20*scl]).add(d)
    u -= translate(v=[(180+35)*scl, (ht-22)*scl, -20*scl]).add(d)
    
    # couple of wings on the side for back base to screw into
    walls[F] = 110
    walls[B] = 110
    b = hollowbox(scl, 170, ht+220, boxheight-40,
                    walls, curverads=curverads, scalecurve=scalecurve)
    b = translate(v=[(w-20)*scl, -110*scl, 40*scl]).add(b)
    u += b

    # end wall for tpanel_mid to lock into
    v = union()
    # wings for screw-holes to fit with front base
    d = cube([(boxheight-40-2)*scl, (48)*scl, (100)*scl])
    d = rotate([0, 90, 0]).add(d)
    d = rotate([0, 0, 90]).add(d)
    c = translate(v=[(180-1)*scl, (-68)*scl, (boxheight)*scl]).add(d)
    v += c
    d = rotate([0, 0, 180]).add(d)
    c = translate(v=[(180-50)*scl, (ht+68)*scl, (boxheight)*scl]).add(d)
    v += c
    d = cube([40*scl, (base_centre_ht)*scl, (boxheight-42)*scl])
    c = translate(v=[(175)*scl, (0)*scl, (40)*scl]).add(d)
    v += c
    # remove runner along bottom of base, for lower panel
    d = union()
    c = shearedcube([15*scl, (ht+2+80*2)*scl, (14)*scl],
                shear=[0*scl, 0*scl, 0],
                innershear=[14*scl, 0*scl, 0])
    c = translate(v=[(180-12)*scl, (-1-80)*scl,
                                (boxheight-hthick-4)*scl]).add(c)
    d += c
    c = cube([40*scl, (base_centre_ht)*scl, (40)*scl])
    c = translate(v=[(180-12)*scl, (0)*scl,
                                (boxheight-hthick-5)*scl]).add(c)
    d -= c
    v -= d

    u += v

    if base_screwholes:
        # chamfered screw hole through to base_front
        s = chamfered_backbox_screwholes(scl, 50)
        s = rotate([0, 90, 0]).add(s)
        t = translate(v=[(200-50)*scl, (-30)*scl, (80)*scl]).add(s)
        u -= t
        t = translate(v=[(200-50)*scl, (base_centre_ht+30)*scl, (80)*scl])
        t.add(s)
        u -= t

    # hole for back screw-support to poke through
    # XXX height is magic constant
    b = cube([(86)*scl, (121)*scl, (41)*scl])
    b = translate(v=[(w-31)*scl, -(121)*scl, (39)*scl]).add(b)
    u -= b
    b = translate(v=[(0)*scl, (ht+121)*scl, (0)*scl]).add(b)
    u -= b

    # dovetail cuts to fit into front base
    # XXX height is magic constant
    b = shearedcube([(50)*scl, (ht+2+80*2)*scl, (32)*scl],
            shear=[0*scl, 0*scl, 0],
            innershear=[10*scl, 0*scl, 0])
    b = rotate([0, 90, 0]).add(b)
    b = translate(v=[(129)*scl, -81*scl, (62)*scl]).add(b)
    u -= b
    b = rotate([180, 0, 0]).add(b)
    b = translate(v=[(0)*scl, (ht)*scl, (168)*scl]).add(b)
    u -= b

    # remove centre between screw wings
    b = cube([(60)*scl, (ht-62)*scl, (boxheight)*scl])
    b = translate(v=[(122)*scl, (31)*scl, (39)*scl]).add(b)
    u -= b

    # diagonal cross-walls for internal stiffness
    fthick = 7
    offs = 190#tpanel_l_b+40
    step = (w-160-offs) / (8.0 if test else 22.0)
    steps = []
    while offs < (w-step*2):
        steps.append((offs+20, boxheight-39-2))
        offs += step

    #steps.append((210, boxheight-39-2))
    #steps.append((280, boxheight-59-2))

    alternate = True
    for (offs, ch) in steps:
        hoff = (boxheight-39-2) - ch
        d = cube([fthick*scl, 125*scl, ch*scl])
        if alternate:
            c = rotate([0, 0, -45]).add(d)
            c = translate(v=[(offs)*scl, (29)*scl, (40+hoff)*scl]).add(c)
            u += c
        else:
            c = rotate([0, 0, 45]).add(d)
            c = translate(v=[(offs+88)*scl, (24)*scl, (40+hoff)*scl]).add(c)
            u += c
        alternate = not alternate

    # fill in end for diagonals to mesh to
    c = cube([(140)*scl, (ht)*scl, (boxheight-39-hthick)*scl])
    c = translate(v=[(w-120)*scl, (0)*scl, (40)*scl]).add(c)
    u += c

    # screw holes in top for back_box_base
    d = cylinder(r=topscrewrad*scl,
                    h=(65)*scl,
                    segments=50, center=True)
    t = translate(v=[(w+87)*scl, (-85)*scl, (50)*scl]).add(d)
    u -= t
    t = translate(v=[(w+87)*scl, (ht+85)*scl, (50)*scl]).add(d)
    u -= t
    t = translate(v=[(w-38)*scl, (25)*scl, (50)*scl]).add(d)
    u -= t
    t = translate(v=[(w-38)*scl, (ht-25)*scl, (50)*scl]).add(d)
    u -= t
    # and for tpanel_mid
    t = translate(v=[(tpanel_l_b-75)*scl, (ht/2)*scl, (60)*scl]).add(d)
    u -= t

    # cutout for cable from PCB2 to PCB3
    c = cube([250*scl, (base_centre_ht+4)*scl, (55)*scl])
    c = translate(v=[(tpanel_l_b-480)*scl, (ht/2-(base_centre_ht+4.)/2)*scl,
                (0)*scl]).add(c)
    u -= c

    # cutout for cable from PCB1 to PCB3
    c = cube([200*scl, (base_centre_ht+4)*scl, (55)*scl])
    c = translate(v=[(tpanel_l_b+700)*scl, (ht/2-(base_centre_ht+4.)/2)*scl,
                (0)*scl]).add(c)
    u -= c

    # back keyboard support
    b = hollowbox(scl, 13, ht, boxheight,
                {T:-1, L:13, R:-1, F:-1, D:-1, B:-1},
                curverads={ T|L: (hthick, 0)})
    b = translate(v=[(w-40-74)*scl, 0*scl, (0)*scl]).add(b)
    u += b

    # lock for back keyboard runner
    d = shearedcube([(boxheight-70)*scl, 25*scl, 20*scl],
                shear=[0*scl, 0*scl, 0],
                innershear=[8*scl, 0*scl, 0])
    d = rotate([0, 90, 0]).add(d)
    d = rotate([0, 0, -90]).add(d)
    bl = boxlength - back_top_width - 47
    c = translate(v=[(bl)*scl,
                (1)*scl, (boxheight-17)*scl]).add(d)
    u += c
    d = rotate([0, 0, 180]).add(d)
    c = translate(v=[(bl+25)*scl,
                (ht-1)*scl, (53+50)*scl]).add(d)
    u += c
    d = cube([(32)*scl, ht*scl, (boxheight-40)*scl])
    c = translate(v=[(boxlength-back_top_width-27)*scl,
                (0)*scl, (40)*scl]).add(d)
    u += c
    d = shearedcube([(90)*scl, 22*scl, 20*scl],
                shear=[0*scl, 0*scl, 0],
                innershear=[17*scl, 0*scl, 0])
    d = rotate([0, 90, 0]).add(d)
    d = rotate([0, 0, 90]).add(d)
    c = translate(v=[(boxlength-back_top_width+0)*scl,
                (-5)*scl, (75)*scl]).add(d)
    u -= c
    d = rotate([0, 0, 180]).add(d)
    c = translate(v=[(boxlength-back_top_width-22)*scl,
                (ht+5)*scl, (74)*scl]).add(d)
    u -= c

    # now remove along length of base
    c = shearedcube([14*scl, (boxlength-180-150-5-8-6)*scl, (12)*scl],
                shear=[-12*scl, 0*scl, 0],
                innershear=[0*scl, 0*scl, 0])
    c = rotate([0, 0, 90]).add(c)
    c = translate(v=[(boxlength-180+8+8-6)*scl, (-3)*scl,
                                (boxheight-hthick-4)*scl]).add(c)
    u -= c
    c = shearedcube([14*scl, (boxlength-180-150-5-7-6)*scl, (12)*scl],
                shear=[0*scl, 0*scl, 0],
                innershear=[12*scl, 0*scl, 0])
    c = rotate([0, 0, 90]).add(c)
    c = translate(v=[(boxlength-180+8+8-6)*scl, (ht-10)*scl,
                                (boxheight-hthick-4)*scl]).add(c)
    u -= c

    if pin_parts_3d:
        c = union()
        h = pin(B0, scl, fill=True)
        h = translate([(130)*scl, (0)*scl, 15*scl]).add(h)
        c += h
        h = pin(B0, scl, fill=True)
        h = translate([(205)*scl, (0)*scl, -(ht+30)*scl]).add(h)
        c += h
        h = pin(B0, scl, fill=True)
        h = translate([(110)*scl, (0)*scl, -ht/2*scl]).add(h)
        c += h
        h = pin(B0, scl, fill=True)
        h = translate([(205)*scl, (0)*scl, 30*scl]).add(h)
        c += h
        h = pin(B0, scl, fill=True)
        h = translate([(130)*scl, (0)*scl, -(ht+15)*scl]).add(h)
        c += h

        h = pin(B0, scl, fill=True)
        h = translate([(w-52)*scl, (0)*scl, -(ht+90)*scl]).add(h)
        c += h
        h = pin(B0, scl, fill=True)
        h = translate([(w-52)*scl, (0)*scl, 90*scl]).add(h)
        c += h
        h = pin(B0, scl, fill=True)
        h = translate([(w-52)*scl, (0)*scl, -(ht+15)*scl]).add(h)
        c += h
        h = pin(B0, scl, fill=True)
        h = translate([(w-52)*scl, (0)*scl, (15)*scl]).add(h)
        c += h

        h = pin(B0, scl, fill=True)
        h = translate([(w+25)*scl, (0)*scl, -(ht+115)*scl]).add(h)
        c += h
        h = pin(B0, scl, fill=True)
        h = translate([(w+25)*scl, (0)*scl, 115*scl]).add(h)
        c += h
        h = pin(B0, scl, fill=True)
        h = translate([(w+100)*scl, (0)*scl, -(ht+115)*scl]).add(h)
        c += h
        h = pin(B0, scl, fill=True)
        h = translate([(w+100)*scl, (0)*scl, 115*scl]).add(h)
        c += h
        h = pin(B0, scl, fill=True)
        h = translate([(w+177)*scl, (0)*scl, -(ht+65)*scl]).add(h)
        c += h
        h = pin(B0, scl, fill=True)
        h = translate([(w+177)*scl, (0)*scl, (65)*scl]).add(h)
        c += h

        h = pin(B0, scl, fill=True)
        h = translate([(tpanel_l_b+65)*scl, (0)*scl, 32*scl]).add(h)
        c += h
        h = pin(B0, scl, fill=True)
        h = translate([(tpanel_l_b+65)*scl, (0)*scl, -(ht+32)*scl]).add(h)
        c += h

        c = rotate([90, 0, 0]).add(c)
        c = translate([(0)*scl, (0)*scl, (boxheight-3)*scl]).add(c)

        step = (ht+110-3) / 7.0
        offs = -110
        while offs < ht+110:
            h = cube([145*scl, 7*scl, (boxheight-40)*scl])
            h = translate([w*scl, (offs)*scl, 40*scl]).add(h)
            c += h
            offs += step

        h = cube([91*scl, (ht+124)*scl, 95*scl])
        h = translate([(w-1)*scl, (-111)*scl, 0*scl]).add(h)
        c -= h
        h = translate([(0)*scl, (ht+111)*scl, 0*scl]).add(h)
        c -= h
        h = cube([20*scl, (ht+220)*scl, 1.8*scl])
        h = translate([(w+125)*scl, (-110)*scl, (boxheight-1.8)*scl]).add(h)
        c += h

        u += c

    v = union()
    u = translate(v=[0*scl, 0, (55)*scl]).add(u)
    v.add(u)
    return v

def screen_mid(scl, ht):
    print "SCREEN_MID ht", ht

    u = union()
    b = screen_box(scl, ht, end=False)
    u += b

    # cutouts for connectors
    d = cube([(34)*scl, (ht+4)*scl, (39)*scl])
    c = translate(v=[25*scl, (-2)*scl, (-1)*scl]).add(d)
    u -= c
    c = translate(v=[(lcd_w+157)*scl, (-2)*scl, (-7)*scl]).add(d)
    u -= c
    d = cube([(45)*scl, (ht+2)*scl, (45)*scl])
    c = translate(v=[(lcd_w+75)*scl, (-1)*scl, (-5)*scl]).add(d)
    u -= c

    # remove runner for top panel
    c = shearedcube([2*scl, (boxlength-210)*scl, (14)*scl],
                shear=[0*scl, 0*scl, 0],
                innershear=[-14*scl, 0*scl, 0])
    c = rotate([0, 0, 90]).add(c)
    u -= translate(v=[(boxlength+10-140)*scl, (ht)*scl,
                                (-27)*scl]).add(c)
    c = rotate([0, 180, 0]).add(c)
    c = rotate([180, 0, 0]).add(c)
    u -= translate(v=[(80)*scl, (0)*scl,
                                (-27)*scl]).add(c)

    if pin_parts_3d:
        c = union()
        h = pin(B0, scl)
        c += translate([(boxlength-62)*scl, (0)*scl, -60*scl]).add(h)
        c += translate([(boxlength-140)*scl, (0)*scl, -75*scl]).add(h)
        c += translate([(boxlength+15)*scl, (0)*scl, 3*scl]).add(h)
        c += translate([(boxlength-18)*scl, (0)*scl, 85*scl]).add(h)
        c += translate([(boxlength-95)*scl, (0)*scl, 85*scl]).add(h)
        c += translate([(boxlength-165)*scl, (0)*scl, 85*scl]).add(h)

        c += translate([(190)*scl, (0)*scl, -75*scl]).add(h)
        c += translate([(107)*scl, (0)*scl, -75*scl]).add(h)
        c += translate([(30)*scl, (0)*scl, -45*scl]).add(h)
        c += translate([(-30)*scl, (0)*scl, 8*scl]).add(h)
        c += translate([(10)*scl, (0)*scl, 85*scl]).add(h)
        c += translate([(90)*scl, (0)*scl, 85*scl]).add(h)

        h = pin_t(0)
        h = rotate([0, 0, 180]).add(h)
        for l in [0.25, 0.5, 0.75]:
            c += translate([(boxlength*l)*scl, (1.2)*scl, -40*scl]).add(h)

        h = cube([(boxlength-300)*scl, (1.8)*scl, (50)*scl])
        c += translate([(140)*scl, (1.2)*scl, -80*scl]).add(h)

        c = translate([0*scl, (-1.2)*scl, 0*scl]).add(c)

        u += c

    # shift up a bit
    u = translate(v=[0*scl,0*scl,-lid_offset*scl]).add(u)

    return u

def screen_end(scl, ht, lcd_end_ht):

    ht = ht + lcd_end_ht
    print "SCREEN_END ht", ht
    u = union()
    b = screen_box(scl, ht, end=True)
    u += b

    # bolt-hole
    for end in [False]:
        c = chamfered_backbox_screwholes(scl, 60+ht, 25, lcdscrewrad)
        c = rotate([0, -90, 90]).add(c)
        #c = translate(v=[0, 0*scl, 0]).add(c)
        t = lid_bolthole(scl, end=end).add(c)
        u -= t

    screw_holes = [120.0, 790.0, lcd_w-120.0, lcd_w-790.0]
    if not test:
        # lcd screw holes
        for sht in screw_holes:
            c = chamfered_backbox_screwholes(scl, 60, 25, lcdscrewrad)
            c = rotate([0, -90, 90]).add(c)
            c = translate(v=[(sht+lcd_inset_top+35)*scl, 0*scl,
                       14*scl]).add(c)
            u -= c

    # indentation to fit screen front edge lockin
    d = cube([(32)*scl, (50)*scl, (39)*scl])
    c = translate(v=[24*scl, (ht-48)*scl, (-1)*scl]).add(d)
    u -= c

    # indentation
    c = cube([102*scl, 45*scl, 45*scl], center=True)
    c = rotate([45, 0, 0]).add(c)
    t = lid_bolthole(scl, end=False).add(c)
    t = translate(v=[10*scl,(ht-10)*scl,0*scl]).add(t)
    u -= t

    # lock-in to screen_hinge part
    d = cube([48*scl, 20*scl, 34*scl])
    c = translate(v=[(lcd_w+79)*scl, (ht-10)*scl,
                (hthick-3.6-14)*scl]).add(d)
    u += c

    # remove runner along top screen edge
    c = shearedcube([14*scl, (lcd_w)*scl, (14)*scl],
                shear=[14*scl, 0*scl, 0],
                innershear=[0*scl, 0*scl, 0])
    c = rotate([0, 0, -90]).add(c)
    t = translate(v=[(70)*scl, (ht+4)*scl,
                                (-27)*scl]).add(c)
    u -= t

    if pin_parts_3d:
        c = union()
        h = pin(B0, scl)
        h = translate([(boxlength-50)*scl, (3)*scl, -60*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(boxlength+16)*scl, (3)*scl, 3*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(boxlength-18)*scl, (3)*scl, 80*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(boxlength-95)*scl, (3)*scl, 80*scl]).add(h)
        c += h

        h = pin(B0, scl)
        h = translate([(47)*scl, (3)*scl, -59*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(-19)*scl, (3)*scl, 3*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(47)*scl, (3)*scl, 80*scl]).add(h)
        c += h

        if not test:
            # lcd screw holes
            for sht in screw_holes:
                h = pin(B0, scl)
                h = translate([(sht+80)*scl, (3)*scl, 88*scl]).add(h)
                c += h
                h = translate([0*scl, (0)*scl, -145*scl]).add(h)
                c += h
        else:
            h = pin(B0, scl)
            h = translate([(boxlength/2)*scl, (3)*scl, 60*scl]).add(h)
            c += h
            h = pin(B0, scl)
            h = translate([(boxlength/2)*scl, (3)*scl, -45*scl]).add(h)
            c += h


        c = translate([0, (-24.2)*scl, 0*scl]).add(c)
        u += c

    if cutdown:
        # cut down
        c = cube([(boxlength+500)*scl, (ht+100)*scl, 400*scl])
        c = translate([(-700)*scl, -30*scl, -150*scl]).add(c)
        u -= c

        if pin_parts_3d:
            c = union()
            h = pin(B0, scl)
            h = translate([(boxlength-225)*scl, (3)*scl, 30*scl]).add(h)
            c += h
            h = pin(B0, scl)
            h = translate([(boxlength-225)*scl, (3)*scl, -40*scl]).add(h)
            c += h
            c = translate([0, (-24.2)*scl, 0*scl]).add(c)
            u += c

    # shift up a bit
    u = translate(v=[0*scl,0*scl,-lid_offset*scl]).add(u)

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
    print "SCREEN_FRONT_EDGE ht", ht

    # main box
    b = screen_box(scl, ht-2, end=False, front=True)
    b = translate(v=[(0)*scl, (2)*scl, (0)*scl]).add(b)

    # remove interior
    c = touch_arc(0, ht-30, 45,
                        25, scl,
                  angle=0)
    c = rotate([-90, 0, 0]).add(c)
    c = rotate([0, -90, 0]).add(c)
    c = resize([(60)*scl, 0, 0], False).add(c)
    c = translate(v=[(76)*scl, (ht-15)*scl, (lcd_d-15)*scl]).add(c)
    b -= c

    fthick = 6
    offs = 15-hthick+fthick
    step = (ht-160-offs) / (8.0 if test else 20.0)
    count = 0
    print offs, step
    while offs < (ht-step):
        count += 1
        if count in [4, 5]:
            t = step+fthick # this is to act as support for a magnet holder
            if count == 4:
                mholdero = offs
                mholderw = t*2
        else:
            t = fthick
        c = touch_arc(0, t, 45,
                            25, scl,
                      angle=0)
        c = rotate([-90, 0, 0]).add(c)
        c = rotate([0, -90, 0]).add(c)
        c = resize([(60)*scl, 0, 0], False).add(c)
        c = translate(v=[(76)*scl, (offs+step-fthick)*scl, (lcd_d-15)*scl]).add(c)
        b += c

        offs += step

    print "magholder width", mholderw-fthick*4
    # add a hole for a magnet.  quite low down
    c = shearedcube([(65)*scl, 145*scl, 57*scl],
            shear=[2*scl, 20*scl, 0],
            innershear=[-2*scl, 0*scl, 0])
    c = rotate([0, 0, 90]).add(c)
    c = translate(v=[175*scl, (mholdero+35)*scl, (lcd_d-59)*scl]).add(c)
    b -= c

    # matching screen mid (front)
    d = shearedcube([(23)*scl, (28)*scl, (30)*scl],
            shear=[0, -0*scl, 0],
            innershear=[0, 0*scl, 0])
    c = translate(v=[30.5*scl, (ht-4)*scl, (3.5)*scl]).add(d)
    b += c
    d = rotate([0, 0, 180]).add(d)
    c = translate(v=[(28.5+23)*scl, (4)*scl, (3.5)*scl]).add(d)
    b += c

    if pin_parts_3d:
        c = union()
        
        if False: # XXX rely on repsnapper support
            # support magnet holder
            h = cube([65*scl, 6*scl, 45*scl])
            c += translate([(15)*scl, (mholdero+mholderw/2-20)*scl, 0*scl]).add(h)
            h = cube([6*scl, (mholderw-10)*scl, 45*scl])
            c += translate([(70)*scl, (mholdero-10)*scl, 0*scl]).add(h)

        # support hex bolt hole
        h = cube([6*scl, 25*scl, 30*scl])
        c += translate([(45.5)*scl, (-24)*scl, 17*scl]).add(h)
        c += translate([(28.5)*scl, (-24)*scl, 17*scl]).add(h)

        h = cube([6*scl, scrn_centre_ht/2*scl, 40*scl])
        h = translate([(47.5)*scl, (ht-4)*scl, 7.4*scl]).add(h)
        c += h
        h = translate([(-17)*scl, (0)*scl, 0*scl]).add(h)
        c += h

        h = pin(B0, scl)
        h = rotate([90, 0, 0]).add(h)
        c += translate([(30)*scl, (ht/2)*scl, (7.4+37)*scl]).add(h)
        c += translate([(30)*scl, (ht-4)*scl, (7.4+37)*scl]).add(h)
        c += translate([(30)*scl, (10)*scl, (7.4+37)*scl]).add(h)

        h = pin(B0, scl)
        h = rotate([90, 0, 0]).add(h)
        for l in [ht-45, ht/2, 45]:
            c += translate([(-17)*scl, l*scl, (7.4+37)*scl]).add(h)

        h = pin_t(mirror=False)
        h = rotate([90, 0, 0]).add(h)
        c += translate([(15)*scl, (-95)*scl, (7.4+37+3)*scl]).add(h)
        c += translate([(15)*scl, (ht-35)*scl, (7.4+37+3)*scl]).add(h)
        c += translate([(70)*scl, (-125)*scl, (7.4+37+3)*scl]).add(h)
        c += translate([(70)*scl, (ht-5)*scl, (7.4+37+3)*scl]).add(h)

        c = translate([0, 0, (8)*scl]).add(c)
        b += c

    # shift up a bit
    b = translate(v=[0*scl,0*scl,-lid_offset*scl]).add(b)

    return b

def screen_back_edge(scl, ht, cable_access=False):
    b = screen_box(scl, ht-2, end=False, back=True)
    b = translate(v=[(0)*scl, (2)*scl, (0)*scl]).add(b)

    # add cutin to screen_end
    d = screen_cutin(scl, ht, diam=35, length=83)
    d = translate(v=[0*scl,(-ht+3)*scl,0*scl]).add(d)
    b += d

    # TODO: this is going to need some underside supports
    # TODO: length of the cable run doesn't have to be this long
    fthick = 8
    offs = 80-hthick+fthick
    step = (ht-160-offs) / (8.0 if test else 20.0)
    while offs < (ht-step-10):
        c = touch_arc(0, step-fthick, 50,
                            25, scl,
                      angle=0)
        c = rotate([90, 0, 0]).add(c)
        c = rotate([0, -90, 0]).add(c)
        c = resize([(70)*scl, 0, 0], False).add(c)
        c = translate(v=[(lcd_w+140)*scl, (offs)*scl, (lcd_d-15)*scl]).add(c)
        b -= c
        c = cube([140*scl, (step-fthick)*scl, 45*scl])
        c = translate(v=[(lcd_w+41)*scl, (offs)*scl, (lcd_d-10-46)*scl]).add(c)
        b -= c
        offs += step
    v = union()
    v += hollowbox(scl, 100, (ht+2), 45,
                {T:50, L:40, R:30, F:1, D:18, B:1},
                curverads={ T|R: (35, 0)})
    c = cube([95*scl, (ht+2)*scl, 20*scl])
    v += translate(v=[0, 0, 23*scl]).add(c)
    b -= translate(v=[(lcd_w+20)*scl, (-1)*scl, (lcd_d-10-46)*scl]).add(v)

    # slot to fit a nut into
    c = cube([140*scl, 25*scl, 55*scl], center=True)
    c = translate(v=[(-75)*scl, (55)*scl, (0)*scl]).add(c)
    t = lid_bolthole(scl, end=False).add(c)
    b -= t
    c = cylinder(r=32.0*scl, h=25*scl, center=True, segments=6)
    c = rotate([0, 90, 90]).add(c)
    c = rotate([0, 30, 0]).add(c)
    t = lid_bolthole(scl, end=False).add(c)
    t = translate(v=[(0)*scl, (55)*scl, (0)*scl]).add(t)
    b -= t

    # cable access
    d = shearedcube([(46)*scl, ((320))*scl, (41)*scl],
            shear=[50*scl, -0*scl, 0],
            innershear=[0, 0*scl, 0])
    c = translate(v=[(lcd_w+35)*scl, (ht-630)*scl, (-15)*scl]).add(d)
    b -= c

    # matching screen mid (back)
    d = shearedcube([(26)*scl, ((28))*scl, (31)*scl],
            shear=[0, -0*scl, 0],
            innershear=[0, 0*scl, 0])
    c = translate(v=[(lcd_w+161)*scl, (ht-1)*scl, (-3)*scl]).add(d)
    b += c

    c = lcd_screen_removeparts(scl)
    b -= translate([0*scl, -180*scl, 16*scl]).add(c)

    if pin_parts_3d:
        c = union()

        if False: # XXX use repsnapper "support" instead
            h = union()
            h += cube([6*scl, 15*scl, 60*scl])
            l = []
            i = 137
            while i < ht:
                l.append(i)
                i += step * 1.5
            for l in [2, 70, ht-15] + l:
                # three supports under the lvds cable cutout move back
                if abs(l - (ht-470)) < 160:
                    offs = 20
                else:
                    offs = 0
                c += translate([(lcd_w+50+lcd_panel_offs+offs)*scl,
                        (l)*scl, -18*scl]).add(h)

            h = cube([6*scl, scrn_centre_ht/2*scl, 40*scl])
            h = translate([(lcd_w+181)*scl, (ht-4)*scl, 7.4*scl]).add(h)
            c += h
            h = translate([(-20)*scl, (0)*scl, 0*scl]).add(h)
            c += h

        v = union()
        h = pin_t(mirror=False, dep=209)
        h = rotate([0, 0, -90]).add(h)
        v += h
        h = pin_t(mirror=True, dep=180, ht=100)
        h = rotate([0, 0, -90]).add(h)

        v += translate([(0)*scl, (0)*scl, (-218)*scl]).add(h)

        c += translate([(lcd_w+220)*scl, (ht)*scl, (179)*scl]).add(v)
        c += translate([(lcd_w+220)*scl, (ht/2)*scl, (179)*scl]).add(v)
        c += translate([(lcd_w+220)*scl, (8)*scl, (179)*scl]).add(v)
        b += c

    # bolt-hole (remove afterwards due to complex pinning)
    c = cylinder(r=lcdscrewrad*scl, h=(100)*scl, center=True, segments=50)
    c = rotate([0, 90, 90]).add(c)
    t = lid_bolthole(scl, end=False).add(c)
    b -= t

    if cutdown:
        # cut down
        c = cube([(boxlength+500)*scl, (ht+100)*scl, 400*scl])
        c = translate([(-300)*scl, 350*scl, -150*scl]).add(c)
        b -= c

        if pin_parts_3d:
            h = pin_t(mirror=False, dep=15)
            h = rotate([90, 0, 0]).add(h)
            b += translate([(lcd_w+90)*scl, (359)*scl, (7.4+37+11)*scl]).add(h)
            b += translate([(lcd_w+200)*scl, (359)*scl, (7.4+37+11)*scl]).add(h)

    # shift up a bit
    b = translate(v=[0*scl,0*scl,-lid_offset*scl]).add(b)

    return b

def friction_hinge2(scl, ht):

    a = union()
    rad = 35

    c = cylinder(r=rad*scl,
                        h=(30)*scl, segments=50, center=True)
    c = rotate([180, 90, 90]).add(c)
    a += c

    c = cube([30*scl, 30*scl, 27*scl], center=True)
    c = translate([-35*scl, 0, 0]).add(c)
    a += c

    # hinge hole
    r = cylinder(r=(17)*scl, h=(ht*5+0.3)*scl, segments=50, center=True)
    r = rotate([180, 90, 90]).add(r)
    t = translate(v=[0, (-ht/2+16.5)*scl, 0*scl]).add(r)
    a -= t

    if pin_parts_3d:
        c = union()
        h = pin(B0, scl, fill=True)
        h = translate([(0)*scl, (12)*scl, 0*scl]).add(h)
        c += h
        h = pin(B0, scl, fill=True)
        h = translate([(-20)*scl, (12)*scl, 0*scl]).add(h)
        c += h
        a += c

    a = hinge_translate(scl).add(a)
    return a

def friction_hinge1(scl, ht):

    a = union()
    hht = 40
    rad = 36.5
    rad2 = rad+12

    # outer disc
    r = union()
    c = cylinder(r=(rad-2)*scl,
                        h=(hht)*scl, segments=50, center=True)
    c = rotate([180, 90, 90]).add(c)
    r += c
    c = cylinder(r1=(rad-2)*scl, r=(rad2-2)*scl,
                        h=(20)*scl, segments=50, center=True)
    c = rotate([180, 90, 90]).add(c)
    c = translate(v=[0, (6)*scl, 0]).add(c)
    r += c
    c = cylinder(r=(rad2+0.5)*scl,
                        h=(32)*scl, segments=50, center=True)
    c = rotate([180, 90, 90]).add(c)
    c = translate(v=[0, (-19.5)*scl, 0]).add(c)
    r += c
    c = cylinder(r=(rad2-6)*scl, r1=(rad2-9)*scl,
                        h=(25)*scl, segments=6, center=True)
    c = rotate([180, 90, 90]).add(c)
    c = translate(v=[0, (-29+2.5)*scl, 0]).add(c)
    r -= c

    t = hinge_translate(scl).add(r)
    t = translate(v=[0, (-ht/2+27.5-bwid)*scl, 0]).add(t)
    a += t

    # hinge hole
    r = cylinder(r=(screwrad)*scl, h=(ht*5+0.3)*scl, segments=50, center=True)
    r = rotate([180, 90, 90]).add(r)
    t = hinge_translate(scl).add(r)
    t = translate(v=[0, (-ht/2+16.5)*scl, 0]).add(t)
    a -= t

    # bolt  hole
    r = cylinder(r1=(26.5)*scl, r=(29)*scl, h=(24)*scl, segments=6, center=True)
    r = rotate([180, 90, 90]).add(r)
    r = rotate([0, -1.5, 0]).add(r)
    t = hinge_translate(scl).add(r)
    t = translate(v=[0, (-24/2-6)*scl, 0]).add(t)
    a -= t

    return a

def cable_exit_xform(c):
    c = translate(v=[0*scl,-20*scl,0*scl]).add(c)
    c = rotate([0, 90, 90]).add(c)
    c = rotate([0, 130, 0]).add(c)
    return c

def cable_protector(scl, ht):
    u = union()

    rad=20.0
    # add hinge
    c = cylinder(r=(rad+15)*scl, h=(ht)*scl, segments=50)
    c = rotate([0, 90, 90]).add(c)
    c = translate(v=[0*scl,0*scl,0]).add(c)
    u += c

    # exit hole support
    c = union()
    d = cube([(42)*scl, (50)*scl, (ht)*scl])
    u += cable_exit_xform(d)
    d = cube([(42)*scl, (30)*scl, (ht-10)*scl])
    d = translate(v=[1*scl,10*scl,-1*scl]).add(d)
    u -= cable_exit_xform(d)

    # hollow hinge out
    c = cylinder(r=(50/2.)*scl, r1=39*scl, h=(20)*scl, segments=50)
    c = rotate([0, 90, 90]).add(c)
    c = translate(v=[0*scl,-8*scl,0*scl]).add(c)
    u -= c

    # cable hole
    c = cylinder(r=22*scl,
                    h=(1000)*scl, center=True, segments=50)
    c = rotate([0, 90, 90]).add(c)
    u -= c

    # cable access
    c = cube([(45)*scl, (50)*scl, (ht+2)*scl])
    c = translate(v=[10*scl,-10*scl,-1*scl]).add(c)
    c = rotate([0, 90, 90]).add(c)
    c = rotate([0, -120, 0]).add(c)
    u -= c
    c = rotate([0, 70, 0]).add(c)
    #u -= c

    u = hinge_translate(scl).add(u)

    if pin_parts_3d:
        c = union()
        h = pin(B0, scl, fill=True)
        c += translate([(boxlength-30)*scl, (ht-3)*scl, 90*scl]).add(h)
        c += translate([(boxlength-30)*scl, (ht-3)*scl, 130*scl]).add(h)
        c += translate([(boxlength-80)*scl, (ht-3)*scl, 130*scl]).add(h)
        c += translate([(boxlength-80)*scl, (ht-3)*scl, 90*scl]).add(h)
        u += c

    return u

def screen_cutin(scl, ht, diam=45, length=99):
    # indentation - has to be done this way (recreate screen_box) so
    # that the profile of the indentation fits with screen_end curvature
    d = intersection()
    b = screen_box(scl, ht, end=False, back=True, hingewall=False)
    r = union()
    r += b
    d.add(r)
    c = cube([length*scl, diam*scl, diam*scl], center=True)
    c = rotate([45, 0, 0]).add(c)
    t = lid_bolthole(scl, end=False).add(c)
    t = translate(v=[10*scl,(ht)*scl,0*scl]).add(t)
    d.add(t)
   
    return d
    
def screen_hinge(scl, ht):
    print "SCREEN_HINGE ht", ht

    u = union()
    b = screen_box(scl, ht, end=False, back=True, hingewall=False)
    u += b

    rad=35.0
    # add hinge
    #u += t
    c = cylinder(r=(rad+15)*scl, h=(ht)*scl, segments=50)
    c = rotate([0, 90, 90]).add(c)
    c = translate(v=[0*scl,0*scl,0]).add(c)
    t = hinge_translate(scl).add(c)
    t = translate(v=[0*scl,0*scl,lid_offset*scl]).add(t)
    u += t

    w = lcd_w+lcd_inset_top+lcd_inset_bot
    c = shearedcube([(87)*scl, ht*scl, (hinge_offs-18+lid_offset)*scl],
                shear=[41*scl, 0, 0],
                innershear=[0*scl, 0, 0])
    c = rotate([0, 0, 180]).add(c)
    c = rotate([180, 0, 0]).add(c)
    c = translate(v=[(w)*scl,0*scl,(30+hinge_offs+lid_offset)*scl]).add(c)
    u += c

    # add cutin to screen_end
    d = screen_cutin(scl, ht)
    d = translate(v=[0*scl,(-ht+3)*scl,0*scl]).add(d)
    u += d

    # add cutout to screen_edge
    c = cube([128*scl, 35*scl, 35*scl], center=True)
    c = rotate([45, 0, 0]).add(c)
    t = lid_bolthole(scl, end=False).add(c)
    t = translate(v=[25*scl,(ht)*scl,0*scl]).add(t)
    u -= t

    # hex indentation
    c = cylinder(r=27*scl, r1=26*scl, h=(30)*scl, center=True, segments=6)
    c = rotate([0, 90, 90]).add(c)
    c = rotate([0, 30, 0]).add(c)
    t = lid_bolthole(scl, end=False).add(c)
    t = translate(v=[0*scl,-5*scl,0*scl]).add(t)
    #u += t

    # bolt-hole
    c = cylinder(r=lcdscrewrad*scl, h=(ht+81)*scl, center=True, segments=50)
    c = rotate([0, 90, 90]).add(c)
    t = lid_bolthole(scl, end=False).add(c)
    u -= t

    # cable cutout
    c = cube([(40)*scl, (ht*2)*scl, (30+hinge_offs)*scl])
    c = rotate([0, 0, 180]).add(c)
    c = rotate([180, 0, 0]).add(c)
    c = rotate([0, 31, 0]).add(c)
    c = translate(v=[(w-rad-4)*scl,-(ht+hthick)*scl,
                     (2+hinge_offs+lid_offset)*scl]).add(c)
    u -= c
    # put a bit back
    c = cube([(42)*scl, (14)*scl, (51)*scl])
    c = rotate([0, 0, 180]).add(c)
    c = rotate([180, 0, 0]).add(c)
    c = rotate([0, 31, 0]).add(c)
    c = translate(v=[(w-rad-3)*scl,(ht-26)*scl,
                     (2+hinge_offs+lid_offset)*scl]).add(c)
    u += c

    c = cube([(80)*scl, (ht+30)*scl, (lcd_d-hthick-3)*scl])
    u -= translate(v=[(w-170)*scl,-(20)*scl, (-5)*scl]).add(c)
    c = shearedcube([(80)*scl, (ht+30)*scl, (lcd_d-hthick-3)*scl],
                shear=[0*scl, 0*scl, 0],
                innershear=[0*scl, 30*scl, 0])
    c = rotate([0, 0, 180]).add(c)
    u -= translate(v=[(w-90)*scl,(ht*2)*scl, (-8+hthick)*scl]).add(c)

    # hollow hinge out
    c = cylinder(r=(64/2.)*scl, h=(ht+15)*scl, segments=50)
    c = rotate([0, 90, 90]).add(c)
    c = translate(v=[0*scl,-30*scl,0*scl]).add(c)
    t = hinge_translate(scl).add(c)
    t = translate(v=[0*scl,0*scl,lid_offset*scl]).add(t)
    u -= t

    # rim round hinge, fits with base_end
    c = cylinder(r=(59.9/2.)*scl, r1=(84/2.)*scl, h=(15)*scl, segments=50)
    c = rotate([0, 90, 90]).add(c)
    c = translate(v=[0*scl,-1*scl,0*scl]).add(c)
    t = hinge_translate(scl).add(c)
    t = translate(v=[0*scl,0*scl,lid_offset*scl]).add(t)
    u -= t

    # shift hinge end up a bit
    u = translate(v=[0*scl,0*scl,-lid_offset*scl]).add(u)

    # bolt  hole
    c = cylinder(r=15*scl,
                    h=(1000)*scl, center=True, segments=50)
    c = rotate([0, 90, 90]).add(c)
    t = hinge_translate(scl).add(c)
    u -= t

    if pin_parts_3d:
        c = union()
        h = pin(B0, scl, fill=True)
        c += translate([(boxlength-64)*scl, (ht-3)*scl, -74*scl]).add(h)
        c += translate([(boxlength-152)*scl, (ht-3)*scl, -66*scl]).add(h)
        c += translate([(boxlength+7)*scl, (ht-3)*scl, 0*scl]).add(h)
        c += translate([(boxlength-30)*scl, (ht-3)*scl, 165*scl]).add(h)
        c += translate([(boxlength-80)*scl, (ht-3)*scl, 165*scl]).add(h)
        c += translate([(boxlength-110)*scl, (ht-3)*scl, 83.9*scl]).add(h)
        c += translate([(boxlength-165)*scl, (ht-3)*scl, 83.9*scl]).add(h)
        c += translate([(boxlength+20)*scl, (ht-3)*scl,
                        (88-lid_offset)*scl]).add(h)
        u += c

    # XXX bugs so cut off the end
    c = cube([(400)*scl, (100)*scl, 500*scl])
    c = translate([(boxlength-250)*scl, ht*scl, -150*scl]).add(c)
    u -= c

    return u

def indented_screwhole(scl, u, x, y, z, rot=0, depth=16, base_screwholes=True):
    d = cylinder(r=topscrewrad*1.2*scl, r1=28*scl,
                    h=17*scl,
                    segments=50, center=True)
    d = rotate([90, 0, 0]).add(d)
    s = translate(v=[(0)*scl, (-9)*scl, (0)*scl]).add(d)
    s = rotate([0, 0, rot]).add(s)
    s = translate(v=[(x)*scl, (y)*scl, (z)*scl]).add(s)
    u += s
    if not base_screwholes:
        return u
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
    w = lcd_w-kbd_w-back_top_width+12
    l = ht-tpanel_b_w/2+hthick
    if woffs < 0:
        h = 40
        d = 30
        doff = 5
    else:
        h = boxheight - hthick - pcbthick - 3
        d = 30
        doff = 5

    b = hollowbox(scl, d, l-2, h,
                {T:-1, L:-1, R:d, F:hthick, D:-1, B:hthick*2},
                curverads={ T|R: (hthick, 0)})
    b = translate(v=[(w-25+woffs-doff)*scl, 1*scl, (0)*scl]).add(b)
    u += b

    if woffs < 0:
        b = hollowbox(scl, 25-woffs, hoffs+7, h,
                    {T:hthick, L:20, R:15, F:hthick, D:-1, B:hthick*2},
                    curverads={ T|R: (hthick, 0), T|B: (hthick, 0),
                                B|R: (hthick, 0)}) # XXX argh need better box!
        b = translate(v=[(w-25+woffs)*scl, (l-8-hoffs)*scl, (0)*scl]).add(b)
        u += b
        # XXX blergh cut off corner using arc...
        c = touch_arc(60, 60, 20,
                            30, scl, roffsinner=0,
                      angle=0)
        c = rotate([0, 0, 90]).add(c)
        c = translate(v=[(w-30)*scl, (l-8-hoffs+30)*scl, (50)*scl]).add(c)
        u -= c

    # floor L-piece, stabilise and allow sticking to PCB
    if woffs < 0:
        b = cube([(36)*scl, (l)*scl, (hthick)*scl])
        b = translate(v=[(w-1+woffs)*scl, 0*scl, (h-hthick)*scl]).add(b)
        b = translate(v=[(-49)*scl, 0*scl, (0)*scl]).add(b)
    else:
        b = union()
        d = cube([(62)*scl, (l-6-400)*scl, (18)*scl])
        d = translate(v=[(0)*scl, (400)*scl, 0*scl]).add(d)
        b += d
        d = cube([(42)*scl, (410)*scl, (18)*scl])
        d = translate(v=[(20)*scl, (3)*scl, 0*scl]).add(d)
        b += d
        b = translate(v=[(w-1+woffs-40)*scl, (3)*scl, (h-18)*scl]).add(b)
    u += b
    if woffs < 0:
        b = cube([(60)*scl, (l-41)*scl, (40-hthick-3)*scl])
        b = translate(v=[(w-1+woffs-80)*scl, 40*scl, (h-40+hthick+3)*scl]).add(b)
        u += b

    # screw holes in top for base_end
    d = cylinder(r=topscrewrad*scl,
                    h=(55)*scl,
                    segments=50, center=True)

    if woffs >= 0:
        b = cube([(50)*scl, (100)*scl, (40-hthick)*scl])
        b = translate(v=[(w-1+woffs-52)*scl, -55*scl, (h-40+hthick)*scl]).add(b)
        u += b
        b = translate(v=[(w-1+woffs-28)*scl, -28*scl, (h-31+hthick)*scl]).add(d)
        u -= b
    else:
        b = cube([(53)*scl, (100)*scl, (39-hthick-2)*scl])
        b = translate(v=[(w-1+woffs-52)*scl, -55*scl, (h-39+hthick+2)*scl]).add(b)
        u += b
        b = translate(v=[(w-1+woffs-28)*scl, -28*scl, (h-31+hthick+2)*scl]).add(d)
        u -= b

    # extra bit for kbd corner support
    b = hollowbox(scl, hthick, 20+hthick, h,
                {T:-1, L:-1, R:-1, F:20+hthick, D:-1, B:-1},
                curverads={ T|F: (hthick, 0)})
    b = translate(v=[(w-hthick+woffs)*scl, (0)*scl, (0)*scl]).add(b)
    u += b
    if woffs >= 0:
        b = cube([(hthick+52)*scl, (hthick+3)*scl, (66)*scl])
    else:
        b = cube([(hthick+52)*scl, (hthick+3)*scl, (16)*scl])
    b = translate(v=[(w-hthick-41+woffs)*scl, -1*scl, (-1)*scl]).add(b)
    u -= b

    if woffs < 0:
        cutht = hthick
        shr = cutht
        doff = 4
        wo = 18
    else:
        cutht = 21
        shr = 0
        doff = -2
        wo = 0
    # cutouts for bamboo panel
    b = shearedcube([(25)*scl, (2+l)*scl, cutht*scl],
            shear=[shr*scl, 0*scl, 0],
            innershear=[-shr*scl, 0*scl, 0])
    b = translate(v=[(w-25-hthick+woffs-wo)*scl,
                        (hthick)*scl, (-1+doff)*scl]).add(b)
    u -= b

    # screw holes in top for touchpanel
    d = cylinder(r=topscrewrad*scl,
                    h=(55)*scl,
                    segments=50, center=True)

    # keyboard tray indents
    b = kbd_tray_indent(scl)
    if woffs >= 0:
        t = translate(v=[(w-26)*scl, (l-132)*scl, (16)*scl]).add(b)
        u -= t
        t = translate(v=[(w-26)*scl, (134)*scl, (16)*scl]).add(b)
        u -= t
    else:
        t = translate(v=[(w-19+woffs)*scl, (l-312-hoffs)*scl, (16)*scl]).add(b)
        u -= t
        t = translate(v=[(w-19+woffs)*scl, (123)*scl, (16)*scl]).add(b)
        u -= t

    if woffs >= 0:
        # lock-in to tpanel
        b = cube([(95)*scl, (30)*scl, (h-40)*scl])
        b = translate(v=[(w-70)*scl, (l-31)*scl, (40)*scl]).add(b)
        u += b
        b = cube([(79)*scl, (112)*scl, (h-71)*scl])
        b = translate(v=[(w-100)*scl, (l-50)*scl, (71)*scl]).add(b)
        u += b
        b = cube([(46)*scl, (92)*scl, (40)*scl])
        b = translate(v=[(w-100)*scl, (l-30)*scl, (51)*scl]).add(b)
        u += b

        t = translate(v=[(w-75)*scl, (l+40)*scl, (50)*scl]).add(d)
        u -= t
    else:
        b = cube([(100)*scl, (66)*scl, (18)*scl])
        b = translate(v=[(w-129)*scl, (l-1)*scl, (22)*scl]).add(b)
        u += b

        t = translate(v=[(w-75)*scl, (l+40)*scl, (19)*scl]).add(d)
        u -= t

    if woffs < 0:
        boffs = pcb3_lock_offs-40
        # ... cutout for the actual support, the rest was housing for the cutout
        c = cube([75*scl, 36*scl, (boxheight-47)*scl])
        c = translate(v=[-22*scl, (9-54)*scl, (-3)*scl]).add(c)
        c = translate(v=[(w-hoffs)*scl, (boffs)*scl, (0)*scl]).add(c)
        u -= c

    if pin_parts_3d:
        if woffs >= 0:
            c = union()
            h = pin_t(mirror=False, dep=boxheight-30)
            h = rotate([0, 90, 0]).add(h)
            c += translate([(w+50)*scl, (0)*scl, -14*scl]).add(h)

            h = pin_t(mirror=False, dep=29)
            h = rotate([0, 90, 0]).add(h)
            c += translate([(w+35)*scl, (0)*scl, 55*scl]).add(h)

            h = pin_t(mirror=False, dep=43)
            h = rotate([0, 90, 0]).add(h)
            c += translate([(w-31)*scl, (0)*scl, -(l+56)*scl]).add(h)

            h = pin_t(mirror=False, pht=72, dep=boxheight-30, half=True)
            h = rotate([0, 90, 0]).add(h)
            c += translate([(w+50)*scl, (0)*scl, (-l+7)*scl]).add(h)

            h = pin(B0, scl)
            h = translate([(w+31)*scl, (-3)*scl, 30*scl]).add(h)
            c += h

            h = pin(B0, scl)
            h = translate([(w-70)*scl, (-3)*scl, (-l+62)*scl]).add(h)
            c += h

            c = rotate([90, 0, 0]).add(c)
            c = translate([0*scl, (0)*scl,
                           (boxheight-hthick-pcbthick-2)*scl]).add(c)

            u += c
        else:
            c = union()
            h = pin_t(mirror=False, dep=25)
            c += translate([(w-86)*scl, (0)*scl, 85*scl]).add(h)

            h = pin_t(mirror=False, dep=18)
            c += translate([(w-49)*scl, (0)*scl, (-l)*scl]).add(h)
            h = pin_t(mirror=False, dep=25)
            h = rotate([0, 90, 0]).add(h)
            c += translate([(w-89)*scl, (0)*scl, (-l+66)*scl]).add(h)
            h = pin_t(mirror=False, dep=40, half=True, pht=70)
            h = rotate([0, 90, 0]).add(h)
            c += translate([(w+50)*scl, (0)*scl, (-l+166)*scl]).add(h)
            h = pin_t(mirror=False, dep=40, half=True, pht=270)
            c += translate([(w-40)*scl, (0)*scl, (-l+266)*scl]).add(h)

            h = pin(B0, scl)
            c += translate([(w-46)*scl, (-3)*scl, (-150)*scl]).add(h)
            c += translate([(w-46)*scl, (-3)*scl, (-200)*scl]).add(h)
            c += translate([(w-46)*scl, (-3)*scl, (-l+470)*scl]).add(h)
            c += translate([(w-46)*scl, (-3)*scl, (-l+440)*scl]).add(h)

            if False: # XXX don't need these (use support)
                v = cube([12*scl, 30*scl, 6*scl])
                h = translate([(w-12+woffs)*scl, (-30)*scl, (-l+470)*scl]).add(v)
                c += h
                h = translate([(w-12+woffs)*scl, (-30)*scl,
                                            (-l+440)*scl]).add(v)
                c += h
                h = translate([(w-12+woffs)*scl, (-30)*scl, (-160)*scl]).add(v)
                c += h
                h = translate([(w-12+woffs)*scl, (-30)*scl, (-200)*scl]).add(v)
                c += h

            c = rotate([90, 0, 0]).add(c)
            c = translate([0*scl, (0)*scl,
                           (40)*scl]).add(c)

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

    b = cube([25.1*scl, 70*scl, (boxheight-hthick-22)*scl])
    b = translate(v=[(-3.1)*scl, 0*scl, (21)*scl]).add(b)
    u += b

    t = shearedcube([(boxheight-hthick*2-26)*scl, (71)*scl, (25)*scl],
            shear=[8*scl, 0*scl, 0],
            innershear=[-8*scl, 0*scl, 0])
    t = rotate([0, 90, 0]).add(t)
    b = translate(v=[(-28)*scl, (-1)*scl, (boxheight-21)*scl]).add(t)
    u += b

    v = union()
    u = translate(v=[(180)*scl, 0, (55)*scl]).add(u)
    v.add(u)
    return v

def back_kbd_runner(scl, ht, toffs, mirrored=False):

    u = union()
    w = boxlength-back_top_width
    l = boxheight-hthick-3

    b = hollowbox(scl, 13, ht-2+12, l,
                {T:14, L:8, R:-1, F:30, D:12, B:10},
                curverads={ T|L: (hthick, 0)})
    b = translate(v=[(w-15)*scl, 1*scl, (0)*scl]).add(b)
    u += b
    c = cube([(31)*scl, (30)*scl, (boxheight*2)*scl])
    b = translate(v=[(w-21)*scl, (ht-2)*scl, (55)*scl]).add(c)
    u -= b
    c = shearedcube([(4.0)*scl, (ht-50)*scl, (13)*scl],
                    shear=[0*scl, 0, 0],
                    innershear=[-12*scl, 0, 0])
    c = rotate([0, 90, 0]).add(c)
    b = translate(v=[(w-27)*scl, (25)*scl, (42.0)*scl]).add(c)
    u += b
    c = shearedcube([(13)*scl, (17)*scl, (14)*scl],
                    shear=[0, -12*scl, 0, 0],
                    innershear=[0, 0*scl, 0])
    #c = rotate([0, 0, 180]).add(c)
    c = rotate([90, 0, 0]).add(c)
    b = translate(v=[(w-15)*scl, (3)*scl, (38)*scl]).add(c)
    u += b
    c = rotate([0, 0, 180]).add(c)
    b = translate(v=[(w-2)*scl, (ht-3)*scl, (55)*scl]).add(c)
    u += b
    c = shearedcube([(14.0)*scl, (ht-2)*scl, (13)*scl],
                    shear=[0*scl, 0, 0],
                    innershear=[12*scl, 0, 0])
    c = rotate([0, 90, 0]).add(c)
    b = translate(v=[(w-15)*scl, (1)*scl, (26.0)*scl]).add(c)
    u += b

    offs = ht + toffs - tpanel_l_b/2
    if not mirrored:
        offs += 110

    if not mirrored:
        locks = [140, ht-658+175]
    else:
        locks = [130, ht-899+75]

    # add interlocks for base panel
    d = union()
    d += shearedcube([(25)*scl, (50)*scl, (12)*scl],
                    shear=[0, 20*scl, 0],
                    innershear=[0, 0*scl, 0, 0])
    b = cube([(25)*scl, (70)*scl, (3.1)*scl])
    d += translate(v=[(0)*scl, (0)*scl, (11.9)*scl]).add(b)
    d = rotate([0, 0, 180]).add(d)
    u += translate(v=[(w-10)*scl, (130)*scl, (l-15)*scl]).add(d)
    u += translate(v=[(w-10)*scl, (ht/2)*scl, (l-15)*scl]).add(d)
    u += translate(v=[(w-10)*scl, (ht-30)*scl, (l-15)*scl]).add(d)

    # add set of interlocks into back_base to hold it down
    c = union()
    d = cube([(15)*scl, (16)*scl, (l-22)*scl])
    c += d
    d = shearedcube([(l-14)*scl, (16)*scl, (22)*scl],
                    shear=[0*scl, 0, 0],
                    innershear=[0*scl, 0, 0])
    d = rotate([0, 90, 0]).add(d)
    d = rotate([0, 0, 180]).add(d)
    d = translate(v=[(31)*scl, (16)*scl, (l-14)*scl]).add(d)
    c += d
    supports = [ht-162, ht*0.35, 305, ht*0.55, offs+35, offs+119]
    #for s in locks:
    #   supports.append(s+35)
    for h in supports:
        b = translate(v=[(w-12)*scl, h*scl, (hthick+2)*scl]).add(c)
        u += b

    # add series of keyboard locks
    c = union()
    b = shearedcube([(19.5)*scl, (70)*scl, (10)*scl],
                    shear=[-9*scl, 0, 0],
                    innershear=[10*scl, 0, 0])
    b = rotate([0, -90, 0]).add(b)
    c.add(b)

    for h in locks:
        b = translate(v=[(w-12)*scl, (h+5)*scl, (11)*scl]).add(c)
        u += b

    # remove bit for pcb1/battery support
    c = cube([(13)*scl, (86)*scl, (boxheight-31)*scl])
    b = translate(v=[(w-15)*scl, (offs+42)*scl, (10+2)*scl]).add(c)
    u += b
    #c = cube([(28)*scl, (86)*scl, (boxheight-105)*scl])
    #b = translate(v=[(w-20)*scl, (offs+42)*scl, (10+4)*scl]).add(c)
    #u += b
    c = cube([(90)*scl, (36)*scl, (l-23)*scl])
    b = translate(v=[(w-50)*scl, (offs+68)*scl, (50+1)*scl]).add(c)
    u -= b
    c = cube([(30)*scl, (36)*scl, (l-23)*scl])
    b = translate(v=[(w-45)*scl, (offs+68)*scl, (35+1)*scl]).add(c)
    u -= b

    if pin_parts_3d:
        c = union()
        h = pin(B0, scl)
        h = translate([(ht-40)*scl, (-3)*scl, 33*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(ht/2)*scl, (-3)*scl, 33*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(ht/2-70)*scl, (-3)*scl, 33*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(ht*0.25+30)*scl, (-3)*scl, 33*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(ht*0.25-40)*scl, (-3)*scl, 33*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(ht*0.8)*scl, (-3)*scl, 33*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(ht*0.8+70)*scl, (-3)*scl, 33*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(ht+32)*scl, (-3)*scl, 33*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(40)*scl, (-3)*scl, 33*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(-32)*scl, (-3)*scl, 33*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(offs+86)*scl, (-3)*scl, 33*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(offs-66+86)*scl, (-3)*scl, 33*scl]).add(h)
        c += h
        h = pin(B0, scl)
        h = translate([(offs+66+86)*scl, (-3)*scl, 33*scl]).add(h)
        c += h
        c = rotate([90, 0, 0]).add(c)
        c = rotate([0, 0, 90]).add(c)

        c = translate([(w-10)*scl, (0)*scl, (l)*scl]).add(c)
        u += c
        c = translate([(-70)*scl, (0)*scl, 0*scl]).add(c)
        u += c

        h = cube([(76)*scl, (6)*scl, (l)*scl])
        b = translate(v=[(w-80)*scl, (offs+62)*scl, (0)*scl]).add(h)
        u += b
        b = translate(v=[(w-80)*scl, (ht-6)*scl, (0)*scl]).add(h)
        u += b
        b = translate(v=[(w-80)*scl, (0)*scl, (0)*scl]).add(h)
        u += b
        b = translate(v=[(w-20)*scl, (0)*scl, (0)*scl]).add(h)
        u += b
        b = translate(v=[(w-20)*scl, (ht-6)*scl, (0)*scl]).add(h)
        u += b

    v = union()
    u = translate(v=[0, 0, (55)*scl]).add(u)
    v.add(u)
    return v


def compartment_lockin_capture(scl, ht, tpanel_offset, kbd_offs):

    u = union()

    w = tpanel_l_b-180-20

    offs = tpanel_l_b/2
    v = union()
    c = cube([145*scl, 155*scl, (boxheight-78)*scl], center=True)
    v += translate(v=[0, 5*scl, (65)*scl]).add(c)
    c = cube([112*scl, 55*scl, (60)*scl], center=True)
    v -= translate(v=[0*scl, 36*scl, (66)*scl]).add(c)
    c = cube([147*scl, 74*scl, (boxheight-78)*scl], center=True)
    v -= translate(v=[0*scl, -56*scl, (46)*scl]).add(c)
    c = cylinder(r=56.*scl, h=(140)*scl, segments=50, center=True)
    v -= translate(v=[0, 0*scl, (boxheight-46)*scl]).add(c)
    c = cube([27*scl, 22*scl, 34*scl], center=True)
    v += translate(v=[59*scl, -8*scl, (boxheight-75)*scl]).add(c)
    v += translate(v=[-59*scl, -8*scl, (boxheight-75)*scl]).add(c)

    c = translate(v=[(offs-180+50)*scl, (ht-5)*scl, (20)*scl]).add(v)
    u += c

    v = union()
    u = translate(v=[180*scl, 0, (55)*scl]).add(u)
    v.add(u)

    if pin_parts_3d:
        c = union()
        h = pin(B0, scl)
        h = rotate([0,90,0]).add(h)
        c += translate([(offs-40)*scl, (90)*scl, -(ht-100)*scl]).add(h)
        c += translate([(offs+140)*scl, (90)*scl, -(ht-100)*scl]).add(h)
        c += translate([(offs-40)*scl, (90)*scl, -(ht+80)*scl]).add(h)
        c += translate([(offs+140)*scl, (90)*scl, -(ht+80)*scl]).add(h)

        c = translate([(0)*scl, (55-5+20)*scl, 0*scl]).add(c)
        c = rotate([90,0,0]).add(c)
        v += c

    return v

def compartment_lockin(scl, ht, tpanel_offset, kbd_offs):

    u = union()

    w = tpanel_l_b-180-20

    offs = tpanel_l_b/2
    v = union()
    c = cylinder(r=25.*scl, h=(boxheight-25)*scl, segments=50, center=True)
    v += translate(v=[0, 0*scl, (29.5)*scl]).add(c)
    c = cylinder(r=40.*scl, h=(18)*scl, segments=50, center=True)
    v += translate(v=[0, 0*scl, (1)*scl]).add(c)
    c = cylinder(r=25.*scl, r1=40.*scl, h=(19)*scl, segments=50, center=True)
    v += translate(v=[0, 0*scl, (18.9)*scl]).add(c)
    c = cylinder(r=52.*scl, h=(20)*scl, segments=50, center=True)
    v += translate(v=[0, 0*scl, (boxheight-46)*scl]).add(c)
    c = cube([15*scl, 90*scl, 20*scl], center=True)
    v -= translate(v=[0, 0*scl, (-13)*scl]).add(c)
    c = cube([90*scl, 40*scl, 105*scl], center=True)
    v -= translate(v=[0, -40*scl, (-11)*scl]).add(c)

    v = rotate([0,0,45]).add(v)
    v = rotate([0,0,45]).add(v)
    c = translate(v=[(offs-180+50)*scl, (ht-5)*scl, (20)*scl]).add(v)
    u += c

    v = union()
    u = translate(v=[180*scl, 0, (55)*scl]).add(u)
    v.add(u)

    if pin_parts_3d:
        c = union()
        h = pin_t(ht=185, dep=108)
        h = rotate([0,90,0]).add(h)
        c += translate([(offs+14.9)*scl, (91)*scl, -(ht-8)*scl]).add(h)
        h = pin_t(ht=180.8, dep=108)
        c += translate([(offs+47)*scl, (91)*scl, -(ht+25.9)*scl]).add(h)

        c = translate([(0)*scl, (55-3+20)*scl, 0*scl]).add(c)
        c = rotate([90,0,0]).add(c)
        v += c

    return v


def compartment_lid(scl, ht, tpanel_offset, kbd_offs):

    u = union()

    w = tpanel_l_b-180-15

    indent = 50
    # main panel, create staggered part for bamboo panel fill-in
    b = cube([(w-8)*scl, (ht-8)*scl, (15)*scl])
    b = translate(v=[4*scl, 4*scl, (0)*scl]).add(b)
    u += b

    # compartment lockin
    offs = tpanel_l_b/2
    b = shearedcube([(150)*scl, (52)*scl, (50)*scl],
                shear=[0*scl, -5*scl, 0],
                innershear=[0, 0*scl, 0])
    c = translate(v=[(offs-180-25)*scl, (ht-55)*scl, (0)*scl]).add(b)
    u += c
    b = cube([(120)*scl, (40)*scl, (90)*scl])
    c = translate(v=[(offs-180-10)*scl, (ht-34)*scl, (-1)*scl]).add(b)
    u -= c
    b = shearedcube([(50)*scl, (80)*scl, (28)*scl],
                shear=[0*scl, -10*scl, 0],
                innershear=[30*scl, 10*scl, 0])
    b = rotate([90,90,0]).add(b)
    c = translate(v=[(offs-180+10)*scl, (ht-20)*scl, (59)*scl]).add(b)
    u -= c

    b = cube([(w-indent*2)*scl, (ht-indent*2)*scl, (5)*scl])
    b = translate(v=[indent*scl, indent*scl, (-1)*scl]).add(b)
    u -= b

    b = shearedcube([(w-indent*2)*scl, (ht-indent*2)*scl, (15)*scl],
                shear=[-15*scl, -15*scl, 0],
                innershear=[15*scl, 15*scl, 0])
    b = translate(v=[indent*scl, indent*scl, (3)*scl]).add(b)
    u -= b

    # add a runner, fits into base_front_top
    c = shearedcube([2*scl, (w-260)*scl, (15)*scl],
                shear=[0*scl, 0*scl, 0],
                innershear=[-14*scl, 0*scl, 0])
    c = rotate([0,0,90]).add(c)
    c = translate(v=[(w-130)*scl, 4*scl,
                                (0)*scl]).add(c)
    u += c

    # cut out corner for tpanel_mid joiner
    b = cube([60*scl, 30*scl, (15)*scl])
    b = rotate([-22,0,0]).add(b)
    b = translate(v=[-11*scl, (ht-27)*scl, (20)*scl]).add(b)
    u -= b

    v = union()
    u = translate(v=[180*scl, 0, (55)*scl]).add(u)
    v.add(u)

    if pin_parts_3d:
        c = union()
        h = pin(B0, scl)
        c += translate([(-20)*scl, (0)*scl, 20*scl]).add(h)
        c += translate([(0)*scl, (0)*scl, (-ht-42)*scl]).add(h)
        c += translate([(-41.7)*scl, (0)*scl, (-ht+47)*scl]).add(h)
        c += translate([(w+26)*scl, (0)*scl, 13*scl]).add(h)
        c += translate([(w+35)*scl, (0)*scl, -76*scl]).add(h)
        c += translate([(w+26)*scl, (0)*scl, (-ht+1)*scl]).add(h)
        c += translate([(w+35)*scl, (0)*scl, (-ht+90)*scl]).add(h)

        c = translate([(180)*scl, (55-1.2)*scl, 0*scl]).add(c)
        c = rotate([90,0,0]).add(c)
        v += c

    if False: # test single clip hole
        b = cube([(w-6+30)*scl, (ht+200)*scl, (40)*scl])
        b = translate(v=[82*scl, -100*scl, (45)*scl]).add(b)
        v -= b

        b = cube([(w-6+300)*scl, (ht)*scl, (40)*scl])
        b = translate(v=[82*scl, -200*scl, (45)*scl]).add(b)
        v -= b

    return v


def pcb2(scl):

    t = union()

    # PCB
    pcb = union()
    b = cube([870*scl, 640*scl, (12)*scl])
    pcb += b
    b = cube([981*scl, 500*scl, (30)*scl])
    b = translate([(190)*scl, 400*scl, -10*scl]).add(b)
    pcb -= b

    # touchpanel connector
    j = cube([90*scl, 60*scl, (12)*scl])
    r = translate([(50)*scl, 590*scl,
                (-12)*scl]).add(j)
    t.add(r)

    # lcd connector
    j = cube([40*scl, 140*scl, (12)*scl])
    r = translate([(260)*scl, (150)*scl,
                (-12)*scl]).add(j)
    t.add(r)

    # keyboard connector
    j = cube([330*scl, 70*scl, (12)*scl])
    r = translate([(480)*scl, (290)*scl,
                (-12)*scl]).add(j)
    t.add(r)

    # STM32F0
    j = cube([100*scl, 100*scl, (12)*scl])
    r = translate([(470)*scl, (90)*scl,
                (-12)*scl]).add(j)
    t.add(r)

    # SIP-8 1
    j = cube([20*scl, 100*scl, (30)*scl])
    r = translate([(370)*scl, (50)*scl,
                (12)*scl]).add(j)
    t.add(r)
    # SIP-8 2
    j = cube([20*scl, 100*scl, (30)*scl])
    r = translate([(370)*scl, (250)*scl,
                (12)*scl]).add(j)
    t.add(r)

    t.add(pcb)

    t = translate([(tpanel_l_b-360-90)*scl, (lcd_l/2-480)*scl,
                    (52+55)*scl]).add(t)
    return t

def pcb3(scl):

    c = cube([327.66*scl, 849.63*scl, (pcbthick)*scl])
    c = translate(v=[(front_top_width+25)*scl, 0, (55+26)*scl]).add(c)
    return c


def pcb1(scl):
    """ TODO: extend PCB1 by 5mm, move all USB ports up.
    """

    t = union()

    # PCB
    pcb = union()
    b = cube([1630*scl, 1255*scl, (pcbthick)*scl])
    pcb += b
    b = cube([521*scl, 1200*scl, (30)*scl])
    b = translate([(-1)*scl, 245*scl, -10*scl]).add(b)
    pcb -= b
    # extra small cutout to fit pcb1_support at corner
    b = cube([80*scl, 280*scl, (30)*scl])
    b = translate([(510)*scl, (1090)*scl, -10*scl]).add(b)
    pcb -= b
    b = cube([835*scl, (101)*scl, 30*scl])
    b = translate(v=[(470)*scl, (-1)*scl, (-10)*scl]).add(b)
    pcb -= b
    # cutout around USB connector
    b = cube([483*scl, 25*scl, (30)*scl])
    b = translate([(-1)*scl, (-1)*scl, -10*scl]).add(b)
    pcb -= b

    r = translate([(0)*scl, 15*scl, 0]).add(pcb)
    t.add(r)

    s = union()
    b = cube([710*scl, 986*scl, (58)*scl])
    s += b
    b = cube([540*scl, 861*scl, (60)*scl])
    b = translate([(110)*scl, -1*scl,
                (-1)*scl]).add(b)
    s -= b
    b = cube([900*scl, 100*scl, (60)*scl])
    b = translate([(55)*scl, -1*scl,
                (-1)*scl]).add(b)
    s -= b

    cpu_offs = 590
    r = translate([(cpu_offs)*scl, 0*scl,
                (-58)*scl]).add(s)
    t.add(r)

    # EOMA68 CPU Card
    card = import_stl(filename = "eoma68.stl")
    r = rotate([90,180,180]).add(card)
    r = translate([(600+cpu_offs)*scl, 0*scl,
                (-19)*scl]).add(r)
    t.add(r)

    # Micro SD
    j = cube([165.0*scl, 151.1*scl, (18)*scl])
    r = translate([(1440)*scl, 0*scl,
                (-18)*scl]).add(j)
    t.add(r)

    # LVDS IC
    j = cube([141*scl, 83*scl, (12)*scl])
    r = translate([(1040)*scl, 1000*scl,
                (-12)*scl]).add(j)
    t.add(r)

    # Headphone jack
    j = union()
    c = cube([100*scl, 100*scl, (1)*scl])
    c = translate([(0)*scl, 40*scl, (-1)*scl]).add(c)
    j += c
    c = cube([50*scl, 120*scl, (52)*scl])
    c = translate([(25)*scl, 20*scl, (-52)*scl]).add(c)
    j += c
    c = cylinder(r=50/2.*scl, h=40*scl, segments=50, center=True)
    c = rotate([90, 0, 0]).add(c)
    c = translate([(50)*scl, 20*scl, (-20)*scl]).add(c)
    j += c
    r = translate([(1320)*scl, 0*scl,
                (0)*scl]).add(j)
    t.add(r)

    # USB x 2
    u = cube([132*scl, 137*scl, (66.5)*scl])
    r = translate([(40)*scl, 130*scl, (-66.5)*scl]).add(u)
    t.add(r)
    r = translate([(185)*scl, 0*scl, (-66.5)*scl]).add(u)
    t.add(r)
    r = translate([(330)*scl, 130*scl, (-66.5)*scl]).add(u)
    t.add(r)

    v = union()
    t = translate([(390)*scl, 10*scl, (150)*scl]).add(t)
    v.add(t)

    return t

def lcd_screen_removeparts(scl):

    u = union()
    p = lcd_panel(scl, offs=2)
    p = translate(v=[155.5*scl,61*scl,(lcd_ht)*scl]).add(p)
    u += p

    p = lcd_view_area(scl, offs=3)
    p = translate(v=[155.5*scl,61*scl,(lcd_doff+lcd_ht)*scl]).add(p)
    u += p

    u = translate(v=[0*scl,0*scl,(-lid_offset+2)*scl]).add(u)

    return u

def screen_adjust(b, scl, angle):

    b -= lcd_screen_removeparts(scl)
    return hinge_rotate(scl, b, angle)

def mirror_part(se, scl, offs):
    m = mirror([0, 0, 1]).add(se)
    m = rotate([0, 0, 180]).add(m)
    return translate(v=[0, offs*scl,0]).add(m)

def create_laptop(t, scl, part, angle):
    b = union()

    lid_adjust_ht = 0
    base_adjust_ht = 0
    scrn_end_ht = 30
    scrn_hinge_ht = 80

    if part == SCREEN_END:
        print "screen end", scrn_end_ht/10., lcd_end_ht/10.
        se = screen_end(scl, scrn_end_ht, lcd_end_ht)
        m = translate(v=[0, 0*scl,0]).add(se)
        if mirroring & LEFTPART:
            b.add(m)
        if mirroring & RIGHTPART:
            m = mirror_part(se, scl, total_width)
            b.add(m)

        b = screen_adjust(b, scl, angle)

    lid_adjust_ht += scrn_end_ht
    lid_adjust_ht += lcd_end_ht

    pcb1_support_offset = 120
    tpanel_offset = -190

    if part == FRICTION_HINGE2:
        se = friction_hinge2(scl, 12)
        h = lid_adjust_ht+scrn_hinge_ht+3+10
        m = translate(v=[0, h*scl,0]).add(se)
        if mirroring & LEFTPART:
            b.add(m)
        if mirroring & RIGHTPART:
            m = mirror_part(se, scl, total_width-h)
            b.add(m)

        b = screen_adjust(b, scl, angle)

    if part == FRICTION_HINGE1:
        se = friction_hinge1(scl, 40)
        h = lid_adjust_ht+scrn_hinge_ht+30
        m = translate(v=[0, h*scl,0]).add(se)
        if mirroring & LEFTPART:
            b.add(m)
        if mirroring & RIGHTPART:
            m = mirror_part(se, scl, total_width-h)
            b.add(m)

        b = screen_adjust(b, scl, angle)

    if part == SCREEN_HINGE:
        se = screen_hinge(scl, scrn_hinge_ht-5)
        m = translate(v=[0, (lid_adjust_ht-5)*scl,0]).add(se)
        if mirroring & LEFTPART:
            b.add(m)
        if mirroring & RIGHTPART:
            m = mirror_part(se, scl, total_width-(lid_adjust_ht-5))
            b.add(m)

        b = screen_adjust(b, scl, angle)

    if part == CABLE_PROTECTOR:
        se = cable_protector(scl, 30)
        m = translate(v=[0, (lid_adjust_ht-40)*scl,0]).add(se)
        if mirroring & LEFTPART:
            b.add(m)

    lid_adjust_ht += scrn_hinge_ht

    if part == BASE_END:
        if mirroring & LEFTPART:
            se = base_end(scl, base_end_ht, 0)
            m = translate(v=[0, -10*scl, 55*scl]).add(se)
            b.add(m)
        if mirroring & RIGHTPART:
            se = base_end(scl, base_end_ht, kbd_numpad_indent)
            m = mirror_part(se, scl, total_width+10)
            b.add(m)

    base_adjust_ht = base_end_ht-10
    base_adjust_ht += scrn_hinge_ht

    base_back_ht = (total_width - base_centre_ht) / 2 - base_adjust_ht
    base_front_ht = total_width / 2 - base_adjust_ht
    base_back_hinge_ht = 172

    if part == PCB1:
        se = pcb1(scl)
        m = translate(v=[0, -20*scl,0]).add(se)
        b.add(m)

    if part == PCB2:
        se = pcb2(scl)
        b.add(se)

    if part == BASE_BACK_HINGE:
        bh = base_back_hinge_ht+scrn_hinge_ht-9
        print "base back hinge", bh/10., (scrn_hinge_ht)/10.
        if mirroring & LEFTPART:
            # NOTE: ... here's the other bit
            se = base_back_hinge(scl, bh, scrn_hinge_ht+2,
                                    tpanel_offset+110)
            m = translate(v=[0, (base_adjust_ht-scrn_hinge_ht)*scl,0]).add(se)
            b.add(m)
        if mirroring & RIGHTPART:
            se = base_back_hinge(scl, bh, scrn_hinge_ht+2,
                                    -tpanel_offset)
            m = mirror_part(se, scl, total_width-base_adjust_ht+scrn_hinge_ht)
            b.add(m)

    if part == BASE_BACK:
        bh = base_back_ht-base_back_hinge_ht+5
        off = base_adjust_ht+ base_back_hinge_ht-5
        print "base back height", bh/10., (scrn_hinge_ht)/10.
        if mirroring & LEFTPART:
            # NOTE: ... here's the other bit
            se = base_back_bot(scl, bh, 0,
                                    tpanel_offset+pcb1_support_offset)
            m = translate(v=[0, off*scl,0]).add(se)
            b.add(m)
        if mirroring & RIGHTPART:
            se = base_back_bot(scl, bh, 0,
                                    -tpanel_offset)
            m = mirror_part(se, scl, total_width-off)
            b.add(m)

    if part == PCB3:
        se = pcb3(scl)
        m = translate(v=[0, (total_width-pcb3_lock_offs)*scl,0])
        m.add(se)
        b.add(m)

    back_kbd_offs = 20

    if part == BACK_KBD_RUNNER:
        if mirroring & LEFTPART:
            se = back_kbd_runner(scl, base_back_ht+scrn_hinge_ht-back_kbd_offs,
                                      tpanel_offset+10)
            m = translate(v=[0,
                            (base_adjust_ht-scrn_hinge_ht+back_kbd_offs)*scl,
                             0]).add(se)
            b.add(m)
        if mirroring & RIGHTPART:
            # XXX grr magic constant, matching battery support
            se = back_kbd_runner(scl, base_back_ht+scrn_hinge_ht-back_kbd_offs,
                                        -tpanel_offset-50, True)
            m = mirror_part(se, scl, total_width-
                    (base_adjust_ht-scrn_hinge_ht+back_kbd_offs))
            b.add(m)

    adj = scrn_end_ht+lcd_end_ht
    if part == SCREEN_FRONT_EDGE:
        sfh = (total_width-scrn_centre_ht)/2-adj
        print "screen front edge", sfh/10., scrn_centre_ht/2./10.
        se = screen_front_edge(scl, sfh)
        adj -= 10
        m = translate(v=[0, (adj)*scl,0]).add(se)
        if mirroring & LEFTPART:
            b.add(m)
        if mirroring & RIGHTPART:
            m = mirror_part(se, scl, total_width-adj)
            b.add(m)
        b = screen_adjust(b, scl, angle)

    adj = scrn_end_ht+lcd_end_ht+scrn_hinge_ht
    if part == SCREEN_BACK_EDGE:
        sbh = (total_width-scrn_centre_ht)/2-adj
        print "screen back edge", sbh/10., scrn_centre_ht/2./10.
        se = screen_back_edge(scl, sbh, mirroring & RIGHTPART)
        adj -= 10
        m = translate(v=[0, (adj)*scl,0]).add(se)
        if mirroring & LEFTPART:
            b.add(m)
        if mirroring & RIGHTPART:
            m = mirror_part(se, scl, total_width-adj)
            b.add(m)
        b = hinge_rotate(scl, b, angle)

    compartment_ht = base_adjust_ht-scrn_hinge_ht

    if part == BASE_FRONT_TOP:
        if mirroring & LEFTPART:
            se = base_front_top(scl, base_front_ht+scrn_hinge_ht, tpanel_offset)
            m = translate(v=[0, (compartment_ht*scl),0]).add(se)
            b.add(m)
        if mirroring & RIGHTPART:
            se = base_front_top(scl, base_front_ht+scrn_hinge_ht, -tpanel_offset)
            m = mirror_part(se, scl, total_width-compartment_ht)
            b.add(m)

    if part == BASE_PANEL_BACK_CLIPS:
        if mirroring & LEFTPART:
            se = base_panel_back_clips(scl, base_front_ht+scrn_hinge_ht, tpanel_offset)
            m = translate(v=[0, (compartment_ht*scl),0]).add(se)
            b.add(m)
        if mirroring & RIGHTPART:
            se = base_panel_back_clips(scl, base_front_ht+scrn_hinge_ht, -tpanel_offset)
            m = mirror_part(se, scl, total_width-compartment_ht)
            b.add(m)

    if part == BASE_PANEL_FRONT_CLIPS:
        if mirroring & LEFTPART:
            se = base_panel_front_clips(scl, base_front_ht+scrn_hinge_ht, tpanel_offset)
            m = translate(v=[0, (compartment_ht*scl),0]).add(se)
            b.add(m)
        if mirroring & RIGHTPART:
            se = base_panel_front_clips(scl, base_front_ht+scrn_hinge_ht, -tpanel_offset)
            m = mirror_part(se, scl, total_width-compartment_ht)
            b.add(m)

    if part == BASE_PANEL:
        if mirroring & LEFTPART:
            se = base_panel(scl, base_front_ht+scrn_hinge_ht, tpanel_offset)
            m = translate(v=[0, (compartment_ht*scl),0]).add(se)
            b.add(m)
        if mirroring & RIGHTPART:
            se = base_panel(scl, base_front_ht+scrn_hinge_ht, -tpanel_offset)
            m = mirror_part(se, scl, total_width-compartment_ht)
            b.add(m)

    if part == FRONT_KBD_TRAY:
        if mirroring & LEFTPART:
            se = front_kbd_tray(scl, base_front_ht+scrn_hinge_ht+tpanel_offset,
                                     0, 0)
            m = translate(v=[0, (base_adjust_ht-scrn_hinge_ht-hthick)*scl,
                             0]).add(se)
            b.add(m)
        if mirroring & RIGHTPART:
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

    if part == SCREEN_MID:
        se = screen_mid(scl, scrn_centre_ht+10)
        m = translate(v=[0, (total_width/2-(scrn_centre_ht+10)/2)*scl,0]).add(se)
        b.add(m)
        b = screen_adjust(b, scl, angle)

    base_joiner_ht = 150

    tpanel_ht = (base_adjust_ht + tpanel_offset + base_centre_ht/2 -
                            (tpanel_b_w)/2)
    if part == TPANEL_MID:
        se = tpanel_mid(scl, tpanel_b_w, tpanel_offset, pcb1_support_offset)
        m = translate(v=[0, tpanel_ht*scl, 0]).add(se)
        b.add(m)

    pcb1_support_ht = 30

    if part == COMPARTMENT_LOCKIN:
        se = compartment_lockin(scl, tpanel_ht-compartment_ht, tpanel_offset,
                             kbd_numpad_indent)
        m = translate(v=[0, (compartment_ht*scl),0]).add(se)
        b.add(m)

    if part == COMPARTMENT_LOCKIN_CAPTURE:
        se = compartment_lockin_capture(scl, tpanel_ht-compartment_ht,
                             tpanel_offset, kbd_numpad_indent)
        m = translate(v=[0, (compartment_ht*scl),0]).add(se)
        b.add(m)

    if part == COMPARTMENT_LID:
        se = compartment_lid(scl, tpanel_ht-compartment_ht, tpanel_offset,
                             kbd_numpad_indent)
        m = translate(v=[0, (compartment_ht*scl),0]).add(se)
        b.add(m)

    if part == BATTERY_SUPPORT1:
        se = battery_support1(scl, pcb1_support_ht, tpanel_offset)
        # XXX grr, magic constant for height, has to match
        # back kbd runner
        m = translate(v=[0,
                         (tpanel_ht+tpanel_b_w-80)*scl,
                         0]).add(se)
        b.add(m)

    if part == PCB3_SUPPORT:
        se = pcb3_support(scl, 30)
        m = translate(v=[0, (total_width-pcb3_lock_offs)*scl,0]).add(se)
        b.add(m)

    if part == PCB1_SUPPORT:
        se = pcb1_support(scl, pcb1_support_ht,
                            tpanel_offset, pcb1_support_offset)
        m = translate(v=[0,
                         (tpanel_ht+110)*scl,
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
    b = translate(v=[(0)*scl, (1000)*scl, (0)*scl]).add(b)
    u -= b
    b = translate(v=[(0)*scl, (1370)*scl, (0)*scl]).add(b)
    u -= b
    b = translate(v=[(0)*scl, (670)*scl, (0)*scl]).add(b)
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
        angles = [0]

    for i in range(rpt):
        for angle in angles:
            u = union()
            for i in [
                        #BASE_END,
                        #SCREEN_END,
                        #CABLE_PROTECTOR,
                        #SCREEN_HINGE,
                        #FRICTION_HINGE1,
                        #FRICTION_HINGE2,
                        #SCREEN_BACK_EDGE,
                        #SCREEN_FRONT_EDGE,
                        #SCREEN_MID,
                        #BASE_FRONT_TOP,
                        #FRONT_KBD_TRAY,
                        #PCB1,
                        #PCB2,
                        #PCB3,
                        #TPANEL_MID,
                        #BASE_MID,
                        #BACK_KBD_RUNNER,
                        #BASE_BACK,
                        BASE_BACK_HINGE,
                        #PCB1_SUPPORT,
                        #PCB3_SUPPORT,
                        #BATTERY_SUPPORT1,
                        #COMPARTMENT_LID,
                        #COMPARTMENT_LOCKIN,
                        #COMPARTMENT_LOCKIN_CAPTURE,
                        #BASE_PANEL,
                        #BASE_PANEL_BACK_CLIPS,
                        #BASE_PANEL_FRONT_CLIPS,
                    ]:
                t = union()
                create_laptop(t, scl, part=i, angle=angle)
                r = union().add(t)
                if i == BASE_PANEL:
                    c = [0.8, 0.8, 0.3, 0.25]
                elif i == PCB1: # pcb1
                    c = [0.8, 0.3, 0.8, 0.5]
                elif i == PCB2: # pcb2
                    c = [0.3, 0.8, 0.3, 0.25]
                elif i == PCB3: # pcb3
                    c = [0.1, 0.8, 0.3, 0.25]
                #elif i == CASE_CLASP: # pcb1
                    #c = [0.3, 0.8, 0.3, 0.2]
                else:
                    c = [0.3, 0.5, 0.8, 0.5]
                c = color(c)
                c.add(r)
                u.add(c)

            if add_internal_parts:

                if add_internal_parts & USB_WIFI:
                    # USB WIFI dongle
                    wifi = usb_wifi(scl)
                    r = translate([(665)*scl, 150*scl,
                                    (85)*scl]).add(wifi)
                    c = [0.2, 0.8, 0.8, 0.2]
                    r = union().add(r)
                    c = color(c)
                    c.add(r)
                    u.add(c)

                if add_internal_parts & KEYBOARD:
                    # Keyboard
                    kbd = kbd_part(scl)
                    r = translate([(lcd_w-kbd_w/2+25-79)*scl, total_width/2*scl,
                                    (62+5)*scl]).add(kbd)
                    c = [0.3, 0.8, 0.5, 0.2]
                    r = union().add(r)
                    c = color(c)
                    c.add(r)
                    u.add(c)

                if add_internal_parts & LCD_PANEL:
                    # LCD Panel
                    b = union()
                    p = lcd_panel(scl, offs=2)
                    p = translate(v=[155.5*scl,
                            lcd_indent*scl,(lcd_ht+2-lid_offset)*scl]).add(p)
                    b += p

                    r = hinge_rotate(scl, b, angle)
                    c = [0.8, 0.8, 0.2, 0.2]
                    c = color(c)
                    c.add(r)
                    u.add(c)

                if add_internal_parts & BATTERY:
                    # Battery
                    b = union()
                    p = cube([1620*scl, 1360*scl, 65*scl])
                    p = translate(v=[(500.0-80)*scl,
                                (lcd_l-1360-70)*scl,(97)*scl]).add(p)
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
