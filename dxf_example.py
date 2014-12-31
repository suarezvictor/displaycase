from pyopenscad import *


u = union()
u.add(dxf_linear_extrude(file="squashed_pear.dxf", height=6))

scad_render_to_file(u, "shape_prog.scad")
f = open("shape_model.scad", "w")
f.write("""include<shape_prog.scad>;
""")
f.close()


