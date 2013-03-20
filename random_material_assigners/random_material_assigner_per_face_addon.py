# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

#
#
#  Author            : Tamir Lousky (tlousky@gmail.com)
#
#  Homepage(Wiki)    : http://biological3d.wordpress.com/
#
#  Start of project              : 2013-01-25 by Clemens Barth
#  Last modified                 : 2013-01-30
#
#  Acknowledgements 
#  ================
#
#  Blender: Patrick Boelens (helpful tuts!), CoDEmanX (useful bmesh info on BA forums!)

bl_info = {    
    "name"       : "Random Face Material Assigner",
    "author"     : "Tamir Lousky",
    "version"    : (1, 0, 0),
    "blender"    : (2, 65, 0),
    "category"   : "Materials",
    "location"   : "3D View >> Tools",
    "wiki_url"   : "http://blenderartists.org/forum/showthread.php?279723",
    "tracker_url": "http://blenderartists.org/forum/showthread.php?279723",
    "description": "Assign random materials to mesh object faces."}

import bpy
import random
import bmesh

class random_mat_panel(bpy.types.Panel):
    bl_idname      = "randomFaceMatPanel"
    bl_label       = "Random Face Material Assigner"
    bl_space_type  = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context     = 'objectmode'

    def draw( self, context):                # Draw panel UI elements #
        layout = self.layout                 # Reference to panel layout object
        
        props = context.scene.face_assigner  # Create reference material assigner property group

        col1 = layout.column()               # Create a column
        col1.label(text="Randomly assign materials to each face on the object")
        
        box = layout.box()                   # Draw a box
        col2 = box.column(align=True)        # Create a column
        col2.prop( props, "rand_seed"  )     # Create randomization seed property on column
        col2.label(text="use this field to filter materials by name")
        col2.prop( props, "mat_prefix" )     # And the material prefix property too

class rand_mat_assigner(bpy.types.PropertyGroup):
   
    def randomize( self, context ):
        """ function name: randomize
            description:   This function assigns a random material to each face on the selected
                           object's mesh, from its list of materials (filtered by the mat_prefix)
        """
        random.seed(self.rand_seed)   # Set the randomization seed
    
        all_materials = bpy.context.object.data.materials
        filtered_materials = []

        if self.mat_prefix != "":                       # IF the user entered a prefix
            for material in all_materials:              # Iterate over all the object's materials
                if self.mat_prefix in material.name:    # Look for materials with the prefix
                    filtered_materials.append(material) # And filter them in
        else:
            filtered_materials = all_materials          # If there's no prefix, use all materials
        
        no_of_materials = len(filtered_materials)       # Count all/filtered materials on object

        bpy.ops.object.mode_set(mode = 'EDIT')          # Go to edit mode to create bmesh
        ob = bpy.context.object

        bm = bmesh.from_edit_mesh(ob.data)              # Create bmesh object from object mesh

        for face in bm.faces:    # Iterate over all of the object's faces
            face.material_index = random.randint(0, no_of_materials - 1)  # Assign random material to face
            
        ob.data.update()                            # Update the mesh from the bmesh data
        bpy.ops.object.mode_set(mode = 'OBJECT')    # Return to object mode

        return {'FINISHED'}

    rand_seed = bpy.props.IntProperty(     # Randomization seed
        name="rand_seed",
        description="Randomization seed",
        update=randomize)  
    mat_prefix = bpy.props.StringProperty( # Prefix to filter materials by
        name="mat_prefix", 
        description="Material name filter",
        default="",
        update=randomize)

def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.face_assigner = bpy.props.PointerProperty(type=rand_mat_assigner)
    
def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.Scene.face_assigner = bpy.props.PointerProperty(type=rand_mat_assigner)