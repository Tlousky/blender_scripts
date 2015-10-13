bl_info = {
    "name"        : "Update text to mesh",
    "blender"     : (2, 75, 0),
    "version"     : (0, 0, 0, 1),
    "location"    : "3D View > Toolbox",
    "description" : "Update mesh copy of text object",
    "category"    : "Object"
}

import bpy

class update_text_mesh( bpy.types.Operator ):
    bl_idname      = 'object.update_text_mesh'
    bl_label       = 'Update text mesh'
    bl_options     = {'REGISTER', 'UNDO'}

    @classmethod
    def poll( self, context ): return 'Text' in context.scene.objects

    def generate_text_mesh( self, context ):
        if 'TextMesh' not in context.scene.objects:
             m = bpy.data.meshes.new_from_object( 
                context.scene, context.scene.objects['Text'], True, 'RENDER', True, True 
             )

             o = bpy.data.objects.new( 'TextMesh', m )
             context.scene.objects.link( o )

    def execute( self, context ):
        o = context.scene.objects['TextMesh']
        t = context.scene.objects['Text']

        t.hide = True
        o.location = t.location

        o.data = t.to_mesh( context.scene, True, 'RENDER', True, True )
        
        return {'FINISHED'}
        

class UpdateTextPanel( bpy.types.Panel ):
    bl_idname      = "UpdateTextPanel"
    bl_label       = "Text to Mesh Updater"
    bl_category    = "Text"
    bl_space_type  = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    
    @classmethod
    def poll( self, context ): return 'Text' in context.scene.objects

    def draw( self, context):
        layout = self.layout
        col    = layout.column()
        
        col.operator(
            'object.update_text_mesh',
            text = 'Update text mesh'
        )
          
def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()