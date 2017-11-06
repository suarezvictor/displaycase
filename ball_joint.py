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
num_ridges = 4
symmetrical_ridges = True

BALL = 1
SOCKET     = 2
SOCKETCLAMP     = 3
JOINER     = 4
ROD     = 5
LONGROD     = 6
JOINERBOTTOM = 7

def create_joiner(screw=False):

    v = union()

    d = difference()

    c = curvebox(1.0, 15,15,4.8, 2.5, center=True)
    c = rotate([90, 0, 0]).add(c)
    d.add(translate([0,2.70,0]).add(c))

    # screw-hole
    c = cylinder(r=1.75, h=20, segments=20, center=True)
    c = rotate([90, 0, 0]).add(c)
    d.add(translate([0,0,0]).add(c))

    # nut head
    if screw:
        c = cylinder(r=3.4, h=3.0, segments=20, center=True)
    else:
        c = cylinder(r=3.3, h=5.0, segments=6, center=True)
    c = rotate([90, 0, 0]).add(c)
    d.add(translate([0,5,0]).add(c))

    v.add(d)

    # problem with printing, undersupport screwhole
    c = cylinder(r=1.60, h=2.0, segments=20, center=True)
    c = rotate([90, 0, 0]).add(c)
    v.add(translate([0,4.10,0]).add(c))

    c = union()
    c.add(cylinder(r=2.15, h=6, center=True, segments=30))
    c.add(cylinder(r=2.15, h=6, center=True, segments=30))
    a = cylinder(r=2.5, h=3.5, center=True, segments=30)
    a = translate([0,0,-1.3]).add(a)
    c.add(a)
    a = translate([0,0,4.3]).add(a)
    c.add(a)

    d.add(translate([0,0,5.7]).add(c))
    c = rotate([0, 180, 0]).add(c)
    d.add(translate([0,0,-5.7]).add(c))
    c = rotate([0, -90, 0]).add(c)
    d.add(translate([5.7,0,0]).add(c))
    c = rotate([0, 180, 0]).add(c)
    d.add(translate([-5.7,0,0]).add(c))
    d.add(translate([-5.7,0,7.7]).add(c))
    d.add(translate([-5.7,0,-7.7]).add(c))
    c = rotate([0, 180, 0]).add(c)
    d.add(translate([5.7,0,-7.7]).add(c))
    d.add(translate([5.7,0,7.7]).add(c))

    return v

def socketbox():

    d = difference()

    c = curvebox(1.0, 10.8,9,16.5, 2.5, center=True)
    d.add(translate([0,0.5,5.2]).add(c))
    c = cube([12,12,17.5], center=True)
    d.add(translate([0,-5.8,5.2]).add(c))

    t = difference()
    t.add(cube([12,12,12], center=True))
    c = cylinder(r=4.8, h=15, center=True, segments=30)
    c = rotate([0, 90, 0]).add(c)
    t.add(translate([0,-6,6]).add(c))

    d.add(translate([0,6.8,-5.2]).add(t))
    t = rotate([0, 180, 0]).add(t)
    d.add(translate([0,6.8,4.9+10.4]).add(t))

    c = union()
    c.add(cylinder(r=2.15, h=20, segments=30))
    c.add(cylinder(r=2.7, h=5, segments=30))
    c = rotate([0, 90, 0]).add(c)
    d.add(translate([-0.1,0,8.7]).add(c))
    c = rotate([0, 180, 0]).add(c)
    d.add(translate([0.1,0,8.7]).add(c))

    return d

boltoffset = 5.6

def create_socketclamp():

    v = union()

    d = socketbox()

    if use_sphere:
        c = sphere(r=4.2, segments=30)
    else:
        c = cylinder(r=4.2, h=7.8, center=True, segments=30)
        c = rotate([0, 90, 0]).add(c)
    d.add(c)

    c = cylinder(r=1.4, h=20, segments=20, center=True)
    c = rotate([90, 0, 0]).add(c)
    d.add(translate([0,0,boltoffset]).add(c))

    c = cylinder(r=2.9, h=5, segments=6, center=True)
    c = rotate([90, 0, 0]).add(c)
    d.add(translate([0,5.2,boltoffset]).add(c))

    c = cube([5.2,8,15], center=True)
    c = rotate([90, 0, 0]).add(c)
    d.add(translate([0,0,-1.6]).add(c))

    v.add(d)

    # problem with printing, undersupport screwhole
    c = cylinder(r=1.40, h=2.0, segments=20, center=True)
    c = rotate([90, 0, 0]).add(c)
    v.add(translate([0,4.00,boltoffset]).add(c))

    c = cylinder(r=2.7, h=20, segments=30)
    d.add(translate([0,0,6.5]).add(c))

    return v

def add_column(loffs=0):

    t = union()

    c = cylinder(r=2.1, h=4.5+num_ridges*2-loffs, segments=30)
    t.add(c)

    for i in range(num_ridges):
        if symmetrical_ridges:
            c = cylinder(r=2.4, h=1, segments=30)
        else:
            c = cylinder(r=3.1, h=1, segments=30)
            c = resize([0,3,0]).add(c)
        c = translate([0,0,5.5+i*2-loffs]).add(c)
        t.add(c)

    return t


def create_rod(loffs=3):

    v = union()

    c = add_column(loffs)
    v.add(translate([0,0,-3]).add(c))
    c = rotate([180, 0, 0]).add(c)
    v.add(translate([0,0,3]).add(c))

    return v

def create_socket():

    v = union()

    d = socketbox()

    if use_sphere:
        c = sphere(r=4.2, segments=30)
    else:
        c = cylinder(r=4.2, h=7.8, center=True, segments=30)
        c = rotate([0, 90, 0]).add(c)
    d.add(c)

    c = cylinder(r=3.5, h=4, segments=20, center=True)
    c = rotate([90, 0, 0]).add(c)
    d.add(translate([0,5,boltoffset]).add(c))

    c = cylinder(r=1.75, h=20, segments=20, center=True)
    c = rotate([90, 0, 0]).add(c)
    d.add(translate([0,0,boltoffset]).add(c))

    v.add(d)

    # problem with printing, undersupport screwhole
    c = cylinder(r=1.60, h=2.0, segments=20, center=True)
    c = rotate([90, 0, 0]).add(c)
    v.add(translate([0,4.00,boltoffset]).add(c))

    # bit more undersupport
    c = cube([0.6, 2.5, 2*num_ridges-0.1])
    v.add(translate([-1.2,2.5,boltoffset+9]).add(c))
    v.add(translate([1.2-0.6,2.5,boltoffset+9]).add(c))

    v.add(translate([0,0,11.25]).add(add_column(1.25)))
    v.add(translate([0,0,11.5]).add(cube([2.0,3.5,2], center=True)))

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

    elif part == JOINERBOTTOM:

        se = create_joiner(screw=True)
        se = rotate([0, 0, 180]).add(se)
        m = translate(v=[0,0,7.6 + num_ridges*2]).add(se)
        b.add(m)

    elif part == JOINER:

        se = create_joiner()
        se = rotate([180, 0, 180]).add(se)
        m = translate(v=[0,0,7.6 + num_ridges*2]).add(se)
        b.add(m)

    elif part == ROD:

        se = create_rod()
        se = rotate([90, 90, 90]).add(se)
        m = translate(v=[0,0,7.6 + num_ridges*2]).add(se)
        m = translate(v=[1.6 + num_ridges*2, 0, 0]).add(m)
        b.add(m)

    elif part == LONGROD:

        se = create_rod(0)

        se = rotate([90, 90, 90]).add(se)
        m = translate(v=[0,0,-8.7]).add(se)
        m = translate(v=[-3.2 - num_ridges*2, 0, 0]).add(m)
        b.add(m)

    t.add(rotate([90,0,0]).add(b))

def create_scad():
    u = union()
    for i in [
                BALL,
                #SOCKET,
                #SOCKETCLAMP,
                #JOINER,
                #JOINERBOTTOM,
                #ROD,
                #LONGROD,
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
        elif i in [JOINER, JOINERBOTTOM]:
            c = [0.2, 0.7, 0.3, 0.5]
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
