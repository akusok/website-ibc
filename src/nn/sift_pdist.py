# -*- coding: utf-8 -*-
"""Computes pairwise distances for SIFT histograms, pytohn implementation.
"""

import numpy as np
from bottleneck import argpartsort


def getA(N, THR=2):
    """Get thresholded weighting matrix.
    
    Uses best settings from the article, THR=2.
    """
    A = np.zeros((N,N), dtype=np.float64);
    for i in xrange(N):
        for j in xrange(max(0, i-THR+1), min(N, i+THR)):
            A[i,j] = 1 - float(abs(i-j))/THR
    return A


def get_dist_bln(P, Q, A, m, K):
    """Distance function using Bottleneck.
    """
    Z = (P+Q).dot(A)
    Z = Z**m
    Z[Z==0] = 1
    D = (P-Q)/Z
    # calc only diagonal of dot operation, for multiple vectors at a time
    DA = D.dot(A)
    sqdist = np.einsum('ij,ji->i', DA, D.T)  # squared distance
    # getting the closest K members
    k_idx = argpartsort(sqdist, K)[:K]
    k_dist = sqdist[k_idx]
    idx = np.argsort(k_dist)
    k_dist = k_dist[idx] ** 0.5
    k_idx = k_idx[idx]
    return (k_idx, k_dist)


def get_dist(P, Q, A, m, K):
    """Distance function using np.argsort.
    """
    Z = (P+Q).dot(A)
    Z = Z**m
    Z[Z==0] = 1
    D = (P-Q)/Z
    # calc only diagonal of dot operation, for multiple vectors at a time
    DA = D.dot(A)
    dist = np.einsum('ij,ji->i', DA, D.T)**0.5
    # getting the closest K members
    k_idx = np.argsort(dist)[:K]
    k_dist = dist[k_idx]
    return (k_idx, k_dist, (np.mean(dist), np.std(dist)))


if __name__ == "__main__":
    from tables import openFile
    import cProfile

    df = openFile("/data/spiiras_test/spiiras_test.h5","r")
    P = df.root.Descriptors.read(0,1,field="data")
    QQ = df.root.Descriptors.read(1,100000,field="data")
    
    N = QQ.shape[1]
    A = getA(N)
    print "Start"
    
    profiler = cProfile.Profile()
    profiler.enable()
    
    nn = get_dist(P, QQ, A, m=0.5, K=100)
    
    profiler.disable()
    profiler.dump_stats("/data/clust/siftdist.prof")

