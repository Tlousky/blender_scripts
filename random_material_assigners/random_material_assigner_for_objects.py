bl_info = {
    "name"     : "Random Material Assigner for Objects",
    "category" : "Object",
    "author"   : "Tamir Lousky",
    "version"  : "1.0"
}

import bpy
import random

class random_mat_panel(bpy.types.Panel):
    bl_idname      = "randomObjMatPanel"
    bl_label       = "Random Material Assigner for the selected objects"
    bl_space_type  = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    def draw( self, context) :
        layout = self.layout
        layout.operator("object.rand_mat_assigner")
        
class rand_mat_assigner( bpy.types.Operator ):
    """ Assign a random material to the each of the selected objects """ # Tooltip
    bl_idname      = "object.rand_mat_assigner"                          # Unique identifier for buttons and menus to reference
    bl_label       = "Assign Random Materials to selected objects"       # display name
    bl_description = "This script assigns random materials out of \
                      a pool of materials which share a name prefix, \
                      to a each of the selected objects"
    bl_options     = {'REGISTER', 'UNDO' }                               # Enable undo

    seed   = bpy.props.IntProperty(name="seed")      # randomization seed
    prefix = bpy.props.StringProperty(name="prefix", default="") # a field in the panel to choose the prefix name

    def execute( self, context):
        self.randomize()
        return {'FINISHED'}

    def check( self, context ):  # This function runs when properties change
        random.seed(self.seed)   # Set the randomization seed
        self.randomize()
        return {'FINISHED'}
        
    def randomize( self ):
        random.seed(self.seed)   # Set the randomization seed
    
        filtered_materials = []
        if self.prefix != "":                           # If the user entered a prefix
            for material in bpy.data.materials:         # Iterate over all materials
                if self.prefix in material.name:        # Look for materials with the prefix
                    filtered_materials.append(material) # And filter them in
        else:
            filtered_materials = bpy.data.materials     # If there's no prefix, use all materials
        
        no_of_materials = len(filtered_materials)
        
        for obj in bpy.context.selected_objects:        # Iterate over all selected objects
            random_index    = random.randint(0, no_of_materials - 1)    # Choose a random (index) number
            randomly_chosen_material = filtered_materials[random_index] # Reference the corresponding material
            obj.active_material = randomly_chosen_material              # Then assign this material to the current object
        
        return {'FINISHED'}        

# This registers the class and panel when the script starts
bpy.utils.register_class(rand_mat_assigner)
bpy.utils.register_class(random_mat_panel)
