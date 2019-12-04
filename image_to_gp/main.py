import bpy, cv2, os, sys, time
import numpy as np
from os.path import join, dirname

#SRC = r'C:\Users\tfc64\\Documents\GitHub\blender_scripts\image_to_gp'
SRC = '/Users/tlousk/Documents/code/blender_scripts/image_to_gp'
sys.path.append( SRC )

from gp_utils import get_grease_pencil, get_grease_pencil_layer, init_grease_pencil, draw_contour
from cvfunctions import find_contours, find_contour_color

# CONFIGURATION
fp = '/Users/tlousk/Google Drive/Documents/Hellscore/bass_fish_clef.jpg'
cntLenThresh = 10
mint, maxt   = 20, 225
nlevels      = 5
stroke       = False
fill         = True

start = time.time()
im, contours = find_contours( fp, cntLenThresh, nlevels, mint, maxt )

# DRAW GP CURVES BASED ON CONTOURS IN CURRENT FRAME
gp_layer = init_grease_pencil()
gp       = get_grease_pencil()
gp_frame = gp_layer.frames.new(0)

# CALCULATE MEAN COLOR AND CREATE GP STROKES
bpy.context.view_layer.objects.active = gp

cntcolors = []
for i, cnt in enumerate(contours):

    # Create new material
    m = bpy.data.materials.new(f"gpmat_{str(i).zfill(3)}")
    bpy.data.materials.create_gpencil_data(m)
    m.grease_pencil.show_fill   = fill
    m.grease_pencil.show_stroke = stroke

    if fill:
        color = find_contour_color( im, cnt )
        cntcolors.append(color)
        m.grease_pencil.fill_color = tuple( list(color) + [1] )
    
    # Add new material slot and set material
    bpy.ops.object.material_slot_add()
    material_index = len(gp.material_slots) - 1
    gp.material_slots[material_index].material = m    

    # Draw contour as GP stroke
    gp_stroke = draw_contour(gp_frame, cnt, material_index )
    
print( f"Elapsed: {time.time() - start} seconds with {nlevels} levels and {len(contours)} contours" )