from pyopenscad import *
from polysurface import spline_double_divide, Offset, SurfaceFromCurves

spline_me = False

import math
def frange(x, y, jump):
  while x < y:
    yield x
    x += jump

def polar(x, y):
    return math.hypot(x, y), math.atan2(y, x)

def test_bonnet1(thick, scl):

    inner_hole = 25.4/2.0
    inner_radius = 30.0
    outer_radius = 60.0
    bearing_radius = 10.0
    diff = (outer_radius - inner_radius) / 2.0
    centre_radius = inner_radius + diff

    step = math.pi / 200.0
    rlist = []

    angle = -math.pi
    while angle < math.pi:
        radius = outer_radius#math.sin(angle*3) * diff + centre_radius
        rlist.append((radius, angle))
        angle += step

    angle = 0.0
    for p in range(len(rlist)):
        rrad, angle = rlist[p]
        radius = math.sin(angle*3) * diff + centre_radius + bearing_radius
        x = math.sin(angle) * radius
        y = math.cos(angle) * radius
        ba = -math.pi
        while ba < math.pi:
            x1 = x + (math.sin(ba) * bearing_radius)
            y1 = y + (math.cos(ba) * bearing_radius)
            dist = math.hypot(x1, y1)
            ang = math.atan2(y1, x1)
            maxadiff = 100000.0
            for (i, r) in enumerate(rlist):
                r, a = r
                adiff = abs(ang-a)
                if adiff < maxadiff:
                    maxadiff = adiff
                    besti = i
                    besta = a
                    bestr = r
            rlist[besti] = (min(bestr, dist), besta)
            ba += step/5

    plist = []
    for (radius, angle) in rlist:

        p0 = [(math.sin(angle) * inner_hole, math.cos(angle) * inner_hole, 0)]
        p0.append((math.sin(angle) * radius,
                   math.cos(angle) * radius, 0))
        angle += step
        plist.append(p0)

    if spline_me: plist = spline_double_divide(plist, step_v=0.15, step_h=.15)

    po = Offset((0, 0, -thick))
    return SurfaceFromCurves(plist).create_surface(po, scl)


def bullbars_front(scl, mirror):
    u = union()
    r = rotate([90, 0, 90])
    for bb in range(3):
        r.add(cylinder(h=90*scl, r=3*scl, center=True))
        t = translate(v=[-45*scl*mirror, 230*scl, -(97-bb*19)*scl])
        t.add(r)
        u.add(t)

    r = rotate([0, 0, 90])
    r.add(cylinder(h=40*scl, r=3*scl, center=True))
    t = translate(v=[-88*scl*mirror, 230*scl, -(97-19)*scl])
    t.add(r)
    u.add(t)

    r = rotate([0, 0, 90])
    r.add(cylinder(h=40*scl, r=3*scl, center=True))
    t = translate(v=[-55*scl*mirror, 230*scl, -(97-19)*scl])
    t.add(r)
    u.add(t)
    return u

def create_lobe(t, _scl, mirror):

    scl = [-_scl*mirror, _scl, _scl]

    b = union()
    c = color([0.0, 0.0, 0.0, 1.0])
    b.add(test_bonnet1(8.0, scl))
    c.add(b)

    t.add(c)


if __name__ == '__main__':

    scl = 0.1
    t = union()
    create_lobe(t, scl, 1.0)

    scad_render_to_file(t, "trilobegen.scad")
    f = open("trilobe.scad", "w")
    f.write("""projection(cut=false) include<trilobegen.scad>;
    """)
    f.close()

