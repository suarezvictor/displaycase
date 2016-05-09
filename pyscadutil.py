# Copyright (C) 2014, 2015 Luke Kenneth Casson Leighton <lkcl@lkcl.net>
# License: GPLv3+

import time
import itertools
from pyopenscad import *
from polysurface import spline_double_divide, Offset, SurfaceFromCurves
from polysurface import spline_divide, vsub, vmult, vtrans, turnaround
from polysurface import surface_indices_from_pointsets
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
        
def triangle(size, center=False):
    v = size
    points = [
    [ 0.5,  0.5,  0.5],
    [ 0.5,  0.5, -0.5],
    [ 0.5, -0.5,  0.5],
    [ 0.5, -0.5, -0.5],
    [-0.5,  0.5,  0.5],
    [-0.5,  0.5, -0.5],
    [-0.5, -0.5,  0.5],
    [-0.5, -0.5, -0.5]]

    faces = [
    [ 4 , 5, 1, 0],
    [ 2 , 4, 0],
    [ 1 , 3, 2, 0],
    [ 5 , 4, 3, 2],
    [ 3 , 1, 5]]

    for i in range(len(points)):
        for j in range(len(v)):
            if not center:
                points[i][j] += 0.5
            points[i][j] *= v[j]

    return polyhedron(points, faces)


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
    [-0.5, -0.5, -0.5]]
    faces = [
    [ 4 , 5, 1, 0],
    [ 2 , 6, 4, 0],
    [ 1 , 3, 2, 0],
    [ 6 , 2, 3, 7],
    [ 5 , 4, 6, 7],
    [ 3 , 1, 5, 7]]

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

def curvebox(scl, l, w, ht, rad, center=False):
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

    if center:
        u = translate([-l/2.0, -w/2.0, -ht/2.0]).add(u)

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

def roundpt(pt):
    return tuple(map(lambda x: round(x, 5), pt))

class Polygon:
    def __init__(self):
        self.points = []
        self.triangles = []
        self.triangles_idx = set()
        self.points_idx = {}

    def add_points(self, pts):
        for pt in pts:
            self.add_point(pt)

    def add_point(self, pt):
        pt = roundpt(pt)
        if pt in self.points_idx:
            #print "point already in %s %s" % \
                        #(repr(pt), repr(self.points_idx))
            return 
        self.points_idx[pt] = len(self.points)
        self.points.append(list(pt))

    def add_triangle(self, points):
        tarray = []
        pts = list(points)
        pts = map(tuple, pts)
        pts.sort()
        pts = tuple(pts)
        print pts
        if pts in self.triangles_idx:
            return
        self.triangles_idx.add(pts)

        pts = []
        for pt in points:
            pt = roundpt(pt)
            if pt in pts:
                continue
            if len(pts) > 1:
                if pts[-1] == pt or pts[0] == pt:
                    continue
            pts.append(pt)
        if len(pts) < 3:
            return
        for pt in pts:
            self.add_point(pt)
            tarray.append(self.points_idx[pt])
        tarray.reverse()
        self.triangles.append(tarray)

    def add_triangles(self, tr):
        for t in tr:
            self.add_triangle(t)

    def _add_triangles(self, tr):
        self.triangles += tr

def pf(pspec, pwo, pdo, pho):
    return (pspec[0][pwo], pspec[1][pdo], pspec[2][pho])

spline_res = 1.0/6

def sl(pspec, lidx):
    """ ok this function takes 4 points, uses the 1st two and last two
        each as "direction-finders", then creates a spline which is
        approximately going to go flat to those pairs.
    """
    pts = map(lambda x: pf(pspec, x[0], x[1], x[2]), lidx)
    scale = [0.000000000005] * 3
    v1 = vmult(scale, vsub(pts[1], pts[0]))
    v2 = vmult(scale, vsub(pts[3], pts[4]))
    print "points", pts
    print "v1", v1
    print "v2", v2
    pts = [pts[1], vtrans(pts[1], v1), pts[2], vtrans(pts[3], v2), pts[3]]
    #pts = [pts[1], pts[1], pts[2], pts[3], pts[3]]
    #pts = [pts[1], pts[2], pts[3]]
    pts = spline_divide([pts], spline_res)
    print pts
    return v1, v2, pts[0]
    
    
def splinebox(scl, w, d, h, thick=0.0, curverads=None):

    if curverads is None:
        curverads = {}
    pg = Polygon()

    ws = (0, curverads.get(L, 0), w-curverads.get(R, 0), w)
    ds = (0, curverads.get(F, 0), d-curverads.get(B, 0), d)
    hs = (0, curverads.get(D, 0), h-curverads.get(T, 0), h)

    mvec = lambda x : x * scl
    ws = map(mvec, ws)
    ds = map(mvec, ds)
    hs = map(mvec, hs)

    pspec = (ws, ds, hs)

    # centre rectangles (very middles)
    d = ( pf(pspec, 1, 2, 0),
         pf(pspec, 2, 2, 0),
         pf(pspec, 2, 1, 0),
         pf(pspec, 1, 1, 0),)
    t = (pf(pspec, 1, 1, 3),
         pf(pspec, 2, 1, 3),
         pf(pspec, 2, 2, 3),
         pf(pspec, 1, 2, 3))
    f = (pf(pspec, 1, 0, 1),
         pf(pspec, 2, 0, 1),
         pf(pspec, 2, 0, 2),
         pf(pspec, 1, 0, 2))
    b = (pf(pspec, 1, 3, 2),
         pf(pspec, 2, 3, 2),
         pf(pspec, 2, 3, 1),
         pf(pspec, 1, 3, 1),)
    l = (pf(pspec, 0, 1, 1),
         pf(pspec, 0, 1, 2),
         pf(pspec, 0, 2, 2),
         pf(pspec, 0, 2, 1))
    r = (
         pf(pspec, 3, 2, 1),
         pf(pspec, 3, 2, 2),
         pf(pspec, 3, 1, 2),
         pf(pspec, 3, 1, 1),
            )

    for pts in [d,t,f,b,l,r]:
        pg.add_triangle(pts)

    # spinelines
    ft_l = (
            (1, 2, 3),
            (1, 1, 3),
            (1, 0, 3),
            (1, 0, 2),
            (1, 0, 1))
    ft_l_v1, ft_l_v2, ft_l = sl(pspec, ft_l)
    ft_offs = len(pg.points)
    ft_r = (
            (2, 2, 3),
            (2, 1, 3),
            (2, 0, 3),
            (2, 0, 2),
            (2, 0, 1),)
    ft_r_v1, ft_r_v2, ft_r = sl(pspec, ft_r)

    if curverads.get(F,0) !=0 or curverads.get(T,0) !=0:
        add_edge(pg, ft_l, ft_r)

    fd_l = ((1, 0, 2),
            (1, 0, 1),
            (1, 0, 0),
            (1, 1, 0),
            (1, 2, 0))
    fd_l_v1, fd_l_v2, fd_l = sl(pspec, fd_l)
    fd_offs = len(pg.points)
    fd_r = ((2, 0, 2),
            (2, 0, 1),
            (2, 0, 0),
            (2, 1, 0),
            (2, 2, 0))
    fd_r_v1, fd_r_v2, fd_r = sl(pspec, fd_r)

    add_edge(pg, fd_l, fd_r)

    bd_l = (
            (1, 1, 0),
            (1, 2, 0),
            (1, 3, 0),
            (1, 3, 1),
            (1, 3, 2),
            )
    bd_l_v1, bd_l_v2, bd_l = sl(pspec, bd_l)
    bd_offs = len(pg.points)
    bd_r = (
            (2, 1, 0),
            (2, 2, 0),
            (2, 3, 0),
            (2, 3, 1),
            (2, 3, 2),
            )
    bd_r_v1, bd_r_v2, bd_r = sl(pspec, bd_r)

    add_edge(pg, bd_l, bd_r)

    bt_l = ((1, 3, 1),
            (1, 3, 2),
            (1, 3, 3),
            (1, 2, 3),
            (1, 1, 3))
    bt_l_v1, bt_l_v2, bt_l = sl(pspec, bt_l)
    bt_offs = len(pg.points)
    bt_r = ((2, 3, 1),
            (2, 3, 2),
            (2, 3, 3),
            (2, 2, 3),
            (2, 1, 3))
    bt_r_v1, bt_r_v2, bt_r = sl(pspec, bt_r)

    add_edge(pg, bt_l, bt_r)

    lt_f = ((0, 1, 1),
            (0, 1, 2),
            (0, 1, 3),
            (1, 1, 3),
            (2, 1, 3))
    lt_f_v1, lt_f_v2, lt_f = sl(pspec, lt_f)
    lt_b = ((0, 2, 1),
            (0, 2, 2),
            (0, 2, 3),
            (1, 2, 3),
            (2, 2, 3))
    lt_b_v1, lt_b_v2, lt_b = sl(pspec, lt_b)

    add_edge(pg, lt_f, lt_b)

    rt_f = (
            (1, 1, 3),
            (2, 1, 3),
            (3, 1, 3),
            (3, 1, 2),
            (3, 1, 1),
    )
    rt_f_v1, rt_f_v2, rt_f = sl(pspec, rt_f)
    rt_b = (
            (1, 2, 3),
            (2, 2, 3),
            (3, 2, 3),
            (3, 2, 2),
            (3, 2, 1),
            )
    rt_b_v1, rt_b_v2, rt_b = sl(pspec, rt_b)

    add_edge(pg, rt_f, rt_b)

    ld_f = (
            (2, 1, 0),
            (1, 1, 0),
            (0, 1, 0),
            (0, 1, 1),
            (0, 1, 2),
)
    ld_f_v1, ld_f_v2, ld_f = sl(pspec, ld_f)
    ld_b = ( (2, 2, 0),
            (1, 2, 0),
            (0, 2, 0),
            (0, 2, 1),
            (0, 2, 2),)
    ld_b_v1, ld_b_v2, ld_b = sl(pspec, ld_b)

    add_edge(pg, ld_f, ld_b)

    rd_f = ((3, 1, 2),
            (3, 1, 1),
            (3, 1, 0),
            (2, 1, 0),
            (1, 1, 0))
    rd_f_v1, rd_f_v2, rd_f = sl(pspec, rd_f)
    rd_b = ((3, 2, 2),
            (3, 2, 1),
            (3, 2, 0),
            (2, 2, 0),
            (1, 2, 0))
    rd_b_v1, rd_b_v2, rd_b = sl(pspec, rd_b)

    add_edge(pg, rd_f, rd_b)

    rf_t = ((3, 2, 2),
            (3, 1, 2),
            (3, 0, 2),
            (2, 0, 2),
            (1, 0, 2))
    rf_t_v1, rf_t_v2, rf_t = sl(pspec, rf_t)
    rf_d = ((3, 2, 1),
            (3, 1, 1),
            (3, 0, 1),
            (2, 0, 1),
            (1, 0, 1))
    rf_d_v1, rf_d_v2, rf_d = sl(pspec, rf_d)

    add_edge(pg, rf_t, rf_d)

    lf_t = (
            (2, 0, 2),
            (1, 0, 2),
            (0, 0, 2),
            (0, 1, 2),
            (0, 2, 2),)
    lf_t_v1, lf_t_v2, lf_t = sl(pspec, lf_t)
    lf_d = (
            (2, 0, 1),
            (1, 0, 1),
            (0, 0, 1),
            (0, 1, 1),
            (0, 2, 1),)
    lf_d_v1, lf_d_v2, lf_d = sl(pspec, lf_d)

    add_edge(pg, lf_t, lf_d)

    lb_t = ((0, 1, 2),
            (0, 2, 2),
            (0, 3, 2),
            (1, 3, 2),
            (2, 3, 2))
    lb_t_v1, lb_t_v2, lb_t = sl(pspec, lb_t)
    lb_d = ((0, 1, 1),
            (0, 2, 1),
            (0, 3, 1),
            (1, 3, 1),
            (2, 3, 1))
    lb_d_v1, lb_d_v2, lb_d = sl(pspec, lb_d)

    add_edge(pg, lb_t, lb_d)

    rb_t = (
            (1, 3, 2),
            (2, 3, 2),
            (3, 3, 2),
            (3, 2, 2),
            (3, 1, 2),
            )
    rb_t_v1, rb_t_v2, rb_t = sl(pspec, rb_t)
    rb_d = (
            (1, 3, 1),
            (2, 3, 1),
            (3, 3, 1),
            (3, 2, 1),
            (3, 1, 1),
            )
    rb_d_v1, rb_d_v2, rb_d = sl(pspec, rb_d)

    add_edge(pg, rb_t, rb_d)


    # at corners
    #ft_r.reverse()
    add_corner(pg, pspec, rf_t, ft_r, ft_r_v2, rf_t_v2)
    ft_l.reverse()
    add_corner(pg, pspec, lf_t, ft_l, ft_l_v2, lf_t_v1)
    rf_d.reverse()
    add_corner(pg, pspec, rf_d, fd_r, fd_r_v1, rf_d_v2)
    lf_d.reverse()
    fd_l.reverse()
    add_corner(pg, pspec, lf_d, fd_l, fd_l_v1, lf_d_v1)
    #rb_t.reverse()
    add_corner(pg, pspec, rb_t, bt_r, bt_r_v1, rb_t_v1)
    bt_l.reverse()
    add_corner(pg, pspec, lb_t, bt_l, bt_l_v1, lb_t_v2)
    lb_d.reverse()
    bd_l.reverse()
    add_corner(pg, pspec, lb_d, bd_l, bd_l_v2, lb_d_v2)
    rb_d.reverse()
    add_corner(pg, pspec, rb_d, bd_r, bd_r_v2, rb_d_v1)

    return polyhedron(points=pg.points, faces=pg.triangles)

def add_edge(pg, ft_l, ft_r):
    for i in range(len(ft_l)-1):
        pts = (ft_l[i], ft_l[i+1], ft_r[i+1], ft_r[i])
        pg.add_triangle(pts)

def add_corner(pg, pspec, rf_t, ft_r, rf_t_v1, ft_r_v2):
    frt = []
    for (pts1, pts2) in zip(rf_t, ft_r):
        midpoint = (pts1[0], pts1[1], pts2[2])
        pts = [pts1, vtrans(pts1, rf_t_v1),
                midpoint,
                vtrans(pts2, ft_r_v2),
                pts2]
        print "corner pts", pts
        pts = spline_divide([pts], spline_res)
        pts = pts[0]
        frt.append(pts)

    print "frt", len(frt), len(frt[0])
    for j in range(len(frt)-1):
        for i in range(len(frt[0])-1):
            pts = (frt[j][i], frt[j][i+1],
                   frt[j+1][i+1], frt[j+1][i])
            pg.add_triangle(pts)

def hollowsplinebox(scl, w, d, h, thick=0.0, curverads=None):

    if isinstance(thick, float):
        thick = {L:thick, R:thick, T:thick, D:thick,
                 F:thick, B:thick}

    c = union()
    c += splinebox(scl, w, d, h, curverads=curverads)
    w2 = w-thick[L]-thick[R]
    d2 = d-thick[F]-thick[B]
    h2 = h-thick[T]-thick[D]
    for k in curverads.keys():
        if thick.has_key(k) and thick[k] > 0:
            curverads[k] -= thick[k]
            curverads[k] = max( curverads[k], 0.1)
    b = splinebox(scl, w2, d2, h2, curverads=curverads)
    c -= translate([thick[L]*scl, thick[F]*scl, thick[D]*scl]).add(b)

    return c

if __name__ == '__main__':

    p = splinebox(0.1, 300, 200, 100,
                    curverads={L:10, T:20, D:10, R:45, B: 15, F: 25})
    t = union()
    t += p

    p = hollowsplinebox(0.1, 300, 200, 100,
                    curverads={L:15, T:30, D:15, R:45, B: 20, F: 25},
                    thick={L:-50, R:10, T:10, D:10, F: 10, B:-40})
    p = translate([0,0,30]).add(p)
    t += p

    scad_render_to_file(t, "test.scad")


