from pyopenscad import *
from polysurface import spline_double_divide, Offset, SurfaceFromCurves

test = False

if not test:
    lcd_l = 3598.0
    lcd_w = 2100.0
    lcd_la = 3500.0
    lcd_wa = 1970.1
    lcd_d = 50
else:
    t_l = 200
    t_w = 200

bwid = 25
lcd_inset_top = 20
lcd_inset_bot = 130
lcd_gap = 3
lcd_hinge_inner_rad=85
lcd_ext_rot_angle=250
lcd_outer_rad = lcd_hinge_inner_rad+bwid

def hinge_translate(scl):
    return translate(v=[+(+lcd_inset_bot+lcd_w+63-lcd_gap)*scl,
                       0,
                        (30-lcd_d+lcd_hinge_inner_rad)*scl])
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

def screen_mid1(scl, ht=60):

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

    # bottom end curve
    r = union()
    r = touch_arc(lcd_hinge_inner_rad, ht, bwid, 30, scl)
    r = rotate([180, 90, 90]).add(r)
    r = rotate([0, lcd_ext_rot_angle, 0]).add(r)
    t = translate(v=[+(-lcd_inset_top+w+63-lcd_gap)*scl, (-ht+24)*scl, (30-lcd_d+lcd_hinge_inner_rad)*scl]).add(r)
    a.add(t)

    # hinge
    r = union()
    r = touch_arc(lcd_hinge_inner_rad, ht, bwid, 15, scl)
    r = rotate([180, 90, 90]).add(r)
    r = rotate([0, -10, 0]).add(r)
    t = translate(v=[+(-lcd_inset_top+w+63-lcd_gap)*scl, (-ht+24)*scl, (30-lcd_d+lcd_hinge_inner_rad)*scl]).add(r)
    a.add(t)

    # hinge
    r = union()
    r = touch_arc(lcd_hinge_inner_rad, ht, bwid, 15, scl)
    r = rotate([180, 90, 90]).add(r)
    r = rotate([0, 20, 0]).add(r)
    t = translate(v=[+(-lcd_inset_top+w+63-lcd_gap)*scl, (-ht+24)*scl, (30-lcd_d+lcd_hinge_inner_rad)*scl]).add(r)
    a.add(t)

    # hinge hole
    r = union()
    r = cylinder(r=70*scl, h=(ht+0.3)*scl, segments=50, center=True)
    r = rotate([180, 90, 90]).add(r)
    t = translate(v=[+(-lcd_inset_top+w+63-lcd_gap)*scl, (-ht/2+16.5)*scl, (30-lcd_d+lcd_hinge_inner_rad)*scl]).add(r)
    a -= t

    a = translate(v=[0, (ht-edge_inset)*scl, 0]).add(a)
    return a

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

    # bottom end curve
    r = union()
    r = touch_arc(lcd_hinge_inner_rad, ht, bwid, lcd_hinge_inner_rad, scl)
    r = rotate([180, 90, 90]).add(r)
    r = rotate([0, lcd_ext_rot_angle, 0]).add(r)
    t = translate(v=[+(-lcd_inset_top+w+63-lcd_gap)*scl, (-ht+24)*scl, (30-lcd_d+lcd_hinge_inner_rad)*scl]).add(r)
    #a.add(t)

    # hinge
    r = union()
    r = cylinder(r=(lcd_outer_rad)*scl, h=(ht+0.1)*scl, segments=50, center=True)
    r = rotate([180, 90, 90]).add(r)
    t = hinge_translate(scl).add(r)
    t = translate(v=[0, (-ht/2+16.5)*scl, 0]).add(t)
    a.add(t)

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

    return a

def base_end(scl, ht):
    r = union()
    
def create_laptop(t, scl, mirror, colour, part):

    if part != 0:
        return

    c = color(colour)
    c.add(t)

    b = union()

    if part == 0:
        lcd_end_ht = 40
        ht2 = 250
        b.add(screen_end(scl, lcd_end_ht))
        m = screen_mid1(scl, ht2)
        m = translate(v=[0, lcd_end_ht*scl,0]).add(m)
        b.add(m)
        ht2 += lcd_end_ht

        p = lcd_panel(scl, offs=3)
        p = translate(v=[155.5*scl,61*scl,0]).add(p)
        b -= p

        p = lcd_view_area(scl, offs=3)
        p = translate(v=[155.5*scl,61*scl,0*scl]).add(p)
        b -= p

    if part == 1:
        ht = 40
        b.add(base_end(scl, ht))

    c = color([0.2, 0.2, 0.2, 1.0])
    c.add(b)
    t.add(c)

if __name__ == '__main__':

    scl = 0.1
    t = union()
    c = [0.3, 0.5, 0.8, 0.5]
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
