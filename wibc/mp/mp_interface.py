# -*- coding: utf-8 -*-
"""Input/Output multiprocessing module, hdf5 storage.


Created on Sat Apr  6 21:01:26 2013
"""


from wibc.config.wibc_config import cf
from multiprocessing.managers import BaseManager
from multiprocessing import Process
from tables import openFile
import time
import os


# existing class has connection, extending to add useful functions
class QueueManager(BaseManager):
    """Connects multiprocessing module to web server distribution system.
    """
    pass


class MPInterface(Process):
    """Prepares tasks and stores processed data.
    """
    
    def __init__(self, tasklist=[]):
        """Connects to a mandatory HDF5 database and task queues.
        """

        # start multiprocessing part
        super(MPInterface, self).__init__()
        host_ip = open(cf._host, "r").read()
        
        # connect to queues
        QueueManager.register('qinit')
        # next two are for reporting purposes only
        QueueManager.register('qwork')
        QueueManager.register('qfinalize')
        mng = QueueManager(address=(host_ip, cf._port), authkey=cf._key)
        mng.connect()
        self.qinit = mng.qinit()
        self.qwork = mng.qwork()
        self.qfinalize = mng.qfinalize()
        self.tasklist = tasklist
        self.t = time.time()
        self.N = 0


    def set_config(self, cf_new):
        cf_orig = __file__[:-19] + "config/config.ini"
        os.system("cp %s %s" % (cf_new, cf_orig))


    def get_config(self, cf_file):
        cf_orig = __file__[:-19] + "config/config.ini"
        os.system("cp %s %s" % (cf_orig, cf_file))


    def add_tasks(self, tasks=[]):
        """Puts tasks to input queue, starts timer.
        """
        for task in tasks:
            self.qinit.put(task)
        self.t = time.time()
        self.N = len(tasks)


    def reset_timer(self):
        """Resets time and count.
        """
        self.t = time.time()
        self.N = self.qinit.qsize() + cf._qsize

    
    def get_progress(self):
        """Returns estimate tasks and time until finish.
        
        Works correctly for the last task list
        """
        N1 = self.qinit.qsize()
        N2 = self.qwork.qsize()
        N3 = self.qfinalize.qsize()
        N = self.N - cf._qsize  # substracting queued samples
        t1 = float(time.time() - self.t) / (N - N1)
        trem = int(t1*N1)
        s = "tasks %d/%d/%d" % (N1,N2,N3)
        s = s + ", time %d:%02d:%02d" % (trem/3600, (trem % 3600)/60, 
                                         trem % 60)
        return s, N1+N2+N3

    def terminate(self):
        self.qinit.put("empty")

