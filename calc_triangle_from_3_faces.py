import bpy, bmesh
from mathutils import Vector
from math import degrees, acos

bm = bmesh.from_edit_mesh( bpy.context.object.data )
centers = [ f.calc_center_median() * bpy.context.object.matrix_world for f in bm.faces if f.select ]

if len( centers ) == 3:
    # Face centers as triangle vertices
    A, B, C = centers
    
    # Triangle edges (sides)
    AB = B - A
    AC = C - A
    BC = C - B

    # Triangle angles
    a =       degrees( acos( ( AB.dot( AC ) ) / ( AB.length * AC.length ) ) )
    b = 180 - degrees( acos( ( AB.dot( BC ) ) / ( AB.length * BC.length ) ) )
    c =       degrees( acos( ( BC.dot( AC ) ) / ( BC.length * AC.length ) ) )
    
    # The smallest angle between the two triangle edge vectors equals
    # To the sum of the two smallest angles within the triangle
    angles = sorted( [ a, b, c ] )
    print( "AB: ", AB )
    print( "AC: ", AC )
    print( "BC: ", BC )
    print( angles )
    print( "All: ", sum( angles ) )
    print( "Smaller: ", sum( angles[:2] ) )
        
else:
    print( "Invalid number of selected faces" )