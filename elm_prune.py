# -*- coding: utf-8 -*-
"""
Created on Mon Oct 21 12:16:30 2013

@author: akusoka1
"""

import numpy as np
from matplotlib import pyplot as plt
import sys

print "Starting!"

def normalize(X,Y):
    N = X.shape[0]
    X = X - np.tile(np.mean(X,0), (N,1)) 
    X = X / np.tile(np.std(X,0), (N,1))
    Y = Y - np.tile(np.mean(Y,0), (N,1)) 
    Y = Y / np.tile(np.std(Y,0), (N,1))
    return X,Y

def get_data_finance():
    X = np.loadtxt("finance_x.txt")
    C = np.loadtxt("finance_y.txt")
    N = X.shape[0]    
    Y = np.ones((N,2)) * -1
    Y[xrange(N), np.array((C+1)/2, dtype=np.int)] = 1
    X,Y = normalize(X,Y)    
    X = np.hstack((X, np.ones((N,1))))
    d = X.shape[1]
    return X,Y,N,d
    
def project(X, neurons={'lin':30, 'tanh':30}, inverse=False):
    N = X.shape[0]  # number of data samples
    d = X.shape[1]  # sample dimensionality
    H = np.empty((N,0), dtype=np.float64)        
    # iterate over types of neurons
    for key in neurons.keys():  
        K = neurons[key]
        # if K is a number (of neurons), create new neurons
        if isinstance(K, (int, long, float)):
            if K <= 0:  # skip if set to zero
                continue
            # calc projection matrix, bias and transformation function
            if key in ['lin','linear','l']:
                W = np.random.randn(d, int(K)) / 3**0.5  # Momo's normalization
                f = lambda x: x  # identity function
                fi = lambda x: x  # inverse also indentity function
            elif key in ['tanh']:
                W = np.random.randn(d, int(K)) / 3**0.5
                f = np.tanh  # tanh function
                fi = np.arctanh  # inverse of tanh function
            else:
                print "Unknown neuron type: %s, skipping..." % key
                continue
            neurons[key] = (W,f,fi)
        else:  # load saved neurons
            W,f,fi = neurons[key]
        # apply given neurons
        if inverse == False:
            H0 = f(X.dot(W))
        else:  # inverse projection of ELM
            H0 = fi(X).dot(np.linalg.pinv(W))
        H = np.hstack((H, H0))            
    return H



X,Y,N,d = get_data_finance()
k = 50  # neurons, both linear and tanh

H = project(X)
print H.shape
raise IOError



# generate neurons
W = np.random.rand(d,k*2)
# k tanh neurons + k linear neurons
H = np.hstack((np.tanh(X.dot(W[:,:k])), X.dot(W[:,k:])))

# solve ELM
B = np.linalg.pinv(H).dot(Y)

# get LOO error
P = H.dot(np.linalg.pinv(H))
e1 = Y - P.dot(Y)    
e2 = np.ones((H.shape[0],)) - np.diag(P)
e = e1 / np.tile(e2, (Y.shape[1],1)).T
e = np.mean(np.abs(e))    

print 'error: %.03f' % e

#############################################################################