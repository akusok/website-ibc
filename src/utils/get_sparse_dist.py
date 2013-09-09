# -*- coding: utf-8 -*-
"""Processes an image and returns all data (properties + descriptors).

If something goes wrong, returns string describing the error.
"""

from wibc_config import IBCConfig as cf
from mp.mp_master import MPMaster
from mp.mp_worker import MPBaseWorker
from nn.sift_pdist import get_dist
from tables import openFile
from subprocess import Popen
import time
import numpy as np
import cPickle
import os


class Worker(MPBaseWorker):
    """Calculates nearest descriptors.
    """

    def __init__(self, wrk_idx):
        """Loads descriptors into memory, they are small (422MB).
        """
        super(Worker, self).__init__(wrk_idx)
        self.descr = cPickle.load(open(cf._nm_descr, "rb"))
    
    def _process_task(self, task):
        """Calculates closest 1000 descriptors.
        
        Input:
          task[0] = query descriptor P
          task[1] = start:stop indexes of reference descriptors
          task[2] = position of descriptor P, jsut copied to result[2]
        
        Output:
          result[0] = K closes descriptors indexes with distances
          result[1] = mean and std of distance distribution
          result[2] = task[2], position of query descriptor
        """
        P = task[0]
        # task[1] are start:stop batch indexes
        Q = self.descr[task[1][0]:task[1][1], :]
        data = get_dist(P, Q, cf._nm_K)
        nn = np.vstack((data[0], data[1])).T
        result = (nn, data[2], task[2])
        return result


class Master(MPMaster):
    """Implements "get_new_task" and "process_result" of Master class.
    """

    def __init__(self, kill_workers):
        super(Master, self).__init__(kill_workers, profiling=False)

        # preparing for job generation
        self.hdf5 = openFile(cf._nm_hdf5, "a")
        #self.NN = self.hdf5.root.NN
        self.descr = cPickle.load(open(cf._nm_descr, "rb"))
        
        # initializing reporting part
        self.task_max = cf._nm_N * (cf._nm_N / cf._nm_batch) + 1
        self.task_curr = self.task_max


    def __del__(self):
        #self.hdf5.close()
        pass
            
    
    def get_new_task(self):
        """Assembles a multiprocessing task.
        """
        # just yielding tasks here
        N = cf._nm_N
        B = cf._nm_batch
        for pI in xrange(N):
            for b in xrange(0, N, B):
                i0 = b
                i1 = min(b+B, N)
                d = self.descr[pI,:]
                task = [d, (i0,i1), pI]
                self.task_curr -= 1
                yield task
            break
    
    def process_result(self, result, flush):
        """Merge and write output to HDF5 file.
        """
        data1, distr, pI = result
        # updating regions records
        data0 =  self.hdf5.root.NN.read(pI)[0]  # [0] to remove 3rd axis
        data = np.vstack((data0, data1))
        idx = np.argsort(data[:,1])
        data = data[idx < cf._nm_K, :]
        self.hdf5.root.NN[pI] = data  

        # flush results every once a while
        if flush:
            self.hdf5.root.NN.flush()            

        
        

def calc_neigh_matrix(kill_workers=True):
    """Starts and stops mp master to get NN.
    """
    
    wrk = []
    mng = None
    
    mng = Popen(["python", cf._ibc + "mp/mp_manager.py"])
    mng.poll()
    time.sleep(1)  # time to create "hostname.txt" file
    # starting parallel workers
    for i in xrange(cf._nr_wrk):
        wrk.append(Worker(i))
        wrk[-1].start()


    master = Master(kill_workers)
    if cf._show_progress:
        print "Calculating nearest neighbours..."
    master.start()
    master.join()


    """Terminating multiprocessing part.
    """
    for w in wrk:
        w.join()
    mng.terminate()











