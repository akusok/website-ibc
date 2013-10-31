# -*- coding: utf-8 -*-
"""Website Image-based Classification wrapper, using HDF5 database.

Created on Mon Sep 16 13:40:20 2013

@author: akusoka1
"""

from hdf5.hdf5_tools import create_empty_hdf5
from modules.add_website import add_website
from modules.get_csift import csift
from tables import openFile
import numpy as np
import os, stat


class wibc_hdf5(object):
    
    def __init__(self, hdf5_file):
        """Connects to a mandatory HDF5 database.
        """
        if not os.path.isfile(hdf5_file):
            create_empty_hdf5(hdf5_file)
        self.h5 = openFile(hdf5_file, "a")
        

    def __del__(self):
        """Closing HDF5 database nicely.
        """
        self.h5.close()


    def add_website(self, imglist, imgfolder, class_idx=-1, wsparam={}):
        """Adds websites and images to db, preprocesses images.
        
        imglist -- list of images as paths
        imgfolder -- folder with subfolders for each website,
                     containing preprocessed images
        class_idx -- index of true class
        wsparam -- other parameters:
            "class_text"
            "url" 
        """
        WsRec = self.h5.root.Websites
        data = add_website(imglist, imgfolder)
        
        # create website record
        wsrow = WsRec.row
        wsindex = WsRec.attrs.last_index + 1
        wsrow['index'] = wsindex
        WsRec.attrs.last_index += 1
        wsrow['class_idx'] = class_idx
        wsrow['img_count'] = data['img_count']
        wsrow['img_present'] = data['img_present']
        wsrow['folder'] = data['folder']
        # add other custom attributes
        for key,value in wsparam.items():
            if key in WsRec.colnames:
                wsrow[key] = value
        wsrow.append()
        WsRec.flush()

        # add image records
        ImgRec = self.h5.root.Images
        for imgdata in data['images']:
            imgrow = ImgRec.row
            imgrow['index'] = ImgRec.attrs.last_index + 1
            ImgRec.attrs.last_index += 1
            imgrow['class_idx'] = class_idx
            imgrow['site_idx'] = wsindex
            imgrow['orig_sha1'] = imgdata['sha1']
            imgrow['true_size'] = imgdata['true_size']
            imgrow['new_size'] = imgdata['new_size']
            imgrow['true_name'] = imgdata['true_name']
            imgrow['new_name'] = imgdata['new_name']
            imgrow.append()
        ImgRec.flush()
        
        
    def get_csift(self, img_idx):
        """Calculate cSIFT and corresponding attributes for some images.
        
        Now for one image at a time, but 'csift' can do several.        
        
        img_idx -- index of image from database.
        """
        img = self.h5.root.Images.readWhere('index == %d' % img_idx)
        imglist = [(img['new_name'][0], img['index'][0])]
        
        image_idx = img['index'][0]
        site_idx = img['site_idx'][0]        
        class_idx = img['class_idx'][0]        
                        
        data = csift(imglist)
        cSIFT = self.h5.root.cSIFT
        for lf in data:
            row = cSIFT.row
            row['index'] = cSIFT.attrs.last_index + 1
            cSIFT.attrs.last_index += 1
            row['data'] = lf['data']
            row['image_idx'] = image_idx
            row['site_idx'] = site_idx
            row['class_idx'] = class_idx
            row['center'] = lf['center']
            row['radius'] = lf['radius']
            row['cornerness'] = lf['cornerness']
            row.append()
        cSIFT.flush()





































































                
        
        











