''' Find UV islands and create a data structure
with the list of all UV indices in each island '''

import bpy
C = bpy.context
o = bpy.data.objects[ C.object.name ]

# Go to object mode to read UV data
bpy.ops.object.mode_set( mode = 'OBJECT' )

uvLayer = o.data.uv_layers.active
uvs     = [ uvLayer.data[i] for i in range( len( uvLayer.data ) ) ]

others = uvs.copy()

islands = []

def select_island( uv ):
    uv.select = True

    bpy.ops.object.mode_set( mode = 'EDIT' )
    bpy.ops.uv.select_linked()
    bpy.ops.object.mode_set( mode = 'OBJECT' )
    
    return [ i for i, uv in enumerate( uvs ) if uv.select ]

for i in range( len( uvs ) ):
    bpy.ops.object.mode_set( mode = 'EDIT' )
    bpy.ops.uv.select_all( action = 'DESELECT' )
    bpy.ops.object.mode_set( mode = 'OBJECT' )
    
    flat = [ idx for isle in islands for idx in isle ]
    if i in flat: continue
    
    island = select_island( uvs[i] )

    exists = len( set( flat ).intersection( set( island ) ) )
    if island and not exists: islands.append( island )
    
print( islands )
print( " number of islands: ", len( islands ) )