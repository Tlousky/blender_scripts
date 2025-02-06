import bpy, cv2, os, sys, time, datetime
import numpy as np
from os.path import join, dirname
from pathlib import Path
from tqdm import tqdm

SRC = '/Users/tlousk/Documents/code/blender_scripts/image_to_gp'
sys.path.append( SRC )

from gp_utils import get_grease_pencil, get_grease_pencil_layer, init_grease_pencil, draw_contour
from cvfunctions import find_contours_canny, find_contour_color

# CONFIGURATION
fp = '/Users/tlousk/Documents/test_images/character/anime_char.png'

nlevels      = 7
imgwidth     = 720
fill         = True
stroke       = True
scale_to     = 5

def main(fp):
    start = time.time()

    gp_layer = init_grease_pencil()
    gp       = get_grease_pencil()

    im, contours = find_contours_canny( fp, nlevels = nlevels, resize_to = None )
    #im, contours = find_contours( fp, nlevels = nlevels, resize_to = imgwidth )

    # DRAW GP CURVES BASED ON CONTOURS IN CURRENT FRAME
    gp_frame = gp_layer.frames.new(1)

    # CALCULATE MEAN COLOR AND CREATE GP STROKES
    bpy.context.view_layer.objects.active = gp

    h = im.shape[0]
    pbar = tqdm(contours)
    for i, cnt in enumerate(pbar):
        # Change y coords from y-down to y-up
        cnt[:,0,1] = h - cnt[:,0,1]    

        # Create new material
        m = bpy.data.materials.new(f"gpmat_{str(i).zfill(3)}")
        bpy.data.materials.create_gpencil_data(m)
        m.grease_pencil.show_fill   = fill
        m.grease_pencil.show_stroke = stroke

        if fill:
            color = find_contour_color( im, cnt )
            m.grease_pencil.fill_color = tuple( list(color) + [1] )

        # Add new material slot and set material
        bpy.ops.object.material_slot_add()
        material_index = len(gp.material_slots) - 1
        gp.material_slots[material_index].material = m    

        # Draw contour as GP stroke
        gp_stroke = draw_contour(gp_frame, cnt, material_index )

    # Scale GP object
    scale = scale_to / h
    gp.scale = [scale]*3

if __name__ == "__main__":
    main(fp)