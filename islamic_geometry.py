import bpy, bmesh
from math import radians, degrees
from mathutils import Vector, Euler

def find_intersection( edges ):
    p1, p2 = edges[0]
    p3, p4 = edges[1]

    v1 = p2 - p1 # Edge 1 line vector
    v2 = p4 - p3 # Edge 2 line vector

    # Calcualte intersection
    # Based on paramteric line equation: (x,y,z) = p0 + t * lineVec
    numer = v2.y * ( p3.x - p1.x ) + v2.x * ( p1.y - p3.y )
    denom = v1.x * v2.y - v1.y * v2.x
    t1    = numer / denom

    co = Vector( [ getattr( p1, i ) + t1 * getattr( v1, i ) for i in 'xyz' ] )

    return co

pt = Vector((0,1,0))
n  = 9
a  = Euler(( 0, 0, radians( 360 / n ) ))
bm = bmesh.new()

for i in range(n):
    v1 = bm.verts.new(( pt ))
    
    # This is the next point
    next = pt.copy()
    next.rotate(a)
    
    # The point after that
    nextAgain = next.copy()
    nextAgain.rotate(a)    

    # One before - rotated in opposite direction    
    prev = pt.copy()
    prev.rotate( Euler([ ai * -1 for ai in a ]) )
    
    edge1 = ( pt, nextAgain )
    edge2 = ( prev, next    )
    
    intersection = find_intersection([ edge1, edge2 ])
    
    # Create another vertex at the intersection point
    v2 = bm.verts.new(( intersection ))
    
    # Finally
    pt = next
    
bm.verts.ensure_lookup_table()
for i in range( len( bm.verts ) - 1 ):
    bm.edges.new([ bm.verts[i], bm.verts[i+1] ])

# Add last edge
bm.edges.new([ bm.verts[-1], bm.verts[0] ])
    
m = bpy.data.meshes.new('ismesh')
bm.to_mesh(m)

o = bpy.data.objects.new('ismesh',m)
bpy.context.scene.objects.link(o)

