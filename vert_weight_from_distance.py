import bpy

def weight_from_distance( scene ):
    floor = bpy.data.objects['Plane']  # <== REPLACE "PLANE" with the name of your grass field object
    cam   = bpy.data.objects['Camera']

    vert_distances = [ 
        ( cam.location - floor.matrix_world * v.co ).length for v in floor.data.vertices 
    ]

    normalize = lambda x, minX, maxX: ( x - minX ) / ( maxX - minX )

    maxDist   = max( vert_distances )
    minDist   = min( vert_distances )

    vert_distances_normalized = [ normalize( d, minDist, maxDist ) for d in vert_distances ]

    for v, w in zip( floor.data.vertices, vert_distances_normalized ):
        v.groups[0].weight = w

    pSysName      = 'ParticleSystem' # <== REPLACE with the name of your grass' particle system if needed
    vertGroupName = 'Group'          # <== REPLACE with the name of your vertex group if needed
        
    floor.particle_systems[ pSysName ].vertex_group_density = vertGroupName

bpy.app.handlers.frame_change_pre.append( weight_from_distance )