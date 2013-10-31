# -*- coding: utf-8 -*-
"""Calculates and returns cSIFT descriptors of an image.

Created on Thu Sep 19 11:53:55 2013

@author: akusoka1
"""

from wibc.config.wibc_config import cf
from wibc.sift.DescriptorIO import readDescriptors
import numpy as np
import os
import tempfile
import shutil  # to remove directory with subdirectories


def csift(imglist):
    """Calculates and returns descriptors of one or several images.
    
    Uses binary software and temporary folders.
    imglist -- list of (image_file_name, image_index) 
    """    

    results = []
    for img_file, img_index in imglist:
        # extracting descriptors, dropping console output
        # works for LINUX
        temp_file = tempfile.mktemp(dir=cf._fast_dir)
        # run command with no spamming to terminal
        command = ('%s %s --detector harrislaplace --descriptor csift '
                   '--output %s --outputFormat binary '
                   '--keepLimited %d > /dev/null'
                   % (cf._cD_bin, img_file, temp_file, cf._max_reg))    
        os.system(command)  # running "colorDescriptors" for one image, one thread

        # reading data        
        regions, descriptors = readDescriptors(temp_file)
        if regions.shape[1] == 5:  # if there are local features
            for reg, des in zip(regions, descriptors):            
                lf = {}
                lf['image_idx'] = img_index
                lf['data'] = np.asarray(des, dtype=np.uint8)                
                lf['center'] = np.int64(reg[:2])  # center              
                lf['radius'] = np.int64(reg[2]*8.4853)  # radius                
                lf['cornerness'] = np.float64(reg[4])  # cornerness                 
                results.append(lf.copy())
                
        # delete temp file        
        os.remove(temp_file)
        
    return results
        