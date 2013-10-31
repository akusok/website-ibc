# -*- coding: utf-8 -*-
"""Setup for an IBC experiment.

Created on Mon Sep 16 15:22:39 2013

@author: akusoka1
"""

__author__ = "Anton Akusok"
__license__ = "PSFL"
__version__ = "0.0.1"
import os
import stat
import ConfigParser


class IBCConfig(object):
    """Global parameters for WIC system.
    """

    def __init__(self):
        """Load ini data into object variables for quick access.
        """
        # open config file
        self._ini = '/'.join(__file__.split('/')[:-2]) + "/config/config.ini"
        #self.reset_defaults()
        self._cp = ConfigParser.ConfigParser()          
        self._cp.read(self._ini)
        
        # check binary cSIFT executable permissions
        cD_bin = '/'.join(__file__.split('/')[:-2]) + '/sift/colorDescriptor'
        st = os.stat(cD_bin)
        os.chmod(cD_bin, st.st_mode | 01111)  # chmod a+x

        #################
        ### load data ###
        #################

        self._min_size = int(self._cp.get("Images","min_size"))
        self._max_dim = int(self._cp.get("Images","max_dim"))
        self._jpeg_quality = int(self._cp.get("Images","jpeg_quality"))

        self._cSIFT = self._cp.get("module cSIFT","Active")
        self._fast_dir = self._cp.get("module cSIFT","fast_dir")
        self._max_reg = int(self._cp.get("module cSIFT","max_reg"))
        self._cD_bin = self._cp.get("module cSIFT","cD_bin")

        self._SIFT_kNN = self._cp.get("module SIFT_kNN","Active")
        if self._cp.get("module SIFT_kNN","Use_SIFT_distance") == "True":
            self._knn_use_sift = True
        else:
            self._knn_use_sift = False
        self._Centroids = self._cp.get("module SIFT_kNN","Centroids")
        self._knn_K = int(self._cp.get("module SIFT_kNN","K"))

        self._SIFT_pdist = self._cp.get("module SIFT_pdist", "Active")
        self._pd_descriptors = self._cp.get("module SIFT_pdist", "Descriptors")
        
        self._nr_wrk = int(self._cp.get("multiprocessing","nr_wrk"))
        self._qsize = int(self._cp.get("multiprocessing","qsize"))
        self._host = self._cp.get("multiprocessing","host")
        self._port = int(self._cp.get("multiprocessing","port"))
        self._key = self._cp.get("multiprocessing","key")
        if self._cp.get("multiprocessing","show_progress") == "True":
            self._show_progress = True
        else:
            self._show_progress = False
    
       
    def reset_defaults(self):
        """Set default values.
        """
        self._cp = ConfigParser.ConfigParser()          
        self._cp.add_section("Images")
        self._cp.set("Images", "min_size", "2400")
        self._cp.set("Images", "max_dim", "500")
        self._cp.set("Images", "jpeg_quality", "95")

        self._cp.add_section("module cSIFT")
        self._cp.set("module cSIFT", "Active", "False")
        fast_dir = "/run/shm"
        self._cp.set("module cSIFT", "fast_dir", fast_dir)
        self._cp.set("module cSIFT", "max_reg", "10000")
        cD_bin = '/'.join(__file__.split('/')[:-2]) + '/sift/colorDescriptor'
        self._cp.set("module cSIFT", "cD_bin", cD_bin)

        self._cp.add_section("module SIFT_kNN")
        self._cp.set("module SIFT_kNN", "Active", "False")
        self._cp.set("module SIFT_kNN","Use_SIFT_distance", "False")
        self._cp.set("module SIFT_kNN", "Centroids", "none")
        self._cp.set("module SIFT_kNN", "K", "100")

        self._cp.add_section("module SIFT_pdist")
        self._cp.set("module SIFT_pdist", "Active", "False")
        self._cp.set("module SIFT_pdist", "Descriptors", "none")
        
        self._cp.add_section("multiprocessing")
        self._cp.set("multiprocessing", "nr_wrk", "8")
        self._cp.set("multiprocessing", "qsize", "100")
        self._cp.set("multiprocessing", "host", "%s/hostname.txt" % fast_dir)
        self._cp.set("multiprocessing", "port", "50763")
        self._cp.set("multiprocessing", "key", "WIBC")
        self._cp.set("multiprocessing", "show_progress", "True")

        self._cp.add_section("other")  # for other variables
        with open(self._ini, "wb") as cfgfile:
            self._cp.write(cfgfile)
    
    def set_value(self, section, variable, value):
        """Modify value or add a new one.
        """
        self._cp.set(section, variable, str(value))
        with open(self._ini, "wb") as cfgfile:
            self._cp.write(cfgfile)
        
cf = IBCConfig()        
        
        

""" OLD DATA:
    
    # Images
    _min_size = 2400
    _max_dim = 500
    _jpeg_quality = 95
    
    # cSIFT
    _fast_dir = '/run/shm'
    _max_reg = 10000  # maximum number of regions
    _cD_bin = '/'.join(__file__.split('/')[:-2]) + '/sift/colorDescriptor'

    # check executable mod
    st = os.stat(_cD_bin)
    os.chmod(_cD_bin, st.st_mode | 01111)  # chmod a+x

    # multiprocessing config
    _nr_wrk = 8  # a good guess is the number of cores - 1
    _qsize = 100  # maximum size of a queue, to limit memory consumption
    _host = os.path.join(_fast_dir, "hostname.txt")
    _port = 50763
    _key = "WIBC"
    _show_progress = True
"""















