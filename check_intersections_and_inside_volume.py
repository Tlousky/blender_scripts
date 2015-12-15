import bpy, bmesh
from mathutils import Vector

def check_raycast(ray_origin, ray_destination, obj):
    mat = obj.matrix_local.inverted()
    f   = obj.ray_cast(mat * ray_origin, mat * ray_destination)
    loc, normal, face_idx = f

    if face_idx == -1:
        return False

    return True

c = bpy.data.objects['Cube']
o = bpy.data.objects['Suzanne']

bm = bmesh.new()
bm.from_mesh( c.data )

bm.edges.ensure_lookup_table()
bm.verts.ensure_lookup_table()

# Check if cube intersects with mesh
intersectsMesh = False
for e in bm.edges:
    coos = [ c.matrix_world * v.co for v in e.verts ]
    ray_origin, ray_destination = coos
    if check_raycast(ray_origin, ray_destination, o):
        intersectsMesh = True
        break

insideMesh = check_raycast( c.location, Vector( (0,0,1000) ),  o )
   
print( "Intersects: ", intersectsMesh )
print( "Inside Mesh: ", insideMesh )


