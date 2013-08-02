.. highlight:: bash

User guide
==========


Installation
------------

Copy the code to your machine, then check *wibc_config.py* and change options accordingly. Add execution permission to *./sift/colorDescriptor* binary file.

Software is written for Linux (Ubuntu 12.10) and was not tested for other OS.
If porting to Windows is necessary, except apating the code, a Windows-specific binary file ./sift/colorDescriptors would be required.


Prerequisities
**************

* Python 2.7 with Numpy and Scipy
* recent versions of Python's Multiprocessing and Subprocess modules
* `HDF5 <http://www.hdfgroup.org/HDF5/>`_
* `pyTables <http://pytables.github.io/>`_, version >= 3.0.0 `here <http://sourceforge.net/projects/pytables/files/pytables/>`_
* `Python Imaging Library <http://www.pythonware.com/products/pil/>`_
* `bottleneck <https://pypi.python.org/pypi/Bottleneck>`_


Manual
******

Configure your experiment using *wibc.py* and *wibc_config.py* in source folder. Check the necessary temporary folders, and create input files. For more information, refer to demo (coming soon) and *docs/dia/IBC2.pdf* flow diagram.


Configuring a run
*****************

coming soon...

