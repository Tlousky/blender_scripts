import bpy
from math import sqrt

rowLen = 10
colLen = 10

diam  = 2              # = 2 * r
sDiam = diam / sqrt(3) # = small diameter

xDist = sDiam * 1.5
yDist = diam  * 0.75

for i in range( rowLen ):
    y = i * yDist
    for j in range( colLen ):
        x = j * xDist if i % 2 == 0 else (j + 0.5) * xDist 
        bpy.ops.mesh.primitive_circle_add(
            vertices  = 6,
            radius    = diam / 2,
            fill_type = 'NOTHING', 
            location  = (x, y, 0)
        )
        
        if i == 0 and j == 0:
            bpy.ops.object.mode_set( mode = 'EDIT' )
            

bpy.ops.mesh.select_all( action = 'SELECT' )
bpy.ops.mesh.remove_doubles()

bpy.ops.object.mode_set( mode = 'OBJECT' )

o = bpy.context.object
o.modifiers.new( 'Skin', 'SKIN' )

for v in o.data.skin_vertices[0].data:
    v.radius = 0.2, 0.2