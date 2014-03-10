# ##### BEGIN GPL LICENSE BLOCK #####
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# Author           : Tamir Lousky ( tlousky@gmail.com )
# Homepage(Wiki)   : http://bioblog3d.wordpress.com
# Start of project : 2013-11-01 by Tamir Lousky
# Last modified    : 2013-10-03

bl_info = {    
    "name"        : "Fibonacci",
    "author"      : "Tamir Lousky",
    "version"     : (0, 0, 1),
    "blender"     : (2, 69, 0),
    "category"    : "Add Curve",
    "warning"     : "",
    "location"    : "View3D > Add > Curve > Fibonacci",
    "wiki_url"    : "",
    "tracker_url" : "https://github.com/Tlousky/blender_scripts.git",
    "description" : "Generates Fibonacci objects"
}

import bpy
from mathutils import Vector
from math import sqrt, radians, sin, cos

## Constants
w                = 1 # Curve weight  

def F(n):
    ''' returns the Fibonacci number of n-th iteration '''
    return (( 1 + sqrt(5) ) ** n - ( 1 - sqrt(5) ) ** n ) / ( 2 ** n * sqrt(5))
 
def MakePolyLine( objname, curvename, cList ):
    ''' This function creates a Bezier curve object from the list of provided 
        points with object name objname, and curve data block name curvename.
        It also rotates bezier handles to create a smooth spiral.
    '''
    curvedata = bpy.data.curves.new( name = curvename, type = 'CURVE' )  
    curvedata.dimensions = '3D'  
  
    # Create a new object, set its origin to xyz = 0, link obj to scene
    objectdata = bpy.data.objects.new( objname, curvedata)  
    objectdata.location = (0,0,0) # object origin  
    bpy.context.scene.objects.link( objectdata )  
  
    # Create a bezier spline and add the same number of control points as
    # the number of coordinates in provided cList
    polyline = curvedata.splines.new( 'BEZIER' )
    polyline.bezier_points.add( len(cList) - 1 )

    # Set each control point's XYZ coordiate
    for bp, vp in zip( polyline.bezier_points, cList ):
        x, y, z = vp  
        bp.co = (x, y, z)

    # Reference curve object, select and activate it
    obj = bpy.context.scene.objects[ objectdata.name ]
    obj.select = True
    bpy.context.scene.objects.active = obj
    
    # Set bezier handles to Auto, then Free
    for bp in polyline.bezier_points:    
        for htype in [ p for p in dir(bp) if 'handle_' in p and 'type' in p]:
            setattr( bp, htype, 'AUTO' )
            setattr( bp, htype, 'FREE' )
    
    bpy.ops.object.mode_set( mode = 'EDIT' ) # Go to edit mode

    r_angle = -45
    odata   = obj.data.splines[0] # Reference spline data block

    # Rotate handles to create the correct perfect spiral shape
    bp = odata.bezier_points[0]
    for orientation in [ 'right', 'left' ]:
        # Get 2D (XY) coordinates of right / left handle
        x,y = getattr( bp, 'handle_' + orientation )[:2]

        # Calculate new X and Y positions from rotation
        x_rot   = x * cos( r_angle ) - y * sin( r_angle )
        y_rot   = x * sin( r_angle ) + y * cos( r_angle )

        # Create rotation vector to set new handle coordinates
        rot_vec = Vector(( x_rot, y_rot, 0 ))

        setattr( bp, 'handle_' + orientation, rot_vec )

    # Reference last bezier point
    bp = odata.bezier_points[-1] 

    # Rotate the very last bezier point by 180 deg to complete spiral
    xc, yc  = bp.co[:2]
    r_angle = 180
    for orientation in [ 'right', 'left' ]:
        # Get 2D (XY) coordinates of right / left handle
        x,y = getattr(bp, 'handle_' + orientation)[:2]
        xdiff = xc - x 
        ydiff = yc - y

        # Calculate new X and Y positions from rotation
        x_rot = xdiff * cos( r_angle ) - ydiff * sin( r_angle )
        y_rot = xdiff * sin( r_angle ) + ydiff * cos( r_angle )

        # Create rotation vector to set new handle coordinates        
        rot_vec = Vector(( x_rot + xc, y_rot + yc, 0 ))

        setattr( bp, 'handle_' + orientation, rot_vec )
    
    bpy.ops.object.mode_set( mode = 'OBJECT' ) # Return to object mode


class add_fibonacci_spiral( bpy.types.Operator ):
    """ Add a Fibonacci Spiral: Operator """

    bl_idname  = "curve.add_fibonacci_spiral"
    bl_label   = "Add Fibonacci Spiral"
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}

    iterations = bpy.props.IntProperty(
        name        = "Iterations",
        description = "Number of fractal iterations",
        min         = 1,
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

    def create_control_points( self, context ):
        listOfVectors   = []
        growth_direction = 1 # Direction of Fib spiral

        for i in range( self.iterations ):
            # Calculate offset distance
            p_offset = F(i) * growth_direction

            if i % 2 == 0: # Even and odd points positioned differently
                if not len(listOfVectors): # If this is the first point
                    listOfVectors += [ Vector(( 0, p_offset, 0 )) ]
                else:
                    growth_direction *= -1
                    prev_point_x   = listOfVectors[len(listOfVectors) - 1][0]
                    listOfVectors += [ Vector(( prev_point_x, p_offset, 0 )) ]
            else:
                if not len(listOfVectors): # If this is the first point
                    listOfVectors += [ Vector(( p_offset, 0, 0 )) ]
                else:
                    prev_point_y   = listOfVectors[len(listOfVectors) - 1][1]
                    listOfVectors += [ Vector(( p_offset, prev_point_y, 0 )) ]

        return listOfVectors

    def draw( self, context ):
        layout = self.layout
        
        box = layout.box()
        box.prop( self, 'radius'     )
        box.prop( self, 'iterations' )
        
    def execute( self, context ):

        MakePolyLine( 
            "FibCurveObj", 
            "FibCurve", 
            self.create_control_points( context ) 
        ) 

        return {'FINISHED'}
        
# Operator adding function (used to inject operator to menu)
def menu_func( self, context ):
    self.layout.operator( 
        "curve.add_fibonacci_spiral", 
        text = "Fibonacci", 
        icon = "PLUGIN"
    )

def register():
    bpy.utils.register_module(__name__)

    # Add "Fibonacci" menu to the "Add Mesh" menu
    bpy.types.INFO_MT_curve_add.append( menu_func )

def unregister():
    bpy.utils.unregister_module(__name__)

    # Remove "Fibonacci" menu from the "Add Mesh" menu.
    bpy.types.INFO_MT_curve_add.remove( menu_func )

if __name__ == "__main__":
    register()
