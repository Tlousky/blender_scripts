import bpy

def weight_from_distance( scene ):
    floor = bpy.data.objects['Plane']  # <== REPLACE "PLANE" with the name of your grass field object
    cam   = bpy.data.objects['Camera']

    vert_distances = [ 
        ( cam.location - floor.matrix_world * v.co ).length for v in floor.data.vertices 
    ]

    maxDist = max( vert_distances )
    minDist = min( vert_distances )

    for i, d in enumerate( vert_distances ):
        # Normalize distance and set as vertex weight
        floor.data.vertices[i].groups[0].weight = ( d - minDist ) / ( maxDist - minDist )

    pSysName      = 'ParticleSystem' # <== REPLACE with the name of your grass' particle system if needed
    vertGroupName = 'Group'          # <== REPLACE with the name of your vertex group if needed
        
    floor.particle_systems[ pSysName ].vertex_group_density = vertGroupName # Update / Refresh

bpy.app.handlers.frame_change_pre.append( weight_from_distance )