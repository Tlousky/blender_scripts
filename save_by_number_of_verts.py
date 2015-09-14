import bpy, bmesh

vertCount = 8 # <-- Faces with this amount of verts will be selected

bpy.ops.object.mode_set( mode = 'EDIT' )
bm = bmesh.from_edit_mesh( bpy.context.object.data )

bpy.ops.mesh.select_mode( type = 'FACE' )
bpy.ops.mesh.select_all( action = 'DESELECT' )

for f in bm.faces: 
    if len( f.verts ) == vertCount: 
        f.select = True

bm.select_flush(True)
