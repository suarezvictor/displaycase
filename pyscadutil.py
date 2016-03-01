# Copyright (C) 2014, 2015 Luke Kenneth Casson Leighton <lkcl@lkcl.net>
# License: GPLv3+

import time
import itertools
from pyopenscad import *
from polysurface import spline_double_divide, Offset, SurfaceFromCurves
from copy import deepcopy

B0 = 1
B45 = 2

def pin(spec, scl, r=0, fill=True, ht=1.8):
    if spec == B0 or spec == B45:
        c = union()
        h = cube([90*scl, ht*scl, (90)*scl], center=True)
        c += h
        if not fill:
            h = cube([65*scl, (ht+1)*scl, (65)*scl], center=True)
            c -= h
    if spec == B45:
        c = rotate([0, 45, 0]).add(c)
    if r == 1:
        c = rotate([90,0,0]).add(c)
    c = translate([0*scl, (-ht/2+3)*scl, 0]).add(c)
    return c
        
def shearedcube(size, center=False, shear=None, innershear=None):
    v = size
    points = [
    [ 0.5,  0.5,  0.5],
    [ 0.5,  0.5, -0.5],
    [ 0.5, -0.5,  0.5],
    [ 0.5, -0.5, -0.5],
    [-0.5,  0.5,  0.5],
    [-0.5,  0.5, -0.5],
    [-0.5, -0.5,  0.5],
    [-0.5, -0.5, -0.5]];
    faces = [
    [ 4 , 5, 1, 0],
    [ 2 , 6, 4, 0],
    [ 1 , 3, 2, 0],
    [ 6 , 2, 3, 7],
    [ 5 , 4, 6, 7],
    [ 3 , 1, 5, 7]];

    for i in range(len(points)):
        for j in range(len(v)):
            if not center:
                points[i][j] += 0.5
            points[i][j] *= v[j]
    if innershear is None:
        innershear = shear
    if shear:
        points[0][0] += shear[0]
        points[2][0] += shear[0]

        points[0][1] += shear[1]
        points[4][1] += shear[1]

        points[4][0] += innershear[0]
        points[6][0] += innershear[0]

        points[2][1] += innershear[1]
        points[6][1] += innershear[1]
    return polyhedron(points, faces)

L=0x1
R=0x2
T=0x4
D=0x8
F=0x10
B=0x20

def curvebox(scl, l, w, ht, rad):
    """ hollowbox has some bugs (not proper overlaps leaving gaps
        between sections.  it therefore can't be used for "subtract".
        this function can create a cube with 4 curved corners
    """
    u = union()
    c = cylinder( r=rad*scl, h=ht*scl,
                  segments=100, center=True)
    t = translate([rad*scl, rad*scl, ht/2.0*scl]).add(c)
    u += t
    t = translate([(l-rad)*scl, rad*scl, ht/2.0*scl]).add(c)
    u += t
    t = translate([(l-rad)*scl, (w-rad)*scl, ht/2.0*scl]).add(c)
    u += t
    t = translate([(rad)*scl, (w-rad)*scl, ht/2.0*scl]).add(c)
    u += t

    c = cube([(l-rad*2)*scl, w*scl, ht*scl])
    t = translate([(rad)*scl, (0)*scl, 0*scl]).add(c)
    u += t
    c = cube([l*scl, (w-rad*2.0)*scl, ht*scl])
    t = translate([(0)*scl, (rad)*scl, 0*scl]).add(c)
    u += t

    return u
    
def box_edge_xform(scl, r, spec, w, h, d, r12):
    r = rotate([0, -90, 90]).add(r)
    rangy = {T|B: 90, D|B: 180, D|F: -90, T|F: 0}
    r = rotate([0, rangy[spec], 90]).add(r)
    tx = w
    ty = r12 if (spec & B) else (d-r12)
    tz = (h-r12) if (spec & D) else r12
    t = translate(v=[tx*scl, ty*scl, tz*scl])
    t.add(r)
    return t

def box_edge_xform2(scl, r, spec, w, h, d, r12, resize1=0, resize2=0):
    r = rotate([0, -90, 90]).add(r)
    rangy = {T|L: 90, D|L: 180, D|R: -90, T|R: 0}
    r = rotate([0, rangy[spec], 0]).add(r)
    if resize2 == 0:
        resize2 = r12
    tx = resize2 if (spec & L) else (w-resize2)
    ty = 0
    if resize1 == 0:
        resize1 = r12
    tz = (h-resize1) if (spec & D) else resize1
    t = translate(v=[tx*scl, ty*scl, tz*scl])
    t.add(r)
    return t

def box_edge_xform3(scl, r, spec, w, h, d, r12):
    r = rotate([0, -90, 90]).add(r)
    rangz = {F|R: 90, F|L: 180, B|L: -90, B|R: 0}
    r = rotate([-90, 0, rangz[spec]]).add(r)
    tx = r12 if (spec & L) else (w-r12)
    ty = (d-r12) if (spec & F) else r12
    tz = h
    t = translate(v=[tx*scl, ty*scl, tz*scl])
    t.add(r)
    return t

def hollowbox(scl, w, d, h, thick=0.0, curverads=None, scalecurve=None):
    """ note: in 3-corner mode, make sure that the radii of the
        edge curves are the same, esp. on the outside.
    """
    if curverads is None:
        curverads = {}
    if scalecurve is None:
        scalecurve = {}
    if isinstance(thick, float):
        thick = {L:thick, R:thick, T:thick, D:thick,
                 F:thick, B:thick}
    v = union()
    c = cube([w*scl, d*scl, h*scl])
    v.add(c)

    if thick.values() != [0.0] * 6:
        w1 = w - thick.get(L, 0.0) - thick.get(R, 0.0)
        d1 = d - thick.get(F, 0.0) - thick.get(B, 0.0)
        h1 = h - thick.get(T, 0.0) - thick.get(D, 0.0)
        c = cube([w1*scl, d1*scl, h1*scl])
        c = translate(v=[thick.get(L, 0.0)*scl,
                         thick.get(B, 0.0)*scl,
                         thick.get(T, 0.0)*scl]).add(c)
        v -= c

    il = {T|L|F:[], T|R|F:[], D|L|F:[], D|R|F:[],
          T|L|B:[], T|R|B:[], D|L|B:[], D|R|B:[]}
    a = []
    su = []
    for spec in [T|B, D|B, D|F, T|F,
                 T|L, T|R, D|L, D|R,
                 F|L, B|L, F|R, B|R]:
        rad1, rad2 = curverads.get(spec, (0.0, 0.0))
        resize1, resize2 = scalecurve.get(spec, (0.0, 0.0))
        r12 = rad1+rad2
        if rad1 == 0.0:
            continue
        #print hex(spec), hex(~spec), hex(R|L), hex((~spec) & (R|L))
        xaxis = spec in [T|B, D|B, D|F, T|F]
        yaxis = spec in [T|L, T|R, D|L, D|R]
        zaxis = spec in [F|L, B|L, F|R, B|R]
        sx = resize2 or r12
        if xaxis:
            s = cube([(w+2)*scl, (r12+1)*scl, (r12+1)*scl])
        elif yaxis:
            s = cube([(sx+1)*scl, (d+2)*scl, (r12+1)*scl])
        else:
            s = cube([(r12+1)*scl, (r12+1)*scl, (h+2)*scl])
        tx = -1.0 if xaxis or (spec & L) else (w+1-sx)
        ty = -1.0 if yaxis or (spec & B) else (d+1-r12)
        tz = -1.0 if zaxis or not (spec & D) else (h+1-r12)
        s = translate(v=[tx*scl, ty*scl, tz*scl]).add(s)

        su.append(s)
        r = union()
        if xaxis:
            r = touch_arc(rad2, w, rad1, 0, scl)
            t = box_edge_xform(scl, r, spec, w, h, d, r12)
        elif yaxis:
            r = touch_arc(rad2, d, rad1, 0, scl)
            if resize1 or resize2:
                if spec == L|D or spec == R|T:
                    r = resize([resize1*scl, resize2*scl, 0], False).add(r)
                if spec == R|D or spec == L|T:
                    r = resize([resize2*scl, resize1*scl, 0], False).add(r)
            t = box_edge_xform2(scl, r, spec, w, h, d, r12, resize1, resize2)
        else:
            r = touch_arc(rad2, h, rad1, 0, scl)
            t = box_edge_xform3(scl, r, spec, w, h, d, r12)

        a.append(t)
        r1 = union()
        if xaxis:
            r1 = touch_arc(0, w, r12, 0, scl)
            t1 = box_edge_xform(scl, r1, spec, w, h, d, r12)
        elif yaxis:
            r1 = touch_arc(0, d, r12, 0, scl)
            t1 = box_edge_xform2(scl, r1, spec, w, h, d, r12)
        else:
            r1 = touch_arc(0, h, r12, 0, scl)
            t1 = box_edge_xform3(scl, r1, spec, w, h, d, r12)

        for k in il.keys():
            if spec & k == spec:
                il[k].append((su, t, t1))

    # remove bits from the cube
    for i in range(len(a)):
        v -= su[i]

    # for each curve-part remove all other bits then add the remainder,
    # don't worry about bits that don't overlap, just remove them all
    for i in range(len(a)):
        cp = union()
        cp.add(a[i])
        for j in range(len(a)):
            if i == j:
                continue # don't remove the part we just added!
            cp -= su[j]
        v += cp

    # now we work out the intersection of all corners, using the
    # intersection list (il)

    for itl in il.values():
        if len(itl) < 2:
            continue
        #cp = intersection()
        #for i in itl:
        #    cp.add(i[1])
        #v += cp
        for i in range(len(itl)):
            cp = intersection()
            cp.add(itl[i][2])
            for j in range(len(itl)):
                if i == j:
                    continue
                cp.add(itl[j][1])
            v += cp

    return v

def touch_arc(rad, ht, bwid, iro, scl, roffs=0, roffsinner=0, angle=0.0,
                    shear=0):
    rad2 = bwid+rad
    rad -= iro
    rad_r = rad
    rad2_r = rad2
    rad2 += roffsinner
    rad += roffs

    r = union()
    c = cylinder( r=rad2*scl, r1=rad2_r*scl, h=ht*scl,
                  segments=100, center=True)
    z = cylinder( r=rad*scl, r1=rad_r*scl, h=(ht+5.0)*scl,
                   segments=100, center=True)
    z = translate(v=[0*scl,0*scl,-2.0*scl]).add(z)
    c -= z
    cb = cube(size=[rad2*scl*2.2,2.2*rad2*scl,2.0*(ht)*scl])
    ct = translate(v=[0*scl,-rad2*scl,-ht*scl])
    ct.add(cb)
    c -= ct
    cb = shearedcube(size=[(rad2*2.0)*scl,(rad2+1.0)*scl,(ht+5.0)*scl],
            shear=[shear*scl, 0, 0],
            innershear=[0*scl, 0, 0])
    cb = rotate([0, 0, -90]).add(cb)
    cb = translate(v=[0*scl,(rad2*2.0+shear/2.0)*scl,0]).add(cb)
    #cb = cube(size=[2.2*rad2*scl,rad2*2*scl,2*(ht)*scl])
    ct = translate(v=[-(rad2+0.5)*scl,-0*scl,-(ht/2.0+1)*scl])
    ct.add(cb)
    c -= ct
    if angle != 0.0:
        cb = shearedcube(size=[(rad2*2.0)*scl,(rad2+1.0)*scl,(ht+5.0)*scl],
                shear=[shear*scl, 0, 0],
                innershear=[0*scl, 0, 0])
        cb = rotate([0, 0, -90]).add(cb)
        cb = translate(v=[0*scl,(rad2*2.0+shear/2.0)*scl,0]).add(cb)
        t = rotate([0, 0, 270-angle]).add(cb)
        ct = translate(v=[0*scl,0*scl,-(ht/2.0+1)*scl]).add(t)
        c -= ct
    r.add(c)
    t = translate(v=[0,0,-ht/2.0*scl+0*scl])
    t.add(r)
    return t

