# Vertex guided duplication:
# Author: Tamir Lousky. March 2014.

bl_info = {    
    "name"        : "Mesh Guided Duplication",
    "author"      : "Tamir Lousky",
    "version"     : (0, 0, 1),
    "blender"     : (2, 69, 0),
    "category"    : "Object",
    "warning"     : "",
    "location"    : "3D View >> Tools",
    "wiki_url"    : "",
    "tracker_url" : "https://github.com/Tlousky/blender_scripts/blob/master/mesh_guided_duplication.py",
    "description" : "Duplicate objects or groups to the locations of selected \
                     mesh elements on active object"
}

import bpy, bmesh, json
from   math      import degrees, radians
from   mathutils import Vector

class mesh_guided_duplication_panel( bpy.types.Panel ):
    bl_idname      = "MeshGuidedDuplication"
    bl_label       = "Mesh Guided Duplication"
    bl_space_type  = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    @classmethod
    def poll( self, context ):
        return True

    def draw( self, context):
        layout = self.layout
        col    = layout.column()

        props = context.scene.mesh_dupli_props

        col.operator( 
            'object.mesh_guided_duplication',
            text = 'Duplicate to selected elements',
            icon = 'COPYDOWN'
        )

        box = layout.box()
        box.prop( props, 'duplicate_type' )

        if props.duplicate_type == 'GROUP':
            box.prop_search( 
                props,    'source_group',
                bpy.data, 'groups'
            )
        else:
            box.prop_search(
                props,         'source_object',
                context.scene, 'objects'
            )

        box.prop( props, 'rotate_duplicates' )
        
        if props.rotate_duplicates: box.prop( props, 'rotation_axis' )

class MeshDumpliPropGroup( bpy.types.PropertyGroup ):
    ''' Class meant to enable transferring data between operator and panel '''
    types = [
        ('DUPLICATE', 'Duplicate', ''), 
        ('INSTANCE',  'Instance',  ''), 
        ('GROUP',     'Group',     '')
    ]

    source_object = bpy.props.StringProperty(
        description = "Object to duplicate",
        name        = "Duplicate Object"
    )

    source_group = bpy.props.StringProperty(
        description = "Group to duplicate",
        name        = "Duplicate Group"
    )

    rotate_duplicates = bpy.props.BoolProperty(
        description = "Rotate duplicates to match element normals",
        name        = "Rotate to match normals",
        default     = False
    )

    rotation_axis = bpy.props.BoolVectorProperty(
        description = "Axis to use for rotation along normals",
        name        = "Rotation Axis",
        subtype     = "XYZ",
        size        = 3,
        default     = (True, True, True)
    )
    
    duplicate_type = bpy.props.EnumProperty(
        name    = "Duplication Type",
        items   = types, 
        default = 'INSTANCE'
    )
    
class mesh_guided_duplication( bpy.types.Operator ):
    """ Duplicate an object or a group instance to all the selected elements on
        the active mesh 
    """

    bl_idname  = "object.mesh_guided_duplication"
    bl_label   = "Mesh Guided Duplication"
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}

    @classmethod
    def poll( self, context ):
        ''' Only works with selected MESH type objects in Edit mode '''
        any_selected_obj = context.object
        is_mesh = obj_in_editmode = obj_is_selected = False
        props = context.scene.mesh_dupli_props

        if context.object:
            is_mesh         = context.object.type == 'MESH'
            obj_in_editmode = context.object.mode == 'EDIT'
            obj_is_selected = context.object.select

            group = props.duplicate_type == 'GROUP' and props.source_group != ''
            obj   = props.duplicate_type != 'GROUP' and props.source_object!= ''
            
        return (
            any_selected_obj and \
            is_mesh          and \
            obj_is_selected  and \
            obj_in_editmode  and \
            ( group or obj )
        )

    def calc_angles_from_normal( self, co, normal ):
        ''' Use normal to calculate rotation angles '''
        rot = Vector( ( 0, 0, 1 ) ).rotation_difference( normal )
        eul = rot.to_euler()        

        return [ a for a in eul ]

    def get_element_coordinates( self, context ):
        ''' Creates a list of coordinates from the selected mesh elements.
            Returns the global coordinates and the normal, converted to rotation
            angles in radians, of all elements.
        '''
        o  = context.object
        wm = o.matrix_world                             # Global matrix
        rm = o.rotation_euler.to_matrix()               # Rotation matrix
        sm = o.scale.to_track_quat('X','Z').to_matrix() # Scale matrix
        
        bm = bmesh.from_edit_mesh( o.data )

        coordinates = []

        if 'FACE' in bm.select_mode:
            for f in [ f for f in bm.faces if f.select ]:
                co = f.calc_center_median()
                if co == co * wm * rm:
                    co = co + o.location
                else:
                    co = co * wm * rm
                coordinates.append( {
                    'co' : co,
                    'no' : self.calc_angles_from_normal( co, f.normal )
                } )
            
        if 'EDGE' in bm.select_mode:
            for e in [ e for e in bm.edges if e.select ]: 
                # Calculate the average coordinate and normal from vert pair
                avg_co = ( e.verts[0].co     + e.verts[1].co     ) / 2
                avg_no = ( e.verts[0].normal + e.verts[1].normal ) / 2

                if avg_co == avg_co * wm * rm:
                    avg_co = avg_co + o.location
                else:
                    avg_co = avg_co * wm * rm
                
                coordinates.append( {
                    'co' : avg_co,
                    'no' : self.calc_angles_from_normal( avg_co, avg_no )
                } )

        if 'VERT' in bm.select_mode:
            for v in [ v for v in bm.verts if v.select ]:
                co = v.co
                if co == co * wm * rm:
                    co = co + o.location
                else:
                    co = co * wm * rm
                coordinates.append( {
                    'co' : co,
                    'no' : self.calc_angles_from_normal( v.co, v.normal )
                } )

        return coordinates

    def create_duplicates( self, context, coordinates ):
        ''' Create duplicate objects or groups on all provided coordinates 
            and rotate the objects to match provided rotation matrix if 
            'rotate_duplicates' option is selected.
        '''

        bpy.ops.object.mode_set
        props = context.scene.mesh_dupli_props
        
        bpy.ops.object.mode_set(mode = 'OBJECT')

        for c in coordinates:
            if props.duplicate_type == 'GROUP':
                context.scene.cursor_location = c['co'] # Cursor to coordinate
                bpy.ops.object.group_instance_add( 
                    group = props.source_group
                )

                o = context.object      # Reference duplicated object
                o.location = c['co']    # Set location to requested                

            else:
                # Reference and select object
                obj = context.scene.objects[ props.source_object ]

                bpy.ops.object.select_all( action = 'DESELECT' )
                obj.select = True
                context.scene.objects.active = obj

                # Create a duplicate (or instance)
                bpy.ops.object.duplicate( 
                    linked = props.duplicate_type == 'INSTANCE' 
                )

                if props.duplicate_type != 'INSTANCE':
                    # Apply rotation and scale
                    bpy.ops.object.transform_apply( 
                        rotation = True, scale = True 
                    )
                
                o = context.object      # Reference duplicated object
                o.location = c['co']    # Set location to requested

            # Rotate object according to vertex normal
            if props.rotate_duplicates:
                if props.rotation_axis[0]: o.rotation_euler.x = c['no'][0]
                if props.rotation_axis[1]: o.rotation_euler.y = c['no'][1]
                if props.rotation_axis[2]: o.rotation_euler.z = c['no'][2]

    def execute(self, context):
        self.create_duplicates( 
            context, 
            self.get_element_coordinates( context ) 
        )

        return {'FINISHED'}

def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.mesh_dupli_props = bpy.props.PointerProperty( 
        type = MeshDumpliPropGroup 
    )
    
def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.Scene.mesh_dupli_props = ''