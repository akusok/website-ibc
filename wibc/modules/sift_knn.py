# -*- coding: utf-8 -*-
"""Computes pairwise distances for SIFT histograms, pytohn implementation.
"""

from wibc.config.wibc_config import cf
import numpy as np
import scipy.spatial.distance as distance
from bottleneck import argpartsort  # finding k smallest elements fast
import cPickle


class sift_knn(object):
    """Provides all distance calculations.
    """
    
    def __init__(self):
        """Loading centroids to memory.
        """
        self.C = cPickle.load(open(cf._Centroids, 'rb'))['C']
        self.A = self.getA(self.C.shape[1])
        self.K = cf._knn_K  # number of nearest neighbours
        self.true_dist = cf._knn_use_sift
    
    def getA(self, N, THR=2):
        """Get thresholded weighting matrix.
        
        Uses best settings from the article, THR=2.
        """
        A = np.zeros((N,N), dtype=np.float64);
        for i in xrange(N):
            for j in xrange(max(0, i-THR+1), min(N, i+THR)):
                A[i,j] = 1 - float(abs(i-j))/THR
        return A

    def _knn_sift_helper(self, P, m=0.5):
        """Helper function for 1 descriptor vs All centroids
        """
        Q = self.C
        Z = (P+Q).dot(self.A)
        Z = Z**m
        Z[Z==0] = 1
        D = (P-Q)/Z
        # calc only diagonal of dot operation, for multiple vectors at a time
        DA = D.dot(self.A)
        dist = np.einsum('ij,ji->i', DA, D.T)**0.5
        # getting the closest K members
        k_idx = np.argsort(dist)[:self.K]
        k_dist = dist[k_idx]
        return k_idx, k_dist
        
    def get_knn_sift(self, D):
        """Get histogram SIFT distance, long to compute.
        """
        N = D.shape[0]
        knn_idx = np.empty((N, self.K), dtype=np.int64)
        knn_dist = np.empty((N, self.K), dtype=np.float64)
        for i in xrange(N):
            res = self._knn_sift_helper(D[i,:])
            knn_idx[i,:] = res[0]
            knn_dist[i,:] = res[1]
            print i
        return knn_idx, knn_dist
        
    def _knn_euclid_helper(self, D):
        """Helper function to reduce memory consumption.
        """        
        dist = distance.cdist(D, self.C, 'sqeuclidean')
        L = D.shape[0]  # number of samples
        k = self.K  # number of nearest neighbours to return
        k_idx = argpartsort(dist, k, 1)[:, :k]  # getting K smallest indices, unordered
        k_dist = dist[[[t]*k for t in xrange(L)], k_idx]  # get distances, unordered
        idx = np.argsort(k_dist, 1)  # get correct ordering
        k_dist = k_dist[[[t]*k for t in xrange(L)], idx]  # apply ordering to distances
        k_idx = k_idx[[[t]*k for t in xrange(L)], idx]  # apply ordering to indices
        return k_idx, k_dist
        
    def get_knn_euclid(self, D):
        """Indexes and distances of *k* nearest neighbours.
        """
        N = D.shape[0]
        bs = max(1000, self.K*10)  # batch size
        B = N/bs + 1  # number of batches, batch size = 1000
        knn_idx_list = []
        knn_dist_list = []
        # getting batch results
        for b in xrange(B):        
            D1 = D[b*bs:(b+1)*bs]
            if D1.shape[0] > 0:  # if batch is not empty
                res = self._knn_euclid_helper(D1)
                knn_idx_list.append(res[0])
                knn_dist_list.append(res[1])
        k_idx = np.vstack(knn_idx_list)
        k_dist = np.vstack(knn_dist_list)
        return k_idx, k_dist
        
    def get_knn(self, D):
        """Select desired type of distance.
        """
        if self.true_dist:
            return self.get_knn_sift(D)
        else:
            return self.get_knn_euclid(D)

















































