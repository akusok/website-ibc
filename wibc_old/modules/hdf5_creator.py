# -*- coding: utf-8 -*-
"""Creates .h5 file, and fills websites in it.

Created on Thu Jun 20 14:07:34 2013
"""

from config.config_hdf5 import *
from wibc_config import IBCConfig as cf
from os.path import join
import os


def create_empty_hdf5(fname=cf._hdf5):
    """Builds an empty HDF5 file having the given tables.
    """    
    dnew = openFile(fname, 'w')

    WsNew = dnew.createTable(dnew.root, 'Websites', WebsitesRecord,
                             expectedrows=100000)
    WsNew.attrs.last_index = -1
    WsNew.cols.classN.createCSIndex()

    ImNew = dnew.createTable(dnew.root, "Images", ImagesRecord,
                             expectedrows=1000000)
    ImNew.attrs.last_index = -1
    ImNew.attrs.nr_in_class = np.zeros((cf._maxc,))
    ImNew.cols.site_index.createCSIndex()
    ImNew.cols.index.createCSIndex()        
    
    RgNew = dnew.createTable(dnew.root, 'Regions', RegionsRecord,
                             expectedrows=500000000)
    RgNew.attrs.last_index = -1
    RgNew.cols.img_index.createCSIndex()
        
    DsNew = dnew.createTable(dnew.root, 'Descriptors', DColorSIFTRecord,
                             expectedrows=500000000)
    DsNew.attrs.last_index = -1
    DsNew.cols.index.createCSIndex()
    DsNew.cols.classN.createCSIndex()
    DsNew.autoIndex = True  
    
    GistNew = dnew.createTable(dnew.root, 'GIST', DGISTRecord,
                               expectedrows=1000000)
    GistNew.cols.index.createCSIndex()
    GistNew.cols.classN.createCSIndex()

    dnew.close()
    
    
def init_hdf5():
    """Fills websites into an empty HDF5.
    """
    if cf._mode != "hdf5":
        return
    create_empty_hdf5()

    db = openFile(cf._hdf5, "a")    
    wdf = open(cf._ws_descr, "r")
    Websites = db.root.Websites
    for ws in wdf:
        d1,url,cl = ws.split(";")
        cl = int(cl)
        d1 = join(cf._raw_dir, d1)
        nfiles = 0
        for root,dirs,files in os.walk(d1):
            nfiles += len(files)
        # add website record        
        index = Websites.attrs.last_index + 1
        row = Websites.row
        row['index'] = index
        row['classN'] = cl
        row['folder'] = d1
        row['url'] = url
        row['img_count'] = nfiles
        row.append()
        Websites.attrs.last_index = index
    Websites.flush()    
    db.close()
    

    
    
    
    
