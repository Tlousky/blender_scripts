import bpy

C = bpy.context
S = C.scene
o = C.object
d = o.data

o.active_material = bpy.data.materials['textMat'].copy()
m = o.active_material

m.use_transparency = True

# Add keyframe on transp alpha
m.alpha = 0
m.keyframe_insert( 'alpha' )

S.frame_set( S.frame_current + 4 )
m.alpha = 1
m.keyframe_insert( 'alpha' )