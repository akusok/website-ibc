# -*- coding: utf-8 -*-
"""Database structure description, hdf5.

Created on Mon Sep 16 13:18:17 2013

@author: akusoka1
"""


from tables import Int64Col, Float64Col, Float32Col, UInt8Col, Int8Col,\
                   StringCol, IsDescription, openFile


class WebsitesRecord(IsDescription):
    """Table type which describes websites.
    
    | Attributes:
    |  **index** -- Unique index of a website.
    |  **class_idx** -- Index of true class, i/2^32 is superclass, 
                        i%2^32 - subclass
    |  **img_count** -- Total number of images on that web page.
    |  **img_present** -- Number of database images in that website.
    |  **folder** -- Folder containing images from that website.
    |  **url** -- Web page of that website, if known.
    |  **class_text** -- Textual notation of the class
    """
    index           = Int64Col(dflt=-1, pos=0)
    class_idx       = Int64Col(dflt=-1, pos=1)
    img_count       = Int64Col(dflt=-1, pos=2)
    img_present     = Int64Col(dflt=-1, pos=3)
    class_text      = StringCol(itemsize=1024)
    folder          = StringCol(itemsize=1024)
    url             = StringCol(itemsize=1024)


class ImagesRecord(IsDescription):
    """Table type which describes images.

    | Attributes:
    |  **index** -- Unique image index.
    |  **class_idx** -- True class of image's website, true class for the image
            is unknown.
    |  **site_index** -- Index of website this image is taken from.
    |  **orig_sha1** -- Sha1 of an original image, used to find duplicates.
    |  **true_size** -- Dimensionality (x,y) of an original image.
    |  **new_size** -- Dimensionality (x,y) of a resized image.
    |  **true_name** -- File name of an original downloaded image.
    |  **new_name** -- File name of a preprocessed image.
    """
    index           = Int64Col(dflt=-1, pos=0)
    class_idx       = Int64Col(dflt=-1, pos=1)
    site_idx        = Int64Col(dflt=-1, pos=2)
    orig_sha1       = StringCol(itemsize=40, dflt="", pos=8)  # for finding duplicates
    true_size       = Int64Col(shape=(2), dflt=-1, pos=9)  # (x,y) before resize
    new_size        = Int64Col(shape=(2), dflt=-1, pos=9)  # (x,y) after resize
    true_name       = StringCol(itemsize=255, pos=10)  # name of a downloaded file
    new_name        = StringCol(itemsize=255, pos=11)  # name of a preprocessed image
    

class cSIFTRecord(IsDescription):
    """Table type what describes cSIFT local features.

    | Attributes:
    |  **index** -- Unique index of local sample.
    |  **data** -- cSIFT descriptor itself, with the dimensionality 3*128 = 384.
    |  **image_idx** -- Index of parental image.
    |  **site_idx** -- Website index of parental image.
    |  **class_idx** -- Class of corresponding image
    |  **center** -- Center coordinates (x,y) of that local sample.
    |  **radius** -- Radius of that local sample. Knowing center and radius,
            it is possible to read pixel representation of sample from image.
    |  **cornerness** -- Some value returned by sample detection algorithm.
            May be useful, don't take much space anyway.
    """
    index           = Int64Col(dflt=-1, pos=0)
    data            = UInt8Col(shape=(384), pos=1)
    image_idx       = Int64Col(dflt=-1, pos=2)
    site_idx        = Int64Col(dflt=-1, pos=3)
    class_idx       = Int64Col( dflt=-1, pos=4)
    center          = Int64Col(shape=(2), dflt=-1)
    radius          = Int64Col(dflt=-1) 
    cornerness      = Float64Col(dflt=0)


class cSIFT_nnRecord(IsDescription):
    """Table type what stores nearest neighbours in cSIFT.

    | Attributes:
    |  **index** -- Unique index of local sample.
    |  **nn_idx** -- indexes of nearest neighbours.
    |  **nn_dist** -- distances to those neighbours.
    |  **image_idx** -- Index of parental image.
    |  **feature_idx** -- Index of corresponding feature.
    """
    index           = Int64Col(dflt=-1, pos=0)
    nn_idx          = Int64Col(shape=(100), pos=1)
    nn_dist         = Float64Col(shape=(100), pos=2)
    image_idx       = Int64Col(dflt=-1, pos=3)
    feature_idx     = Int64Col(dflt=-1, pos=4)


class cSIFT_histRecord(IsDescription):
    """Table type what stores image histograms in cSIFT.

    | Attributes:
    |  **index** -- Unique index of local sample.
    |  **hist1** -- histogram of first level classes.
    |  **hist2** -- histogram of second level classes.
    |  **image_idx** -- Index of parental image.
    """
    index           = Int64Col(dflt=-1, pos=0)
    hist1           = Float64Col(shape=(10), pos=1)
    hist2           = Float64Col(shape=(24), pos=2)
    image_idx       = Int64Col(dflt=-1, pos=3)

























