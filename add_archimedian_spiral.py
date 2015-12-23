import bpy
from math import cos, sin
S = bpy.context.scene

def add_archimedian_spiral( size, length, name ):
    z = 0

    mesh = bpy.data.meshes.new( name = name )

    o = bpy.data.objects.new(name, mesh)
    o.location = (0,0,0) # place at object origin
    S.objects.link( o )

    verts = []  
    for i in range( length ):
        angle = 0.1 * i
        x     = ( 2 * size * angle ) * cos( angle )
        y     = ( 2 * size * angle ) * sin( angle )
        verts.append((x,y,z))

    edges = []
    for i in range( len( verts ) ):
        if i == len( verts ) - 1: break
        edges.append((i, i+1))
            

    mesh.from_pydata( verts, edges, [] )
    
add_archimedian_spiral( 0.1, 100, 'archispiral' )