import bpy
from math import sin

def linspace( start, end, n ):
    step = ( end - start ) / n
    return [ start + i * step for i in range(n) ]

# Generate a new mesh
m = bpy.data.meshes.new( 'sin' )

n = 100               # Number of vertices
m.vertices.add( n )   # Add n vertices
m.edges.add( n - 1 )  # Add n-1 edges

# Generate 100 y values ranging from 0 to 10
yVals = linspace( 0, 10, 100 )

# Iterate over y values and generate 3D vertex coordinates
for i, y in zip( range(n), yVals ):       
    m.vertices[i].co = ( 0, y, sin( y ) ) # Set (x,y,z) vertex coordinate
    
    if i < n - 1:
        # Set edge vertices => this vertex and the next
        m.edges[i].vertices = ( i, i+1 )

# Generate an object to contain an instance of this mesh 'm'
o = bpy.data.objects.new( 'sin', m )

# Link this virtual object to an acutal scene (the active or 'context' scene)
bpy.context.scene.objects.link( o )
    
