# Copyright (C) 2014, 2015 Luke Kenneth Casson Leighton <lkcl@lkcl.net>
# License: GPLv3+

import time
import itertools
from pyopenscad import *
from polysurface import spline_double_divide, Offset, SurfaceFromCurves
from copy import deepcopy

# set this to add in some side-supports that help stabilise the parts
# as they are being printed.  the parts are quite narrow and tall, so
# tend to come unstuck.
pin_parts_3d=False

test = True


if not test:
    lcd_l = 3598.0
    lcd_w = 2100.0
    lcd_la = lcd_l-98.0
    lcd_wa = lcd_w-129.9
    lcd_d = 50
else:
    # HSD070PWW1
    lcd_l = 1612
    lcd_w = 1055
    # HSD101PWW1
    #lcd_l = 2294.6
    #lcd_w = 1492.0
    lcd_la = lcd_l-104.8+40
    lcd_wa = lcd_w-113.0+40
    lcd_d = 50

bwid = 17 # 24
lcd_inset_top = 25
lcd_inset_bot = 200
lcd_gap = 3
lcd_hinge_inner_rad=70
lcd_hinge_inside_rad=70
lcd_ext_rot_angle=250
lcd_outer_rad = lcd_hinge_inner_rad+bwid
lcd_end_ht = 20 # 40

screwrad = 30 / 2.0
boxheight = 140
boxtopoffs = 2
boxinset = 55
hinge_depth = 130
hole_depth = 80
boxlength = lcd_w + lcd_inset_top + lcd_inset_bot + lcd_d-20

bdep = 310
ethdep = 160

def hinge_translate(scl):
    return translate(v=[+(+lcd_inset_bot+lcd_w+63-lcd_gap)*scl,
                       0,
                        (30-lcd_d+lcd_hinge_inner_rad)*scl])

def hinge_rotate(scl, o, angle):
    u = union()
    t = hinge_translate(-scl).add(o)
    t = rotate([0, -angle, 0]).add(t)
    t = hinge_translate(scl).add(t)
    return t

hinge_x = -20
hinge_y = -20

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
    if shear:
        if innershear is None:
            innershear = shear
        for i in range(len(points)/4):
            for j in range(len(v)):
                points[i*2][j] += shear[j]
                points[i*2+4][j] += innershear[j]
    return polyhedron(points, faces)

L=0x1
R=0x2
T=0x4
D=0x8
F=0x10
B=0x20

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

def box_edge_xform2(scl, r, spec, w, h, d, r12):
    r = rotate([0, -90, 90]).add(r)
    rangy = {T|L: 90, D|L: 180, D|R: -90, T|R: 0}
    r = rotate([0, rangy[spec], 0]).add(r)
    tx = r12 if (spec & L) else (w-r12)
    ty = 0
    tz = (h-r12) if (spec & D) else r12
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

def hollowbox(scl, w, d, h, thick=0.0, curverads=None):
    """ note: in 3-corner mode, make sure that the radii of the
        edge curves are the same, esp. on the outside.
    """
    if curverads is None:
        curverads = {}
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
        r12 = rad1+rad2
        if rad1 == 0.0:
            continue
        print hex(spec), hex(~spec), hex(R|L), hex((~spec) & (R|L))
        xaxis = spec in [T|B, D|B, D|F, T|F]
        yaxis = spec in [T|L, T|R, D|L, D|R]
        zaxis = spec in [F|L, B|L, F|R, B|R]
        if xaxis:
            s = cube([(w+2)*scl, (r12+1)*scl, (r12+1)*scl])
        elif yaxis:
            s = cube([(r12+1)*scl, (d+2)*scl, (r12+1)*scl])
        else:
            s = cube([(r12+1)*scl, (r12+1)*scl, (h+2)*scl])
        tx = -1.0 if xaxis or (spec & L) else (w+1-r12)
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
            t = box_edge_xform2(scl, r, spec, w, h, d, r12)
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

def touch_arc(rad, ht, bwid, iro, scl, roffs=0, roffsinner=0, angle=0.0):
    rad2 = bwid+rad
    rad -= iro
    rad_r = rad
    rad2_r = rad2
    rad2 += roffsinner
    rad += roffs

    r = union()
    c = cylinder( r=rad2*scl, r1=rad2_r*scl, h=ht*scl,
                  segments=50, center=True)
    c -= cylinder( r=rad*scl, r1=rad_r*scl, h=(ht+1)*scl,
                   segments=50, center=True)
    cb = cube(size=[rad2*scl*2.2,2.2*rad2*scl,2*(ht)*scl])
    ct = translate(v=[0*scl,-rad2*scl,-ht*scl])
    ct.add(cb)
    c -= ct
    cb = cube(size=[2.2*rad2*scl,rad2*2*scl,2*(ht)*scl])
    ct = translate(v=[-rad2*scl*1.1,-0*scl,-ht*scl])
    ct.add(cb)
    c -= ct
    if angle != 0.0:
        cb = cube(size=[rad2*scl*2.2,2.2*rad2*scl,2*(ht)*scl])
        #cb = translate(v=[0*scl,-rad2*scl,-ht*scl]).add(cb)
        t = rotate([0, 0, 270-angle]).add(cb)
        ct = translate(v=[0*scl,0*scl,-ht*scl]).add(t)
        c -= ct
    r.add(c)
    t = translate(v=[0,0,-ht/2*scl+0*scl])
    t.add(r)
    return t

def lcd_panel(scl, offs=0):

    w = lcd_w
    h = lcd_l
    d = lcd_d

    a = union()

    r = union()
    c = cube(size=[(w+offs*2)*scl,(h+offs*2)*scl,(d+offs*2)*scl])
    c = rotate([00, 0, 0 ]).add(c)
    r.add(c)
    t = translate(v=[(-93-offs)*scl, (-40-offs)*scl, (32.5-d-offs)*scl])
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

def case_bolthole(scl, end):
    bht = lcd_hinge_inner_rad+boxtopoffs-2.1-lcd_d
    print bht
    if end == 0:
        return translate([(29.0+54-lcd_d-lcd_inset_top+30)*scl, 0*scl, bht*scl])
    elif end == 1:
        return translate([(-10+lcd_w+11)*scl, 0*scl, bht*scl])
    elif end == 2:
        return translate([(lcd_w+lcd_inset_bot-95)*scl, 0*scl,
                            (-lcd_d+129+boxtopoffs-boxheight)*scl])
    elif end == 3:
        return translate([(-20+lcd_w/2+30)*scl, 0*scl, bht*scl])

def lid_bolthole(scl, end=True):
    if end:
        return translate([(-lcd_inset_top+56)*scl, 0*scl, (42-lcd_d)*scl])
    else:
        return translate([(95+lcd_w)*scl, 0*scl, (42-lcd_d)*scl])

def screen_mid3(scl, ht, hole_ht, nohinge=True, endpart=True):

    w = lcd_w+lcd_inset_top+lcd_inset_bot-200
    iro = 0
    shear = 0
    innershear = 0
    edge_inset = bwid
    a = union()

    # top edge
    toplen = w+lcd_gap*2
    toplenoffs = (-lcd_inset_top+w+65)
    r = union()
    c = shearedcube(size=[(bwid+iro)*scl,toplen*scl,ht*scl],
                shear=[-shear*scl, 0, 0],
                innershear=[-innershear*scl, 0, 0])
    c = rotate([0, 90, 90]).add(c)
    r.add(c)
    t = translate(v=[toplenoffs*scl, (16.5-ht)*scl, (30-lcd_d)*scl])
    t.add(r)
    a.add(t)

    a = translate(v=[0, (ht-edge_inset)*scl, 0]).add(a)
    a += screen_mid2(scl, ht, hole_ht)
    a += screen_mid1(scl, ht, hole_ht, nohinge=True, endpart=True)
    return a

def screen_mid2(scl, ht, hole_ht, nohinge=True, endpart=True,
                removemiddle=True):

    shear = 0
    innershear = 0
    w = lcd_w+lcd_inset_top+lcd_inset_bot
    edge_inset = bwid
    iro = 0

    rad = 15

    a = union()

    toplen = 180 if test else 250
    toplenoffs = (w-lcd_inset_top-10)

    # top and bottom edge
    a += screen_frontedge(scl, ht, toplen, toplenoffs, 
                               curvefront=False, curvetopback=True)

    # add hinge-end filler over top of screwhole
    r = union()
    c = shearedcube(size=[(lcd_d+lcd_gap*2)*scl,(lcd_gap*2+bwid)*scl,ht*scl],
                shear=[-shear*scl, 0, 0],
                innershear=[-innershear*scl, 0, 0])
    c = rotate([0, 90, 90]).add(c)
    r.add(c)
    t = translate(v=[(+lcd_inset_bot+lcd_w-100)*scl,
                        (16.5-ht)*scl, (30+lcd_gap)*scl])
    t.add(r)
    a.add(t)

    a.add(lid_bottom_boltholder(scl, lcd_gap, ht, iro))

    if removemiddle:
        # top edge
        r = union()
        c = shearedcube(size=[(bwid*3+iro)*scl,
                            (w-toplen-lcd_inset_top-lcd_inset_bot)*scl,
                            (ht+2)*scl],
                    shear=[-shear*scl, 0, 0],
                    innershear=[-innershear*scl, 0, 0])
        c = rotate([0, 90, 90]).add(c)
        r.add(c)
        t = translate(v=[(w-lcd_inset_bot-lcd_inset_top)*scl,
                        (16.5-ht-1)*scl, (-bwid)*scl])
        t.add(r)
        a -= t
    # screw holes through lid
    a -= lid_screwholes(scl, edge_inset)

    a = translate(v=[0, (ht-edge_inset)*scl, 0]).add(a)
    return a

def lid_bottom_boltholder(scl, lcd_gap, ht, iro):
    shear = 0
    innershear = 0

    a = union()

    # bottom edge bolt holder
    r = union()
    c = cylinder(r=29*scl, h=ht*scl, segments=50)
    c = rotate([0, 90, 90]).add(c)
    #r.add(c)
    t = translate(v=[(0)*scl, (16.5-ht)*scl, (0)*scl]).add(r)
    t = lid_bolthole(scl, end=False).add(t)
    a.add(t)
    r = union()
    c = shearedcube(size=[(bwid+5+iro)*scl,(50+lcd_gap*2)*scl,ht*scl],
                shear=[-shear*scl, 0, 0],
                innershear=[-innershear*scl, 0, 0])
    c = rotate([0, 90, 90]).add(c)
    r.add(c)
    t = translate(v=[(38)*scl, (16.5-ht)*scl, (-2)*scl]).add(r)
    t = lid_bolthole(scl, end=False).add(t)
    a.add(t)

    return a

def screen_frontedge(scl, ht, toplen, toplenoffs, 
                            curvefront=True, curvetopback=False):
    shear = 0
    innershear = 0
    edge_inset = bwid
    iro = 0

    rad = 15
    rad2 = 2
    a = union()

    if curvetopback:
        to = toplenoffs-40
    else:
        to = toplenoffs

    print "box", ht, to, lcd_d+40
    curverads={
               D|R:(bwid+5, 5),
               }
    if curvefront:
        curverads[L|T] = (bwid, bwid)
        curverads[L|D] = (bwid, 0)
        offs = 0
    else:
        to -= lcd_w
        offs = lcd_w
    if curvetopback:
        curverads[T|R] = (bwid+lcd_gap, bwid*2)
    c = hollowbox(scl, to+15, ht, lcd_d+35+lcd_gap*2,
                    {T:bwid, B: -1,
                    L:80, R:bwid+lcd_gap, F:-1, D:bwid},
                    curverads=curverads)
    c = translate(v=[(offs)*scl, (16.5-ht)*scl, (12-lcd_d-lcd_gap)*scl]).add(c)
    a.add(c)

    return a

def screen_mid1(scl, ht, hole_ht, nohinge=False, endpart=False):

    shear = 0
    innershear = 0
    w = lcd_w+lcd_inset_top+lcd_inset_bot
    edge_inset = bwid
    iro = 0

    rad = 15

    a = union()

    if endpart:
        toplen = 120 if test else 200
        toplenoffs = (toplen-131+165)

    else:
        toplen = w+lcd_gap*2
        toplenoffs = (-lcd_inset_top+w+65)

    # top and bottom edge
    a += screen_frontedge(scl, ht, toplen, toplenoffs, curvetopback=True)

    if not endpart:
        a.add(lid_bottom_boltholder(scl, lcd_gap, ht, iro))

    if endpart:
        # middle filler
        r = union()
        c = shearedcube(size=[(lcd_d+lcd_gap*2)*scl,toplen*scl,ht*scl],
                    shear=[-shear*scl, 0, 0],
                    innershear=[-innershear*scl, 0, 0])
        c = rotate([0, 90, 90]).add(c)
        r.add(c)
        t = translate(v=[toplenoffs*scl, (16.5-ht)*scl, (30+lcd_gap)*scl])
        t.add(r)
        a.add(t)

    if not endpart:
        # middle filler, doesn't fill up hinge part, allow cable access
        r = union()
        c = shearedcube(size=[(lcd_d+lcd_gap*2)*scl,
                        (w-lcd_inset_bot+lcd_gap*2)*scl,ht*scl],
                    shear=[-shear*scl, 0, 0],
                    innershear=[-innershear*scl, 0, 0])
        c = rotate([0, 90, 90]).add(c)
        r.add(c)
        t = translate(v=[(-lcd_inset_top-lcd_inset_bot+w+65)*scl,
                        (16.5-ht)*scl, (30+lcd_gap)*scl])
        t.add(r)
        a.add(t)

        # add hinge-end filler over top of screwhole
        r = union()
        c = shearedcube(size=[(lcd_d+lcd_gap*2)*scl,
                        (lcd_gap*2+bwid)*scl,ht*scl],
                    shear=[-shear*scl, 0, 0],
                    innershear=[-innershear*scl, 0, 0])
        c = rotate([0, 90, 90]).add(c)
        r.add(c)
        t = translate(v=[(+lcd_inset_bot+lcd_w-75)*scl, (16.5-ht)*scl,
                        (30+lcd_gap)*scl])
        t.add(r)
        a.add(t)

        # bottom end curve (1st)
        r = union()
        r = touch_arc(lcd_hinge_inner_rad, ht, bwid, 30, scl)
        r = rotate([180, 90, 90]).add(r)
        r = rotate([0, -30, 0]).add(r)
        r = rotate([0, lcd_ext_rot_angle, 0]).add(r)
        t = translate(v=[+(-lcd_inset_top+w+63-lcd_gap)*scl, (-ht+24-7.5)*scl,
                        (30-lcd_d+lcd_hinge_inner_rad)*scl]).add(r)
        a.add(t)

        # bottom end curve, overlap with 1st
        r = union()
        r = touch_arc(lcd_hinge_inner_rad, ht, bwid, 30, scl)
        r = rotate([180, 90, 90]).add(r)
        r = rotate([0, 10, 0]).add(r)
        r = rotate([0, lcd_ext_rot_angle+5, 0]).add(r)
        t = translate(v=[+(-lcd_inset_top+w+63-lcd_gap)*scl, (-ht+24-7.5)*scl,
                        (30-lcd_d+lcd_hinge_inner_rad)*scl]).add(r)
        a.add(t)

    if not nohinge:
        # outer surround
        r = union()
        r = cylinder(r=(lcd_hinge_inner_rad+bwid)*scl, h=(hole_ht)*scl,
                     segments=50, center=True)
        r = rotate([180, 90, 90]).add(r)
        t = translate(v=[+(-lcd_inset_top+w+63-lcd_gap)*scl,
                         (-ht+hole_ht/2+16.5)*scl,
                         (30-lcd_d+lcd_hinge_inner_rad)*scl]).add(r)
        a += t

        # hole for cable
        r = union()
        r = touch_arc(lcd_hinge_inner_rad+1, hinge_depth+ht, bwid,
                        lcd_hinge_inner_rad, scl,
                      angle=54)
        r = rotate([180, 90, 90]).add(r)
        r = rotate([0, lcd_ext_rot_angle+8, 0]).add(r)
        t = hinge_translate(scl).add(r)
        t = translate(v=[0, -(hole_ht+ht/2-7.5)*scl, 0]).add(t)
        a -= t

    # hinge hole
    r = union()
    r = cylinder(r=lcd_hinge_inside_rad*scl,
                        h=(ht+0.3)*scl, segments=50, center=True)
    r = rotate([180, 90, 90]).add(r)
    t = translate(v=[+(-lcd_inset_top+w+63-lcd_gap)*scl,
                        (-ht/2+16.5)*scl,
                        (30-lcd_d+lcd_hinge_inner_rad)*scl]).add(r)
    a -= t

    # screw holes through lid
    a -= lid_screwholes(scl, edge_inset)

    a = translate(v=[0, (ht-edge_inset)*scl, 0]).add(a)
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
    r = cylinder(r=screwrad*scl, h=(lcd_l*2+100)*scl, segments=50, center=True)
    r = rotate([90, 0, 0]).add(r)
    r = translate(v=[0, (lcd_l/2+50-edge_inset)*scl, 0]).add(r)
    t.add(r)
    u += t

    t = lid_bolthole(scl, False)
    r = cylinder(r=screwrad*scl, h=(lcd_l*2+100)*scl, segments=50, center=True)
    r = rotate([90, 0, 0]).add(r)
    r = translate(v=[0, (lcd_l/2+50-edge_inset)*scl, 0]).add(r)
    t.add(r)
    u += t

    return u

def screen_end(scl, ht=60):

    shear = 0
    innershear = 0
    w = lcd_w+lcd_inset_top+lcd_inset_bot
    edge_inset = bwid
    iro = 0

    rad = 15

    a = union()

    toplen = w+lcd_gap*2
    toplenoffs = (-lcd_inset_top+w+65)
    a += screen_frontedge(scl, ht, toplen, toplenoffs, curvetopback=True)

    # middle filler
    r = union()
    c = shearedcube(size=[(lcd_d+lcd_gap*2)*scl,(w+lcd_gap*2)*scl,ht*scl],
                shear=[-shear*scl, 0, 0],
                innershear=[-innershear*scl, 0, 0])
    c = rotate([0, 90, 90]).add(c)
    r.add(c)
    t = translate(v=[(-lcd_inset_top+w+65)*scl, (16.5-ht)*scl,
                        (30+lcd_gap)*scl])
    t.add(r)
    a.add(t)

    # hinge
    r = union()
    r = cylinder(r=(lcd_outer_rad)*scl, h=(ht+0.1)*scl,
                        segments=50, center=True)
    r = rotate([180, 90, 90]).add(r)
    t = hinge_translate(scl).add(r)
    t = translate(v=[0, (-ht/2+16.5)*scl, 0]).add(t)
    a.add(t)

    if pin_parts_3d:
        c = union()
        h = cube([25*scl, 10*scl, (500)*scl])
        h = translate([-50*scl, (16.5-ht)*scl, -200*scl]).add(h)
        c += h
        h = cube([25*scl, 10*scl, (500)*scl])
        h = translate([40*scl, (16.5-ht)*scl, -200*scl]).add(h)
        c += h
        h = cube([25*scl, 10*scl, (500)*scl])
        h = translate([(boxlength-20)*scl, (16.5-ht)*scl, -200*scl]).add(h)
        c += h
        h = cube([25*scl, 10*scl, (300)*scl])
        h = translate([(boxlength-180)*scl, (16.5-ht)*scl, 0*scl]).add(h)
        c += h
        h = cube([45*scl, 10*scl, (500)*scl])
        h = translate([(boxlength+140)*scl, (16.5-ht)*scl, -200*scl]).add(h)
        c += h
        h = cube([(boxlength+20+200)*scl, 10*scl, (55)*scl])
        h = translate([(-50)*scl, (16.5-ht)*scl, -200*scl]).add(h)
        c += h
        h = cube([(boxlength+20+200)*scl, 10*scl, (55)*scl])
        h = translate([(-50)*scl, (16.5-ht)*scl, 245*scl]).add(h)
        c += h
        h = cube([(20+100)*scl, 10*scl, (25)*scl])
        h = translate([(boxlength+30)*scl, (16.5-ht)*scl, 50*scl]).add(h)
        c += h
        h = cube([(20+100)*scl, 10*scl, (25)*scl])
        h = translate([(-40)*scl, (16.5-ht)*scl, -5*scl]).add(h)
        c += h
        a.add(c)

    # hinge hole
    r = union()
    r = cylinder(r=15*scl, h=(ht+0.3)*scl, segments=50, center=True)
    r = rotate([180, 90, 90]).add(r)
    t = translate(v=[+(-lcd_inset_top+w+63-lcd_gap)*scl,
                        (-ht/2+16.5)*scl,
                        (30-lcd_d+lcd_hinge_inner_rad)*scl]).add(r)
    a -= t

    a = translate(v=[0, (ht-edge_inset)*scl, 0]).add(a)
    p = lcd_panel(scl, offs=3)
    p = translate(v=[155.5*scl,61*scl,0]).add(p)
    a -= p

    # screw holes through lid
    a -= lid_screwholes(scl, edge_inset)

    return a

def box_hook_cutout(scl, hinge_depth):
    a = union()
    b = cube([29.1*2*scl, 90*scl, 70*scl])
    b = translate([-29.1*scl, -10*scl, -30*scl]).add(b)
    t = case_bolthole(scl, end=0).add(b)
    t = translate(v=[(0)*scl, (-hinge_depth/2+3)*scl,
                  (boxheight)*scl]).add(t)
    a += t
    return a

def lid_end(scl, ht_offset, ht, hinge_depth, hole_depth):
    edge_inset = bwid
    a = union()

    border=3.0
    slot_depth = 100
    boxdepth = hinge_depth+ht+edge_inset

    c = union()
    # long outside wall
    b = cube([(boxlength)*scl, (bwid)*scl, boxheight*scl])
    b = translate([0, 20*scl, 0*scl]).add(b)
    c.add(b)
    # top of lid
    lid_depth = (boxlength-lcd_inset_top-lcd_inset_bot+5)
    b = cube([lid_depth*scl,
              (boxdepth)*scl, bwid*scl])
    b = translate([0, 20*scl, 0*scl]).add(b)
    c.add(b)
    # short wall hinge-end
    b = cube([(bwid)*scl, (boxdepth)*scl, (boxinset-border)*scl])
    b = translate([(lid_depth-bwid)*scl, 20*scl, 0*scl]).add(b)
    c.add(b)
    # short front-facing wall
    b = cube([(bwid)*scl, (boxdepth)*scl, boxheight*scl])
    b = translate([0, 20*scl, 0*scl]).add(b)
    c.add(b)
    b = cube([(bwid+1)*scl, (boxdepth)*scl, boxinset*scl])
    b = translate([-0.5*scl, (20+77)*scl, (boxinset-border)*scl]).add(b)
    c -= b
    a.add(c)

    a = translate(v=[(30-lcd_inset_top)*scl, (-bwid)*scl,
                        (+50+boxtopoffs)*scl]).add(a)

    # insets for nuts and threaded bar
    holes = [0, 1, 2] if test else [0, 1, 2, 3]
    for end in holes:
        r = union()
        c = cylinder(r=29*scl, h=(77)*scl, segments=50)
        c = rotate([0, 90, 90]).add(c)
        r.add(c)
        if end != 0:
            dp = 0
            c = cube([29*2*scl, 77*scl, (dp+29*2)*scl], center=True)
            c = translate(v=[(0)*scl, (77/2)*scl, (dp/2)*scl]).add(c)
        else:
            c = cube([29*scl, 77*scl, (29)*scl], center=True)
            c = translate(v=[(29/2.0)*scl, (77/2)*scl, (29/2.0)*scl]).add(c)
        r.add(c)
        t = case_bolthole(scl, end=end).add(r)
        t = translate(v=[(0)*scl, (3)*scl, (boxheight)*scl]).add(t)
        a += t

    # screw holes in box
    t = box_screwholes(scl, edge_inset, holes=holes)
    t = translate(v=[0, 0, boxheight*scl]).add(t)
    a -= t

    # hollow out tube including base box
    t = hollow_out_edge(scl, hole_depth, ht, border)
    t = translate(v=[0, (-20)*scl, 0]).add(t)
    a -= t

    return a

def back_box_lidfront(scl, ht_offset, ht, extraht):
    edge_inset = bwid
    bht = bwid*3-10
    blen = ht+extraht
    a = union()
    c = hollowbox(scl, bdep-ethdep+100+bwid, blen, bht,
                    {T:bwid, B: -1, L:bwid, R:-1, F:-1, D:-1},
                    curverads={ T|L:(bwid, 0),
                               })
    c = translate(v=[(-100-bwid)*scl,
                    0*scl, (lcd_d-15+bwid)*scl]).add(c)
    a.add(c)
    c = cube([159*scl, (extraht+26)*scl, 200*scl])
    c = translate(v=[(40)*scl,
                    -1*scl, (lcd_d-15+bwid-1)*scl]).add(c)
    
    a -= c

    a = translate(v=[(lcd_w+35)*scl, 0, 0]).add(a)

    # supports for threads, one (end=1) needs a cutout in the base box
    dep = 40
    holes = [(1, extraht+25), (2, extraht+25),
                (2, (blen-dep)/2), (2, blen-dep-25)]
    for (end, offs) in holes:
        r = union()
        if end == 1:
            dp = 70
        else:
            dp = 0
        c = cube([29*2*scl, dep*scl, (dp+29*2)*scl], center=True)
        c = translate(v=[(0)*scl, (dep/2)*scl, (-dp/2)*scl]).add(c)
        r.add(c)
        t = case_bolthole(scl, end=end).add(r)
        t = translate(v=[(0)*scl, (offs)*scl, (boxheight)*scl]).add(t)
        a += t

    # screw holes in box
    t = box_screwholes(scl, edge_inset, holes=[1,2])
    t = translate(v=[0, 0, boxheight*scl]).add(t)
    a -= t
    return a

def back_box_lid(scl, ht_offset, ht):
    edge_inset = bwid
    bht = bwid*3-10
    blen = ht
    a = union()
    c = hollowbox(scl, ethdep+bwid, blen, bht,
                    {T:bwid, B: -1, L:bwid, R:-1, F:-1, D:-1},
                    curverads={ T|L:(bwid, 0),
                               T|R:(bwid, 0),
                               B|R:(80, 0),
                               })
    c = translate(v=[(bdep-ethdep-bwid)*scl, 0, (lcd_d-22-bwid)*scl]).add(c)
    a.add(c)

    a = translate(v=[(lcd_w+35)*scl, 0, 0]).add(a)

    return a

def back_box_base(scl, ht_offset, ht):
    edge_inset = bwid
    bht = boxheight+bwid*2-10
    blen = ht
    a = union()
    c = hollowbox(scl, ethdep, blen, bht,
                    {T:-1, B: bwid, L:-25.0, R:bwid, F:bwid, D:bwid},
                    curverads={ D|R:(bwid, 0),
                               B|R:(80, 0),
                               })
    c = translate(v=[(bdep+100-ethdep)*scl, 0, (lcd_d-22)*scl]).add(c)
    a.add(c)
    c = hollowbox(scl, bdep+100-ethdep+1, blen, boxheight-bwid,
                    {T:-1, B: bwid, L:-25.0, R:-1, F:bwid, D:bwid})
    c = translate(v=[0, 0, (lcd_d-32+bwid*3)*scl]).add(c)
    a.add(c)
    csw = 50.0
    # add corner supports
    c = cube([scl*csw, scl*csw, bht*scl])
    c = translate(v=[(bdep+100-ethdep)*scl, 0, (lcd_d-22)*scl]).add(c)
    a.add(c)
    c = cube([scl*csw, scl*csw, bht*scl])
    c = translate(v=[(bdep+100-ethdep)*scl, (blen-csw)*scl,
            (lcd_d-22)*scl]).add(c)
    a.add(c)
    c = cube([scl*csw, scl*csw, bht*scl])
    c = translate(v=[(bdep+100-csw)*scl, (blen-csw)*scl, (lcd_d-22)*scl]).add(c)
    a.add(c)
    # these are for the keyboard lid
    c = cube([scl*csw, scl*csw, (bht-bwid*3)*scl])
    c = translate(v=[(bdep+100-ethdep-csw)*scl, (blen-csw)*scl,
            (lcd_d-32+bwid*3)*scl]).add(c)
    a.add(c)
    c = cube([scl*csw, scl*csw, (bht-bwid*3)*scl])
    c = translate(v=[(0)*scl, (blen-csw)*scl,
            (lcd_d-32+bwid*3)*scl]).add(c)
    a.add(c)
    c = cube([scl*csw, scl*csw, (bht-bwid*3)*scl])
    c = translate(v=[(bdep+100-ethdep-csw)*scl, 0*scl,
            (lcd_d-32+bwid*3)*scl]).add(c)
    a.add(c)

    a = translate(v=[(lcd_w+35-100)*scl, 0, 0]).add(a)

    # add a structural support for bolthole (nut lock point)
    # has to be extended slightly so that the lid can sit on top of it
    hwid = 25.0
    for (hole, offs) in [(1, 0), (2, 0), (2, blen-hwid), (1, blen-hwid)]:
        r = union()
        if hole == 2:
            dp = 0
        else:
            dp = 50
        c = cube([29*2*scl, hwid*scl, (dp+29*2)*scl], center=True)
        c = translate(v=[(0)*scl, (hwid/2-3)*scl, (-dp/2)*scl]).add(c)
        r.add(c)
        if hole == 2 and offs == 0:
            c = cube([29*2*scl, hwid*scl, (dp+29*2)*scl], center=True)
            c = translate(v=[(+28*2)*scl, (hwid/2-3)*scl, (dp/2)*scl]).add(c)
            r.add(c)
        t = case_bolthole(scl, end=hole).add(r)
        t = translate(v=[(0)*scl, (offs+3)*scl, (boxheight)*scl]).add(t)
        a += t

    # screw holes in box
    t = box_screwholes(scl, edge_inset, holes=[1,2])
    t = translate(v=[0, 0, boxheight*scl]).add(t)
    a -= t

    # this is a cut-out so that the lid's thread-support goes through
    end = 1
    offs = 25
    dep = 40
    r = union()
    dp = 0
    c = cube([29*2*scl, dep*scl, (30+29*2)*scl], center=True)
    c = translate(v=[(0)*scl, (dep/2)*scl, (-dp/2)*scl]).add(c)
    r.add(c)
    t = case_bolthole(scl, end=end).add(r)
    t = translate(v=[(0)*scl, (offs)*scl, (boxheight)*scl]).add(t)
    a -= t

    return a

def front_box_base(scl, ht_offset, ht):
    bdep = 310
    edge_inset = bwid
    bht = boxheight-boxinset
    blen = ht
    a = union()
    c = hollowbox(scl, bdep, blen, bht,
                    {T:-1, B: -1, R:-25.0, L:bwid, F:-1, D:bwid},
                    curverads={ D|L:(29, 0),
                               })
    c = translate(v=[(5)*scl, 0, (lcd_d-32+bwid*2+boxinset)*scl]).add(c)
    a.add(c)
    hwid = 25
    r = union()
    c = cylinder(r=29*scl, h=(hwid)*scl, segments=50)
    c = rotate([0, 90, 90]).add(c)
    r.add(c)
    dp = 0
    c = cube([29*2*scl, hwid*scl, (dp+29*2)*scl], center=True)
    c = translate(v=[(0)*scl, (hwid/2)*scl, (dp/2)*scl]).add(c)
    r.add(c)
    t = case_bolthole(scl, end=0).add(r)
    t = translate(v=[(0)*scl, (0)*scl, (boxheight)*scl]).add(t)
    t -= translate(v=[0, (ht+20)*scl/2.0, 0]).add(co)
    a += t

    # screw holes in box
    t = box_screwholes(scl, edge_inset, holes=[0])
    t = translate(v=[0, 0, boxheight*scl]).add(t)
    a -= t

    return a

def base_end2(scl, ht_offset, ht, hinge_depth, hole_depth, mid=False):
    edge_inset = bwid
    a = union()

    border=3.0 # move cylinders inwards so that lid cylinders fit around them
    slot_depth = 100
    extradepth = 0

    if mid:
        extradepth = 140
    else:
        # inner tube
        r = union()
        r = cylinder(r=(lcd_hinge_inside_rad-border)*scl, h=(bwid)*scl,
                     segments=50, center=True)
        r = rotate([180, 90, 90]).add(r)
        t = hinge_translate(scl).add(r)
        t = translate(v=[0, (-27-bwid/2)*scl, 0]).add(t)
        a.add(t)

    # base hinge box
    boxdepth = hinge_depth+ht
    box = base_box(scl, boxdepth, hole_depth, ht, extralen=extradepth,
                   hollow=True, inner=True)

    a += box

    holes = [0, 1, 2] if test else [0, 1, 2, 3]
    # screw support at both ends
    for end in holes:
        r = union()
        c = cylinder(r=29*scl, h=boxdepth*scl, segments=50)
        c = rotate([0, 90, 90]).add(c)
        r.add(c)
        t = case_bolthole(scl, end=end).add(r)
        t = translate(v=[(0)*scl, (-(boxdepth)/2-3.5)*scl,
                        (boxheight)*scl]).add(t)
        a += t

    # screw holes in box
    t = box_screwholes(scl, edge_inset, holes=holes)
    t = translate(v=[0, 0, boxheight*scl]).add(t)
    a -= t

    if not mid:
        # this screwhole is only part-way through
        t = box_screwholes(scl, edge_inset, holes=[1], h=60)
        t = translate(v=[0, -69.0*scl, boxheight*scl]).add(t)
        a -= t

        # cutout for cable
        h = cube([(105)*scl, (60)*scl,
                   (50)*scl])
        h = translate(v=[(boxlength-bwid-105)*scl,
                            (-70-0.2)*scl, (89)*scl]).add(h)
        a -= h

    a = translate(v=[0, (ht-edge_inset+ht_offset)*scl, 0]).add(a)

    return a

def hollow_out_edge(scl, hole_depth, ht, border):
    r = union()
    r = cylinder(r=(lcd_outer_rad+border)*scl, h=(hole_depth+ht*1+10.0)*scl,
                        segments=50, center=True)
    r = rotate([180, 90, 90]).add(r)
    t = hinge_translate(scl).add(r)
    t = translate(v=[0, (hole_depth-ht*2-hole_depth/2+16.5)*scl, 0]).add(t)
    return t

def hollow_out_basebox(scl, border, hinge_depth):
    r = union()
    r = cylinder(r=(lcd_hinge_inside_rad-bwid-border)*scl,
                        h=(hinge_depth+0.4)*scl, segments=50, center=True)
    r = rotate([180, 90, 90]).add(r)
    t = hinge_translate(scl).add(r)
    t = translate(v=[0, (hinge_depth-hinge_depth/2+16.5)*scl, 0]).add(t)
    return t

def base_end(scl, ht_offset, ht, hinge_depth, hole_depth, innerpart=False):
    edge_inset = bwid
    a = union()

    border=3.0 # move cylinders inwards so that lid cylinders fit around them
    slot_depth = 100

    # inner tube
    r = union()
    r = cylinder(r=(lcd_hinge_inside_rad-border)*scl, h=(hinge_depth-20)*scl,
                        segments=50, center=True)
    r = rotate([180, 90, 90]).add(r)
    t = hinge_translate(scl).add(r)
    t = translate(v=[0, (hinge_depth-hinge_depth/2+6.5)*scl, 0]).add(t)
    a.add(t)

    # base hinge box
    boxdepth = hinge_depth+ht
    box = base_box(scl, boxdepth, hole_depth, ht, hollow=True)

    # add curved inner wall
    u = intersection()
    r = union()
    r = cylinder(r=(lcd_outer_rad+20)*scl, h=(hole_depth+ht*2+bwid+0.1)*scl,
                        segments=50, center=True)
    r = rotate([180, 90, 90]).add(r)
    t = hinge_translate(scl).add(r)
    t = translate(v=[0, (hole_depth-ht*2-hole_depth/2+16.5)*scl, 0]).add(t)
    b = base_box(scl, boxdepth, hole_depth, ht, hollow=False)
    u.add(b)
    u.add(t)

    box += u

    # add 2nd covering curved inner wall
    u = intersection()
    r = union()
    r = cylinder(r=(lcd_outer_rad)*scl, h=(20+0.1)*scl,
                        segments=50, center=True)
    r = rotate([180, 90, 90]).add(r)
    t = hinge_translate(scl).add(r)
    t = translate(v=[0, (hole_depth-15)*scl, 0]).add(t)
    b = base_box(scl, boxdepth, hole_depth, ht, hollow=False)
    u.add(b)
    u.add(t)

    box += u

    # slot to main base (for cable)
    r = union()
    cable_slot_depth = 95
    r = touch_arc(lcd_hinge_inner_rad, cable_slot_depth, bwid,
                        lcd_hinge_inner_rad, scl,
                  angle=30)
    r = rotate([180, 90, 90]).add(r)
    r = rotate([0, lcd_ext_rot_angle+110, 0]).add(r)
    t = hinge_translate(scl).add(r)
    t = translate(v=[0, (hinge_depth-ht-cable_slot_depth/2+6.5-7.5)*scl,
                     0]).add(t)
    a -=t

    # hollow out base box at edge
    box -= hollow_out_edge(scl, hole_depth, ht, border)

    a += box

    # hollow out tube including base box
    a -= hollow_out_basebox(scl, border, hinge_depth)

    # cutout for base top "hook" with screw-hole in it
    a -= box_hook_cutout(scl, hinge_depth)

    if test:
        l = [(0, 36), (1, -46), (2, 36)]
    else:
        l = [(0, 36), (1, -46), (2, 36), (3, -46), (3, 36)]
    for (end, offs) in l:
        doffs = boxheight-45
        if end == 2:
            doffs += 20
        b = cube([10*scl, (boxdepth-63.5)*scl, (60)*scl])
        t = case_bolthole(scl, end=end).add(b)
        t = translate(v=[(offs)*scl, (-boxdepth/2+105)*scl, doffs*scl]).add(t)
        a += t
    b = cube([25*scl, (boxdepth-70)*scl, (bwid*1.2)*scl])
    t = case_bolthole(scl, end=0).add(b)
    t = translate(v=[(20)*scl, (-boxdepth/2+105)*scl, (boxheight)*scl]).add(t)
    a += t
    # 1/4 cutouts at the corner edges for case rounding
    b = cube([80*scl, 90*scl, 170*scl])
    t = case_bolthole(scl, end=0).add(b)
    t = translate(v=[(-90)*scl, (-hinge_depth/2-7)*scl, (0)*scl]).add(t)
    a -= t

    # screw support at both ends
    for end in range(3 if test else 4):
        if end != 0:
            if end == 2:
                bht = 29.1*2
            else:
                bht = 80
            if end == 2:
                b = cube([(29.1*2+15)*scl, 70*scl, 53*scl])
                b = translate([(-29.1+5)*scl, 18.5*scl, 7*scl]).add(b)
            else:
                b = cube([(29.1*2+bwid*2)*scl, 70*scl, 64*scl])
                b = translate([(-29.1-bwid)*scl, 18.5*scl, -30*scl]).add(b)
            t = case_bolthole(scl, end=end).add(b)
            t = translate(v=[(0)*scl, (-hinge_depth/2+3)*scl,
                        (boxheight-bwid)*scl]).add(t)
            a += t

            b = cube([29.1*2*scl, 70*scl, bht*scl])
            b = translate([-29.1*scl, 10*scl, -30*scl]).add(b)
            t = case_bolthole(scl, end=end).add(b)
            t = translate(v=[(0)*scl, (-hinge_depth/2+3)*scl,
                        (boxheight)*scl]).add(t)
            a -= t
        r = union()
        c = cylinder(r=29*scl, h=(boxdepth+18.5)*scl, segments=50)
        c = rotate([0, 90, 90]).add(c)
        r.add(c)
        b = cube([80*scl, 90*scl, 170*scl])
        r -= translate([-35*scl, -10*scl, -30*scl]).add(b)
        t = case_bolthole(scl, end=end).add(r)
        t = translate(v=[(0)*scl, (-hinge_depth/2+3)*scl,
                        (boxheight)*scl]).add(t)
        a += t

    # screw holes in box
    t = box_screwholes(scl, edge_inset)
    t = translate(v=[0, 0, boxheight*scl]).add(t)
    a -= t

    # additional cutout for cable
    h = cube([(40)*scl, (60)*scl,
               (55+0.2)*scl])
    h = translate(v=[(boxlength-bwid-25)*scl,
                        (boxdepth-95+0.2)*scl, (40)*scl]).add(h)
    a -= h

    a = translate(v=[0, (ht-edge_inset+ht_offset+20)*scl, 0]).add(a)

    return a

def base_box(scl, boxdepth, hole_depth, ht, extralen=0,
                hollow=True, inner=False):
    blen = boxlength+extralen
    # base hinge box
    c = union()
    nonhollowb = cube([blen*scl, (boxdepth)*scl, boxheight*scl])
    nonhollowb = translate([0, 20*scl, 0*scl]).add(nonhollowb)
    if not hollow:
        c.add(nonhollowb)
    if hollow:
        if True:
            curverads={
                       D|L:(30, 0),
                       D|R:(bwid, bwid),
                       }
            b = hollowbox(scl, blen, boxdepth, boxheight,
                            {T:-1, B: -1,
                            L:bwid, R:bwid*3, F:bwid, D:bwid},
                            curverads=curverads)
            b = translate([0, 20*scl, 0*scl]).add(b)
            c.add(b)
            if inner:
                hoffs=bwid*2
                loffs=0
                bl = blen-bwid*2
            else:
                hoffs = -0.3
                loffs=0
                bl = blen-lcd_outer_rad-80-bwid*2
            h = cube([(boxlength-lcd_outer_rad-80-bwid-loffs+0.3)*scl,
                       (boxdepth+bwid+0.3)*scl,
                       (boxinset+0.3)*scl])
            h = translate(v=[(loffs-0.3)*scl, (bwid-0.3)*scl, -0.3*scl]).add(h)
            c -= h
        if not inner:
            h = cube([(bwid+0.5)*scl, (boxdepth)*scl,
                       (boxheight)*scl])
            h = translate(v=[(blen-lcd_outer_rad-80-bwid)*scl, 20*scl,
                              -0.0*scl]).add(h)
            c += h

        if not inner:
            # add some structural support
            sstep = 140
            sdep = sstep
            while sdep <= boxlength-sstep*(2 if test else 2):
                u = intersection()
                u.add(nonhollowb)
                r = union()
                h = cube([bwid*scl, 100*scl, 100*scl])
                h = rotate([-45, 0, 0]).add(h)
                h = translate(v=[sdep*scl, 100*scl, (boxheight-2)*scl]).add(h)
                r.add(h)
                u.add(r)
                c += u
                sdep += sstep

        # cutout in side of box for cable
        h = cube([(140)*scl, (60)*scl,
                   (55+0.2)*scl])
        h = translate(v=[(boxlength-bwid-120)*scl,
                            (boxdepth-32+0.1)*scl, (20)*scl]).add(h)
        if not inner:
            c -= h
        if pin_parts_3d:
            h = cube([25*scl, 10*scl, (500)*scl])
            h = translate([-50*scl, (boxdepth+10)*scl, -200*scl]).add(h)
            c += h
            h = cube([(90)*scl, 10*scl, (20)*scl])
            h = translate([(-50)*scl, (boxdepth+10)*scl, 40*scl]).add(h)
            c += h
            h = cube([(60)*scl, 10*scl, (25)*scl])
            h = translate([(-50)*scl, (boxdepth+10)*scl, 95*scl]).add(h)
            c += h
            if not test:
                for m in [0.2, 0.45, 0.7]:
                    h = cube([17*scl, 10*scl, (500)*scl])
                    h = translate([(boxlength*m)*scl,
                                   (boxdepth+10)*scl, -200*scl]).add(h)
                    c += h
            h = cube([17*scl, 10*scl, (500)*scl])
            h = translate([30*scl, (boxdepth+10)*scl, -200*scl]).add(h)
            c += h
            h = cube([15*scl, 10*scl, (500)*scl])
            h = translate([(boxlength)*scl, (boxdepth+10)*scl, -200*scl]).add(h)
            c += h
            h = cube([25*scl, 10*scl, (300)*scl])
            h = translate([(boxlength-180)*scl, (boxdepth+10)*scl,
                        -200*scl]).add(h)
            c += h
            h = cube([45*scl, 10*scl, (500)*scl])
            h = translate([(boxlength+110)*scl, (boxdepth+10)*scl,
                        -200*scl]).add(h)
            c += h
            h = cube([(boxlength+20+150)*scl, 10*scl, (55)*scl])
            h = translate([(-40)*scl, (boxdepth+10)*scl, -200*scl]).add(h)
            c += h
            h = cube([(boxlength+20+150)*scl, 10*scl, (55)*scl])
            h = translate([(-40)*scl, (boxdepth+10)*scl, 245*scl]).add(h)
            c += h
            h = cube([(20+100)*scl, 10*scl, (25)*scl])
            h = translate([(boxlength+10)*scl, (boxdepth+10)*scl,
                        -10*scl]).add(h)
            c += h

    # lid at hinge end
    b = cube([(lcd_outer_rad+100+extralen-3)*scl, (boxdepth)*scl, 20*scl])
    b = translate(v=[(boxlength-lcd_outer_rad-100+3)*scl, 20*scl, 0]).add(b)
    c += b
    if extralen == 0:
        # back piece at hinge end
        b = cube([(8)*scl, (boxdepth)*scl, 70*scl])
        b = translate(v=[(boxlength-0.3)*scl, 20*scl, 40*scl]).add(b)
        c += b
    t = hinge_translate(scl).add(c)
    box = translate(v=[-boxlength*scl, (+16.5-ht*2)*scl, boxtopoffs*scl]).add(t)
    return box

def screen_adjust(b, scl, angle):
    p = lcd_panel(scl, offs=3)
    p = translate(v=[155.5*scl,61*scl,0]).add(p)
    b -= p

    p = lcd_view_area(scl, offs=3)
    p = translate(v=[155.5*scl,61*scl,0*scl]).add(p)
    b -= p

    return hinge_rotate(scl, b, angle)


def create_laptop(t, scl, mirror, colour, part, angle):

    #if part != 1 and part != 8 and part != 6 and part != 7:
    #if part != 3 and part != 4 and part != 0 and part != 2:
    if part != 1 and part != 6:
    #if part > 3:
    #if part > 6:
    #    return
    #if part != 0 and part != 2 and part != 4 and part != 5 and part != 3:
    #if part != 8 and part != 6 and part != 9 and part != -1 and part != -7 and \
    #    part != -0.1 and part != -4 and part != 10 and part != 11:
        return

    c = color(colour)
    c.add(t)

    b = union()

    if part == 0:
        b.add(screen_end(scl, lcd_end_ht))
        m = screen_mid1(scl, hinge_depth, hole_depth)
        m = translate(v=[0, lcd_end_ht*scl,0]).add(m)
        b.add(m)
        #ht2 += lcd_end_ht

        b = screen_adjust(b, scl, angle)

    ht = 40
    if part == 1:
        b.add(base_end(scl, lcd_end_ht, ht, hinge_depth, hole_depth))
    if part == 7:
        b.add(lid_end(scl, lcd_end_ht, ht, hinge_depth, hole_depth))

    base_ht = 40
    if part == 6:
        e = base_end2(scl, lcd_end_ht, ht, base_ht, hole_depth)
        e = translate(v=[0, (lcd_end_ht+ht+hinge_depth)*scl,0]).add(e)
        b.add(e)

    offs = (lcd_end_ht+ht+hinge_depth+base_ht+40)
    wid = lcd_l/2-offs-50
    if part == 8:
        e = back_box_base(scl, lcd_end_ht, wid)
        e = translate(v=[0, offs*scl,0]).add(e)
        b.add(e)

    if part == 10:
        e = back_box_lid(scl, lcd_end_ht, wid)
        e = translate(v=[0, offs*scl,0]).add(e)
        b.add(e)

    if part == 11:
        e = back_box_lidfront(scl, lcd_end_ht, wid, base_ht+40)
        e = translate(v=[0, (offs-base_ht-40)*scl,0]).add(e)
        b.add(e)

    if part == 9:
        e = front_box_base(scl, lcd_end_ht, wid)
        e = translate(v=[0, offs*scl,0]).add(e)
        b.add(e)

    if part == 2:
        m = screen_mid1(scl, 40.0, hole_depth, nohinge=True)
        m = translate(v=[0, (lcd_end_ht+hinge_depth)*scl,0]).add(m)
        b.add(m)

        b = screen_adjust(b, scl, angle)

    numparts = 10 if test else 30
    offs = lcd_end_ht+hinge_depth+40.0
    midht = (lcd_l/2.0-offs+bwid-50.0) / numparts
    print midht

    for i in range(numparts):
        if part == 3:
            m = screen_mid1(scl, midht, hole_depth, nohinge=True, endpart=True)
            m = translate(v=[0, offs*scl,0]).add(m)
            m = screen_adjust(m, scl, angle)
            b.add(m)

        if part == 4:
            m = screen_mid2(scl, midht, hole_depth)
            m = translate(v=[0, offs*scl,0]).add(m)
            m = screen_adjust(m, scl, angle)
            b.add(m)

        offs += midht

    if part == 5:
        m = screen_mid3(scl, 100, hole_depth)
        m = translate(v=[0, (lcd_l/2+bwid-50)*scl,0]).add(m)
        m = screen_adjust(m, scl, angle)
        b.add(m)


    c = color([0.2, 0.2, 0.2, 1.0])
    c.add(b)
    t.add(c)

if __name__ == '__main__':

    animate = False
    max_open = 130
    if animate:
        rpt = 3
        angles = [0, max_open*0.25, max_open*0.5, max_open*0.75, max_open]
    else:
        rpt = 1
        angles = [130]

    for i in range(rpt):
        for angle in angles:
            scl = 0.1
            t = union()
            c = [0.3, 0.5, 0.8, 0.5]
            for i in range(12):
                create_laptop(t, scl, 1.0, c, part=i, angle=angle)
            t = color(c).add(t)

            if True: # add inner parts for reference
                p = lcd_panel(scl)
                p = translate(v=[155.5*scl,61*scl,0]).add(p)
                p = hinge_rotate(scl, p, angle)
                t.add(p)
                # ethernet, amphenol RJCSE-538X-01
                eth = cube([157.5*scl, 165.5*scl, (134.8+13.0)*scl])
                p = translate(v=[(lcd_w+190)*scl,340*scl,(5+23)*scl]).add(eth)
                t.add(p)

            if True:
                card = import_stl(filename = "eoma68.stl")
                r = rotate([90,180,-90]).add(card)
                r = translate([(lcd_w+350)*scl, 1100*scl, 135*scl]).add(r)
                t.add(r)

            scad_render_to_file(t, "laptop_prog.scad")
            f = open("laptop_model.scad", "w")
            f.write("""include<laptop_prog.scad>;
            """)
            f.close()
            if i != rpt:
                time.sleep(2)
