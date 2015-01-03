from pyopenscad import *
from polysurface import spline_double_divide, Offset, SurfaceFromCurves

test = True

if not test:
    t_l = 1028
    t_w = 1752
else:
    t_l = 1000
    t_w = 1400


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

    #points = [[-v[0]/2, -v[1]/2, -v[2]/2],
    #          [v[0]/2, -v[1]/2, -v[2]/2],
    #          [v[0]/2, v[1]/2, -v[2]/2],
    #          [-v[0]/2, v[1]/2, -v[2]/2],
    #          [-v[0]/2, -v[1]/2, v[2]/2],
    #          [v[0]/2, -v[1]/2, v[2]/2],
    #          [v[0]/2, v[1]/2, v[2]/2],
    #          [-v[0]/2, v[1]/2, v[2]/2]]
    #faces = [[0,1,2], [2,3,0], # back
    #         [6,5,4], [7,6,4], # front
    #         [0,1,4], [4,1,5], # top
    #         [3,2,7], [6,2,7], # bottom
    #         [0,3,4], [3,4,7], # left
    #         [1,2,5], [5,6,2] # right
    #        ]
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

def topsupport(scl, offs=0):
    r = union()
    r.add(cube(size=[(15)*scl,(t_l+160)*scl,40*scl]))
    t = translate(v=[(611)*scl, (-40)*scl, (-90)*scl])
    t.add(r)
    return t

def close_top(scl, ht=15):
    u = union()
    if False:
        c = cube(size=[(t_l+100)*scl,(t_w+120)*scl,ht*scl])
        t = translate(v=[-125*scl, -25*scl, (32.5-ht)*scl])
        t.add(c)
        u.add(t)
    else:
        # save plastic during dev
        c = cube(size=[(t_w+100)*scl,(20)*scl,ht*scl])
        t = translate(v=[-125*scl, (t_l*0.55)*scl, (32.5-ht)*scl])
        t.add(c)
        u.add(t)
        c = cube(size=[(t_w+100)*scl,(20)*scl,ht*scl])
        t = translate(v=[-125*scl, (t_l*0.2)*scl, (32.5-ht)*scl])
        t.add(c)
        u.add(t)
        c = cube(size=[(20)*scl,(t_l+120)*scl,ht*scl])
        t = translate(v=[(40)*scl, -25*scl, (32.5-ht)*scl])
        t.add(c)
        u.add(t)
        c = cube(size=[(20)*scl,(t_l+120)*scl,ht*scl])
        t = translate(v=[(t_w*0.90)*scl, -25*scl, (32.5-ht)*scl])
        t.add(c)
        u.add(t)
        c = cube(size=[(t_w+100)*scl,(20)*scl,ht*scl])
        t = translate(v=[-125*scl, (t_w/2+40)*scl, (32.5-ht)*scl])
        t.add(c)
        u.add(t)
        c = cube(size=[(20)*scl,(t_l+120)*scl,ht*scl])
        t = translate(v=[(t_l/2+92)*scl, -25*scl, (32.5-ht)*scl])
        t.add(c)
        u.add(t)
        c = cube(size=[(20)*scl,(t_l+120)*scl,ht*scl])
        t = translate(v=[(t_w*0.58)*scl, -25*scl, (32.5-ht)*scl])
        t.add(c)
        u.add(t)
    return u


def touch_taped(scl, l, w, ht=15, iro=70, bwid=1):
    a = union()

    r = union()
    r.add(cube(size=[(bwid+iro)*scl,(l+100)*scl,ht*scl]))
    t = translate(v=[-(133+bwid)*scl, -23*scl, (32.5-ht)*scl])
    t.add(r)
    a.add(t)

    r = union()
    r.add(cube(size=[(w+150)*scl,(bwid+iro)*scl,ht*scl]))
    t = translate(v=[-140*scl, (l+112-iro)*scl, (32.5-ht)*scl])
    t.add(r)
    a.add(t)

    r = union()
    r.add(cube(size=[(bwid+iro)*scl,(l+100)*scl,ht*scl]))
    t = translate(v=[(w-iro)*scl, -23*scl, (32.5-ht)*scl])
    t.add(r)
    a.add(t)

    r = union()
    r.add(cube(size=[(w+140)*scl,32*scl,ht*scl]))
    t = translate(v=[-135*scl, -(bwid+37)*scl, (32.5-ht)*scl])
    t.add(r)
    a.add(t)

    v = union()
    v.add(a)

    # wipe off overlapping corners
    r = union()
    r.add(cube(size=[(85)*scl,45*scl,ht*2*scl]))
    t = rotate([0, 0, -45]).add(r)
    t = translate(v=[-170*scl, -10*scl, (32.5-ht*1.5)*scl]).add(t)
    v -= t

    r = union()
    r.add(cube(size=[(85)*scl,45*scl,ht*2*scl]))
    t = rotate([0, 0, -45-90]).add(r)
    t = translate(v=[(w-iro+75)*scl, 20*scl, (32.5-ht*1.5)*scl]).add(t)
    v -= t

    r = union()
    r.add(cube(size=[(85)*scl,45*scl,ht*2*scl]))
    t = rotate([0, 0, -45-90-90]).add(r)
    t = translate(v=[(w-iro+110)*scl, (l+155-iro)*scl, (32.5-ht*1.5)*scl]).add(t)
    v -= t

    r = union()
    r.add(cube(size=[(95)*scl,55*scl,ht*2*scl]))
    t = rotate([0, 0, -45-90-90-90]).add(r)
    t = translate(v=[(-141)*scl, (l+117-iro)*scl, (32.5-ht*1.5)*scl]).add(t)
    v -= t


    return v

def touch_surround(scl, ht=15, iro=0, bwid=50, taped=False, holes=False,
                        shear=0, innershear=None):

    if innershear is None:
        innershear = shear

    a = union()

    l = t_l
    w = t_w

    r = union()
    r.add(shearedcube(size=[(bwid+iro)*scl,l*scl,ht*scl],
                shear=[-shear*scl, 0, 0],
                innershear=[-innershear*scl, 0, 0]))
    t = translate(v=[-(143+bwid)*scl, 37*scl, (33-ht)*scl])
    t.add(r)
    a.add(t)

    r = union()
    c = shearedcube(size=[(bwid+iro)*scl,(w+4.0)*scl,ht*scl],
                shear=[-shear*scl, 0, 0],
                innershear=[-innershear*scl, 0, 0])
    c = rotate([0, 0, -90]).add(c)
    r.add(c)
    t = translate(v=[-67.0*scl, (l+114+bwid)*scl, (32.5-ht)*scl])
    t.add(r)
    a.add(t)

    r = union()
    r.add(shearedcube(size=[(bwid+iro)*scl,l*scl,ht*scl],
                innershear=[shear*scl, 0, 0],
                shear=[innershear*scl, 0, 0]))
    t = translate(v=[(w+13-iro)*scl, 37*scl, (32.5-ht)*scl])
    t.add(r)
    a.add(t)

    r = union()
    c = shearedcube(size=[(bwid+iro)*scl,(w+3)*scl,ht*scl],
                shear=[-shear*scl, 0, 0],
                innershear=[-innershear*scl, 0, 0])
    c = rotate([0, 0, 90]).add(c)
    r.add(c)
    t = translate(v=[(w-62.5)*scl, -(bwid+40)*scl, (32.5-ht)*scl])
    t.add(r)
    a.add(t)

    rad = 78
    r = touch_arc(rad, ht, bwid, iro, scl, roffs=shear, roffsinner=innershear)
    t = translate(v=[-65*scl, 38*scl, 25*scl])
    t.add(r)
    a.add(t)

    r = rotate([0, 0, -90])
    rc = touch_arc(rad, ht, bwid, iro, scl, roffs=shear, roffsinner=innershear)
    r.add(rc)
    t = translate(v=[-65*scl, (l+36)*scl, 25*scl])
    t.add(r)
    a.add(t)

    r = rotate([0, 0, -180])
    rc = touch_arc(rad, ht, bwid, iro, scl, roffs=shear, roffsinner=innershear)
    r.add(rc)
    t = translate(v=[(w-65)*scl, (l+36)*scl, 25*scl])
    t.add(r)
    a.add(t)

    r = rotate([0, 0, 90])
    rc = touch_arc(rad, ht, bwid, iro, scl, roffs=shear, roffsinner=innershear)
    r.add(rc)
    t = translate(v=[(w-65)*scl, 38*scl, 25*scl])
    t.add(r)
    a.add(t)

    if taped:
        a.add(touch_taped(scl, l, w, ht=ht))

    if holes:
        for h in drill_holes(scl, w, l):
            a -= h

    o = union()
    o.add(translate(v=[-8*scl, 0, 0]).add(a))

    return o


def create_picture(t, _scl, mirror, colour, part):

    if part != 2:
        return
    scl = [-_scl*mirror, _scl, _scl]

    c = color(colour)
    c.add(t)

    b = union()
    laminates = False

    p2_inset = 19

    if laminates:
        tb_inset = 30
        innerwall = 13
    else:
        if part == 0:
            tb_inset = 6
            innerwall = 5
            p0_innerwall = 20
            swid = -35
        elif part == 1:
            tb_inset = 0
            innerwall = -12
        else:
            tb_inset = p2_inset
            innerwall = -12
            p2_innerwall = innerwall+4

    if part == 0:
        layers = 0x1f-3
        #layers = 0x18
    elif part == 1:
        layers = 4+8
    elif part == 2:
        layers = 0x7
        #layers = 0x0

    if layers & 0x1:
        if laminates:
            top_ht=15.0
        else:
            top_ht=10.0
        # touchpanel capture layer
        ts=touch_surround(_scl, top_ht+1, 50, tb_inset, holes=laminates,
                          shear=8, innershear=-8)
        td = translate(v=[0,0,(top_ht)*_scl])
        td.add(ts)
        b.add(td)

    if layers & 0x4:

        top_ht = 15
        # layer around touchscreen
        ts=touch_surround(_scl, top_ht, 12, tb_inset, holes=laminates)
        td = translate(v=[0,0,(-15)*_scl])
        td.add(ts)
        b.add(td)

    if layers & 0x2:
        # layer on top of touchscreen
        shear = 10
        innershear = 0
        if part != 1 or laminates:
            ht = 15
        else:
            ht = 10
        if part == 2 and not laminates:
            taped = False
            iw = 10
        elif part == 0 and not laminates:
            innershear = -10
            taped = False
            iw = 18.5
        else:
            taped = True
            iw = 35
        ts = touch_surround(_scl, ht, iw, tb_inset, taped=taped,
                           holes=laminates, shear=shear, innershear=innershear)
        td = translate(v=[0,0,(top_ht-15)*_scl])
        td.add(ts)
        if not test:
            td -= panelcable(_scl) # remove panelcable
        if not test:
            td -= camera(_scl) # remove camera
            #if part != 1 and not laminates:
                #td -= headphone(_scl) # remove headphone
                #if not test:
                    #if part != 2 or laminates:
                #        td -= cardslot(_scl) # remove cpu card
            if not test:
                if part == 0 and not laminates:
                    #td -= sdcard(_scl) # remove sd card
                    td -= pcb(_scl) # remove sd card
        b.add(td)


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
        create_picture(t, scl, 1.0, c, part=2)
    t = translate(v=[-155.5*scl,-61*scl,0]).add(t)
    t = color(c).add(t)

    #projection(cut=False).add(t)

    scad_render_to_file(t, "picture_prog.scad")
    f = open("picture_model.scad", "w")
    f.write("""include<picture_prog.scad>;
    """)
    f.close()
