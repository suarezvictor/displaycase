# Copyright (C) 2014, 2015 Luke Kenneth Casson Leighton <lkcl@lkcl.net>
# License: GPLv3+

import time
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
    lcd_l = 1400
    lcd_w = 600
    lcd_la = lcd_l-50.0
    lcd_wa = lcd_w-80.0
    lcd_d = 50

bwid = 17 # 24
lcd_inset_top = 30 
lcd_inset_bot = 160
lcd_gap = 3
lcd_hinge_inner_rad=70
lcd_hinge_inside_rad=70
lcd_ext_rot_angle=250
lcd_outer_rad = lcd_hinge_inner_rad+bwid
lcd_end_ht = 20 # 40

screwrad = 30 / 2.0
boxheight = 150
boxtopoffs = 20
boxinset = 75
hinge_depth = 130
hole_depth = 80
boxlength = lcd_w + lcd_inset_top + lcd_inset_bot + lcd_d-20

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
    t = translate(v=[0,0,-ht/2*scl+7.5*scl])
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
    bht = boxheight+lcd_hinge_inner_rad-199.0+boxtopoffs
    print bht
    if end == 0:
        return translate([29.0*scl, 0*scl, bht*scl])
    elif end == 1:
        return translate([(-20+lcd_w+11)*scl, 0*scl, bht*scl])
    elif end == 2:
        return translate([(-20+lcd_w+lcd_inset_bot-20)*scl, 0*scl, bht*scl])
    elif end == 3:
        return translate([(-20+lcd_w/2+30)*scl, 0*scl, bht*scl])

def lid_bolthole(scl, end=True):
    if end:
        return translate([30*scl, 0*scl, (10)*scl])
    else:
        return translate([(65+lcd_w+lcd_inset_top)*scl, 0*scl, (35)*scl])

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

def screen_mid2(scl, ht, hole_ht, nohinge=True, endpart=True):

    shear = 0
    innershear = 0
    w = lcd_w+lcd_inset_top+lcd_inset_bot
    edge_inset = bwid
    iro = 0

    rad = 15

    a = union()

    toplen = 180 if test else 250
    toplenoffs = (w-40)
    # top edge
    r = union()
    c = shearedcube(size=[(bwid+iro)*scl,toplen*scl,ht*scl],
                shear=[-shear*scl, 0, 0],
                innershear=[-innershear*scl, 0, 0])
    c = rotate([0, 90, 90]).add(c)
    r.add(c)
    t = translate(v=[toplenoffs*scl, (16.5-ht)*scl, (30-lcd_d)*scl])
    t.add(r)
    a.add(t)

    # bottom edge
    r = union()
    c = shearedcube(size=[(bwid+iro)*scl,(toplen)*scl,ht*scl],
                shear=[-shear*scl, 0, 0],
                innershear=[-innershear*scl, 0, 0])
    c = rotate([0, 90, 90]).add(c)
    r.add(c)
    t = translate(v=[toplenoffs*scl, (16.5-ht)*scl, (30+bwid+lcd_gap)*scl])
    t.add(r)
    a.add(t)

    # add hinge-end filler over top of screwhole
    r = union()
    c = shearedcube(size=[(lcd_d+lcd_gap*2)*scl,(lcd_gap*2+bwid)*scl,ht*scl],
                shear=[-shear*scl, 0, 0],
                innershear=[-innershear*scl, 0, 0])
    c = rotate([0, 90, 90]).add(c)
    r.add(c)
    t = translate(v=[(+lcd_inset_bot+lcd_w-75)*scl, (16.5-ht)*scl, (30+lcd_gap)*scl])
    t.add(r)
    a.add(t)

    # add hinge-end filler over top of screwhole
    r = union()
    c = shearedcube(size=[(lcd_d+lcd_gap*2)*scl,(bwid)*scl,ht*scl],
                shear=[-shear*scl, 0, 0],
                innershear=[-innershear*scl, 0, 0])
    c = rotate([0, 90, 90]).add(c)
    r.add(c)
    t = translate(v=[(+lcd_inset_bot+lcd_w-10)*scl, (16.5-ht)*scl, (30+lcd_gap)*scl])
    t.add(r)
    a.add(t)

    # bottom edge bolt holder
    r = union()
    c = cylinder(r=29*scl, h=ht*scl, segments=50)
    c = rotate([0, 90, 90]).add(c)
    r.add(c)
    t = translate(v=[(0)*scl, (16.5-ht)*scl, (0)*scl]).add(r)
    t = lid_bolthole(scl, end=False).add(t)
    a.add(t)
    r = union()
    c = shearedcube(size=[(bwid+10+iro)*scl,(100+lcd_gap)*scl,ht*scl],
                shear=[-shear*scl, 0, 0],
                innershear=[-innershear*scl, 0, 0])
    c = rotate([0, 90, 90]).add(c)
    r.add(c)
    t = translate(v=[(55)*scl, (16.5-ht)*scl, (29)*scl]).add(r)
    t = lid_bolthole(scl, end=False).add(t)
    a.add(t)

    # screw holes through lid
    a -= lid_screwholes(scl, edge_inset)

    a = translate(v=[0, (ht-edge_inset)*scl, 0]).add(a)
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
        toplenoffs = (lcd_inset_bot+toplen-131)
    else:
        toplen = w+lcd_gap*2
        toplenoffs = (-lcd_inset_top+w+65)
    # top edge
    r = union()
    c = shearedcube(size=[(bwid+iro)*scl,toplen*scl,ht*scl],
                shear=[-shear*scl, 0, 0],
                innershear=[-innershear*scl, 0, 0])
    c = rotate([0, 90, 90]).add(c)
    r.add(c)
    t = translate(v=[toplenoffs*scl, (16.5-ht)*scl, (30-lcd_d)*scl])
    t.add(r)
    a.add(t)

    # bottom edge
    r = union()
    c = shearedcube(size=[(bwid+iro)*scl,(toplen)*scl,ht*scl],
                shear=[-shear*scl, 0, 0],
                innershear=[-innershear*scl, 0, 0])
    c = rotate([0, 90, 90]).add(c)
    r.add(c)
    t = translate(v=[toplenoffs*scl, (16.5-ht)*scl, (30+bwid+lcd_gap)*scl])
    t.add(r)
    a.add(t)

    if not endpart:
        # bottom edge bolt holder
        r = union()
        c = cylinder(r=29*scl, h=ht*scl, segments=50)
        c = rotate([0, 90, 90]).add(c)
        r.add(c)
        t = translate(v=[(0)*scl, (16.5-ht)*scl, (0)*scl]).add(r)
        t = lid_bolthole(scl, end=False).add(t)
        a.add(t)
        r = union()
        c = shearedcube(size=[(bwid+10+iro)*scl,(100+lcd_gap*2)*scl,ht*scl],
                    shear=[-shear*scl, 0, 0],
                    innershear=[-innershear*scl, 0, 0])
        c = rotate([0, 90, 90]).add(c)
        r.add(c)
        t = translate(v=[(58)*scl, (16.5-ht)*scl, (29)*scl]).add(r)
        t = lid_bolthole(scl, end=False).add(t)
        a.add(t)

    # end piece NOTE: height (lcd_d-rad) is not perfect but it's close
    r = union()
    c = shearedcube(size=[(lcd_d-rad)*scl,(bwid+5+rad)*scl,ht*scl],
                shear=[-shear*scl, 0, 0],
                innershear=[-innershear*scl, 0, 0])
    c = rotate([0, 90, 90]).add(c)
    r.add(c)
    t = translate(v=[(-lcd_inset_top+65)*scl, (16.5-ht)*scl, (25)*scl])
    t.add(r)
    a.add(t)

    # top end curve
    inner_rad=rad
    r = union()
    r = touch_arc(inner_rad, ht, bwid, inner_rad, scl)
    r = rotate([180, -90, 90]).add(r)
    t = translate(v=[+(-lcd_inset_top+63-lcd_gap)*scl, 9*scl, (30-lcd_d+rad)*scl])
    t.add(r)
    a.add(t)

    # bottom end curve
    inner_rad=rad
    r = union()
    r = touch_arc(inner_rad, ht, bwid, inner_rad, scl)
    r = rotate([180, 90, 90]).add(r)
    t = translate(v=[+(-lcd_inset_top+63-lcd_gap)*scl, (-ht+24)*scl, (33-rad)*scl])
    t.add(r)
    a.add(t)

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
        c = shearedcube(size=[(lcd_d+lcd_gap*2)*scl,(w-lcd_inset_bot+lcd_gap*2)*scl,ht*scl],
                    shear=[-shear*scl, 0, 0],
                    innershear=[-innershear*scl, 0, 0])
        c = rotate([0, 90, 90]).add(c)
        r.add(c)
        t = translate(v=[(-lcd_inset_top-lcd_inset_bot+w+65)*scl, (16.5-ht)*scl, (30+lcd_gap)*scl])
        t.add(r)
        a.add(t)

        # add hinge-end filler over top of screwhole
        r = union()
        c = shearedcube(size=[(lcd_d+lcd_gap*2)*scl,(lcd_gap*2+bwid)*scl,ht*scl],
                    shear=[-shear*scl, 0, 0],
                    innershear=[-innershear*scl, 0, 0])
        c = rotate([0, 90, 90]).add(c)
        r.add(c)
        t = translate(v=[(+lcd_inset_bot+lcd_w-75)*scl, (16.5-ht)*scl, (30+lcd_gap)*scl])
        t.add(r)
        a.add(t)

        # bottom end curve (1st)
        r = union()
        r = touch_arc(lcd_hinge_inner_rad, ht, bwid, 30, scl)
        r = rotate([180, 90, 90]).add(r)
        r = rotate([0, -30, 0]).add(r)
        r = rotate([0, lcd_ext_rot_angle, 0]).add(r)
        t = translate(v=[+(-lcd_inset_top+w+63-lcd_gap)*scl, (-ht+24)*scl, (30-lcd_d+lcd_hinge_inner_rad)*scl]).add(r)
        a.add(t)

        # bottom end curve, overlap with 1st
        r = union()
        r = touch_arc(lcd_hinge_inner_rad, ht, bwid, 30, scl)
        r = rotate([180, 90, 90]).add(r)
        r = rotate([0, 10, 0]).add(r)
        r = rotate([0, lcd_ext_rot_angle+5, 0]).add(r)
        t = translate(v=[+(-lcd_inset_top+w+63-lcd_gap)*scl, (-ht+24)*scl, (30-lcd_d+lcd_hinge_inner_rad)*scl]).add(r)
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
        r = touch_arc(lcd_hinge_inner_rad+1, hinge_depth+ht, bwid, lcd_hinge_inner_rad, scl,
                      angle=54)
        r = rotate([180, 90, 90]).add(r)
        r = rotate([0, lcd_ext_rot_angle+8, 0]).add(r)
        t = hinge_translate(scl).add(r)
        t = translate(v=[0, -(hole_ht+ht/2)*scl, 0]).add(t)
        a -= t

    # hinge hole
    r = union()
    r = cylinder(r=lcd_hinge_inside_rad*scl, h=(ht+0.3)*scl, segments=50, center=True)
    r = rotate([180, 90, 90]).add(r)
    t = translate(v=[+(-lcd_inset_top+w+63-lcd_gap)*scl, (-ht/2+16.5)*scl, (30-lcd_d+lcd_hinge_inner_rad)*scl]).add(r)
    a -= t

    # screw holes through lid
    a -= lid_screwholes(scl, edge_inset)

    a = translate(v=[0, (ht-edge_inset)*scl, 0]).add(a)
    return a

def box_screwholes(scl, edge_inset):
    u = union()

    for i in range(3 if test else 4):
        t = case_bolthole(scl, i)
        r = cylinder(r=screwrad*scl, h=(lcd_l*2+100)*scl, segments=50, center=True)
        r = rotate([90, 0, 0]).add(r)
        r = translate(v=[0, (lcd_l/2+50-edge_inset)*scl, 0]).add(r)
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

    # top edge
    r = union()
    c = shearedcube(size=[(bwid+iro)*scl,(w+lcd_gap*2)*scl,ht*scl],
                shear=[-shear*scl, 0, 0],
                innershear=[-innershear*scl, 0, 0])
    c = rotate([0, 90, 90]).add(c)
    r.add(c)
    t = translate(v=[(-lcd_inset_top+w+65)*scl, (16.5-ht)*scl, (30-lcd_d)*scl])
    t.add(r)
    a.add(t)

    # bottom edge
    r = union()
    c = shearedcube(size=[(bwid+iro)*scl,(w+lcd_gap*2)*scl,ht*scl],
                shear=[-shear*scl, 0, 0],
                innershear=[-innershear*scl, 0, 0])
    c = rotate([0, 90, 90]).add(c)
    r.add(c)
    t = translate(v=[(-lcd_inset_top+w+65)*scl, (16.5-ht)*scl, (30+bwid+lcd_gap)*scl])
    t.add(r)
    a.add(t)

    # end piece NOTE: height (lcd_d-rad) is not perfect but it's close
    r = union()
    c = shearedcube(size=[(lcd_d-rad)*scl,(bwid+5+rad)*scl,ht*scl],
                shear=[-shear*scl, 0, 0],
                innershear=[-innershear*scl, 0, 0])
    c = rotate([0, 90, 90]).add(c)
    r.add(c)
    t = translate(v=[(-lcd_inset_top+65)*scl, (16.5-ht)*scl, (25)*scl])
    t.add(r)
    a.add(t)

    # middle filler
    r = union()
    c = shearedcube(size=[(lcd_d+lcd_gap*2)*scl,(w+lcd_gap*2)*scl,ht*scl],
                shear=[-shear*scl, 0, 0],
                innershear=[-innershear*scl, 0, 0])
    c = rotate([0, 90, 90]).add(c)
    r.add(c)
    t = translate(v=[(-lcd_inset_top+w+65)*scl, (16.5-ht)*scl, (30+lcd_gap)*scl])
    t.add(r)
    a.add(t)

    # top end curve
    inner_rad=rad
    r = union()
    r = touch_arc(inner_rad, ht, bwid, inner_rad, scl)
    r = rotate([180, -90, 90]).add(r)
    t = translate(v=[+(-lcd_inset_top+63-lcd_gap)*scl, 9*scl, (30-lcd_d+rad)*scl])
    t.add(r)
    a.add(t)

    # bottom end curve
    inner_rad=rad
    r = union()
    r = touch_arc(inner_rad, ht, bwid, inner_rad, scl)
    r = rotate([180, 90, 90]).add(r)
    t = translate(v=[+(-lcd_inset_top+63-lcd_gap)*scl, (-ht+24)*scl, (33-rad)*scl])
    t.add(r)
    a.add(t)

    # hinge
    r = union()
    r = cylinder(r=(lcd_outer_rad)*scl, h=(ht+0.1)*scl, segments=50, center=True)
    r = rotate([180, 90, 90]).add(r)
    t = hinge_translate(scl).add(r)
    t = translate(v=[0, (-ht/2+16.5)*scl, 0]).add(t)
    a.add(t)

    # screw hole support
    r = union()
    c = shearedcube(size=[(bwid+10+iro)*scl,(100+lcd_gap*2)*scl,ht*scl],
                shear=[-shear*scl, 0, 0],
                innershear=[-innershear*scl, 0, 0])
    c = rotate([0, 90, 90]).add(c)
    r.add(c)
    t = translate(v=[(58)*scl, (16.5-ht)*scl, (29)*scl]).add(r)
    t = lid_bolthole(scl, end=False).add(t)
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
    t = translate(v=[+(-lcd_inset_top+w+63-lcd_gap)*scl, (-ht/2+16.5)*scl, (30-lcd_d+lcd_hinge_inner_rad)*scl]).add(r)
    a -= t

    a = translate(v=[0, (ht-edge_inset)*scl, 0]).add(a)
    p = lcd_panel(scl, offs=3)
    p = translate(v=[155.5*scl,61*scl,0]).add(p)
    a -= p

    # screw holes through lid
    a -= lid_screwholes(scl, edge_inset)

    return a

def base_end(scl, ht_offset, ht, hinge_depth, hole_depth):
    edge_inset = bwid
    a = union()

    border=3.0 # move cylinders inwards so that lid cylinders fit around them
    slot_depth = 100

    # inner tube
    r = union()
    r = cylinder(r=(lcd_hinge_inside_rad-border)*scl, h=(hinge_depth-20)*scl, segments=50, center=True)
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
    r = cylinder(r=(lcd_outer_rad+20)*scl, h=(hole_depth+ht*2+bwid+0.1)*scl, segments=50, center=True)
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
    r = cylinder(r=(lcd_outer_rad)*scl, h=(20+0.1)*scl, segments=50, center=True)
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
    r = touch_arc(lcd_hinge_inner_rad, cable_slot_depth, bwid, lcd_hinge_inner_rad, scl,
                  angle=30)
    r = rotate([180, 90, 90]).add(r)
    r = rotate([0, lcd_ext_rot_angle+110, 0]).add(r)
    t = hinge_translate(scl).add(r)
    t = translate(v=[0, (hinge_depth-ht-cable_slot_depth/2+6.5)*scl, 0]).add(t)
    a -=t

    # hollow out base box at edge
    r = union()
    r = cylinder(r=(lcd_outer_rad+border)*scl, h=(hole_depth+ht*1+10.0)*scl, segments=50, center=True)
    r = rotate([180, 90, 90]).add(r)
    t = hinge_translate(scl).add(r)
    t = translate(v=[0, (hole_depth-ht*2-hole_depth/2+16.5)*scl, 0]).add(t)
    box -= t

    a += box

    # hollow out tube including base box
    r = union()
    r = cylinder(r=(lcd_hinge_inside_rad-bwid-border)*scl, h=(hinge_depth+0.4)*scl, segments=50, center=True)
    r = rotate([180, 90, 90]).add(r)
    t = hinge_translate(scl).add(r)
    t = translate(v=[0, (hinge_depth-hinge_depth/2+16.5)*scl, 0]).add(t)
    a -= t

    # cutout for base top "hook" with screw-hole in it
    b = cube([29.1*2*scl, 90*scl, 70*scl])
    b = translate([-29.1*scl, -10*scl, -30*scl]).add(b)
    t = case_bolthole(scl, end=0).add(b)
    t = translate(v=[(0)*scl, (-hinge_depth/2+3)*scl, (boxheight)*scl]).add(t)
    a -= t
    b = cube([29.1*scl, 400*scl, 30*scl])
    b = translate([-29.1*1*scl, -10*scl, 0*scl]).add(b)
    t = case_bolthole(scl, end=0).add(b)
    t = translate(v=[(0)*scl, (-hinge_depth/2+3)*scl, (boxheight)*scl]).add(t)
    a -= t
    if test:
        l = [(1, -46), (2, -46), (2, 36)]
    else:
        l = [(1, -46), (2, -46), (2, 36), (3, -46), (3, 36)]
    for (end, offs) in l:
        b = cube([10*scl, (boxdepth-70)*scl, (60)*scl])
        t = case_bolthole(scl, end=end).add(b)
        t = translate(v=[(offs)*scl, (-boxdepth/2+105)*scl, (boxheight-45)*scl]).add(t)
        a += t
    b = cube([25*scl, (boxdepth-70)*scl, (bwid*1.2)*scl])
    t = case_bolthole(scl, end=0).add(b)
    t = translate(v=[(20)*scl, (-boxdepth/2+105)*scl, (boxheight)*scl]).add(t)
    a += t
    b = cube([80*scl, 90*scl, 170*scl])
    t = case_bolthole(scl, end=0).add(b)
    t = translate(v=[(-90)*scl, (-hinge_depth/2-7)*scl, (0)*scl]).add(t)
    a -= t

    # screw support at both ends
    for end in range(3 if test else 4):
        if end != 0:
            b = cube([(29.1*2+bwid*2)*scl, 70*scl, 60*scl])
            b = translate([(-29.1-bwid)*scl, 18.5*scl, -30*scl]).add(b)
            t = case_bolthole(scl, end=end).add(b)
            t = translate(v=[(0)*scl, (-hinge_depth/2+3)*scl, (boxheight-bwid)*scl]).add(t)
            a += t
            b = cube([29.1*2*scl, 70*scl, 70*scl])
            b = translate([-29.1*scl, 10*scl, -30*scl]).add(b)
            t = case_bolthole(scl, end=end).add(b)
            t = translate(v=[(0)*scl, (-hinge_depth/2+3)*scl, (boxheight)*scl]).add(t)
            a -= t
        r = union()
        c = cylinder(r=29*scl, h=(boxdepth+18.5)*scl, segments=50)
        c = rotate([0, 90, 90]).add(c)
        r.add(c)
        b = cube([80*scl, 90*scl, 170*scl])
        r -= translate([-35*scl, -10*scl, -30*scl]).add(b)
        t = case_bolthole(scl, end=end).add(r)
        t = translate(v=[(0)*scl, (-hinge_depth/2+3)*scl, (boxheight)*scl]).add(t)
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
    
def base_box(scl, boxdepth, hole_depth, ht, hollow=True):
    # base hinge box
    c = union()
    b = cube([(boxlength)*scl, (boxdepth)*scl, boxheight*scl])
    b = translate([0, 20*scl, 0*scl]).add(b)
    c.add(b)
    if hollow:
        h = cube([(boxlength-lcd_outer_rad-80-bwid*2)*scl, (boxdepth+0.3)*scl,
                   ((boxheight-bwid)+0.3)*scl])
        h = translate(v=[bwid*scl, (bwid*0-0.3)*scl, -0.3*scl]).add(h)
        c -= h
        h = cube([(boxlength-lcd_outer_rad-80-bwid+0.3)*scl, (boxdepth+0.3)*scl,
                   (boxinset+0.3)*scl])
        h = translate(v=[-0.3*scl, (bwid*2-0.3)*scl, -0.3*scl]).add(h)
        c -= h
        h = cube([(boxlength-bwid*2)*scl, (boxdepth-bwid*2)*scl,
                   (boxheight-bwid+0.2)*scl])
        h = translate(v=[bwid*scl, (bwid*2)*scl, -0.1*scl]).add(h)
        c -= h
        h = cube([(bwid+0.5)*scl, (boxdepth)*scl,
                   (boxheight)*scl])
        h = translate(v=[(boxlength-lcd_outer_rad-80-bwid)*scl, 20*scl, -0.0*scl]).add(h)
        c += h
        # cutout in side of box for cable
        h = cube([(140)*scl, (60)*scl,
                   (55+0.2)*scl])
        h = translate(v=[(boxlength-bwid-120)*scl,
                            (boxdepth-32+0.1)*scl, (20)*scl]).add(h)
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
            h = cube([25*scl, 10*scl, (500)*scl])
            h = translate([(boxlength-30)*scl, (boxdepth+10)*scl, -200*scl]).add(h)
            c += h
            h = cube([25*scl, 10*scl, (300)*scl])
            h = translate([(boxlength-180)*scl, (boxdepth+10)*scl, -200*scl]).add(h)
            c += h
            h = cube([45*scl, 10*scl, (500)*scl])
            h = translate([(boxlength+110)*scl, (boxdepth+10)*scl, -200*scl]).add(h)
            c += h
            h = cube([(boxlength+20+150)*scl, 10*scl, (55)*scl])
            h = translate([(-40)*scl, (boxdepth+10)*scl, -200*scl]).add(h)
            c += h
            h = cube([(boxlength+20+150)*scl, 10*scl, (55)*scl])
            h = translate([(-40)*scl, (boxdepth+10)*scl, 245*scl]).add(h)
            c += h
            h = cube([(20+100)*scl, 10*scl, (25)*scl])
            h = translate([(boxlength+10)*scl, (boxdepth+10)*scl, -10*scl]).add(h)
            c += h
    

        if True:
            # add some structural support 
            sstep = 140
            sdep = sstep
            while sdep <= boxlength-sstep*(2 if test else 2):
                u = intersection()
                u.add(b)
                r = union()
                h = cube([bwid*scl, 100*scl, 100*scl])
                h = rotate([-45, 0, 0]).add(h)
                h = translate(v=[sdep*scl, 100*scl, (boxheight-2)*scl]).add(h)
                r.add(h)
                u.add(r)
                c += u
                sdep += sstep

    b = cube([(lcd_outer_rad+80)*scl, (boxdepth)*scl, 20*scl])
    b = translate(v=[(boxlength-lcd_outer_rad-80)*scl, 20*scl, 0]).add(b)
    c += b
    b = cube([(bwid)*scl, (boxdepth)*scl, 70*scl])
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

    if part == 9:
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
        angles = [0, max_open/2, max_open]
    else:
        rpt = 1
        angles = [110]

    for i in range(rpt):
        for angle in angles:
            scl = 0.1
            t = union()
            c = [0.3, 0.5, 0.8, 0.5]
            for i in range(6):
                create_laptop(t, scl, 1.0, c, part=i, angle=angle)
            t = color(c).add(t)

            if True: # add inner parts for reference
                p = lcd_panel(scl)
                p = translate(v=[155.5*scl,61*scl,0]).add(p)
                p = hinge_rotate(scl, p, angle)
                t.add(p)


            if False:
                card = import_stl(filename = "eoma68.stl")
                r = rotate([90,180,-90]).add(card)
                r = translate([2280*scl, 1000*scl, 135*scl]).add(r)
                t.add(r)

            scad_render_to_file(t, "laptop_prog.scad")
            f = open("laptop_model.scad", "w")
            f.write("""include<laptop_prog.scad>;
            """)
            f.close()
            if i != rpt:
                time.sleep(2)
