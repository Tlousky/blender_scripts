import bpy, bmesh

bm = bmesh.new()
bm.from_mesh( bpy.context.object.data )

ref_obj_name     = bpy.context.object.name
reference_volume = float( bm.calc_volume() )
ref_vol_scale    = ( '%.0E' % reference_volume )[-3:]

# Select all the objects in the scene that have a similar volume (of the same scale)
for o in [ m for m in bpy.context.scene.objects if m.type == 'MESH' ]:
    if o.name == ref_obj_name: continue

    bm = bmesh.new()
    bm.from_mesh( o.data )
    
    vol       = float( bm.calc_volume() )
    vol_scale = ( '%.0E' % vol )[-3:]
    
    if vol_scale == ref_vol_scale:
        o.select = True