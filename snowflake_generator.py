# Author: Tamir Lousky
# Updated: 23Jan2014

bl_info = {
    "name"        : "Snowflake Generator",
    "author"      : "Tamir Lousky",
    "version"     : (0, 0, 1),
    "blender"     : (2, 69, 0),
    "category"    : "Add Mesh",
    "location"    : "View3D > Add > Mesh > Snowflake",
    "wiki_url"    : "https://github.com/Tlousky/blender_scripts/wiki/Snowflake-Generator",
    "tracker_url" : "https://github.com/Tlousky/blender_scripts/blob/master/snowflake_generator.py",
    "description" : "Generates Koch Snowflakes"
}

import bpy, json, bmesh
from mathutils import Vector, Matrix
from math      import pi, radians, cos, sin, sqrt

def draw_initial_polygon( sides = 6, radius = 1.0 ):
    """ Create initial polygon shape """

    points = []
    edges  = []
    step   = ( 2.0 / sides )
    i      = 0

    for i in range( sides ):
        t  = ( i * step )
        x1 = cos( t * pi ) * radius
        y1 = sin( t * pi ) * radius

        points.append( ( x1, y1, 0 ) )

    for i in range( len(points) ):
        edge = []

        if i == len( points ) - 1:
            edge.append( i )
            edge.append( 0 )
        else:
            edge.append( i )
            edge.append( i + 1)

        edges.append( tuple( edge ) )

    return { 'verts' : points, 'edges' : edges }

def create_mesh_obj( name, data ):
    # Create mesh and object
    m = bpy.data.meshes.new( name + '_mesh' )
    o = bpy.data.objects.new( name, m )

    o.location  = ( 0, 0, 0 )

    # Link object to scene
    bpy.context.scene.objects.link( o )

    # Create mesh from given verts, edges, faces. Either edges or
    # faces should be [], or you ask for problems
    m.from_pydata( data['verts'], data['edges'], [] )

    # Update mesh with new data
    m.update( calc_edges = True )

    return o

def create_snowflake( o, iterations = 2 ):

    # Create rotation matrices
    rot_matrix         = Matrix.Rotation( radians(90), 3, 'Z' )
    turn_around_matrix = Matrix.Rotation( radians(180), 3, 'Z' )

    # Select object and set it as active object
    o.select = True
    bpy.context.scene.objects.active = o

    # Ensure we're in edit mode and in vertex selection mode
    if o.mode != 'EDIT': bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.select_mode(type = 'VERT')

    for i in range( iterations ):
        # Refresh object data and edge list (which changes with each iterations)
        d     = o.data
        bm    = bmesh.from_edit_mesh( d )
        bv    = bm.verts
        edges = { e.index : [ v.index for v in e.verts ] for e in bm.edges }

        for edge_index, edge in enumerate( edges ):
            # Go to vert selection mode
            bpy.ops.mesh.select_mode(type = 'VERT')

            # Deselect all verts
            bpy.ops.mesh.select_all(action = 'DESELECT')

            # Select current edge (by selecting its verts)
            bm.verts.ensure_lookup_table() # Update verts list

            for v in edges[ edge ]:
                bv[ v ].select = True

            bm.select_flush( True )

            # Subdivide edge
            result = bpy.ops.mesh.subdivide( number_cuts = 2 )

            bm.select_flush( True )

            # Find innermost edge
            selected_edges = {
                e.index : set([ v.index for v in e.verts ]) \
                for e in bm.edges if e.select
            }

            # Innermost edge shares both its verts with the other edges
            mid = 42  # out-of-range index to to indicate if procedure worked
            for i in selected_edges.keys():
                other_edges = set( selected_edges.keys() ) - set( [i] )

                # check how many joint verts this edge has with the others
                num_of_joint_verts = 0
                for oe in other_edges:
                    if selected_edges[i] & selected_edges[oe]:
                        num_of_joint_verts += 1

                # The middle edge will have two joint verts
                if num_of_joint_verts == 2:
                    mid = i
                    break

            # Select innermost edge (by selecting its verts)
            bm.verts.ensure_lookup_table() # Update verts list

            bpy.ops.mesh.select_all(action = 'DESELECT')
            for v in selected_edges[ mid ]:
                bv[ v ].select = True

            bm.select_flush( True )

            # Subdivide it once
            bpy.ops.mesh.subdivide( number_cuts = 1 )

            # Select innermost vert (joint vert between both edges)
            selected_edges_verts = [
                set([ v.index for v in e.verts ]) for e in bm.edges if e.select
            ]

            # Find common vert by intersecting both vert sets
            joint_vert = list(
                selected_edges_verts[0] & selected_edges_verts[1]
            ).pop()

            # Find the verts that aren't joint (via set symmetrical_difference)
            other_verts = list(
                selected_edges_verts[0] ^ selected_edges_verts[1]
            )
            
            # Make sure vertices are in right order
            if(other_verts[0] > other_verts[1]):
                other_verts[0], other_verts[1] = other_verts[1], other_verts[0]

            # Calculate its new position: should create an equilateral triangle
            bm.verts.ensure_lookup_table() # Update verts list

            vdiff = bv[ other_verts[1] ].co - bv[ other_verts[0] ].co
            vdiff[0] *=  sqrt(3)/2.0
            vdiff[1] *=  sqrt(3)/2.0
            vrot  = vdiff * rot_matrix

            new_pos = bv[ joint_vert ].co + vrot

            # Select middle vert and translate it by the rotate vector
            bpy.ops.mesh.select_all(action = 'DESELECT')
            bv[ joint_vert ].select = True

            bm.select_flush( True )

            bpy.ops.transform.translate( value = tuple( vrot ) )

    # Return to object mode
    bpy.ops.object.mode_set(mode = 'OBJECT')

class add_snowflake( bpy.types.Operator ):
    """Add a Koch Snowflake"""
    bl_idname  = "mesh.add_snowflake"
    bl_label   = "Add Snowflake"
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}

    iterations = bpy.props.IntProperty(
        name        = "Iterations",
        description = "Number of fractal iterations",
        min         = 0,
        max         = 6,
        default     = 2
    )

    sides = bpy.props.IntProperty(
        name        = "Number of sides",
        description = "The number of sides of the initial polygon",
        min         = 3,
        max         = 32,
        default     = 6
    )

    radius = bpy.props.FloatProperty(
        name        = "Radius",
        description = "Radius of the snowflake",
        min         = 0.1,
        max         = 100.0,
        unit        = 'LENGTH',
        default     = 1.0
    )

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.prop( self, 'radius'     )
        box.prop( self, 'sides'      )
        box.prop( self, 'iterations' )

    def execute(self, context):

        create_snowflake(
            create_mesh_obj(
                'snowflake', draw_initial_polygon(
                    sides  = self.sides,
                    radius = self.radius
                )
            ), iterations = self.iterations
        )

        return {'FINISHED'}

# Operator adding function (used to inject operator to menu)
def menu_func( self, context ):
    self.layout.operator(
        "mesh.add_snowflake",
        text = "Snowflake",
        icon = "PLUGIN"
    )

def register():
    bpy.utils.register_module(__name__)

    # Add "Snowflake" menu to the "Add Mesh" menu
    bpy.types.INFO_MT_mesh_add.append( menu_func )

def unregister():
    bpy.utils.unregister_module(__name__)

    # Remove "Snowflake" menu from the "Add Mesh" menu.
    bpy.types.INFO_MT_mesh_add.remove( menu_func )

if __name__ == "__main__":
    register()
