from pyopenscad import *
from polysurface import spline_double_divide, Offset, SurfaceFromCurves

test = False

if not test:
    t_l = 1028
    t_w = 1752
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
        l = 70
    else:
        l = 670
    r.add(cube(size=[(l-offs)*scl,240*scl,150*scl]))
    t = translate(v=[-(60-offs/2)*scl, (t_l+32)*scl, (-100)*scl])
    t.add(r)
    return t

def sdcard(scl, offs=0):
    r = union()
    r.add(cube(size=[(165-offs)*scl,125*scl,151.3*scl]))
    t = translate(v=[(275+offs/2)*scl, -120*scl, (-100.51)*scl])
    t.add(r)
    return t

def power(scl, offs=0):
    r = union()
    r.add(cube(size=[85*scl,(410-offs)*scl,160.2*scl]))
    t = translate(v=[1725*scl, (70+offs/2)*scl, (-100.51)*scl])
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
    t = translate(v=[1075*scl, -25*scl, (-90.51)*scl])
    t.add(r)
    return t

def camera(scl):
    r = union()
    r.add(cube(size=[80*scl,80*scl,120*scl]))
    t = translate(v=[-105*scl, 28*scl, (-90.51)*scl])
    t.add(r)
    return t

def headphone(scl, offs=0):
    r = union()
    r.add(cube(size=[140*scl,(115-offs)*scl,165.2*scl]))
    t = translate(v=[1665*scl, (34+offs/2)*scl, (-103.51)*scl])
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
        c = cube(size=[(t_w+100)*scl,(30)*scl,ht*scl])
        t = translate(v=[-125*scl, (t_w/2+20)*scl, (32.5-ht)*scl])
        t.add(c)
        u.add(t)
        c = cube(size=[(30)*scl,(t_l+120)*scl,ht*scl])
        t = translate(v=[(t_l/2+255)*scl, -25*scl, (32.5-ht)*scl])
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

def capture1(_scl, ioff=0, oof=0):
    u = union()
    c = cube(size=[(40+oof-ioff)*scl,(45+oof)*scl,(50+oof)*_scl])
    c = translate(v=[(-oof+ioff)/2.0*_scl, 0, 0]).add(c)
    u.add(c)
    c = cube(size=[(42+oof*2)*scl, 60*scl, 30*scl])
    c = translate(v=[(-oof+ioff-2)/2.0*_scl, 0, 0]).add(c)
    c = rotate(a=-50.0, v=[1*_scl,0,0]).add(c)
    c = translate(v=[0, (16+oof/2.5)*_scl,55*_scl]).add(c)
    u -= c
    c = cube(size=[(42+(oof-ioff)*2)*scl, 30*scl, 10*scl])
    c = translate(v=[(-oof+ioff-2)/2.0*_scl, 0, 0]).add(c)
    c = rotate(a=-60.0, v=[1*_scl,0,0]).add(c)
    c = translate(v=[0, 18*_scl,5*_scl]).add(c)
    u -= c
    c = cube(size=[(42+(oof-ioff)*2)*scl, (20+ioff)*scl, (25+ioff)*scl])
    c = translate(v=[(-oof+ioff-2)/2.0*_scl, 0, 0]).add(c)
    c = translate(v=[0, 7*_scl,-5*_scl]).add(c)
    u -= c

    return u

def capture(_scl, ioff=0, oof=0):

    if test:
        w1 = [t_w*0.35]
        w2 = [t_w*0.64]
    else:
        w1 = [t_w*0.118, t_w*.266, t_w*0.54, t_w*0.92]
        w2 = [t_w*0.387, t_w*0.65]
    v = union()

    for w in w1:
        t = translate(v=[w*_scl, (-60)*_scl, (-32)*_scl])
        t.add(capture1(_scl, ioff, oof))
        v.add(t)

    for w in w2:
        t = rotate(a=180.0, v=[0,0,1])
        t.add(capture1(_scl, ioff, oof))
        t = translate(v=[(w-oof/2.0)*_scl, (t_l+134)*_scl, (-32)*_scl]).add(t)
        v.add(t)

    for h in [t_l/2+140, t_l-20]:
        t = rotate(a=90.0, v=[0,0,1])
        t.add(capture1(_scl, ioff, oof))
        t = translate(v=[(t_w+25)*_scl, h*_scl, (-32)*_scl]).add(t)
        v.add(t)

    for h in [t_l/2+10, t_l+36]:
        t = rotate(a=-90.0, v=[0,0,1])
        t.add(capture1(_scl, ioff, oof))
        t = translate(v=[(-171)*_scl, h*_scl, (-32)*_scl]).add(t)
        v.add(t)

    return v

def clips(_scl, wd, dp=2, offs=0, doffs=0, ht=60, z=0, flat=False):

    dh = []
    t =-24.0
    b = t_l+98.0
    l = -132.0
    r = t_w-14.0

    lst = [(l,t,3.5), (r,t,0.5), (l,b,2.5), (r,b,1.5)]
    if test:
        lst += [(t_w*0.18, -49, 0),
                (t_w*0.18, t_l+123, 2),
                (-160, t_l*0.5, 3),
                (t_w+14, t_l/2, 1)
                    ]

    if not test:
        lst += [(t_w*0.88, -49, 0),
                    (t_w*0.69, t_l+123, 2),
                    (t_w*0.59, t_l+123, 2),
                    
                    
                        ]

        if False:
            lst += [(t_w*0.80, -49, 0),
                    (t_w*0.85, t_l+123, 2),
                    (-160, t_l*0.2, 3),

                        ]
        lst += [(-160, t_l*0.92, 3),
                (-160, t_l*0.57, 3),
                (-160, t_l*0.41, 3),
                (t_w+14, t_l*0.92, 1),
                (t_w+14, t_l*0.59, 1),
                (t_w+14, t_l*0.72, 1),
                    ]
        lst += [(t_w*0.32, -49, 0),
                (t_w*0.09, -49, 0),
                (t_w*0.50, -49, 0),
                (t_w*0.60, -49, 0),
                (t_w*0.42, t_l+123, 2),
                    ]
    for x, y, rot in lst:
        if rot in [0.5,1.5,2.5,3.5]:
            wd2 = wd
        else:
            wd2 = 1.0*wd
        h = clip(_scl, wd2, dp, ht, rot+2, offs=offs, doffs=doffs, flat=flat)

        t = translate(v=[x*_scl, y*_scl, (z-62)*_scl])
        t.add(h)
        dh.append(t)

    r = union()
    for h in dh:
        r += h

    return r

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
    d=18
    u = union()
    u.add(cube(size=[(w+offs*2.0)*scl,(dp+offs*2.0)*scl,(ht+offs*2.0)*_scl]))
    c = cube(size=[(w+offs*2.0)*scl,(d+offs*2.0)*scl,(d+offs*2.0)*_scl])
    c = rotate(a=-42.0, v=[1*_scl,0,0]).add(c)
    c = translate(v=[0, -d*0.5*_scl,d*0.8*_scl]).add(c)
    u.add(c)
    c = cube(size=[(w+offs*2.0)*scl,(d+offs*2.0)*scl,(d*0.7+offs)*_scl])
    c = translate(v=[0, -d*0.5*_scl,d*0.8*_scl]).add(c)
    u.add(c)
    if flat:
        c = cube(size=[(w+offs*2.0)*scl,(d+offs*2.0)*scl,(ht+offs*2.0)*_scl])
        c = translate(v=[0, -d*0.5*_scl,1.5*d*_scl]).add(c)
    else:
        c = cube(size=[(w+offs*2.0)*scl,(d+offs*2.0)*scl,(d+offs*2.0)*_scl])
        c = rotate(a=-62.0, v=[1*_scl,0,0]).add(c)
        c = translate(v=[0, -d*0.5*_scl,1.5*d*_scl]).add(c)
    u.add(c)

    # cut the back off the rotated rectangles
    v = union()
    b = cube(size=[(w*1.6+offs*4)*_scl,(0+dp+d+offs*2.0)*_scl,(ht*3+offs*2.0)*_scl])
    v.add(translate(v=[-w*0.5*_scl, (dp+0+offs*2.0)*scl, -ht*_scl*0.5]).add(b))
    u -= v

    t = union()
    t.add(translate(v=[-(offs+w/2.0)*_scl,
                       -(offs+dp/2.0-doffs)*_scl,
                       -offs*_scl]).add(u))

    v = union()
    v.add(rotate(a=rot*90, v=[0,0,1]).add(t))

    return v

def create_tablet(t, _scl, mirror, colour, part):

    if part == 1:
        return
    scl = [-_scl*mirror, _scl, _scl]

    c = color(colour)
    c.add(t)

    b = union()
    laminates = False

    p2_inset = 20

    if laminates:
        tb_inset = 50
        innerwall = 13
    else:
        if part == 0:
            tb_inset = 6
            innerwall = 5
            p0_innerwall = 13
            swid = -35
        elif part == 1:
            tb_inset = 0
            innerwall = -12
        else:
            tb_inset = p2_inset
            innerwall = -12
            p2_innerwall = innerwall+4

    if part == 0:
        layers = 0x3f-7
    elif part == 1:
        layers = 4+8
    elif part == 2:
        layers = 0x7f

    if layers & 0x1:
        if laminates:
            top_ht=15.0
        else:
            top_ht=10.0
        # touchpanel capture layer
        ts=touch_surround(_scl, top_ht, 50, tb_inset, holes=laminates)
        td = translate(v=[0,0,(top_ht)*_scl])
        td.add(ts)
        b.add(td)

    if layers & 0x2:

        top_ht = 15
        # layer around touchscreen
        ts=touch_surround(_scl, top_ht, -0.0, tb_inset, holes=laminates)
        td = translate(v=[0,0,(top_ht-15)*_scl])
        td.add(ts)
        b.add(td)

    if layers & 0x4:
        # layer on top of touchscreen
        if part == 2 or laminates:
            ht = 15
        else:
            ht = 10
        if part == 2 and not laminates:
            taped = False
            iw = p2_innerwall
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
            td -= camera(_scl) # remove camera
            if part != 1 and not laminates:
                td -= headphone(_scl) # remove headphone
                if not test:
                    if part != 2 or laminates:
                        td -= cardslot(_scl) # remove cpu card
            if not test:
                if part == 0 and not laminates:
                    td -= sdcard(_scl) # remove sd card
        b.add(td)

    if layers & 0x8:
        if part == 1 and not laminates:
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
            u.add(cardslot(_scl, 2))
            b.add(u)
        else:
            l = 1
            ht = 15
            ht_step = 0
            z = -30
            if part == 0 and not laminates:
                z = -40.0-2
                l = 5
                ht = 3.0
                ht_step = 3.0
                _p0_innerwall = innerwall+3
            for i in range(l):
                # layer on top of touchscreen
                if part == 2 and not laminates:
                    iw = p2_innerwall
                elif part == 0 and not laminates:
                    iw = _p0_innerwall
                    _p0_innerwall = min(p0_innerwall, _p0_innerwall+3)
                else:
                    iw = innerwall
                ts = touch_surround(_scl, ht, iw, tb_inset,
                                    holes=laminates)
                td = translate(v=[0,0,z*_scl])
                z += ht_step
                td.add(ts)
                if part != 2 and not laminates:
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

        if not test and part == 0 and not laminates:
            ts = touch_surround(_scl, 15, p0_innerwall+5, tb_inset,
                                    holes=laminates)
            td = translate(v=[0,0,-30*_scl])
            td.add(ts)
            u = intersection()
            u.add(td)
            u.add(cardslot(_scl, swid))
            u -= cardslot(_scl, 0)
            b.add(u)

            u = intersection()
            u.add(td)
            u.add(sdcard(_scl, swid))
            u -= sdcard(_scl, 0)
            b.add(u)

            u = intersection()
            u.add(td)
            u.add(power(_scl, swid))
            u -= power(_scl, 0)
            u -= headphone(_scl, 0)
            u -= pcb(_scl) # remove pcb
            b.add(u)

            u = intersection()
            u.add(td)
            u.add(headphone(_scl, swid))
            u -= pcb(_scl) # remove pcb
            u -= power(_scl, 0)
            u -= headphone(_scl, 0)
            b.add(u)


    if layers & 0x10:
        if part == 2 and not laminates:
            iw = p2_innerwall
        else:
            iw = innerwall
        # layer around cpu card
        ts = touch_surround(_scl, 40, iw, tb_inset,
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

        if not test and part == 0 and not laminates:
            ts = touch_surround(_scl, 40, p0_innerwall+5, tb_inset,
                                    holes=laminates)
            td = translate(v=[0,0,-45*_scl])
            td.add(ts)
            u = intersection()
            u.add(td)
            u.add(cardslot(_scl, swid))
            u -= cardslot(_scl, 0)
            b.add(u)

            u = intersection()
            u.add(td)
            u.add(sdcard(_scl, swid))
            u -= sdcard(_scl, 0)
            b.add(u)

            u = intersection()
            u.add(td)
            u.add(power(_scl, swid))
            u -= power(_scl, 0)
            u -= headphone(_scl, 0)
            u -= pcb(_scl) # remove pcb
            b.add(u)

            u = intersection()
            u.add(td)
            u.add(headphone(_scl, swid))
            u -= pcb(_scl) # remove pcb
            u -= power(_scl, 0)
            u -= headphone(_scl, 0)
            b.add(u)

    if layers & 0x20:
        if part == 2 and not laminates:
            iw = p2_innerwall
        else:
            iw = innerwall
        # layer above cpu card and microsd
        ts = touch_surround(_scl, 30, iw, tb_inset,
                                holes=laminates)
        td = translate(v=[0,0,-85*_scl])
        td.add(ts)
        td -= camera(_scl) # remove headphone
        td -= usb(_scl) # remove usb slot
        td -= power(_scl) # remove power jack
        td -= headphone(_scl) # remove headphone
        td -= cardslot(_scl, 0) # remove cpu card
        if not test and part == 2 and not laminates:
            td -= sdcard(_scl) # remove microsd
        b.add(td)

        if not test and part == 0 and not laminates:
            ts = touch_surround(_scl, 30, iw, p2_inset,
                                    holes=laminates)
            td = translate(v=[0,0,-85*_scl])
            td.add(ts)
            u = intersection()
            u.add(td)
            u.add(sdcard(_scl, 4))
            b.add(u)

            ts = touch_surround(_scl, 40, p0_innerwall+5, tb_inset,
                                    holes=laminates)
            td = translate(v=[0,0,-85*_scl])
            td.add(ts)
            u = intersection()
            u.add(td)
            u.add(cardslot(_scl, swid))
            u -= cardslot(_scl, 0)
            b.add(u)

            u = intersection()
            u.add(td)
            u.add(sdcard(_scl, swid))
            u -= sdcard(_scl, 0)
            b.add(u)

            u = intersection()
            u.add(td)
            u.add(power(_scl, swid))
            u -= power(_scl, 0)
            u -= headphone(_scl, 0)
            b.add(u)

            u = intersection()
            u.add(td)
            u.add(headphone(_scl, swid))
            u -= power(_scl, 0)
            u -= headphone(_scl, 0)
            b.add(u)

    if layers & 0x40:
        if part == 2 and not laminates:
            iw = p2_innerwall
        else:
            iw = 40

        top_ht = 10.0
        # top case
        ts = touch_surround(_scl, top_ht, iw, tb_inset,
                                holes=laminates)
        if part == 0:
            ts += close_top(_scl, top_ht) # complete top
        td = translate(v=[0,0,-115*_scl])
        td.add(ts)
        if part == 2 and not laminates:
            td -= cardslot(_scl, 0) # remove cpu card
        if not test and part == 2 and not laminates:
            td -= power(_scl) # remove power
            td -= headphone(_scl) # remove headphone
            td -= sdcard(_scl) # remove microsd

        b.add(td)

        if not test and part == 0 and not laminates:
            ts = touch_surround(_scl, top_ht, iw, p2_inset,
                                    holes=laminates)
            td = translate(v=[0,0,-115*_scl])
            td.add(ts)
            u = intersection()
            u.add(td)
            u.add(sdcard(_scl, 4))
            b.add(u)

            u = intersection()
            u.add(td)
            u.add(cardslot(_scl, 4))
            b.add(u)

            u = intersection()
            u.add(td)
            u.add(power(_scl, 4))
            b.add(u)

            u = intersection()
            u.add(td)
            u.add(headphone(_scl, 4))
            b.add(u)

    if part == 2 and not laminates:
        #b.add(clips(_scl, 25, ht=61, z=-17, dp=9.0, doffs=5))
        b.add(clips(_scl, 25, ht=61, z=28, dp=9.0, doffs=5))
        b.add(capture(_scl, ioff=0))

    if part == 0 and not laminates:
        c = union()
        c += clips(_scl, 40, dp=0, offs=4, z=28, ht=8.5, doffs=-17, flat=True)
        #c += clips(_scl, 40, dp=0, offs=4, z=-17, ht=38, doffs=-17, flat=True)

        u = union()
        u.add(b)
        u += c
        u -= capture(_scl, oof=6, ioff=-4)
        b = u

    if part != 2 and not laminates:
        #c = clips(_scl, 25, dp=1, offs=2, z=-16, ht=20, doffs=-1, flat=part==1)
        #b -= c
        c = clips(_scl, 25, dp=1, offs=2, z=30, ht=30, doffs=-1, flat=part==1)
        b -= c


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
    t = translate(v=[-155.5*scl,-61*scl,0]).add(t)
    t = color(c).add(t)

    #projection(cut=False).add(t)

    scad_render_to_file(t, "tablet_prog.scad")
    f = open("tablet_model.scad", "w")
    f.write("""include<tablet_prog.scad>;
%import_stl(filename = "tablet10.stl");
    """)
    f.close()

