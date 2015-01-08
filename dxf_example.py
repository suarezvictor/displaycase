from pyopenscad import *


u = union()
u.add(dxf_linear_extrude(file="wing.dxf", height=6))

r = dxf_linear_extrude(file="star.dxf", height=8)
r = rotate([0,0,45]).add(r)
s = dxf_linear_extrude(file="star.dxf", height=8)
r = translate(v=[225,135,-1]).add(r)
s = translate(v=[225,135,-1]).add(s)
u -=s
s = translate(v=[-30,-30,0]).add(s)
u -=s
r = translate(v=[35,-75,0]).add(r)
#u +=r
s = translate(v=[-35,-15,0]).add(s)
u -=s
s = translate(v=[14,-38,0]).add(s)
u -=s
s = translate(v=[15,-40,0]).add(s)
u -=s
s = translate(v=[-25,-30,0]).add(s)
u -=s
s = translate(v=[36,-18,0]).add(s)
u -=s
s = translate(v=[22,32,0]).add(s)
u -=s
s = translate(v=[-10,46,0]).add(s)
u -=s
s = translate(v=[12,35,0]).add(s)
u -=s
c = cube([8,20,6])
c = translate(v=[296,100,0]).add(c)
u += c
c = cube([8,20,6])
c = translate(v=[296,15,0]).add(c)
u += c
c = cube([8,20,6])
c = translate(v=[298,150,0]).add(c)
u += c
c = cube([8,20,6])
c = translate(v=[193,-4,0]).add(c)
u += c
c = cube([8,20,6])
c = translate(v=[208,-14,0]).add(c)
u += c
c = cube([8,20,6])
c = translate(v=[256,150,0]).add(c)
u += c
c = cube([8,20,6])
c = translate(v=[188,117,0]).add(c)
u += c

scad_render_to_file(u, "shape_prog.scad")
f = open("shape_model.scad", "w")
f.write("""include<shape_prog.scad>;
""")
f.close()


