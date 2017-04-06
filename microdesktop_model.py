# Copyright (C) 2014, 2015 Luke Kenneth Casson Leighton <lkcl@lkcl.net>
# License: GPLv3+

""" TODO:
    * sort out gaps between base end, base hinge end, and screen edge
    * parameterise plastic join-point gaps/sizes so it can be varied
    * allow [flat] cable access through to screen connector
    * base_front_top is short by 1mm on each side.
    * add chamfering on bacK kbd runner and pcb/battery support.
    * move back kbd runner last internal supports in so that they miss
      the hex nut slot in base_back
    * move left keyboard lock on right front_kbd_tray, keyboard jamming
"""

import sdxf
import time
import math
from pyopenscad import *
from polysurface import spline_double_divide, Offset, SurfaceFromCurves
from copy import deepcopy
from pyscadutil import B0, B45, pin
from pyscadutil import curvebox, shearedcube, hollowbox, touch_arc
from pyscadutil import L, R, T, D, F, B

pin_parts_3d=False
orientate=False
LEFTPART = 1
RIGHTPART = 2
mirroring = RIGHTPART#LEFTPART| RIGHTPART #RIGHTPART

BATTERY = 0x1
KEYBOARD = 0x2
USB_WIFI = 0x4
LCD_PANEL = 0x8
add_internal_parts = 0#BATTERY

pcbthick = 16.0
scl = 0.1
test = False
single = True
cutdown = False
revision_1_pcb = True

PCB1 = 1
LAYER0     = 6
LAYER1_TOP = 2
LAYER2_TOP = 3
LAYER3_TOP = 4
LAYER4_TOP = 5
LAYER5_TOP = 7
LAYER2_BOT = 8
LAYER3_BOT = 9
LAYER6     = 10
CORNER1     = 11
CORNER2     = 12
CORNER3     = 13
CORNER4     = 14
FRONT_PLATE = 15
BACK_PLATE = 16
SIDE_PLATE1 = 17
SIDE_PLATE2 = 18

TOP=0x1
BOTTOM=0x2

md_w = 1144
md_h = 841
md_d = 190
boxthick = 80
indent = 40

def add_offset(offs, l):
    x, y = offs
    for i in range(len(l)):
        l[i] = (l[i][0] + x, l[i][1] + y)
    return l

def points_arc(x, y, r, angle1, angle2, lines=30.0, incstart=True, incend=True):
    angle1 = math.radians(angle1)
    angle2 = math.radians(angle2)

    step = (angle2 - angle1) / (lines+1)
    if step > 0:
        dirn = 1.0
    else:
        dirn = -1.0

    l = []
    a = angle1
    if not incend:
        angle2 -= step
    if not incstart:
        a += step
    while (a * dirn < angle2 * dirn*0.9995):
        l.append((x + math.sin(a) * r, y + math.cos(a) * r,))
        a += step
    return l

def create_corner2(scl, gap):
    t = union()

    u = union()

    b = curvebox(scl, 140, 88, md_d, 25)
    u.add(b)

    c = cylinder(h=200*scl, r=17.5*scl, segments=30)
    u -= translate([(boxthick/2)*scl, (boxthick/2)*scl, -1*scl]).add(c)
    u -= translate([(boxthick+10)*scl, (boxthick/2)*scl, -1*scl]).add(c)

    d = cube([50*scl, 22*scl, 200*scl])
    d = translate([(140-17)*scl, (88-22-(boxthick/2-gap-15))*scl, -1*scl]).add(d)

    u -= d

    d = cube([22*scl, 50*scl, 200*scl])
    d = translate([(indent-gap-17)*scl, (88-50-(boxthick-gap))*scl,
                    -1*scl]).add(d)

    u -= d

    d = cube([100*scl, 100*scl, 20*scl])
    d = translate([(indent-gap)*scl, (88-100-(boxthick-gap))*scl,
                    18*scl]).add(d)

    u -= d

    t.add(u)

    return t

def create_corner1(scl, gap, pcbcut=False):
    t = union()

    u = union()

    b = curvebox(scl, 140, 88, md_d, 25)
    u.add(b)

    if pcbcut:

        d = cube([300*scl, 100*scl, 65*scl])
        d = translate([-1*scl, (88-gap)*scl, 32*scl]).add(d)

        u -= d

        #b = curvebox(scl, 160, 32, 50, 12)
        #b = translate([100*scl, 55*scl, 0*scl]).add(b)
        ##u += b

    c = cylinder(h=200*scl, r=17.5*scl, segments=30)
    u -= translate([(boxthick/2)*scl, (boxthick/2)*scl, -1*scl]).add(c)
    u -= translate([(boxthick+10)*scl, (boxthick/2)*scl, -1*scl]).add(c)

    d = cube([50*scl, 22*scl, 200*scl])
    d = translate([(140-17)*scl, (boxthick/2-gap-15)*scl, -1*scl]).add(d)

    u -= d

    d = cube([22*scl, 50*scl, 200*scl])
    d = translate([(indent-gap-17)*scl, (boxthick-gap)*scl, -1*scl]).add(d)

    u -= d

    if pcbcut:
        dep = 230
    else:
        dep = 30
    d = cube([300*scl, 100*scl, 20*scl])
    d = translate([(dep)*scl, (boxthick-gap)*scl, 18*scl]).add(d)

    u -= d

    t.add(u)

    return t

def create_side(scl, gap, d, doffs):

    md_w1 = md_w-175#-286

    angle = 19.0
    rangle = math.radians(angle)
    a, r, xm, ym = arc_between_points(0, 0, md_w1, 0, rangle, x1=1, y1=1)
    print md_w1, r, xm, ym

    t = union()
    #d = dxf_linear_extrude(file=fname, height=1.5)
    c = touch_arc(r, md_d-gap*2, 15, 0, scl, 0, angle=90-angle, segments=400)
    c = rotate([0, 0, -angle/2.0]).add(c)
    c = translate([(ym)*scl, (xm-1)*scl, -gap*scl]).add(c)
    c = rotate([180, 0, 0]).add(c)

    t.add(c)

    md_w2 = (r+15) * rangle
    tlist = [(0, 0), (md_d*scl, 0), (md_d*scl, md_w2*scl), (0, md_w2*scl)]

    add_offset(doffs, tlist)
    d.append(sdxf.PolyLine(points=tlist,closed=1,color=1))

    fname = 'microdesktopcase_side.dxf'
    d.saveas(fname)

    if False: # testing
        d = dxf_linear_extrude(file=fname, height=1.5)
        d = rotate([0, -90, 0]).add(d)
        t.add(d)
    return t

def create_back(scl, gap, d, doffs):

    tlist = [(0, 0), (md_d*scl, 0), (md_d*scl, md_h*scl), (0, md_h*scl)]
    l = add_offset(doffs, tlist)

    d.append(sdxf.PolyLine(points=tlist,closed=1,color=1))

    micro = [(0, 0), (1.7, 0), (1.7, 15), (0, 15)]

    posx, posy = (0*scl, 200*scl,)
    l = []
    for p1, p2 in micro:
        l.append((p1+posx, p2+posy,))
    l = add_offset(doffs, l)
    d.append(sdxf.PolyLine(points=l,closed=1,color=1))

    eject = [(0, 0), (7.5, 0), (7.5, 7), (0, 7)]

    posx, posy = (25*scl, 771*scl,)
    l = []
    for p1, p2 in eject:
        l.append((p1+posx, p2+posy,))
    l = add_offset(doffs, l)
    d.append(sdxf.PolyLine(points=l,closed=1,color=1))

    pcmcia = [(0, 0), (5.2, 0), (5.2, 61), (0, 61)]

    posx, posy = (35*scl, 124*scl,)
    l = []
    for p1, p2 in pcmcia:
        l.append((p1+posx, p2+posy,))
    l = add_offset(doffs, l)
    d.append(sdxf.PolyLine(points=l,closed=1,color=1))

    fname = 'microdesktopcase_back.dxf'
    d.saveas(fname)

    t = union()
    d = dxf_linear_extrude(file=fname, height=1.5)
    d = rotate([0, -90, 0]).add(d)
    t.add(d)

    return t

def create_front(scl, gap, d, doffs):

    offs = 0.25
    tlist = [(0, 0), (md_d*scl, 0), (md_d*scl, md_h*scl), (0, md_h*scl)]

    l = add_offset(doffs, tlist)
    d.append(sdxf.PolyLine(points=tlist,closed=1,color=1))

    usb = [(0, 0), (7.0, 0), (7.0, 14.5), (0, 14.5)]

    for posx, posy in [(40*scl, 670.0*scl,), (40*scl, 490.0*scl,)]:
        l = []
        for p1, p2 in usb:
            l.append((p1+posx, p2+posy-offs,))
        l = add_offset(doffs, l)
        d.append(sdxf.PolyLine(points=l,closed=1,color=1))

    vga = [(0, 0), (13.4, 0), (13.4, 30.8), (0, 30.8)]

    posx, posy = (32*scl, 166.0*scl-offs,)
    l = []
    for p1, p2 in vga:
        l.append((p1+posx, p2+posy,))
    l = add_offset(doffs, l)
    d.append(sdxf.PolyLine(points=l,closed=1,color=1))

    dc = [(0, 0), (11, 0), (11, 9.2), (0, 9.2)]

    posx, posy = (34*scl, 22*scl-offs,)
    l = []
    for p1, p2 in dc:
        l.append((p1+posx, p2+posy,))
    l = add_offset(doffs, l)
    d.append(sdxf.PolyLine(points=l,closed=1,color=1))

    led = [(0, 0), (1.5, 0), (1.5, 1.0), (0, 1.0)]

    posx, posy = (34*scl, 133*scl-offs,)
    l = []
    for p1, p2 in led:
        l.append((p1+posx, p2+posy,))
    l = add_offset(doffs, l)
    d.append(sdxf.PolyLine(points=l,closed=1,color=1))

    fname = 'microdesktopcase_front.dxf'
    d.saveas(fname)

    t = union()
    d = dxf_linear_extrude(file=fname, height=1.5)
    d = rotate([0, -90, 0]).add(d)
    t.add(d)

    return t

def create_top_line_outer(scl, downtoleft, downtoright, gap):
    tlist = []
    tlist.append((0      , (boxthick+md_h-downtoleft)*scl))
    tlist.append((0, (boxthick*2+md_h)*scl))
    tlist.append(((md_w+indent*2)*scl, (boxthick*2+md_h)*scl))
    tlist.append(((md_w+indent*2)*scl, (boxthick+md_h-downtoright)*scl))

    return tlist

def create_top_line_inner(scl, downtoleft, downtoright, gap):
    tlist = []
    tlist.append(((md_w+indent)*scl, (boxthick+md_h-downtoright)*scl))
    tlist.append(((md_w+indent)*scl, (boxthick+md_h)*scl))
    tlist.append((indent*scl      , (boxthick+md_h)*scl))
    tlist.append((indent*scl, (boxthick+md_h-downtoleft)*scl))

    return tlist

def create_bottom_line_outer(scl, uptoleft, uptoright, gap):
    tlist = []
    tlist.append(((md_w+indent*2)*scl, (boxthick+uptoright)*scl))
    tlist.append(((md_w+indent*2)*scl, (0)*scl))
    tlist.append((0, (0)*scl))
    tlist.append((0      , (boxthick+uptoleft)*scl))

    return tlist

def create_bottom_line_inner(scl, uptoleft, uptoright, gap):
    tlist = []
    tlist.append((indent*scl, (boxthick+uptoleft)*scl))
    tlist.append((indent*scl      , (boxthick)*scl))
    tlist.append(((md_w+indent)*scl, (boxthick)*scl))
    tlist.append(((md_w+indent)*scl, (boxthick+uptoright)*scl))

    return tlist

def create_layer(scl, layer, topbot, gap, microsd, d, doffs):

    if layer == 0 or layer == 6:
        tlist = []
        r=2.5

        md_w1 = md_w-115
        angle = 19.0
        rangle = math.radians(angle)
        y1 = 0
        a, r1, xm, ym = arc_between_points(8.0-r, y1, md_w1*scl, y1,
                                           rangle, x1=1, y1=-1)

        xm += md_w1*scl
        pts = points_arc(xm, ym, r1, angle/2, -angle/2)
        #pts.reverse()
        tlist += pts
        tlist += points_arc(r, r, r, 180, 270)

        angle1 = 8.0
        rangle1 = math.radians(angle1)
        x1 = 0
        h = (md_h+boxthick*2)*scl - (8.8)
        a, r1, xm, ym = arc_between_points(x1, 8.8, x1, h,
                                           rangle1, x1=-1, y1=1)

        #xm -= md_w1*scl - 14
        ym += h - (8.8)
        pts = points_arc(xm, ym, r1, angle1/2+90, -angle1/2+90)
        tlist += pts
    
        tlist += points_arc(r, (md_h+boxthick*2)*scl-r, r, 270, 360)

        y1 = (md_h+boxthick*2)*scl
        a, r1, xm, ym = arc_between_points(md_w1*scl, y1, 8.0-r, y1,
                                           rangle, x1=1, y1=1)

        xm -= md_w1*scl - 14
        pts = points_arc(xm, ym, r1, angle/2-180, -angle/2-180)
        tlist += pts

        tlist += points_arc((md_w+indent*2)*scl-(r),
                            (md_h+boxthick*2)*scl-r, r,
                            0, 90)
        tlist += points_arc((md_w+indent*2)*scl-(r),
                            (md_h+boxthick*2)*scl+r-8.8, r,
                            90, 160)

        if microsd:
            msd_x = 430*scl
            msd_w = 150*scl
            msd_h = 30*scl
            h = tlist[-1][0]
            tlist += [(h, msd_x), (h-msd_h, msd_x),
                      (h-msd_h, msd_x-msd_w),
                      (h, msd_x-msd_w)]

        tlist += points_arc((md_w+indent*2)*scl-(r),
                            (8.8-r), r,
                            20, 90)
        tlist += points_arc((md_w+indent*2)*scl-(r),
                            #(md_h+boxthick*2)*scl+r-8.8, r,
                            r, r,
                            90, 180)

    add_offset(doffs, tlist)

    d.append(sdxf.PolyLine(points=tlist,closed=1,color=1))

    for c1 in add_offset(doffs,
              [(boxthick/2.0*scl, (boxthick+md_h+boxthick/2.0)*scl),
              ((indent+md_w)*scl,
               (md_h+boxthick+boxthick/2.0)*scl),]):
        d.append(sdxf.Circle(center=c1, radius=1.75, color=1))

    for c1 in add_offset(doffs,
              [(boxthick/2.0*scl, boxthick/2.0*scl),
               ((indent+md_w)*scl, boxthick/2.0*scl)]):
        d.append(sdxf.Circle(center=c1, radius=1.75, color=1))

    if layer == 0:
        for c1 in add_offset(doffs,
            [((md_w-250+indent)*scl, (md_h-100+boxthick)*scl,)]):
            d.append(sdxf.Circle(center=c1, radius=1.75, color=1))

    fname = 'microdesktopcase_%d.dxf' % (layer)
    d.saveas(fname)

    t = union()
    t.add(dxf_linear_extrude(file=fname, height=2))

    return t

def pcb1(scl):

    t = union()

    # PCB
    pcb = union()
    b = cube([md_w*scl, md_h*scl, (pcbthick)*scl])
    pcb += b
    b = cube([521*scl, 1200*scl, (30)*scl])
    b = translate([(947.8)*scl, 688*scl, -10*scl]).add(b)
    pcb -= b

    r = translate([(0)*scl, 00*scl, 0]).add(pcb)
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
    s = rotate([0,180,90]).add(s)
    s = translate([(555+590)*scl, (708.5+126)*scl,
                (74)*scl]).add(s)
    s -= b

    t.add(s)

    # EOMA68 CPU Card
    card = import_stl(filename = "eoma68.stl")
    r = rotate([90,180,270]).add(card)
    r = translate([(1160)*scl, 675.0*scl,
                (50)*scl]).add(r)
    t.add(r)

    # Micro SD
    j = cube([165.0*scl, 151.1*scl, (18)*scl])
    r = translate([(980)*scl, 200*scl,
                (-18)*scl]).add(j)
    t.add(r)

    # USB x 2
    u = union()
    u.add(cube([132*scl, 130*scl, (70.0)*scl]))
    d = cube([21*scl, 145*scl, (66.0)*scl])
    u.add(translate([(-20)*scl, -7.5*scl, (10)*scl]).add(d))
    
    r = translate([(0)*scl, 675*scl, (pcbthick)*scl]).add(u)
    t.add(r)
    r = translate([(0)*scl, 495*scl, (pcbthick)*scl]).add(u)
    t.add(r)

    # VGA
    u = cube([150*scl, 305*scl, (130)*scl])
    r = translate([(-20)*scl, 166*scl, (pcbthick)*scl]).add(u)
    t.add(r)

    # DC
    u = cube([144*scl, 90*scl, (110)*scl])
    r = translate([(-20)*scl, 20*scl, (pcbthick)*scl]).add(u)
    t.add(r)

    # hole through PCB and PCMCIA holder
    c = cylinder(h=200*scl, r=17.5*scl, segments=30)
    t -= translate([(md_w-250)*scl, (md_h-100)*scl, -1*scl]).add(c)

    v = union()
    t = translate([(390)*scl, 12.5*scl, (150)*scl]).add(t)
    v.add(t)

    return t

def arc_between_points(xa, ya, xb, yb, angle, x1=1, y1=1):
    """
    http://mymathforum.com/algebra/21368-find-equation-circle-given-two-points-arc-angle.html
    """

    xd = xa - xb
    yd = ya - yb
    d2 = xd*xd+yd*yd

    d = math.sqrt(d2)
    r = math.sqrt(d2 / (2*(1 - math.cos(angle))))

    xm = (xd/2.0) + xa
    ym = (yd/2.0) + ya

    a = math.sqrt(r*r - d2/4)

    if abs(yd) > abs(xd):
        m = xd / yd
    else:
        m = yd / xd

    a1 = a / math.sqrt(m*m + 1)
    a2 = m * a1

    if abs(yd) > abs(xd):
        return a, r, xm + a1*x1, ym + a2*y1
    else:
        return a, r, xm + a2*x1, ym + a1*y1


def create_microdesktop(t, scl, part, d, doffs):
    b = union()

    if part == PCB1:
        se = pcb1(scl)
        m = translate(v=[(indent*2-200)*scl, (-7.5+boxthick-100)*scl,
                          0.5]).add(se)
        b.add(m)

    elif part == BACK_PLATE:

        gap = 4
        se = create_back(scl, gap, d, doffs)
        m = translate(v=[24.7+(indent+md_w)*scl,
                        (-9.5+boxthick*scl), 13.6]).add(se)
        b.add(m)

    elif part == SIDE_PLATE1:

        gap = 4
        se = create_side(scl, gap, d, doffs)
        se = rotate([0,0,-90]).add(se)
        m = translate(v=[22.7+(indent+90)*scl,
                            (-9.5+23*scl), 13.6]).add(se)
        b.add(m)

    elif part == SIDE_PLATE2:

        gap = 4
        se = create_side(scl, gap, d, doffs)
        se = rotate([0,0,90]).add(se)
        m = translate(v=[22.7+(md_w-(indent+4))*scl,
                            (-9.5+(md_h+138)*scl), 13.6]).add(se)
        b.add(m)

    elif part == FRONT_PLATE:

        gap = 4
        se = create_front(scl, gap, d, doffs)
        m = translate(v=[22.7+indent*scl, (-9.5+boxthick*scl), 13.6]).add(se)
        b.add(m)

    elif part == LAYER0:

        gap = 4
        se = create_layer(scl, 0, TOP|BOTTOM, gap, True, d, doffs)
        m = translate(v=[19+indent*scl, -9.5, 11.6]).add(se)
        b.add(m)

    elif part == CORNER1:

        gap = 4
        se = create_corner1(scl, gap)
        m = translate(v=[19+indent*scl, -9.5, 13.6]).add(se)
        b.add(m)

    elif part == CORNER2:

        gap = 4
        se = create_corner2(scl, gap)
        m = translate(v=[19+indent*scl, -9.5+(md_h+boxthick-8)*scl,
                            13.6]).add(se)
        b.add(m)

    elif part == CORNER3:

        gap = 4
        se = create_corner1(scl, gap, True)
        se = rotate([0,0,180]).add(se)
        se = translate(v=[(md_w+indent*2)*scl,
                          (md_h+boxthick*2)*scl, 0]).add(se)
        m = translate(v=[19+indent*scl, -9.5, 13.6]).add(se)
        b.add(m)

    elif part == CORNER4:

        gap = 4
        se = create_corner2(scl, gap)
        se = rotate([0,0,180]).add(se)
        se = translate(v=[(md_w+indent*2)*scl,
                          (boxthick*1+gap*2)*scl, 0]).add(se)
        m = translate(v=[19+indent*scl, -9.5, 13.6]).add(se)
        b.add(m)

    elif part == LAYER6:

        offs = md_d*scl
        gap = 4
        se = create_layer(scl, 6, TOP|BOTTOM, gap, False, d, doffs)
        m = translate(v=[19+indent*scl, -9.5, 13.6+offs]).add(se)
        b.add(m)

    t.add(b)

def create_sides_grouped():

    d = sdxf.Drawing()
    l = [ SIDE_PLATE1, SIDE_PLATE2, BACK_PLATE, FRONT_PLATE]
    j = 0
    for x in range(5,500,25):
        for y in range(5,500,110):
            i = l[j]
            j += 1
            if j == len(l):
                j = 0
            t = union()
            doffs = (x, y)
            create_microdesktop(t, scl, i, d, doffs)

    fname = 'microdesktopcase_group2.dxf'
    d.saveas(fname)

def create_topbot_grouped():

    d = sdxf.Drawing()
    l = [ LAYER0, LAYER6, ]
    j = 0
    for x in range(5,500,130):
        for y in range(5,500,110):
            i = l[j]
            j += 1
            if j == len(l):
                j = 0
            t = union()
            doffs = (x, y)
            create_microdesktop(t, scl, i, d, doffs)

    fname = 'microdesktopcase_group1.dxf'
    d.saveas(fname)


def create_scad():
    u = union()
    for i in [
                PCB1,
                LAYER0,
                CORNER1,
                CORNER2,
                CORNER3,
                CORNER4,
                #LAYER6,
                FRONT_PLATE,
                BACK_PLATE,
                SIDE_PLATE1,
                SIDE_PLATE2,
            ]:
        t = union()
        d = sdxf.Drawing()
        create_microdesktop(t, scl, i, d, (0, 0))
        r = union().add(t)
        if i == -1:
            c = [0.8, 0.8, 0.3, 0.25]
        elif i == PCB1: # pcb1
            c = [0.8, 0.3, 0.8, 0.5]
        elif i in [LAYER0, LAYER6]:
            c = [0.9, 0.3, 0.3, 0.5]
        elif i in[ FRONT_PLATE, BACK_PLATE, SIDE_PLATE1, SIDE_PLATE2]:
            c = [0.3, 0.8, 0.3, 0.5]
        else:
            c = [0.3, 0.5, 0.8, 0.5]
        c = color(c)
        c.add(r)
        u.add(c)


    scad_render_to_file(u, "microdesktop_prog2.scad")
    f = open("microdesktop_model2.scad", "w")
    f.write("""include<microdesktop_prog2.scad>;
    """)
    f.close()

if __name__ == '__main__':
    #create_scad()
    create_topbot_grouped()
    create_sides_grouped()
