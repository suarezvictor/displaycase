from operator import add
from pyopenscad import *
from copy import copy
from spline import Spline

def vmult(v1, v2):
    return map(lambda (x,y): x*y, zip(v1, v2))

def vtrans(v1, v2):
    return map(lambda (x,y): x+y, zip(v1, v2))

def turnaround(l):
    res = []
    for i in range(len(l[0])):
        res.append([])
    for lp in l:
        for (i, p) in enumerate(lp):
            res[i].append(p)

    #print "turnaround", len(l), len(l[0]), len(res), len(res[0])
    return res

def spline_divide(plist, step=0.1):
    res = []
    for l in plist:
        #print "spline", l
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
        
def surface_indices_from_pointsets(l, invert=False):
    triangles = []
    for i in range(l-1):
        if invert:
            triangles.append((i, i+1, l+i+1))
            triangles.append((l+i+1, l+i, i))
        else:
            triangles.append((i+1, i, l+i+1))
            triangles.append((l+i, l+i+1, i))
    return triangles
        
class SurfaceFromCurves:

    def __init__(self, plist):
        self.sp = surface_indices_from_pointsets(len(plist[0]))
        self.isp = surface_indices_from_pointsets(len(plist[0]), True)
        self.plist = plist
        
    def create_surface_pair(self, points1, points2, po):

        t_idx = copy(self.sp)

        plen = len(points1)

        o = Offset(1)
        ol = Offset(plen*2)
        points3 = po.voffset(points1)
        points4 = po.voffset(points2)
        #print "offset", points1, points3

        #print "triangles", t_idx

        t_ofs_idx = copy(self.isp)
        t_ofs_idx = ol.offset(t_ofs_idx)

        points = points1+points2+points3+points4
        triangles = t_idx + t_ofs_idx + surface_front_end(plen) + surface_back_end(plen)

        return points, triangles

    def create_surface(self, po, scale=(1.0, 1.0, 1.0),
                                 trans=(0.0, 0.0, 0.0)):

        points = []
        triangles = []

        trans = vmult(trans, scale)

        for i in range(len(self.plist)-1):
            pl1 = self.plist[i]
            pl2 = self.plist[i+1]
            npoints, ntriangles = self.create_surface_pair(pl1, pl2, po)
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
    p3 = [(0,200,50), (100,200,0), (200,200,400), (300, 220, 80)]
    p4 = [(0,300,50), (100,300,0), (200,300,50), (300, 320, 80)]

    plist = [p1, p2, p3, p4]

    #plist = spline_double_divide(plist, step_h=0.1, step_v=0.1)

    scale = (0.01, 0.01, 0.01)
    po = Offset((0,0,50))
    p = SurfaceFromCurves(plist).create_surface(po, scale)

    t = union()
    t.add(p)

    scad_render_to_file(t, "test.scad")

