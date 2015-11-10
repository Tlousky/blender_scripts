bl_info = {
    "name"        : "Move object with Vert",
    "blender"     : (2, 74, 0),
    "version"     : (0, 0, 0, 1),
    "location"    : "3D View > Toolbox",
    "description" : "Move object with Vert",
    "category"    : "Object"
}

import bpy, bmesh
from mathutils import Vector

class VertexMoverPropGroup( bpy.types.PropertyGroup ):
    newLoc = bpy.props.FloatVectorProperty(
        name        = "New Location",
        description = "New location for selected vertex",
        default     = ( 0.0, 0.0, 0.0 ),
        precision   = 2,
        subtype     = 'XYZ',
        unit        = 'LENGTH',
        size        = 3
    )

def get_current_vertex_loc():
    o = bpy.context.object
    if o:
        if o.mode == 'EDIT':
            bm = bmesh.from_edit_mesh( o.data )
            activeElement = bm.select_history.active
            if activeElement and type( activeElement ) == bmesh.types.BMVert:
                return o.matrix_world * bm.select_history.active.co
    return False    
        
class VertexMover( bpy.types.Operator ):
    """ Move vertex to desired position and object with it """
    bl_idname      = "object.vertex_and_object_mover"
    bl_label       = "Vertex Mover"
    bl_description = "Move vertex to desired position and object with it"
    bl_options     = {'REGISTER', 'UNDO'}

    @classmethod
    def poll( self, context ):
        return get_current_vertex_loc()

    def execute( self, context ):
        o     = context.object
        newLoc = context.scene.vertex_mover_props.newLoc

        offset = Vector( newLoc ) - get_current_vertex_loc()
        o.location += offset

        return {'FINISHED'}
    
class VertexMoverPanel( bpy.types.Panel ):
    bl_idname      = "VertexMoverPanel"
    bl_label       = "Move objet by vertex"
    bl_category    = "Vertex Mover"
    bl_space_type  = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    @classmethod
    def poll( self, context ): 
        return context.object and context.object.mode == 'EDIT'

    def draw( self, context):
        layout = self.layout
        col    = layout.column()
        props  = context.scene.vertex_mover_props

        vertLoc = get_current_vertex_loc() if get_current_vertex_loc() else [ "N/A" for i in range(3) ]
        col.label( "Current Position" )
        col.label( "X: %s  Y: %s  Z: %s" % tuple( vertLoc ) ) 

        col.prop( props, 'newLoc' )

        col.operator(
            'object.vertex_and_object_mover',
            text = 'Move',
            icon = 'MAN_TRANS'
        )

def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.vertex_mover_props = bpy.props.PointerProperty(
        type = VertexMoverPropGroup
    )

def unregister():
    bpy.utils.unregister_module(__name__)