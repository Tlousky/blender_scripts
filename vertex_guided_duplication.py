# Vertex guided duplication:
# Author: Tamir Lousky. March 2014.

import bpy, bmesh
from   math import degrees

class vertex_guided_duplication( bpy.types.Operator ):
    """Duplicate an object or a group instance to all selected vertices on
       active mesh 
    """

    bl_idname  = "object.vertex_guided_duplication"
    bl_label   = "Vertex Guided Duplication"
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}

    source_object = bpy.props.StringProperty(
        description = "",
        name        = "",
    )
    group_name    = bpy.props.StringProperty(
        description = "",
        name        = "",
    )

    create_folders = bpy.props.BoolProperty(
        description = "",
        name        = "",
        default     = True
    )

    items = [
        ('DUPLICATE', 'Duplicate', ''), 
        ('INSTANCE',  'Instance',  ''), 
        ('GROUP',     'Group',     '')
    ]

    duplicate_type = bpy.props.EnumProperty( # Material distribution method
        name    = "Duplication Type",
        items   = items, 
        default = 'INSTANCE'
    )

    def get_vert_coordinates( self, context ):
        o  = context.object
        bm = bmesh.from_edit_mesh( o.data )

        coordinates = []
        for v in bm.verts: 
            coordinates.append( {
                'co' : v.co * o.matrix_world,
                'no' : [ math.degrees( a ) for a in v.normal ]
            } )

        # To calculate the angles I need to rotate the object to match the normal
        # I can create a vector that starts from the vertex co, and subtract it from
        # A vector representing a point 1 blender units up on Z axis.
        # I can then c

        return coordinates

    def create_duplicates( self, context, coordinates ):
        
        for v in coordinates:
            if self.duplicate_type = 'GROUP':
                bpy.ops.view3d.cursor3d( v['co'] ) # Cursor to coordinate
                bpy.ops.object.group_instance_add( group = self.group_name )
            else:
                # Reference and select object
                obj = context.scene.objects[ self.source_object ]

                bpy.ops.object.select_all( action = 'DESELECT' )
                obj.select = True
                context.scene.objects.active = obj

                # Create a duplicate (or instance)
                bpy.ops.object.duplicate( 
                    linked = self.duplicate_type == 'INSTANCE' 
                )

                o = context.object # Reference duplicated object
                o.location = v['co']    # Set location to requested
                
            # Rotate object according to vertex normal
            if self.rotate_along_normal:
                for i, a in enumerate( v['no'] ):
                    bpy.ops.transform.rotate( 
                        value = math.radians( a ), 
                        axis  = ( i == 0, i == 1, i == 2 )
                    )

    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        box.prop( self, 'radius'     )
        box.prop( self, 'sides'      )
        box.prop( self, 'iterations' )
        
    def execute(self, context):

        return {'FINISHED'}


""" In Panel:
        col.prop_search(
            obj, "LeavesObject", # Pick LeavesObject out of
            context.scene, "objects" # the list of objects in the scene
            )
"""
