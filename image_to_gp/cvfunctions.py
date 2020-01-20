import cv2, sys
import numpy as np
from os.path import join, dirname, isfile

# CUSTOM EXCEPTIONS AND WARNINGS
class NoContoursFound(Warning):
    """ Exception class to raise when no contours were found in the image"""
    
class EmptyContour(Warning):
    """ Exception class to raise when proivided contour bind no pixels"""

# FUNCTIONS
def find_contours( filepath, contour_len_thresh, nlevels, min_val, max_val, resize_to = None ):
    if not isfile( filepath ):
        raise FileExistsError(f'Image file [{filepath}] does not exist')

    im = cv2.imread(filepath)
    
    scaled = im
    if resize_to is not None:
        h, w, c  = im.shape
        ratio    = w / resize_to
        new_size = tuple([ int(round(v / ratio)) for v in [ im.shape[1], im.shape[0] ] ])
        scaled   = cv2.resize(im, new_size )

    dst = cv2.edgePreservingFilter(scaled, sigma_s=20, sigma_r=0.95)
        
    imgray = cv2.cvtColor(dst, cv2.COLOR_BGR2GRAY)
    blur   = cv2.GaussianBlur(imgray, (9,9), 0)

    # FIND CONTOURS
    contours_all = []
    layers_all   = []
    threshvals = np.linspace( min_val, max_val, num = nlevels, dtype = np.int )
    for t in threshvals:
        ret, thresh = cv2.threshold(blur, t, 255, 0)
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        order = [ v for i in sorted(set(hierarchy[0,:,3])) for v in np.where(hierarchy[0,:,3] == i)[0]  ]
        layers = (hierarchy[0,:,3]+1) + (hierarchy[0,:,0]+1)
        contours_all.extend([ contours[i] for i in order ])
        layers_all.extend(layers)

    if not len( contours_all ):
        raise NoContoursFound(f'Failed to find contours in image file [{filepath}]')

    #merged        = list( zip(contours_all, layers_all))
    #merged_sorted = sorted( merged, key = lambda m: m[1], reverse = False ) 
    #contours_all  = [ m[0] for m in merged_sorted ]
    #contours_all  = 
    fcnt = [ c for c in contours_all if len(c) > contour_len_thresh ]
    
    if not len( contours_all ):
        raise NoContoursFound(f'Failed to find contours with len > {contour_len_thresh} in image file [{filepath}]')
    
    return dst, fcnt

def find_contour_color(im, cnt, default_color = (0,0,0,1) ):
    mask    = np.zeros(im.shape[:-1], np.uint8)
    mask    = cv2.drawContours( mask, [cnt], -1, (255), 1 )
    maskbin = np.array( mask, np.bool )
    
    if not sum( maskbin.ravel() ):
        raise EmptyContour('Empty contour')
        return default_color
    
    px      = im[ maskbin ]
    meanrgb = np.mean( px, axis = 0, dtype = np.float )[::-1] / 255
    
    return meanrgb