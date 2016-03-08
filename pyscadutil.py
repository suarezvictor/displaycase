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

class Polygon:
    def __init__(self):
        self.points = []
        self.triangles = []
        self.points_idx = {}

    def add_points(self, pts):
        for pt in pts:
            self.add_point(pt)

    def add_point(self, pt):
        if pt in self.points_idx:
            #print "point already in %s %s" % \
                        #(repr(pt), repr(self.points_idx))
            return 
        self.points_idx[pt] = len(self.points)
        self.points.append(list(pt))

    def add_triangle(self, points):
        tarray = []
        for pt in points:
            tarray.append(self.points_idx[pt])
        self.triangles.append(tarray)

    def add_triangles(self, tr):
        for t in tr:
            self.add_triangle(t)

    def _add_triangles(self, tr):
        self.triangles += tr

W = 1
D = 2
H = 4

def pf(pspec, pwo, pdo, pho):
    return (pspec[0][pwo], pspec[1][pdo], pspec[2][pho])

def sl(pspec, lidx):
    """ ok this function takes 4 points, uses the 1st two and last two
        each as "direction-finders", then creates a spline which is
        approximately going to go flat to those pairs.
    """
    pts = map(lambda x: pf(pspec, x[0], x[1], x[2]), lidx)
    scale = (0.0001,0.0001,0.0001)
    v1 = vmult(scale, vsub(pts[1], pts[0]))
    v2 = vmult(scale, vsub(pts[4], pts[3]))
    print "points", pts
    print "v1", v1
    print "v2", v2
    f = [pts[1]]
    b = [pts[3]]
    for i in range(2):
        print f, b, v1
        x = vtrans(v1, f[-1])
        print x
        f.append(x)
        x = vtrans(v2, b[-1])
        print x
        b.append(x)
    b.reverse()
    pts = f + [pts[2]] + b
    pts = spline_divide([pts], 0.1)
    print pts
    return v1, v2, pts[0]
    
    
def splinebox(scl, w, d, h, thick=0.0, curverads=None, scalecurve=None):

    if curverads is None:
        curverads = {}
    pg = Polygon()

    ws = (0, curverads.get(L, 0), w-curverads.get(R, 0), w)
    ds = (0, curverads.get(F, 0), d-curverads.get(B, 0), d)
    hs = (0, curverads.get(D, 0), h-curverads.get(T, 0), h)

    pspec = (ws, ds, hs)

    for i in range(8):
        for pwo in range(4):
            for pdo in range(4):
                for pho in range(4):
                    pg.add_point(pf(pspec, pwo, pdo, pho))

    # centre rectangles (very middles)
    d = (pf(pspec, 1, 1, 0),
         pf(pspec, 2, 1, 0),
         pf(pspec, 2, 2, 0),
         pf(pspec, 1, 2, 0))
    t = (pf(pspec, 1, 1, 3),
         pf(pspec, 2, 1, 3),
         pf(pspec, 2, 2, 3),
         pf(pspec, 1, 2, 3))
    f = (pf(pspec, 1, 0, 1),
         pf(pspec, 2, 0, 1),
         pf(pspec, 2, 0, 2),
         pf(pspec, 1, 0, 2))
    b = (pf(pspec, 1, 3, 1),
         pf(pspec, 2, 3, 1),
         pf(pspec, 2, 3, 2),
         pf(pspec, 1, 3, 2))
    l = (pf(pspec, 0, 1, 1),
         pf(pspec, 0, 1, 2),
         pf(pspec, 0, 2, 2),
         pf(pspec, 0, 2, 1))
    r = (pf(pspec, 3, 1, 1),
         pf(pspec, 3, 1, 2),
         pf(pspec, 3, 2, 2),
         pf(pspec, 3, 2, 1))

    #for pts in [d,t,f,b,l,r]:
    #    pg.add_triangle(pts)

    # ok these will be 2-axis curves
    ft = (pf(pspec, 1, 0, 2),
          pf(pspec, 2, 0, 2),
          pf(pspec, 2, 1, 3),
          pf(pspec, 1, 1, 3))
    #pg.add_triangle(ft)
    fd = (pf(pspec, 1, 0, 1),
          pf(pspec, 2, 0, 1),
          pf(pspec, 2, 1, 0),
          pf(pspec, 1, 1, 0))
    pg.add_triangle(fd)
    bd = (pf(pspec, 1, 3, 1),
          pf(pspec, 2, 3, 1),
          pf(pspec, 2, 2, 0),
          pf(pspec, 1, 2, 0))
    pg.add_triangle(bd)
    bt = (pf(pspec, 1, 3, 2),
          pf(pspec, 2, 3, 2),
          pf(pspec, 2, 2, 3),
          pf(pspec, 1, 2, 3))
    pg.add_triangle(bt)

    lt = (pf(pspec, 0, 1, 2),
          pf(pspec, 0, 2, 2),
          pf(pspec, 1, 2, 3),
          pf(pspec, 1, 1, 3))
    pg.add_triangle(lt)
    ld = (pf(pspec, 0, 1, 1),
          pf(pspec, 0, 2, 1),
          pf(pspec, 1, 2, 0),
          pf(pspec, 1, 1, 0))
    pg.add_triangle(ld)
    rt = (pf(pspec, 3, 1, 2),
          pf(pspec, 3, 2, 2),
          pf(pspec, 2, 2, 3),
          pf(pspec, 2, 1, 3))
    pg.add_triangle(rt)
    rd = (pf(pspec, 3, 1, 1),
          pf(pspec, 3, 2, 1),
          pf(pspec, 2, 2, 0),
          pf(pspec, 2, 1, 0))
    pg.add_triangle(rd)

    rf = (pf(pspec, 3, 1, 2),
          pf(pspec, 3, 1, 1),
          pf(pspec, 2, 0, 1),
          pf(pspec, 2, 0, 2))
    pg.add_triangle(rf)
    rb = (pf(pspec, 3, 2, 2),
          pf(pspec, 3, 2, 1),
          pf(pspec, 2, 3, 1),
          pf(pspec, 2, 3, 2))
    pg.add_triangle(rb)
    lf = (pf(pspec, 0, 1, 2),
          pf(pspec, 0, 1, 1),
          pf(pspec, 1, 0, 1),
          pf(pspec, 1, 0, 2))
    pg.add_triangle(lf)
    lb = (pf(pspec, 0, 2, 2),
          pf(pspec, 0, 2, 1),
          pf(pspec, 1, 3, 1),
          pf(pspec, 1, 3, 2))
    pg.add_triangle(lb)

    # ok corners
    ldf = (pf(pspec, 1, 0, 1),
           pf(pspec, 0, 1, 1),
           pf(pspec, 1, 1, 0))
    pg.add_triangle(ldf)
    rdf = (pf(pspec, 2, 0, 1),
           pf(pspec, 3, 1, 1),
           pf(pspec, 2, 1, 0))
    pg.add_triangle(rdf)
    rdb = (pf(pspec, 2, 3, 1),
           pf(pspec, 3, 2, 1),
           pf(pspec, 2, 2, 0))
    pg.add_triangle(rdb)
    ldb = (pf(pspec, 1, 3, 1),
           pf(pspec, 0, 2, 1),
           pf(pspec, 1, 2, 0))
    pg.add_triangle(ldb)

    ltf = (pf(pspec, 1, 0, 2),
           pf(pspec, 0, 1, 2),
           pf(pspec, 1, 1, 3))
    pg.add_triangle(ltf)
    rtf = (pf(pspec, 2, 0, 2),
           pf(pspec, 3, 1, 2),
           pf(pspec, 2, 1, 3))
    pg.add_triangle(rtf)
    rtb = (pf(pspec, 2, 3, 2),
           pf(pspec, 3, 2, 2),
           pf(pspec, 2, 2, 3))
    pg.add_triangle(rtb)
    ltb = (pf(pspec, 1, 3, 2),
           pf(pspec, 0, 2, 2),
           pf(pspec, 1, 2, 3))
    pg.add_triangle(ltb)

    # spinelines
    ft_l = ((1, 0, 1),
            (1, 0, 2),
            (1, 0, 3),
            (1, 1, 3),
            (1, 2, 3))
    ft_l_v1, ft_l_v2, ft_l = sl(pspec, ft_l)
    ft_offs = len(pg.points)
    pg.add_points(ft_l)
    ft_r = ((2, 0, 1),
            (2, 0, 2),
            (2, 0, 3),
            (2, 1, 3),
            (2, 2, 3))
    ft_r_v1, ft_r_v2, ft_r = sl(pspec, ft_r)
    pg.add_points(ft_r)

    rt_f = ((3, 1, 1),
            (3, 1, 2),
            (3, 1, 3),
            (2, 1, 3),
            (1, 1, 3))
    rt_f_v1, rt_f_v2, rt_f = sl(pspec, rt_f)
    pg.add_points(rt_f)
    rt_b = None # TODO

    rf_t = ((3, 2, 2),
            (3, 1, 2),
            (3, 0, 2),
            (2, 0, 2),
            (1, 0, 2))
    rf_t_v1, rf_t_v2, rf_t = sl(pspec, rf_t)
    pg.add_points(rf_t)

    rf_d = ((3, 2, 1),
            (3, 1, 1),
            (3, 0, 1),
            (2, 0, 1),
            (1, 0, 1))
    rf_d_v1, rf_d_v2, rf_d = sl(pspec, rf_d)
    pg.add_points(rf_d)

    # between edges
    ft_pts = []
    for i in range(len(ft_l)-1):
        pts = (ft_l[i], ft_l[i+1], ft_r[i+1], ft_r[i])
        ft_pts.append(pts)
        pg.add_triangle(pts)
    rf_pts = []
    for i in range(len(rf_t)-1):
        pts = (rf_t[i], rf_t[i+1], rf_d[i+1], rf_d[i])
        rf_pts.append(pts)
        pg.add_triangle(pts)

    ft_r.reverse()
    # at corners
    frt = []
    for (pts1, pts2) in zip(rf_t, ft_r):
        midpoint = pf(pspec, 3, 1, 3)
        pts = [vtrans(pts1, rf_t_v1), pts1,
                midpoint,
                pts2, vsub(pts2, ft_r_v2)]
        print "corner pts", pts
        pts = spline_divide([pts], 0.1)
        pts = pts[0]
        pg.add_points(pts)
        frt.append(pts)

    print "frt", len(frt), len(frt[0])
    for j in range(len(frt)-1):
        for i in range(len(frt[0])-1):
            pts = (frt[j][i], frt[j][i+1],
                   frt[j+1][i+1], frt[j+1][i])
            pg.add_triangle(pts)


    return polyhedron(points=pg.points, faces=pg.triangles)

if __name__ == '__main__':

    p = splinebox(0.01, 300, 200, 100,
                    curverads={L:10, T:20, D:30, R:40, B: 15, F: 25})
    t = union()
    t.add(p)

    scad_render_to_file(t, "test.scad")


