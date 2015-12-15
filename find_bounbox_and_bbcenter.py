import bpy, bmesh
from mathutils import Vector

def bb_center( o ):
    bb = [ o.matrix_world * Vector(p[:]) for p in o.bound_box ]

    vSum = Vector()
    for v in vList: vSum += v
        
    return vSum / len( vList )

o = bpy.context.object

bb = [ Vector(p[:]) + o.location for p in C.object.bound_box ]

bbCenter = vecSum( bb ) / len( bb )