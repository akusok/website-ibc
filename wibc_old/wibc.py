# -*- coding: utf-8 -*-
"""
Created on Thu Jun 20 14:02:59 2013

@author: akusoka1
"""

from wibc_config import IBCConfig as cf
from modules.hdf5_creator import init_hdf5, create_empty_hdf5
from modules.img_preprocessor import normalize_images
from modules.get_csift import calc_csift
from modules.get_gist import calc_gist
from modules.get_nn import calc_nn
from modules.img_repr import get_repr
from modules.classifier import train_elm, run_elm
from mp.mp_support import *
from mp.mp_worker import MPWorker
from utils.get_sparse_dist import calc_neigh_matrix
import sys
import cProfile

##############################################################################
print "IBC started"
profiler = cProfile.Profile()
profiler.enable()

#mp_start()
#init_hdf5()
#normalize_images()
#calc_csift(kill_workers=False)
#mp_boost_nn()
calc_gist(kill_workers=True)
#calc_nn(kill_workers=True)
#mp_finalize()
#get_repr(all_repr=True)
#train_elm()
#run_elm(save_txt=True)

#calc_neigh_matrix()

profiler.disable()
profiler.dump_stats(cf._dir + "caltech101.prof")
print "IBC finished"
##############################################################################
sys.exit()  # suicide


