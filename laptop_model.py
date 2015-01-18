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

scl = 0.1
hthick = 10 # horizontal pieces not as thick
bwid = 17 # 24
lcd_inset_top = 25
lcd_inset_bot = 200
lcd_gap = 3
lcd_hinge_inner_rad=70
lcd_hinge_inside_rad=70
lcd_ext_rot_angle=250
lcd_outer_rad = lcd_hinge_inner_rad+bwid
lcd_end_ht = 20 # 40

screwrad = 32 / 2.0
topscrewrad = 20 / 2.0 # supposed to be 3mm screw holes but 3d baaad....
boxheight = 140
backboxheight = boxheight+bwid*2-10
boxtopoffs = 2
boxinset = 55
hinge_depth = 70 
hole_depth = hinge_depth
boxlength = lcd_w + lcd_inset_top + lcd_inset_bot + lcd_d-20
lidfront_offs = 10

bdep = 325
fdep = 300
ethdep = 160
bdepoffs = 15
csw = 55.0 # centre support width (for screws to go into)

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

def ethernet(scl):
    # ethernet, amphenol RJCSE-538X-01
    eth = cube([157.5*scl, 165.5*scl, (134.8+13.0)*scl])
    return translate(v=[(lcd_w+190)*scl,130*scl,(4+23)*scl]).add(eth)

def lcd_panel(scl, offs=0):

    w = lcd_w
    h = lcd_l
    d = lcd_d

    a = union()

    r = union()
    c = cube(size=[(w+offs*2)*scl,(h+offs*2)*scl,(d+offs*2)*scl])
    c = rotate([00, 0, 0 ]).add(c)
    r.add(c)
    t = translate(v=[(-93-offs)*scl, (-40-offs)*scl, (29.5-d-offs)*scl])
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
        return translate([(29.0+140-lcd_d-lcd_inset_top+6)*scl, 0*scl, bht*scl])
    elif end == 1:
        return translate([(-10+lcd_w+11)*scl, 0*scl, bht*scl])
    elif end == 2:
        return translate([(lcd_w+lcd_inset_bot-95)*scl, 0*scl,
                            (-lcd_d+129+boxtopoffs-boxheight)*scl])
    elif end == 3:
        return translate([(-20+lcd_w/2.0+30)*scl, 0*scl, bht*scl])

def lid_bolthole(scl, end=True):
    if end:
        return translate([(-lcd_inset_top+58)*scl, 0*scl, (16)*scl])
    else:
        return translate([(95+lcd_w)*scl, 0*scl, (16)*scl])

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

def screen_mid2(scl, ht, hole_ht, endpart=True,
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
    a += screen_frontedge(scl, ht, 80, toplenoffs, 
                               curvefront=False, curvetopback=True)

    # add hinge-end filler over top of screwhole
    r = union()
    c = shearedcube(size=[(lcd_d+10+lcd_gap*2)*scl,(lcd_gap*2+bwid+5)*scl,ht*scl],
                shear=[-shear*scl, 0, 0],
                innershear=[-innershear*scl, 0, 0])
    c = rotate([0, 90, 90]).add(c)
    r.add(c)
    t = translate(v=[(+lcd_inset_bot+lcd_w-110)*scl,
                        (16.5-ht)*scl, (37+lcd_gap)*scl])
    t.add(r)
    a.add(t)

    a.add(lid_bottom_boltholder(scl, lcd_gap, ht, iro))

    if removemiddle:
        # top edge
        r = union()
        c = shearedcube(size=[(bwid*3+iro)*scl,
                            (w-toplen-lcd_inset_top-lcd_inset_bot-80)*scl,
                            (ht+2)*scl],
                    shear=[-shear*scl, 0, 0],
                    innershear=[-innershear*scl, 0, 0])
        c = rotate([0, 90, 90]).add(c)
        r.add(c)
        t = translate(v=[(w-lcd_inset_bot-lcd_inset_top-80)*scl,
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
    c = shearedcube(size=[(bwid+5+iro)*scl,(70+lcd_gap*2)*scl,ht*scl],
                shear=[-shear*scl, 0, 0],
                innershear=[-innershear*scl, 0, 0])
    c = rotate([0, 90, 90]).add(c)
    r.add(c)
    t = translate(v=[(55)*scl, (16.5-ht)*scl, (25)*scl]).add(r)
    t = lid_bolthole(scl, end=False).add(t)
    a.add(t)

    return a

def screen_frontedge(scl, ht, extralen, toplenoffs, 
                            curvefront=True, curvetopback=False,
                            edge=False):
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
    if edge:
        curverads[B|T] = (bwid, 0)
    if curvefront:
        curverads[L|T] = (lcd_d+bwid+5, 0)
        curverads[L|D] = (bwid, 0)
        offs = 0
    else:
        to -= lcd_w
        offs = lcd_w
    if curvetopback:
        curverads[T|R] = (bwid+lcd_gap, bwid*2)
    c = hollowbox(scl, to+15+extralen, ht, lcd_d+35+lcd_gap*2,
                    {T:bwid, B: -1,
                    L:80, R:bwid+lcd_gap, F:-1, D:bwid},
                    curverads=curverads)
    c = translate(v=[(offs-extralen)*scl, (16.5-ht)*scl,
                    (12-lcd_d-lcd_gap)*scl]).add(c)
    a.add(c)

    return a

def screen_mid1(scl, ht, hole_ht, nohinge=False, endpart=False,
                        halfhollow=False, fillinner=False):
    """
        TODO: inside edge of lcd support is too thin, gcode is 2 layers
              separated by a large gap
    """

    shear = 0
    innershear = 0
    w = lcd_w+lcd_inset_top+lcd_inset_bot
    edge_inset = bwid
    iro = 0

    rad = 15

    a = union()

    if endpart:
        toplen = 140 if test else 200
        toplenoffs = (toplen-131+165)+40

    else:
        toplen = w+lcd_gap*2
        toplenoffs = (-lcd_inset_top+w+65)+30
    extralen = 0
    if nohinge and not endpart:
        extralen = 80

    # top and bottom edge
    a += screen_frontedge(scl, ht, extralen, toplenoffs,
                curvefront=not fillinner,
                curvetopback=not (nohinge and endpart))

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

    if fillinner:
        # add hinge-end filler over top of screwhole
        c = shearedcube(size=[60*scl,
                        bwid*scl,(lcd_d+10+lcd_gap*2)*scl],
                    shear=[-shear*scl, 0, 0],
                    innershear=[-innershear*scl, 0, 0])
        t = translate(v=[(+lcd_inset_bot+lcd_w-52)*scl, (-0.5)*scl,
                        (-26)*scl])
        t.add(c)
        a.add(t)

        # add a tiny clip which locks into the screen end part
        c = shearedcube(size=[30*scl,
                        ht*scl,(15)*scl],
                    shear=[-shear*scl, 0, 0],
                    innershear=[-innershear*scl, 0, 0])
        t = translate(v=[(+lcd_inset_bot+lcd_w-44)*scl, (-ht+5)*scl,
                        (-25)*scl])
        t.add(c)
        a.add(t)

    if not endpart:
        if not fillinner:
            # lid end filler for front screwhole
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
        c = shearedcube(size=[(lcd_d+bwid+lcd_gap*2)*scl,
                        (lcd_gap*2+bwid)*scl,ht*scl],
                    shear=[-shear*scl, 0, 0],
                    innershear=[-innershear*scl, 0, 0])
        c = rotate([0, 90, 90]).add(c)
        r.add(c)
        t = translate(v=[(+lcd_inset_bot+lcd_w-115)*scl, (16.5-ht)*scl,
                        (30+lcd_gap)*scl])
        t.add(r)
        a.add(t)

        # bottom end curve (1st)
        r = union()
        r = touch_arc(lcd_hinge_inner_rad, ht, bwid, 30, scl)
        r = rotate([180, 90, 90]).add(r)
        r = rotate([0, -30, 0]).add(r)
        r = rotate([0, lcd_ext_rot_angle+20, 0]).add(r)
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

    if halfhollow:
        hrad = lcd_hinge_inside_rad-20
    else:
        hrad = lcd_hinge_inside_rad
    # hinge hole
    r = union()
    r = cylinder(r=hrad*scl,
                        h=(ht+90+0.3)*scl, segments=50, center=True)
    r = rotate([180, 90, 90]).add(r)
    t = hinge_translate(scl).add(r)
    t = translate(v=[0, (-ht/2+28.5)*scl, 0]).add(t)
    a -= t
    if halfhollow:
        # hinge hole inset against base hinge part, only we have
        # to take a tiny bit out of it for the cable
        r = union()
        r = cylinder(r=lcd_hinge_inside_rad*scl,
                            h=(ht)*scl, segments=50, center=True)
        r = rotate([180, 90, 90]).add(r)
        t = hinge_translate(scl).add(r)
        t = translate(v=[0, (-ht/2+65)*scl, 0]).add(t)
        a -= t
        # hole for cable
        r = union()
        r = touch_arc(hrad, hinge_depth+ht, bwid,
                        lcd_hinge_inner_rad-20, scl,
                      angle=14)
        r = rotate([180, 90, 90]).add(r)
        r = rotate([0, lcd_ext_rot_angle+28, 0]).add(r)
        t = hinge_translate(scl).add(r)
        t = translate(v=[0, -(hole_ht+ht/2-7.5)*scl, 0]).add(t)
        a -= t

    # screw holes through lid
    a -= lid_screwholes(scl, edge_inset)

    a = translate(v=[0, (ht-edge_inset)*scl, 0]).add(a)
    return a

def friction_hinge_inner(scl, ht):

    a = union()
    hht = 50

    # outer disc
    r = union()
    c = cylinder(r=48*scl, 
                        h=(hht)*scl, segments=50, center=True)
    c = rotate([180, 90, 90]).add(c)
    r.add(c)
    # cutout to match with inset in the wall, stops the friction hinge turning
    for ang in [0, 180]:
        c = touch_arc(lcd_hinge_inner_rad-20, 60, bwid,
                            13, scl,
                      angle=58)
        c = rotate([180, 90, 90]).add(c)
        c = rotate([0, lcd_ext_rot_angle+221+ang, 0]).add(c)
        c = translate(v=[0, (-55)*scl, 0]).add(c)
        r -= c
    # cutout for the cable
    c = touch_arc(lcd_hinge_inner_rad-20, 60, bwid,
                        25, scl,
                  angle=0)
    c = rotate([0, 90, 90]).add(c)
    c = rotate([0, lcd_ext_rot_angle+223+210, 0]).add(c)
    c = translate(v=[0, (24)*scl, 0]).add(c)
    r -= c
    c = touch_arc(lcd_hinge_inner_rad-20, 60, bwid,
                        25, scl,
                  angle=0)
    c = rotate([0, 90, 90]).add(c)
    c = rotate([0, lcd_ext_rot_angle+223+205, 0]).add(c)
    c = translate(v=[0, (26)*scl, 0]).add(c)
    r -= c
    t = hinge_translate(scl).add(r)
    t = translate(v=[0, (-ht/2+27.5-bwid)*scl, 0]).add(t)
    a += t

    # hinge hole
    r = union()
    r = cylinder(r=(screwrad-3)*scl, h=(ht*5+0.3)*scl, segments=50, center=True)
    r = rotate([180, 90, 90]).add(r)
    t = hinge_translate(scl).add(r)
    t = translate(v=[0, (-ht/2+16.5)*scl, 0]).add(t)
    a -= t

    return a

def friction_hinge_outer(scl, ht):

    a = union()

    # inner hexagon
    r = union()
    c = cylinder(r=43*scl, 
                        h=(bwid+35)*scl, segments=6, center=True)
    c = rotate([180, 90, 90]).add(c)
    r.add(c)
    c = cylinder(r=30*scl, 
                        h=(bwid*2)*scl, segments=50, center=True)
    c = rotate([180, 90, 90]).add(c)
    c = translate(v=[0, (bwid*2)*scl, 0]).add(c)
    r.add(c)
    c = cylinder(r=60*scl, r1=65*scl,
                        h=(bwid+5)*scl, segments=50, center=True)
    c = rotate([180, 90, 90]).add(c)
    c = translate(v=[0, -(bwid+2.5)*scl, 0]).add(c)
    r.add(c)
    c = cylinder(r=(28)*scl, # XXX: nuts are 4mm hex diameter!
                        h=(bwid*3)*scl, segments=6, center=True)
    c = rotate([180, 90, 90]).add(c)
    c = translate(v=[0, -(bwid-5)*scl, 0]).add(c)
    r -= c
    t = hinge_translate(scl).add(r)
    t = translate(v=[0, (-ht/2+27.5)*scl, 0]).add(t)
    a += t

    # hinge hole
    r = union()
    r = cylinder(r=screwrad*scl, h=(ht*5+0.3)*scl, segments=50, center=True)
    r = rotate([180, 90, 90]).add(r)
    t = hinge_translate(scl).add(r)
    t = translate(v=[0, (-ht/2+16.5)*scl, 0]).add(t)
    a -= t

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
    a += screen_frontedge(scl, ht, 0, toplenoffs, curvetopback=True)

    # middle filler
    r = union()
    c = shearedcube(size=[(lcd_d+lcd_gap*4)*scl,(w+lcd_gap*2)*scl,ht*scl],
                shear=[-shear*scl, 0, 0],
                innershear=[-innershear*scl, 0, 0])
    c = rotate([0, 90, 90]).add(c)
    r.add(c)
    t = translate(v=[(-lcd_inset_top+w+65)*scl, (16.5-ht)*scl,
                        (30+lcd_gap*2)*scl])
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
        h = cube([25*scl, 6*scl, (500)*scl])
        h = translate([-50*scl, (16.5-ht)*scl, -200*scl]).add(h)
        c += h
        h = cube([25*scl, 6*scl, (500)*scl])
        h = translate([40*scl, (16.5-ht)*scl, -200*scl]).add(h)
        c += h
        h = cube([25*scl, 6*scl, (500)*scl])
        h = translate([(boxlength-20)*scl, (16.5-ht)*scl, -200*scl]).add(h)
        c += h
        h = cube([25*scl, 6*scl, (300)*scl])
        h = translate([(boxlength-180)*scl, (16.5-ht)*scl, 0*scl]).add(h)
        c += h
        h = cube([45*scl, 6*scl, (500)*scl])
        h = translate([(boxlength+140)*scl, (16.5-ht)*scl, -200*scl]).add(h)
        c += h
        h = cube([(boxlength+20+200)*scl, 6*scl, (55)*scl])
        h = translate([(-50)*scl, (16.5-ht)*scl, -200*scl]).add(h)
        c += h
        h = cube([(boxlength+20+200)*scl, 6*scl, (55)*scl])
        h = translate([(-50)*scl, (16.5-ht)*scl, 245*scl]).add(h)
        c += h
        h = cube([(20+100)*scl, 6*scl, (25)*scl])
        h = translate([(boxlength+30)*scl, (16.5-ht)*scl, 50*scl]).add(h)
        c += h
        h = cube([(20+100)*scl, 6*scl, (25)*scl])
        h = translate([(-40)*scl, (16.5-ht)*scl, 2*scl]).add(h)
        c += h
        a.add(c)

    # hinge hole
    r = union()
    r = cylinder(r=45*scl, h=(ht+0.3)*scl, segments=6, center=True)
    r = rotate([180, 90, 90]).add(r)
    t = hinge_translate(scl).add(r)
    t = translate(v=[0, (-ht/2+16.5)*scl, 0]).add(t)
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
    """
        TODO:
        fill in between hinge-end small stop-part and screwhole support 2
        shrink cube screwhole supports top and bottom to stop "levering"
        when fitting against base_end
        add structural support bits on edge (inset by bwid) to stop
        base_end bowing inwards on long side
        fix curving on end T|L so that printhead is a bit happier
        create clips to lock matching base_end into place
    """
    # matches up with front_box_lid
    edge_inset = bwid
    a = union()

    border=3.0
    slot_depth = 100
    boxdepth = hinge_depth+ht+edge_inset # matches front_box_lid
    lid_depth = (boxlength-lcd_inset_bot+bwid-2)

    c = union()
    if True:
        curverads={
                   D|L:(80, 0),
                   D|R:(bwid*2, 0),
                   T|L:(bwid, 0), # XXX: gcode chops this separate
                   #B|L:(bwid, 0), # XXX: bug in hollowbox
                   D|B:(bwid, 0),
                   T|B:(bwid, 0),
                   }
        b = hollowbox(scl, boxlength, boxdepth, boxheight,
                        {T:bwid, B: bwid,
                        L:bwid, R:-1, F:-1, D:-1},
                        curverads=curverads)
        b = translate([0, 20*scl, 0*scl]).add(b)
        c.add(b)
        # short wall hinge-end
        b = cube([(bwid)*scl, (boxdepth-bwid)*scl, (boxinset-border)*scl])
        b = translate([(lid_depth-bwid)*scl, (20+bwid)*scl, 0*scl]).add(b)
        c.add(b)

        # back hinge-end cutout
        b = cube([(90)*scl, (boxdepth)*scl, (boxinset+100)*scl])
        b = translate([-1*scl, (20+bwid)*scl, (boxinset-border)*scl]).add(b)
        c -= b
        # front cut-out 
        b = cube([(400)*scl, (boxdepth)*scl, (boxinset+100)*scl])
        b = translate([(lid_depth)*scl, (bwid*2+3.0)*scl, (-1)*scl]).add(b)
        c -= b
    a.add(c)
    a = translate(v=[(30-lcd_inset_top)*scl, (-bwid)*scl,
                        (+50+boxtopoffs)*scl]).add(a)

    # insets for nuts and threaded bar
    holes = [0, 1, 2] if test else [0, 1, 2, 3]
    cdep = 60
    for end in holes:
        r = union()
        c = cylinder(r=26*scl, h=(cdep)*scl, segments=50)
        c = rotate([0, 90, 90]).add(c)
        r.add(c)
        if end == 2:
            dp = -3
        else:
            dp = 5
        c = cube([26*2*scl, cdep*scl, (27*2)*scl], center=True)
        c = translate(v=[(0)*scl, (cdep/2)*scl, (dp/2)*scl]).add(c)
        r.add(c)
        t = case_bolthole(scl, end=end).add(r)
        t = translate(v=[(0)*scl, (3+bwid-1)*scl, (boxheight)*scl]).add(t)
        a += t

    # add some structural support, algorithm matches up with
    # back_box lid_end base_mid
    sstep = 140
    sdep = sstep*2
    while sdep <= boxlength-sstep*2:
        h = cube([bwid*scl, 70*scl, 50*scl])
        h = translate(v=[sdep*scl, 10*scl, (60)*scl]).add(h)
        a.add(h)
        h = shearedcube([25*scl, 15*scl, 20*scl],
                shear=[-10*scl, 0, 0], innershear=[0,0,0])
        h = rotate([0, 0, 90]).add(h)
        h = translate(v=[sdep*scl, bwid*scl,
                    (boxheight+50+boxtopoffs-bwid-20)*scl]).add(h)
        a.add(h)
        sdep += sstep

    # screw holes in box
    t = box_screwholes(scl, edge_inset, holes=holes)
    t = translate(v=[0, 0, boxheight*scl]).add(t)
    a -= t

    # hollow out tube including base box
    t = hollow_out_edge(scl, 100, ht, border)
    a -= t

    if pin_parts_3d:
        c = union()
        h = cube([25*scl, 6*scl, (500)*scl])
        h = translate([-50*scl, (16.5-ht)*scl, -200*scl]).add(h)
        c += h
        h = cube([25*scl, 6*scl, (500)*scl])
        h = translate([60*scl, (16.5-ht)*scl, -200*scl]).add(h)
        c += h
        h = cube([25*scl, 6*scl, (500)*scl])
        h = translate([(boxlength+8)*scl, (16.5-ht)*scl, -200*scl]).add(h)
        c += h
        h = cube([25*scl, 6*scl, (500)*scl])
        h = translate([(boxlength-120)*scl, (16.5-ht)*scl, -200*scl]).add(h)
        c += h
        h = cube([45*scl, 6*scl, (500)*scl])
        h = translate([(boxlength+140)*scl, (16.5-ht)*scl, -200*scl]).add(h)
        c += h
        h = cube([(boxlength+20+200)*scl, 6*scl, (55)*scl])
        h = translate([(-50)*scl, (16.5-ht)*scl, -200*scl]).add(h)
        c += h
        h = cube([(boxlength+20+200)*scl, 6*scl, (55)*scl])
        h = translate([(-50)*scl, (16.5-ht)*scl, 245*scl]).add(h)
        c += h
        h = cube([(20+200)*scl, 6*scl, (25)*scl])
        h = translate([(boxlength-40)*scl, (16.5-ht)*scl, 150*scl]).add(h)
        c += h
        h = cube([(20+100)*scl, 6*scl, (25)*scl])
        h = translate([(-40)*scl, (16.5-ht)*scl, 95*scl]).add(h)
        c += h
        c = translate([0*scl, (26.5)*scl, -5*scl]).add(c)
        a += c

    return a

def chamfered_backbox_screwholes(scl, sht):
    # chamfered screw holes in top of lid 
    c = union()
    c.add(cylinder(r=topscrewrad*scl, r1=topscrewrad*2*scl,
                    h=((bwid+1)/2)*scl,
                    segments=50, center=True))
    d = cylinder(r=topscrewrad*scl, 
                    h=(bwid+2.5)*scl,
                    segments=50, center=True)
    d = translate(v=[0, 0, +(bwid+0.2)*0.5*scl]).add(d)
    c.add(d)
    c = rotate([180, 0, 0]).add(c)
    return c


def back_box_lidfront(scl, ht_offset, ht, extraht, boxextraht):
    edge_inset = bwid
    bht = bwid*3-10
    blen = ht+extraht
    a = union()
    c = hollowbox(scl, bdep-ethdep+100+lidfront_offs+bwid, blen+boxextraht, bht,
                    {T:hthick, B: -1, L:bwid, R:-1, F:-1, D:-1},
                    curverads={ T|L:(bwid, 0),
                               })
    c = translate(v=[(-100-lidfront_offs-bwid)*scl,
                    0*scl, (lcd_d-15+bwid)*scl]).add(c)
    a.add(c)
    # cutout at outer edge for base_end2 bits to poke through
    c = cube([159*scl, (extraht+48)*scl, 200*scl])
    c = translate(v=[(55)*scl,
                    -1*scl, (lcd_d-15+bwid-1)*scl]).add(c)
    
    a -= c
    for ((x,y,z), sht) in backboxsupports(blen-extraht, csw,
                                            overhanglid=boxextraht,
                                            underhanglid=25,
                                            frontlidonly=True):
        c = screwsupport(scl, csw, csw, sht)
        c = translate(v=[x,y,z]).add(c)
        c = translate(v=[-csw/2.0*scl, -csw/2.0*scl, 0]).add(c)
        c = translate(v=[-99*scl, extraht*scl, -7*scl]).add(c)
        a += c

    a = translate(v=[(lcd_w+35-bdepoffs)*scl, 0, 0]).add(a)

    # cutout in lid which matches the base_mid screwhole cross-supports
    c = cube([(59+2)*2*scl, (extraht+56)*scl, 25*scl])
    c = translate(v=[(-29-2)*scl,
                    (ht+extraht-45-1)*scl, (105)*scl]).add(c)
    c = case_bolthole(scl, end=2).add(c)
    a -= c

    # supports for threads, one (end=1) needs a cutout in the base box
    dep = 40
    holes = [(1, extraht+45), (2, extraht+105),
                (2, (blen-dep)/2.0), (2, blen-dep-50)]
    for (end, offs) in holes:
        r = union()
        if end == 1:
            dp = 70
        else:
            dp = 0
        c = cube([29*2*scl, dep*scl, (dp+29*2)*scl], center=True)
        c = translate(v=[(0)*scl, (dep/2.0)*scl, (-dp/2)*scl]).add(c)
        r.add(c)
        t = case_bolthole(scl, end=end).add(r)
        t = translate(v=[(0)*scl, (offs)*scl, (boxheight)*scl]).add(t)
        a += t

    # screw holes in box
    t = box_screwholes(scl, edge_inset, holes=[1,2])
    t = translate(v=[0, 0, boxheight*scl]).add(t)
    a -= t

    return a

def back_box_lid(scl, ht_offset, ht, extraht):
    edge_inset = bwid
    bht = bwid*2+hthick-10
    blen = ht
    a = union()
    c = hollowbox(scl, ethdep+hthick, blen+extraht, bht,
                    {T:hthick, B: -1, L:hthick, R:-1, F:-1, D:-1},
                    curverads={ T|L:(hthick, 0),
                               T|R:(hthick, 0),
                               B|R:(bwid, 0),
                               })
    c = translate(v=[(bdep-ethdep-hthick)*scl, 0, (lcd_d-22-hthick)*scl]).add(c)
    a.add(c)
    # ok limitations of hollowbox we need to cut out the back right corner
    c = cube([159*scl, (bwid+1)*scl, 50*scl])
    c = translate(v=[(ethdep+bwid)*scl,
                    -0.9*scl, (lcd_d-22)*scl]).add(c)
    
    a -= c

    for ((x,y,z), sht) in backboxsupports(blen, csw, overhanglid=extraht,
                                                backlidonly=True):
        c = screwsupport(scl, csw, csw, sht)
        c = translate(v=[x,y,z]).add(c)
        c = translate(v=[-csw/2.0*scl, -csw/2.0*scl, 0]).add(c)
        c = translate(v=[-99*scl, 0*scl, -(12)*scl]).add(c)
        a += c

    a = translate(v=[(lcd_w+35-bdepoffs)*scl, 0, 0]).add(a)

    return a

def backboxsupports(blen, csw, overhanglid=0, onlyoverhang=False,
                               underhanglid=None,
                               backlidonly=False,
                               frontlidonly=False):
    l = []
    if not onlyoverhang:
        fl = [
            # these are for the keyboard lid
            ([(bdep+98-ethdep-csw/2)*scl, (blen-csw/2-100)*scl,
                                           (lcd_d-32+bwid*3)*scl],
                (backboxheight-bwid*2-hthick)),
            ([(csw/2-lidfront_offs-0.5)*scl,
                (blen*0.45-csw/2)*scl, (lcd_d-32+bwid*3)*scl],
                (backboxheight-bwid*2-hthick)),
            ([(csw/2-lidfront_offs-0.5)*scl, 
                (blen-csw/2-19)*scl, (lcd_d-32+bwid*3)*scl],
                (backboxheight-bwid*2-hthick)),
            ([(csw/2-lidfront_offs-0.5)*scl, 
                (csw/2+19)*scl, (lcd_d-32+bwid*3)*scl],
                (backboxheight-bwid*2-hthick)),
            ([(bdep+98-ethdep-csw/2)*scl, 
                (csw/2+bwid+30)*scl, (lcd_d-32+bwid*3)*scl],
                (backboxheight-bwid*2-hthick)),
            ]
        bl = [
            # towards back of box
            ([(bdep+100-csw/2-19)*scl, (19+csw/2)*scl, (lcd_d-22)*scl], 
                backboxheight),
            ([(bdep+100-csw/2-19)*scl, (320+csw/2)*scl, (lcd_d-22)*scl], 
                backboxheight),
            ([(bdep+100-ethdep+csw/2-1)*scl, (19+csw/2)*scl, (lcd_d-22)*scl], 
                backboxheight),
            ([(bdep+100-ethdep+csw/2-1)*scl, (blen-csw/2-19)*scl, (lcd_d-22)*scl], 
                backboxheight),
            ([(bdep+100-csw/2-19)*scl, (blen-csw/2-19)*scl, (lcd_d-22)*scl], 
                backboxheight),
        ]
        if backlidonly:
            l = bl
        elif frontlidonly:
            l = fl
        else:
            l = bl + fl
    if overhanglid:
        _blen = blen + overhanglid
        if not frontlidonly:
            l += [
            # towards back of box
            ([(bdep+100-csw/2-bwid-2)*scl, (_blen-csw/2)*scl, (lcd_d-22)*scl], 
                backboxheight),
            ]
        if not backlidonly:
            l += [
            # these are for the keyboard lid
            ([(csw/2-12)*scl, (_blen-csw/2)*scl, (lcd_d-32+bwid*3)*scl],
                (backboxheight-bwid*3)),
        ]
    if underhanglid is not None:
        l += [
            # these are for the keyboard lid
            ([(csw/2-12)*scl, (-underhanglid-csw/2)*scl,
                                           (lcd_d-32+bwid*3)*scl],
                (backboxheight-bwid*2-hthick)),
        ]
    return l

def back_box_base(scl, ht_offset, ht, midpart=False, frontpart=False):
    """
    TODO:
    * underfill (shearedcube) underneath the screwhole supports
    * add some "part pinning" as the edges warped and lifted off
    * reduce thickness of floor
    """
    edge_inset = bwid
    blen = ht
    a = union()
    curverads={ D|R:(bwid, 0),
               }
    if not midpart:
        # XXX: minor problem with this one, it covers the screwhole support
        # in the corner.
        curverads[B|R] = (bwid, 0)
    c = hollowbox(scl, ethdep, blen, backboxheight,
                    {T:-1, B: bwid, L:-25.0, R:bwid, F:bwid, D:hthick},
                    curverads=curverads)
    c = translate(v=[(bdep+100-ethdep)*scl, 0, (lcd_d-22)*scl]).add(c)
    a.add(c)
    c = hollowbox(scl, bdep+100+lidfront_offs-ethdep+1, blen, boxheight-hthick,
                    {T:-1, B: bwid, L:-25.0, R:-1, F:bwid, D:hthick})
    c = translate(v=[-lidfront_offs*scl, 0, (lcd_d-32+bwid*2+hthick)*scl]).add(c)
    a.add(c)

    if not midpart:
        overhanglid = 0
        boxlen = blen
        onlyoverhang = False
    else:
        overhanglid = 35 # XXX: total guess-work
        boxlen = 0
        onlyoverhang = True
    # add corner supports
    for ((x,y,z), sht) in backboxsupports(boxlen, csw, overhanglid=overhanglid,
                                            onlyoverhang=onlyoverhang):
        c = chamfered_backbox_screwholes(scl, sht)
        c = translate(v=[x,y,(backboxheight+7+bwid)*scl]).add(c)
        if midpart:
            c = translate(v=[0, 35*scl, 0]).add(c) # XXX: guesswork!
        a -= c
        if midpart:
            c = translate(v=[0, 55*scl, 0]).add(c) # XXX: guesswork!
            a -= c

    a = translate(v=[(lcd_w+35-100-bdepoffs)*scl, 0, 0]).add(a)

    if frontpart:
        a += front_box_base(scl, ht_offset, ht, dep=lcd_w-80, midpart=True)

    # add a structural support for bolthole (nut lock point)
    # has to be extended slightly so that the lid can sit on top of it
    hwid = 45.0 if not midpart else ht/2+1
    hoffsl = [(2, 0), (2, blen-hwid)]
    if not midpart:
        hoffsl += [(1, 0)]
    if midpart and not test:
        hoffsl += [(3, 0), (3, blen-hwid)]
    for (hole, offs) in hoffsl:
        r = union()
        doffs = 0
        if midpart and hole == 2:
            doffs = -70
            dp = 70
        elif hole == 2 or hole == 3:
            dp = 0
        else:
            dp = 50
        c = cube([29*2*scl, hwid*scl, (dp+29*2)*scl], center=True)
        c = translate(v=[(0)*scl, (hwid/2-3)*scl, (-dp/2-doffs)*scl]).add(c)
        r.add(c)
        if hole == 2:#and offs == 0:
            c = cube([29*2*scl, hwid*scl, (dp+29*2)*scl], center=True)
            c = translate(v=[(+25.5*2)*scl, (hwid/2-3)*scl,
                        (dp/2)*scl]).add(c)
            r.add(c)
        t = case_bolthole(scl, end=hole).add(r)
        t = translate(v=[(0)*scl, (offs+3)*scl, (boxheight)*scl]).add(t)
        a += t

    # screw holes in box
    holes = [1,2] if not midpart else [2]
    if midpart and not test:
        holes.append(3)
    t = box_screwholes(scl, edge_inset, holes=holes)
    t = translate(v=[0, 0, boxheight*scl]).add(t)
    a -= t

    if not midpart:
        # this is a cut-out so that the lid's thread-support goes through
        dep = 40
        for (end, offs) in [(1, 45), ]:
            r = union()
            dp = 0
            c = cube([29*2*scl, dep*scl, (30+29*2)*scl], center=True)
            c = translate(v=[(0)*scl, (dep/2.0)*scl, (-dp/2)*scl]).add(c)
            r.add(c)
            t = case_bolthole(scl, end=end).add(r)
            t = translate(v=[(0)*scl, (offs)*scl, (boxheight)*scl]).add(t)
            a -= t

        # match up with base_end2 hinge location
        r = union()
        r = cylinder(r=16*scl,
                            h=90*scl, segments=50, center=True)
        r = rotate([180, 90, 90]).add(r)
        t = hinge_translate(scl).add(r)
        t = translate(v=[0, (-bwid/2+0.5)*scl, 0]).add(t)
        a -= t

    if not midpart:
        # cutout in other side for cable
        h = cube([(85)*scl, (50)*scl,
                   (50)*scl])
        h = translate(v=[(boxlength-bwid-125)*scl,
                            (-32-0.2)*scl, (120)*scl]).add(h)
        a -= h

    if not midpart:
        a -= ethernet(scl)

    return a

def frontboxsupports(blen, dep, csw, overhanglid=0, onlyoverhang=False,
                               underhanglid=None,
                               touchpaneltray=None):
    l = []
    if not onlyoverhang:
        l = [
            # these are for the keyboard lid
            ([(dep-csw/2)*scl, (blen-csw/2)*scl,
                                           (lcd_d-32+bwid*3)*scl],
                (backboxheight-bwid*2-hthick)),
            ([(csw/2+124-0.5)*scl, 
                (blen*0.45-csw/2)*scl, (lcd_d-32+bwid*3)*scl],
                (backboxheight-bwid*2-hthick)),
            ([(csw/2+124-0.5)*scl, 
                (blen-csw/2)*scl, (lcd_d-32+bwid*3)*scl],
                (backboxheight-bwid*2-hthick)),
            ([(csw/2+124-0.5)*scl, 
                (csw/2+bwid+2)*scl, (lcd_d-32+bwid*3)*scl],
                (backboxheight-bwid*2-hthick)),
            ([(dep-csw/2)*scl, 
                (csw/2+bwid+2)*scl, (lcd_d-32+bwid*3)*scl],
                (backboxheight-bwid*2-hthick)),
            ]
    if overhanglid:
        _blen = blen + overhanglid
        l += [
            # these go into base_end2
            ([(csw/2-12)*scl, (_blen-csw/2)*scl, (lcd_d-32+bwid*3)*scl],
                (backboxheight-bwid*2-hthick)),
        ]
    if touchpaneltray is not None:
        _blen = blen + touchpaneltray
        l += [
            # these go into base_end2
            ([(csw/2+124-0.5)*scl, (_blen-csw/2)*scl, (lcd_d-32+bwid*3)*scl],
                (backboxheight-bwid*2-hthick)),
            ([(dep-csw/2)*scl, (_blen-csw/2)*scl, (lcd_d-32+bwid*3)*scl],
                (backboxheight-bwid*2-hthick)),
        ]
    if underhanglid is not None:
        l += [
            # these are for the keyboard lid
            ([(csw/2+120-0.5)*scl, (-underhanglid-csw/2)*scl,
                                           (lcd_d-32+bwid*3)*scl],
                (backboxheight-bwid*2-hthick)),
            ([(dep-csw/2-0.5)*scl, (-underhanglid-csw/2)*scl,
                                           (lcd_d-32+bwid*3)*scl],
                (backboxheight-bwid*2-hthick)),
        ]
    return l

def front_box_lid(scl, ht_offset, ht, extraht=0):
    """
    TODO:
    * reduce thickness of ceiling
    """
    # matches up with lid_end
    edge_inset = bwid
    bht = boxheight-88 # XXX: magic number...
    flen = ht+extraht
    boxextraht = 0
    a = union()
    c = hollowbox(scl, fdep, flen, bht,
                    {T:hthick, B: -1, L:bwid, R:-1, F:bwid, D:-1},
                    curverads={ T|L:(bwid, 0),
                               })
    c = translate([5*scl, 0, (+50+boxtopoffs)*scl]).add(c)
    a.add(c)

    for ((x,y,z), sht) in frontboxsupports(flen-extraht, fdep, csw,
                                            overhanglid=boxextraht,
                                            underhanglid=18):
        c = screwsupport(scl, csw, csw, sht)
        c = translate(v=[x,y,z]).add(c)
        c = translate(v=[-csw/2.0*scl, -csw/2.0*scl, 0]).add(c)
        c = translate(v=[5*scl, extraht*scl, -7*scl]).add(c)
        a += c

    # bridge between supports, stops front box from moving about
    # XXX: magic constants
    c = cube([30*scl, (extraht+56)*scl, 44*scl])
    c = translate(v=[(fdep-25)*scl,
                    (extraht-65-1)*scl, (60)*scl]).add(c)
    a += c

    # supports for threads, one (end=1) needs a cutout in the base box
    dep = 20
    holes = [(0, extraht+50), 
                (0, (flen-dep)/2.0), (0, flen-dep)]
    for (end, offs) in holes:
        r = union()
        if end == 0:
            dp = 70
        else:
            dp = 0
        c = cube([29*2*scl, dep*scl, (dp+31*2)*scl], center=True)
        c = translate(v=[(0)*scl, (dep/2.0)*scl, (-dp/2)*scl]).add(c)
        r.add(c)
        t = case_bolthole(scl, end=end).add(r)
        t = translate(v=[(0)*scl, (offs)*scl, (boxheight)*scl]).add(t)
        a += t

    # screw holes in box
    t = box_screwholes(scl, edge_inset, holes=[0])
    t = translate(v=[0, 0, boxheight*scl]).add(t)
    a -= t

    return a

def front_box_base(scl, ht_offset, ht, lid_ht=0, extraht=0, dep=None, midpart=False):
    """
    TODO:
    * add in small runner supports for long bolt so it doesn't bow box
    * make a small cut-out so that front lid can drop hooks down to the
      long bolt (like in back box)
    * put a similar support into the opposite wall on the long bolt
    * reduce thickness of floor
    """
    if dep is None:
        dep = fdep
    edge_inset = bwid
    bht = boxheight-boxinset
    blen = ht
    flen = lid_ht+extraht
    a = union()
    c = hollowbox(scl, dep, blen, bht,
                    {T:-1, B: bwid, R:-25.0, L:bwid, F:bwid, D:hthick},
                    curverads={ D|L:(80, 0),
                               })
    c = translate(v=[(5)*scl, 0, (lcd_d-32+bwid*2+boxinset)*scl]).add(c)
    a.add(c)

    # add a structural support for bolthole (nut lock point)
    hwid = 25
    hoffsl = [(0, hwid/2), (0, blen-hwid*1.5)]
    if not midpart:
        hoffsl += [(0, (blen-hwid)/2)]
    for (hole, offs) in hoffsl:
        r = union()
        doffs = 0
        dp = 0
        c = cube([29*2*scl, hwid*scl, (dp+29*2)*scl], center=True)
        c = translate(v=[(0)*scl, (hwid/2-3)*scl, (-dp/2-doffs)*scl]).add(c)
        r.add(c)
        t = case_bolthole(scl, end=hole).add(r)
        t = translate(v=[(0)*scl, (offs+3)*scl, (boxheight)*scl]).add(t)
        a += t

    if not midpart:
        # XXX: magic constant for length and touchpaneltray arg
        for ((x,y,z), sht) in frontboxsupports(blen-130, fdep, csw, 0,
                                                touchpaneltray=57):
            c = chamfered_backbox_screwholes(scl, sht)
            c = translate(v=[x,y,(backboxheight+7+bwid)*scl]).add(c)
            a -= c

    if not midpart:
        # this is a cut-out so that the lid's thread-support goes through
        hdep = 24
        dep = 20
        holes = [(0, extraht+50), 
                    (0, (flen-dep)/2.0), (0, flen-dep),
                    (0, blen+20) # XXX: magic number, for touchpanel tray
                ]
        for (end, offs) in holes:
            r = union()
            dp = 0
            c = cube([31*2*scl, hdep*scl, (40+29*2)*scl], center=True)
            c = translate(v=[(0)*scl, (hdep/2.0)*scl, (-dp/2)*scl]).add(c)
            r.add(c)
            t = case_bolthole(scl, end=end).add(r)
            t = translate(v=[(0)*scl, (offs-extraht-(hdep-dep)/2)*scl,
                    (boxheight)*scl]).add(t)
            a -= t


    # screw holes in box
    t = box_screwholes(scl, edge_inset, holes=[0])
    t = translate(v=[0, 0, boxheight*scl]).add(t)
    a -= t

    return a

def base_mid(scl, ht_offset, ht, hinge_depth, hole_depth, mid=False):
    edge_inset = bwid
    a = union()
    a += back_box_base(scl, ht_offset, ht, midpart=True, frontpart=True)

    # add some structural support, algorithm matches up with
    # back_box lid_end
    sstep = 140
    sdep = sstep
    while sdep <= boxlength-sstep*3:
        h = cube([bwid*scl, ht*scl, 50*scl])
        h = translate(v=[sdep*scl, 0*scl, (boxheight)*scl]).add(h)
        a.add(h)
        sdep += sstep

    return a

def screwsupport(scl, w, d, h):
    sht = 80 # screw hole height: 8mm screws
    u = union()
    u.add(cube([w*scl, d*scl, h*scl]))
    sh = cylinder(r=topscrewrad*scl, h=sht*scl, center=True, segments=50)
    sh = translate(v=[w/2.0*scl, d/2.0*scl, +(h-sht/2+0.5)*scl]).add(sh)
    u -= sh
    return u

def base_end2(scl, ht_offset, ht, hinge_depth, hole_depth, mid=False):
    edge_inset = bwid
    a = union()

    border=3.0 # move cylinders inwards so that lid cylinders fit around them
    slot_depth = 100
    extradepth = 0
    boxdepth = hinge_depth+ht

    if mid:
        extradepth = 140
    else:
        # inner tube
        r = union()
        r = cylinder(r=(lcd_hinge_inside_rad-border)*scl, h=(boxdepth)*scl,
                     segments=50, center=True)
        r = rotate([180, 90, 90]).add(r)
        t = hinge_translate(scl).add(r)
        t = translate(v=[0, (-27-bwid+boxdepth/2)*scl, 0]).add(t)
        a.add(t)

    # base hinge box
    box = base_box(scl, boxdepth, hole_depth, ht, extralen=extradepth,
                   hollow=True, inner=True)

    a += box

    # add corner supports
    # XXX: locations are all a bit bogus (magic numbers)
    for ((x,y,z), sht) in backboxsupports(0, csw, underhanglid=-10,
                                            onlyoverhang=True):
        c = chamfered_backbox_screwholes(scl, sht)
        c = translate(v=[x,y,(boxdepth+92+bwid)*scl]).add(c)
        c = translate(v=[(lcd_w-80)*scl, 0, 0]).add(c)
        a -= c

    for ((x,y,z), sht) in frontboxsupports(0, fdep, csw,
                                            onlyoverhang=True,
                                            underhanglid=-18): # XXX: magic
        c = chamfered_backbox_screwholes(scl, sht)
        c = translate(v=[x,y,(backboxheight+7+bwid)*scl]).add(c)
        a -= c

    # hollow out the inner tube
    ho = hollow_out_basebox(scl, border, boxdepth)
    t = translate(v=[0, (-60.5-bwid)*scl, 0]).add(ho)
    a -= t

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
        h = cube([(105)*scl, (boxdepth)*scl,
                   (60)*scl])
        h = translate(v=[(boxlength-bwid-100)*scl,
                            (-72-0.2)*scl, (73)*scl]).add(h)
        a -= h

        # arc cutout for cable
        r = union()
        cable_slot_depth = 60
        c = touch_arc(lcd_hinge_inner_rad-10, cable_slot_depth, bwid,
                            20, scl,
                      angle=33)
        c = rotate([180, 90, 90]).add(c)
        c = rotate([0, lcd_ext_rot_angle+96, 0]).add(c)
        r += c
        t = hinge_translate(scl).add(r)
        t = translate(v=[0, (hinge_depth-ht-cable_slot_depth/2-22)*scl,
                         0]).add(t)
        a -=t

        # cutout in other side for cable
        h = cube([(85)*scl, (boxdepth)*scl,
                   (50)*scl])
        h = translate(v=[(boxlength-bwid-125)*scl,
                            (-32-0.2)*scl, (120)*scl]).add(h)
        a -= h

        # fill-in just above front box lid, in between two screwholes
        # XXX: magic numbers here... *sigh*
        h = cube([(100)*scl, (bwid)*scl,
                   (55)*scl])
        h = translate(v=[(boxlength-bwid-260)*scl,
                            (bwid+2.5)*scl, (53+hthick)*scl]).add(h)
        a += h

    # hinge hole, for friction hinge to poke through and support back box
    r = union()
    r = cylinder(r=16*scl,
                        h=(ht+90+0.3)*scl, segments=50, center=True)
    r = rotate([180, 90, 90]).add(r)
    t = hinge_translate(scl).add(r)
    t = translate(v=[0, (-ht/2+28.5)*scl, 0]).add(t)
    a -= t

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
    t = translate(v=[0, (hinge_depth-hinge_depth/2+16.5-10)*scl, 0]).add(t)
    return t

def base_end(scl, ht_offset, ht, hinge_depth, hole_depth, innerpart=False):
    """
        TODO:
        fill in between lid screwhole gap 1 and 2
        increase size of insets a bit to fit with the lid
    """
    edge_inset = bwid
    a = union()

    border=3.0 # move cylinders inwards so that lid cylinders fit around them
    slot_depth = 100

    # inner tube
    r = union()
    r = cylinder(r=(lcd_hinge_inside_rad-border)*scl, h=(hinge_depth-10)*scl,
                        segments=50, center=True)
    r = rotate([180, 90, 90]).add(r)
    t = hinge_translate(scl).add(r)
    t = translate(v=[0, (hinge_depth-hinge_depth/2+6.5-5)*scl, 0]).add(t)
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

    # hollow out base box at edge
    box -= hollow_out_edge(scl, hole_depth, ht, border)

    a += box

    # hollow out tube including base box
    a -= hollow_out_basebox(scl, border, hinge_depth)

    soffset = -30.0
    if test:
        l = [(0, 26), (1, -46), (2, 26)]
    else:
        l = [(0, 26), (1, -46), (2, 26), (3, -46), (3, 26)]
    for (end, offs) in l:
        doffs = boxheight-45
        if end == 2:
            doffs += 20
        b = cube([20*scl, (boxdepth-63.5)*scl, (60)*scl])
        t = case_bolthole(scl, end=end).add(b)
        t = translate(v=[(offs)*scl, (-boxdepth/2+105+soffset)*scl, doffs*scl]).add(t)
        a += t
    b = cube([25*scl, (boxdepth-70)*scl, (bwid*1.2)*scl])
    t = case_bolthole(scl, end=0).add(b)
    t = translate(v=[(20)*scl, (-boxdepth/2+105+soffset)*scl, (boxheight)*scl]).add(t)
    a += t

    # screw support at both ends
    for end in range(3 if test else 4):
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
        t = translate(v=[(0)*scl, (-hinge_depth/2+3+soffset)*scl,
                    (boxheight-bwid)*scl]).add(t)
        a += t

        b = cube([29.1*2*scl, 70*scl, bht*scl])
        b = translate([-29.1*scl, 10*scl, -30*scl]).add(b)
        t = case_bolthole(scl, end=end).add(b)
        t = translate(v=[(0)*scl, (-hinge_depth/2+3+soffset)*scl,
                    (boxheight)*scl]).add(t)
        a -= t

        r = union()
        c = cube([29*2*scl, 48*scl, 29*1.7*scl])
        r += translate([-29*scl, 80*scl, -28*scl]).add(c)
        t = case_bolthole(scl, end=end).add(r)
        t = translate(v=[(0)*scl, (-hinge_depth/2+3+soffset)*scl,
                        (boxheight)*scl]).add(t)
        a += t

    # screw holes in box
    t = box_screwholes(scl, edge_inset)
    t = translate(v=[0, 0, boxheight*scl]).add(t)
    a -= t

    # additional support for friction hinge
    r = union()
    cable_slot_depth = 30
    for ang in [0, 180]:
        c = touch_arc(lcd_hinge_inner_rad-20, cable_slot_depth, bwid,
                            10, scl,
                      angle=65)
        c = rotate([180, 90, 90]).add(c)
        c = rotate([0, lcd_ext_rot_angle+168+ang, 0]).add(c)
        r += c
    t = hinge_translate(scl).add(r)
    t = translate(v=[0, (hinge_depth-ht-cable_slot_depth/2)*scl,
                     0]).add(t)
    a +=t

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
        curverads={
                   D|L:(80, 0),
                   D|R:(bwid*2, 0),
                   }
        b = hollowbox(scl, blen, boxdepth, boxheight,
                        {T:-1, B: -1,
                        L:bwid, R:bwid*3, F:bwid, D:bwid},
                        curverads=curverads)
        b = translate([0, 20*scl, 0*scl]).add(b)
        c.add(b)
        if inner:
            hoffs=bwid*2
            bl = blen-bwid*2
        else:
            hoffs = -0.3
            bl = blen-lcd_outer_rad-80-bwid*2
        # cut out top front part of box (for base lid, keyboard etc.)
        h = cube([(boxlength-lcd_outer_rad-80-bwid+0.3)*scl,
                   (boxdepth+bwid+0.3)*scl,
                   (boxinset+0.3)*scl])
        h = translate(v=[(-0.3)*scl, (bwid-0.3)*scl, -0.3*scl]).add(h)
        c -= h

        if not inner:
            h = cube([(bwid+0.5)*scl, (boxdepth)*scl,
                       (boxheight)*scl])
            h = translate(v=[(blen-lcd_outer_rad-80-bwid)*scl, 20*scl,
                              -0.0*scl]).add(h)
            c += h

        if not inner:
            # add some structural support, algorithm matches with base_mid
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

        if pin_parts_3d:
            p = union()
            h = cube([25*scl, 6*scl, (500)*scl])
            h = translate([-50*scl, (boxdepth+10)*scl, -200*scl]).add(h)
            p += h
            h = cube([(90)*scl, 6*scl, (20)*scl])
            h = translate([(-50)*scl, (boxdepth+10)*scl, 55*scl]).add(h)
            p += h
            if not test:
                for m in [0.2, 0.45, 0.7]:
                    h = cube([17*scl, 6*scl, (500)*scl])
                    h = translate([(boxlength*m)*scl,
                                   (boxdepth+10)*scl, -200*scl]).add(h)
                    p += h
            h = cube([17*scl, 6*scl, (500)*scl])
            h = translate([70*scl, (boxdepth+10)*scl, -200*scl]).add(h)
            p += h
            h = cube([15*scl, 6*scl, (500)*scl])
            h = translate([(boxlength)*scl, (boxdepth+10)*scl, -200*scl]).add(h)
            p += h
            h = cube([25*scl, 6*scl, (300)*scl])
            h = translate([(boxlength-180)*scl, (boxdepth+10)*scl,
                        -200*scl]).add(h)
            p += h
            h = cube([45*scl, 6*scl, (500)*scl])
            h = translate([(boxlength+110)*scl, (boxdepth+10)*scl,
                        -200*scl]).add(h)
            p += h
            h = cube([(boxlength+20+150)*scl, 6*scl, (55)*scl])
            h = translate([(-40)*scl, (boxdepth+10)*scl, -200*scl]).add(h)
            p += h
            h = cube([(boxlength+20+150)*scl, 6*scl, (55)*scl])
            h = translate([(-40)*scl, (boxdepth+10)*scl, 245*scl]).add(h)
            p += h
            h = cube([(20+100)*scl, 6*scl, (25)*scl])
            h = translate([(boxlength+10)*scl, (boxdepth+10)*scl,
                        -10*scl]).add(h)
            p += h
            p = translate([0, 4*scl, 0]).add(p)
            c += p

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
    #if part != 1 and part != 7:
    #if part > 3:
    #if part > 6:
    #    return
    #if part != 0 and part != 2 and part != 4 and part != 5 and part != 3:
    #if part != 8 and part != 6 and part != 9 and part != 1 and part != 7 and \
    #    part != -0 and part != -4 and part != 10 and part != 11 and \
    #    part != 12:
    #    return
    #if part != 1 and part != 7 and part != 6 and part != 11 and \
    #    part != 0.1 and part != 8 and part != 12:
    if part != 9 and part != 12:
    #if part != 10 and part != 11 and part != 12 and part != 8 and \
        #part != 6 and part != 9 and part != 15 and part != 7:
    #if part != 8 and part != 1 and part != 6:
    #if part != -6 and part != 0 and part != 1 and part != 7 and part != -13 \
    #    and part != 2 and part != 4 and part != 3:
        return

    c = color(colour)
    c.add(t)

    b = union()

    if part == 0:
        b.add(screen_end(scl, lcd_end_ht))
        m = screen_mid1(scl, hinge_depth, hole_depth, halfhollow=True)
        m = translate(v=[0, lcd_end_ht*scl,0]).add(m)
        b.add(m)
        #ht2 += lcd_end_ht

        b = screen_adjust(b, scl, angle)

    ht = 40
    if part == 1:
        b.add(base_end(scl, lcd_end_ht, ht, hinge_depth, hole_depth))
    if part == 7:
        b.add(lid_end(scl, lcd_end_ht, ht, hinge_depth, hole_depth))
    if part == 13:
        b.add(friction_hinge_outer(scl, ht))

    base_ht = 40

    if part == 14:
        h = friction_hinge_inner(scl, ht)
        h = translate(v=[0, (lcd_end_ht+ht+hinge_depth)*scl,0]).add(h)
        b.add(h)

    offs = (lcd_end_ht+ht+hinge_depth+base_ht+40)
    mid_ht = 140
    wid = lcd_l/2-offs-mid_ht/2
    if part == 8:
        print "wid, offs",  wid, offs
        e = back_box_base(scl, lcd_end_ht, wid)
        e = translate(v=[0, offs*scl,0]).add(e)
        b.add(e)

    if part == 10:
        e = back_box_lid(scl, lcd_end_ht, wid, mid_ht/2)
        e = translate(v=[0, offs*scl,0]).add(e)
        b.add(e)

    if part == 11:
        e = back_box_lidfront(scl, lcd_end_ht, wid, base_ht+40, mid_ht/2)
        e = translate(v=[0, (offs-base_ht-40)*scl,0]).add(e)
        b.add(e)

    if test:
        tpanel_wid = 400.0
    else:
        tpanel_wid = 700.0
    front_lid_ht = wid+mid_ht/2-tpanel_wid/2
    if part == 15:
        # 
        e = front_box_lid(scl, lcd_end_ht, front_lid_ht, extraht=(base_ht+40))
        e = translate(v=[0, (offs-base_ht-40)*scl,0]).add(e)
        b.add(e)

    if part == 9:
        e = front_box_base(scl, lcd_end_ht, wid,
                        front_lid_ht, extraht=(base_ht+40))
        e = translate(v=[0, offs*scl,0]).add(e)
        b.add(e)

    if part == 6:
        e = base_end2(scl, lcd_end_ht, ht, base_ht, hole_depth)
        e = translate(v=[0, (lcd_end_ht+ht+hinge_depth)*scl,0]).add(e)
        b.add(e)

    if part == 12:
        e = base_mid(scl, lcd_end_ht, mid_ht, base_ht, hole_depth)
        e = translate(v=[0, (offs+wid)*scl,0]).add(e)
        b.add(e)

    numparts = 10 if test else 30
    offs = lcd_end_ht+hinge_depth
    midht = (lcd_l/2.0-offs+bwid-50.0) / numparts

    for i in range(1 if part == 2 else numparts):
        m = None
        if part == 2:
            m = screen_mid1(scl, midht, hole_depth, nohinge=True,
                                fillinner=True, endpart=False)
        if part == 3:
            m = screen_mid1(scl, midht, hole_depth, nohinge=True, endpart=True)
        if part == 4:
            m = screen_mid2(scl, midht, hole_depth)

        if m:
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
        angles = [0]

    for i in range(rpt):
        for angle in angles:
            t = union()
            c = [0.3, 0.5, 0.8, 0.5]
            for i in range(16):
                create_laptop(t, scl, 1.0, c, part=i, angle=angle)
            t = color(c).add(t)

            if False: # add inner parts for reference
                p = lcd_panel(scl)
                p = translate(v=[155.5*scl,61*scl,0]).add(p)
                p = hinge_rotate(scl, p, angle)
                t.add(p)
                p = ethernet(scl)
                p  = translate(v=[0, 210*scl,0]).add(p)
                t.add(p)

            if False:
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
