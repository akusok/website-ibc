# -*- coding: utf-8 -*-
"""Creates .h5 file, and fills websites in it.

Created on Thu Jun 20 14:07:34 2013
"""

from tables import openFile
from hdf5_config import *

def create_empty_hdf5(fname, exp_img_count=1000000):
    """Builds an empty HDF5 file having the given tables.
  
    fname -- name of a new HDF5 file
    exp_img_count -- expected maximum number of images, roughly
    """    
    ic = exp_img_count
    # database file    
    dnew = openFile(fname, 'w')

    # websites
    WsNew = dnew.createTable(dnew.root, 'Websites', WebsitesRecord,
                             expectedrows=ic/10)
    WsNew.attrs.last_index = -1
    WsNew.cols.class_idx.createCSIndex()

    # images
    ImNew = dnew.createTable(dnew.root, "Images", ImagesRecord,
                             expectedrows=ic)
    ImNew.attrs.last_index = -1
    ImNew.cols.index.createCSIndex()
    ImNew.cols.class_idx.createCSIndex()        
    ImNew.cols.site_idx.createCSIndex()
    
    # cSIFT
    f1 = dnew.createTable(dnew.root, 'cSIFT', cSIFTRecord, 
                          expectedrows=ic*250)
    f1.attrs.last_index = -1
    f1.cols.image_idx.createCSIndex()
    f1.cols.site_idx.createCSIndex()
    f1.cols.class_idx.createCSIndex()
    
    # cSIFT_nn
    f2 = dnew.createTable(dnew.root, 'cSIFT_nn', cSIFT_nnRecord, 
                          expectedrows=ic*250)
    f2.attrs.last_index = -1
    f2.cols.image_idx.createCSIndex()
    f2.cols.feature_idx.createCSIndex()
    
    #cSIFT_hist
    f3 = dnew.createTable(dnew.root, 'cSIFT_hist', cSIFT_histRecord, 
                          expectedrows=ic)
    f3.attrs.last_index = -1
    f3.cols.image_idx.createCSIndex()

    # closing file to enable its re-opening
    dnew.close()
    
   
    
    
    
    
