#!/usr/bin/env python

from distutils.core import setup

setup(name='WIBC',
      version='1.1',
      description='Website Image-Based Classifier',
      author='Anton Akusok',
      author_email='akusok.a@gmail.com',
      url='http://akusoka1.github.io/website-ibc/index.html',
      packages=['wibc', 
                'wibc/hdf5',
                'wibc/modules',
                'wibc/config',
                'wibc/sift',
                'wibc/mp',
                ],
      package_data={'wibc/sift': ['colorDescriptor'],
                    'wibc/config': ['config.ini']},
     )
