# Copyright (C) 2011-2017 Luke Kenneth Casson Leighton <lkcl@lkcl.net>
# License: GNU GPLv3+

from operator import add
from pyopenscad import *
from copy import copy, deepcopy
from spline import Spline

def vmult(v1, v2):
    return map(lambda (x,y): x*y, zip(v1, v2))

def vtrans(v1, v2):
    return map(lambda (x,y): x+y, zip(v1, v2))

def vsub(v1, v2):
    return map(lambda (x,y): x-y, zip(v1, v2))

def normalise(v1):
    d = pow(reduce(lambda x,y:x+y, map(lambda x: pow(x, 2), v1)), 0.5)
    print v1, d
    return map(lambda x: x / d, v1)

def turnaround(l):
    res = []
    for i in range(len(l[0])):
        res.append([])
    for lp in l:
        for (i, p) in enumerate(lp):
            res[i].append(p)

    #print "turnaround", len(l), len(l[0]), len(res), len(res[0])
    return res

def plane_normal(p1, p2, p3):
    x1 = p1[0]
    y1 = p1[1]
    z1 = p1[2]
    x2 = p2[0]
    y2 = p2[1]
    z2 = p2[2]
    x3 = p3[0]
    y3 = p3[1]
    z3 = p3[2]
    vector1 = normalise([x2 - x1, y2 - y1, z2 - z1])
    vector2 = normalise([x3 - x1, y3 - y1, z3 - z1])

    #print "vector1", vector1
    #print "vector2", vector2
    cross_product = [vector1[1] * vector2[2] - \
                     vector1[2] * vector2[1], 
                     -1 * (vector1[0] * vector2[2] - \
                           vector1[2] * vector2[0]),
                     vector1[0] * vector2[1] - \
                     vector1[1] * vector2[0]]

    a = cross_product[0]
    b = cross_product[1]
    c = cross_product[2]
    d = - (cross_product[0] * x1 + \
           cross_product[1] * y1 + \
           cross_product[2] * z1)

    #print a, b, c, d

    return [a, b, c]

def spline_divide(plist, step=0.1):
    res = []
    for l in plist:
        print "spline", l
        s = Spline(len(l)-1, l)
        #s.Spaceout()
        res.append(s.plot(step))
    return res

def spline_double_divide(pl, step_h=0.1, step_v=0.1):
    res = turnaround(pl)
    res = spline_divide(res, step_h)
    res = turnaround(res)
    #print len(res), len(res[0])
    res = spline_divide(res, step_v)
    #print len(res), len(res[0])
    return res

def foursplit_spline(plist, step_h, step_v, loopx=True):

    length = len(plist[0]) / 4
    for i in range(4):
        pl = []
        for l in plist:
            if i == 0:
                pl.append(l[0:length+1])
            elif i == 3:
                pl.append(l[3*length:4*length])
                if loopx:
                    pl[-1].append(l[0])
            else:
                pl.append(l[i*length:(i+1)*length+1])
        print "pl", i, pl
        pl = spline_double_divide(pl, step_h, step_v)
        for j, l in enumerate(pl):
            if i != 3 or loopx:
                pl[j] = l[:-1]
            #if i != 0:
                #pl[j] = l[1:]
        if i == 0:
            res = pl
        else:
            for (j, l) in enumerate(pl):
                res[j] += l

    return res

class Offset:
    def __init__(self, offs):
        self.offs = offs
    def offset(self, t):
        if isinstance(t, list):
            return map(self.offset, t)
        return tuple(map(lambda x: x+self.offs, t))
    def voffset(self, t):
        if isinstance(t, list):
            return map(self.voffset, t)
        return tuple(map(lambda (x,y): x+y, list(zip(self.offs, t))))

def surface_front_end(l):
    return [(0, l*2, l), (l*2, l*3, l)]

def surface_back_end(l):
    o = Offset(l-1)
    return o.offset([(0, l, l*2), (l*3, l*2, l)])

def end_indices_from_pointsets(l, invert=False):
    triangles = []
    for i in range(l-1):
        if invert:
            triangles.append((i, i+1, l*2+i+1))
            triangles.append((l*2+i+1, l*2+i, i))
        else:
            triangles.append((i+1, i, l*2+i+1))
            triangles.append((l*2+i, l*2+i+1, i))
    return triangles
        
def surface_indices_from_pointsets(l, invert=False, offs=0):
    triangles = []
    for i in range(l-1):
        if invert:
            triangles.append((offs+i, offs+i+1, offs+l+i+1))
            triangles.append((offs+l+i+1, offs+l+i, offs+i))
        else:
            triangles.append((offs+i+1, offs+i, offs+l+i+1))
            triangles.append((offs+l+i, offs+l+i+1, offs+i))
    return triangles
        
class SurfaceFromCurves:

    def __init__(self, plist, loopy=False):
        self.loopy = loopy
        self.plist = plist
        llen = len(self.plist)
        if loopy:
            for i in range(llen):
                pl1 = self.plist[i]
                self.plist[i].append(pl1[0])
                
        self.sp = surface_indices_from_pointsets(len(plist[0]))
        self.isp = surface_indices_from_pointsets(len(plist[0]), True)
        
    def create_surface_pair(self, points1, points2, po):

        t_idx = copy(self.sp)

        plen = len(points1)

        o = Offset(1)
        ol = Offset(plen*2)
        #print "offset points1", points1
        #print "offset points2", points2
        #print

        points3 = []
        points4 = []

        for i in range(plen):
            if i < plen-1:
                p1 = points1[i]
                p2 = points2[i]
                p3 = points1[i+1]
                m = -po
            else:
                p1 = points1[i]
                p2 = points2[i]
                p3 = points1[i-1]
                m = po
            [a, b, c] = plane_normal(p1, p2, p3)

            a *= m
            b *= m
            c *= m

            x1 = p1[0]
            y1 = p1[1]
            z1 = p1[2]
            x2 = p2[0]
            y2 = p2[1]
            z2 = p2[2]

            pt1 = [x1 + a, y1 + b, z1 + c]
            pt2 = [x2 + a, y2 + b, z2 + c]

            points3.append(pt1)
            points4.append(pt2)

        #print "triangles", t_idx

        t_ofs_idx = copy(self.isp)
        t_ofs_idx = ol.offset(t_ofs_idx)

        points = [points1, points2, points3, points4]
        triangles = t_idx + t_ofs_idx
        if not self.loopy:
            triangles += surface_front_end(plen) + surface_back_end(plen)

        return points, triangles

    def create_surface(self, po, scale=(1.0, 1.0, 1.0),
                                 trans=(0.0, 0.0, 0.0),
                                 loopx=False):

        points = []
        triangles = []

        trans = vmult(trans, scale)

        n = []
        p = []
        llen = len(self.plist)

        for i in range(llen-(1 if loopx else 0)):
            pl1 = self.plist[i]
            pl2 = self.plist[(i+1) % llen]
            plen = len(pl1)
            npoints, ntriangles = self.create_surface_pair(pl1, pl2, po)
            n.append(npoints)
            p.append(ntriangles)

        nc = deepcopy(n)
        for i in range(llen-2):
            for j in range(plen):
                p1 = nc[(i+1) % llen][2][j]
                p2 = nc[i][3][j]
                np = vmult([0.5,0.5,0.5], vtrans(p1, p2))
                #np = vtrans(p1, [0, 0, -100])
                #print p1, p2, np
                n[(i+1) % llen][2][j] = np
                n[i][3][j] = np
                
        if self.loopy:
            nc = deepcopy(n)
            for i in range(llen):
                for lst in [2,3]:
                    p1 = nc[i][lst][0]
                    p2 = nc[i][lst][plen-1]
                    np = vmult([0.5,0.5,0.5], vtrans(p1, p2))
                    #np = vtrans(p1, [0, 0, -100])
                    #print p1, p2, np
                    n[i][lst][0] = np
                    n[i][lst][plen-1] = np

        for i in range(len(self.plist)-1):
            npoints = n[i]
            npoints = npoints[0] + npoints[1] + npoints[2] + npoints[3]
            ntriangles = p[i]
            ol = Offset((len(npoints), len(npoints), len(npoints)))
            triangles = ol.voffset(triangles)
            points = npoints + points
            triangles = ntriangles + triangles
            if i == 0:
                pln = len(self.plist[0])
                #olr = Offset((pln*2, pln*2, pln*2))
                olr = Offset((0, 0, 0))
                right_edge = olr.voffset(end_indices_from_pointsets(pln, True))
                triangles += right_edge

        pln = len(self.plist[0])
        ol = Offset((pln, pln, pln))
        left_edge = ol.voffset(end_indices_from_pointsets(pln))
        triangles += left_edge 

        points = map(list, points)
        triangles = map(list, triangles) 

        points = [vtrans(trans, vmult(scale, p)) for p in points]

        return polyhedron(points=points, faces=triangles)

if __name__ == '__main__':
    p1 = [(0,0,0), (100,0,20), (200,0,0), (300,0, 60)]
    p2 = [(0,100,0), (100,100,10), (200,100,0), (300, 120, 100)]
    p3 = [(0,200,50), (100,200,0), (200,200,250), (300, 220, 80)]
    p4 = [(0,220,-50), (100,300,0), (200,300,50), (250, 280, 0)]

    plist = [p1, p2, p3, p4]

    plist = spline_double_divide(plist, step_h=0.05, step_v=0.05)

    scale = (0.01, 0.01, 0.01)
    po = 20
    p = SurfaceFromCurves(plist).create_surface(po, scale)

    t = union()
    t.add(p)

    scad_render_to_file(t, "test.scad")

