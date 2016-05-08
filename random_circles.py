import bpy
from mathutils import Vector
from random import random

def check_circle_bounbox( circC, circR, rectC, rectR ):
    ''' Make sure this circle does not protrude outside the rectangle's bounding box '''
    maxX = rectC.x + rectR
    minX = rectC.x - rectR
    maxY = rectC.y + rectR
    minY = rectC.y - rectR

    withinX = ( circC.x + circR <= maxX ) and ( circC.x - circR >= minX )
    withinY = ( circC.y + circR <= maxY ) and ( circC.y - circR >= minY )

    return withinX and withinY

def check_overlap( circles, circC, circR ):
    ''' Make sure the distance between the current circle's center and all
        other circle centers is greater than or equal to the circle's perimeter (2r)
    '''
    return len(
        [ True for c in circles if ( c - circC ).length >= circR * 2 ]
    ) == len( circles )

circleRadius = 1.0
circleCount  = 100
rectCenter   = Vector((0, 0, 0))
rectRadius   = 10

circles = []

maxIterations = 500 # Set max number of loop iterations to prevent infinite loop

z = 0 # All circles lie on Z = 0
i = 0 # Current loop iteration
while len( circles ) < circleCount and i < maxIterations:
    x = rectCenter.x + 2 * rectRadius * random() - rectRadius
    y = rectCenter.y + 2 * rectRadius * random() - rectRadius
    circC = Vector((x, y, z ))

    if check_circle_bounbox( circC, circleRadius, rectCenter, rectRadius ) \
       and check_overlap( circles, circC, circleRadius ):
           circles.append( circC )

    i += 1

for c in circles:
    bpy.ops.mesh.primitive_circle_add( radius = circleRadius, location = c )