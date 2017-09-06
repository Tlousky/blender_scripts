import bpy

C = bpy.context
S = C.scene
o = C.object
d = o.data

o.active_material = bpy.data.materials['textMat']

#d.extrude     = 0.033
d.bevel_depth = 0.0066

# Set bevel factor end to 0 and add keyframe
d.bevel_factor_end = 0
d.keyframe_insert( 'bevel_factor_end' )

# Move 3 frames in time
S.frame_set( S.frame_current + 3 )

# Set bevel factor end to 1 and add keyframe
d.bevel_factor_end = 1
d.keyframe_insert( 'bevel_factor_end' )

# Move 1 frame in time and set start bevel factor animation
S.frame_set( S.frame_current + 1 )
d.keyframe_insert( 'bevel_factor_start' )
S.frame_set( S.frame_current + 3 )
d.bevel_factor_start = 1
d.keyframe_insert( 'bevel_factor_start' )
