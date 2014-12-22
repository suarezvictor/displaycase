from pyopenscad import *
from polysurface import spline_double_divide, Offset, SurfaceFromCurves

def powerbutton(scl):
    t = translate(v=[1725*scl, 300*scl, (-90.51)*scl])
    t.add(r)
    return t

def drill_holes(_scl):

    rad = 6 # 1.2mm diameter
    dh = []
    r = union()
    t =-30
    b = 1124
    l = -137
    r = 1740

    for x, y in [(l,t), (r,t), (l,b), (r,b)]:
        h = cylinder(h=130*scl, r=rad*scl, segments=50, center=True)
        t = translate(v=[x*scl, y*scl, 0*scl])
        t.add(h)
        dh.append(t)

    top = -58
    bottom = 1150
    left = 240
    lefty = -160 
    right = 1150
    rightx = 1300
    righty = 1767 
    xt = [left, 480, right]
    yl = [525]
    yr = [525]
    xb = [660, right]
    for x in xt:
        h = cylinder(h=130*scl, r=rad*scl, segments=50, center=True)
        t = translate(v=[x*scl, top*scl, 0*scl])
        t.add(h)
        dh.append(t)
    for x in xb:
        h = cylinder(h=130*scl, r=rad*scl, segments=50, center=True)
        t = translate(v=[x*scl, bottom*scl, 0*scl])
        t.add(h)
        dh.append(t)
    for y in yl:
        h = cylinder(h=130*scl, r=rad*scl, segments=50, center=True)
        t = translate(v=[lefty*scl, y*scl, 0*scl])
        t.add(h)
        dh.append(t)
    for y in yr:
        h = cylinder(h=130*scl, r=rad*scl, segments=50, center=True)
        t = translate(v=[righty*scl, y*scl, 0*scl])
        t.add(h)
        dh.append(t)
    return dh



if __name__ == '__main__':

    scl = 0.08
    t = union()
    #t.add(cube(size=[140*scl,82*scl,30*scl]))
    t.add(cylinder(h=30*scl, r=80*scl, segments=50, center=True))
    c = [0.3, 0.5, 0.8, 1.0]
    rad=15
    u = union()
    h = cylinder(h=130*scl, r=rad*scl, segments=50, center=True)
    r = translate(v=[30*scl, 30*scl, 40*scl])
    r.add(h)
    u.add(r)
    h = cylinder(h=130*scl, r=rad*scl, segments=50, center=True)
    r = translate(v=[30*scl, -30*scl, 40*scl])
    r.add(h)
    u.add(r)
    t -= u
    u = union()
    h = cylinder(h=20*scl, r=rad*scl, segments=50, center=True)
    r = translate(v=[5*scl, 0*scl, 20*scl])
    r.add(h)
    u.add(r)
    t += u

    u = union()
    r = translate(v=[-170*scl, 0*scl, 0*scl])
    r.add(cube(size=[210*scl,62*scl,30*scl], center=True))
    u.add(r)
    t.add(u)

    u = union()
    r = translate(v=[-120*scl, 0*scl, 0*scl])
    r.add(cube(size=[30*scl,182*scl,30*scl], center=True))
    u.add(r)
    t.add(u)

    u = union()
    r = translate(v=[-210*scl, 30*scl, 0*scl])
    b = cube(size=[40*scl,130*scl,30*scl], center=True)
    rt = rotate(a=70, v=[0,0,1])
    rt.add(b)
    r.add(rt)
    u.add(r)
    t.add(u)

    u = union()
    r = translate(v=[-210*scl, -30*scl, 0*scl])
    b = cube(size=[40*scl,130*scl,30*scl], center=True)
    rt = rotate(a=-70, v=[0,0,1])
    rt.add(b)
    r.add(rt)
    u.add(r)
    t.add(u)

    u = union()
    r = translate(v=[-300*scl, -30*scl, 0*scl])
    b = cube(size=[70*scl,30*scl,30*scl], center=True)
    r.add(b)
    u.add(r)
    t.add(u)

    u = union()
    r = translate(v=[-340*scl, 30*scl, 15*scl])
    b = cube(size=[30*scl,30*scl,60*scl], center=True)
    r.add(b)
    u.add(r)
    t.add(u)

    u = union()
    r = translate(v=[-300*scl, 30*scl, 0*scl])
    b = cube(size=[70*scl,30*scl,30*scl], center=True)
    r.add(b)
    u.add(r)
    t.add(u)

    u = union()
    r = translate(v=[-340*scl, -30*scl, 15*scl])
    b = cube(size=[30*scl,30*scl,60*scl], center=True)
    r.add(b)
    u.add(r)
    t.add(u)

    u = union()
    h = cylinder(h=40.2*scl, r=50*scl, segments=50, center=True)
    r = translate(v=[25*scl, 00*scl, 0*scl])
    r.add(h)
    u.add(r)
    v = union()
    h = cylinder(h=31.2*scl, r=42*scl, segments=50, center=True)
    v.add(h)
    v -= u
    t -= v

    #t = translate(v=[0,0,114*scl]).add(t)
    t = color(c).add(t)

    #projection(cut=False).add(t)

    scad_render_to_file(t, "test_prog.scad")
    f = open("test_model.scad", "w")
    f.write("""include<test_prog.scad>;
    """)
    f.close()

