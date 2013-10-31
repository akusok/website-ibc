# -*- coding: utf-8 -*-
"""Converts images, returns all information.

Created on Mon Sep 16 14:58:13 2013

@author: akusoka1
"""
from wibc.config.wibc_config import cf
import os
from PIL import Image
import hashlib


def add_website(imglist, out_folder):
    """
    imglist -- list of images with paths
    out_folder -- folder for the given website with processed images
    """    
        
    # creating image folder    
    os.makedirs(out_folder)
    
    # start gathering output
    ws = {}
    ws['img_present'] = len(imglist)    
    ws['img_count'] = 0
    ws['folder'] = out_folder
    ws['images'] = []
    
    # processing images
    img_index = 0  # for saving new images
    for img_raw in imglist:
        # try to open, check file size
        try:
            if os.stat(img_raw).st_size < cf._min_size:
                #print "image too small"
                continue
            # if opened successfully == proper image
            img_obj = Image.open(img_raw).convert('RGB')
        except IOError:
            #print "error opening ", img_raw
            continue
        except:
            print "Unknown image opening/converting exception"
            continue
            
        img = {}  # new image record
        img['true_size'] = img_obj.size
        img['true_name'] = img_raw
        img['sha1'] = hashlib.sha1(open(img_raw, 'r').read()).hexdigest()
        
        # check image dimensions, resize if needed
        maxs = cf._max_dim
        (x, y) = img_obj.size
        if (x > maxs) and (x >= y):
            y = int(y * (float(maxs) / x))
            x = maxs
            img_obj = img_obj.resize((x, y), Image.ANTIALIAS)
        elif y > maxs:
            x = int(x * (float(maxs) / y))
            y = maxs
            img_obj = img_obj.resize((x, y), Image.ANTIALIAS)        
        img['new_size'] = img_obj.size
    
        # saving preprocessed image
        img_new = os.path.join(out_folder, "%d.jpg" % img_index)
        try:
            img_obj.save(img_new, 'JPEG', quality=cf._jpeg_quality)
        except:
            print "Error saving image"
            continue
        img['new_name'] = img_new
        img_index += 1

        # appending image data to output
        ws['images'].append(img.copy())
        ws['img_count'] += 1
    
    return ws






















































