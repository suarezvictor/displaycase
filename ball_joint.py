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

BALL = 1
SOCKET     = 6
SOCKETCLAMP     = 11

def create_socketclamp():

    v = union()

    d = difference()

    c = cube([10,5,16.5], center=True)
    d.add(translate([0,3,5.2]).add(c))

    c = sphere(r=4.2, segments=30)
    d.add(c)

    c = cylinder(r=1.75, h=20, segments=20, center=True)
    c = rotate([90, 0, 0]).add(c)
    d.add(translate([0,0,8]).add(c))

    c = cylinder(r=3.5, h=3, segments=20, center=True)
    c = rotate([90, 0, 0]).add(c)
    d.add(translate([0,5,8]).add(c))

    c = cube([4.8,4,15], center=True)
    c = rotate([90, 0, 0]).add(c)
    d.add(translate([0,0,-1.8]).add(c))

    v.add(d)

    c = cylinder(r=2.7, h=20, segments=30)

    d.add(translate([0,0,10]).add(c))

    return v

def create_socket():

    v = union()

    d = difference()

    c = cube([10,5,16], center=True)
    d.add(translate([0,3,5.2]).add(c))

    c = sphere(r=4.2, segments=30)
    d.add(c)

    c = cylinder(r=1.75, h=20, segments=20, center=True)
    c = rotate([90, 0, 0]).add(c)
    d.add(translate([0,0,8]).add(c))

    v.add(d)

    t = union()

    c = cylinder(r=2.5, h=20, segments=30)
    t.add(c)

    for i in range(7):
        c = cylinder(r=3.5, h=1, segments=30)
        c = resize([0,4,0]).add(c)
        c = translate([0,0,5+i*2]).add(c)
        t.add(c)

    v.add(translate([0,0,10]).add(t))

    return v

def create_ball():

    t = union()

    c = sphere(r=4, segments=30)
    t.add(c)
    c = cylinder(r=2.5, h=20, segments=30)
    t.add(c)

    for i in range(7):
        c = cylinder(r=3.5, h=1, segments=30)
        c = resize([4,0,0]).add(c)
        c = translate([0,0,5+i*2]).add(c)
        t.add(c)

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

    t.add(rotate([90,0,0]).add(b))

def create_scad():
    u = union()
    for i in [
                #BALL,
                #SOCKET,
                SOCKETCLAMP,
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
