# Vertex guided duplication:
# Author: Tamir Lousky. March 2014.

import bpy, bmesh
from   math import degrees

class mesh_guided_duplication_panel( bpy.types.Panel ):
    bl_idname      = "MeshGuidedDuplication"
    bl_label       = "Mesh Guided Duplication"
    bl_space_type  = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context     = 'edit'

    @classmethod
    def poll( self, context ):
        return True

    def draw( self, context):
        layout = self.layout
        col    = layout.column()

        col.operator( 
            'object.mesh_guided_duplication',
            text = 'Duplicate to selected elements',
            icon = 'COPYDOWN'
        )

class mesh_guided_duplication( bpy.types.Operator ):
    """ Duplicate an object or a group instance to all the selected elements on
        the active mesh 
    """

    bl_idname  = "object.mesh_guided_duplication"
    bl_label   = "Mesh Guided Duplication"
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}

    source_object = bpy.props.StringProperty(
        description = "Object to duplicate",
        name        = "Duplicate Object",
    )

    source_group = bpy.props.StringProperty(
        description = "Group to duplicate",
        name        = "Duplicate Group",
    )

    rotate_duplicates = bpy.props.BoolProperty(
        description = "Rotate duplicates to match element normals",
        name        = "Rotate to match normals",
        default     = False
    )

    types = [
        ('DUPLICATE', 'Duplicate', ''), 
        ('INSTANCE',  'Instance',  ''), 
        ('GROUP',     'Group',     '')
    ]

    duplicate_type = bpy.props.EnumProperty(
        name    = "Duplication Type",
        items   = types, 
        default = 'INSTANCE'
    )

    @classmethod
    def poll( self, context ):
        ''' Only works with selected MESH type objects in Edit mode '''
        any_selected_obj = context.object
        is_mesh = obj_in_editmode = obj_is_selected = False

        if context.object:
            is_mesh         = context.object.type == 'MESH'
            obj_in_editmode = context.object.mode == 'EDIT'
            obj_is_selected = context.object.select

        return (
            any_selected_obj and is_mesh and obj_is_selected and obj_in_editmode
        )

    def get_element_coordinates( self, context ):
        ''' Creates a list of coordinates from the selected mesh elements.
            Returns the global coordinates and the normal, converted to rotation
            angles in radians, of all elements.
        '''
        o  = context.object
        bm = bmesh.from_edit_mesh( o.data )

        coordinates = []

        if 'FACE' in bm.select_mode:
            for f in [ f for f in bm.faces if f.select ]:
                coordinates.append( {
                    'co' : f.calc_center_median() * o.matrix_world,
                    'no' : [ math.degrees( a ) for a in f.normal ]
                } )
            
        if 'EDGE' in bm.select_mode:
            for e in [ e for e in bm.edges if e.select ]: 
                # Calculate the average coordinate and normal from vert pair
                avg_co = ( e.verts[0].co     + e.verts[1].co     ) / 2
                avg_no = ( e.verts[0].normal + e.verts[1].normal ) / 2

                coordinates.append( {
                    'co' : avg_co * o.matrix_world,
                    'no' : [ math.degrees( a ) for a in avg_no ]
                } )

        if 'VERT' in bm.select_mode:
            for v in [ v for v in bm.verts if v.select ]: 
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
        ''' Create duplicate objects or groups on all provided coordinates 
            and rotate the objects to match provided rotation matrix if 
            'rotate_duplicates' option is selected.
        '''
        
        for c in coordinates:
            if self.duplicate_type = 'GROUP':
                context.scene.cursorlocation = c['co'] # Cursor to coordinate
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
                o.location = c['co']    # Set location to requested
                
            # Rotate object according to vertex normal
            if self.rotate_duplicates:
                for i, a in enumerate( c['no'] ):
                    bpy.ops.transform.rotate( 
                        value = math.radians( a ), 
                        axis  = ( i == 0, i == 1, i == 2 )
                    )

    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
          
        box.prop( self, 'duplicate_type' )

        if self.duplicate_type == 'GROUP':
            box.prop_search( 
                self,     'source_group',
                bpy.data, 'groups'
            )
        else:
            box.prop_search(
                self,          'source_object',
                context.scene, 'objects'
            )

        box.prop( self, 'rotate_duplicates' )
        
    def execute(self, context):

        self.create_duplicates( 
            context, 
            self.get_element_coordinates( context ) 
        )

        return {'FINISHED'}

def register():
    bpy.utils.register_module(__name__)
    
def unregister():
    bpy.utils.unregister_module(__name__)
