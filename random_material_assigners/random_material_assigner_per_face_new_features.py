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
#  Homepage(Wiki)    : http://bioblog3d.wordpress.com/
#
#  Start of project              : 2013-01-25 by Tamir Lousky
#  Last modified                 : 2017-02-10
#
#  Acknowledgements
#  ================
#
#  Blender: Patrick Boelens (helpful tuts!), CoDEmanX (useful bmesh info @ BA forums!),
#           ni-ko-o-kin ( useful vertex groups info @ BA forums),
#           supergra    ( great tip on how to select loose parts @ BA forums ).

bl_info = {
    "name"       : "Random Face Material Assigner",
    "author"     : "Tamir Lousky",
    "version"    : (3, 0, 2),
    "blender"    : (2, 78, 0),
    "category"   : "Materials",
    "location"   : "3D View >> Tools",
    "wiki_url"   : "http://bioblog3d.wordpress.com/2013/03/20/random-material-assigner-v2/",
    "tracker_url": "https://github.com/Tlousky/blender_scripts/blob/master/random_material_assigners/random_material_assigner_per_face_new_features.py",
    "description": "Assign random materials to mesh faces, vertex groups or loose parts."}

import bpy
import random
import bmesh

class random_mat_panel(bpy.types.Panel):
    bl_idname      = "randomFaceMatPanel"
    bl_label       = "Random Face Material Assigner"
    bl_space_type  = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context     = 'objectmode'

    @classmethod
    def poll( self, context ):
        ''' Only show panel if there is an active mesh object '''
        return context.object and context.object.type == 'MESH'

    def draw( self, context):                # Draw panel UI elements #
        layout = self.layout                 # Reference to panel layout object

        props = context.scene.face_assigner  # Create reference material assigner property group

        col1 = layout.column()               # Create a column
        col1.label(text="Randomly assign materials to each face on the object")

        box = layout.box()                   # Draw a box
        col2 = box.column(align=True)        # Create a column
        col2.prop( props, "rand_seed"  )     # Create randomization seed property on column
        col2.label(text="use this field to filter materials by name")
        col2.prop( props, "mat_prefix" )     # Material prefix property too
        col2.label(text="Distribute materials according to:")
        col2.prop( props, "assign_method" )  # Material assignment method prop

class rand_mat_assigner(bpy.types.PropertyGroup):

    def get_verts_and_groups( self ):
        """ function name: get_verts_and_groups
            description:   iterates over all vertex groups, and aggregates
                           the vertex indices if each vgroup.
            return value:  dict with this info
        """
        ob = bpy.context.object

        groups = {}

        for group in ob.vertex_groups:
            groups[str(group.index)] = []

        for v in ob.data.vertices:
            # iterate over this particular vertex's vgroups
            for group in v.groups:
                # And add the vert index to the group dictionary and each group's list of verts
                groups[str(group.group)].append( v.index )

        return groups

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

        ## Distribute materials based on vertex groups
        if self.assign_method == 'Vertex Group':

            vgroups = self.get_verts_and_groups()     # Get vgroups
            if vgroups and len( vgroups.keys() ) > 0: # make sure that there are actually vgroups on this mesh

                for vgroup in list( vgroups.keys() ):
                    # get random material index
                    rand_mat_index  = random.randint(0, no_of_materials - 1)

                    # Go to vertex selection mode
                    bpy.ops.mesh.select_mode(
                        use_extend=False,
                        use_expand=False,
                        type='VERT')

                    bpy.ops.mesh.select_all(action='DESELECT')  # Deselect all verts

                    # Select all the vertices in the vertex group
                    bm.verts.ensure_lookup_table()

                    for vert in vgroups[vgroup]:
                        bm.verts[vert].select_set(True)

                    # Go to face selection mode
                    bm.select_mode = {'FACE'}
                    bm.select_flush(True)

                    # iterate over all selected faces and assign vgroup material
                    for face in bm.faces:
                        if face.select:
                            face.material_index = rand_mat_index  # Assign random material to face
            else:
                print( "No vertex groups on this mesh, cannot distribute materials!" )

        ## Distribute a rand material to each face
        elif self.assign_method == 'Face':
            for face in bm.faces:    # Iterate over all of the object's faces
                face.material_index = random.randint(0, no_of_materials - 1)  # Assign random material to face

        ## Distribute materials by loose parts
        elif self.assign_method == 'Loose Parts':
            bm.verts.ensure_lookup_table()
            vert_indices = [ vert.index for vert in bm.verts ]  # Reference all vertex indices

            for vert in vert_indices:
                bpy.ops.mesh.select_all(action='DESELECT')  # Deselect all verts

                bm.verts.ensure_lookup_table()
                bm.verts[vert].select = True

                # Select all verts linked to this one (on the same island or "loose part")
                bpy.ops.mesh.select_linked()

                # Go to face selection mode
                bm.select_mode = {'FACE'}
                bm.select_flush(True)

                rand_mat_index  = random.randint(0, no_of_materials - 1)

                # iterate over all selected (linked) faces and assign material
                for face in bm.faces:
                    if face.select:
                        face.material_index = rand_mat_index  # Assign random material to face

                # remove selected vertices from list
                for vert in bm.verts:
                    if vert.select:
                        removed = vert_indices.pop( vert_indices.index(vert.index) )

        ob.data.update()                            # Update the mesh from the bmesh data
        bpy.ops.object.mode_set(mode = 'OBJECT')    # Return to object mode

        return None

    rand_seed = bpy.props.IntProperty(      # Randomization seed
        name        = "rand_seed",
        description = "Randomization seed",
        options     = {'ANIMATABLE'},
        update      = randomize
    )

    mat_prefix = bpy.props.StringProperty(  # Prefix to filter materials by
        name        = "mat_prefix",
        description = "Material name filter",
        default     = "",
        update      = randomize
    )

    items = [
        ('Face', 'Face', ''),
        ('Vertex Group', 'Vertex Group', ''),
        ('Loose Parts', 'Loose Parts', '')
    ]

    assign_method = bpy.props.EnumProperty( # Material distribution method
        name    = "Material distribution method",
        items   = items,
        default = 'Face'
    )

def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.face_assigner = bpy.props.PointerProperty(type=rand_mat_assigner)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.Scene.face_assigner = None