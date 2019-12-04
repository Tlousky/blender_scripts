import bpy, cv2, os, sys
import numpy as np
from os.path import join, dirname

SRC = r'C:\Users\tfc64\\Documents\GitHub\blender_scripts\image_to_gp'
sys.path.append( SRC )

from gp_utils import get_grease_pencil, get_grease_pencil_layer, init_grease_pencil, draw_contour

# CONFIGURATION
fp = r'E:\Drive\Google Photos\IMG-20170529-WA0000.jpg'
cntLenThresh = 10
mint, maxt   = 20, 225
nlevels      = 7

# READ IMAGE
im = cv2.imread(fp)

imgray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
blur   = cv2.GaussianBlur(imgray, (11,11), 0)

# FIND CONTOURS
contours_all = []
threshvals = np.linspace( mint, maxt, num = nlevels, dtype = np.int )
for t in threshvals:
    ret, thresh = cv2.threshold(blur, t, 255, 0)
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours_all.extend(contours)

contours_all = sorted( contours_all, key = len, reverse = True )
fcnt         = [ c for c in contours_all if len(c) > cntLenThresh ]

# DRAW GP CURVES BASED ON CONTOURS IN CURRENT FRAME
gp_layer = init_grease_pencil()
gp       = get_grease_pencil()
gp_frame = gp_layer.frames.new(0)

# CALCULATE MEAN COLOR AND CREATE GP STROKES
bpy.context.view_layer.objects.active = gp

cntcolors = []
for i, cnt in enumerate(fcnt):
    mask    = np.zeros(imgray.shape, np.uint8)
    mask    = cv2.drawContours( mask, [cnt], -1, (255), 1 )
    maskbin = np.array( mask, np.bool )
    px      = im[ maskbin ]
    meanbgr = np.mean( px, axis = 0, dtype = np.float )[::-1] / 255
    cntcolors.append(meanbgr)

    # Create new material
    m = bpy.data.materials.new(f"gpmat_{str(i).zfill(3)}")
    bpy.data.materials.create_gpencil_data(m)
    m.grease_pencil.show_fill  = True
    m.grease_pencil.fill_color = tuple( list(meanbgr) + [1] )
    
    # Add new material slot and set material
    bpy.ops.object.material_slot_add()
    material_index = len(gp.material_slots) - 1
    gp.material_slots[material_index].material = m    

    # Draw contour as GP stroke
    gp_stroke = draw_contour(gp_frame, cnt, material_index )