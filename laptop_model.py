from pyopenscad import *
from polysurface import spline_double_divide, Offset, SurfaceFromCurves

test = False

if not test:
    t_l = 1028
    t_w = 1752
    lcd_l = 2100
    lcd_w = 3598
    lcd_d = 50
else:
    t_l = 200
    t_w = 200


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

def touch_arc(rad, ht, bwid, iro, scl, roffs=0, roffsinner=0):
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
    r.add(c)
    t = translate(v=[0,0,-ht/2*scl+7.5*scl])
    t.add(r)
    return t

def lcd_panel(scl):

    shear = 0
    innershear = 0
    w = lcd_w
    h = lcd_l
    d = lcd_d

    a = union()

    r = union()
    c = cube(size=[h*scl,w*scl,d*scl])
    c = rotate([00, 0, 0 ]).add(c)
    r.add(c)
    t = translate(v=[(-93)*scl, (-40)*scl, (32.5-d)*scl])
    t.add(r)
    a.add(t)

    return a

def screen_end(scl):

    shear = 0
    innershear = 0
    w = lcd_l
    bwid = 20
    iro = 0

    ht = 20
    rad = 15
    gap = 3

    a = union()

    # top edge
    r = union()
    c = shearedcube(size=[(bwid+iro)*scl,(w+gap*2)*scl,ht*scl],
                shear=[-shear*scl, 0, 0],
                innershear=[-innershear*scl, 0, 0])
    c = rotate([0, 90, 90]).add(c)
    r.add(c)
    t = translate(v=[(w+65)*scl, (16.5-ht)*scl, (30-lcd_d)*scl])
    t.add(r)
    a.add(t)

    # bottom edge
    r = union()
    c = shearedcube(size=[(bwid+iro)*scl,(w+gap*2)*scl,ht*scl],
                shear=[-shear*scl, 0, 0],
                innershear=[-innershear*scl, 0, 0])
    c = rotate([0, 90, 90]).add(c)
    r.add(c)
    t = translate(v=[(w+65)*scl, (16.5-ht)*scl, (50+gap)*scl])
    t.add(r)
    a.add(t)

    # middle filler
    r = union()
    c = shearedcube(size=[(lcd_d+gap*2)*scl,(w+gap*2)*scl,ht*scl],
                shear=[-shear*scl, 0, 0],
                innershear=[-innershear*scl, 0, 0])
    c = rotate([0, 90, 90]).add(c)
    r.add(c)
    t = translate(v=[(w+65)*scl, (16.5-ht)*scl, (30+gap)*scl])
    t.add(r)
    a.add(t)

    # top end curve
    inner_rad=rad
    r = touch_arc(inner_rad, ht, bwid, inner_rad, scl)
    r = rotate([180, -90, 90]).add(r)
    t = translate(v=[+(63-gap)*scl, 9*scl, (30-lcd_d+rad)*scl])
    t.add(r)
    a.add(t)

    # bottom end curve
    inner_rad=rad
    r = touch_arc(inner_rad, ht, bwid, inner_rad, scl)
    r = rotate([180, 90, 90]).add(r)
    t = translate(v=[+(63-gap)*scl, 4*scl, (33-rad)*scl])
    t.add(r)
    a.add(t)

    return a

def create_laptop(t, _scl, mirror, colour, part):

    if part != 0:
        return
    scl = [-_scl*mirror, _scl, _scl]

    c = color(colour)
    c.add(t)

    b = union()

    if part == 0:
        b.add(screen_end(_scl))

    c = color([0.2, 0.2, 0.2, 1.0])
    c.add(b)
    t.add(c)

if __name__ == '__main__':

    scl = 0.1
    t = union()
    c = [0.3, 0.5, 0.8, 1.0]
    if False: # de-blob creation
        u = union()
        u.add(cube(size=[150, 1.6, 0.25]))
        u = translate(v=[0*scl,-10*scl,0]).add(u)
        #t.add(cube(size=[150, 0.8, 0.25]))
        t.add(u)
    else:
        create_laptop(t, scl, 1.0, c, part=0)
    t = translate(v=[-155.5*scl,-61*scl,0]).add(t)
    t = color(c).add(t)

    if False:
        card = import_stl(filename = "eoma68.stl")
        r = rotate([90,180,0]).add(card)
        t.add(r)

    if True: # add inner parts for reference
        t.add(lcd_panel(scl))

    scad_render_to_file(t, "laptop_prog.scad")
    f = open("laptop_model.scad", "w")
    f.write("""include<laptop_prog.scad>;
    """)
    f.close()
