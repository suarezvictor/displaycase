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

scl = 1.0

MALE = 1
FEMALE     = 2
FEMALE2     = 3

def create_male():

    t = difference()

    d = union()
    c = cube([20, 12, 5], center=True)
    d.add(c)
    c = union()
    e = cube([5, 10, 15], center=True)
    e = translate([0,0,2]).add(e)
    c.add(e)
    e = cylinder(r=5, h=5, center=True)
    e = rotate([0, 90, 0]).add(e)
    e = translate([0,0,-5]).add(e)
    c.add(e)
    d.add(translate([-7.5, 0, -7]).add(c))
    d.add(translate([7.5, 0, -7]).add(c))

    t.add(d)
    c = cylinder(r=1.6, h=25, center=True, segments=20)
    t.add(c)
    c = rotate([0, 90, 0]).add(c)
    c = translate([0,0,-12]).add(c)
    t.add(c)
    c = cylinder(r=4, h=4, center=True, segments=20)
    c = rotate([0, 0, 30]).add(c)
    c = translate([0,0,-3]).add(c)
    t.add(c)

    return t

def create_female(rot=90):

    t = difference()

    d = union()
    c = cube([28, 18, 5], center=True)
    c = rotate([0, 0, rot]).add(c)
    d.add(c)
    c = union()
    e = cube([9.9, 10, 15], center=True)
    e = translate([0,0,2]).add(e)
    c.add(e)
    e = cylinder(r=5, h=9.9, center=True)
    e = rotate([0, 90, 0]).add(e)
    e = translate([0,0,-5]).add(e)
    c.add(e)
    d.add(translate([0, 0, -7]).add(c))

    t.add(d)

    c = cylinder(r=1.6, h=25, center=True, segments=20)
    c = rotate([0, 90, 0]).add(c)
    c = translate([0,0,-12]).add(c)
    t.add(c)

    e = union()
    c = cylinder(r=1.6, h=25, center=True, segments=20)
    e.add(c)
    c = cylinder(r=6.5/2, h=4, center=True, segments=20)
    c = translate([0,0,-3]).add(c)
    e.add(c)

    a = translate([10.5,0,0]).add(e)
    a = rotate([0, 0, rot]).add(a)
    t.add(a)
    a = rotate([0, 0, 180]).add(a)
    t.add(a)

    return t

def create_bracket(t, part):
    b = union()

    if part == MALE:
        se = create_male()
        m = translate(v=[0,0,0]).add(se)
        b.add(m)

    elif part == FEMALE2:

        se = create_female()
        se = rotate([-90, 0, 0]).add(se)
        m = translate(v=[0,12,-12]).add(se)
        b.add(m)

    elif part == FEMALE:

        se = create_female(rot=0)
        se = rotate([90, 0, 0]).add(se)
        m = translate(v=[0,-12,-12]).add(se)
        b.add(m)

    t.add(rotate([90,0,0]).add(b))

def create_scad():
    u = union()
    for i in [
                MALE,
                FEMALE,
                FEMALE2,
            ]:
        t = union()
        create_bracket(t, i)
        r = union().add(t)
        if i == -1:
            c = [0.8, 0.8, 0.3, 0.25]
        elif i == MALE: # pcb1
            c = [0.8, 0.3, 0.8, 0.5]
        elif i in [FEMALE]:
            c = [0.9, 0.3, 0.3, 0.5]
        elif i in [FEMALE2]:
            c = [0.3, 0.3, 0.9, 0.5]
        c = color(c)
        c.add(r)
        u.add(c)


    scad_render_to_file(u, "bracket_prog2.scad")
    f = open("bracket_model2.scad", "w")
    f.write("""include<bracket_prog2.scad>;
    """)
    f.close()

if __name__ == '__main__':
    create_scad()
