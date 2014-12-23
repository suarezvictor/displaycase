from pyopenscad import *
from polysurface import spline_double_divide, Offset, SurfaceFromCurves

test = True

if not test:
    t_l = 1018
    t_w = 1746
else:
    t_l = 200
    t_w = 200


def touch_arc(rad, ht, bwid, iro, scl):
    rad2 = bwid+rad
    rad -= iro
    r = union()
    c = cylinder( r=rad2*scl, h=ht*scl, segments=50, center=True)
    c -= cylinder( r=rad*scl, h=(ht+1)*scl, segments=50, center=True)
    cb = cube(size=[rad2*scl,2*rad2*scl,2*(ht)*scl])
    ct = translate(v=[0*scl,-rad2*scl,-ht*scl])
    ct.add(cb)
    c -= ct
    cb = cube(size=[2.2*rad2*scl,rad2*scl,2*(ht)*scl])
    ct = translate(v=[-rad2*scl*1.1,-0*scl,-ht*scl])
    ct.add(cb)
    c -= ct
    r.add(c)
    t = translate(v=[0,0,-ht/2*scl+7.5*scl])
    t.add(r)
    return t

def cardslot(scl, offs=0):
    r = union()
    if test:
        l = 120
    else:
        l = 670
    r.add(cube(size=[(l-offs)*scl,240*scl,150*scl]))
    t = translate(v=[-(60-offs/2)*scl, (t_l+32)*scl, (-83)*scl])
    t.add(r)
    return t

def sdcard(scl):
    r = union()
    r.add(cube(size=[159*scl,125*scl,81.3*scl]))
    t = translate(v=[275*scl, -120*scl, (-53.51)*scl])
    t.add(r)
    return t

def power(scl):
    r = union()
    r.add(cube(size=[85*scl,355*scl,140.2*scl]))
    t = translate(v=[1725*scl, 90*scl, (-90.51)*scl])
    t.add(r)
    return t

def powerbutton(scl):
    r = union()
    r.add(cube(size=[75*scl,52*scl,80.2*scl]))
    t = translate(v=[1725*scl, 300*scl, (-90.51)*scl])
    t.add(r)
    return t

def usb(scl):
    r = union()
    r.add(cube(size=[75*scl,145*scl,100.2*scl]))
    t = translate(v=[1725*scl, 157*scl, (-90.51)*scl])
    t.add(r)
    return t

def pcb(scl):
    r = union()
    r.add(cube(size=[1870*scl,670*scl,80*scl]))
    d = union()
    d.add(cube(size=[100*scl,170*scl,80*scl]))
    d = translate(v=[-1*scl,-1*scl,-1*scl]).add(d)
    r -= d
    d = union()
    d.add(cube(size=[103*scl,52*scl,80*scl]))
    d = translate(v=[1790*scl,-6*scl,-1*scl]).add(d)
    r -= d
    t = translate(v=[-133*scl, -30*scl, (-60.51)*scl])
    t.add(r)
    return t

def panelcable(scl):
    r = union()
    r.add(cube(size=[215*scl,170*scl,120*scl]))
    t = translate(v=[1075*scl, -55*scl, (-90.51)*scl])
    t.add(r)
    return t

def camera(scl):
    r = union()
    r.add(cube(size=[80*scl,80*scl,120*scl]))
    t = translate(v=[-105*scl, 28*scl, (-90.51)*scl])
    t.add(r)
    return t

def headphone(scl):
    r = union()
    r.add(cube(size=[140*scl,85*scl,145.2*scl]))
    t = translate(v=[1665*scl, 33*scl, (-83.51)*scl])
    t.add(r)
    return t

def close_top(scl, ht=15):
    c = cube(size=[1866*scl,1160*scl,ht*scl])
    t = translate(v=[-125*scl, -40*scl, (32.5-ht)*scl])
    t.add(c)
    return t


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
    r.add(cube(size=[(w+140)*scl,35*scl,ht*scl]))
    t = translate(v=[-135*scl, -(bwid+40)*scl, (32.5-ht)*scl])
    t.add(r)
    a.add(t)

    v = union()
    v.add(a)

    # wipe off overlapping corners
    r = union()
    r.add(cube(size=[(65)*scl,35*scl,ht*2*scl]))
    t = rotate([0, 0, -45]).add(r)
    t = translate(v=[-165*scl, -23*scl, (32.5-ht*1.5)*scl]).add(t)
    v -= t

    r = union()
    r.add(cube(size=[(65)*scl,35*scl,ht*2*scl]))
    t = rotate([0, 0, -45-90]).add(r)
    t = translate(v=[(w-iro+80)*scl, 10*scl, (32.5-ht*1.5)*scl]).add(t)
    v -= t

    r = union()
    r.add(cube(size=[(65)*scl,35*scl,ht*2*scl]))
    t = rotate([0, 0, -45-90-90]).add(r)
    t = translate(v=[(w-iro+105)*scl, (l+162-iro)*scl, (32.5-ht*1.5)*scl]).add(t)
    v -= t

    r = union()
    r.add(cube(size=[(65)*scl,35*scl,ht*2*scl]))
    t = rotate([0, 0, -45-90-90-90]).add(r)
    t = translate(v=[(-140)*scl, (l+135-iro)*scl, (32.5-ht*1.5)*scl]).add(t)
    v -= t


    return v

def touch_surround(scl, ht=15, iro=0, bwid=50, taped=False, holes=False):
    a = union()

    l = t_l
    w = t_w

    r = union()
    r.add(cube(size=[(bwid+iro)*scl,l*scl,ht*scl]))
    t = translate(v=[-(143+bwid)*scl, 37*scl, (32.5-ht)*scl])
    t.add(r)
    a.add(t)

    r = union()
    r.add(cube(size=[(w+0.02)*scl,(bwid+iro)*scl,ht*scl]))
    t = translate(v=[-65.01*scl, (l+114-iro)*scl, (32.5-ht)*scl])
    t.add(r)
    a.add(t)

    r = union()
    r.add(cube(size=[(bwid+iro)*scl,l*scl,ht*scl]))
    t = translate(v=[(w+13-iro)*scl, 37*scl, (32.5-ht)*scl])
    t.add(r)
    a.add(t)

    r = union()
    r.add(cube(size=[(w+0.02)*scl,(bwid+iro)*scl,ht*scl]))
    t = translate(v=[-65.01*scl, -(bwid+40)*scl, (32.5-ht)*scl])
    t.add(r)
    a.add(t)

    rad = 78
    r = touch_arc(rad, ht, bwid, iro, scl)
    t = translate(v=[-65*scl, 38*scl, 25*scl])
    t.add(r)
    a.add(t)

    r = rotate([0, 0, -90])
    rc = touch_arc(rad, ht, bwid, iro, scl)
    r.add(rc)
    t = translate(v=[-65*scl, (l+36)*scl, 25*scl])
    t.add(r)
    a.add(t)

    r = rotate([0, 0, -180])
    rc = touch_arc(rad, ht, bwid, iro, scl)
    r.add(rc)
    t = translate(v=[(w-65)*scl, (l+36)*scl, 25*scl])
    t.add(r)
    a.add(t)

    r = rotate([0, 0, 90])
    rc = touch_arc(rad, ht, bwid, iro, scl)
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

def clips(_scl, wd, dp=2, offs=0, doffs=0, ht=60, flat=False):

    dh = []
    t =-24.0
    b = t_l+98.0
    l = -132.0
    r = t_w-14.0

    lst = [(l,t,3.5), (r,t,0.5), (l,b,2.5), (r,b,1.5)]
    if test:
        lst += [(t_w/2, -50, 0),
                (t_w/2, t_l+124, 2),
                (-161, t_l/2, 3),
                (t_w+15, t_l/2, 1)
                    ]

    if not test:
        lst += [(t_w/2, -50, 0),
                (t_w*0.6, t_l+124, 2),
                (-161, t_l*0.55, 3),
                (t_w+15, t_l*0.55, 1)
                    ]

        lst += [(t_w*0.80, -50, 0),
                (t_w*0.85, t_l+124, 2),
                (-161, t_l*0.2, 3),
                
                    ]
        lst += [(-161, t_l*0.85, 3),
                (t_w+15, t_l*0.85, 1)
                    ]
        lst += [(t_w*0.30, -50, 0),
                (t_w*0.11, -50, 0),
                (t_w*0.40, t_l+124, 2),
                    ]
    for x, y, rot in lst:
        if rot in [0.5,1.5,2.5,3.5]:
            wd2 = wd
        else:
            wd2 = 1.5*wd
        h = clip(_scl, wd2, dp, ht, rot+2, offs=offs, doffs=doffs, flat=flat)
                 
        t = translate(v=[x*_scl, y*_scl, (-32)*_scl])
        t.add(h)
        dh.append(t)

    r = union()
    for h in dh:
        r += h

    return r

    top = -69
    bottom = wd+142
    left = 240
    lefty = -167 
    right = wd+132
    righty = ln+38 
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

def drill_holes(_scl, ln, wd):

    rad = 5 # 1.2mm diameter
    dh = []
    r = union()
    t =-35
    b = wd+111
    l = -137
    r = ln+8

    for x, y in [(l,t), (r,t), (l,b), (r,b)]:
        h = cylinder(h=130*scl, r=rad*scl, segments=50, center=True)
        t = translate(v=[x*scl, y*scl, 0*scl])
        t.add(h)
        dh.append(t)

    top = -69
    bottom = wd+142
    left = 240
    lefty = -167 
    right = wd+132
    righty = ln+38 
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

def clip(_scl, w, dp, ht, rot, offs=0, doffs=0, flat=False):
    d=12
    u = union()
    u.add(cube(size=[(w+offs*2)*scl,(dp+offs*2)*scl,(ht+offs*2)*_scl]))
    c = cube(size=[(w+offs*2)*scl,(d+offs*2)*scl,(d+offs*2)*_scl])
    c = rotate(a=-52, v=[1*_scl,0,0]).add(c)
    c = translate(v=[0, -d*0.4*_scl,d*0.8*_scl]).add(c)
    u.add(c)
    c = cube(size=[(w+offs*2)*scl,(d+offs*2)*scl,(d*0.7+offs*2)*_scl])
    c = translate(v=[0, -d*0.4*_scl,d*0.8*_scl]).add(c)
    u.add(c)
    if flat:
        c = cube(size=[(w+offs*2)*scl,(d+offs*2)*scl,(ht+offs*2)*_scl])
        c = translate(v=[0, -d*0.4*_scl,1.5*d*_scl]).add(c)
    else:
        c = cube(size=[(w+offs*2)*scl,(d+offs*2)*scl,(d+offs*2)*_scl])
        c = rotate(a=-32, v=[1*_scl,0,0]).add(c)
        c = translate(v=[0, -d*0.4*_scl,1.5*d*_scl]).add(c)
    u.add(c)

    # cut the back off the rotated rectangles
    v = union()
    b = cube(size=[(w*1.2+offs*4)*_scl,(dp+d*2+offs*2)*_scl,(ht*4+offs*2)*_scl])
    v.add(translate(v=[-w*0.1*_scl, (dp+offs*2)*scl, -ht*_scl*0.5]).add(b))
    u -= v

    t = union()
    t.add(translate(v=[-(offs+w/2)*_scl,
                       -(offs+dp/2-doffs)*_scl,
                       -offs*_scl]).add(u))

    v = union()
    v.add(rotate(a=rot*90, v=[0,0,1]).add(t))

    return v
    
def create_tablet(t, _scl, mirror, colour, part):

    if part != 2:
        return
    scl = [-_scl*mirror, _scl, _scl]

    c = color(colour)
    c.add(t)
    
    b = union()
    laminates = False

    if laminates:
        tb_inset = 50 
        innerwall = 13
    else:
        if part == 0:
            tb_inset = 6 
            innerwall = 0
        elif part == 1:
            tb_inset = 8 
            innerwall = -12
        else:
            tb_inset = 12 
            innerwall = -12

    if part == 0:
        layers = 0x1f-7
    elif part == 1:
        layers = 4+8
    elif part == 2:
        layers = 0x2f

    if layers & 0x1:
        if laminates:
            top_ht=15.0
        else:
            top_ht=10.0
        # touchpanel capture layer
        ts=touch_surround(_scl, top_ht, 25, tb_inset, holes=laminates)
        td = translate(v=[0,0,(top_ht)*_scl])
        td.add(ts)
        b.add(td)

    if layers & 0x2:

        top_ht = 15
        # layer around touchscreen
        ts=touch_surround(_scl, top_ht, -0.0, tb_inset, holes=laminates)
        td = translate(v=[0,0,(top_ht-15)*_scl])
        td.add(ts)
        if part == 2 and not laminates:
            b.add(clips(_scl, 25, dp=3, doffs=-4))
        b.add(td)

    if layers & 0x4:
        # layer on top of touchscreen
        if part == 2 or laminates:
            ht = 15
        else:
            ht = 10
        if part == 2 and not laminates:
            taped = False
            iw = innerwall+4
        else:
            taped = True
            iw = 35
        ts = touch_surround(_scl, ht, iw, tb_inset, taped=taped,
                           holes=laminates)
        td = translate(v=[0,0,-15*_scl])
        td.add(ts)
        if not test:
            td -= panelcable(_scl) # remove panelcable
        if not test:
            td -= camera(_scl) # remove headphone
            if part != 1 and not laminates:
                td -= headphone(_scl) # remove headphone
                if not test:
                    td -= cardslot(_scl) # remove cpu card
            if not test:
                if part == 0 and not laminates:
                    td -= sdcard(_scl) # remove sd card
        b.add(td)

    if layers & 0x8:
        if part != 0 and not laminates:
            ts = touch_surround(_scl, 20, innerwall, tb_inset)
            td = translate(v=[0,0,-25*_scl])
            td.add(ts)
            u = intersection()
            u.add(td)
            u.add(sdcard(_scl)) 
            b.add(u)
            u = intersection()
            u.add(td)
            v = union()
            v.add(power(_scl)) 
            v -= headphone(_scl)
            u.add(v)
            b.add(u)
            u = intersection()
            u.add(td)
            u.add(cardslot(_scl, 20*_scl)) 
            b.add(u)
        else:
            # layer on top of touchscreen
            ts = touch_surround(_scl, 15, innerwall, tb_inset,
                                holes=laminates)
            td = translate(v=[0,0,-30*_scl])
            td.add(ts)
            td -= cardslot(_scl) # remove cpu card
            if not test:
                td -= panelcable(_scl) # remove panelcable
                td -= pcb(_scl) # remove pcb
                td -= camera(_scl) # remove headphone
                td -= headphone(_scl) # remove headphone
                if part == 0 and not laminates:
                    td -= sdcard(_scl) # remove cpu card
                    td -= power(_scl) # remove power jack
            b.add(td)

    if layers & 0x10:
        # layer around cpu card
        ts = touch_surround(_scl, 40, innerwall, tb_inset,
                                holes=laminates)
        td = translate(v=[0,0,-45*_scl])
        td.add(ts)
        td -= cardslot(_scl) # remove cpu card
        if not test:
            td -= panelcable(_scl) # remove panelcable
            td -= pcb(_scl) # remove pcb
            td -= camera(_scl) # remove camera
            td -= power(_scl) # remove power jack
            td -= headphone(_scl) # remove headphone
            td -= sdcard(_scl) # remove microsd
            td -= usb(_scl) # remove usb slot
            td -= powerbutton(_scl) # remove power button 
        b.add(td)

    if layers & 0x20:
        # layer above cpu card and microsd
        ts = touch_surround(_scl, 30, innerwall, tb_inset,
                                holes=laminates)
        td = translate(v=[0,0,-85*_scl])
        td.add(ts)
        td -= camera(_scl) # remove headphone
        td -= usb(_scl) # remove usb slot
        td -= power(_scl) # remove power jack
        td -= headphone(_scl) # remove headphone
        td -= cardslot(_scl, 0) # remove cpu card 
        b.add(td)

    if layers & 0x40:
        top_ht = 10.0
        # top case
        ts = touch_surround(_scl, top_ht, 40, tb_inset,
                                holes=laminates)
        if not test:
            ts += close_top(_scl, top_ht) # complete top
        td = translate(v=[0,0,-115*_scl])
        td.add(ts)
        b.add(td)

    if part == 0 and not laminates:
        c = union()
        c += clips(_scl, 35, dp=0, offs=3, ht=10, doffs=-8, flat=True)
    
        u = union()
        u.add(b)
        u += c
        b = u

    if part != 2 and not laminates:
        c = union()
        c += clips(_scl, 25, dp=1, offs=3, doffs=-4, flat=part==1)
    
        u = union()
        u.add(b)
        u -= c
        b = u

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
        create_tablet(t, scl, 1.0, c, part=0)
        create_tablet(t, scl, 1.0, c, part=1)
        create_tablet(t, scl, 1.0, c, part=2)
    t = translate(v=[-152.5*scl,-56*scl,0]).add(t)
    t = color(c).add(t)

    #projection(cut=False).add(t)

    scad_render_to_file(t, "car_prog.scad")
    f = open("car_model.scad", "w")
    f.write("""include<car_prog.scad>;
%import_stl(filename = "tablet10.stl");
    """)
    f.close()

