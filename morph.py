from pyopenscad import *
import math
from polysurface import *

def mk_sq(xw, yw, ht, offs=0.5):
    sq = []

    if True:
        ioffs = 1-offs
        sq.append([xw        , 0         , ht])
        #sq.append([xw       , -yw*ioffs , ht])
        sq.append([xw        , -yw*offs  , ht])
        sq.append([xw        , -yw       , ht])
        sq.append([xw*offs   , -yw       , ht])
        #sq.append([xw*ioffs , -yw       , ht])
        sq.append([0         , -yw       , ht])
        #sq.append([-xw*ioffs, -yw       , ht])
        sq.append([-xw*offs  , -yw       , ht])
        sq.append([-xw       , -yw       , ht])
        sq.append([-xw       , -yw*offs  , ht])
        #sq.append([-xw      , -yw*ioffs , ht])
        sq.append([-xw       , 0         , ht])
        #sq.append([-xw      , yw*ioffs  , ht])
        sq.append([-xw       , yw*offs   , ht])
        sq.append([-xw       , yw        , ht])
        sq.append([-xw*offs  , yw        , ht])
        #sq.append([-xw*ioffs, yw        , ht])
        sq.append([0         , yw        , ht])
        #sq.append([xw*ioffs , yw        , ht])
        sq.append([xw*offs   , yw        , ht])
        sq.append([xw        , yw        , ht])
        sq.append([xw        , yw*offs   , ht])
        #sq.append([xw       , yw*ioffs  , ht])
    else:
        for i in range(2):
            sq.append([xw        , -yw       , ht])
        for i in range(4):
            sq.append([-xw       , -yw       , ht])
        for i in range(4):
            sq.append([-xw       , yw        , ht])
        for i in range(4):
            sq.append([xw        , yw        , ht])
        for i in range(2):
            sq.append([xw        , -yw       , ht])

    return sq

def pmult(l, m):
    res = []
    for x in l:
        res += [x] * m
    return res

if __name__ == '__main__':

    circ = []
    npoints = 16
    for i in range(npoints):
        j = i + npoints / 4.0
        x = math.sin(j/(npoints/2)*math.pi)
        y = math.cos(j/(npoints/2)*math.pi)
        circ.append([x*40, y*40, 0])

    sq1 = mk_sq(30, 30, 50, 0.9)
    sq2 = mk_sq(20, 40, 100, 0.9)
    sq3 = mk_sq(10, 60, 150, offs=0.90)

    plist = [circ, sq1, sq2, sq3]
    #plist.append(pmult(sq3, 10))

    plist = spline_double_divide(plist, step_h=0.1, step_v=0.05)


    scale = (0.01, 0.01, 0.01)
    po = -4
    p = SurfaceFromCurves(plist, loopy=True).create_surface(po, scale)

    t = union()
    t.add(p)

    scad_render_to_file(t, "test.scad")

