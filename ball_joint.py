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
use_sphere = True
num_ridges = 3
symmetrical_ridges = True

BALL = 1
SOCKET     = 2
SOCKETCLAMP     = 3
JOINER     = 4

def create_joiner():

    v = union()

    d = difference()

    c = curvebox(1.0, 15,15,4.5, 2.5, center=True)
    c = rotate([90, 0, 0]).add(c)
    d.add(translate([0,2.6,0]).add(c))

    c = cylinder(r=1.75, h=20, segments=20, center=True)
    c = rotate([90, 0, 0]).add(c)
    d.add(translate([0,0,0]).add(c))

    c = cylinder(r=4.5, h=5, segments=20, center=True)
    c = rotate([90, 0, 0]).add(c)
    d.add(translate([0,5,0]).add(c))

    v.add(d)

    c = cylinder(r=2.7, h=6, center=True, segments=30)

    d.add(translate([0,0,6]).add(c))
    d.add(translate([0,0,-6]).add(c))
    c = rotate([0, 90, 0]).add(c)
    d.add(translate([6,0,0]).add(c))
    d.add(translate([-6,0,0]).add(c))

    return v

def socketbox():

    d = difference()

    c = curvebox(1.0, 10,9,16.5, 2.5, center=True)
    d.add(translate([0,0.5,5.2]).add(c))
    c = cube([11,12,17.5], center=True)
    d.add(translate([0,-5.8,5.2]).add(c))

    return d

def create_socketclamp():

    v = union()

    d = socketbox()

    if use_sphere:
        c = sphere(r=4.2, segments=30)
    else:
        c = cylinder(r=4.2, h=7.8, center=True, segments=30)
        c = rotate([0, 90, 0]).add(c)
    d.add(c)

    c = cylinder(r=1.75, h=20, segments=20, center=True)
    c = rotate([90, 0, 0]).add(c)
    d.add(translate([0,0,8]).add(c))

    c = cylinder(r=3.5, h=5, segments=20, center=True)
    c = rotate([90, 0, 0]).add(c)
    d.add(translate([0,5,8]).add(c))

    c = cube([5.2,8,15], center=True)
    c = rotate([90, 0, 0]).add(c)
    d.add(translate([0,0,-1.8]).add(c))

    v.add(d)

    c = cylinder(r=2.7, h=20, segments=30)

    d.add(translate([0,0,10]).add(c))

    return v

def add_column():

    t = union()

    c = cylinder(r=2.1, h=6+num_ridges*2, segments=30)
    t.add(c)

    for i in range(num_ridges):
        if symmetrical_ridges:
            c = cylinder(r=2.4, h=1, segments=30)
        else:
            c = cylinder(r=3.1, h=1, segments=30)
            c = resize([0,3,0]).add(c)
        c = translate([0,0,7+i*2]).add(c)
        t.add(c)

    return t


def create_socket():

    v = union()

    d = difference()

    c = curvebox(1.0, 10,9,16.5, 2.5, center=True)
    d.add(translate([0,0.5,5.2]).add(c))
    c = cube([11,12,17.5], center=True)
    d.add(translate([0,-5.7,5.2]).add(c))

    if use_sphere:
        c = sphere(r=4.2, segments=30)
    else:
        c = cylinder(r=4.2, h=7.8, center=True, segments=30)
        c = rotate([0, 90, 0]).add(c)
    d.add(c)

    c = cylinder(r=3.5, h=4, segments=20, center=True)
    c = rotate([90, 0, 0]).add(c)
    d.add(translate([0,5,8]).add(c))

    c = cylinder(r=1.75, h=20, segments=20, center=True)
    c = rotate([90, 0, 0]).add(c)
    d.add(translate([0,0,8]).add(c))

    v.add(d)

    v.add(translate([0,0,10]).add(add_column()))

    return v

def create_ball():

    t = union()

    if use_sphere:
        c = sphere(r=4.0, segments=30)
    else:
        c = cylinder(r=4, h=7.5, segments=30, center=True)
        c = rotate([0, 90, 0]).add(c)
    t.add(c)

    t.add(add_column())

    return t

def create_ball_joint(t, part):
    b = union()

    if part == BALL:
        se = create_ball()
        m = translate(v=[0,0,0]).add(se)
        b.add(m)

    elif part == SOCKET:

        se = create_socket()
        se = rotate([180, 0, 0]).add(se)
        m = translate(v=[0,0,0]).add(se)
        b.add(m)

    elif part == SOCKETCLAMP:

        se = create_socketclamp()
        se = rotate([180, 0, 180]).add(se)
        m = translate(v=[0,0,0]).add(se)
        b.add(m)

    elif part == JOINER:

        se = create_joiner()
        se = rotate([180, 0, 180]).add(se)
        m = translate(v=[0,0,9.1 + num_ridges*2]).add(se)
        b.add(m)

    t.add(rotate([90,0,0]).add(b))

def create_scad():
    u = union()
    for i in [
                BALL,
                SOCKET,
                SOCKETCLAMP,
                JOINER,
            ]:
        t = union()
        create_ball_joint(t, i)
        r = union().add(t)
        if i == -1:
            c = [0.8, 0.8, 0.3, 0.25]
        elif i == BALL: # pcb1
            c = [0.8, 0.3, 0.8, 0.5]
        elif i in [SOCKET]:
            c = [0.9, 0.3, 0.3, 0.5]
        else:
            c = [0.3, 0.5, 0.8, 0.5]
        c = color(c)
        c.add(r)
        u.add(c)


    scad_render_to_file(u, "ball_joint_prog2.scad")
    f = open("ball_joint_model2.scad", "w")
    f.write("""include<ball_joint_prog2.scad>;
    """)
    f.close()

if __name__ == '__main__':
    create_scad()
    #create_topbot_grouped()
    #create_sides_grouped()
