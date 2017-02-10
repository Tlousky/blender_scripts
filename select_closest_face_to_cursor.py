import bpy

cur = bpy.context.scene.cursor_location
o   = bpy.context.object

bpy.ops.object.mode_set( mode = 'OBJECT' )
faceIdx = o.closest_point_on_mesh( cur )[-1]

if faceIdx != -1:
    o.data.polygons[ faceIdx ].select = True
    
bpy.ops.object.mode_set( mode = 'EDIT' )