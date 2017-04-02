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
import itertools
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

TOP=0x1
BOTTOM=0x2

md_w = 1144
md_h = 841
md_d = 150
boxthick = 80
indent = 40

def create_corner2(scl, gap):
    t = union()

    u = union()

    b = curvebox(scl, 140, 88, 150, 25)
    u.add(b)

    c = cylinder(h=200*scl, r=17.5*scl, segments=30)
    u -= translate([(boxthick/2)*scl, (boxthick/2)*scl, -1*scl]).add(c)
    u -= translate([(boxthick+10)*scl, (boxthick/2)*scl, -1*scl]).add(c)

    d = cube([50*scl, 19*scl, 200*scl])
    d = translate([(140-15)*scl, (88-19-(boxthick/2-gap-15))*scl, -1*scl]).add(d)

    u -= d

    d = cube([19*scl, 50*scl, 200*scl])
    d = translate([(indent-gap-15)*scl, (88-50-(boxthick-gap))*scl,
                    -1*scl]).add(d)

    u -= d

    d = cube([100*scl, 100*scl, 19*scl])
    d = translate([(indent-gap)*scl, (88-100-(boxthick-gap))*scl,
                    13*scl]).add(d)

    u -= d

    t.add(u)

    return t
    
def create_corner1(scl, gap, pcbcut=False):
    t = union()

    u = union()

    
    b = curvebox(scl, 140, 88, 150, 25)
    u.add(b)

    if pcbcut:

        d = cube([300*scl, 100*scl, 65*scl])
        d = translate([-1*scl, (88-gap)*scl, 27*scl]).add(d)

        u -= d

        b = curvebox(scl, 180, 35, 45, 15)
        b = translate([100*scl, 53*scl, 0*scl]).add(b)
        u += b

    c = cylinder(h=200*scl, r=17.5*scl, segments=30)
    u -= translate([(boxthick/2)*scl, (boxthick/2)*scl, -1*scl]).add(c)
    u -= translate([(boxthick+10)*scl, (boxthick/2)*scl, -1*scl]).add(c)

    d = cube([50*scl, 19*scl, 200*scl])
    d = translate([(140-15)*scl, (boxthick/2-gap-15)*scl, -1*scl]).add(d)

    u -= d

    d = cube([19*scl, 50*scl, 200*scl])
    d = translate([(indent-gap-15)*scl, (boxthick-gap)*scl, -1*scl]).add(d)

    u -= d

    d = cube([300*scl, 100*scl, 19*scl])
    d = translate([(230)*scl, (boxthick-gap)*scl, 13*scl]).add(d)

    u -= d

    t.add(u)

    return t
    
def create_front(scl, gap):

    tlist = [(0, 0), (md_d*scl, 0), (md_d*scl, md_h*scl), (0, md_h*scl)]

    d = sdxf.Drawing()
    d.append(sdxf.PolyLine(points=tlist,closed=1,color=1))

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

def create_layer(scl, layer, topbot, gap):

    if topbot & TOP:
        if layer == 0:
            tlisti = create_bottom_line_outer(scl, 0, 0, gap)
            tlisto = create_top_line_outer(scl, 800, 500, gap)
        if layer == 1:
            tlisti = create_top_line_inner(scl, 700, 500, gap)
            tlisto = create_top_line_outer(scl, 700, 500, gap)
            tlisti += create_bottom_line_inner(scl, 60, 180, gap)
            tlisti += create_bottom_line_outer(scl, 60, 180, gap)
        elif layer == 2 or layer == 3:
            tlisti = create_top_line_inner(scl, 35, 50, gap)
            tlisto = create_top_line_outer(scl, 35, 50, gap)
        elif layer == 4:
            tlisti = create_top_line_inner(scl, 375, 800, gap)
            tlisto = create_top_line_outer(scl, 375, 800, gap)
            tlisto += create_bottom_line_outer(scl, 7, 180, gap)
            tlisto += create_bottom_line_inner(scl, 7, 180, gap)
        elif layer == 5:
            tlisti = create_top_line_inner(scl, 735, 800, gap)
            tlisto = create_top_line_outer(scl, 735, 800, gap)
            tlisto += create_bottom_line_outer(scl, 7, 180, gap)
            tlisto += create_bottom_line_inner(scl, 7, 180, gap)
        elif layer == 6:
            tlisti = create_top_line_inner(scl, 7, 100, gap)
            tlisto = create_bottom_line_outer(scl, 7, 180, gap)
            tlisto += create_top_line_outer(scl, 7, 100, gap)
            tlisti += create_bottom_line_inner(scl, 7, 180, gap)
    elif topbot & BOTTOM:
        if layer == 2 or layer == 3:
            tlisto = create_bottom_line_outer(scl, 7, 110, gap)
            tlisti = create_bottom_line_inner(scl, 7, 110, gap)

    d = sdxf.Drawing()
    if layer == 6:
        d.append(sdxf.PolyLine(points=tlisto,closed=1,color=1))
        d.append(sdxf.PolyLine(points=tlisti,closed=1,color=1))
    else:
        d.append(sdxf.PolyLine(points=tlisto+tlisti,closed=1,color=1))

    tb = ''
    if topbot & TOP:
        tb += 't'
        for c1 in ((boxthick/2.0*scl, (boxthick+md_h+boxthick/2.0)*scl),
                  ((indent+md_w)*scl,
                   (md_h+boxthick+boxthick/2.0)*scl),):
            d.append(sdxf.Circle(center=c1, radius=1.75, color=3))

    if topbot & BOTTOM:
        tb += 'b'
        for c1 in ((boxthick/2.0*scl, boxthick/2.0*scl),
                  ((indent+md_w)*scl, boxthick/2.0*scl),):
            d.append(sdxf.Circle(center=c1, radius=1.75, color=3))

    fname = 'microdesktopcase_%s_%d.dxf' % (tb, layer)
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
    s = rotate([0,180,90]).add(s)
    s = translate([(555+590)*scl, (725+125)*scl,
                (74)*scl]).add(s)
    s -= b

    t.add(s)

    # EOMA68 CPU Card
    card = import_stl(filename = "eoma68.stl")
    r = rotate([90,180,270]).add(card)
    r = translate([(1140)*scl, 690*scl,
                (50)*scl]).add(r)
    t.add(r)

    # Micro SD
    j = cube([165.0*scl, 151.1*scl, (18)*scl])
    r = translate([(980)*scl, 200*scl,
                (-18)*scl]).add(j)
    t.add(r)

    # USB x 2
    u = cube([132*scl, 137*scl, (66.5)*scl])
    r = translate([(0)*scl, 678*scl, (pcbthick)*scl]).add(u)
    t.add(r)
    r = translate([(0)*scl, 502*scl, (pcbthick)*scl]).add(u)
    t.add(r)

    # VGA
    u = cube([132*scl, 310*scl, (90)*scl])
    r = translate([(0)*scl, 166*scl, (pcbthick)*scl]).add(u)
    t.add(r)

    # DC
    u = cube([144*scl, 90*scl, (110)*scl])
    r = translate([(0)*scl, 26*scl, (pcbthick)*scl]).add(u)
    t.add(r)

    v = union()
    t = translate([(390)*scl, 10*scl, (150)*scl]).add(t)
    v.add(t)

    return t

def arc_between_points(xa, ya, xb, yb, angle, x1=1, y1=1):
    """
    http://mymathforum.com/algebra/21368-find-equation-circle-given-two-points-arc-angle.html
    """
    xd = xa - xb
    yd = ya - yb
    d2 = xd*xd+yd*yd

    d = sqrt(d2)
    r = sqrt(d2 / (1 - math.cos(angle)))
    
    xm = (xd/2.0) + xa
    ym = (yd/2.0) + ya
 
    a = sqrt(r*r - d2/4)

    if xd > yd:
        m = xd / yd
    else:
        m = yd / xd

    a1 = a / sqrt(m*m + 1)
    a2 = m * a1

    if xd > yd:
        return xm + a1*x1, ym + a2*y1
    else:
        return xm + a2*x1, ym + a1*y1


def create_microdesktop(t, scl, part):
    b = union()

    if part == PCB1:
        se = pcb1(scl)
        m = translate(v=[(indent*2-200)*scl, (-20+boxthick-100)*scl,0]).add(se)
        b.add(m)

    elif part == FRONT_PLATE:

        gap = 4
        se = create_front(scl, gap)
        m = translate(v=[22.7+indent*scl, (-9.5+boxthick*scl), 13.6]).add(se)
        b.add(m)

    elif part == LAYER0:

        gap = 4
        se = create_layer(scl, 0, TOP|BOTTOM, gap)
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

    elif part == LAYER1_TOP:

        gap = 4
        se = create_layer(scl, 1, TOP|BOTTOM, gap)
        m = translate(v=[19+indent*scl, -9.5, 13.6]).add(se)
        b.add(m)

    elif part == LAYER2_TOP:

        offs = 3
        gap = 4
        se = create_layer(scl, 2, TOP, gap)
        m = translate(v=[19+indent*scl, -9.5, 13.6+offs]).add(se)
        b.add(m)

    elif part == LAYER2_BOT:

        offs = 3
        gap = 4
        se = create_layer(scl, 2, BOTTOM, gap)
        m = translate(v=[19+indent*scl, -9.5, 13.6+offs]).add(se)
        b.add(m)

    elif part == LAYER3_TOP:

        offs = 6
        gap = 4
        se = create_layer(scl, 3, TOP, gap)
        m = translate(v=[19+indent*scl, -9.5, 13.6+offs]).add(se)
        b.add(m)

    elif part == LAYER3_BOT:

        offs = 6
        gap = 4
        se = create_layer(scl, 3, BOTTOM, gap)
        m = translate(v=[19+indent*scl, -9.5, 13.6+offs]).add(se)
        b.add(m)

    elif part == LAYER4_TOP:

        offs = 9
        gap = 4
        se = create_layer(scl, 4, TOP|BOTTOM, gap)
        m = translate(v=[19+indent*scl, -9.5, 13.6+offs]).add(se)
        b.add(m)

    elif part == LAYER5_TOP:

        offs = 12
        gap = 4
        se = create_layer(scl, 5, TOP|BOTTOM, gap)
        m = translate(v=[19+indent*scl, -9.5, 13.6+offs]).add(se)
        b.add(m)

    elif part == LAYER6:

        offs = 15
        gap = 4
        se = create_layer(scl, 0, TOP|BOTTOM, gap)
        m = translate(v=[19+indent*scl, -9.5, 13.6+offs]).add(se)
        b.add(m)

    t.add(b)


if __name__ == '__main__':

    u = union()
    for i in [
                PCB1,
                #LAYER0,
                CORNER1,
                CORNER2,
                CORNER3,
                CORNER4,
                #LAYER6,
                FRONT_PLATE,
            ]:
        t = union()
        create_microdesktop(t, scl, part=i)
        r = union().add(t)
        if i == -1:
            c = [0.8, 0.8, 0.3, 0.25]
        elif i == PCB1: # pcb1
            c = [0.8, 0.3, 0.8, 0.5]
        elif i == -3: # pcb2
            c = [0.3, 0.8, 0.3, 0.25]
        elif i == -4: # pcb3
            c = [0.1, 0.8, 0.3, 0.25]
        #elif i == CASE_CLASP: # pcb1
            #c = [0.3, 0.8, 0.3, 0.2]
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
