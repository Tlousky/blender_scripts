import bpy

S = bpy.context.scene
O = bpy.data.objects
o = bpy.context.object

def isKeyframe( f ):
    for fc in o.animation_data.action.fcurves:
        kfs  = [ kf.co[0]     for kf in fc.keyframe_points ]
        if f in kfs:
            amp = fc.evaluate( f )
            idx = fc.array_index
            print( 
                "kf at %s for %s[%s(%s)] val: %s" % ( f, o.name, fc.data_path, idx, amp ) 
            )

for i in range( S.frame_start, S.frame_end ):
    isKeyframe( i )