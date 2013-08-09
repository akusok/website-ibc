# -*- coding: utf-8 -*-
"""
Utilites for copying huge HDF5 files.

Created on Thu Jun 20 14:02:59 2013
"""

#from ../modules/hdf5_creator import create_empty_hdf5
from tables import openFile
import numpy as np
import time


def copy_hdf5_newindex(data, new):
    """Copying a part of data, updating indexes.
    
    Copying process is image-based.
    Websites currently stays the same, as they are a tiny table.
    Only full-file copy, no appends!
    """

    def modify_data(imgrow, regs, descrs, rli):
        """Modifying data before writing it back.
        
        Returns an empty tuple if an image is to be deleted.
        """
        K = 0.8  # coeffitient
        regs1 = []
        descrs1 = []
        rli1 = rli
        x,y = imgrow[9]        
        
        for i in xrange(len(regs)):
            rg = regs[i]
            ds = descrs[i]
            
            xr,yr = rg[4]
            # centering and normalizing
            xr = (float(xr)/x - 0.5)*2
            yr = (float(yr)/y - 0.5)*2
            
            # check required condition
            if (xr**2 + yr**2 >= K**2):
                rg[0] = rli1  # self index
                ds[0] = rli1  # self index
                rli1 += 1
                regs1.append(rg)
                descrs1.append(ds)
        
        if len(regs1) == 0:
            return ()
        else:
            return (regs1, descrs1)


    print "Opening files"
    db0 = openFile(data, "r")
    db1 = openFile(new, "a")
    i = 0
    Ws0 = db0.root.Websites
    Img0 = db0.root.Images
    Reg0 = db0.root.Regions
    Des0 = db0.root.Descriptors
    Ws1 = db1.root.Websites
    Img1 = db1.root.Images
    Reg1 = db1.root.Regions
    Des1 = db1.root.Descriptors

    # websites
    print "Copying websites"
    batch = 10000
    N = Ws0.nrows
    for b in range(N/batch + 1):
        nmin = b*batch
        nmax = min((b+1)*batch, N)
        rows = []
        # just copy rows as they are the same
        Ws1.append(Ws0.read(nmin, nmax))
        print  "ws: %d/%d" % (nmax, N)
    Ws1.attrs.last_index = Ws0.attrs.last_index
    Ws1.flush()

    # image-based copy process
    t = time.time()
    reg_first = 0
    last_index = 0
    reg_last_index = 0
    nr_in_class = np.zeros((Img0.attrs.nr_in_class.shape[0],))
    flush = 0
    flushbatch = 1000
    N = Img0.nrows
    for j in xrange(N):
        imgrow = Img0.read(j,j+1)[0]        
        i0 = imgrow[3]
        i1 = i0 + imgrow[4]
        regs = Reg0.read(i0, i1)
        descrs = Des0.read(i0, i1)

        imgrow[0] = last_index
        data = modify_data(imgrow, regs, descrs, reg_last_index)
        # skipping an image if needed
        if data == ():
            continue        
        regs, descrs = data
        reg_count = len(regs)
        
        # update image row
        imgrow[0] = last_index
        imgrow[3] = reg_first
        imgrow[4] = reg_count        
        
        # writing data - an array of tuples
        Img1.append([tuple(imgrow)])       
        Reg1.append([tuple(r) for r in regs])
        Des1.append([tuple(d) for d in descrs])
        
        # update global attributes
        nr_in_class[imgrow[1]] += 1
        last_index += 1
        reg_first += reg_count  # updating reg_first for next image
        reg_last_index += reg_count
        flush += 1
        
        # flushing
        if flush >= flushbatch:
            dt = time.time() - t
            etr = int((float(dt)/(j+1)) * (N-j-1))
            print "Images %d/%d, time remaining %d:%02d:%02d" % \
                  (j+1, N, etr/3600, (etr % 3600)/60, etr % 60)
            flush = 0
            Img1.attrs.last_index = last_index
            Img1.attrs.nr_in_class = nr_in_class
            Img1.flush()
            Reg1.attrs.last_index = reg_last_index
            Reg1.flush()
            Des1.attrs.last_index = reg_last_index
            Des1.flush()

    # final flush
    Img1.attrs.last_index = last_index
    Img1.attrs.nr_in_class = nr_in_class
    Img1.flush()
    Reg1.attrs.last_index = reg_last_index
    Reg1.flush()
    Des1.attrs.last_index = reg_last_index
    Des1.flush()

    db0.close()
    db1.close()
    print 'Done copying!'


def copy_hdf5(data, new, batch=100000):
    """Copying all data to modify some columns.
    """
    print "Opening files"
    db0 = openFile(data, "r")
    db1 = openFile(new, "a")
    i = 0
    Ws0 = db0.root.Websites
    Img0 = db0.root.Images
    Reg0 = db0.root.Regions
    Des0 = db0.root.Descriptors
    Ws1 = db1.root.Websites
    Img1 = db1.root.Images
    Reg1 = db1.root.Regions
    Des1 = db1.root.Descriptors

    # websites
    print "Copying websites"
    N = Ws0.nrows
    for b in range(N/batch + 1):
        nmin = b*batch
        nmax = min((b+1)*batch, N)
        rows = []
        # just copy rows as they are the same
        Ws1.append(Ws0.read(nmin, nmax))
        print  "ws: %d/%d" % (nmax, N)
    Ws1.attrs.last_index = Ws0.attrs.last_index
    Ws1.flush()

    # images
    print "Copying images"
    N = Img0.nrows    
    img_repr = np.ones((24,), dtype=np.float64) * -1
    for b in range(N/batch + 1):        
        nmin = b*batch
        nmax = min((b+1)*batch, N)
        rows = []
        for row in Img0.read(nmin, nmax):
            rows.append(tuple(row) + (img_repr,))
        Img1.append(rows)
        print  "img: %d/%d" % (nmax, N)
    Img1.attrs.last_index = Img0.attrs.last_index
    Img1.attrs.nr_in_class = Img0.attrs.nr_in_class
    Img1.flush()

    # regions
    print "Copying regions"
    N = Reg0.nrows    
    ngb = np.ones((10,2), dtype=np.float64) * -1
    for b in range(N/batch + 1):        
        nmin = b*batch
        nmax = min((b+1)*batch, N)
        rows = []
        for tupl in Reg0.read(nmin, nmax):
            row = list(tupl)
            # format rows here
            rows.append(tuple(row[:6] + [ngb] + row[6:]))
        Reg1.append(rows)
        print  "reg: %d/%d" % (nmax, N)
    Reg1.attrs.last_index = Reg0.attrs.last_index
    Reg1.flush()

    # descriptors
    print "Copying descriptors"
    N = Des0.nrows   
    for b in range(N/batch + 1):        
        nmin = b*batch
        nmax = min((b+1)*batch, N)
        Des1.append(Des0.read(nmin, nmax))
        print  "des: %d/%d" % (nmax, N)
    Des1.attrs.last_index = Des0.attrs.last_index
    Des1.flush()

    db0.close()
    db1.close()
    print 'Done copying!'
        
        
if __name__ == "__main__":
    copy_hdf5_newindex("/data/spiiras/spiiras.h5", 
                       "/users/akusoka1/local/spiiras_border.h5")



















































