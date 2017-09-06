#import pandas as pd
import bpy, bmesh
from math import pi, radians, cos, sin, sqrt
from mathutils import Vector, geometry
from itertools import combinations

C = bpy.context
S = C.scene

def draw_initial_polygon( sides = 6, radius = 1.0, center = Vector((0,0,0)) ):
    """ Create initial polygon shape """

    points = []
    edges  = []
    step   = ( 2.0 / sides )
    i      = 0

    for i in range( sides ):
        t  = ( i * step )
        x1 = cos( t * pi ) * radius
        y1 = sin( t * pi ) * radius

        points.append( center + Vector(( x1, y1, 0 )) )

    for i in range( len(points) ):
        edge = []

        if i == len( points ) - 1:
            edge.append( i )
            edge.append( 0 )
        else:
            edge.append( i )
            edge.append( i + 1)

        edges.append( tuple( edge ) )

    return { 'verts' : points, 'edges' : edges }

def generate_polygon( sides = 6, radius = 1, name = 'poly', center = Vector((0,0,0)) ):
    bm = bmesh.new()
    geom = draw_initial_polygon( sides = sides, radius = radius, center = center )
    for v in geom['verts']:
        bm.verts.new( v )

    bm.verts.ensure_lookup_table()
    for e in geom['edges']:
        bm.edges.new([ bm.verts[i] for i in e ])
        
    m = bpy.data.meshes.new( name )
    bm.to_mesh( m )
    o = bpy.data.objects.new( name, m )

    S.objects.link( o )
    
    return o, bm

globCo = lambda co, o: o.matrix_world * co

def find_intersection( edges, o ):
    # Calculate global locations of edge verts
    p1, p2 = [ globCo( v.co, o ) for v in edges[0].verts ]
    p3, p4 = [ globCo( v.co, o ) for v in edges[1].verts ]

    return geometry.intersect_line_line(p1, p2, p3, p4)

hex, bm_hex = generate_polygon( sides = 5, radius = 1, name = 'hex' )

hex.select = True
S.objects.active = hex

for v in bm_hex.verts:
    circle, bm_circle = generate_polygon( sides = 5, radius = 1, name = 'circle', center = v.co )
    
# Join all and find intersections
bpy.ops.object.select_all( action = 'SELECT' )
bpy.ops.object.join()

bm = bmesh.new()
bm.from_mesh( C.object.data )

bmesh.ops.remove_doubles( bm, verts = bm.verts )
bm.verts.ensure_lookup_table()
bm.edges.ensure_lookup_table()

# Find intersections between edges and add verts
edgeCombinations = list( combinations( bm.edges, 2 ) )

edgeIntersections = {}
for edges in edgeCombinations:
    p1, p2 = [ globCo( v.co, C.object ) for v in edges[0].verts ]
    p3, p4 = [ globCo( v.co, C.object ) for v in edges[1].verts ]
    CO     = find_intersection( edges, C.object )
    
    for e in edges:    
        # Find the one intersection that's on the edge
        e1Len = ( p2 - p1 ).length
        e2Len = ( p4 - p3 ).length
        co = [ 
            co for co in CO 
            if  ( co - p1 ).length <= e1Len
            and ( co - p2 ).length <= e1Len
            and ( co - p3 ).length <= e2Len
            and ( co - p4 ).length <= e2Len
        ] if CO else None

        co = co[0] if co else None
        
        if co:
            if e in edgeIntersections:
                edgeIntersections[ e ].append( co )
            else:
                edgeIntersections[ e ] = [ co ]

newObjVerts = []
newObjEdges = []
for e in edgeIntersections:    
    # Create list of all verts
    allVerts = [ globCo( v.co, C.object ) for v in e.verts ] + edgeIntersections[ e ]

    # Sort verts by proximity to p1
    p1, p2 = [ globCo( v.co, C.object ) for v in e.verts ]
    allVerts.sort( key = lambda co: ( co - p1 ).length )

    newIndices = [ len( newObjVerts ) + i for i in range( 0, len(allVerts) ) ]
    newObjVerts.extend( allVerts )

    # Create new edges from vertices, numEdges = numVerts - 1
    newObjEdges.extend([ 
        [ newIndices[i], newIndices[i+1] ] for i in range( len( allVerts ) - 1 ) 
    ])

print( len( newObjVerts ) - len( bm.verts ) )

# Create new object mesh
newbm = bmesh.new()
for co in newObjVerts:
    newbm.verts.new( co )

newbm.verts.ensure_lookup_table()
for e in newObjEdges: 
    newbm.edges.new([ newbm.verts[i] for i in e ])

bmesh.ops.remove_doubles( newbm, verts = newbm.verts )
    
newbm.to_mesh( C.object.data )
bm.free()
newbm.free()