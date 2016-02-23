import bpy, bmesh

o  = bpy.context.object
bm = bmesh.from_edit_mesh( o.data )

active   = bm.select_history.active
selected = list( # Find non-active face using set boolean difference
    set( bm.select_history ).difference( 
        set( [ bm.select_history.active ] ) 
    ) 
)[0]

# Calculate the rotation difference between the selected and active faces' normals
rot = active.normal.rotation_difference( selected.normal ).to_matrix()

# The pivot is the common edge's center point
pivot = list( # Intersect both faces edge sets to find the common edge
    set( active.edges[:] ).intersection( 
        set( selected.edges ) 
    ) 
)[0]
pivot_coos = [ o.matrix_world * v.co for v in pivot.verts ]
pivot_vec  = ( pivot_coos[0] + pivot_coos[1] ) / 2 # Calculate edge center

bmesh.ops.rotate(
    bm,                      # BMESH object
    cent   = pivot_vec,      # Rotation pivot point (edge center)
    matrix = rot,            # Rotation value
    verts  = active.verts,   # What verts to rotate (active face's verts)
    space  = o.matrix_world  # Rotate in object world space
)