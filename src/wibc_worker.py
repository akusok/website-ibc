# -*- coding: utf-8 -*-
"""
Created on Thu Jun 20 14:02:59 2013

@author: akusoka1
"""

from wibc_config import IBCConfig as cf
from mp.mp_worker import MPWorker
import sys
import time

##############################################################################
print "IBC started"
n = int(sys.argv[1])
wrk = []
for i in xrange(n):
    wrk.append(MPWorker(i))
    wrk[-1].start()
    time.sleep(0.1)



print "IBC finished"
##############################################################################
sys.exit()  # suicide


