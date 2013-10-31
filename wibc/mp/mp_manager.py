# -*- coding: utf-8 -*-
"""Starts the queue server and runs forever.

A port will be busy as long as the server is running.

Manual operation: just start the script, manually close when finished.

Script operation: 
 - start with p=subprocess.Popen(...), call p.poll() to wait for
 - an actual start, terminate with p.terminate() which takes
 - around 20 seconds to actually close the process.

Created on Sat Apr  6 21:01:26 2013
"""

from wibc.config.wibc_config import cf
import socket
from multiprocessing.managers import SyncManager
import Queue


def MPManager(host=""):
    """Creates web server with two Python queues attached.

    | Variables:
    |    *host*   -- host to start server, local machine host by default
    """

    host_file = open(cf._host, "w")
    if host == "":    
        host = socket.gethostbyname(socket.gethostname())
    host_file.write(host)
    host_file.close()
    
    qinit = Queue.Queue()  # small tasks here, no limit
    qwork = Queue.Queue(maxsize=cf._qsize)
    qfinalize = Queue.Queue(maxsize=cf._qsize)
    
    class QueueManager(SyncManager):
        pass

    QueueManager.register('qinit', callable=lambda:qinit)
    QueueManager.register('qwork', callable=lambda:qwork)
    QueueManager.register('qfinalize', callable=lambda:qfinalize)
    print "Starting queue server at %s" % host
    manager = QueueManager(address=(host, cf._port), authkey=cf._key)
    manager.get_server().serve_forever()












