# Author: Tamir Lousky
# Updated: 27Dec2015

bl_info = {
    "name"        : "Add Archimedian Spiral",
    "author"      : "Tamir Lousky",
    "version"     : (0, 0, 1),
    "blender"     : (2, 75, 0),
    "category"    : "Add Mesh",
    "location"    : "View3D > Add > Mesh > Archimedian Spiral",
    "tracker_url" : "https://github.com/Tlousky/blender_scripts/blob/master/add_archimedian_spiral.py",
    "description" : "Generates An Archimedian Spiral"
}

import bpy
from math import cos, sin

# Operator adding function (used to inject operator to menu)
def menu_func( self, context ):
    self.layout.operator(
        "mesh.add_archimedian_spiral",
        text = "Spiral",
        icon = "PLUGIN"
    )

class add_archimedian_spiral( bpy.types.Operator ):
    """ Generate Archimedian Spiral """
    bl_idname      = "mesh.add_archimedian_spiral"
    bl_label       = "Add Spiral"
    bl_description = "Add Archimedian Spiral"
    bl_options     = {'REGISTER', 'UNDO'}

    @classmethod
    def poll( self, context ): return True

    name   = bpy.props.StringProperty( default = 'archispiral' )
    size   = bpy.props.FloatProperty( 
        default = 0.1,
        min     = 0
    )
    length = bpy.props.IntProperty( 
        default = 500,
        min     = 10
    )
    height = bpy.props.FloatProperty( 
        default = 5,
        min     = 0,
    )

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.prop( self, 'name'   )
        box.prop( self, 'size'   )
        box.prop( self, 'length' )
        box.prop( self, 'height' )
    
    def execute( self, context ):
        S = bpy.context.scene

        mesh = bpy.data.meshes.new( name = self.name )

        o = bpy.data.objects.new( self.name, mesh )
        o.location = (0,0,0) # place at object origin
        S.objects.link( o )

        z     = 0
        verts = []  
        for i in range( self.length ):
            angle = 0.1 * i
            x     = ( 2 * self.size * angle ) * cos( angle )
            y     = ( 2 * self.size * angle ) * sin( angle )
            z    += i / 10000 * self.height
            verts.append((x,y,z))

        edges = []
        for i in range( len( verts ) ):
            if i == len( verts ) - 1: break
            edges.append((i, i+1))
                
        mesh.from_pydata( verts, edges, [] )

        return {'FINISHED'}

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_mesh_add.append( menu_func )

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_mesh_add.remove( menu_func )

if __name__ == "__main__":
    register()