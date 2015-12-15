import bpy, bmesh
from mathutils import Vector

def vecSum( vList ):
    vSum = Vector()
    for v in vList:
        vSum += v
        
    return vSum

o = bpy.context.object

bb = [ Vector(p[:]) + o.location for p in C.object.bound_box ]

bbCenter = vecSum( bb ) / len( bb )