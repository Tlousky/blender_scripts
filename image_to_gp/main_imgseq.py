import bpy, cv2, os, sys, time, datetime
import numpy as np
from os.path import join, dirname
from pathlib import Path
from tqdm import tqdm

#SRC = r'C:\Users\tfc64\\Documents\GitHub\blender_scripts\image_to_gp'
SRC = '/Users/tlousk/Documents/code/blender_scripts/image_to_gp'
sys.path.append( SRC )

from gp_utils import get_grease_pencil, get_grease_pencil_layer, init_grease_pencil, draw_contour
from cvfunctions import find_contours_canny, find_contour_color

# CONFIGURATION
#dirpath = '/Users/tlousk/Documents/test_images'
dirpath = '/Users/tlousk/Downloads/Bacteriophage_Freestyle'


nFrames      = 121
cntLenThresh = 5
mint, maxt   = 50, 220
nlevels      = 12
stroke       = False
fill         = True
imgwidth     = 720

start = time.time()

d = Path( dirpath )
imgs = sorted([ str( f.absolute() ) for f in d.glob('*.png') ])[:nFrames]

gp_layer = init_grease_pencil()
gp       = get_grease_pencil()

pbar = tqdm( imgs, ncols = 100 )
for i, fp in enumerate( pbar ):
    im, contours = find_contours_canny( fp, nlevels = nlevels, resize_to = imgwidth )

    # DRAW GP CURVES BASED ON CONTOURS IN CURRENT FRAME
    gp_frame = gp_layer.frames.new(i)

    # CALCULATE MEAN COLOR AND CREATE GP STROKES
    bpy.context.view_layer.objects.active = gp

    cntcolors = []
    for i, cnt in enumerate(contours):
        # Change y coords from y-down to y-up
        h = im.shape[0]
        #cnt[:,0,1] = h - cnt[:,0,1] 

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

total_time = time.time() - start
timefor    = str(datetime.timedelta(seconds=total_time ))
print( f"Elapsed: {timefor} with {nlevels} levels" )