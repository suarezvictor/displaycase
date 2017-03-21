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

def pcb1(scl):

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


def create_microdesktop(t, scl, part):
    b = union()

    if part == PCB1:
        se = pcb1(scl)
        m = translate(v=[0, -20*scl,0]).add(se)
        b.add(m)

    t.add(b)


if __name__ == '__main__':

    u = union()
    for i in [
                PCB1,
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
