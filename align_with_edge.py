'''
This script aligns a vertex with an edge, so that the vert will lie
either on the edge or the 3D line it represents (beyond the edge's boundaries)
See additional explanations and gif demo here:
http://blender.stackexchange.com/a/56259/15861

To use:
1. Go to edit mode
2. Select two vertices that represent the edge you want to align a vert with
3. Select the vert to be aligned with the edge.
4. Copy and paste this code to a new text file in the text editor
5. Press "Run Script"
'''

import bpy, bmesh
from mathutils import Vector, geometry

bm = bmesh.from_edit_mesh( bpy.context.object.data )
mw = bpy.context.object.matrix_world

# Make sure that only 3 are selected
if len( bm.select_history ) == 3:
    # Calculate global coordinates for the 3 verts
    v1, v2, v3 = [ mw * v.co for v in bm.select_history ]
    edgeVec = v2 - v1 # Calculate the edge's direction vector
    
    # 4th coord that with v3, defines an intersection line
    v4 = v3 + Vector((0,0,1000))
    
    # Find intersections between the edge and the intersection line
    intersections = geometry.intersect_line_line(v1, v2, v3, v4)
    
    # Move the vertex to the position of the 1st intersection
    bm.select_history[2].co = intersections[0]