# -*- coding: utf-8 -*-
"""Input/Output multiprocessing module, hdf5 storage.


Created on Sat Apr  6 21:01:26 2013
"""


from wibc.config.wibc_config import cf
from wibc.hdf5.hdf5_tools import create_empty_hdf5
from multiprocessing.managers import BaseManager
from multiprocessing import Process
from tables import openFile
import Queue  # for exceptions
import os
import time


# existing class has connection, extending to add useful functions
class QueueManager(BaseManager):
    """Connects multiprocessing module to web server distribution system.
    """
    pass


class IO_HDF5(Process):
    """Prepares tasks and stores processed data.
    """
    
    def __init__(self, hdf5_file):
        """Connects to a mandatory HDF5 database and task queues.
        """

        # start multiprocessing part
        super(IO_HDF5, self).__init__()
        host_ip = open(cf._host, "r").read()
        
        # connect to queues
        QueueManager.register('qinit')
        QueueManager.register('qwork')
        QueueManager.register('qfinalize')
        mng = QueueManager(address=(host_ip, cf._port), authkey=cf._key)
        mng.connect()
        self.qinit = mng.qinit()
        self.qwork = mng.qwork()
        self.qfinalize = mng.qfinalize()

        # connect to an hdf5 file
        if not os.path.isfile(hdf5_file):
            create_empty_hdf5(hdf5_file)
        self.h5 = openFile(hdf5_file, "a")        
        self.WsRec = self.h5.root.Websites
        self.ImgRec = self.h5.root.Images
        self.csiftRec = self.h5.root.cSIFT
        # loading module-specific tables
        if cf._SIFT_kNN == "True":
            self.NN = self.h5.root.cSIFT_nn
        if cf._SIFT_pdist == "True":
            self.Idx = self.h5.root.Index
            self.Dist = self.h5.root.Distance
            self.Pr = self.h5.root.Param


    def __del__(self):
        """Closing HDF5 database nicely.
        """
        self.h5.close()


    def task_init(self, task):
        """Loads task data.
        
        task[0] is the task type:
            add_website
            get_csift
        """
        # adding websites and images
        if task[0] == "add_website":
            return task
        # getting cSIFT descriptors
        elif task[0] == "get_csift":
            img_idx = task[1]
            img = self.ImgRec.readWhere('index == %d' % img_idx)
            if img == []:  # if image not found
                print "Image %d not found!" % img_idx
                return -1  # empty task buffer
            imglist = [(img['new_name'][0], img['index'][0])]
            param = {"image_idx": img_idx,
                     "site_idx": img['site_idx'][0],
                     "class_idx": img['class_idx'][0]}
            newtask = [task[0], imglist, param]
            return newtask
        elif task[0] == "tree_clust":
            task.append(task[1])
            return task
        elif task[0] == "get_knn":
            img_idx = task[1]
            # here we have two queries, not so elegant solution
            # but they are fast
            # better solution may be introduced later
            I = self.csiftRec.readWhere('image_idx == %d' % img_idx,
                                        field="index")
            if I.shape[0] == 0:  # if nothing found
                return -1  # return empty task
            D = self.csiftRec.readWhere('image_idx == %d' % img_idx,
                                        field="data")
            newtask = [task[0], D, (img_idx, I)]
            return newtask

            
    def do_flush(self):
        """Save data to disk.
        """
        self.WsRec.flush()
        self.ImgRec.flush()
        self.csiftRec.flush()
            

    def task_finalize(self, task):
        """Writes data to HDF5 storage.
        """
        # adding websites and images
        if task[0] == "add_website":
            data = task[1]        
            # create website record
            wsrow = self.WsRec.row
            wsindex = self.WsRec.attrs.last_index + 1
            wsrow['index'] = wsindex
            self.WsRec.attrs.last_index += 1
            wsrow['img_count'] = data['img_count']
            wsrow['img_present'] = data['img_present']
            wsrow['folder'] = data['folder']
            # add other custom attributes
            for key,value in task[2].items():
                if key in self.WsRec.colnames:
                    wsrow[key] = value
            wsrow.append()
            # add image records
            for imgdata in data['images']:
                imgrow = self.ImgRec.row
                imgrow['index'] = self.ImgRec.attrs.last_index + 1
                self.ImgRec.attrs.last_index += 1
                if 'class_idx' in task[2].keys():  # if class is known
                    imgrow['class_idx'] = task[2]['class_idx']
                imgrow['site_idx'] = wsindex
                imgrow['orig_sha1'] = imgdata['sha1']
                imgrow['true_size'] = imgdata['true_size']
                imgrow['new_size'] = imgdata['new_size']
                imgrow['true_name'] = imgdata['true_name']
                imgrow['new_name'] = imgdata['new_name']
                imgrow.append()
                
        # getting cSIFT descriptors
        elif task[0] == "get_csift":
            data = task[1]
            for lf in data:
                row = self.csiftRec.row
                row['index'] = self.csiftRec.attrs.last_index + 1
                self.csiftRec.attrs.last_index += 1
                row['data'] = lf['data']
                row['image_idx'] = task[2]["image_idx"]
                row['site_idx'] = task[2]["site_idx"]
                row['class_idx'] = task[2]["class_idx"]
                row['center'] = lf['center']
                row['radius'] = lf['radius']
                row['cornerness'] = lf['cornerness']
                row.append()

        elif task[0] == "get_knn":
            knn_idx, knn_dist = task[1]
            img_idx, I = task[2]
            for i in xrange(I.shape[0]):
                row = self.NN.row
                row['index'] = self.NN.attrs.last_index + 1
                self.NN.attrs.last_index += 1
                row['nn_idx'] = knn_idx[i,:]
                row['nn_dist'] = knn_dist[i,:]
                row['image_idx'] = img_idx
                row['feature_idx'] = I[i]
                row.append()
    
        elif task[0] == "tree_clust":
            i = task[2]
            self.Idx[i,:] = task[1][0]
            self.Dist[i,:] = task[1][1]
            self.Pr[i,:] = [task[1][2], task[1][3]]

    def run(self, taskbuff=-1):
        """Check queues.
        """
        while True:
            # finalizing all tasks in a queue          
            #print "running..."
            empty = False
            try:
                while not empty:
                    task = self.qfinalize.get(block=False)
                    # process task
                    self.task_finalize(task)
                    self.qfinalize.task_done()
            except Queue.Empty:
                empty = True
    
            # preprocessing new tasks
            full = False
            empty = False
            try:
                while (not full) and (not empty):
                    while taskbuff == -1:  # '-1' means no task stored in buffer
                        task = self.qinit.get(block=False)   
                        
                        # closing everything if needed
                        if task == "empty": 
                            # close workers
                            for i in xrange(cf._nr_wrk):
                                self.qwork.put("empty", block=True)
                            self.qinit.task_done()
                            # close itself                
                            return                
    
                        # preprocess task
                        taskbuff = self.task_init(task)                
                        self.qinit.task_done()
                    # writing task to queue
                    # if write fails, tasks remains in the buffer until next time
                    self.qwork.put(taskbuff, block=False)
                    taskbuff = -1
            except Queue.Empty:
                empty = True  # initial task queue empty
            except Queue.Full:
                full = True  # work queue full
    
            self.do_flush()
            # preventing busy loop
            time.sleep(0.1)
            #time.sleep(3)


def start_io_hdf5(h5file):
    io = IO_HDF5(h5file)
    io.start()
    return io

