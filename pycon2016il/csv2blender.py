import bpy
import csv
from math import radians

fPath   = 'C:/Users/TLOUSKY/Google Drive/Work/invertex/PyCon2016IL/examples/sales.csv'
csvFile = csv.reader( open( fPath ) )
data    = [ row for row in csvFile ][1:]

allSales = sum([ int( row[1] ) for row in data ])
for i, row in enumerate( data ):
    date, sales = row

    # Set cube physical height as proportion of this sale from the total X 10
    saleHeight = ( int( sales ) / allSales ) * 10
    
    # Add cube (box) object
    bpy.ops.mesh.primitive_cube_add( 
        radius   = 0.5,      # Set base size
        location = ( 
            i * 1.1,         # X = current sale's index with a small gap
            0,               # Y = 0. All cubes are aligned in a straight line along the X axis.
            saleHeight / 2   # Z = half the height
        )
    )
       
    cube = bpy.context.object
    cube.dimensions.z = saleHeight # Set the cube's height

    # Add text object
    bpy.ops.object.text_add(
        location = ( i * 1.1, 1, 0 )
    )
    
    text = bpy.context.object
    text.rotation_euler.z = radians(90) # Rotate text by 90 degrees along Z axis
    text.data.extrude     = 0.05        # Add depth to the text
    text.data.bevel_depth = 0.01        # Add a nice bevel effect to smooth the text's edges
    text.data.body        = date        # Set the text to be the current row's date