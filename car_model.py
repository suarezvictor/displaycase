from pyopenscad import *
from polysurface import spline_double_divide, Offset, SurfaceFromCurves

spline_me = True


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

def cardslot(scl, wofs=0):
    r = union()
    r.add(cube(size=[(670-wofs)*scl,80*scl,90*scl]))
    t = translate(v=[-(60-wofs)*scl, 1110*scl, (-83)*scl])
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
    r.add(cube(size=[85*scl,355*scl,100.2*scl]))
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
    t = translate(v=[-(143+bwid)*scl, -23*scl, (32.5-ht)*scl])
    t.add(r)
    a.add(t)

    r = union()
    r.add(cube(size=[(w+160)*scl,(bwid+iro)*scl,ht*scl]))
    t = translate(v=[-145*scl, (l+112-iro)*scl, (32.5-ht)*scl])
    t.add(r)
    a.add(t)

    r = union()
    r.add(cube(size=[(bwid+iro)*scl,(l+100)*scl,ht*scl]))
    t = translate(v=[(w-iro)*scl, -23*scl, (32.5-ht)*scl])
    t.add(r)
    a.add(t)

    r = union()
    r.add(cube(size=[(w+160)*scl,35*scl,ht*scl]))
    t = translate(v=[-145*scl, -(bwid+40)*scl, (32.5-ht)*scl])
    t.add(r)
    a.add(t)

    return a

def touch_surround(scl, ht=15, iro=0, bwid=50, taped=False, holes=False):
    a = union()

    #l=200
    #w=200
    l=1018
    w=1746

    r = union()
    r.add(cube(size=[(bwid+iro)*scl,l*scl,ht*scl]))
    t = translate(v=[-(143+bwid)*scl, 37*scl, (32.5-ht)*scl])
    t.add(r)
    a.add(t)

    r = union()
    r.add(cube(size=[w*scl,(bwid+iro)*scl,ht*scl]))
    t = translate(v=[-65*scl, (l+114-iro)*scl, (32.5-ht)*scl])
    t.add(r)
    a.add(t)

    r = union()
    r.add(cube(size=[(bwid+iro)*scl,l*scl,ht*scl]))
    t = translate(v=[(w+13-iro)*scl, 37*scl, (32.5-ht)*scl])
    t.add(r)
    a.add(t)

    r = union()
    r.add(cube(size=[w*scl,(bwid+iro)*scl,ht*scl]))
    t = translate(v=[-65*scl, -(bwid+40)*scl, (32.5-ht)*scl])
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

def wheel_back_left(scl, mirror):
    r = rotate([90, 0, 90])
    r.add(cylinder(h=25*scl, r=60*scl, center=True))
    t = translate(v=[-120*scl*mirror, -185*scl, -97*scl])
    t.add(r)
    return t

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

def create_tablet(t, _scl, mirror, colour):

    scl = [-_scl*mirror, _scl, _scl]

    c = color(colour)
    c.add(t)
    
    b = union()
    c = color([0.2, 0.2, 0.2, 1.0])
    c.add(b)
    t.add(c)

    laminates = False

    if laminates:
        tb_inset = 50 
        innerwall = 13
    else:
        tb_inset = 30 
        innerwall = 0

    test = False
    top_part = False

    if top_part:
        layers = 0x3f-3
    else:
        layers = 0xf

    top_ht=15.0
    if layers & 0x1:
        # touchpanel capture layer
        ts=touch_surround(_scl, top_ht, 20, tb_inset, holes=laminates)
        td = translate(v=[0,0,(top_ht)*_scl])
        td.add(ts)
        b.add(td)

    if layers & 0x2:
        # layer around touchscreen
        ts=touch_surround(_scl, top_ht, -0.0, tb_inset, holes=laminates)
        td = translate(v=[0,0,(top_ht-15)*_scl])
        td.add(ts)
        if not test:
            if not top_part and not laminates:
                u = intersection()
                u.add(touch_surround(_scl, top_ht, -0.0, tb_inset))
                u.add(sdcard(_scl)) 
                ts.add(u)
        b.add(td)

    if layers & 0x4:
        # layer on top of touchscreen
        if not top_part and not laminates:
            ts = touch_surround(_scl, 15, innerwall, tb_inset)
            td = translate(v=[0,0,-15*_scl])
            td.add(ts)
            u = intersection()
            u.add(td)
            u.add(sdcard(_scl)) 
            b.add(u)
        else:
            ts = touch_surround(_scl, 15, 35, tb_inset, taped=True, holes=laminates)
            td = translate(v=[0,0,-15*_scl])
            td.add(ts)
            if not test:
                td -= panelcable(_scl) # remove panelcable
                td -= camera(_scl) # remove headphone
                td -= cardslot(scl) # remove cpu card
                if top_part and not laminates:
                    td -= sdcard(_scl) # remove cpu card
            b.add(td)

    if layers & 0x8:
        if not top_part and not laminates:
            ts = touch_surround(_scl, 15, innerwall, tb_inset)
            td = translate(v=[0,0,-30*_scl])
            td.add(ts)
            u = intersection()
            u.add(td)
            u.add(sdcard(_scl)) 
            b.add(u)
        else:
            # layer on top of touchscreen
            ts = touch_surround(_scl, 15, innerwall, tb_inset,
                                holes=laminates)
            td = translate(v=[0,0,-30*_scl])
            td.add(ts)
            if not test:
                td -= panelcable(_scl) # remove panelcable
                td -= pcb(_scl) # remove pcb
                td -= camera(_scl) # remove headphone
                td -= headphone(_scl) # remove headphone
                td -= cardslot(scl) # remove cpu card
                if top_part and not laminates:
                    td -= sdcard(_scl) # remove cpu card
            b.add(td)

    if layers & 0x10:
        # layer around cpu card
        ts = touch_surround(_scl, 40, innerwall, tb_inset,
                                holes=laminates)
        td = translate(v=[0,0,-45*_scl])
        td.add(ts)
        if not test:
            td -= panelcable(_scl) # remove panelcable
            td -= pcb(_scl) # remove pcb
            td -= camera(_scl) # remove camera
            td -= power(_scl) # remove power jack
            td -= headphone(_scl) # remove headphone
            td -= sdcard(_scl) # remove microsd
            td -= cardslot(_scl) # remove cpu card
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
        top_ht = 15.0
        # top case
        ts = touch_surround(_scl, top_ht, 20, tb_inset,
                                holes=laminates)
        ts += close_top(_scl, top_ht) # complete top
        td = translate(v=[0,0,-115*_scl])
        td.add(ts)
        b.add(td)


if __name__ == '__main__':

    scl = 0.1
    t = union()
    c = [0.3, 0.5, 0.8, 1.0]
    create_tablet(t, scl, 1.0, c)
    t = translate(v=[-152.5*scl,-56*scl,0]).add(t)
    #t = translate(v=[112.5*scl,56*scl,0]).add(t)
    #t = rotate(a=90, v=[0,0,1]).add(t)
    t = color(c).add(t)

    #projection(cut=False).add(t)

    scad_render_to_file(t, "car_prog.scad")
    f = open("car_model.scad", "w")
    f.write("""include<car_prog.scad>;
%import_stl(filename = "tablet10.stl");
    """)
    f.close()

