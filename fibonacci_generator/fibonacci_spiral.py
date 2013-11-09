import bpy
from mathutils import Vector
from math import sqrt, radians, sin, cos

w = 1 # weight  

def F(n):
    return ((1+sqrt(5))**n-(1-sqrt(5))**n)/(2**n*sqrt(5))
 
def MakePolyLine(objname, curvename, cList):  
    curvedata = bpy.data.curves.new(name=curvename, type='CURVE')  
    curvedata.dimensions = '3D'  
  
    objectdata = bpy.data.objects.new(objname, curvedata)  
    objectdata.location = (0,0,0) #object origin  
    bpy.context.scene.objects.link(objectdata)  
  
    polyline = curvedata.splines.new('BEZIER')  
    polyline.bezier_points.add(len(cList)-1)

    for bp, vp in zip(polyline.bezier_points, cList):
        x, y, z = vp  
        bp.co = (x, y, z)

    obj = bpy.context.scene.objects[ objectdata.name ]
    obj.select = True
    bpy.context.scene.objects.active = obj
    
    for bp in polyline.bezier_points:    
        for htype in [ p for p in dir(bp) if 'handle_' in p and 'type' in p]:
            setattr( bp, htype, 'AUTO' )
            setattr( bp, htype, 'FREE' )
            #setattr( bp, htype, 'ALIGNED' )
    
    bpy.ops.object.mode_set( mode = 'EDIT' )

    r_angle = -45
    odata   = obj.data.splines[0]

    bp = odata.bezier_points[0]
    for orientation in [ 'right', 'left' ]:
        x,y = getattr(bp, 'handle_' + orientation)[:2]
        x_rot   = x * cos( r_angle ) - y * sin( r_angle )
        y_rot   = x * sin( r_angle ) + y * cos( r_angle )
        rot_vec = Vector(( x_rot, y_rot, 0 ))

        print( getattr(bp, 'handle_' +   orientation), " --> ", rot_vec )
        
        setattr( bp, 'handle_' + orientation, rot_vec )

    bp = odata.bezier_points[-1]        

    xc, yc  = bp.co[:2]
    r_angle = 180
    for orientation in [ 'right', 'left' ]:
        x,y = getattr(bp, 'handle_' + orientation)[:2]
        xdiff = xc - x 
        ydiff = yc - y
        
        x_rot = xdiff * cos( r_angle ) - ydiff * sin( r_angle )
        y_rot = xdiff * sin( r_angle ) + ydiff * cos( r_angle )
        
        rot_vec = Vector(( x_rot + xc, y_rot + yc, 0 ))

        print( getattr(bp, 'handle_' +   orientation), " --> ", rot_vec )
        
        setattr( bp, 'handle_' + orientation, rot_vec )
    
    bpy.ops.object.mode_set( mode = 'OBJECT' )

listOfVectors = []
growth_direction = 1
for i in range(0,10):
    p_offset = F(i) * growth_direction

    if i % 2 == 0:
        if not len(listOfVectors): # If this is the first point
            listOfVectors += [ Vector(( 0, p_offset, 0 )) ]
        else:
            growth_direction *= -1
            prev_point_x = listOfVectors[len(listOfVectors) - 1][0]
            listOfVectors += [ Vector(( prev_point_x, p_offset, 0 )) ]
    else:
        if not len(listOfVectors): # If this is the first point
            listOfVectors += [ Vector(( p_offset, 0, 0 )) ]
        else:
            prev_point_y = listOfVectors[len(listOfVectors) - 1][1]
            listOfVectors += [ Vector(( p_offset, prev_point_y, 0 )) ]
MakePolyLine("FibCurveObj", "FibCurve", listOfVectors) 