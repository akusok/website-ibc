# -*- coding: utf-8 -*-
"""
Created on Thu Sep  5 12:11:12 2013

@author: akusoka1
"""

from PIL import Image
from leargist import color_gist
import numpy as np


def get_gist(fname):
    """Get GIST image descriptor (image reshaped to square).
    """
    try:
        im = Image.open(fname)
    except IOError:
        # cannot open image
        print "cannot open: %s" % fname
        return np.ones((960,)) * -1        
    # resize to square image, for non-square GIST does not make sense
    s = im.size
    if s[0] != s[1]:
        d = np.min(im.size)
        im = im.resize((d,d), Image.ANTIALIAS)
    # calculate gist
    try:
        gist = color_gist(im)
    except: # something goes wrong, i.e. too small image
        print "error calculating gist:"
        return np.ones((960,)) * -1    
    return gist

#if __name__ == "__main__":
#    gist = get_gist("/users/akusoka1/local/spiiras_test/websites/3/c9cb88b60add5172abcf4330430780aef02fa911.jpg.jpg")
#    print gist.shape
