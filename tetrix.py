import bpy, bmesh
import numpy as np
from time import time
from mathutils import Vector

def generate_quad( original, quads, level, max_level ):
    ''' Recursive function generating 4 tetrahedra off of the the input tetrahedron '''
    
    # The 1st new tetrahedron is simply half the scale of the original starting from the original tet's bottom left corner
    origin = original.min(axis=0) / 2    
    half  = original / 2
    half += origin

    # Calculate the dimensions of the new tetrahedra
    newdims = Vector( half.max(axis=0) - half.min(axis=0) )
    
    # The 2nd moves by the new tet's x dimension to the right
    right = half.copy()
    right[:,0] += newdims.x
    
    # The 3rd moves by half the x dim and all the y dim
    forward = half.copy()
    forward[:,0] += newdims.x / 2
    forward[:,1] += newdims.y
    
    # The 4th moves by half the x, a third of the y and all the z
    up = half.copy()
    up[:,0] += newdims.x / 2
    up[:,1] += newdims.y / 3
    up[:,2] += newdims.z
    
    quad = [ half, right, forward, up ]
    quads[ level ].extend( quad )
    
    if level < max_level:
        for q in quad:
            quads = generate_quad( q, quads, level + 1, max_level )

    return quads

## Main Code
start = time()

C = bpy.context
D = bpy.data
S = C.scene

n     = 4  # Number of steps of the fractal
scale = 10 # Scale of the original tetrahedron

# Generate regular tetrahedron at the desired scale
orig = np.array([
    [0,   0, 0],
    [1,   0, 0],
    [0.5, 3**0.5/2, 0],
    [0.5, 1/3*3**0.5/2, ((3**0.5/2)**2 - (1/3*3**0.5/2)**2)**0.5]
]) * scale

regular_tet_faces = np.array([[3, 0, 1], [1, 0, 2], [0, 3, 2], [3, 1, 2]])

# Initialize data structure for all tetrahedra in all steps
quads = { i : [] for i in range( n+1 ) }

# Generate tetrix via recursive function
quads = generate_quad( orig, quads, 0, n )

# Generate mesh data and initialize vertex and face arrays
m     = D.meshes.new('tetrix')
verts = []
faces = regular_tet_faces.tolist()

# Generate mesh data
for q in quads[n]:
    # Find last vert index and add new verts
    last_vert_index = max([ len( verts ) - 1, 0 ])
    verts.extend( q.tolist() )
    
    # Use base face arrangement of original regular tetrahedron and offset indices
    faces_indices = regular_tet_faces + last_vert_index + 1
    faces.extend( faces_indices.tolist() )

# Generate mesh object and add to scene
m.from_pydata( verts, [], faces )
print({ k : len( quads[k] ) for k in quads })
o = D.objects.new('base',m)
S.collection.objects.link( o )

elapsed = time() - start
print( f'Took {elapsed} seconds for {n} levels' )
