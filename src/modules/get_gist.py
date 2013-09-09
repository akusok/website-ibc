# -*- coding: utf-8 -*-
"""Processes an image and returns all data (properties + descriptors).

If something goes wrong, returns string describing the error.
"""

from wibc_config import IBCConfig as cf
from mp.mp_master import MPMaster
from tables import openFile
import numpy as np
import cPickle
from PIL import Image
import os
import time


class Master(MPMaster):
    """Implements "get_new_task" and "process_result" of Master class.
    """

    def __init__(self, kill_workers):
        super(Master, self).__init__(kill_workers, profiling=False)

        self.tasks = []   
        # preparing for job generation
        if cf._mode == "hdf5":
            self.hdf5 = openFile(cf._hdf5, "a")
            self.Images = self.hdf5.root.Images
            self.Gist = self.hdf5.root.GIST
            # gathering a list of tasks
            for row in self.Images.iterrows():
                self.tasks.append((row["index"], row["true_name"]))
        else:
            raise NotImplementedError
            #self.img_data = []
            #imglist = cPickle.load(open(cf._img_data, "rb"))
            #for item in imglist:
                # here using ("url", "filename") instead of "index" in hdf5,
                # because we need both filename and url later on
            #    self.tasks.append(((item[1], item[0]), item[0]))       
        
        # initializing reporting part
        self.task_max = len(self.tasks)
        self.task_curr = self.task_max


    def __del__(self):
        if cf._mode == "hdf5":
            self.hdf5.close()
            
        
    def get_new_task(self):
        """Combines a new task.
        """
        # just yielding tasks here
        for idx, true_name in self.tasks:
            imgf = ''.join(['/data/r0/spiiras_train',
                            true_name[29:],'.jpg'])
            yield ("gist", imgf, idx)

    
    '''def _process_result(self, result, flush):
        """Demo mode, save output as is.
        """
        data, (url, filename) = result
        for i in xrange(len(data["regions"])):
            r = data["regions"][i]
            r.append(url)  # hide url in parameters list
            d = data["descriptors"][i]
            self.img_data.append([filename, r, d])

        if flush:
            cPickle.dump(self.img_data, open(cf._img_data, "wb"), -1)     
    '''
    
    def _process_result_hdf5(self, result, flush):
        """Batch mode, write output to HDF5 file.
        """
        gist, idx = result
        if not gist == []:
            #gist = np.reshape(np.array(gist), (1,960))
            #print gist.shape
            self.Gist.modify_column(idx, idx+1, column=gist, colname="data")
        if flush:
            self.Gist.flush()
    
    
    def process_result(self, result, flush):
        """Choose between batch and demo mode.        
        """
        self.task_curr -= 1
        if cf._mode == "hdf5":
            self._process_result_hdf5(result, flush)
        #else:
        #    self._process_result(result, flush)
        
        

def calc_gist(kill_workers):
    """Actually starts and stops mp master.
    """
    if cf._show_progress:
        print "Extracting descriptors..."
    master = Master(kill_workers)
    time.sleep(1)
    master.start()
    master.join()











