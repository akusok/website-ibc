# -*- coding: utf-8 -*-
"""Computes pairwise distances for SIFT histograms, pytohn implementation.
"""

#from wibc.config.wibc_config import cf
import numpy as np
import cPickle


class sift_pdist(object):
    
    def __init__(self, Dname):
        """Loading data to memory.
        """
        self.D = cPickle.load(open(Dname, 'rb'))
    
    def getA(self, N, THR=2):
        """Get thresholded weighting matrix.
        
        Uses best settings from the article, THR=2.
        """
        A = np.zeros((N,N), dtype=np.float64);
        for i in xrange(N):
            for j in xrange(max(0, i-THR+1), min(N, i+THR)):
                A[i,j] = 1 - float(abs(i-j))/THR
        return A
        
    def get_dist(self, P, Q, K, m=0.5):
        """Distance function using np.argsort.
        """
        A = self.getA(P.shape[0])
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
        return [k_idx, k_dist, np.mean(dist), np.std(dist)]

    def get_dist_1k(self, Pi):
        """Get 1000 closest neighbours of descriptor Pi.
        """
        P = self.D[Pi]
        res = [[]]*4
        res[0] = np.empty((0,))
        res[1] = np.empty((0,))
        for k in xrange(22):
            Q = self.D[k*50000:(k+1)*50000, :]
            r1 = self.get_dist(P, Q, K=1000)
            r1[0] += k*50000
            res[0] = np.hstack((res[0], r1[0]))
            res[1] = np.hstack((res[1], r1[1]))
            res[2].append(r1[2])
            res[3].append(r1[3])
        idx = np.argsort(res[1])[:1000]
        res[0] = res[0][idx]
        res[1] = res[1][idx]
        res[2] = np.mean(res[2])
        res[3] = np.mean(res[3])
        #return [k_idx, k_dist, np.mean(dist), np.std(dist)]
        return res