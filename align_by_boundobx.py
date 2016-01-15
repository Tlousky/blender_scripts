import bpy, bmesh
from mathutils import Vector

C = bpy.context

bb = [ C.object.matrix_world * Vector(v[:]) for v in C.object.bound_box ]

# Bound box (BB) points to faces
points      = 'abcdefgh' # 8 points of BB represented as letters
faceLetters = ( 'abcd', 'adhe', 'hdcg', 'ehgf', 'fgcb', 'efba' )
faces       = [ [ points.index( p ) for p in face ] for face in faceLetters ]

# Generate BB object
bm = bmesh.new()

for bp in bb: bm.verts.new( bp ) # Add verts from BB points
bm.verts.ensure_lookup_table()

for face in faces:               # Add faces
    bm.faces.new( [ bm.verts[vIdx] for vIdx in face ] )
    
m = bpy.data.meshes.new( "BB" )
bm.to_mesh(m)

o = bpy.data.objects.new( "BB", m )

C.scene.objects.link( o )

# Calculate face centers
faceCenters = [ [ i, f.calc_center_median() ] for i, f in enumerate( bm.faces ) ]

# Find top face
faceCenters.sort( key = lambda fc: fc[1].z )

top = faceCenters[-1][0]
topNormal = bm.faces[ top ].normal

rot = topNormal.rotation_difference( Vector((0,0,1)) ).to_euler()

