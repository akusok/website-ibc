# -*- coding: utf-8 -*-
"""
A parallel worker running in a separate process.

Created on Sat Apr  6 21:01:26 2013
"""

from wibc_config import IBCConfig as cf
from sift.csift_extractor import csift
from gist.gist_extractor import get_gist
from nn.pdist import PDist
from multiprocessing.managers import BaseManager
from multiprocessing import Process
import time


# existing class has connection, extending to add useful functions
class QueueManager(BaseManager):
    """Connects multiprocessing module to web server distribution system.
    """
    pass


class MPBaseWorker(Process):
    """Accepts a parallel job and runs an appropriate processor.
    """

    def __init__(self, wrk_idx):
        """Connects to distribution queues on init.
        """
        super(MPBaseWorker, self).__init__()
        host_ip = open(cf._host, "r").read()
        
        QueueManager.register('qtask')
        QueueManager.register('qresult')
        mng = QueueManager(address=(host_ip, cf._port), authkey=cf._key)
        mng.connect()
        self.qtask = mng.qtask()
        self.qresult = mng.qresult()
        self.idx = wrk_idx  # for creating unique temp directory

    def _process_task(self, task):
        """Here a task processing takes place.
        """
        raise NotImplementedError
        return

    def run(self):
        """Just gets a task, processes and sends back to output queue.
        """
        while True:
            task = self.qtask.get(block=True)
            if task == "empty": 
                # close worker if job is done
                self.qresult.put("done", block=True)
                self.qtask.task_done()
                return
            
            result = self._process_task(task)
            # submitting results            
            self.qresult.put(result, block=True)
            self.qtask.task_done()
            time.sleep(0.01)


class MPWorker(MPBaseWorker):
    """Extention with default result processing.
    """
    
    def __init__(self, wrk_idx):
        super(MPWorker, self).__init__(wrk_idx)
        self.pd = PDist()

    def _process_task(self, task):
        """Processing needed for main program workflow.
        """
        if task[0] == "csift":
            result = (csift(task[1], self.idx), task[2])
        elif task[0] == "gist":  # 1-line calculation here:
            time.sleep(0.01)
            result = (get_gist(task[1]), task[2])
        elif task[0] == "nn":
            # task[2] are start and stop indices of descriptors
            result = (self.pd.get_knn(task[1]), task[2])
        else:
            result = "Unknown task type"
        return result
    


