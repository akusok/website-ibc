# -*- coding: utf-8 -*-
"""Script to start and stop multiprocessing part.

All niuances are kept here, like 2 cores per process in SIFT stage
and  1 core per process in NN stage.

Created on Wed Jun 26 14:23:12 2013
"""

from wibc_config import IBCConfig as cf
from mp_worker import MPWorker
from subprocess import Popen
import time

wrk = []
mng = None

def mp_start():
    """Starting mutiprocessing manager.
    """
    global mng
    global wrk
    mng = Popen(["python", cf._ibc + "mp/mp_manager.py"])
    mng.poll()
    time.sleep(1)  # time to create "hostname.txt" file
    # starting parallel workers
    for i in xrange(cf._nr_wrk/2):
        wrk.append(MPWorker(i))
        wrk[-1].start()
        time.sleep(0.1)

def mp_boost_nn():
    """Add workers for NN here.
    
    Because too many workers crash feature extraction.
    """
    global wrk
    for i in xrange(cf._nr_wrk - cf._nr_wrk/2):  # rest of the workers
        wrk.append(MPWorker(i))
        wrk[-1].start()
        time.sleep(0.1)

def mp_finalize():
    """Terminating multiprocessing part.
    """
    for w in wrk:
        w.join()
    mng.terminate()
