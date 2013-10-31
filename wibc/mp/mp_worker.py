# -*- coding: utf-8 -*-
"""Input/Output multiprocessing module, hdf5 storage.


Created on Sat Apr  6 21:01:26 2013
"""


from wibc.config.wibc_config import cf
from wibc.modules.add_website import add_website
from wibc.modules.get_csift import csift
from wibc.modules.sift_pdist import sift_pdist
from wibc.modules.sift_knn import sift_knn
from multiprocessing.managers import BaseManager
from multiprocessing import Process
import time


# existing class has connection, extending to add useful functions
class QueueManager(BaseManager):
    """Connects multiprocessing module to web server distribution system.
    """
    pass


class MPWorker(Process):
    """Accepts a parallel job and runs an appropriate processor.
    """

    def __init__(self, wrk_idx):
        """Connects to distribution queues on init.
        """
        super(MPWorker, self).__init__()
        host_ip = open(cf._host, "r").read()
        
        QueueManager.register('qwork')
        QueueManager.register('qfinalize')
        mng = QueueManager(address=(host_ip, cf._port), authkey=cf._key)
        mng.connect()
        self.qwork = mng.qwork()
        self.qfinalize = mng.qfinalize()
        self.idx = wrk_idx  # for creating unique temp directory
        # loading module data
        if cf._SIFT_kNN == "True":
            self.sift_knn = sift_knn()
        if cf._SIFT_pdist == "True":
            self.sift_pdist = sift_pdist(cf._pd_descriptors)
        print "starting worker %d ..." % wrk_idx

    def _process_task(self, task):
        """Here a task processing takes place.
        """
        newtask = [[]]*3
        newtask[0] = task[0]
        newtask[2] = task[2]
        if task[0] == "add_website":
            newtask[1] = add_website(task[1][0], task[1][1])
        elif task[0] == "get_csift":
            newtask[1] = csift(task[1])
        elif task[0] == "tree_clust":
            newtask[1] = self.sift_pdist.get_dist_1k(task[1])
        elif task[0] == "get_knn":
            newtask[1] = self.sift_knn.get_knn(task[1])
        return newtask
                        
    def run(self):
        """Just gets a task, processes and sends back to output queue.
        """
        while True:
            task = self.qwork.get(block=True)
            if task == "empty": 
                # close worker if job is done
                self.qwork.task_done()
                return
            # submitting results            
            result = self._process_task(task)
            self.qfinalize.put(result, block=True)
            self.qwork.task_done()
            time.sleep(0.01)


def start_worker(i):
    wrk = MPWorker(i)
    wrk.start()
    time.sleep(0.1)    

