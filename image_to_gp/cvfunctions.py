import cv2
import numpy as np
from os.path import join, dirname, isfile

# CUSTOM EXCEPTIONS AND WARNINGS
class NoContoursFound(Warning):
    """ Exception class to raise when no contours were found in the image"""
    
class EmptyContour(Warning):
    """ Exception class to raise when proivided contour bind no pixels"""

# FUNCTIONS
def find_contours( filepath, contour_len_thresh, nlevels, min_val, max_val ):
    if not isfile( filepath ):
        raise FileExistsError(f'Image file [{filepath}] does not exist')

    im = cv2.imread(filepath)

    imgray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    blur   = cv2.GaussianBlur(imgray, (11,11), 0)

    # FIND CONTOURS
    contours_all = []
    threshvals = np.linspace( min_val, max_val, num = nlevels, dtype = np.int )
    for t in threshvals:
        ret, thresh = cv2.threshold(blur, t, 255, 0)
        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours_all.extend(contours)

    if not len( contours_all ):
        raise NoContoursFound(f'Failed to find contours in image file [{filepath}]')

    contours_all = sorted( contours_all, key = len, reverse = True )
    fcnt         = [ c for c in contours_all if len(c) > contour_len_thresh ]
    
    if not len( contours_all ):
        raise NoContoursFound(f'Failed to find contours with len > {contour_len_thresh} in image file [{filepath}]')
    
    return im, fcnt

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