from PIL import Image, ImageDraw
from matplotlib import pyplot as plt
from math import radians, degrees, sqrt, acos, cos, sin

def dotproduct(v1, v2):
  return sum( (a*b) for a, b in zip(v1, v2) )

def length(v):
  return sqrt( dotproduct(v, v) )

def angle(v1, v2):
  return acos( dotproduct(v1, v2) / ( length(v1) * length(v2) ) )
  
def vec_subtraction( v1, v2 ):
    return [ e1 - e2 for e1, e2 in zip( v1, v2 ) ]

def calc_edge_vec( poly, edge ):
    p1 = poly['points'][ edge[0] ]
    p2 = poly['points'][ edge[1] ]
    
    return vec_subtraction( p2, p1 )

def rotatePolygon( poly, theta ):
    ''' Rotates the given polygon which consists of corners represented
        as (x,y), around the ORIGIN, clock-wise, theta degrees
    '''

    rotatedPolygon = []
    for corner in poly:
        rotatedPolygon.append((
            corner[0] * cos( theta ) - corner[1] * sin( theta ), # x
            corner[0] * sin( theta ) + corner[1] * cos( theta )  # y
        ))

    # Make sure rotated polygon coordinates are within image boundaries
    minX = min( [ c[0] for c in rotatedPolygon ] ) * -1
    minX = minX if minX > 0 else 0
    minY = min( [ c[1] for c in rotatedPolygon ] ) * -1
    minY = minY if minY > 0 else 0

    rotatedPolygon = [ ( x + minX, y + minY ) for x, y in rotatedPolygon ]
    
    return rotatedPolygon

def draw_and_plot_polygon( im, poly, color, plotTitle, plotIndex ):
    draw = ImageDraw.Draw( im )
    
    for e in poly['edges']:
        p1 = tuple( poly['points'][ e[0] ] )
        p2 = tuple( poly['points'][ e[1] ] )
        draw.line( [p1, p2], fill = color )

    del draw

    plt.subplot( 3, 2, plotIndex ),
    plt.imshow( im ),
    plt.title( plotTitle ),
    plt.xticks([]), plt.yticks([])

    # Draw point names (ABCD)
    for i, c in enumerate( poly['points'] ):
        plt.text( c[0], c[1], "ABCD"[i], color = 'white' )

# Define polygon as dictionary of point coordinates and edges
# each edge is a pair of point indices
p = {
    'points' : [ (50,10), (95,30), (80,20), (62,48) ],
    'edges'  : [ (3,0), (3,1), (1,2), (2,0) ]
}

xVec = [1,0] # Horizontal axis

# Draw original poly in white
im = Image.new( 'RGB', (100,100) )
draw_and_plot_polygon( im, p, (255,255,255), 'Original', 1 )

colors = [ (50,50,255), (255,0,0), (0,255,0), (200, 150, 50) ]

i = 2
for e, color in zip( p['edges'], colors ):
    edgeVec = calc_edge_vec( p, e )
    a       = angle( edgeVec, xVec )

    rotPol = p.copy()
    rotPol['points'] = rotatePolygon( p['points'], a )

    # Draw rotated polygon
    im = Image.new( 'RGB', (100,100) )
    angleTitle = "Angle: " + str( round( degrees(a), 2 ) )
    draw_and_plot_polygon( im, rotPol, color, angleTitle, i )

    i += 1

plt.show()
