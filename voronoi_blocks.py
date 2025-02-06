import bpy, bmesh
import numpy as np
from mathutils import Vector
from scipy.spatial import Voronoi

C = bpy.context
S = C.scene
O = S.objects

def voronoi_to_mesh( vor ):
    for i, r in enumerate(vor.regions):
        if (len(r) >= 3) and (-1 not in r):
            bm = bmesh.new()    
            verts = []            
            for i in r:
                vec3d = Vector( list( vor.vertices[i] ) + [0] )
                verts.append( bm.verts.new( vec3d ) )
        
            bm.verts.ensure_lookup_table()
            f = bm.faces.new(verts)
            #bmesh.ops.convex_hull( bm, input = verts )

            m = bpy.data.meshes.new( "Voronoi" )
            bm.to_mesh( m )
            
            o = bpy.data.objects.new( "Voronoi", m )
            C.collection.objects.link( o )
            
o = bpy.context.object
coos = -10 + np.random.random((200,2)) * 20
vor = Voronoi(coos)
voronoi_to_mesh( vor )

add_height    = True
add_wireframe = False

vorobjs = [ o for o in C.collection.objects if 'Vor' in o.name ]
for o in vorobjs:
    bm = bmesh.new()
    bm.from_mesh(o.data)
     
    bm.faces.ensure_lookup_table()
    f = bm.faces[0]
    if f.normal.z > 0:
        f.normal_flip()
         
    bm.to_mesh(o.data)
     
    if add_height:
        m = o.modifiers.new('Solidify', 'SOLIDIFY')
        m.thickness = np.random.random() * 10
     
    if add_wireframe:
        m = o.modifiers.new('Wireframe', 'WIREFRAME')
        m.thickness = 0.3
        m.offset    = -1